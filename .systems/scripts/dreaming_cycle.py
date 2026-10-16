"""One universal, advisory-only Dreaming cycle. Only dreams/runs is writable.

Existing v1 report/receipt/candidate interfaces remain independent. v2 artifacts
are explicit, private and immutable after completion; receipt checkpoints allow
history progress to survive an interrupted process without pretending completion.
"""
import argparse
import contextlib
import fcntl
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from dreaming_guard import open_root, read_file, hash_bytes
from dreaming_runner import directory, save, load
from dreaming_universal_evidence import need, digest, findings, route, LENSES
from dreaming_universal_sources import config, inventory, read, chunks, CREDENTIAL
from dreaming_analyzer import CodexAnalyzer

ZONE = ZoneInfo('Europe/Warsaw')
BUDGET = 7200
RESERVE = 300
BATCH_BYTES = 65536


def implementation_digest():
    root = Path(__file__).parent
    names = ('dreaming_cycle.py', 'dreaming_universal_sources.py', 'dreaming_universal_evidence.py',
             'dreaming_analyzer.py', 'dreaming_guard.py', 'dreaming_runner.py', 'dreaming_provider_v1.py',
             'dreaming_candidates.py', 'dreaming_contracts.py', 'dreaming_case_resolver.py')
    binding = {p: hash_bytes((root/p).read_bytes()) for p in names}
    for rel in ('ai/core/dreaming-mode.md', 'ai/templates/dreaming/universal/v2/README.md'):
        binding[rel] = hash_bytes((root.parent/rel).read_bytes())
    binding['python'] = sys.version
    return digest(binding)


def slot(stamp):
    local = stamp.astimezone(ZONE)
    if local.weekday() not in (2, 5) or local.hour != 2 or local.minute >= 5:
        return None
    return 'universal-' + local.date().isoformat()


def error_code(exc):
    text = str(exc) if isinstance(exc, ValueError) else ''
    return text if re.fullmatch('[a-z][a-z0-9-]{0,79}', text) else 'operation-unavailable'


@contextlib.contextmanager
def cycle_lock(workspace):
    path = directory(workspace, 'universal-control', True)
    fd = open_root(str(path))
    lock = os.open('cycle.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600, dir_fd=fd)
    try:
        try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError: raise ValueError('cycle-already-running') from None
        yield
    finally:
        os.close(lock); os.close(fd)


def state_save(path, value):
    # Reuse the established dirfd/no-follow/atomic broker writer.
    save(path, 'state.json', value)


def previous(workspace, key, current):
    """Only byte-bound v2 checkpoints; never ingest legacy reports as raw truth."""
    runs = Path(workspace)/'dreams/runs'
    candidates = sorted((p for p in runs.iterdir() if p.name.startswith('universal-') and
                         p.name != current and p.name != 'universal-control'), reverse=True)
    for path in candidates:
        if path.is_symlink() or not (path/'state.json').is_file(): continue
        state = load(path/'state.json')
        if state.get('schema_version') != 2 or state.get('analysis_key') != key: continue
        receipts = []
        for name, expected in state['receipts'].items():
            need(re.fullmatch(r'receipt-[0-9]{6}\.json', name), 'invalid-receipt-name')
            receipt = load(path/name)
            need(digest(receipt) == expected, 'receipt-drift')
            receipts.append(receipt)
        return state, receipts
    return {}, []


def model_call(analyzer, batch, context, deadline, clock):
    for attempt in range(2):
        remaining = deadline-clock()
        need(remaining > 0, 'analysis-deadline')
        try:
            response = analyzer(batch, context, remaining)
            need(clock() < deadline, 'analysis-deadline')
            return response
        except ValueError as exc:
            if attempt or str(exc) != 'analyzer-unavailable': raise
    raise ValueError('analyzer-unavailable')


def batches(items):
    batch = []; size = 0
    for item in items:
        length = len(json.dumps(item, ensure_ascii=False).encode()) + (item.get('end', 0)-item.get('start', 0) if 'text' not in item else 0)
        need(length <= BATCH_BYTES, 'oversized-analysis-input')
        if batch and size+length > BATCH_BYTES:
            yield batch; batch = []; size = 0
        batch.append(item); size += length
    if batch: yield batch


def wep_packets(items, source_chunks):
    """Use native v1 case resolution, only with one explicit project/owner.

    Durations and time approval are deliberately absent. Generic or mixed-project
    observations remain universal proposals, never coerced into WEP identities.
    """
    from dreaming_case_resolver import context_for, case_key
    from dreaming_candidates import reconcile
    result = []; groups = {}
    for item in items:
        refs = item['evidence_refs']
        if not refs or any(r['subject_type'] != 'project' or r['source_class'] == 'personal' for r in refs): continue
        if len({(r['owner'], r['subject_id']) for r in refs}) != 1: continue
        aliases = {r['native_owner_id'] for r in refs if r.get('native_owner_id')}
        if len(aliases) > 1: continue
        native_owner = next(iter(aliases)) if aliases else refs[0]['owner']
        converted = []
        for r in refs:
            ref = {'source_root_id': r['source_id'], 'relative_path': r['path'],
                   'project_id': r['subject_id'], 'owner_workspace_id': native_owner,
                   'sha256': r['sha256'], 'byte_count': r['byte_count'],
                   'observed_at': datetime.now(timezone.utc).isoformat(), 'fact_date': 'unknown',
                   'evidence_level': 'inference', 'source_class': 'source' if r['source_class'] == 'source' else 'work'}
            if ref not in converted: converted.append(ref)
        actual = {'chunks': [], 'native_metadata': []}
        for chunk in source_chunks:
            matches = [r for r in converted if r['sha256'] == chunk['ref']['sha256'] and
                       r['relative_path'] == chunk['ref']['path'] and r['source_root_id'] == chunk['ref']['source_id']]
            if matches: actual['chunks'].append({**chunk, 'source_ref': matches[0]})
        f = {'finding_id': 'universal-' + item['finding_id'], 'source_hashes': list({r['sha256'] for r in converted}),
             'facts': item['facts'], 'inferences': item['inferences'], 'unknowns': item['unknowns'],
             'native_state': 'unknown', 'native_quality': 'unknown'}
        # Case parsing requires complete bytes. Partial source coverage supplies no native identity.
        complete = all(sum(c['end']-c['start'] for c in actual['chunks'] if c['source_ref'] == r) == r['byte_count'] for r in converted if r['relative_path'].endswith('.json'))
        from dreaming_case_resolver import empty_context, merge_context
        ctx = context_for(f, converted, actual) if complete else empty_context()
        key = (converted[0]['owner_workspace_id'], converted[0]['project_id'], case_key(f, ctx))
        claims = {label: [{'text': t, 'source_hashes': f['source_hashes'], 'evidence_level': level}
                          for t in item[label]] for label, level in
                  (('facts', 'observed'), ('inferences', 'inference'), ('unknowns', 'unknown'))}
        if key not in groups: groups[key] = [converted, claims, ctx]
        else:
            group = groups[key]; group[0].extend(r for r in converted if r not in group[0]); group[2] = merge_context(group[2], ctx)
            for label in claims: group[1][label].extend(c for c in claims[label] if c not in group[1][label])
    for (owner, project, key), (refs, claims, ctx) in groups.items():
        result.append(reconcile(owner, project, key, refs, claims, ctx))
    return result


def markdown(report, owner_packet):
    counts = report['coverage']
    lines = ['# Dream Report — ' + report['run_id'], '', 'Wynik: ' + report['result'],
             'Tryb: prywatne propozycje dla właściciela.', '',
             f"Pokrycie: {counts['reviewed']} przeanalizowanych, {counts['pending']} oczekujących; "
             f"{counts['excluded']} wyłączonych, {counts['unsupported']} nieobsługiwanych, "
             f"{counts['blocked']} zablokowanych, {counts['missing']} brakujących.",
             'Pełna historia: ' + ('pokryta w dopuszczonym zakresie' if report['result'] == 'complete' else 'niepełna; szczegóły w report.json'),
             'Historycznie przeanalizowane źródła: ' + str(report.get('history_reviewed', 0)) + '. Bieżące pokrycie wymaga świeżego sprawdzenia źródeł.', '']
    if report.get('scope_gaps'): lines += ['Luki manifestu: ' + str(report['scope_gaps'].get('task_unknown_owner_count', 0)) + ' zadań z nieustaloną własnością; nie wchodzą do zatwierdzonego zakresu.', '']
    if report['errors']: lines += ['Ograniczenia: ' + ', '.join(report['errors']), '']
    labels = {'person': 'Kuba — osoba i sposób działania', 'brand': 'Marka osobista',
              'company': 'Onlinen', 'systems': 'Systemy i projekty'}
    verbs = {'keep': 'Utrzymać', 'improve': 'Poprawić', 'stop': 'Zaprzestać', 'try': 'Spróbować', 'unknown': 'Nie wiemy'}
    for lens in LENSES:
        items = [f for f in owner_packet['findings'] if f['lens'] == lens]
        lines += ['## ' + labels[lens], '']
        if not items: lines += ['Brak ustaleń popartych dostępnymi dowodami w tym cyklu.', '']
        for f in items[:12]:
            lines += [f"- **{verbs[f['kind']]}:** {f['summary']}",
                      '  Dowody: ' + ', '.join(sorted({r['source_id'] + ':' + r['path'] + '#' + r['sha256'][:12] for r in f['evidence_refs']})),
                      '  Status: ' + ('nowe lub zmienione' if f['finding_id'] in report['changed_findings'] else 'wcześniejsze ustalenie') + '; ' + f['state'] + '.']
            if f['inferences']: lines += ['  Interpretacje: ' + '; '.join(f['inferences'])]
            if f['unknowns']: lines += ['  Niewiadome: ' + '; '.join(f['unknowns'])]
        if len(items) > 12: lines += [f'Dalsze {len(items)-12} ustaleń: report.json.']
        lines += ['']
    lines += ['## Decyzje i dalsze działania', '',
              'Pakiety odbiorców są propozycjami. Przyjęcie nie uruchamia zmian w źródłach ani w WEP.',
              'Wcześniejsze odrzucenia/odroczenia pozostają w historii pakietów.', '']
    return '\n'.join(lines)


def run(value, analyzer=None, stamp=None, manual=False, clock=time.monotonic):
    config(value)
    route([], value['recipients'], value['report_owner'], value['decisions'])
    stamp = stamp or datetime.now(ZONE)
    run_id = ('universal-manual-' + stamp.astimezone(ZONE).strftime('%Y-%m-%d-%H%M%S')) if manual else slot(stamp)
    if not run_id: return {'result': 'skipped', 'reason': 'outside-scheduled-window'}
    start = clock(); deadline = start+BUDGET-RESERVE
    key = digest({'config': {k: v for k, v in value.items() if k != 'decisions'}, 'implementation': implementation_digest()})
    with cycle_lock(value['workspace']):
        path = directory(value['workspace'], run_id, True)
        if (path/'completion.json').exists():
            completion = load(path/'completion.json')
            need(completion['config_digest'] == digest(value), 'run-config-conflict')
            for name, expected in completion['artifact_digests'].items():
                need(name in ('report.json', 'inventory.json', 'packets.json') and digest(load(path/name)) == expected, 'completed-artifact-drift')
            need(hash_bytes(read_file(str(path), 'dream-report.md', 67108864, prescreen=False)) == completion['markdown_sha256'], 'completed-report-drift')
            return completion
        need(not (path/'state.json').exists(), 'interrupted-slot-next-cycle-required')
        state = {'schema_version': 2, 'analysis_key': key, 'config_digest': digest(value),
                 'receipts': {}, 'inventory': [], 'decisions': value['decisions'], 'config': value, 'started_at': stamp.isoformat()}
        state_save(path, state)
        old_state = {}; old_receipts = []; current = []; records = []; raw_chunks = []; errors = []
        enumeration_complete = False; synthesis_complete = False
        analyzer = analyzer or CodexAnalyzer(value['analyzer'])
        def check(): need(clock() < deadline, 'analysis-deadline')
        def checkpoint(receipt):
            name = f'receipt-{len(state["receipts"]):06d}.json'
            save(path, name, receipt); state['receipts'][name] = digest(receipt)
            records.append(receipt); state_save(path, state)
        try:
            analyzer.preflight()  # Absolutely before any private source body or historical result read.
            if isinstance(analyzer, CodexAnalyzer):
                authority = value.get('model_data_authority', {})
                need(authority.get('provider') == 'openai-codex' and authority.get('authority_ref') and (manual or authority.get('scope') == 'recurring'), 'model-data-authority-required')
            old_state, old_receipts = previous(value['workspace'], key, run_id)
            state['decisions'] = merge_decisions(old_state.get('decisions', []), value['decisions'])
            current = inventory(value, check); enumeration_complete = True
            sources = {s['id']: s for s in value['sources']}
            old_rows = {(r['source_id'], r['path']): r for r in old_state.get('inventory', [])}
            row_map = {(r['source_id'], r['path']): r for r in current}
            for row in current:
                prior = old_rows.get((row['source_id'], row['path']), {})
                row['history_reviewed'] = bool(prior.get('history_reviewed') or prior.get('state') == 'reviewed')
            # Retained checkpoints preserve historical progress across partitions. They are
            # NOT current evidence until their entire input closure has been rechecked.
            for receipt in old_receipts:
                if receipt['kind'] != 'analysis': continue
                name = f'receipt-{len(state["receipts"]):06d}.json'
                save(path, name, receipt); state['receipts'][name] = digest(receipt)
            state['inventory'] = current
            for decision in state['decisions']:
                if decision['state'] != 'implemented': continue
                proof = decision['quality_evidence']; src = sources.get(proof['source_id'])
                row = row_map.get((proof['source_id'], proof['path']))
                need(src is not None and row is not None and row['state'] == 'pending', 'quality-evidence-out-of-scope')
                need(hash_bytes(read(src, row)) == proof['sha256'], 'quality-evidence-drift')
            state_save(path, state)
            old_chunks = {c['chunk_id']: receipt for receipt in old_receipts if receipt['kind'] == 'analysis' for c in receipt['chunks']}
            available = {}; loaded_paths = set(); reviewed = set(); tried = set(); buffers = {}
            cursor = tuple(old_state.get('scan_cursor', []))
            def scan_priority(row):
                key = (row['source_id'], row['path']); prior = old_rows.get(key)
                changed = prior is not None and any(prior.get(k) != row.get(k) for k in ('size', 'mtime_ns'))
                return (0 if changed else 2 if row['history_reviewed'] else 1,
                        0 if not cursor or key > cursor else 1, *key)
            def remember(row):
                key = (row['source_id'], row['path'])
                if key in loaded_paths: return
                check(); source = sources[row['source_id']]
                data = read(source, row)
                described = [{k: v for k, v in c.items() if k != 'text'} for c in chunks(source, row, data)]
                row['sha256'] = hash_bytes(data); row['chunk_ids'] = [c['chunk_id'] for c in described]
                for c in described: available[c['chunk_id']] = c
                raw_chunks.extend(described); loaded_paths.add(key)
            def reuse(receipt):
                rid = digest(receipt)
                if rid in tried: return
                tried.add(rid)
                try:
                    for c in receipt['chunks']:
                        r = c['ref']; row = row_map.get((r['source_id'], r['path']))
                        need(row is not None and row['state'] == 'pending', 'prior-source-unavailable')
                        remember(row)
                    need(all(c['chunk_id'] in available and available[c['chunk_id']] == c for c in receipt['chunks']), 'prior-source-drift')
                    records.append(receipt); reviewed.update(c['chunk_id'] for c in receipt['chunks'])
                except (OSError, ValueError):
                    if clock() >= deadline: raise ValueError('analysis-deadline') from None
            def flush(audience):
                waiting = [c for c in buffers.pop(audience, []) if c['chunk_id'] not in reviewed]
                for batch in batches(waiting):
                    check()
                    try:
                        delivered = materialize(batch, sources)
                        prior_topics = [{'topic': f['topic'], 'lens': f['lens']} for rec in records for f in rec['findings'] if set(audience) <= set(f['audiences']) and (f['privacy'] == 'personal') == any(c['ref']['source_class'] == 'personal' for c in batch)][:256]
                        response = model_call(analyzer, delivered, prior_topics, deadline, clock)
                        items = findings(response, delivered, value['report_owner'])
                        need(not CREDENTIAL.search(json.dumps(items).encode()), 'credential-in-analysis')
                        recheck(batch, sources)
                        checkpoint({'kind': 'analysis', 'chunks': batch, 'findings': items})
                        reviewed.update(c['chunk_id'] for c in batch)
                    except (ValueError, OSError, subprocess.SubprocessError) as exc:
                        if clock() >= deadline: raise ValueError('analysis-deadline') from None
                        errors.append(error_code(exc))
            for row in sorted(current, key=scan_priority):
                if row['state'] != 'pending': continue
                check()
                try: remember(row)
                except (OSError, ValueError) as exc:
                    if clock() >= deadline: raise ValueError('analysis-deadline') from None
                    row['state'] = 'blocked'; row['reason'] = error_code(exc); continue
                state['scan_cursor'] = [row['source_id'], row['path']]
                for cid in row['chunk_ids']:
                    if cid in reviewed: continue
                    if cid in old_chunks: reuse(old_chunks[cid])
                    if cid in reviewed: continue
                    c = available[cid]; audience = tuple(sorted(c['ref']['audiences']))
                    buffers.setdefault(audience, []).append(c)
                    if sum(x['end']-x['start'] for x in buffers[audience]) >= 32768:
                        flush(audience)
            for audience in list(buffers): flush(audience)
            reviewed = {c['chunk_id'] for receipt in records for c in receipt['chunks']}
            items = merge_findings([f for receipt in records for f in receipt['findings']])
            # A separate private synthesis sees prior evidence-backed observations, never reports as fresh evidence.
            synth_inputs = [{'chunk_id': f['finding_id'], 'refs': f['evidence_refs'], 'context_refs': f['context_refs'],
                             'text': json.dumps({k: f[k] for k in ('topic', 'lens', 'kind', 'summary', 'facts', 'inferences', 'unknowns')}, ensure_ascii=False)} for f in items]
            synth_count = 0
            for batch in batches(synth_inputs):
                check()
                response = model_call(analyzer, batch, [], deadline, clock)
                syn = findings(response, batch, value['report_owner'])
                need(not CREDENTIAL.search(json.dumps(syn).encode()), 'credential-in-analysis')
                # Synthesis receipts keep the original raw input closure, not fictitious fresh reads.
                ids = {r['sha256'] for x in batch for r in x['context_refs']}
                closure = [c for c in raw_chunks if c['ref']['sha256'] in ids and c['chunk_id'] in reviewed]
                recheck(closure, sources)
                checkpoint({'kind': 'synthesis', 'chunks': [], 'context_refs': [r for x in batch for r in x['context_refs']], 'input_findings': [x['chunk_id'] for x in batch], 'findings': syn})
                synth_count += len(batch)
            synthesis_complete = synth_count == len(synth_inputs)
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            errors.append(error_code(exc))
        finally:
            # Recheck every accepted closure; a changed input invalidates the entire dependent receipt.
            sources = {s['id']: s for s in value['sources']}
            verified = []
            cacheable = {digest(r) for r in records if r['kind'] == 'analysis'}
            for receipt in records:
                try:
                    need(clock() < start+BUDGET, 'finalization-deadline')
                    refs = receipt['chunks'] if receipt['kind'] == 'analysis' else [c for c in raw_chunks if c['ref'] in receipt['context_refs']]
                    recheck(refs, sources)
                    verified.append(receipt)
                except (OSError, ValueError): errors.append('source-recheck-failed')
            records = verified
            reviewed = {c['chunk_id'] for receipt in records if receipt['kind'] == 'analysis' for c in receipt['chunks']}
            for row in current:
                if row['state'] == 'pending' and row.get('chunk_ids') and set(row['chunk_ids']) <= reviewed:
                    row['state'] = 'reviewed'; row['history_reviewed'] = True
            state['inventory'] = current
            # Drop invalid checkpoint refs; prior immutable receipt files remain historical, not reusable.
            accepted_hashes = {digest(r) for r in records}
            inherited = {digest(r) for r in old_receipts if r['kind'] == 'analysis'}
            state['receipts'] = {n: h for n, h in state['receipts'].items() if h in accepted_hashes or h in inherited or h in cacheable}
            state_save(path, state)
            items = merge_findings([f for r in records for f in r['findings']])
            packets = route(items, value['recipients'], value['report_owner'], state['decisions'])
            for rid, spec in value['recipients'].items():
                if spec['adapter'] == 'wep':
                    try:
                        packets[rid]['wep_candidates'] = wep_packets(packets[rid]['findings'], materialize([c for c in raw_chunks if c['ref']['subject_type'] == 'project' and c['ref']['path'].endswith('.json') and rid in c['ref']['audiences']], sources))
                    except (OSError, ValueError) as exc:
                        packets[rid]['wep_candidates'] = []
                        packets[rid]['adapter_error'] = error_code(exc)
                        errors.append('wep-adapter-unavailable')
            counts = {k: sum(r['state'] == k for r in current) for k in ('reviewed', 'pending', 'excluded', 'unsupported', 'blocked', 'missing')}
            complete = enumeration_complete and synthesis_complete and bool(current) and not errors and not any(counts[k] for k in ('pending', 'unsupported', 'blocked', 'missing'))
            result = 'complete' if complete else 'blocked' if not records and errors and errors != ['analysis-deadline'] else 'partial'
            old_items = {f['finding_id']: f for r in old_receipts for f in r['findings']}
            report = {'schema_version': 2, 'run_id': run_id, 'result': result, 'authority': 'advisory-only',
                      'coverage': counts, 'history_reviewed': sum(bool(r.get('history_reviewed')) for r in current), 'enumeration_complete': enumeration_complete, 'synthesis_complete': synthesis_complete,
                      'errors': sorted(set(errors)), 'findings': items,
                      'changed_findings': [f['finding_id'] for f in items if old_items.get(f['finding_id']) != f],
                      'current_receipts': [digest(r) for r in records],
                      'analyzer_backend': 'codex-exec' if isinstance(analyzer, CodexAnalyzer) else 'injected-test-adapter',
                      'scope_gaps': value.get('scope_gaps', {}),
                      'elapsed_seconds': round(clock()-start, 3)}
            text = markdown(report, packets[value['report_owner']])
            artifacts = {'report.json': report, 'inventory.json': current, 'packets.json': packets}
            for name, data in artifacts.items(): save(path, name, data)
            # Store prose using the same immutable JSON writer, then a private regular Markdown artifact.
            fd = open_root(str(path))
            try:
                out = os.open('dream-report.md', os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW, 0o600, dir_fd=fd)
                with os.fdopen(out, 'w') as stream: stream.write(text); stream.flush(); os.fsync(stream.fileno())
            finally: os.close(fd)
            completion = {'schema_version': 2, 'run_id': run_id, 'result': result,
                          'config_digest': digest(value), 'analysis_key': key, 'state_digest': digest(state),
                          'artifact_digests': {n: digest(v) for n, v in artifacts.items()},
                          'markdown_sha256': hash_bytes(text.encode()), 'elapsed_seconds': round(clock()-start, 3)}
            save(path, 'completion.json', completion)
        return completion


def merge_decisions(old, new):
    merged = {(d['finding_id'], d['recipient']): d for d in old}
    merged.update({(d['finding_id'], d['recipient']): d for d in new})
    return list(merged.values())


def merge_findings(items):
    merged = {}
    for item in items:
        fid = item['finding_id']
        if fid not in merged: merged[fid] = dict(item)
        else:
            old = merged[fid]
            # Synthesis can cite the same topic while seeing additional private
            # context. Retain that entire closure alongside the stricter routing.
            for key in ('facts', 'inferences', 'unknowns', 'actions', 'evidence_ids', 'evidence_refs', 'context_refs'):
                old[key] = old[key] + [x for x in item[key] if x not in old[key]]
            old['audiences'] = sorted(set(old['audiences']) & set(item['audiences']))
            old['privacy'] = 'personal' if 'personal' in (old['privacy'], item['privacy']) else 'owner-private'
            old['distinct_source_contents'] = len({r['sha256'] for r in old['evidence_refs']})
    return list(merged.values())


def materialize(batch, sources):
    cache = {}; result = []
    for chunk in batch:
        ref = chunk['ref']; key = (ref['source_id'], ref['path'])
        if key not in cache:
            data = read(sources[ref['source_id']], {'source_id': ref['source_id'], 'path': ref['path'], 'state': 'pending'})
            need(hash_bytes(data) == ref['sha256'], 'source-drift')
            cache[key] = data
        part = cache[key][chunk['start']:chunk['end']]
        need(hash_bytes(part) == chunk['sha256'], 'chunk-drift')
        result.append({**chunk, 'text': part.decode('utf-8')})
    return result


def recheck(batch, sources):
    seen = set()
    for c in batch:
        ref = c['ref']; key = (ref['source_id'], ref['path'])
        if key in seen: continue
        seen.add(key)
        data = read(sources[ref['source_id']], {'source_id': ref['source_id'], 'path': ref['path'], 'state': 'pending'})
        need(hash_bytes(data) == ref['sha256'], 'source-drift')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('inspect', 'preflight', 'run'))
    parser.add_argument('--config', required=True); parser.add_argument('--owner-approved', action='store_true')
    parser.add_argument('--manual', action='store_true')
    args = parser.parse_args()
    try:
        value = config(load(args.config))
        if args.action == 'inspect':
            rows = inventory(value)
            result = {'sources': len(value['sources']), 'entries': len(rows),
                      'counts': {s: sum(r['state'] == s for r in rows) for s in ('pending', 'excluded', 'unsupported', 'missing')}}
        elif args.action == 'preflight': result = CodexAnalyzer(value['analyzer']).preflight()
        else:
            need(args.owner_approved, 'owner-approval-required')
            result = run(value, manual=args.manual)
        print(json.dumps(result, sort_keys=True)); return 0 if result.get('result') not in ('blocked', 'partial') else 2
    except (OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError) as exc:
        print(json.dumps({'error': error_code(exc)}), file=sys.stderr); return 2


if __name__ == '__main__': raise SystemExit(main())
