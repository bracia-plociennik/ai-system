"""Explicit local WEP adapter; preview and current action authority remain separate."""
import argparse,json,sys,copy,uuid
from pathlib import Path
from dreaming_contracts import candidate,CONSUMERS
from dreaming_provider_v1 import digest,shape,require,ProtocolError
from dreaming_guard import registry,classification,read_file,hash_bytes
from dreaming_runner import load
from work_evidence import EvidenceError,digest as native_digest
from work_evidence_ledger import Ledger

def recheck(value,scope):
    candidate(value);registry(scope);require(scope['owner_workspace_id']==value['owner_workspace_id'],'cross-owner-selection')
    roots={r['source_root_id']:r for r in scope['roots']}
    for ref in value['evidence_refs']:
        require(ref['source_root_id'] in roots,'unregistered-source');root=roots[ref['source_root_id']]
        bindings=[b for b in root['bindings'] if b['project_id']==ref['project_id'] and b['owner_workspace_id']==ref['owner_workspace_id'] and (not b['prefix'] or ref['relative_path']==b['prefix'] or ref['relative_path'].startswith(b['prefix']+'/'))]
        require(len(bindings)==1,'ambiguous-source');binding=bindings[0]
        require(classification(scope,ref['relative_path'],binding)[0]=='pending','source-policy-denied')
        require(binding['source_class']==ref['source_class'],'class-drift')
        actual=read_file(root['locator'],ref['relative_path'],scope['limits']['file_bytes'])
        require(hash_bytes(actual)==ref['sha256'] and len(actual)==ref['byte_count'],'stale-candidate-source')

def native(ledger,consumer,request, *, write=False,expected=None,taxpayer=None):
    if consumer=='ledger':
        for change in request['changes']:
            entry=change['entry'];require(entry['duration']['basis'] in {'measured','owner-confirmed'} and type(entry['duration']['seconds']) is int,'needs-confirmed-time')
        if not write:return ledger.preview(request)
        prepared=ledger.prepare(request);result=ledger.apply(prepared['transaction_id'],prepared['manifest_hash'])
        return {'prepared':prepared,'receipt':result}
    if consumer=='documentation':
        from work_evidence_docs import assemble,persist
        return persist(ledger,request,expected,owner_approved=True) if write else assemble(ledger,request)
    if consumer=='report':
        from work_evidence_report import report,write_report
        return write_report(ledger,request,expected,owner_approved=True) if write else report(ledger,request)
    if consumer=='tax-evidence':
        from work_evidence_tax_evidence import TaxRegister
        register=TaxRegister(ledger.workspace,taxpayer)
        return register.write(request,expected,owner_approved=True) if write else register.packet(request)
    if consumer=='editorial':
        from work_evidence_editorial_v2 import editorial_version,bundle as bundle2,persist_bundle as persist2
        from work_evidence_editorial import bundle,persist_bundle
        build,persist=(bundle2,persist2) if editorial_version(request)==2 else (bundle,persist_bundle)
        return persist(ledger,request,expected,owner_approved=True) if write else build(ledger,request)
    raise ProtocolError('unsupported-consumer')

def native_hash(consumer,result):
    key={'documentation':'kit_hash','report':'draft_hash'}.get(consumer)
    return result[key] if key else native_digest(result)

def selection(ledger,value,scope,consumer,request):
    recheck(value,scope);require(consumer in CONSUMERS,'unsupported-consumer');require(ledger.config['workspace_id']==value['owner_workspace_id'],'cross-owner-destination')
    require(value['consumer_readiness'][consumer]['state']!='needs-owner-decision','unresolved-case-conflict')
    # A source-derived native entry link must exist in the destination, even when
    # a period report has no explicit entry IDs/texts. Source bytes are advisory.
    try:native_case=str(uuid.UUID(value['case_ref']))
    except (ValueError,TypeError,AttributeError):native_case=None
    if native_case is not None:
        committed=ledger.committed()[0]
        require(native_case in committed and committed[native_case]['work_id']==value['work_id'],'native-case-mismatch')
    allowed={(r['relative_path'],r['sha256']):r for r in value['evidence_refs']}
    roots={r['source_root_id']:r for r in scope['roots']}
    def visit(item):
        if isinstance(item,dict):
            if {'root_alias','relative_path','sha256'}<=set(item):
                ref=allowed.get((item['relative_path'],item['sha256']));require(ref is not None,'unselected-native-source')
                alias=item['root_alias'];require(alias in ledger.config['source_roots'] and Path(ledger.config['source_roots'][alias])==Path(roots[ref['source_root_id']]['locator']),'native-root-mismatch')
            for child in item.values():visit(child)
        elif isinstance(item,list):
            for child in item:visit(child)
    if consumer!='tax-evidence':visit(request)
    # Tax proofs remain inside the existing private TaxRegister and its native protocol;
    # Dreaming never ingests their bodies. Exact bundle/packet hash is reviewed separately.
    if consumer=='ledger':
        require(len(request['changes'])==1,'select-one-work-event')
        entry=request['changes'][0]['entry'];require(value['work_id'] is not None and entry['work_id']==value['work_id'],'native-work-mismatch')
    if consumer in {'editorial','documentation','tax-evidence','report'}:
        entries=ledger.committed()[0]
        def entries_check(item):
            if isinstance(item,dict):
                if 'entry_id' in item:
                    require(item['entry_id'] in entries and value['work_id'] is not None and entries[item['entry_id']]['work_id']==value['work_id'],'native-case-mismatch')
                if 'work_id' in item:
                    require(value['work_id'] is not None and item['work_id']==value['work_id'] and any(e['work_id']==item['work_id'] for e in entries.values()),'native-case-mismatch')
                if 'work_ids' in item:
                    require(isinstance(item['work_ids'],list) and all(value['work_id'] is not None and work==value['work_id'] and any(e['work_id']==work for e in entries.values()) for work in item['work_ids']),'native-case-mismatch')
                if 'entry_ids' in item:
                    require(isinstance(item['entry_ids'],list) and all(key in entries and value['work_id'] is not None and entries[key]['work_id']==value['work_id'] for key in item['entry_ids']),'native-case-mismatch')
                for child in item.values():entries_check(child)
            elif isinstance(item,list):
                for child in item:entries_check(child)
        entries_check(request)

def preview(workspace,value,scope,consumer,request,taxpayer=None):
    ledger=Ledger(workspace);selection(ledger,value,scope,consumer,request)
    result=native(ledger,consumer,request,taxpayer=taxpayer)
    binding={'schema_version':1,'candidate_id':value['candidate_id'],'candidate_hash':digest(value),'candidate_revision':value['revision'],
             'owner_workspace_id':value['owner_workspace_id'],'workspace':str(ledger.workspace),'consumer':consumer,'operation':'write',
             'request_hash':digest(request),'scope_digest':digest(scope),'source_versions':[r['sha256'] for r in value['evidence_refs']],
             'native_hash':native_hash(consumer,result),'taxpayer':taxpayer}
    return {'binding':binding,'preview_hash':digest(binding),'native_preview':result,
            'missing_evidence':value['consumer_readiness'][consumer]['missing_fields'],'authority':'preview-only'}

def apply(workspace,value,scope,consumer,request,binding,approved_preview_hash,*,owner_approved=False):
    require(owner_approved,'current-scoped-approval-required');require(digest(binding)==approved_preview_hash,'stale-action-approval')
    expected_fields={'schema_version','candidate_id','candidate_hash','candidate_revision','owner_workspace_id','workspace','consumer','operation','request_hash','scope_digest','source_versions','native_hash','taxpayer'};shape(binding,expected_fields)
    require(binding['candidate_hash']==digest(value) and binding['request_hash']==digest(request) and binding['scope_digest']==digest(scope) and binding['consumer']==consumer and binding['operation']=='write','action-version-mismatch')
    ledger=Ledger(workspace);require(binding['workspace']==str(ledger.workspace),'destination-drift');selection(ledger,value,scope,consumer,request)
    # The native protocol rechecks current source/config/entry versions under its own locks.
    if consumer!='ledger':
        current=native(ledger,consumer,request,taxpayer=binding['taxpayer']);require(native_hash(consumer,current)==binding['native_hash'],'native-preview-drift')
    else:
        # Native prepare/apply is idempotent and verifies candidate sources and predecessor.
        # Before first prepare, validate current preview; after a completed retry the native receipt is authoritative.
        try:current=native(ledger,consumer,request);require(native_digest(current)==binding['native_hash'],'native-preview-drift')
        except EvidenceError:
            committed=ledger.committed()[0];entry=request['changes'][0]['entry'];require(entry['entry_id'] in committed and committed[entry['entry_id']]==entry,'native-transaction-needs-recovery')
    result=native(ledger,consumer,request,write=True,expected=binding['native_hash'],taxpayer=binding['taxpayer'])
    successor=copy.deepcopy(value);successor.update(revision=value['revision']+1,predecessor_hash=digest(value),prior_decision_ref='native-receipt-'+digest(result))
    candidate(successor)
    return {'native_receipt':result,'successor_candidate':successor,'state':'native-local-write','publication':'not-authorized'}

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['preview','apply']);p.add_argument('--workspace',required=True);p.add_argument('--request',required=True);p.add_argument('--expected-hash');p.add_argument('--owner-approved',action='store_true');args=p.parse_args()
    try:
        v=load(args.request);shape(v,{'candidate','scope','consumer','native_request'},{'taxpayer','binding'})
        if args.action=='preview':result=preview(args.workspace,v['candidate'],v['scope'],v['consumer'],v['native_request'],v.get('taxpayer'))
        else:result=apply(args.workspace,v['candidate'],v['scope'],v['consumer'],v['native_request'],v['binding'],args.expected_hash,owner_approved=args.owner_approved)
        print(json.dumps(result,ensure_ascii=False,sort_keys=True));return 0
    except (OSError,ValueError,TypeError,KeyError):print(json.dumps({'error':'promotion-held'}),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
