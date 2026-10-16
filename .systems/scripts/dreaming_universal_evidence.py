"""Universal v2 proposal protocol. Provenance determines privacy and recipients.

Mirrored byte-for-byte in the two products, like dreaming_guard.py. No I/O,
execution, authority changes or WEP time inference occurs in this interface.
"""
import hashlib
import json
import re
import uuid

LENSES = ('person', 'brand', 'company', 'systems')
KINDS = ('keep', 'improve', 'stop', 'try', 'unknown')
DECISIONS = ('proposed', 'accepted', 'deferred', 'rejected', 'implemented')


def need(ok, code):
    if not ok:
        raise ValueError(code)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def slug(value):
    need(isinstance(value, str) and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', value), 'invalid-identity')
    return value


def texts(value):
    need(isinstance(value, list) and len(value) <= 40 and
         all(isinstance(x, str) and 0 < len(x) <= 4000 for x in value), 'invalid-claims')


def response_schema():
    item = {'type': 'object', 'additionalProperties': False, 'properties': {
        'topic': {'type': 'string'}, 'lens': {'type': 'string', 'enum': list(LENSES)},
        'kind': {'type': 'string', 'enum': list(KINDS)}, 'summary': {'type': 'string'},
        **{k: {'type': 'array', 'items': {'type': 'string'}} for k in
           ('facts', 'inferences', 'unknowns', 'actions', 'evidence_ids')}}}
    item['required'] = list(item['properties'])
    return {'type': 'object', 'additionalProperties': False,
            'properties': {'findings': {'type': 'array', 'items': item}}, 'required': ['findings']}


def findings(response, chunks, report_owner):
    need(isinstance(response, dict) and set(response) == {'findings'} and
         isinstance(response['findings'], list) and len(response['findings']) <= 100, 'invalid-response')
    known = {c['chunk_id']: c for c in chunks}
    result = []
    seen = set()
    for raw in response['findings']:
        need(isinstance(raw, dict) and set(raw) == set(response_schema()['properties']['findings']['items']['required']),
             'invalid-finding')
        slug(raw['topic'])
        need(raw['lens'] in LENSES and raw['kind'] in KINDS, 'invalid-lens-kind')
        need(isinstance(raw['summary'], str) and 0 < len(raw['summary']) <= 4000, 'invalid-summary')
        for key in ('facts', 'inferences', 'unknowns', 'actions'):
            texts(raw[key])
        ids = raw['evidence_ids']
        need(isinstance(ids, list) and ids and len(set(ids)) == len(ids) and
             all(isinstance(x, str) and x in known for x in ids), 'uncited-finding')
        refs = [ref for x in ids for ref in known[x].get('refs', [known[x].get('ref')])]
        owners = sorted({r['owner'] for r in refs})
        # Each source's recipients were established before the model call.
        context_refs = [r for c in chunks for r in c.get('context_refs', c.get('refs', [c.get('ref')]))]
        audiences = set.intersection(*(set(r['audiences']) for r in context_refs))
        personal = any(r['source_class'] == 'personal' for r in context_refs)
        if personal:
            audiences &= {report_owner}
        need(report_owner in audiences, 'unshared-owner-finding')
        key = [owners, sorted({(r['subject_type'], r['subject_id']) for r in refs}), raw['lens'], raw['topic']]
        fid = str(uuid.uuid5(uuid.NAMESPACE_URL, 'dreaming-v2:' + digest(key)))
        need(fid not in seen, 'duplicate-finding')
        seen.add(fid)
        result.append({**raw, 'finding_id': fid, 'owners': owners,
                       'privacy': 'personal' if personal else 'owner-private',
                       'audiences': sorted(audiences), 'evidence_refs': refs, 'context_refs': context_refs,
                       'distinct_source_contents': len({r['sha256'] for r in refs}),
                       'authority': 'advisory-only'})
    return result


def route(items, recipients, report_owner, decisions=()):
    """Independent recipient state; a prior rejection is never reopened here."""
    states = {}
    for d in decisions:
        need(isinstance(d, dict) and {'finding_id', 'recipient', 'state', 'authority_ref'} <= set(d) <= {'finding_id', 'recipient', 'state', 'authority_ref', 'quality_evidence'},
             'invalid-decision')
        need(d['state'] in DECISIONS and isinstance(d['authority_ref'], str) and d['authority_ref'],
             'unbound-decision')
        if d['state'] == 'implemented':
            evidence = d.get('quality_evidence')
            need(isinstance(evidence, dict) and set(evidence) == {'source_id', 'path', 'sha256'} and all(isinstance(v, str) and v for v in evidence.values()) and re.fullmatch('[0-9a-f]{64}', evidence['sha256']), 'implemented-needs-quality-evidence')
        need((d['finding_id'], d['recipient']) not in states, 'conflicting-decision')
        states[d['finding_id'], d['recipient']] = d
    packets = {r: {'schema_version': 2, 'recipient': r, 'authority': 'advisory-only',
                   'findings': [], 'decisions': []} for r in recipients}
    for item in items:
        for rid, spec in recipients.items():
            if rid not in item['audiences'] or item['lens'] not in spec['lenses']:
                continue
            if item['privacy'] == 'personal' and rid != report_owner:
                continue
            decision = states.get((item['finding_id'], rid))
            state = decision['state'] if decision else 'proposed'
            if decision:
                packets[rid]['decisions'].append(decision)
            if state in ('rejected', 'deferred', 'implemented'):
                continue
            packets[rid]['findings'].append({**item, 'state': state})
    return packets
