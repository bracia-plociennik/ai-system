#!/usr/bin/env python3
"""Goal-focused maintenance v1. Data reducer, never an executor or approval source."""
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import fcntl
import json
import math
import os
from pathlib import Path
import re
import stat
import tempfile
import hashlib
import subprocess

WIRE = 'goal-focused-maintenance-v1'
FLOORS = ('E01', 'E02', 'E03', 'E04', 'E05')
STATES = {'open', 'deferred', 'resolved'}
ISSUE_FIELDS = {'id', 'cause_key', 'safe_summary', 'source_refs', 'goal_ref',
                'affected_scope', 'first_seen', 'last_seen', 'occurrence_task_ids',
                'impact', 'independence_evidence', 'immediate_rule_ids', 'state',
                'defer_reason', 'next_trigger', 'resolution_evidence', 'notification_episode'}
QUEUE_FIELDS = {'schema_version', 'owner_ref', 'revision', 'issues', 'budgets', 'notification_episodes'}
BUDGET_FIELDS = {'id', 'parent_task_ref', 'parent_scope_revision', 'approval_ref',
                 'limit_seconds', 'intervals', 'reserved_seconds', 'elapsed_state'}
EPISODE_FIELDS = {'id', 'owner_ref', 'goal_ref', 'issue_ids', 'reason_codes', 'state',
                  'created_at', 'presented_at', 'presentation_evidence_ref',
                  'baseline_active_ids', 'policy_revision'}


class Invalid(ValueError):
    """Malformed or unsupported input; original state is retained."""


class Conflict(Invalid):
    """CAS or concurrent-writer conflict; never silently retried."""


def need(condition, message):
    if not condition:
        raise Invalid(message)


def fields(value, keys):
    need(type(value) is dict and set(value) == set(keys), 'closed schema fields mismatch')


def integer(value):
    need(type(value) is int and value >= 0, 'invalid integer')


def number(value):
    need(type(value) in (int, float) and math.isfinite(value) and value >= 0,
         'invalid finite duration')


def token(value):
    need(type(value) is str and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:/-]{0,239}', value),
         'invalid stable identity')
    need('..' not in value.split('/'), 'identity traversal')


def prose(value):
    need(type(value) is str and 0 < len(value) <= 500 and '\x00' not in value,
         'invalid safe summary')
    need(not re.search(r'(?i)(-----BEGIN .*PRIVATE KEY|Bearer\s+\S+|gh[pousr]_[A-Za-z0-9]+|sk-[A-Za-z0-9]{20,})', value),
         'sensitive content is not authorized')


def strings(value):
    need(type(value) is list and all(type(x) is str and x for x in value)
         and len(value) == len(set(value)), 'invalid distinct string list')


def stamp(value):
    need(type(value) is str and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?Z', value),
         'timestamp must be UTC RFC3339')
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00')).timestamp()
    except ValueError as error:
        raise Invalid('invalid timestamp') from error


def pairs(items):
    out = {}
    for key, value in items:
        need(key not in out, 'duplicate JSON key')
        out[key] = value
    return out


def decode(text):
    try:
        return json.loads(text, object_pairs_hook=pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(Invalid('nonfinite JSON')))
    except (json.JSONDecodeError, UnicodeError) as error:
        raise Invalid('invalid JSON') from error


def safe_path(owner, raw, existing=False):
    """Absolute references, lexical containment and no linked components."""
    root = Path(owner)
    path = Path(raw)
    need(root.is_absolute() and path.is_absolute(), 'absolute owner/reference required')
    need('..' not in path.parts and '.' not in path.parts, 'unsafe path component')
    need(path.is_relative_to(root), 'outside canonical owner')
    for parent in (*reversed(path.parents), path):
        need(not parent.is_symlink(), 'linked owner/reference')
    if existing:
        need(path.is_file(), 'missing evidence reference')
    return path


def evidence(owner, value, required=False):
    if value is None:
        need(not required, 'missing evidence')
    else:
        need(type(value) is str, 'invalid evidence reference')
        safe_path(owner, value, existing=True)


def defaults():
    titles = ('Data integrity and disclosure', 'Security and access boundaries',
              'Unintended financial effects', 'Current deliverable correctness',
              'Unapproved goal or architecture drift')
    return {'schema_version': 1, 'policy_id': WIRE, 'revision': 0, 'parent_revision': None,
            'changed_at': '2026-01-01T00:00:00Z', 'approval_ref': None, 'reason': 'Portable defaults',
            'rules': [{'id': k, 'title': t, 'enabled': True, 'trigger': t,
                       'examples': [], 'severity_floor': 'immediate'} for k, t in zip(FLOORS, titles)],
            'thresholds': {'distinct_open_causes': 5, 'recurring_affected_tasks': 3},
            'incidental_budget_seconds': 600}


def validate_policy(value, owner):
    fields(value, {'schema_version', 'policy_id', 'revision', 'parent_revision', 'changed_at',
                   'approval_ref', 'reason', 'rules', 'thresholds', 'incidental_budget_seconds'})
    need(type(value['schema_version']) is int and value['schema_version'] == 1, 'unsupported policy version')
    need(value['policy_id'] == WIRE, 'unsupported policy identity')
    integer(value['revision']); stamp(value['changed_at']); prose(value['reason'])
    if value['revision'] == 0:
        need(value['parent_revision'] is None and value['approval_ref'] is None, 'invalid initial policy')
        need(value == defaults(), 'first-use policy must be conservative defaults')
    else:
        integer(value['parent_revision'])
        need(value['parent_revision'] + 1 == value['revision'], 'policy revision gap')
        evidence(owner, value['approval_ref'], True)
    fields(value['thresholds'], {'distinct_open_causes', 'recurring_affected_tasks'})
    for v in value['thresholds'].values():
        integer(v); need(v > 0, 'invalid threshold')
    integer(value['incidental_budget_seconds'])
    need(0 < value['incidental_budget_seconds'] <= 600, 'budget cannot exceed accepted ceiling')
    need(type(value['rules']) is list, 'rules must be a list')
    seen = set()
    for rule in value['rules']:
        fields(rule, {'id', 'title', 'enabled', 'trigger', 'examples', 'severity_floor'})
        token(rule['id']); prose(rule['title']); prose(rule['trigger']); strings(rule['examples'])
        need(rule['id'] not in seen, 'duplicate rule'); seen.add(rule['id'])
        need(type(rule['enabled']) is bool and rule['severity_floor'] == 'immediate', 'invalid rule floor')
        if rule['id'] in FLOORS:
            need(rule['enabled'], 'mandatory floor cannot be disabled')
    need(set(FLOORS) <= seen, 'missing mandatory floor')
    return value


def empty_queue(owner):
    safe_path(owner, owner)
    return {'schema_version': 1, 'owner_ref': str(owner), 'revision': 0,
            'issues': [], 'budgets': [], 'notification_episodes': []}


def unique(items, key):
    need(type(items) is list and len({v[key] for v in items}) == len(items), 'duplicate identity')


def consumed(budget, now=None):
    if budget['elapsed_state'] == 'unknown':
        return None
    total, windows = 0.0, []
    for interval in budget['intervals']:
        start = stamp(interval['start'])
        if interval['end'] is None:
            if now is None or interval['state'] != 'active':
                return None
            end = stamp(now)
        else:
            end = stamp(interval['end'])
        need(end >= start, 'negative interval')
        if interval['state'] == 'active':
            windows.append((start, end))
            total += end - start
    windows.sort()
    need(all(a[1] <= b[0] for a, b in zip(windows, windows[1:])), 'overlapping intervals')
    return total


def validate_queue(value, owner):
    fields(value, QUEUE_FIELDS)
    need(type(value['schema_version']) is int and value['schema_version'] == 1, 'unsupported queue version')
    need(value['owner_ref'] == str(owner), 'foreign canonical owner'); safe_path(owner, owner)
    integer(value['revision'])
    for key in ('issues', 'budgets', 'notification_episodes'):
        need(type(value[key]) is list, 'invalid collection')
        for entry in value[key]:
            need(type(entry) is dict and 'id' in entry, 'invalid entry'); token(entry['id'])
        unique(value[key], 'id')
    causes = set()
    for issue in value['issues']:
        fields(issue, ISSUE_FIELDS); token(issue['cause_key']); token(issue['goal_ref'])
        need(issue['cause_key'] not in causes, 'duplicate cause'); causes.add(issue['cause_key'])
        prose(issue['safe_summary']); strings(issue['source_refs']); strings(issue['affected_scope'])
        strings(issue['occurrence_task_ids']); strings(issue['immediate_rule_ids'])
        for ref in issue['source_refs']:
            evidence(owner, ref, True)
        for ref in issue['occurrence_task_ids'] + issue['affected_scope'] + issue['immediate_rule_ids']:
            token(ref)
        need(stamp(issue['last_seen']) >= stamp(issue['first_seen']), 'observation chronology')
        need(issue['impact'] in {'none', 'material', 'unknown'} and issue['state'] in STATES, 'invalid issue state')
        evidence(owner, issue['independence_evidence']); evidence(owner, issue['resolution_evidence'])
        for key in ('defer_reason', 'next_trigger'):
            need(issue[key] is None or type(issue[key]) is str and bool(issue[key]), 'invalid disposition')
        if issue['state'] == 'resolved':
            evidence(owner, issue['resolution_evidence'], True)
        if issue['notification_episode'] is not None:
            token(issue['notification_episode'])
    parents = set()
    for budget in value['budgets']:
        fields(budget, BUDGET_FIELDS); token(budget['parent_task_ref'])
        need(budget['parent_task_ref'] not in parents, 'duplicate parent budget'); parents.add(budget['parent_task_ref'])
        integer(budget['parent_scope_revision']); integer(budget['limit_seconds'])
        need(0 <= budget['limit_seconds'] <= 600, 'invalid budget ceiling')
        evidence(owner, budget['approval_ref'], True); number(budget['reserved_seconds'])
        need(budget['elapsed_state'] in {'observed', 'unknown'}, 'invalid clock state')
        need(type(budget['intervals']) is list, 'invalid intervals'); unique(budget['intervals'], 'id')
        unfinished = 0
        for interval in budget['intervals']:
            fields(interval, {'id', 'start', 'end', 'state', 'reason', 'evidence_ref'})
            token(interval['id']); stamp(interval['start']); prose(interval['reason'])
            evidence(owner, interval['evidence_ref'], True)
            need(interval['state'] in {'active', 'suspended'}, 'invalid interval state')
            if interval['end'] is None:
                unfinished += 1
            else:
                need(stamp(interval['end']) >= stamp(interval['start']), 'invalid interval duration')
        need(unfinished <= 1, 'multiple unfinished intervals')
        # Closed windows are checked even when a recovered clock is unknown.
        closed = dict(budget, elapsed_state='observed', intervals=[i for i in budget['intervals'] if i['end'] is not None])
        consumed(closed)
    ids = {i['id'] for i in value['issues']}
    episode_ids = {e['id'] for e in value['notification_episodes']}
    for episode in value['notification_episodes']:
        fields(episode, EPISODE_FIELDS); token(episode['goal_ref'])
        need(episode['owner_ref'] == str(owner), 'foreign episode owner')
        for key in ('issue_ids', 'reason_codes', 'baseline_active_ids'):
            strings(episode[key])
        need(set(episode['issue_ids']) <= ids and set(episode['baseline_active_ids']) <= ids,
             'unknown episode issue')
        need(episode['state'] in {'pending', 'presented'}, 'invalid episode state')
        stamp(episode['created_at']); integer(episode['policy_revision'])
        if episode['state'] == 'presented':
            need(stamp(episode['presented_at']) >= stamp(episode['created_at']), 'presentation chronology')
            evidence(owner, episode['presentation_evidence_ref'], True)
        else:
            need(episode['presented_at'] is None and episode['presentation_evidence_ref'] is None,
                 'pending episode has no delivery receipt')
    need(all(i['notification_episode'] is None or i['notification_episode'] in episode_ids for i in value['issues']),
         'unknown notification episode')
    return value


@dataclass(frozen=True)
class Facts:
    """Caller-verified observations. Never deserialize a queue row into Facts.

    The coordinator supplies actual current gate/owner/privacy/authority facts;
    repair projection never authorizes an action. Uncertain defaults fail closed.
    """
    goal_ref: str
    parent_task_ref: str
    owner_ref: str
    independence_verified: bool = False
    required_dependency: bool = True
    immediate_rules: tuple = ()
    local_reversible_low_risk: bool = False
    target_covered: bool = False
    collision_free: bool = False
    known_test: bool = False
    request: bool = False
    compatible: bool = True


def budget_for(queue, parent):
    return next((b for b in queue['budgets'] if b['parent_task_ref'] == parent), None)


def threshold_reasons(queue, policy, goal):
    active = [i for i in queue['issues'] if i['state'] != 'resolved' and goal in i['affected_scope']]
    ids = {i['id'] for i in active}
    presented = [e for e in queue['notification_episodes'] if e['goal_ref'] == goal and e['state'] == 'presented']
    reopened = {i['id'] for i in active if i['resolution_evidence'] is not None
                and i['notification_episode'] is None}
    previous = (set().union(*(set(e['baseline_active_ids']) for e in presented)) if presented else set()) - reopened
    recurring_shown = (set().union(*(set(e['issue_ids']) for e in presented if 'threshold:third-task' in e['reason_codes'])) if presented else set()) - reopened
    reasons = []
    if len(ids - previous) >= policy['thresholds']['distinct_open_causes']:
        reasons.append('threshold:five-causes')
    if any(len(i['occurrence_task_ids']) >= policy['thresholds']['recurring_affected_tasks']
           and i['id'] not in recurring_shown for i in active):
        reasons.append('threshold:third-task')
    return reasons


def project(queue, policy, issue_id, facts, now=None):
    validate_queue(queue, facts.owner_ref); validate_policy(policy, facts.owner_ref)
    token(facts.goal_ref); token(facts.parent_task_ref)
    need(all(type(getattr(facts, key)) is bool for key in ('independence_verified', 'required_dependency',
         'local_reversible_low_risk', 'target_covered', 'collision_free', 'known_test', 'request', 'compatible')),
         'facts require actual verified booleans')
    need(type(facts.immediate_rules) is tuple, 'live rules must be an immutable verified tuple')
    issue = next((i for i in queue['issues'] if i['id'] == issue_id), None)
    need(issue is not None, 'unknown issue')
    rules = {r['id'] for r in policy['rules'] if r['enabled']}
    need(set(facts.immediate_rules) <= rules, 'unknown escalation rule')
    need(set(issue['immediate_rule_ids']) <= rules, 'unknown recorded escalation rule')
    # Floor findings are live facts, independent of editable trigger prose.
    immediate = sorted(set(facts.immediate_rules))
    blocking = []
    reasons = ['immediate:' + rule for rule in immediate]
    if issue['impact'] == 'material' or facts.required_dependency:
        reasons.append('goal-blocked'); blocking = [facts.goal_ref]
    safe = (issue['impact'] == 'none' and facts.independence_verified
            and issue['independence_evidence'] is not None and not blocking and not immediate)
    if not safe and not reasons:
        reasons.append('deferred:unknown-impact')
    if not facts.compatible:
        reasons.append('compatibility:unsupported'); blocking = [facts.goal_ref]
    if facts.request:
        reasons.append('owner-request')
    elif safe:
        reasons += threshold_reasons(queue, policy, facts.goal_ref)
    disclosure = ('on-request' if facts.request else 'immediate' if immediate or blocking
                  else 'milestone' if not safe or any(r.startswith('threshold:') for r in reasons) else 'silent')
    budget = budget_for(queue, facts.parent_task_ref)
    elapsed = consumed(budget, now) if budget else None
    allowance = min(budget['limit_seconds'], policy['incidental_budget_seconds']) if budget else 0
    available = max(0, allowance - elapsed - budget['reserved_seconds']) if elapsed is not None else 0
    authority = (facts.local_reversible_low_risk and facts.target_covered and facts.collision_free and facts.known_test)
    eligible = safe and authority and available > 0 and facts.compatible and issue['state'] != 'resolved'
    if safe and not authority:
        reasons.append('deferred:authority')
    elif safe and available <= 0:
        reasons.append('deferred:budget')
    if safe and disclosure == 'silent':
        reasons.append('deferred:independent')
    return {'schema_version': 1, 'owner_ref': queue['owner_ref'], 'issue_id': issue_id,
            'goal_ref': facts.goal_ref, 'policy_revision': policy['revision'], 'impact': issue['impact'],
            'blocking_scope': blocking, 'disclosure': disclosure, 'reason_codes': list(dict.fromkeys(reasons)),
            'repair_eligibility': 'eligible' if eligible else 'ineligible' if safe else 'unknown',
            'budget_ref': budget['id'] if budget else None,
            'next_trigger': 'owner-request or qualifying milestone' if safe else 'verify current dependency/risk'}


def observe(queue, observation, parent_task, now):
    """Only an actual new obstruction or changed evidence is an observation.

    A read/scan calls project(), never this reducer. Cause/parent aliases must be
    resolved with evidence by the coordinator before invocation; no lossy merge.
    """
    fields(observation, ISSUE_FIELDS); token(parent_task); stamp(now)
    result = deepcopy(queue)
    old = next((i for i in result['issues'] if i['cause_key'] == observation['cause_key']), None)
    if old is None:
        need(observation['id'] not in {i['id'] for i in result['issues']}, 'issue ID collision')
        fresh = deepcopy(observation)
        fresh['first_seen'] = fresh['last_seen'] = now
        fresh['occurrence_task_ids'] = [parent_task]
        result['issues'].append(fresh)
    else:
        need(observation['id'] == old['id'], 'cause aliases require explicit evidence, not replacement')
        changed = any(old[k] != observation[k] for k in ('impact', 'independence_evidence', 'immediate_rule_ids', 'source_refs'))
        new_parent = parent_task not in old['occurrence_task_ids']
        if old['state'] == 'resolved':
            # Resolution + genuinely new obstruction may rearm; preserve prior
            # history in immutable resolution evidence and notification episodes.
            evidence(queue['owner_ref'], old['resolution_evidence'], True)
            old['state'] = 'open'; old['notification_episode'] = None
            changed = True; new_parent = True
        if not changed and not new_parent:
            return result
        if changed and (observation['impact'] == 'material' or observation['immediate_rule_ids']):
            # An actual changed impact/evidence event can rearm even the same
            # rule. Mere scans never call observe() and cannot rearm a receipt.
            old['notification_episode'] = None
        for key in ('safe_summary', 'source_refs', 'impact', 'independence_evidence', 'immediate_rule_ids'):
            old[key] = deepcopy(observation[key])
        old['affected_scope'] = sorted(set(old['affected_scope']) | set(observation['affected_scope']))
        if new_parent and parent_task not in old['occurrence_task_ids']:
            old['occurrence_task_ids'].append(parent_task)
        old['last_seen'] = now
    return validate_queue(result, queue['owner_ref'])


def begin_interval(queue, parent, interval, scope_revision, approval_ref, reserve=0):
    """Persist before diagnosis/tool use. Same parent never gets a second budget."""
    result = deepcopy(queue); token(parent); integer(scope_revision); number(reserve)
    fields(interval, {'id', 'start', 'end', 'state', 'reason', 'evidence_ref'})
    need(interval['end'] is None and interval['state'] == 'active', 'new interval must be active')
    stamp(interval['start']); evidence(queue['owner_ref'], approval_ref, True)
    budget = budget_for(result, parent)
    if budget is None:
        budget = {'id': parent + '-budget', 'parent_task_ref': parent, 'parent_scope_revision': scope_revision,
                  'approval_ref': approval_ref, 'limit_seconds': 600, 'intervals': [],
                  'reserved_seconds': reserve, 'elapsed_state': 'observed'}
        result['budgets'].append(budget)
    need(budget['parent_scope_revision'] <= scope_revision, 'parent scope rollback')
    need(not any(i['end'] is None for i in budget['intervals']), 'active/recovered interval must close first')
    elapsed = consumed(budget)
    need(elapsed is not None and elapsed + reserve < budget['limit_seconds'], 'incidental budget exhausted/unknown')
    need(not budget['intervals'] or stamp(interval['start']) >= max(stamp(i['end']) for i in budget['intervals']),
         'clock rollback or overlapping resumed interval')
    need(interval['id'] not in {i['id'] for i in budget['intervals']}, 'interval collision')
    budget['reserved_seconds'] = reserve
    budget['intervals'].append(deepcopy(interval))
    return validate_queue(result, queue['owner_ref'])


def end_interval(queue, parent, interval_id, now, evidence_ref):
    result = deepcopy(queue); stamp(now); evidence(queue['owner_ref'], evidence_ref, True)
    budget = budget_for(result, parent); need(budget is not None, 'unknown parent budget')
    interval = next((i for i in budget['intervals'] if i['id'] == interval_id), None)
    need(interval is not None and interval['end'] is None, 'interval absent/already closed')
    interval['end'] = now; interval['evidence_ref'] = evidence_ref
    # Reconstruction of uncertain elapsed requires a separate caller-reviewed
    # clock record; simply ending one interval cannot clear an unknown clock.
    return validate_queue(result, queue['owner_ref'])


def tool_timeout(queue, policy, parent, now, prediction):
    number(prediction)
    budget = budget_for(queue, parent)
    need(budget is not None, 'missing persisted parent budget')
    elapsed = consumed(budget, now)
    need(elapsed is not None, 'unknown recovered elapsed')
    remaining = min(budget['limit_seconds'], policy['incidental_budget_seconds']) - elapsed - budget['reserved_seconds']
    need(0 < prediction <= remaining, 'tool exceeds available budget/reserve')
    return prediction


def notification(queue, policy, goal, projections, episode_id, now):
    """One proposal for simultaneous reasons. No delivery claim is made here."""
    validate_queue(queue, queue['owner_ref']); validate_policy(policy, queue['owner_ref'])
    token(goal); token(episode_id); stamp(now)
    relevant = [p for p in projections if p['goal_ref'] == goal and p['disclosure'] in {'immediate', 'milestone'}]
    if not relevant:
        return deepcopy(queue)
    ids = sorted({p['issue_id'] for p in relevant})
    reasons = sorted({r for p in relevant for r in p['reason_codes'] if r.startswith(('immediate:', 'threshold:')) or r == 'goal-blocked'})
    if not reasons:
        reasons = ['deferred:unknown-impact']
    result = deepcopy(queue)
    existing = [e for e in result['notification_episodes'] if e['goal_ref'] == goal]
    if any(set(ids) <= set(e['issue_ids']) and set(reasons) <= set(e['reason_codes'])
           and all(next(i for i in queue['issues'] if i['id'] == ident)['notification_episode'] == e['id'] for ident in ids)
           for e in existing):
        return result
    need(episode_id not in {e['id'] for e in result['notification_episodes']}, 'episode collision')
    active = sorted(i['id'] for i in result['issues'] if i['state'] != 'resolved' and goal in i['affected_scope'])
    result['notification_episodes'].append({'id': episode_id, 'owner_ref': queue['owner_ref'], 'goal_ref': goal,
        'issue_ids': ids, 'reason_codes': reasons, 'state': 'pending', 'created_at': now,
        'presented_at': None, 'presentation_evidence_ref': None, 'baseline_active_ids': active,
        'policy_revision': policy['revision']})
    for issue in result['issues']:
        if issue['id'] in ids:
            issue['notification_episode'] = episode_id
    return validate_queue(result, queue['owner_ref'])


def mark_presented(queue, episode_id, now, presentation_evidence, delivered):
    """Caller checks actual owner response. A Dream Report is not delivery."""
    need(callable(delivered) and delivered(episode_id, presentation_evidence), 'actual presentation not verified')
    result = deepcopy(queue)
    episode = next((e for e in result['notification_episodes'] if e['id'] == episode_id), None)
    need(episode is not None and episode['state'] == 'pending', 'episode absent/already presented')
    episode.update(state='presented', presented_at=now, presentation_evidence_ref=presentation_evidence)
    return validate_queue(result, queue['owner_ref'])


def disposition(queue, issue_id, state, reason, evidence_ref=None):
    need(state in {'deferred', 'resolved'}, 'unsupported disposition')
    result = deepcopy(queue)
    issue = next((i for i in result['issues'] if i['id'] == issue_id), None)
    need(issue is not None, 'unknown issue')
    prose(reason)
    issue.update(state=state, defer_reason=reason, next_trigger='owner-request or milestone' if state == 'deferred' else None)
    if state == 'resolved':
        evidence(queue['owner_ref'], evidence_ref, True); issue['resolution_evidence'] = evidence_ref
    return validate_queue(result, queue['owner_ref'])


def transition(old, new, clock_reconstruction=None):
    """Schema-valid replacement is insufficient: timers/history cannot reset."""
    for key in ('issues', 'budgets', 'notification_episodes'):
        previous = {entry['id']: entry for entry in old[key]}
        current = {entry['id']: entry for entry in new[key]}
        need(previous.keys() <= current.keys(), 'history deletion is not a queue operation')
        for ident, before in previous.items():
            after = current[ident]
            if key == 'issues':
                need(before['cause_key'] == after['cause_key'] and before['first_seen'] == after['first_seen'],
                     'issue identity/history changed')
                need(set(before['occurrence_task_ids']) <= set(after['occurrence_task_ids']), 'occurrence history reset')
                need(stamp(after['last_seen']) >= stamp(before['last_seen']), 'observation time rollback')
            elif key == 'budgets':
                for field in ('parent_task_ref', 'approval_ref', 'limit_seconds'):
                    need(before[field] == after[field], 'parent budget/approval reset')
                need(after['parent_scope_revision'] >= before['parent_scope_revision'], 'scope revision rollback')
                need(len(after['intervals']) >= len(before['intervals']), 'elapsed history removed')
                for prior, next_interval in zip(before['intervals'], after['intervals']):
                    if prior['end'] is not None:
                        need(prior == next_interval, 'closed elapsed interval changed')
                    else:
                        need(all(prior[k] == next_interval[k] for k in ('id', 'start', 'state', 'reason')),
                             'active interval identity changed')
                if before['elapsed_state'] == 'unknown' and after['elapsed_state'] == 'observed':
                    need(callable(clock_reconstruction) and clock_reconstruction(before, after),
                         'unknown clock requires separately verified reconstruction')
            elif before['state'] == 'presented':
                need(before == after, 'presented receipt history changed')
            else:
                need(all(before[k] == after[k] for k in before if k not in
                         {'state', 'presented_at', 'presentation_evidence_ref'}), 'pending episode identity changed')


def atomic_update(owner, path, expected_revision, transform, authorize, *, policy=False, clock_reconstruction=None):
    """Authorized local CAS under a nonblocking single-writer lock, no commands.

    authorize is a live coordinator permission/privacy check, not stored data.
    Neither this function nor a proposal repairs source or changes a QA verdict.
    """
    target = safe_path(owner, path)
    need(target.parent.is_dir(), 'writer never creates owner namespaces')
    integer(expected_revision)
    need(callable(authorize) and authorize(target, 'policy' if policy else 'queue'), 'write outside live authority')
    lock_path = safe_path(owner, str(target) + '.lock')
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    temporary = None
    try:
        need(stat.S_ISREG(os.fstat(fd).st_mode) and os.fstat(fd).st_nlink == 1, 'unsafe lock file')
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise Conflict('writer busy') from error
        safe_path(owner, path)
        if target.exists():
            need(target.is_file() and target.stat().st_nlink == 1, 'unsafe state file')
            current = decode(target.read_text())
        else:
            current = defaults() if policy else empty_queue(owner)
        validator = validate_policy if policy else validate_queue
        validator(current, owner)
        if current['revision'] != expected_revision:
            raise Conflict('revision moved')
        candidate = transform(deepcopy(current))
        if candidate == current:
            return current
        if policy:
            need(candidate['parent_revision'] == expected_revision and candidate['revision'] == expected_revision + 1,
                 'policy must advance from reviewed revision')
        else:
            need(candidate['revision'] == expected_revision, 'reducer must not supply revision')
            candidate['revision'] += 1
        validator(candidate, owner)
        if not policy:
            transition(current, candidate, clock_reconstruction)
        payload = json.dumps(candidate, sort_keys=True, indent=2, allow_nan=False) + '\n'
        temp_fd, temporary = tempfile.mkstemp(prefix='.' + target.name + '-', dir=target.parent)
        with os.fdopen(temp_fd, 'w') as output:
            output.write(payload); output.flush(); os.fsync(output.fileno())
        # Parent/path revalidation prevents accepting a linked target. Namespace
        # must be private/single coordinator; a hostile parent writer is excluded.
        safe_path(owner, path)
        os.replace(temporary, target); temporary = None
        directory_fd = os.open(target.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        actual = decode(target.read_text()); validator(actual, owner)
        need(actual == candidate, 'post-write state conflict')
        return actual
    finally:
        if temporary is not None:
            os.unlink(temporary)
        os.close(fd)


def load_policy(owner, path):
    """Read only; malformed update never overwrites last valid state/defaults."""
    target = safe_path(owner, path)
    if not target.exists():
        return defaults(), []
    try:
        return validate_policy(decode(target.read_text()), owner), []
    except (Invalid, OSError, UnicodeError):
        return defaults(), ['invalid-policy: conservative defaults; revision repair required']


def select_goal(inventory, claims, owner, required_work_ids):
    """Conservative selection from live consumer-derived physical claims.

    Full inventory errors remain in output. Required gates cannot call this with
    an empty goal or a data-supplied exclusion list. This grants no QA authority.
    """
    strings(required_work_ids); need(required_work_ids, 'current goal needs required identities')
    required = set(required_work_ids)
    indexes = {'work_ids': {}, 'distillation_refs': {}, 'aliases': {}}
    identities = {}
    blocked_paths, reasons = set(), []
    for claim in claims:
        fields(claim, {'path', 'owner_ref', 'work_ids', 'source_refs', 'distillation_refs', 'aliases', 'complete'})
        for key in ('work_ids', 'source_refs', 'distillation_refs', 'aliases'):
            strings(claim[key])
        need(type(claim['complete']) is bool, 'invalid completeness fact')
        if claim['owner_ref'] != owner or not claim['complete']:
            blocked_paths.add(claim['path']); reasons.append({'path': claim['path'], 'reason': 'unknown/foreign dependency claims'})
        for key, index in indexes.items():
            for ref in claim[key]:
                index.setdefault(ref, set()).add(claim['path'])
        for ref in claim['work_ids'] + claim['aliases']:
            identities.setdefault(ref, set()).add(claim['path'])
    for paths in identities.values():
        if len(paths) > 1:
            blocked_paths |= paths
            reasons += [{'path': path, 'reason': 'shared work/alias identity'} for path in sorted(paths)]
    for key, index in indexes.items():
        for paths in index.values():
            if len(paths) > 1:
                blocked_paths |= paths
                reasons += [{'path': path, 'reason': 'duplicate/shared ' + key + ' claim'} for path in sorted(paths)]
    found = set().union(*(set(c['work_ids']) for c in claims)) if claims else set()
    for missing in sorted(required - found):
        reasons.append({'path': missing, 'reason': 'missing required work identity'})
    live = [c for c in claims if required & set(c['work_ids'] + c['aliases'])]
    refs = set().union(*(set(c['source_refs'] + c['distillation_refs'] + c['aliases']) for c in live)) if live else set()
    selected = {c['path'] for c in live} | blocked_paths
    def overlaps(left, right):
        if left == right:
            return True
        a, b = Path(left), Path(right)
        return a.is_absolute() and b.is_absolute() and (a.is_relative_to(b) or b.is_relative_to(a))
    # Transitive closure, not just the first directly required row.
    while True:
        previous = set(selected)
        for claim in claims:
            if any(overlaps(a, b) for a in claim['source_refs'] + claim['distillation_refs'] + claim['aliases'] for b in refs):
                selected.add(claim['path'])
            if claim['path'] in selected:
                refs |= set(claim['source_refs'] + claim['distillation_refs'] + claim['aliases'])
        if selected == previous:
            break
    known_paths = {c['path'] for c in claims}
    for error in inventory['invalid']:
        if error['path'] not in known_paths:
            reasons.append({'path': error['path'], 'reason': 'unresolved inventory identity'})
    invalid = reasons + [e for e in inventory['invalid'] if e['path'] in selected]
    return {'schema_version': 1, 'scope': 'current-goal', 'required_work_ids': sorted(required),
            'records': [r for r in inventory['records'] if r['path'] in selected], 'invalid': invalid,
            'historical_invalid': [e for e in inventory['invalid'] if e['path'] not in selected and e['path'] in known_paths],
            'inventory': deepcopy(inventory)}


def source_population(root):
    """Independent complete product population; no submitted ignore list."""
    root = Path(root)
    need(root.is_absolute() and root.is_dir() and not root.is_symlink(), 'invalid source root')
    safe_path(root, root)
    result = {}
    for top in ('.systems', '.github', 'AGENTS.md', 'HUMANS.md', 'README.md', '.gitignore'):
        entry = root / top
        need(not entry.is_symlink(), 'linked product namespace')
        if not entry.exists():
            continue
        for path in sorted(entry.rglob('*')) if entry.is_dir() else [entry]:
            need(not path.is_symlink(), 'linked product source')
            if path.is_dir():
                need(path.name != '.git', 'nested source repository'); continue
            need(path.is_file(), 'unsupported product input')
            name = path.relative_to(root).as_posix()
            if '__pycache__' in path.parts or path.suffix in {'.pyc', '.pyo'}:
                continue
            if name == '.systems/ai/capabilities/goal-focused-maintenance-v1.json':
                continue  # Sole typed self-descriptor exclusion; committed below.
            mode = '100755' if path.stat().st_mode & 0o111 else '100644'
            result[name] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'mode': mode}
    return result


def support_profile(root):
    return {'schema_version': 1, 'capability': WIRE, 'wire_schema': 1,
            'authority': 'none', 'source_population': source_population(root)}


def verify_support(root, expected_head, expected_profile):
    """Read-only exact reviewed/committed support, not install or activation.

    The coordinator supplies externally reviewed HEAD/profile, never a queue
    label or a value learned from the candidate itself. No network or Git writes.
    """
    root = Path(root); need(root.is_absolute(), 'absolute source root required')
    need(type(expected_head) is str and re.fullmatch(r'[0-9a-f]{40}', expected_head), 'reviewed source identity required')
    fields(expected_profile, {'schema_version', 'capability', 'wire_schema', 'authority', 'source_population'})
    need(type(expected_profile['schema_version']) is int and expected_profile['schema_version'] == 1
         and type(expected_profile['wire_schema']) is int and expected_profile['wire_schema'] == 1
         and expected_profile['capability'] == WIRE and expected_profile['authority'] == 'none', 'unsupported source profile')
    def git(*args):
        try:
            return subprocess.check_output(['git', '--no-replace-objects', '-C', str(root), *args], stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as error:
            raise Invalid('source identity unavailable') from error
    need(git('rev-parse','--show-toplevel').decode().strip() == str(root), 'not an explicit source repository')
    need(git('rev-parse','HEAD').decode().strip() == expected_head, 'source HEAD differs from reviewed identity')
    path = root / '.systems/ai/capabilities/goal-focused-maintenance-v1.json'
    need(path.is_file() and not path.is_symlink(), 'installed capability absent')
    descriptor = decode(path.read_text())
    minimum = {'AGENTS.md', '.systems/ai/core/goal-focused-maintenance.md',
               '.systems/ai/core/response-contract.md', '.systems/ai/core/permissions.md',
               '.systems/scripts/lib/maintenance-policy.py', '.systems/scripts/lib/capture-record.py',
               '.systems/scripts/lib/capture-state.py', '.systems/scripts/lib/qa-evidence.py',
               '.systems/scripts/lib/maintenance-tests.py', '.systems/scripts/check-goal-focused-maintenance',
               '.systems/ai/templates/maintenance/policy.template.json'}
    need(minimum <= set(expected_profile['source_population']), 'incomplete behavioral consumer support')
    need(descriptor == expected_profile and support_profile(root) == expected_profile, 'source population or descriptor drift')
    names = set(expected_profile['source_population']) | {'.systems/ai/capabilities/goal-focused-maintenance-v1.json'}
    # Compare complete committed/index populations, bytes and modes. Private
    # workspace runtime is deliberately outside this independent product set.
    trees = {}
    for ref in ('HEAD',):
        tree = {}
        for row in git('ls-tree','-r','-z',ref).split(b'\0'):
            if not row: continue
            metadata, raw = row.split(b'\t',1); mode, kind, oid = metadata.decode().split(); name = raw.decode()
            if any(name == top or name.startswith(top + '/') for top in ('.systems','.github','AGENTS.md','HUMANS.md','README.md','.gitignore')):
                need(kind == 'blob' and mode in {'100644','100755'}, 'unsupported committed source type')
                tree[name] = (mode, oid)
        trees[ref] = tree
    index = {}
    for row in git('ls-files','--stage','-z').split(b'\0'):
        if not row: continue
        metadata, raw = row.split(b'\t',1); mode, oid, stage = metadata.decode().split(); name = raw.decode()
        if name in trees['HEAD'] or any(name == top or name.startswith(top + '/') for top in ('.systems','.github','AGENTS.md','HUMANS.md','README.md','.gitignore')):
            need(stage == '0', 'unmerged source index'); index[name] = (mode,oid)
    need(set(trees['HEAD']) == names and index == trees['HEAD'], 'incomplete/changed committed source index')
    for name,(mode,oid) in trees['HEAD'].items():
        blob = git('cat-file','blob',oid)
        need(blob == (root/name).read_bytes(), 'committed/live source mismatch')
        need(mode == ('100755' if (root/name).stat().st_mode & 0o111 else '100644'), 'source mode mismatch')
    return {'schema_version': 1, 'capability': WIRE, 'source_head': expected_head,
            'support_verified': True, 'authority': 'none', 'activated': False}


# System adapter: portable core above is kept source-identical to Workflow.
def workflow_projection(workflow_root, reviewed_head, reviewed_profile, queue, policy, issue_id, facts, now=None):
    """Shared protocol, same canonical queue/budget. Unsupported keeps old gates.

    No import/exec from an unverified candidate. Equality is established using
    complete committed/live product inputs before the shared projection is used.
    """
    verify_support(Path(workflow_root), reviewed_head, reviewed_profile)
    return project(queue, policy, issue_id, facts, now)


def read_only_review(owner, queue_path, policy_path, *, reason):
    """On-request/Dreaming/milestone inventory, with no timer/receipt mutation."""
    need(reason in {'owner-request', 'dreaming', 'milestone'}, 'unknown review trigger')
    path = safe_path(owner, queue_path, existing=True)
    queue = validate_queue(decode(path.read_text()), str(owner))
    policy, errors = load_policy(str(owner), policy_path)
    return {'schema_version': 1, 'scope': str(owner), 'reason': reason,
            'policy_revision': policy['revision'], 'issues': deepcopy(queue['issues']),
            'policy_errors': errors, 'mutations': [], 'delivered': False,
            'authority': 'none', 'supporting_only': True}
