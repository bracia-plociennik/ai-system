"""Explicit local broker; no model client, scheduler, or operational mutation."""
import argparse
import contextlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from dreaming_guard import GuardError, need, open_root, registry, hash_object
from dreaming_provider_v1 import parse_json, envelope, digest, sha, slug, shape, require, ProtocolError
from dreaming_contracts import consume
from dreaming_case_resolver import finding_refs, context_for, case_key, merge_context

def load(path):
    path=Path(path);need(not path.is_symlink() and path.stat().st_size<=67108864,'unsafe-input')
    return parse_json(path.read_text())

def implementation_digest():
    """Bind broker/consumer bytes, including ignored changes, for continuations/reuse."""
    from dreaming_guard import hash_bytes
    scripts=Path(__file__).resolve().parent
    names=['dreaming_runner.py','dreaming_contracts.py','dreaming_provider_v1.py','dreaming_guard.py','dreaming_case_resolver.py']
    if (scripts/'dreaming_candidates.py').is_file():names.append('dreaming_candidates.py')
    return digest({name:hash_bytes((scripts/name).read_bytes()) for name in names})

def provider(policy, producer, accepted):
    root=Path(producer);need(root.is_absolute(),'invalid-provider-root')
    # No arbitrary executable or policy-supplied command. Import only validated local provider bytes.
    need(isinstance(accepted,dict),'invalid-provider-binding')
    required={'.systems/scripts/dreaming_evidence.py','.systems/scripts/dreaming_evidence_reader.py','.systems/scripts/dreaming_guard.py','.systems/scripts/resolve-workflow-env','.systems/scripts/dreaming_native.py','.systems/scripts/lib/qa-evidence.py','.systems/scripts/lib/capture-record.py'}
    need(set(accepted)==required,'incomplete-provider-binding')
    for rel,expected in accepted.items():
        from dreaming_guard import read_file,hash_bytes
        need(hash_bytes(read_file(str(root),rel,1048576,prescreen=False))==expected,'producer-drift')
    # stdin policy prevents an extra source file inside the reviewed corpus.
    code='import json,sys; from dreaming_evidence_reader import provide; print(json.dumps(provide(json.load(sys.stdin))))'
    result=subprocess.run([sys.executable,'-I','-B','-c',"import sys;sys.path.insert(0,sys.argv[1]);"+code,str(root/'.systems/scripts')],input=json.dumps(policy),capture_output=True,text=True,
                          cwd=root/'.systems/scripts',timeout=60,env={**os.environ,'PYTHONPATH':str(root/'.systems/scripts')})
    need(result.returncode==0,'provider-unavailable')
    value=parse_json(result.stdout);consume(value['envelope'],value['envelope']['capability'],accepted)
    return value

def directory(workspace,run_id,create=False):
    slug(run_id);base=Path(workspace);need(base.is_absolute(),'invalid-workspace')
    fd=open_root(str(base))
    try:
        for part in ['dreams','runs',run_id]:
            if create:
                try:os.mkdir(part,0o700,dir_fd=fd)
                except FileExistsError:pass
            newer=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=newer
        return base/'dreams/runs'/run_id
    finally:os.close(fd)

@contextlib.contextmanager
def lock(path):
    fd=open_root(str(path))
    try:
        item=os.open('.run-lock',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=fd)
        os.close(item)
        try:yield
        finally:os.unlink('.run-lock',dir_fd=fd)
    finally:os.close(fd)

def save(path,name,value):
    fd=open_root(str(path));data=json.dumps(value,sort_keys=True,ensure_ascii=False,indent=2,allow_nan=False).encode()+b'\n'
    try:
        existing=None
        try:
            source=os.open(name,os.O_RDONLY|os.O_NOFOLLOW,dir_fd=fd)
            with os.fdopen(source,'rb') as stream:existing=stream.read(67108865)
        except FileNotFoundError:pass
        if existing==data:return
        # Only mutable run state has one current revision; completed artifacts are immutable.
        need(name=='state.json' or existing is None,'artifact-conflict')
        tmp=name+'.writing';out=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=fd)
        try:
            with os.fdopen(out,'wb') as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
            os.rename(tmp,name,src_dir_fd=fd,dst_dir_fd=fd);os.fsync(fd)
        except BaseException:
            try:os.unlink(tmp,dir_fd=fd)
            except FileNotFoundError:pass
            raise
    finally:os.close(fd)

def plan(workspace,run_id,policy,producer,accepted,analyzer,previous_run=None):
    registry(policy);shape(analyzer,{'id','version','policy_digest'});slug(analyzer['id']);slug(analyzer['version']);sha(analyzer['policy_digest'])
    # Caller has explicitly chosen the workspace; matching ID remains required in policy/refs.
    path=directory(workspace,run_id,True);result=provider(policy,producer,accepted)
    state={'run_id':run_id,'policy':policy,'producer':str(producer),'accepted':accepted,'analyzer':analyzer,
           'envelope':result['envelope'],'delivered':[],'analyses':[],'started_at':datetime.now(timezone.utc).isoformat(),'implementation_digest':implementation_digest(),'previous_run':previous_run}
    if previous_run:
        prior=directory(workspace,previous_run);completion=load(prior/'completion.json');old=load(prior/'inventory.json')
        need(completion['artifact_digests']['inventory.json']==digest(old),'reuse-artifact-drift')
        same=(completion.get('implementation_digest')==implementation_digest() and completion['policy_digest']==digest(policy) and completion['analyzer_digest']==digest(analyzer) and completion['capability_digest']==digest(result['envelope']['capability']) and completion['owner_workspace_id']==policy['owner_workspace_id'])
        if same:
            previous_report=load(prior/'report.json')
            need(completion['artifact_digests']['report.json']==digest(previous_report),'reuse-artifact-drift')
            refkeys=['source_root_id','relative_path','project_id','owner_workspace_id','sha256','byte_count','source_class']
            current_refs={tuple(row['source_ref'][k] for k in refkeys) for row in state['envelope']['inventory'] if row['source_ref']}
            prior_receipts={row['read_receipt']['receipt_id']:row['source_ref'] for row in old['inventory'] if row['read_receipt']}
            for row in state['envelope']['inventory']:
                if row['source_ref'] is None:continue
                matched=[r for r in old['inventory'] if r['disposition'] in ['reviewed','reused-unchanged'] and r['source_ref'] and all(r['source_ref'][k]==row['source_ref'][k] for k in ['source_root_id','relative_path','project_id','owner_workspace_id','sha256','byte_count','source_class'])]
                if matched:
                    prior_row=matched[0];receipt=prior_row['read_receipt']
                    # Reuse the complete analysis input closure, never an unchanged
                    # fragment whose finding/context still cites changed source bytes.
                    analyses=[a for a in previous_report['analysis_receipts'] if receipt['receipt_id'] in a['read_receipt_ids'] and all(key in prior_receipts and tuple(prior_receipts[key][k] for k in refkeys) in current_refs for key in a['read_receipt_ids'])]
                    if not analyses:continue
                    row.update(disposition='reused-unchanged',reason_code='bound-prior-analysis',read_receipt=receipt,analysis_receipt=analyses[-1],source_ref=prior_row['source_ref'])
                    # Retain actual prior response provenance; no invented fresh analysis.
                    for analysis in analyses:
                        if not any(a['receipt_id']==analysis['receipt_id'] for a in state['analyses']):state['analyses'].append(analysis)
                    state['delivered'].extend(c['chunk_id'] for c in receipt['chunk_map'])
    with lock(path):
        if (path/'state.json').exists():
            prior=load(path/'state.json');need(all(prior[x]==state[x] for x in ['policy','producer','accepted','analyzer','previous_run']),'run-id-conflict');return prior
        save(path,'state.json',state)
    return state

def snapshot(state):
    need(state.get('implementation_digest')==implementation_digest(),'broker-implementation-drift')
    actual=provider(state['policy'],state['producer'],state['accepted'])
    old={ (r['source_root_id'],r['relative_path']):r['source_ref']['sha256'] for r in state['envelope']['inventory'] if r['source_ref'] }
    current={ (r['source_root_id'],r['relative_path']):r['source_ref']['sha256'] for r in actual['envelope']['inventory'] if r['source_ref'] }
    need(old==current,'source-drift')
    before=[(r['source_root_id'],r['relative_path'],'pending' if r['disposition']=='reused-unchanged' else r['disposition'],'eligible' if r['disposition']=='reused-unchanged' else r['reason_code']) for r in state['envelope']['inventory']]
    after=[(r['source_root_id'],r['relative_path'],r['disposition'],r['reason_code']) for r in actual['envelope']['inventory']]
    need(before==after and state['envelope']['coverage']['enumeration_complete']==actual['envelope']['coverage']['enumeration_complete'],'inventory-drift')
    return actual

def read(workspace,run_id,chunk_id):
    path=directory(workspace,run_id)
    with lock(path):
        state=load(path/'state.json');need(not (path/'completion.json').exists(),'run-completed')
        actual=snapshot(state);found=[x for x in actual['chunks'] if x['chunk_id']==chunk_id];need(len(found)==1,'unknown-chunk')
        if chunk_id not in state['delivered']:state['delivered'].append(chunk_id);save(path,'state.json',state)
        # Original refs from plan carry a stable observed_at, hash and receipt identity.
        row=next(r for r in state['envelope']['inventory'] if r['source_ref'] and r['source_ref']['sha256']==found[0]['source_ref']['sha256'] and r['relative_path']==found[0]['source_ref']['relative_path'] and r['source_root_id']==found[0]['source_ref']['source_root_id'])
        found[0]['source_ref']=row['source_ref'];found[0]['native_metadata']=[m for m in actual.get('native_metadata',[]) if m['source_hash']==row['source_ref']['sha256']];return found[0]

def submit(workspace,run_id,analysis):
    shape(analysis,{'analyzer','policy_digest','read_receipt_ids','covered_chunks','findings','coverage','unresolved_conflicts'})
    path=directory(workspace,run_id)
    with lock(path):
        state=load(path/'state.json');need(not (path/'completion.json').exists(),'run-completed');actual=snapshot(state)
        need(analysis['analyzer']==state['analyzer'] and analysis['policy_digest']==digest(state['policy']),'analysis-binding-mismatch')
        need(analysis['coverage'] in ['complete','partial'] and isinstance(analysis['unresolved_conflicts'],list),'invalid-analysis-coverage')
        need(isinstance(analysis['covered_chunks'],list) and len(set(analysis['covered_chunks']))==len(analysis['covered_chunks']) and set(analysis['covered_chunks'])<=set(state['delivered']),'undisclosed-analysis')
        receipts={r['read_receipt']['receipt_id']:r for r in state['envelope']['inventory'] if r['read_receipt']}
        need(isinstance(analysis['read_receipt_ids'],list) and set(analysis['read_receipt_ids'])<=set(receipts),'unbound-analysis')
        covered={c['chunk_id'] for key in analysis['read_receipt_ids'] for c in receipts[key]['read_receipt']['chunk_map']}
        need(set(analysis['covered_chunks'])<=covered,'unbound-chunks')
        if analysis['coverage']=='complete':need(set(analysis['covered_chunks'])==covered and not analysis['unresolved_conflicts'],'false-analysis-complete')
        refs={r['source_ref']['sha256'] for key,r in receipts.items() if key in analysis['read_receipt_ids']}
        need(isinstance(analysis['findings'],list),'invalid-findings')
        ids=set()
        for finding in analysis['findings']:
            shape(finding,{'finding_id','source_hashes','facts','inferences','unknowns','native_state','native_quality'})
            slug(finding['finding_id']);need(finding['finding_id'] not in ids,'duplicate-finding');ids.add(finding['finding_id'])
            need(isinstance(finding['source_hashes'],list) and finding['source_hashes'] and set(finding['source_hashes'])<=refs,'uncited-finding')
            cited_rows=[r for key,r in receipts.items() if key in analysis['read_receipt_ids']]
            selected=finding_refs(finding,cited_rows);context_for(finding,selected,actual)
            for prior in state['analyses']:
                for old in prior['findings']:
                    if old['finding_id']==finding['finding_id']:
                        old_rows=[row for row in state['envelope']['inventory'] if row['read_receipt'] and row['read_receipt']['receipt_id'] in prior['read_receipt_ids']]
                        need(old==finding and finding_refs(old,old_rows)==selected,'finding-id-conflict')
            for field in ['facts','inferences','unknowns']:need(isinstance(finding[field],list) and all(isinstance(x,str) for x in finding[field]),'invalid-finding-text')
            need(finding['native_state'] in ['new','repeated','promoted','rejected','obsolete','unknown'] and finding['native_quality'] in ['unknown','stale','verified-current'],'unverified-native-quality')
            if finding['native_quality']=='verified-current':need(any(m['source_hash'] in finding['source_hashes'] and m['quality']=='verified-current' for m in actual.get('native_metadata',[])),'unverified-native-quality')
        analysis={**analysis,'receipt_id':digest(analysis)}
        if not any(a['receipt_id']==analysis['receipt_id'] for a in state['analyses']):state['analyses'].append(analysis);save(path,'state.json',state)
    return {'receipt_id':analysis['receipt_id']}

def finalize(workspace,run_id):
    path=directory(workspace,run_id)
    with lock(path):
        state=load(path/'state.json');actual=snapshot(state)
        if (path/'completion.json').exists():return load(path/'completion.json')
        value=state['envelope'];findings=[];bindings={};analysis_provenance={}
        for row in value['inventory']:
            if row['read_receipt'] is None:continue
            chunk_ids={c['chunk_id'] for c in row['read_receipt']['chunk_map']}
            accepted=[a for a in state['analyses'] if a['coverage']=='complete' and row['read_receipt']['receipt_id'] in a['read_receipt_ids'] and chunk_ids<=set(a['covered_chunks'])]
            if accepted:
                row.update(disposition='reused-unchanged' if row['disposition']=='reused-unchanged' else 'reviewed',reason_code='agent-reviewed',analysis_receipt=accepted[-1])
                seen=set()
                for a in accepted:
                    analysis_provenance[a['receipt_id']]=a
                    for f in a['findings']:
                        if row['source_ref']['sha256'] not in f['source_hashes']:continue
                        selected=finding_refs(f,[r for r in value['inventory'] if r['read_receipt'] and r['read_receipt']['receipt_id'] in a['read_receipt_ids']])
                        if row['source_ref'] not in selected:continue
                        need(f['finding_id'] not in bindings or bindings[f['finding_id']]==selected,'finding-id-conflict')
                        bindings[f['finding_id']]=selected
                        findings.append(f)
                        if f['finding_id'] in seen:continue
                        seen.add(f['finding_id'])
                        value['evidence'].append({'evidence_id':f['finding_id']+'-'+digest(row['source_ref'])[:12],'source_ref':row['source_ref'],'native_kind':'agent-finding','native_state':f['native_state'],'native_quality':f['native_quality'],'semantic_summary':'Evidence needs native consumer review.','limitations':f['unknowns']})
        counts={k:sum(r['disposition']==k for r in value['inventory']) for k in value['coverage']['counts']};value['coverage']['counts']=counts
        value['result']='blocked' if counts['blocked'] else 'partial' if not value['inventory'] or not value['coverage']['enumeration_complete'] or any(counts[k] for k in ['pending','unsupported','missing']) else 'complete'
        envelope(value)
        unique={}
        for f in findings:
            need(f['finding_id'] not in unique or unique[f['finding_id']]==f,'finding-id-conflict')
            unique[f['finding_id']]=f
        report={'run_id':run_id,'result':value['result'],'coverage':value['coverage'],'findings':list(unique.values()),'analysis_receipts':list(analysis_provenance.values()),'authority':'advisory-only'}
        from dreaming_candidates import reconcile,CONSUMERS
        packets=[];groups={}
        for finding in report['findings']:
            selected=bindings[finding['finding_id']]
            project=selected[0]['project_id'];ctx=context_for(finding,selected,actual);key=case_key(finding,ctx)
            labels={label:[{'text':text,'source_hashes':list(dict.fromkeys(finding['source_hashes'])),'evidence_level':level} for text in finding[label]] for label,level in [('facts','observed'),('inferences','inference'),('unknowns','unknown')]}
            if (project,key) not in groups:groups[(project,key)]={'refs':selected,'labels':labels,'context':ctx}
            else:
                group=groups[(project,key)];group['refs'].extend(selected);group['context']=merge_context(group['context'],ctx)
                for label,claims in labels.items():
                    group['labels'][label].extend(claim for claim in claims if claim not in group['labels'][label])
        for (project,key),group in sorted(groups.items()):
            selected=group['refs'];labels=group['labels'];ctx=group['context']
            proposed=reconcile(value['owner_workspace_id'],project,key,selected,labels,ctx)
            if state.get('previous_run'):
                prior_path=directory(workspace,state['previous_run']);prior_completion=load(prior_path/'completion.json');prior_packets=load(prior_path/'candidates.json')
                need(digest(prior_packets)==prior_completion['artifact_digests']['candidates.json'],'case-history-drift')
                from dreaming_contracts import candidate
                for old_packet in prior_packets:candidate(old_packet)
                matched=[old for old in prior_packets if old['candidate_id']==proposed['candidate_id']]
                need(len(matched)<=1,'ambiguous-case-history')
                if matched:
                    old=matched[0]
                    if old['prior_decision_ref']:
                        # Do not reopen a recorded decision from a new analysis response.
                        proposed={**old,'consumer_readiness':{c:{'state':'needs-owner-decision','missing_fields':['current-case-decision-required'],'evidence_hashes':[]} for c in CONSUMERS}}
                        proposed.update(revision=old['revision']+1,predecessor_hash=digest(old))
                    else:proposed=reconcile(value['owner_workspace_id'],project,key,selected,labels,ctx,old)
            packets.append(proposed)
        artifacts={'inventory.json':value,'candidates.json':packets,'report.json':report}
        for name,item in artifacts.items():save(path,name,item)
        completion={'schema_version':1,'run_id':run_id,'owner_workspace_id':state['policy']['owner_workspace_id'],'declared_roots':[r['source_root_id'] for r in state['policy']['roots']],'artifact_digests':{name:digest(item) for name,item in artifacts.items()},'policy_digest':digest(state['policy']),'analyzer_digest':digest(state['analyzer']),'capability_digest':digest(value['capability']),'result':value['result'],'started_at':state['started_at'],'finished_at':datetime.now(timezone.utc).isoformat(),'source_recheck':'current'}
        completion['implementation_digest']=implementation_digest()
        save(path,'completion.json',completion);return completion

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['plan','read','submit-analysis','finalize']);p.add_argument('--workspace',required=True);p.add_argument('--run-id',required=True);p.add_argument('--request');p.add_argument('--chunk-id');p.add_argument('--policy');p.add_argument('--owner-approved',action='store_true');args=p.parse_args()
    try:
        need(args.owner_approved,'current-scoped-approval-required')
        if args.action!='plan':
            need(bool(args.policy),'current-policy-required')
            current=registry(load(args.policy));saved=load(directory(args.workspace,args.run_id)/'state.json')
            need(digest(current)==digest(saved['policy']),'policy-revoked-or-changed')
        if args.action=='plan':
            v=load(args.request);shape(v,{'policy','producer','accepted_fingerprints','analyzer'},{'previous_run'});result=plan(args.workspace,args.run_id,v['policy'],v['producer'],v['accepted_fingerprints'],v['analyzer'],v.get('previous_run'))
        elif args.action=='read':result=read(args.workspace,args.run_id,args.chunk_id)
        elif args.action=='submit-analysis':result=submit(args.workspace,args.run_id,load(args.request))
        else:result=finalize(args.workspace,args.run_id)
        print(json.dumps(result,ensure_ascii=False,sort_keys=True));return 0
    except (OSError,ValueError,TypeError,KeyError,subprocess.SubprocessError):print(json.dumps({'error':'run-action-rejected'}),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
