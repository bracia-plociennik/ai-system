"""Offline accounting of explicit normalized usage events and native snapshots."""
import argparse
import hashlib
import json
from pathlib import Path

TOKENS = ('input_tokens', 'cached_input_tokens', 'output_tokens')


def counters(value):
    result = {key: value.get(key) for key in TOKENS}
    if any(type(v) is not int or v < 0 for v in result.values()):
        raise ValueError('missing or invalid token counters')
    if result['cached_input_tokens'] > result['input_tokens']:
        raise ValueError('cached input exceeds input')
    return result


def analyze(events):
    seen, previous, totals, warnings = {}, {}, {}, []
    duplicates = 0
    modes = {}
    for event in events:
        identity = ('response', event['response_id']) if event.get('response_id') else (event['session_id'], event['event_id'])
        if identity in seen:
            if ({k: seen[identity].get(k) for k in ('usage', 'model', 'kind')} !=
                    {k: event.get(k) for k in ('usage', 'model', 'kind')}):
                raise ValueError('conflicting duplicate usage identity')
            duplicates += 1
            continue
        seen[identity] = event
        usage = counters(event['usage'])
        kind = event['kind']
        mode_key = (event['session_id'], event.get('epoch', 'unspecified'))
        if mode_key in modes and modes[mode_key] != kind:
            raise ValueError('mixed delta and cumulative accounting in one session epoch')
        modes[mode_key] = kind
        key = (event['session_id'], event.get('epoch', 'unspecified'))
        if kind == 'cumulative':
            old = previous.get(key, dict.fromkeys(TOKENS, 0))
            if any(usage[k] < old[k] for k in TOKENS):
                warnings.append({'session_id': event['session_id'], 'reason': 'counter-reset-or-out-of-order'})
                continue
            previous[key] = usage
            usage = {k: usage[k] - old[k] for k in TOKENS}
        elif kind != 'delta':
            raise ValueError('unknown accounting kind')
        group = (event.get('task_id') or 'unassigned', event.get('role') or 'unassigned',
                 event.get('model') or 'unknown', event.get('effort') or 'unknown')
        total = totals.setdefault(group, dict.fromkeys(TOKENS, 0))
        for token in TOKENS:
            total[token] += usage[token]
    groups = [dict(task_id=k[0], role=k[1], model=k[2], effort=k[3], **v) for k, v in sorted(totals.items())]
    return dict(schema=1, groups=groups, duplicates_skipped=duplicates, warnings=warnings,
                subscription_usage_attribution='not-established',
                fork_coverage='global-response-id-when-supplied; native-snapshots-use-upstream-accounting', execution_authorized=False,
                cost_estimate=None, elapsed_seconds=None)


def native_events(paths):
    events, sources = [], []
    for path in paths:
        raw = path.read_bytes()
        value = json.loads(raw)
        sources.append(dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest()))
        for thread in value['threads']:
            if not thread.get('usage'):
                continue
            events.append(dict(session_id=thread['id'], event_id='native-final-snapshot',
                               task_id=value['root_id'], role='parent' if thread['is_root'] else 'subagent',
                               model=thread.get('model'), effort=thread.get('reasoning_effort'),
                               kind='cumulative', usage={k: thread['usage'].get(k) for k in TOKENS}))
    return events, sources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', nargs='+', type=Path)
    parser.add_argument('--native', action='store_true')
    args = parser.parse_args()
    try:
        if args.native:
            events, sources = native_events(args.files)
        else:
            events = []
            sources = []
            for path in args.files:
                raw = path.read_bytes()
                events.extend(json.loads(raw))
                sources.append(dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest()))
        result = analyze(events)
        result['sources'] = sources
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, 'Usage analysis: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()
