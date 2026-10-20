"""Deterministic, owner-private Dreaming sessions. No model or subprocess calls.

Trusted control/input files are separate from the model-writable draft directory.
All source reads use the existing v2 guard. Preparing a file is not reviewing it.
Only a validated checkpoint can advance coverage; every claim stays advisory.
"""
import argparse
import contextlib
from datetime import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import uuid
from collections import defaultdict, deque
from zoneinfo import ZoneInfo

from dreaming_universal_evidence import digest, findings, need, route
from dreaming_universal_sources import CREDENTIAL, chunks as source_chunks, config, inventory, read

ZONE = ZoneInfo('Europe/Warsaw')
BUDGET = 7200
RESERVE = 300
MAX_JSON = 32 * 1024 * 1024
MAX_CHUNKS = 128
MAX_INPUT_BYTES = 512 * 1024
CYCLE = re.compile(r'chat-(?:\d{4}-\d{2}-\d{2}|manual-\d{8}T\d{6}-[a-f0-9]{8})\Z')


def safe_directory(path):
    path = Path(path)
    need(path.is_absolute() and path == path.resolve(), 'unsafe-directory')
    for part in (path, *path.parents):
        need(not part.is_symlink(), 'linked-directory')
    return path


def mkdir(path):
    path = safe_directory(path)
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    need(path.is_dir() and path.stat().st_uid == os.getuid(), 'foreign-directory')
    return path


def read_bytes(path, limit=MAX_JSON):
    path = Path(path); safe_directory(path.parent)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        s = os.fstat(fd)
        need(stat.S_ISREG(s.st_mode) and s.st_nlink == 1 and
             s.st_uid == os.getuid() and s.st_size <= limit, 'unsafe-file')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            data = stream.read(limit + 1)
        need(len(data) <= limit, 'oversized-file')
        after = os.fstat(fd)
        need((s.st_size, s.st_mtime_ns, s.st_ctime_ns) ==
             (after.st_size, after.st_mtime_ns, after.st_ctime_ns), 'file-race')
        return data
    finally:
        os.close(fd)


def load(path):
    def unique(pairs):
        d = {}
        for k, v in pairs:
            need(k not in d, 'duplicate-json-key'); d[k] = v
        return d
    value=json.loads(read_bytes(path), object_pairs_hook=unique,
                     parse_constant=lambda _: need(False, 'invalid-json-number'))
    # Model drafts are always the strict, unextended checkpoint protocol.
    return value if Path(path).name=='checkpoint.json' else unpack_contexts(value)


def pack_contexts(value):
    """Store shared references/sets once, rather than once per finding/cycle."""
    if not isinstance(value,dict):return value
    result=dict(value);refs={};sets={}
    for field in ('findings','previous_findings'):
        if field not in value:continue
        rows=[]
        for f in value[field]:
            if 'context_refs' not in f:rows.append(f);continue
            ids=[]
            for ref in f['context_refs']:
                rid=digest(ref);refs[rid]=ref;ids.append(rid)
            ids=sorted(set(ids));sid=digest(ids);sets[sid]=ids
            rows.append({**{k:v for k,v in f.items() if k!='context_refs'},'_context_set':sid})
        result[field]=rows
    if sets:result['_context_registry']={'refs':refs,'sets':sets}
    return result


def unpack_contexts(value):
    if not isinstance(value,dict) or '_context_registry' not in value:return value
    result={k:v for k,v in value.items() if k!='_context_registry'};table=value['_context_registry']
    need(isinstance(table,dict) and set(table)=={'refs','sets'},'invalid-context-registry')
    refs=table['refs'];sets=table['sets']
    need(isinstance(refs,dict) and isinstance(sets,dict) and len(refs)<=200000,'invalid-context-registry')
    for rid,ref in refs.items():need(digest(ref)==rid,'context-reference-drift')
    for sid,ids in sets.items():
        need(isinstance(ids,list) and all(isinstance(x,str) and x in refs for x in ids) and
             ids==sorted(set(ids)) and digest(ids)==sid,'context-set-drift')
    expanded=0
    for field in ('findings','previous_findings'):
        if field not in result:continue
        rows=[]
        for f in result[field]:
            if '_context_set' not in f:rows.append(f);continue
            sid=f['_context_set'];need(sid in sets,'missing-context-set')
            expanded+=len(sets[sid]);need(expanded<=2000000,'context-expansion-limit')
            rows.append({**{k:v for k,v in f.items() if k!='_context_set'},'context_refs':[refs[x] for x in sets[sid]]})
        result[field]=rows
    return result


def atomic(path, value):
    path = Path(path); directory = mkdir(path.parent)
    if path.exists() or path.is_symlink():
        read_bytes(path)
    raw = (json.dumps(pack_contexts(value), ensure_ascii=False, allow_nan=False, indent=2) + '\n').encode()
    need(len(raw) <= MAX_JSON, 'oversized-state')
    temp = directory / ('.atomic-' + uuid.uuid4().hex)
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
        os.replace(temp, path)
        fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
        try: os.fsync(fd)
        finally: os.close(fd)
    finally:
        temp.unlink(missing_ok=True)


@contextlib.contextmanager
def lock(root,name='session.lock'):
    need(name in ('session.lock','cycle.lock'),'unsafe-lock-name')
    fd = os.open(mkdir(root) / name, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        s = os.fstat(fd)
        need(stat.S_ISREG(s.st_mode) and s.st_nlink == 1, 'unsafe-lock')
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    finally: os.close(fd)


def paths(cfg, cycle):
    need(isinstance(cycle, str) and CYCLE.fullmatch(cycle), 'invalid-cycle')
    base = safe_directory(Path(cfg['workspace']) / 'dreams')
    return {'control': base / 'chat-control',
            'state': base / 'chat-control' / (cycle + '.json'),
            'inputs': base / 'chat-inputs' / cycle,
            'drafts': base / 'chat-output' / cycle,
            'report': base / 'runs' / cycle}


def clock(): return datetime.now(ZONE)


def session_key(cfg):
    # Decisions can change between cycles without authorizing new source access.
    scripts=Path(__file__).parent
    implementation={name:hashlib.sha256((scripts/name).read_bytes()).hexdigest() for name in
                    ('dreaming_chat.py','dreaming_chat_dispatch.py','dreaming_universal_sources.py','dreaming_universal_evidence.py','dreaming_guard.py')}
    return digest({'configuration':{k:v for k,v in cfg.items() if k!='decisions'},
                   'implementation':implementation})


def begin(config_path, stamp=None, manual=False, cycle=None):
    cfg = config(load(config_path)); stamp = stamp or clock()
    need(stamp.tzinfo is not None, 'timezone-required'); stamp = stamp.astimezone(ZONE)
    if cycle is None:
        if manual:
            cycle = 'chat-manual-' + stamp.strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:8]
        else:
            need(stamp.weekday() in (2, 5) and stamp.hour == 2, 'outside-slot')
            cycle = 'chat-' + stamp.date().isoformat()
    p = paths(cfg, cycle)
    with lock(p['control']):
        if p['state'].exists():
            state = load(p['state'])
            need(state['config_digest'] == digest(cfg), 'configuration-revoked')
            need(state['scope_key'] == session_key(cfg),'implementation-drift')
            need(state['status'] in ('prepared', 'running', 'interrupted'), 'cycle-terminal')
            need(stamp.timestamp() < state['deadline'], 'session-deadline')
            state['attempt'] += 1
            atomic(p['state'], state)
            return cfg, state
        current = inventory(cfg)
        index_path = p['control'] / 'index.json'
        previous = load(index_path) if index_path.exists() else {'reviewed': {}, 'findings': []}
        # Never silently widen a retired registry through historical cached state.
        same_scope = previous.get('scope_key') == session_key(cfg)
        reviewed = previous['reviewed'] if same_scope else {}
        sources = {s['id']: s for s in cfg['sources']}
        chunks = []; eligible = []; coverage = []; by_file = {}
        total = 0; known_inventory=previous.get('inventory',{}) if same_scope else {}
        baseline=bool(previous.get('cycle_id')) and same_scope
        # Source contents are read once here; finalization performs one fresh check.
        for row in current:
            if row['state'] != 'pending':
                coverage.append(row); continue
            try:
                material = source_chunks(sources[row['source_id']], row, read(sources[row['source_id']], row))
            except (ValueError, OSError):
                coverage.append({**row, 'state': 'blocked'}); continue
            key = digest([row['source_id'], row['path']])
            fingerprint = material[0]['ref']['sha256']
            descriptor = {**row, 'key': key, 'sha256': fingerprint,
                          'chunk_ids': [c['chunk_id'] for c in material]}
            if reviewed.get(key) == fingerprint:
                coverage.append({**descriptor, 'state': 'reviewed'}); continue
            changed=key in reviewed and reviewed[key]!=fingerprint
            new=baseline and key not in known_inventory
            recent=not baseline and row.get('mtime_ns',0)>=int((stamp.timestamp()-7*86400)*1e9)
            priority=0 if changed or new or recent else 1
            eligible.append((priority, descriptor, material))
        eligible.sort(key=lambda x:(x[0],-x[1].get('mtime_ns',0) if x[0]==0 else x[1].get('mtime_ns',0),x[1]['key']))
        queues={0:defaultdict(deque),1:defaultdict(deque)}
        for priority, row, material in eligible:
            already = set(previous.get('partial', {}).get(row['key'], [])) if same_scope else set()
            already &= {c['chunk_id'] for c in material}
            remaining = [c for c in material if c['chunk_id'] not in already]
            by_file[row['key']] = {**row, 'all_chunk_ids': row['chunk_ids'], 'prior_chunk_ids': sorted(already),
                                  'selected_chunk_ids': []}
            queues[priority][row['source_id']].extend((row['key'],c) for c in remaining)
            coverage.append({**row, 'state': 'pending'})
        # Round robin across source roots prevents a large repository starving the
        # other approved perspectives. Priority material always precedes backlog.
        for priority in (0,1):
            active=deque(queues[priority])
            while active and len(chunks)<MAX_CHUNKS:
                sid=active.popleft();key,c=queues[priority][sid].popleft();size=len(c['text'].encode())
                if total+size<=MAX_INPUT_BYTES:
                    chunks.append(c);total+=size;by_file[key]['selected_chunk_ids'].append(c['chunk_id'])
                if queues[priority][sid]:active.append(sid)
        mkdir(p['inputs']); mkdir(p['drafts'])
        for c in chunks:
            atomic(p['inputs'] / (c['chunk_id'] + '.json'), c)
        state = {'schema_version': 1, 'cycle_id': cycle, 'attempt': 1, 'status': 'prepared',
                 'started_at': stamp.isoformat(), 'deadline': stamp.timestamp() + BUDGET,
                 'analysis_deadline': stamp.timestamp() + BUDGET - RESERVE,
                 'config_path': str(Path(config_path).absolute()), 'config_digest': digest(cfg),
                 'scope_key': session_key(cfg), 'input_hashes': {c['chunk_id']: digest(c) for c in chunks},
                 'files': by_file, 'coverage': coverage, 'accepted': [], 'findings': [],
                 'previous_findings': previous['findings'] if same_scope else [], 'checkpoint_revision': 0,
                 'manual': manual, 'authority': 'advisory-only', 'export_policy': 'owner-private-only'}
        brief = {k: state[k] for k in ('cycle_id','attempt','deadline','analysis_deadline','checkpoint_revision')}
        brief.update({'chunks': [{'chunk_id': c['chunk_id'], 'file': c['chunk_id'] + '.json',
                                  'source_id': c['ref']['source_id'], 'bytes': c['end'] - c['start']} for c in chunks],
                      'previous_findings': [{'finding_id': f['finding_id'], 'topic': f['topic'], 'lens': f['lens'],
                                             'summary': f['summary']} for f in state['previous_findings']][-100:],
                      'decisions': cfg['decisions'], 'source_count': len(cfg['sources']),
                      'selection_policy':'new/changed first; bootstrap last7 days; source round-robin; older backlog remains queued',
                      'checkpoint_contract': {'revision': 'consecutive integer from 1', 'cycle_id': cycle,
                                               'reviewed_chunk_ids': 'cumulative list actually reviewed',
                                               'findings': 'cumulative v2 findings; cite evidence_ids',
                                               'synthesis_complete': 'boolean'}})
        atomic(p['inputs'] / 'brief.json', brief)
        atomic(p['state'], state)
    return cfg, state


def accept(config_path, cycle, stamp=None, final=False):
    cfg = config(load(config_path)); p = paths(cfg, cycle); stamp = stamp or clock()
    with lock(p['control']):
        s = load(p['state']); need(s['config_digest'] == digest(cfg), 'configuration-revoked')
        need(s['scope_key'] == session_key(cfg),'implementation-drift')
        need(s['status'] in ('prepared','running','interrupted'), 'cycle-terminal')
        draft = load(p['drafts'] / 'checkpoint.json')
        need(isinstance(draft, dict) and set(draft) == {'cycle_id','revision','reviewed_chunk_ids','findings','synthesis_complete'}, 'invalid-checkpoint')
        need(draft['cycle_id'] == cycle and type(draft['revision']) is int, 'wrong-cycle')
        # Reconciliation after controller restart is idempotent and does not consume more budget.
        if draft['revision'] == s['checkpoint_revision']:
            need(digest(draft) == s.get('checkpoint_digest'), 'checkpoint-rewritten')
            if not final: return s
        else:
            # The model may publish several cumulative checkpoints between polls.
            need(draft['revision'] > s['checkpoint_revision'], 'checkpoint-reversed')
        ids = draft['reviewed_chunk_ids']
        need(isinstance(ids, list) and all(isinstance(x, str) for x in ids) and len(ids) == len(set(ids)), 'invalid-reviewed-chunks')
        need(set(s['accepted']) <= set(ids) <= set(s['input_hashes']), 'unprepared-evidence')
        need(type(draft['synthesis_complete']) is bool, 'invalid-synthesis-state')
        need(stamp.timestamp() <= s['deadline'], 'session-deadline')
        inputs = []
        for cid in ids:
            c = load(p['inputs'] / (cid + '.json')); need(digest(c) == s['input_hashes'][cid], 'snapshot-drift'); inputs.append(c)
        # This validates schema/evidence. It is not a claim that semantic QA can be automated.
        need(len(ids) > 0 or not draft['findings'], 'uncited-finding')
        items = findings({'findings': draft['findings']}, inputs, cfg['report_owner']) if inputs else []
        need({f['finding_id'] for f in s['findings']} <= {f['finding_id'] for f in items}, 'checkpoint-lost-findings')
        # Earlier findings shown in the brief are part of the model's context too.
        inherited = {digest(r):r for f in s['previous_findings'] for r in f['context_refs']}
        for item in items:
            context={digest(r):r for r in item['context_refs']}
            item['context_refs']=list({**inherited,**context}.values())
            item['audiences'] = [cfg['report_owner']]
            item['privacy'] = 'owner-private'
        encoded = json.dumps(draft, ensure_ascii=False).encode()
        need(not CREDENTIAL.search(encoded), 'credential-in-output')
        s.update({'accepted': ids, 'findings': items, 'checkpoint_revision': draft['revision'],
                  'checkpoint_digest': digest(draft), 'status': 'running',
                  'synthesis_complete': draft['synthesis_complete']})
        atomic(p['state'], s)
        if final:
            return finalize(cfg, s, p)
        return s


def finalize(cfg, s, p):
    sources = {r['id']: r for r in cfg['sources']}; changed = set()
    reviewed = {}; partial = {}
    old_index = p['control'] / 'index.json'
    old = load(old_index) if old_index.exists() else {}
    if old.get('scope_key') == session_key(cfg):
        reviewed.update(old.get('reviewed', {})); partial.update(old.get('partial', {}))
    # All reused current claims depend on a fresh hash check, including unchanged cache.
    rows = {(r['source_id'], r['path']): r for r in inventory(cfg)}
    refs = {}
    for item in s['findings'] + s['previous_findings']:
        for ref in item['context_refs']: refs[(ref['source_id'],ref['path'])] = ref
    for row in s['files'].values():
        refs[(row['source_id'],row['path'])] = row
    for row in s['coverage']:
        if row['state'] == 'reviewed': refs[(row['source_id'],row['path'])] = row
    for locator, ref in refs.items():
        row = rows.get(locator)
        try:
            need(row is not None and row['state'] == 'pending', 'source-unavailable')
            fresh = hashlib.sha256(read(sources[locator[0]], row)).hexdigest()
            need(fresh == ref['sha256'], 'source-changed')
        except (ValueError, OSError, KeyError): changed.add(locator)
    valid = [f for f in s['findings'] if not any((r['source_id'],r['path']) in changed for r in f['context_refs'])]
    cached = [f for f in s['previous_findings'] if not any((r['source_id'],r['path']) in changed for r in f['context_refs'])]
    # New observations replace a prior topic; recipient decisions stay in the registry.
    merged = {f['finding_id']: f for f in cached + valid}
    for key, row in s['files'].items():
        if (row['source_id'],row['path']) in changed:
            reviewed.pop(key, None); partial.pop(key, None); continue
        done = set(row['prior_chunk_ids']) | (set(row['selected_chunk_ids']) & set(s['accepted']))
        if set(row['all_chunk_ids']) <= done:
            reviewed[key] = row['sha256']; partial.pop(key, None)
        else: partial[key] = sorted(done)
    for row in s['coverage']:
        key = row.get('key')
        if key and (row['source_id'],row['path']) in changed: row['state'] = 'changed'
        elif key and reviewed.get(key) == row.get('sha256'): row['state'] = 'reviewed'
    count = {}
    for row in s['coverage']: count[row['state']] = count.get(row['state'], 0) + 1
    s.update({'status': 'completed' if s.get('synthesis_complete') and not changed else 'partial',
              'findings': list(merged.values()), 'coverage_counts': count, 'changed_count': len(changed),
              'finished_at': clock().isoformat()})
    mkdir(p['report'])
    atomic(p['report'] / 'findings.json', {'authority':'advisory-only','audience':cfg['report_owner'],
                                         'findings':s['findings'], 'decisions':cfg['decisions']})
    report = render_report(cfg, s)
    # Text uses the same guarded atomic writer without allowing model-selected paths.
    atomic(p['report'] / 'report.json', {'cycle_id':s['cycle_id'],'report':report,'coverage':count})
    target = p['report'] / 'dream-report.md'
    if target.exists() or target.is_symlink():
        need(read_bytes(target) == report.encode(), 'report-already-exists')
    else:
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'w') as stream: stream.write(report); stream.flush(); os.fsync(stream.fileno())
    atomic(old_index, {'scope_key':session_key(cfg),'reviewed':reviewed,'partial':partial,
                       'inventory':{digest([r['source_id'],r['path']]):r.get('sha256') for r in s['coverage']},
                       'findings':s['findings'],'cycle_id':s['cycle_id']})
    atomic(p['state'], s)
    return s


def render_report(cfg, s):
    from dreaming_universal_evidence import LENSES
    lines = ['# Dreaming — prywatny raport', '', 'Cykl: ' + s['cycle_id'],
             'Stan sesji: ' + s['status'], 'Pokrycie: ' + json.dumps(s['coverage_counts'],ensure_ascii=False),
             'Przygotowanie pliku nie oznacza jego przeanalizowania. Pokrycie analizy pochodzi z walidowanych deklaracji chatu.',
             'Ustalenia i działania są propozycjami; nie wykonano rekomendacji.',
             'Wynik pozostaje prywatny dla właściciela; brak automatycznych pakietów dla innych odbiorców.', '']
    packets = route(s['findings'], cfg['recipients'], cfg['report_owner'], cfg['decisions'])
    decisions = {d['finding_id']:d['state'] for d in packets[cfg['report_owner']]['decisions']}
    active = packets[cfg['report_owner']]['findings']
    prior = {f['finding_id']:f for f in s['previous_findings']}
    new = [f for f in active if f['finding_id'] not in prior]
    updated = [f for f in active if f['finding_id'] in prior and f['summary'] != prior[f['finding_id']]['summary']]
    lines += ['## Najważniejsze ustalenia', '',
              f'Nowe tematy: {len(new)}; zaktualizowane podsumowania: {len(updated)}.', '']
    selected = []; ordered = new + updated + active
    for lens in LENSES:
        item = next((f for f in ordered if f['lens']==lens),None)
        if item: selected.append(item)
    for f in ordered:
        if len(selected)>=10: break
        if f not in selected: selected.append(f)
    for f in selected: lines.append('- '+f['summary'])
    lines += ['', 'Odroczone, odrzucone i wdrożone propozycje nie są przedstawiane ponownie jako nowe działania.', '']
    for lens in LENSES:
        lines += ['## ' + {'person':'Osoba właściciela','brand':'Marka osobista','company':'Firma','systems':'Systemy i projekty'}[lens], '']
        fs = [f for f in active if f['lens'] == lens]
        if not fs: lines += ['Brak ustaleń w zweryfikowanym dotąd materiale.', '']
        for f in fs:
            lines += ['### ' + f['summary'], '', 'Rodzaj: ' + f['kind'] + '; decyzja: ' + decisions.get(f['finding_id'],'proposed')]
            for key, label in [('facts','Fakty'),('inferences','Interpretacje'),('unknowns','Niewiadome'),('actions','Propozycje')]:
                if f[key]: lines.append(label + ': ' + ' '.join(f[key]))
            for r in f['evidence_refs']:
                src = next(x for x in cfg['sources'] if x['id'] == r['source_id'])
                lines.append('- Dowód: [' + r['source_id'] + '](' + str(Path(src['root']) / r['path']) + '), SHA256 ' + r['sha256'])
            lines += ['ID: ' + f['finding_id'], '']
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['begin','accept','finalize','inspect'])
    parser.add_argument('--config', required=True); parser.add_argument('--cycle'); parser.add_argument('--manual',action='store_true')
    a = parser.parse_args()
    if a.action == 'begin': _, result = begin(a.config, manual=a.manual, cycle=a.cycle)
    elif a.action == 'inspect':
        cfg = config(load(a.config)); result = load(paths(cfg,a.cycle)['state'])
    else: result = accept(a.config,a.cycle,final=a.action == 'finalize')
    print(json.dumps({k:result[k] for k in ('cycle_id','status','attempt','checkpoint_revision','deadline')},ensure_ascii=False))


if __name__ == '__main__': main()
