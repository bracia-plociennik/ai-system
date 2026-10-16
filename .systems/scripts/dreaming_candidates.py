"""Evidence-backed case proposals; no inferred hours, approval or ownership merge."""
import uuid
from dreaming_contracts import candidate, CONSUMERS
from dreaming_provider_v1 import source_ref,slug,shape,require,digest,sha,ProtocolError

REQUIREMENTS={
    'ledger':['canonical-identity','confirmed-time','time-evidence','registered-entities','outcome'],
    'documentation':['setup','dependencies','procedure','tests','limitations','independent-replay'],
    'report':['recipient','approved-current-text'],
    'tax-evidence':['taxpayer-year','evidence-map'],
    'editorial':['canonical-entry','entry-hash','source-ref','private-lesson-review','anonymization-review'],
}

def reconcile(owner,project,case_key,refs,claims,context,previous=None,decision=None):
    slug(owner);slug(project);slug(case_key)
    shape(context,{'work_id','case_ref','signals','conflicts'})
    require(context['work_id'] is None or isinstance(context['work_id'],str),'invalid-work-identity')
    require(context['case_ref'] is None or isinstance(context['case_ref'],str),'invalid-case-identity')
    require(isinstance(context['conflicts'],list),'invalid-conflicts')
    require(isinstance(context['signals'],dict) and set(context['signals'])==CONSUMERS,'missing-consumer-signals')
    for consumer,values in context['signals'].items():
        require(isinstance(values,dict) and set(values)<=set(REQUIREMENTS[consumer]),'unknown-readiness-signal')
        for refhash in values.values():sha(refhash)
    unique=[];seen=set()
    for ref in refs:
        source_ref(ref);require(ref['owner_workspace_id']==owner and ref['project_id']==project,'cross-owner-evidence')
        identity=(ref['source_root_id'],ref['relative_path'],ref['sha256'])
        if identity not in seen:unique.append(ref);seen.add(identity)
    hashes={r['sha256'] for r in unique}
    require(all(h in hashes for values in context['signals'].values() for h in values.values()),'uncited-readiness')
    shape(claims,{'facts','inferences','unknowns'})
    candidate_id=str(uuid.uuid5(uuid.NAMESPACE_URL,'dreaming-v1:'+owner+':'+project+':'+case_key))
    revision=1;predecessor=None;prior=None
    if previous:
        candidate(previous);require(previous['candidate_id']==candidate_id,'case-identity-conflict')
        revision=previous['revision']+1;predecessor=digest(previous);prior=previous['prior_decision_ref']
        require(prior is None or decision is not None,'current-case-decision-required')
        if decision:
            shape(decision,{'state','candidate_hash','decision_ref','reopen_approved'})
            require(decision['candidate_hash']==digest(previous),'stale-case-decision')
            require(decision['state'] in ['rejected','implemented','accepted','deferred'],'unknown-decision')
            prior=decision['decision_ref']
            if decision['state'] in ['rejected','implemented']:
                if hashes=={r['sha256'] for r in previous['evidence_refs']}:
                    return record_decision(previous,decision)
                require(type(decision['reopen_approved']) is bool and decision['reopen_approved'],'reopening-needs-new-evidence-and-decision')
    readiness={}
    for consumer,fields in REQUIREMENTS.items():
        signals=context['signals'][consumer];missing=[x for x in fields if x not in signals]
        if consumer=='ledger' and context['work_id'] is None and 'canonical-identity' not in missing:missing.append('canonical-identity')
        if context['conflicts']:readiness[consumer]={'state':'needs-owner-decision','missing_fields':['resolve-evidence-conflicts']+missing,'evidence_hashes':list(dict.fromkeys(signals.values()))}
        else:readiness[consumer]={'state':'needs-evidence' if missing else 'ready-for-review','missing_fields':missing,'evidence_hashes':list(dict.fromkeys(signals.values()))}
    result={'schema_version':1,'candidate_id':candidate_id,'revision':revision,'predecessor_hash':predecessor,'owner_workspace_id':owner,
            'project_id':project,'intent':'enrich-case' if context['case_ref'] else 'new-case','case_ref':context['case_ref'],'work_id':context['work_id'],
            'evidence_refs':unique,**claims,'consumer_readiness':readiness,'privacy_state':'private','prior_decision_ref':prior}
    candidate(result)
    if previous and all(result[key]==previous[key] for key in result if key not in {'revision','predecessor_hash'}):return previous
    return result

def record_decision(value,decision):
    """Record a hash-bound history proposal; its contents never authorize a write."""
    import copy
    candidate(value);shape(decision,{'state','candidate_hash','decision_ref','reopen_approved'})
    require(decision['candidate_hash']==digest(value),'stale-case-decision')
    require(decision['state'] in {'rejected','implemented','accepted','deferred'} and isinstance(decision['decision_ref'],str) and decision['decision_ref'],'invalid-case-decision')
    result=copy.deepcopy(value);result.update(revision=value['revision']+1,predecessor_hash=digest(value),prior_decision_ref=decision['decision_ref'])
    if decision['state'] in {'rejected','implemented'}:
        for readiness in result['consumer_readiness'].values():
            readiness['state']='needs-owner-decision';readiness['missing_fields']=list(dict.fromkeys(readiness['missing_fields']+['prior-'+decision['state']+'-needs-new-evidence-and-decision']))
    return candidate(result)

def summary(value):
    candidate(value)
    return {'candidate_id':value['candidate_id'],'revision':value['revision'],'owner_workspace_id':value['owner_workspace_id'],
            'work_events':int(value['work_id'] is not None),'actual_seconds':None,
            'distinct_source_bytes':len({r['sha256'] for r in value['evidence_refs']}),
            'consumers':{k:v['state'] for k,v in value['consumer_readiness'].items()}}
