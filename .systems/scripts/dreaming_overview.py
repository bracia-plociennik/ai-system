"""Local authorized projections and common view; aggregator never opens a corpus."""
import argparse,json,sys,os,uuid
from pathlib import Path
from dreaming_provider_v1 import digest,shape,require,slug,sha,ProtocolError
from dreaming_contracts import candidate
from dreaming_privacy import clean_projection
from dreaming_guard import registry
from dreaming_runner import load,save,lock,directory,snapshot

def alias(owner):return 'scope-'+digest(owner)[:24]

def sharing(scope,recipient):
    registry(scope);slug(recipient)
    require(scope['sharing']['mode']!='none' and scope['sharing']['recipient']==recipient and scope['sharing']['authority_ref'],'sharing-unavailable')

def projection(workspace,run_id,scope,recipient,texts=None,review=None):
    sharing(scope,recipient);path=directory(workspace,run_id);completion=load(path/'completion.json');state=load(path/'state.json')
    require(completion['owner_workspace_id']==scope['owner_workspace_id'] and completion['policy_digest']==digest(scope),'stale-local-policy')
    require(digest(state['policy'])==digest(scope),'scope-drift')
    # Only the owner-local producer rechecks private sources. The common aggregator never does.
    snapshot(state)
    # Local producer validates immutable completion before deriving the allowed projection.
    artifacts={name:load(path/name) for name in completion['artifact_digests']}
    require(all(digest(artifacts[name])==expected for name,expected in completion['artifact_digests'].items()),'completion-artifact-drift')
    packets=artifacts['candidates.json']
    for item in packets:candidate(item)
    counts={'candidates':len(packets),'held':sum(any(r['state'] in ['needs-evidence','needs-owner-decision'] for r in x['consumer_readiness'].values()) for x in packets)}
    value={'export_version':1,'owner_scope':alias(scope['owner_workspace_id']),'run_id':'run-'+digest([scope['owner_workspace_id'],run_id])[:24],
           'completion_digest':digest(completion),'policy_digest':digest(scope),'recipient':recipient,'mode':scope['sharing']['mode'],
           'coverage':artifacts['inventory.json']['coverage'],'result':completion['result'],'counts':counts,
           'candidate_ids':[x['candidate_id'] for x in packets],'reviewed_text':[]}
    if texts:
        require(scope['sharing']['mode']=='reviewed-text','text-sharing-not-authorized')
        require(isinstance(texts,list),'invalid-projection-text')
        for text in texts:
            shape(text,{'candidate_id','title','reason'});require(text['candidate_id'] in value['candidate_ids'],'unbound-projection-text');clean_projection(text)
        value['reviewed_text']=texts
    if value['mode']=='reviewed-text' and review is not None:
        shape(review,{'projection_hash','recipient','approved_by','authority_ref'})
        require(review['projection_hash']==digest(value) and review['recipient']==recipient and review['approved_by']=='owner' and isinstance(review['authority_ref'],str) and review['authority_ref'],'current-projection-review-required')
    return clean_projection({'projection':value,'projection_hash':digest(value),'review':review if value['mode']=='reviewed-text' else None})

def validate(value,completion,current_scope,recipient):
    sharing(current_scope,recipient);shape(value,{'projection','projection_hash','review'});p=value['projection']
    shape(p,{'export_version','owner_scope','run_id','completion_digest','policy_digest','recipient','mode','coverage','result','counts','candidate_ids','reviewed_text'})
    require(type(p['export_version']) is int and p['export_version']==1,'unsupported-projection')
    require(value['projection_hash']==digest(p) and p['completion_digest']==digest(completion),'projection-drift')
    require(p['policy_digest']==digest(current_scope) and completion['policy_digest']==digest(current_scope) and completion['owner_workspace_id']==current_scope['owner_workspace_id'],'sharing-revoked-or-changed')
    require(p['owner_scope']==alias(current_scope['owner_workspace_id']) and p['recipient']==recipient and p['mode']==current_scope['sharing']['mode'],'recipient-or-owner-mismatch')
    require(p['result']==completion['result'] and p['result'] in ['complete','partial','blocked'],'invalid-projection-result')
    shape(p['coverage'],{'enumeration_complete','counts'});require(type(p['coverage']['enumeration_complete']) is bool,'invalid-coverage')
    require(isinstance(p['coverage']['counts'],dict) and set(p['coverage']['counts'])=={'reviewed','reused-unchanged','pending','unsupported','excluded','blocked','missing'},'invalid-coverage-counts')
    require(all(type(n) is int and n>=0 for n in p['coverage']['counts'].values()),'invalid-coverage-count')
    shape(p['counts'],{'candidates','held'});require(all(type(n) is int and n>=0 for n in p['counts'].values()) and p['counts']['held']<=p['counts']['candidates'],'invalid-candidate-count')
    require(isinstance(p['candidate_ids'],list) and len(set(p['candidate_ids']))==len(p['candidate_ids']) and len(p['candidate_ids'])==p['counts']['candidates'],'invalid-candidate-ids')
    for cid in p['candidate_ids']:
        try:uuid.UUID(cid)
        except (ValueError,TypeError,AttributeError):raise ProtocolError('invalid-candidate-id') from None
    if p['mode']=='counts-only':require(not p['reviewed_text'] and value['review'] is None,'unreviewed-text')
    else:
        shape(value['review'],{'projection_hash','recipient','approved_by','authority_ref'})
        require(value['review']['projection_hash']==digest(p) and value['review']['recipient']==recipient and value['review']['approved_by']=='owner' and value['review']['authority_ref'],'stale-projection-review')
        for text in p['reviewed_text']:shape(text,{'candidate_id','title','reason'});require(text['candidate_id'] in p['candidate_ids'],'unbound-title')
    clean_projection(value);return p

def overview(inputs,recipient):
    slug(recipient);scopes=[];seen=set()
    for item in inputs:
        shape(item,{'projection','completion','current_scope'})
        try:
            p=validate(item['projection'],item['completion'],item['current_scope'],recipient)
            require(p['owner_scope'] not in seen,'duplicate-overview-scope');seen.add(p['owner_scope']);scopes.append(p)
        except (ValueError,TypeError,KeyError):scopes.append({'state':'unavailable','reason':'sharing-or-current-evidence-unavailable'})
    return clean_projection({'overview_version':1,'recipient':recipient,'scopes':scopes,'authority':'advisory-only','input_digests':[digest(x['projection']) for x in inputs]})

def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['export','preview','write']);parser.add_argument('--request',required=True);parser.add_argument('--destination');parser.add_argument('--owner-approved',action='store_true');args=parser.parse_args()
    try:
        value=load(args.request)
        if args.action=='export':
            shape(value,{'workspace','run_id','scope','recipient'},{'texts','review'});result=projection(value['workspace'],value['run_id'],value['scope'],value['recipient'],value.get('texts'),value.get('review'))
            if args.destination:
                require(result['projection']['mode']=='counts-only' or result['review'] is not None,'current-projection-review-required')
                require(args.owner_approved,'current-scoped-approval-required');path=directory(value['workspace'],value['run_id']);require(Path(args.destination)==path/'overview-projection.json','invalid-export-destination');save(path,'overview-projection.json',result)
        else:
            shape(value,{'inputs','recipient'});result=overview(value['inputs'],value['recipient'])
            if args.action=='write':
                require(args.owner_approved and args.destination,'explicit-overview-destination-required');destination=Path(args.destination);require(destination.is_absolute() and destination.is_dir(),'invalid-overview-destination')
                with lock(destination):save(destination,'overview-'+digest(result)+'.json',result)
        print(json.dumps(result,ensure_ascii=False,sort_keys=True));return 0
    except (OSError,ValueError,TypeError,KeyError):print(json.dumps({'error':'overview-held'}),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
