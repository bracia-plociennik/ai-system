"""Private, advisory WIG projection and task-scoped conversation state.

Caller verifies the selected personal owner and actual approval. No state or
assessment authenticates consent, diagnoses motivation or authorizes execution.
"""
from __future__ import annotations
import argparse
from datetime import date, datetime, timedelta
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import stat
import sys
from zoneinfo import ZoneInfo

sys.dont_write_bytecode = True
CONTRACT = 'wig-mentoring-v1'
PROJECT = 'wig-mentoring-project-v1'
TRIGGERS = {'new-task', 'next-task', 'scope-change', 'plan-review', 'continuation', 'ordinary'}
RELATIONS = {'unknown', 'aligned', 'unrelated', 'necessary'}
ASSESSMENT = {'relation', 'daily_weekly_relation', 'important_context', 'owner_goal', 'material_change'}


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:raise ValueError('duplicate mentor field')
        result[key] = value
    return result


def unlinked(path):
    path = Path(os.path.abspath(path))
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('linked mentor path')
    return path


def text(value, limit=2000):
    if not isinstance(value, str) or not value.strip() or len(value) > limit or any(ord(c) < 32 for c in value):
        raise ValueError('invalid mentor text')
    return value.strip()


def read_json(path):
    path = unlinked(path)
    if not stat.S_ISREG(path.stat().st_mode) or path.stat().st_size > 65536:
        raise ValueError('invalid mentor file')
    return json.loads(path.read_text(), object_pairs_hook=unique)


def owner_root(workspace):
    root = unlinked(workspace)
    if not root.is_dir():
        raise ValueError('explicit personal workspace required')
    if (root / '.git').exists():
        # Private owner workspaces can themselves be Git repositories. Reuse the
        # user registration and require an exact active workspace root, never a
        # default or a child project. This is binding evidence, not consent.
        from agent_context import registration, workspace_registry
        record, installed, _, environment = registration()
        rows, _ = workspace_registry(installed, environment)
        if not record['enabled'] or root not in {row[1] for row in rows}:
            raise ValueError('project repository is not the selected owner workspace')
    return root


def goal(title, dod):
    if not isinstance(title, str) or not isinstance(dod, str) or not title.strip() or not dod.strip():
        return None
    return {'title': text(title), 'definition_of_done': text(dod)}


def important_tasks(workspace):
    """Read bounded task frontmatter from the selected owner-local store only."""
    from task_store import TaskStore
    from personal_ops_spor_proposals import read_frontmatter
    store = TaskStore.load(workspace)
    if store.profile != 'silverbullet-v1' or not unlinked(store.root).is_relative_to(workspace):
        raise ValueError('unsupported owner task store')
    unlinked(store.task_dir)
    result, count = [], 0
    for directory, dirs, files in os.walk(store.task_dir, followlinks=False):
        count += 1 + len(files)
        if count > 2000:raise ValueError('task metadata bound reached')
        for name in list(dirs):
            unlinked(Path(directory) / name)
            if name.startswith('.') or name.endswith('.assets') or name in {'attachments', 'node_modules'}:dirs.remove(name)
        for name in sorted(files):
            if not name.endswith('.md'):continue
            path = unlinked(Path(directory) / name)
            row, _ = read_frontmatter(path, task=True)
            if row.get('type') != 'task' or row.get('status') not in {'open', 'planned', 'waiting'}:continue
            deadline = row.get('source_deadline', row.get('deadline', row.get('due', '')))
            if deadline:
                if not isinstance(deadline, str):raise ValueError('invalid task deadline')
                date.fromisoformat(deadline[:10])
            if not deadline and row.get('priority') != 'high':continue
            result.append({'id': fingerprint(str(path.relative_to(store.root))),
                           'title': text(row.get('title')), 'deadline': deadline,
                           'priority': row.get('priority', ''), 'status': row['status'],
                           'category': row.get('category', '')})
    return result


def selected_sources(workspace, target):
    """Only canonical structured properties; never raw text as competing evidence."""
    from personal_ops_v4 import daily_path, weekly_path, validate_common, json_value
    from personal_ops_spor_proposals import read_frontmatter
    from personal_ops_aggregates_v4 import is_unified, read_properties
    daily, weekly, items, refs, warnings = None, None, [], [], []
    try:
        if is_unified(workspace):
            rows = [r for r in read_properties(workspace) if str(r.get('session_date')) == target.isoformat()]
            if len(rows) > 1:
                raise ValueError('ambiguous daily properties')
            props = rows[0] if rows else None
            if props:
                refs.append(props['aggregate_source_path'])
        else:
            paths = [unlinked(daily_path(workspace, target)),
                     unlinked(workspace / 'personal-ops/check-ins-v3' / str(target.year) / (target.isoformat() + '.md')),
                     unlinked(workspace / 'personal-ops/check-ins' / str(target.year) / (target.isoformat() + '.md'))]
            present = [p for p in paths if p.exists()]
            if len(present) > 1:
                raise ValueError('ambiguous native daily sources')
            props = None
            if present:
                path = present[0]
                top, props = read_frontmatter(path)
                version = str(top.get('index_contract'))
                if version == '4':validate_common(top, props, path, 'daily')
                elif version != '3' or top.get('type') not in {'daily-check-in', 'daily-check-in-v3'}:
                    raise ValueError('unsupported daily source')
                if str(props.get('session_date', top.get('session_date'))) != target.isoformat():
                    raise ValueError('daily source period mismatch')
            if props:
                refs.append(str(path.relative_to(workspace)))
        if props and props.get('private_index_policy') != 'redacted':
            daily = goal(props.get('wig_title'), props.get('wig_definition_of_done'))
            items = json_value(props, 'planned_items_json', [])
            if not isinstance(items, list):
                raise ValueError('invalid daily items')
    except (OSError, ValueError, KeyError, TypeError):
        daily, items = None, []
        warnings.append('daily-source-unavailable-or-conflicting')
    monday = target - timedelta(days=target.weekday())
    candidates = []
    daily_items = list(items)
    try:
        # Reports review a week and plan the next one. Match the plan period,
        # not the report filename or whichever report happens to be newest.
        for report_monday in [monday - timedelta(days=7), monday]:
            week_id = report_monday.strftime('%G-W%V')
            path = unlinked(weekly_path(workspace, report_monday))
            if not path.exists():
                continue
            top, props = read_frontmatter(path)
            validate_common(top, props, path, 'weekly')
            if props.get('private_index_policy') == 'redacted':
                continue
            if str(props.get('plan_week_start')) == monday.isoformat():
                if str(props.get('plan_week_end')) != (monday + timedelta(days=4)).isoformat():
                    raise ValueError('weekly plan period mismatch')
                candidates.append((path, props))
        if len(candidates) > 1:
            raise ValueError('ambiguous weekly goal')
        if candidates:
            path, props = candidates[0]
            raw = json_value(props, 'future_wig_json', {})
            weekly = goal(raw.get('title'), raw.get('definition_of_done'))
            refs.append(str(path.relative_to(workspace)))
            weekly_items = json_value(props, 'future_plan_items_json', [])
            if not isinstance(weekly_items, list):
                raise ValueError('invalid weekly items')
            items += weekly_items
        else:
            # Existing approved legacy weekly plans remain readable; no import.
            path = unlinked(workspace / 'tasks/weekly-plans' / str(monday.year) / (monday.strftime('%G-W%V') + '.md'))
            if path.exists():
                top, props = read_frontmatter(path)
                props = {**top, **props}
                if str(props.get('week_start')) != monday.isoformat() or props.get('plan_readiness') != 'ready':
                    raise ValueError('weekly plan not current/ready')
                weekly = goal(props.get('wig_title'), props.get('wig_definition_of_done'))
                refs.append(str(path.relative_to(workspace)))
                items += json_value(props, 'weekly_plan_items_json', [])
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        weekly = None
        items = daily_items
        warnings.append('weekly-source-unavailable-or-conflicting')
    important = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get('deadline') or item.get('priority') == 'high' or item.get('important') is True:
            important.append({key: item[key] for key in ('id', 'title', 'deadline', 'priority', 'important') if key in item})
    try:
        important += important_tasks(workspace)
    except (OSError, ValueError, KeyError, TypeError):
        warnings.append('selected-task-store-unavailable-or-incomplete')
    important = sorted({fingerprint(item): item for item in important}.values(), key=fingerprint)
    return {'daily': daily, 'weekly': weekly, 'important': important,
            'source_refs': sorted(set(refs)), 'warnings': warnings}


def assessment(value):
    if not isinstance(value, dict) or set(value) - ASSESSMENT:
        raise ValueError('unknown mentor assessment fields')
    result = {'relation': 'unknown', 'daily_weekly_relation': 'unknown',
              'important_context': '', 'owner_goal': None, 'material_change': False, **value}
    if type(result['material_change']) is not bool:
        raise ValueError('material change must be an explicit factual assessment')
    if result['relation'] not in RELATIONS or result['daily_weekly_relation'] not in {'unknown', 'compatible', 'conflict'}:
        raise ValueError('unknown relation')
    if not isinstance(result['important_context'], str):
        raise ValueError('invalid important context')
    if result['important_context']:
        text(result['important_context'])
    if result['owner_goal'] is not None:
        raw = result['owner_goal']
        if not isinstance(raw, dict) or set(raw) != {'title', 'definition_of_done', 'owner_reference'}:
            raise ValueError('owner goal requires actual scoped owner reference')
        text(raw['owner_reference'])
        result['owner_goal'] = goal(raw['title'], raw['definition_of_done'])
        if result['owner_goal'] is None:
            raise ValueError('incomplete owner goal')
    return result


def state_path(workspace, task_ref):
    return unlinked(workspace / 'personal-ops/mentoring/v1' / (fingerprint(text(task_ref, 300)) + '.json'))


def state_directory(workspace, create=False):
    """Descriptor-relative no-follow traversal, including existing ancestors."""
    parent = workspace / 'personal-ops/mentoring/v1'
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in parent.parts[1:]:
            if create:
                try:os.mkdir(part, mode=0o700, dir_fd=fd)
                except FileExistsError:pass
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd);fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def load_state(workspace, task_ref, directory_fd=None):
    task_ref = text(task_ref, 300)
    path = state_path(workspace, task_ref)
    try:
        parent = state_directory(workspace) if directory_fd is None else os.dup(directory_fd)
    except FileNotFoundError:
        return None
    try:
        try:fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        except FileNotFoundError:return None
        with os.fdopen(fd, 'r') as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > 65536 or info.st_nlink != 1:raise ValueError('invalid state file')
            value = json.loads(stream.read(65537), object_pairs_hook=unique)
    finally:
        os.close(parent)
    if (set(value) != {'schema', 'task_hash', 'context_hash', 'disposition', 'owner_reference_hash'}
            or type(value['schema']) is not int or value['schema'] != 1 or value['task_hash'] != fingerprint(task_ref)
            or value['disposition'] not in {'seen', 'exception', 'finished'}
            or not re.fullmatch('[a-f0-9]{64}', value['context_hash'])
            or not re.fullmatch('[a-f0-9]{64}', value['owner_reference_hash'])):
        raise ValueError('invalid mentor state')
    return value


def enabled(workspace):
    path = unlinked(workspace / 'personal-ops/mentoring/settings.local.json')
    if not path.exists():
        return False
    value = read_json(path)
    if (not isinstance(value, dict) or set(value) != {'contract', 'enabled'}
            or value['contract'] != CONTRACT or type(value['enabled']) is not bool):
        raise ValueError('unsupported mentor settings')
    return value['enabled']


def prepare(workspace, target, timezone, task_ref, trigger, facts=None):
    workspace = owner_root(workspace)
    ZoneInfo(timezone)
    task_ref = text(task_ref, 300)
    if trigger not in TRIGGERS:
        raise ValueError('unknown mentoring trigger')
    facts = assessment(facts or {})
    result = {'contract': CONTRACT, 'authority': 'none', 'execution_authorized': False,
              'task_hash': fingerprint(task_ref), 'context_hash': fingerprint(None),
              'action': 'quiet', 'reason_codes': [], 'date': target.isoformat(),
              'timezone': timezone, 'source_status': 'disabled'}
    if trigger in {'ordinary', 'continuation'}:
        result.update(source_status='not-requested', reason_codes=['not-a-decision-boundary'])
        return result
    if not enabled(workspace):
        result['reason_codes'] = ['mentor-disabled']
        return result
    sources = selected_sources(workspace, target)
    selected = facts['owner_goal'] or sources['daily'] or sources['weekly']
    result.update(private_sources=sources, selected_goal=selected,
                  source_status='available' if selected else 'unknown')
    result['context_hash'] = fingerprint([result['task_hash'], selected, sources['weekly'], sources['important'], facts['important_context']])
    state = load_state(workspace, task_ref)
    # A missing source/new day/rewritten narrative is not a confirmed change.
    # The lead independently verifies material_change against actual evidence.
    same = state and state['disposition'] in {'seen', 'exception'} and (
        state['context_hash'] == result['context_hash'] or not facts['material_change'])
    if state and state['disposition'] == 'finished':
        result['reason_codes'] = ['task-finished']
    elif trigger in {'ordinary', 'continuation'} or same:
        result['reason_codes'] = ['not-a-decision-boundary' if trigger in {'ordinary', 'continuation'} else 'already-addressed-for-this-task']
    elif facts['relation'] == 'necessary':
        result['reason_codes'] = ['necessary-obligation-or-dependency']
    elif not selected:
        result.update(action='clarify', reason_codes=['current-goal-unknown'])
    elif sources['daily'] and sources['weekly'] and facts['daily_weekly_relation'] == 'conflict' and not facts['owner_goal']:
        result.update(action='clarify', reason_codes=['daily-weekly-intent-conflict'])
    elif facts['relation'] == 'unrelated':
        result.update(action='suggest-return', reason_codes=['task-diverges-from-confirmed-priority'])
    else:
        result['reason_codes'] = ['aligned' if facts['relation'] == 'aligned' else 'alignment-not-established']
    return result


def project_view(result):
    return {**{key: result[key] for key in ('authority', 'execution_authorized', 'task_hash',
                                          'context_hash', 'action', 'reason_codes')}, 'contract': PROJECT}


def record(workspace, task_ref, context_hash, disposition, owner_reference, approved=False):
    """Explicit private state mutation only; never task/goal/approval mutation."""
    workspace = owner_root(workspace)
    if not approved or not enabled(workspace):
        raise ValueError('actual scoped owner-approved state write required')
    task_ref = text(task_ref, 300);text(owner_reference)
    if disposition not in {'seen', 'exception', 'finished'} or not re.fullmatch('[a-f0-9]{64}', context_hash):
        raise ValueError('invalid task state transition')
    path = state_path(workspace, task_ref)
    parent = state_directory(workspace, create=True)
    try:
        fd = os.open('.update.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600, dir_fd=parent)
        with os.fdopen(fd, 'r+') as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):raise ValueError('invalid state lock')
            fcntl.flock(stream, fcntl.LOCK_EX)
            current = load_state(workspace, task_ref, parent)
            if current and current['disposition'] == 'finished' and disposition != 'finished':
                raise ValueError('finished task requires a new task identity')
            value = {'schema': 1, 'task_hash': fingerprint(task_ref), 'context_hash': context_hash,
                     'disposition': disposition, 'owner_reference_hash': fingerprint(owner_reference)}
            temporary = '.mentor-' + secrets.token_hex(16)
            temp_fd = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600, dir_fd=parent)
            try:
                with os.fdopen(temp_fd, 'w') as output:
                    json.dump(value, output, sort_keys=True);output.write('\n');output.flush();os.fsync(output.fileno())
                unlinked(path)
                os.replace(temporary, path.name, src_dir_fd=parent, dst_dir_fd=parent)
            finally:
                try:os.unlink(temporary, dir_fd=parent)
                except FileNotFoundError:pass
            if load_state(workspace, task_ref) != value:
                raise ValueError('uncertain mentor write; inspect before retry')
            return {'contract': CONTRACT, 'authority': 'none', 'execution_authorized': False,
                    'recorded': True, 'disposition': disposition, 'task_hash': value['task_hash']}
    finally:
        os.close(parent)


def main(write=False):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--task-ref', required=True)
    if write:
        parser.add_argument('--context-hash', required=True)
        parser.add_argument('--disposition', choices=['seen', 'exception', 'finished'], required=True)
        parser.add_argument('--owner-reference', required=True)
        parser.add_argument('--owner-approved', action='store_true')
    else:
        parser.add_argument('--timezone', required=True)
        parser.add_argument('--date', type=date.fromisoformat)
        parser.add_argument('--trigger', choices=sorted(TRIGGERS), required=True)
        parser.add_argument('--assessment', type=Path, help='Explicit private JSON assessment; never a stored command')
        parser.add_argument('--project-view', action='store_true')
    args = parser.parse_args()
    try:
        if write:
            result = record(args.workspace, args.task_ref, args.context_hash, args.disposition,
                            args.owner_reference, args.owner_approved)
        else:
            target = args.date or datetime.now(ZoneInfo(args.timezone)).date()
            result = prepare(args.workspace, target, args.timezone, args.task_ref, args.trigger,
                             read_json(args.assessment) if args.assessment else None)
            if args.project_view:result = project_view(result)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (ValueError, OSError, KeyError, TypeError):
        # No raw goal, source path, owner statement or malformed payload in errors.
        print(json.dumps({'contract': CONTRACT, 'authority': 'none', 'execution_authorized': False,
                          'error': 'mentor-context-unavailable; inspect selected private sources'}))
        return 2
