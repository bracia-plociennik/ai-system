"""Resolve advisory case proposals only from already guarded, cited source bytes."""
import uuid
from dreaming_provider_v1 import parse_json, digest, CONSUMERS
from dreaming_guard import need, hash_bytes


def finding_refs(finding, rows):
    refs=[row['source_ref'] for row in rows if row['source_ref'] and row['source_ref']['sha256'] in finding['source_hashes']]
    need(refs and {ref['sha256'] for ref in refs}==set(finding['source_hashes']),'unbound-project-finding')
    need(len({ref['project_id'] for ref in refs})==1,'mixed-project-finding')
    return refs


def documents(refs, actual):
    """No filesystem access; complete text comes from the verified provider snapshot."""
    result={}
    for ref in refs:
        if not ref['relative_path'].lower().endswith('.json'):continue
        chunks=sorted((c for c in actual['chunks'] if all(c['source_ref'][k]==ref[k] for k in ['source_root_id','relative_path','sha256'])),key=lambda c:c['start'])
        text=''.join(c['text'] for c in chunks);data=text.encode('utf-8')
        need(len(data)==ref['byte_count'] and hash_bytes(data)==ref['sha256'],'case-source-drift')
        try:value=parse_json(text)
        except (ValueError,TypeError):continue
        if isinstance(value,dict):result[ref['sha256']]=value
    return result


def empty_context():
    return dict(work_id=None,case_ref=None,signals={c:{} for c in CONSUMERS},conflicts=[])


def context_for(finding, refs, actual):
    owner=refs[0]['owner_workspace_id'];project=refs[0]['project_id']
    docs=documents(refs,actual)
    # Recognize native Work Entry records, not arbitrary prose or bare key names.
    identities=[]
    for h,doc in docs.items():
        required={'schema_version','entry_id','work_id','revision','owner_workspace','project_id','duration','source_refs','status'}
        if not required<=set(doc):continue
        if doc['owner_workspace']!=owner or doc['project_id']!=project:continue
        if type(doc['schema_version']) is not int or doc['schema_version']!=1:continue
        if type(doc['revision']) is not int or doc['revision']<1:continue
        try:
            if any(str(uuid.UUID(doc[key]))!=doc[key] for key in ['work_id','entry_id']):continue
        except (ValueError,TypeError,AttributeError):continue
        identities.append((doc['work_id'],doc['entry_id'],h))
    ctx=empty_context();keys={(work,case) for work,case,_ in identities}
    if len(keys)==1:
        ctx['work_id'],ctx['case_ref']=next(iter(keys))
        ctx['signals']['ledger']['canonical-identity']=identities[0][2]
    elif keys:ctx['conflicts']=['multiple-source-case-identities']
    # This is observed source identity only. Native preview verifies the real ledger.
    # Duration, approvals, replay, eligibility and consumer completion are never inferred.
    return ctx


def case_key(finding, ctx):
    if ctx['work_id'] is not None:return 'work-'+digest(ctx['work_id'])
    if ctx['case_ref'] is not None:return 'case-'+digest(ctx['case_ref'])
    return finding['finding_id']


def merge_context(left, right):
    result={**left,'signals':{c:dict(left['signals'][c]) for c in CONSUMERS},'conflicts':list(left['conflicts'])}
    result['conflicts'].extend(right['conflicts'])
    for field in ['work_id','case_ref']:
        if result[field] is None:result[field]=right[field]
        elif right[field] is not None and right[field]!=result[field]:result['conflicts'].append('conflicting-'+field)
    for consumer,signals in right['signals'].items():
        for field,h in signals.items():
            if field in result['signals'][consumer] and result['signals'][consumer][field]!=h:
                result['conflicts'].append('conflicting-readiness-'+consumer+'-'+field)
            else:result['signals'][consumer][field]=h
    result['conflicts']=list(dict.fromkeys(result['conflicts']))
    return result
