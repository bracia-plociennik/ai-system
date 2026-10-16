"""Verify completed universal bundles without opening any original source body."""
import argparse
import json
import sys
from pathlib import Path
from dreaming_guard import read_file, hash_bytes
from dreaming_runner import directory, load
from dreaming_universal_evidence import need, digest, route
from dreaming_universal_sources import relative, CREDENTIAL


def verify(workspace, run_id):
    path = directory(workspace, run_id)
    completion = load(path/'completion.json'); state = load(path/'state.json')
    need(completion.get('schema_version') == state.get('schema_version') == 2 and completion.get('run_id') == run_id, 'invalid-universal-bundle')
    need(digest(state) == completion['state_digest'], 'completed-state-drift')
    cfg = state['config']; need(digest(cfg) == completion['config_digest'], 'completed-config-drift')
    artifacts = {}
    need(set(completion['artifact_digests']) == {'report.json','inventory.json','packets.json'}, 'incomplete-universal-bundle')
    for name, expected in completion['artifact_digests'].items():
        value = load(path/name); need(digest(value) == expected, 'completed-artifact-drift'); artifacts[name] = value
    text = read_file(str(path), 'dream-report.md', 67108864, prescreen=False)
    need(hash_bytes(text) == completion['markdown_sha256'], 'completed-report-drift')
    need(not CREDENTIAL.search(text), 'credential-in-report')
    report = artifacts['report.json']; rows = artifacts['inventory.json']; packets = artifacts['packets.json']
    need(report['schema_version'] == 2 and report['run_id'] == run_id and report['result'] == completion['result'], 'report-identity-mismatch')
    need(report['authority'] == 'advisory-only', 'report-authority-mismatch')
    counts = {key:sum(r['state']==key for r in rows) for key in ('reviewed','pending','excluded','unsupported','blocked','missing')}
    need(report['coverage'] == counts and len(rows) == sum(counts.values()), 'coverage-mismatch')
    if report['result'] == 'complete':
        need(report['enumeration_complete'] and report['synthesis_complete'] and rows and not report['errors'] and not any(counts[k] for k in counts if k not in ('reviewed','excluded')), 'false-complete')
    current = set(report['current_receipts']); chunks = {}
    for name, expected in state['receipts'].items():
        need(Path(name).name == name and name.startswith('receipt-') and name.endswith('.json'), 'unsafe-receipt')
        receipt = load(path/name); need(digest(receipt) == expected, 'receipt-drift')
        if expected not in current: continue
        if receipt['kind'] == 'analysis':
            for c in receipt['chunks']: chunks[c['chunk_id']] = c
    need(current <= set(state['receipts'].values()), 'unbound-current-receipt')
    refs = [c['ref'] for c in chunks.values()]
    for row in rows:
        if row['state'] == 'reviewed': need(row.get('chunk_ids') and set(row['chunk_ids']) <= set(chunks), 'false-reviewed-source')
    sources = {s['id']:s for s in cfg['sources']}
    for f in report['findings']:
        need(f['authority'] == 'advisory-only' and f['evidence_refs'] and f['context_refs'], 'unbound-finding')
        for ref in f['evidence_refs']+f['context_refs']:
            need(ref in refs, 'unbound-finding-ref')
            source = sources[ref['source_id']]; relative(ref['path'])
            prefix = source['prefix']
            need(ref['path'] == prefix or ref['path'].startswith(prefix+'/'), 'out-of-scope-finding')
            need(all(ref[k] == source[field] for k,field in (('owner','owner'),('subject_id','subject_id'),('subject_type','subject_type'),('source_class','source_class'),('audiences','audiences'))), 'finding-owner-drift')
            need(ref.get('native_owner_id') == source.get('native_owner_id'), 'native-owner-alias-drift')
        expected = set.intersection(*(set(r['audiences']) for r in f['context_refs']))
        personal = any(r['source_class'] == 'personal' for r in f['context_refs'])
        if personal: expected &= {cfg['report_owner']}
        need(set(f['audiences']) == expected and (f['privacy']=='personal') == personal, 'finding-privacy-drift')
    expected = route(report['findings'],cfg['recipients'],cfg['report_owner'],state['decisions'])
    need(set(packets)==set(expected),'recipient-drift')
    for rid, packet in packets.items():
        need(all(packet[k] == expected[rid][k] for k in expected[rid]), 'packet-routing-drift')
        need(not CREDENTIAL.search(json.dumps(packet).encode()), 'credential-in-packet')
        if 'wep_candidates' in packet:
            from dreaming_contracts import candidate
            allowed = {(r['source_id'],r['path'],r['sha256']) for f in packet['findings'] for r in f['evidence_refs']}
            for item in packet['wep_candidates']:
                candidate(item)
                need(all((r['source_root_id'],r['relative_path'],r['sha256']) in allowed for r in item['evidence_refs']), 'unbound-wep-candidate')
    return {'schema_version':2,'run_id':run_id,'result':report['result'],'bundle_verified':True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace',required=True);parser.add_argument('--run-id',required=True)
    args=parser.parse_args()
    try: print(json.dumps(verify(args.workspace,args.run_id)));return 0
    except (OSError,ValueError,TypeError,KeyError):
        print('Universal Dreaming bundle verification failed.',file=sys.stderr);return 2


if __name__=='__main__':raise SystemExit(main())
