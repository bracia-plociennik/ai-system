"""Pure SPOR normalization and source-bound, read-only integration preflight.

Callbacks are trusted application code, never commands or paths from a request.
They must not persist anything. Caller attestations do not authenticate consent.
"""
import copy
import hashlib
import json
from datetime import datetime
from finalization_support import safe_path, sha


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def normalize_plan(request):
    """Apply an explicitly confirmed plan patch once; never infer from prose."""
    request = copy.deepcopy(request)
    props = request['properties']
    confirmed = request['confirmed_properties']
    updates = request.pop('plan_item_updates', {})
    if not isinstance(updates, dict):
        raise ValueError('plan_item_updates must be an object')
    key = 'planned_items_json' if props.get('artifact_kind') == 'daily' else 'future_plan_items_json'
    items = json.loads(props.get(key) or '[]')
    if not isinstance(items, list) or any(not isinstance(x, dict) for x in items):
        raise ValueError('Plan items must be objects')
    ids = [x.get('id') for x in items]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate plan item identity')
    allowed = {'title', 'definition_of_done', 'deadline'}
    for identity, update in updates.items():
        if (key not in confirmed or identity not in ids or not isinstance(update, dict)
                or not update or set(update) - allowed
                or any(not isinstance(v, str) for v in update.values())):
            raise ValueError('Unconfirmed or invalid plan item update')
        next(x for x in items if x['id'] == identity).update(update)
    if props.get('artifact_kind') == 'daily':
        linked = props.get('wig_plan_item_id', '')
        deadline = props.get('wig_deadline', '')
        if linked and deadline:
            try:
                datetime.fromisoformat(deadline)
            except (TypeError, ValueError) as exc:
                raise ValueError('Invalid WIG deadline') from exc
            matches = [x for x in items if x.get('id') == linked]
            if len(matches) != 1:
                raise ValueError('WIG must reference exactly one plan item')
            item = matches[0]
            if item.get('deadline') and item['deadline'] != deadline:
                raise ValueError('Conflicting WIG and linked item deadlines')
            if not item.get('deadline'):
                if 'wig_deadline' not in confirmed or key not in confirmed:
                    raise ValueError('WIG deadline binding needs confirmed properties')
                item['deadline'] = deadline
        # One block may hold multiple tasks, but their identities stay distinct.
        schedule = json.loads(props.get('planned_schedule_json') or '[]')
        block_ids = [x.get('block_id') for x in schedule]
        if len(set(block_ids)) != len(block_ids):
            raise ValueError('Duplicate calendar block identity')
    if updates or (props.get('artifact_kind') == 'daily' and props.get('wig_deadline')):
        props[key] = json.dumps(items, ensure_ascii=False)
    return request


def check_calendar_identities(schedule, existing_block_ids):
    """Reject removed/renamed managed identities; never guess aliases or delete."""
    ids = [x.get('block_id') for x in schedule if x.get('kind') != 'checkpoint']
    if any(not x for x in ids) or len(set(ids)) != len(ids):
        raise ValueError('Invalid calendar block identities')
    removed = set(existing_block_ids) - set(ids)
    if removed:
        raise ValueError('Calendar identities removed or renamed; reconcile before save: '
                         + ', '.join(sorted(removed)))


def prepare_integrations(workspace, candidate, integrations, preflights):
    """Every selected integration must prove readiness for these exact bytes."""
    candidate_hash = hashlib.sha256(candidate['body'].encode()).hexdigest()
    inputs = {}
    results = {}
    populations = []
    for name in integrations:
        callback = preflights.get(name)
        if not callable(callback):
            raise ValueError('Missing read-only integration preflight: ' + name)
        # Detach callback input: accidental mutation must not change saved bytes.
        result = callback(copy.deepcopy(candidate), candidate_hash)
        if (not isinstance(result, dict) or result.get('status') != 'ready'
                or result.get('candidate_sha256') != candidate_hash
                or not isinstance(result.get('inputs'), dict) or not result['inputs']):
            raise ValueError('Integration preflight not ready or source-bound: ' + name)
        for relative, digest in result['inputs'].items():
            path = safe_path(workspace, relative)
            valid = not path.exists() if digest is None else (
                isinstance(digest, str) and path.is_file() and sha(path) == digest)
            if not valid:
                raise ValueError('Stale preflight input: ' + str(relative))
            if relative in inputs and inputs[relative] != digest:
                raise ValueError('Conflicting preflight inputs')
            inputs[relative] = digest
        results[name] = result
        if 'task_population' in result:
            if name!='tasks':raise ValueError('Task proof outside selected task integration')
            from spor_new_tasks import check_task_population
            check_task_population(workspace,result['task_population'])
            populations.append(result['task_population'])
    return {'candidate_sha256': candidate_hash, 'inputs': inputs, 'integrations': results,
            'task_populations':populations}


def check_inputs(workspace, preflight):
    for proof in preflight.get('task_populations',[]):
        from spor_new_tasks import check_task_population
        check_task_population(workspace,proof)
    for relative, digest in preflight['inputs'].items():
        path = safe_path(workspace, relative)
        valid = not path.exists() if digest is None else (path.is_file() and sha(path) == digest)
        if not valid:
            raise ValueError('Preflight inputs changed; reprepare before writing: ' + relative)
