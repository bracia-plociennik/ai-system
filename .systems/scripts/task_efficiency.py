"""Optional supporting task-path assessment; no execution or approval authority."""
import json
import sys

KINDS = {'answer', 'research', 'diagnosis', 'planning', 'implementation', 'integration', 'data-operation'}
FLAGS = {'intent_clear', 'scope_known', 'access_available', 'evidence_sufficient', 'required_gates_satisfied'}
OPERATION = {'deterministic_rule', 'explicit_candidates', 'known_side_effects', 'concurrency_guard',
             'readback', 'controlled_restore', 'uncertain_result', 'excluded_impact'}


def assess(facts):
    if type(facts) is not dict or set(facts) != FLAGS | {'kind', 'risk', 'operation'}:
        raise ValueError('unknown or missing task facts')
    if type(facts['kind']) is not str or type(facts['risk']) is not str or facts['kind'] not in KINDS or facts['risk'] not in {'low', 'medium', 'high', 'critical'}:
        raise ValueError('unknown task kind or risk')
    if any(type(facts[k]) is not bool for k in FLAGS):
        raise ValueError('facts must be explicit observations')
    op = facts['operation']
    if facts['kind'] == 'data-operation':
        if type(op) is not dict or set(op) != OPERATION or any(type(v) is not bool for v in op.values()):
            raise ValueError('incomplete operation facts')
    elif op is not None:
        raise ValueError('operation facts belong only to data operations')
    result = dict(contract='task-efficiency-v1', execution_authorized=False, risk=facts['risk'],
                  independent_review='retain-required-local-gates', route='normal-local-route', reasons=[])
    missing = sorted(k for k in FLAGS - {'evidence_sufficient'} if not facts[k])
    if missing:
        result.update(route='blocked', reasons=missing)
    elif facts['kind'] == 'data-operation' and op['uncertain_result']:
        result.update(route='inspect-outcome', reasons=['never-replay-an-uncertain-write'])
    elif not facts['evidence_sufficient']:
        result.update(route='resolve-specific-unknown', reasons=['state-unknown-and-stop-condition'])
    elif facts['kind'] == 'data-operation':
        safeguards = OPERATION - {'uncertain_result', 'excluded_impact'}
        failed = sorted(k for k in safeguards if not op[k])
        if not failed and not op['excluded_impact']:
            result['route'] = 'bounded-operation-candidate'
        else:
            result['reasons'] = failed + (['excluded-impact'] if op['excluded_impact'] else [])
    elif facts['kind'] == 'answer':
        result['route'] = 'answer-directly'
    else:
        result['route'] = 'minimal-sufficient-path'
    return result


def unique(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('duplicate fact')
        value[key] = item
    return value


if __name__ == '__main__':
    try:
        raw = sys.stdin.read(65537)
        if len(raw) > 65536:
            raise ValueError('facts exceed size bound')
        print(json.dumps(assess(json.loads(raw, object_pairs_hook=unique)), sort_keys=True))
    except (ValueError, TypeError, KeyError):
        print('Invalid task facts; no execution authorized', file=sys.stderr)
        raise SystemExit(2)
