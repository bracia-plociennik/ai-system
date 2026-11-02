"""Read-only readiness consumers for an explicitly selected local SPOR adapter.

No adapter is discovered/imported from request data. Application code supplies
its reviewed adapter/API. Nothing here creates a store, event, lock or receipt.
"""
import copy
import json
import os
import hashlib
from finalization_support import safe_path, sha


class ReadOnlyCalendar:
    def __init__(self, api):
        self._api = api

    def validate_calendar(self):
        return self._api.validate_calendar()

    def search(self, days):
        return self._api.search(days)

    def read(self, identity):
        return self._api.read(identity)


def calendar_readiness(workspace, candidate, fingerprint, adapter, api, today):
    """Exercise real calendar access and the existing reconciler before save."""
    props = candidate['properties']
    mode = props['artifact_kind']
    source = adapter.Source(mode, candidate['path'], fingerprint, copy.deepcopy(props))
    plan = adapter.resolve_plan(workspace, source, today)
    # An omitted/past source must not turn a successful empty preview into consent.
    if mode == 'daily' and props['session_date'] not in plan['days']:
        raise ValueError('Candidate calendar date excluded from preflight')
    config_path = safe_path(workspace, adapter.CONFIG)
    config_bytes = config_path.read_bytes()
    config_text = config_bytes.decode('utf-8')
    import re
    config = json.loads(re.search(r'```json\n(.*?)\n```', config_text, re.S).group(1))
    if (not config.get('enabled') or config.get('calendar_id') != adapter.CALENDAR_ID
            or config.get('add_google_meet') is not False
            or config.get('automatic_deletion') is not False):
        raise ValueError('Unsupported calendar preflight configuration')
    state_relative = 'personal-ops/calendar/' + adapter.STATE_NAME
    state_path = safe_path(workspace, state_relative)
    if not state_path.is_file():
        raise ValueError('Calendar registry absent; explicit setup required')
    state_bytes = state_path.read_bytes()
    state = json.loads(state_bytes)
    if (state.get('schema_version') != 1 or state.get('calendar_id') != adapter.CALENDAR_ID
            or not isinstance(state.get('events'), dict)):
        raise ValueError('Invalid calendar registry')
    inputs = {adapter.CONFIG: hashlib.sha256(config_bytes).hexdigest(),
              state_relative: hashlib.sha256(state_bytes).hexdigest()}
    if hasattr(adapter, 'LEGACY'):
        legacy_path = safe_path(workspace, adapter.LEGACY)
        inputs[adapter.LEGACY] = sha(legacy_path) if legacy_path.is_file() else None
    for relative, digest in plan['dependencies'].items():
        if relative != candidate['path']:
            inputs[relative] = digest
    def no_persist(_):
        raise ValueError('Preflight attempted to persist calendar state')
    report = adapter.reconcile(plan, ReadOnlyCalendar(api), copy.deepcopy(state),
                               no_persist, apply=False, adopt=False,
                               legacy=adapter.legacy_receipts(workspace))
    if (report.get('mode') != 'dry-run' or report.get('conflicts')
            or report.get('writes_acknowledged', 0)):
        raise ValueError('Calendar preflight conflict; reconcile before save')
    return {'status': 'ready', 'candidate_sha256': fingerprint,
            'inputs': inputs, 'preview': report}


def existing_tasks_readiness(workspace, candidate, fingerprint):
    """Check the selected existing SilverBullet task set, not a fuzzy scan.

    New-task generation needs its own reviewed preflight callback. This consumer
    never marks execution, creates tasks or changes a lifecycle status.
    """
    from personal_ops_v4 import parse_frontmatter
    from task_store import TaskStore
    relative_config = 'tasks/task-store.local.md'
    config_path = safe_path(workspace, relative_config)
    inputs = {relative_config: sha(config_path)}
    store = TaskStore.load(workspace)
    if store.profile != 'silverbullet-v1' or not os.access(store.root, os.W_OK):
        raise ValueError('Writable selected SilverBullet store unavailable')
    refs = json.loads(candidate['properties'].get('task_generation_references_json') or '[]')
    if not isinstance(refs, list) or not refs or len(set(refs)) != len(refs):
        raise ValueError('Explicit unique existing task references required')
    seen = set()
    for relative in refs:
        path = safe_path(workspace, relative)
        if (not path.is_file() or store.task_dir.resolve() not in path.resolve().parents
                or not os.access(path, os.W_OK)):
            raise ValueError('Unavailable selected task')
        inputs[relative] = sha(path)
        metadata, _, _ = parse_frontmatter(path)
        if metadata.get('type') != 'task':
            raise ValueError('Selected reference is not a task')
        if metadata.get('status') in {'done', 'completed', 'cancelled', 'archived', 'deleted'}:
            raise ValueError('Closed task cannot be reopened by finalization')
        identity = (metadata.get('source_week_id'), metadata.get('source_week_item_id'))
        if all(identity):
            if identity in seen:
                raise ValueError('Duplicate task source identity')
            seen.add(identity)
    return {'status': 'ready', 'candidate_sha256': fingerprint, 'inputs': inputs}
