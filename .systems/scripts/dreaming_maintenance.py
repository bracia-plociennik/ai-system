"""Explicit bounded maintenance operations for the native owner chat.

Configuration is data, never consent. The caller verifies the actual owner mandate.
No model invocation, background worker, arbitrary shell or recommendation execution.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import signal
import shutil
import sqlite3
import subprocess
import tempfile
import time

from dreaming_universal_evidence import digest, need
from dreaming_universal_sources import CREDENTIAL
import dreaming_chat as chat

KINDS = {'artifact-audit', 'artifact-repair', 'artifact-reconcile', 'checkins-refresh', 'tracker-refresh', 'workbook-refresh',
         'product-update', 'workspace-preview', 'workspace-backfill', 'repository-sync'}
DENY = {'.git', '.tmp', '.worktrees', '__pycache__', 'node_modules', 'credentials',
        'secrets', 'backups', 'chat-inputs', 'chat-output', 'chat-control', 'library',
        'generations-v4', 'tracker-outbox', 'tracker-cache'}
SECRET = re.compile(rb'(?i)(-----BEGIN .*PRIVATE KEY|\bBearer\s+\S+|\b(?:gh[pousr]_|sk-)[a-z0-9_-]{12,}|'
                    rb'\b(?:password|api[_-]?key|access[_-]?token|client[_-]?secret)\s*[:=]\s*["\x27]?[^\s"\x27]{8,})')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*')


def sha(path):
    return hashlib.sha256(chat.read_bytes(path)).hexdigest()


def root(value):
    path = Path(value)
    need(path.is_absolute() and str(path) == str(path.resolve()), 'unsafe-maintenance-root')
    chat.safe_directory(path)
    return path


def owned(base, relative, *, exists=True):
    base = root(base); rel = Path(relative)
    need(not rel.is_absolute() and rel.parts and '..' not in rel.parts, 'unsafe-maintenance-path')
    current = base
    for part in rel.parts:
        current /= part
        need(not current.is_symlink(), 'linked-maintenance-path')
    need(current.resolve().is_relative_to(base), 'outside-maintenance-owner')
    need(not exists or current.exists(), 'missing-maintenance-input')
    return current


def policy(path):
    value = chat.load(path)
    need(set(value) == {'schema_version', 'authority_ref', 'workflow_home', 'system_home',
                       'workspaces', 'products', 'artifact_scopes', 'operations'}, 'invalid-maintenance-policy')
    need(type(value['schema_version']) is int and value['schema_version'] == 1 and isinstance(value['authority_ref'], str)
         and value['authority_ref'].strip(), 'maintenance-authority-reference-required')
    root(value['workflow_home']); root(value['system_home'])
    for name in ('workspaces', 'products', 'artifact_scopes'):
        need(isinstance(value[name], dict), 'invalid-maintenance-targets')
        for key, target in value[name].items():
            need(SLUG.fullmatch(key), 'invalid-maintenance-target-id')
            allowed = ({'root', 'remote_url', 'branch', 'sync_paths'} if name == 'workspaces'
                       else {'root', 'remote_url', 'branch', 'kind'} if name == 'products'
                       else {'root', 'projects'})
            need(set(target) in (allowed, allowed | {'sync_generated'}) if name == 'workspaces'
                 else set(target) == allowed, 'invalid-maintenance-target')
            root(target['root'])
            if name != 'artifact_scopes':
                need(re.fullmatch(r'(?:https://github\.com/|git@github\.com:)[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\.git',
                                  target['remote_url']), 'unsupported-maintenance-remote')
                need(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_/-]*', target['branch'])
                     and '..' not in target['branch'] and not target['branch'].endswith('/'), 'invalid-sync-branch')
            if name == 'workspaces':
                need(isinstance(target['sync_paths'], list) and len(set(target['sync_paths'])) == len(target['sync_paths']), 'invalid-sync-inventory')
                for item in target['sync_paths']: sync_path(target['root'], item, exists=False)
                generated = target.get('sync_generated', [])
                need(isinstance(generated, list) and len(generated) == len(set(generated)) and
                     all(x in {'canonical-v4-checkins', 'tracker-projection'} for x in generated), 'invalid-generated-sync-class')
            if name == 'products': need(target['kind'] in ('system', 'workflow'), 'invalid-product-kind')
            if name == 'artifact_scopes':
                need(isinstance(target['projects'], list), 'invalid-project-list')
                for item in target['projects']: owned(target['root'], item)
    need(isinstance(value['operations'], list), 'invalid-maintenance-operations')
    ids = set()
    for op in value['operations']:
        need(isinstance(op, dict) and set(op) in ({'id', 'kind', 'target'},
             {'id', 'kind', 'target', 'repair'}, {'id', 'kind', 'target', 'files'}), 'invalid-maintenance-operation')
        need(SLUG.fullmatch(op['id']) and op['id'] not in ids, 'duplicate-maintenance-operation')
        ids.add(op['id']); need(op['kind'] in KINDS, 'unsupported-maintenance-operation')
        need(('repair' in op) == (op['kind'] == 'artifact-repair'), 'invalid-repair-operation')
        need(('files' in op) == (op['kind'] == 'workspace-backfill'), 'invalid-backfill-operation')
        table = ('artifact_scopes' if op['kind'].startswith('artifact-') else 'products'
                 if op['kind'] == 'product-update' else 'workspaces')
        need(op['target'] in value[table], 'unknown-maintenance-target')
    return value


def sync_path(base, relative, exists=True):
    need(isinstance(relative, str) and not any(c in relative for c in ('\n', '\r', '\0', '*', '?', '[', ']')), 'invalid-sync-path')
    rel = Path(relative)
    need(not any(part in DENY or part.startswith('.env') for part in rel.parts), 'excluded-sync-path')
    need(rel.suffix.lower() in {'.md', '.json', '.jsonl', '.csv', '.py', '.txt', '.mjs'}, 'unsupported-sync-file')
    return owned(base, relative, exists=exists)


@contextmanager
def lock(path):
    path = Path(path); chat.safe_directory(path.parent)
    fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        need(os.fstat(fd).st_nlink == 1, 'unsafe-maintenance-lock')
        try: fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError: raise ValueError('maintenance-already-running') from None
        yield
    finally: os.close(fd)


def start(policy_path, state_path, cycle, started_at=None):
    value = policy(policy_path); path = Path(state_path); chat.mkdir(path.parent)
    need(isinstance(cycle, str) and chat.CYCLE.fullmatch(cycle), 'invalid-maintenance-cycle')
    with lock(path.parent / 'maintenance.lock'):
        if path.exists():
            state = chat.load(path)
            need(state['cycle_id'] == cycle and state['policy_digest'] == digest(value), 'maintenance-scope-drift')
            return state
        now = time.time() if started_at is None else started_at
        state = {'schema_version': 1, 'cycle_id': cycle, 'policy_path': str(Path(policy_path).absolute()),
                 'policy_digest': digest(value), 'started_at': now, 'last_seen_at': now,
                 'deadline': now + 7200, 'maintenance_deadline': now + 2700,
                 'status': 'running', 'operations': {}, 'finished': False,
                 'implementation_digest': implementation_digest(value)}
        chat.atomic(path, state)
        return state


def implementation_digest(value):
    files = [Path(__file__), Path(__file__).with_name('dreaming_chat_dispatch.py'),
             root(value['workflow_home']) / '.systems/scripts/lib/dreaming-maintenance.py',
             root(value['system_home']) / '.systems/scripts/update-workspace',
             root(value['system_home']) / '.systems/scripts/sync-personal-ops-check-ins-v4']
    files += [root(value['system_home']) / '.systems/scripts' / name for name in
              ('dreaming_chat.py','dreaming_guard.py','dreaming_universal_sources.py',
               'dreaming_universal_evidence.py','work_evidence.py','work_evidence_ledger.py','work_evidence_xlsx.py',
               'personal_ops_v4.py','personal_ops_aggregates_v4.py')]
    return digest({str(p): sha(p) for p in files})


class Operator:
    def __init__(self, policy_path, state_path):
        self.policy_path = Path(policy_path); self.state_path = Path(state_path)
        self.policy = policy(policy_path); self.state = chat.load(state_path)
        need(self.state['policy_digest'] == digest(self.policy), 'maintenance-policy-revoked')
        need(self.state['implementation_digest'] == implementation_digest(self.policy), 'maintenance-implementation-drift')
        self.deadline = self.state['maintenance_deadline']

    def remaining(self):
        now = time.time()
        need(now >= self.state['last_seen_at'], 'maintenance-clock-rollback')
        self.state['last_seen_at'] = now
        return self.deadline - now

    def command(self, argv, cwd, *, minimum=1, timeout=120, return_status=False):
        remaining = self.remaining()
        need(remaining >= minimum, 'maintenance-budget-exhausted')
        # argv is constructed exclusively by fixed operation adapters below.
        env = {**os.environ, 'GIT_TERMINAL_PROMPT': '0',
               'PYTHONDONTWRITEBYTECODE': '1'}
        for name in ('AI_SYSTEM_SKIP_SMOKE_TESTS','AI_WORKFLOW_SKIP_SMOKE_TESTS',
                     'AI_WORKFLOW_VALIDATION_PROJECT','GIT_LITERAL_PATHSPECS',
                     'GIT_GLOB_PATHSPECS','GIT_INDEX_FILE','GIT_DIR','GIT_WORK_TREE','GIT_COMMON_DIR'):
            env.pop(name, None)
        process = subprocess.Popen(argv, cwd=cwd, env=env, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, start_new_session=True)
        try:
            out, err = process.communicate(timeout=min(timeout, remaining))
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try: process.communicate(timeout=2)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL); process.communicate()
            raise ValueError('maintenance-command-timeout') from None
        # Never copy raw stdout/stderr (possibly private) into model logs.
        need(process.returncode in ((0, 1) if return_status else (0,)), 'maintenance-command-failed:' + Path(argv[0]).name)
        need(len(out) <= 4 * 1024 * 1024, 'maintenance-output-too-large')
        text = out.decode('utf-8', errors='strict').strip()
        return (text, process.returncode) if return_status else text

    def git(self, repo, *args, **kw):
        # Use the same existing account as the exact private-origin check. Reset
        # ambient helpers and scope the fixed official helper to GitHub HTTPS;
        # never persist configuration or return credentials to the chat.
        return self.command(['git', '--literal-pathspecs', '-c', 'core.hooksPath=/dev/null',
                             '-c', 'credential.helper=',
                             '-c', 'credential.https://github.com.helper=!gh auth git-credential',
                             '-C', str(repo), *args], repo, **kw)

    def checkpoint(self): chat.atomic(self.state_path, self.state)

    def workflow_module(self):
        path = root(self.policy['workflow_home']) / '.systems/scripts/lib/dreaming-maintenance.py'
        spec = importlib.util.spec_from_file_location('workflow_dreaming_maintenance', path)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        return module

    def artifact(self, op):
        target = self.policy['artifact_scopes'][op['target']]; module = self.workflow_module()
        if op['kind'] == 'artifact-audit':
            return {'status': 'executed', 'audits': [module.audit(target['root'], p) for p in target['projects']]}
        if op['kind'] == 'artifact-reconcile':
            results = [module.reconcile(target['root'], p) for p in target['projects']]
            return {'status': 'executed' if any(x['status'] == 'executed' for x in results) else 'no-change',
                    'projects': results}
        need(any(Path(op['repair']['file']).is_relative_to(p) for p in target['projects']), 'repair-outside-selected-project')
        return module.repair(target['root'], op['repair'])

    def checkins(self, target):
        workspace = root(target['root'])
        canonical = owned(workspace, 'personal-ops/check-ins-v4')
        files = sorted(canonical.rglob('*.md'))
        before = {str(p): sha(p) for p in files}
        script = root(self.policy['system_home']) / '.systems/scripts/sync-personal-ops-check-ins-v4'
        from personal_ops_aggregates_v4 import is_unified
        if is_unified(workspace):
            _, status = self.command([str(script),'--workspace',str(workspace),'--status-only'],
                                     workspace,return_status=True)
            if status == 0:
                return {'status':'no-change','effect':'source-hashes-and-derived-generation-current'}
        self.command([str(script), '--workspace', str(workspace), '--post-write'], workspace, minimum=30)
        need(before == {str(p): sha(p) for p in files}, 'canonical-checkin-changed')
        return {'status': 'executed', 'canonical_files_unchanged': len(files)}

    def tracker(self, target):
        # Read-only SQLite snapshot. Never instantiate TaskTracker: its constructor
        # creates state/schema/secret rows even when used for inspection.
        workspace = root(target['root'])
        path = owned(workspace, 'work-evidence/silverbullet-tracker/state.sqlite3')
        need(path.stat().st_nlink == 1, 'unsafe-tracker-state')
        db = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True, timeout=2)
        try:
            db.execute('BEGIN')
            need(db.execute('PRAGMA quick_check').fetchone()[0] == 'ok', 'tracker-integrity-failed')
            rows = [list(row) for row in db.execute('SELECT state, review, count(*) FROM runs GROUP BY state, review ORDER BY state, review').fetchall()]
            version = db.execute("SELECT value FROM meta WHERE key='version'").fetchone()[0]
            confirmed = db.execute("SELECT count(*) FROM approvals WHERE state='committed'").fetchone()[0]
        finally: db.close()
        projection = {'schema_version': 1, 'version': version, 'runs': rows,
                      'committed_approvals': confirmed, 'time_or_approval_mutated': False}
        output = owned(workspace, 'work-evidence/silverbullet-tracker/maintenance-projection.json', exists=False)
        if output.exists() and chat.load(output) == projection:
            return {'status': 'no-change'}
        chat.atomic(output, projection)
        return {'status': 'executed', 'conflicts_require_owner': any(row[1] for row in rows)}

    def workbook(self, target):
        """Refresh the existing native view of committed WEP, never import rows."""
        from work_evidence_ledger import Ledger
        from work_evidence_xlsx import Tracker
        workspace=root(target['root'])
        for relative in ('work-evidence/config.json','work-evidence/entities.json'):
            owned(workspace,relative)
        ledger=Ledger(workspace); before=ledger.snapshot(); view=Tracker(ledger)
        if view.path.exists():
            _,meta,_=view.snapshot(allow_stale_ledger=True)
            if meta['ledger_hash']==before['ledger_hash']:
                return {'status':'no-change','effect':'committed-ledger-view-current'}
        script=owned(self.policy['system_home'],'.systems/scripts/work-evidence-xlsx')
        output=self.command([str(script),'export','--workspace',str(workspace),'--owner-approved'],workspace,minimum=30)
        result=json.loads(output)
        need(result.get('status')=='exported' and ledger.snapshot()==before,'workbook-or-ledger-changed')
        return {'status':'executed','effect':'committed-ledger-view-refreshed',
                'ledger_unchanged':True,'workbook_sha256':result['sha256']}

    def product(self, target, *, controller_barrier=False):
        repo = root(target['root']); home = root(self.policy['system_home'])
        # A running controller may not replace its own imported policy/code.
        if Path(__file__).resolve().is_relative_to(repo):
            need(controller_barrier and self.state['finished'], 'executing-controller-update-deferred')
            session_path = chat.paths({'workspace': self.state['report_workspace']}, self.state['cycle_id'])['state']
            need(not session_path.exists(), 'analysis-already-prepared')
        need(self.git(repo, 'remote', 'get-url', 'origin') == target['remote_url'], 'product-origin-drift')
        need(self.remaining() >= 900, 'insufficient-full-update-budget')
        script = owned(repo, '.systems/scripts/update-from-upstream')
        self.command([str(script), '--dry-run', '--remote', 'origin', '--branch', target['branch']], repo)
        output = self.command([str(script), '--remote', 'origin', '--branch', target['branch']], repo, minimum=900, timeout=2400)
        if target['kind'] == 'system':
            markers = [line for line in output.splitlines() if line.startswith('AI_SYSTEM_VALIDATION_RESULT ')]
            need(markers and 'profile=full status=completed exit_code=0' in markers[-1]
                 and 'smoke=completed' in markers[-1], 'official-full-smoke-evidence-missing')
        else:
            markers = [line for line in output.splitlines() if line.startswith('AI_WORKFLOW_UPDATE_VALIDATION_COMPLETE ')]
            need(markers and 'result=pass' in markers[-1]
                 and re.search(r'^AI_WORKFLOW_SMOKE_COMPLETE group=all result=pass ',output,re.M),
                 'official-full-smoke-evidence-missing')
        self.state.setdefault('implementation_changes', []).append({
            'before': self.state['implementation_digest'], 'after': implementation_digest(self.policy),
            'basis': 'official-updater-full-completed'})
        self.state['implementation_digest'] = implementation_digest(self.policy)
        return {'status': 'executed', 'head': self.git(repo, 'rev-parse', 'HEAD'),
                'full_validation': 'completed-by-official-updater',
                'validation_output_sha256': hashlib.sha256(output.encode()).hexdigest()}

    def workspace_preview(self, target):
        workspace = root(target['root']); home = root(self.policy['system_home'])
        script = owned(home, '.systems/scripts/update-workspace')
        self.command([str(script), '--workspace', str(workspace), '--dry-run'], home, minimum=30)
        return {'status': 'executed', 'effect': 'preview-only', 'backfill': 'explicit-reviewed-additive-operations-only'}

    def workspace_backfill(self, target, files):
        workspace = root(target['root']); home = root(self.policy['system_home'])
        need(isinstance(files, list) and files and len(files) == len(set(files)), 'invalid-backfill-files')
        for relative in files:
            need(Path(relative).name in {'README.md', 'project-state.md', 'capture-state.md'}, 'non-neutral-backfill-blocked')
            need(not owned(workspace, relative, exists=False).exists(), 'backfill-file-exists')
        script = owned(home, '.systems/scripts/update-workspace')
        preview = self.command([str(script), '--workspace', str(workspace), '--dry-run'], home)
        # The official tool reports all writes before apply. Unknown output or a
        # broader proposed file population blocks, not silently widens the scope.
        planned = []
        for line in preview.splitlines():
            if line.startswith('would create file: '):
                full = (home / line.removeprefix('would create file: ')).resolve()
                need(full.is_relative_to(workspace), 'backfill-preview-outside-owner')
                planned.append(str(full.relative_to(workspace)))
        need(set(planned) == set(files), 'backfill-preview-needs-review')
        self.command([str(script), '--workspace', str(workspace)], home, minimum=60)
        need(all(owned(workspace, f).is_file() for f in files), 'backfill-incomplete')
        return {'status': 'executed', 'additive_files': files}

    def repository(self, target, receipt):
        repo = root(target['root']); branch = target['branch']; remote = target['remote_url']
        need(self.git(repo, 'rev-parse', '--show-toplevel') == str(repo), 'not-exact-repository')
        need(self.git(repo, 'remote', 'get-url', 'origin') == remote
             and self.git(repo,'remote','get-url','--push','origin') == remote, 'workspace-origin-drift')
        need(self.git(repo, 'branch', '--show-current') == branch, 'workspace-branch-drift')
        _, filters = self.command(['git','-C',str(repo),'config','--get-regexp',
                                   r'^filter\..*\.(clean|smudge|process)$'],repo,return_status=True)
        need(filters == 1,'repository-filters-require-review')
        need(not self.git(repo, 'diff', '--cached', '--name-only'), 'existing-staged-work')
        # Low-level deterministic commits must not silently bypass an owner's
        # installed repository hook/gate. Unknown active hooks need review first.
        configured, status = self.command(['git','-C',str(repo),'config','--path','--get','core.hooksPath'],repo,return_status=True)
        need(status == 1 or configured == '/dev/null', 'repository-hooks-require-review')
        if status == 1:
            hooks = Path(self.command(['git','-C',str(repo),'rev-parse','--path-format=absolute','--git-path','hooks'],repo))
            if hooks.exists():
                need(not hooks.is_symlink(), 'repository-hooks-require-review')
                need(not any(p.is_symlink() or (p.is_file() and p.stat().st_mode & 0o111)
                             for p in hooks.iterdir() if not p.name.endswith('.sample')),
                     'repository-hooks-require-review')
        # Privacy must be current and tied to the exact remote, not a config flag.
        def destination():
            need(self.git(repo,'remote','get-url','origin') == remote
                 and self.git(repo,'remote','get-url','--push','origin') == remote,'workspace-origin-drift')
            slug = remote.removeprefix('https://github.com/').removesuffix('.git')
            view = json.loads(self.command(['gh','repo','view',remote.removesuffix('.git'),'--json','isPrivate,nameWithOwner'],repo))
            need(view == {'isPrivate': True,'nameWithOwner':slug},'verified-private-origin-required')
        destination()
        common = Path(self.git(repo, 'rev-parse', '--path-format=absolute', '--git-common-dir'))
        with lock(common / 'dreaming-maintenance-sync.lock'):
            # Use a private alternate index. Never stage or commit another actor's work.
            tracking='refs/remotes/origin/'+branch
            self.git(repo, 'fetch', remote, 'refs/heads/'+branch+':'+tracking)
            remote_head = self.git(repo, 'rev-parse', 'FETCH_HEAD')
            head = self.git(repo, 'rev-parse', 'HEAD')
            old_commit = receipt.get('commit')
            if old_commit:
                if remote_head == old_commit:
                    return {'status': 'executed', 'commit': old_commit, 'push_verified': True}
                need(head == old_commit, 'uncertain-sync-head-changed')
            if head != remote_head and not old_commit:
                # A dirty tree can only be imported by ff when Git itself can
                # preserve it; disallow dirty imports entirely for predictable CAS.
                need(not self.git(repo, 'status', '--porcelain'), 'remote-import-needs-clean-worktree')
                self.git(repo, 'merge-base', '--is-ancestor', head, remote_head)
                self.git(repo, 'merge', '--ff-only', remote_head)
                head = remote_head
            files = list(target['sync_paths'])
            if 'canonical-v4-checkins' in target.get('sync_generated', []):
                source = owned(repo, 'personal-ops/check-ins-v4')
                for file in source.glob('[0-9][0-9][0-9][0-9]/*.md'):
                    try: date = datetime.strptime(file.stem, '%Y-%m-%d')
                    except ValueError: continue
                    need(file.parent.name == str(date.year), 'checkin-year-mismatch')
                    files.append(str(file.relative_to(repo)))
            if 'tracker-projection' in target.get('sync_generated', []):
                projection = owned(repo, 'work-evidence/silverbullet-tracker/maintenance-projection.json', exists=False)
                if projection.exists(): files.append(str(projection.relative_to(repo)))
            files = sorted(set(files)); need(files, 'reviewed-sync-inventory-empty')
            entries = {}
            for relative in files:
                file = sync_path(repo, relative)
                need(file.is_file() and file.stat().st_nlink == 1, 'unsafe-sync-file')
                data = chat.read_bytes(file)
                need(not SECRET.search(data) and not CREDENTIAL.search(data), 'suspected-sync-secret')
                entries[relative] = hashlib.sha256(data).hexdigest()
            # Only files that differ from HEAD participate; input fingerprint binds
            # future replay to this reviewed set and current bytes.
            receipt['input_digest'] = digest(entries); self.checkpoint()
            temp = tempfile.TemporaryDirectory(prefix='dreaming-git-')
            try:
                index = str(Path(temp.name) / 'index')
                real_index = Path(self.git(repo, 'rev-parse', '--path-format=absolute', '--git-path', 'index'))
                initial_index = chat.read_bytes(real_index) if real_index.exists() else None
                if initial_index is not None:
                    Path(index).write_bytes(initial_index)
                def indexed(*args):
                    # No shell/env command supplied by policy.
                    return self.command(['env', 'GIT_INDEX_FILE=' + index, 'git', '--literal-pathspecs', '-c',
                                         'core.hooksPath=/dev/null', '-C', str(repo), *args], repo)
                if initial_index is None: indexed('read-tree', head)
                indexed('add', '--', *files)
                changes = [p for p in indexed('diff', '--cached', '--name-only', '-z').split('\0') if p]
                need(set(changes) <= set(files), 'unexpected-staged-path')
                for relative, expected in entries.items():
                    need(sha(sync_path(repo, relative)) == expected, 'sync-input-changed')
                if changes and not old_commit:
                    tree = indexed('write-tree')
                    commit = indexed('commit-tree', tree, '-p', head, '-m',
                                     'Synchronize reviewed workspace maintenance artifacts')
                    # Durable intent before changing branch or sending anything.
                    receipt.update(commit=commit, parent=head, paths=changes); self.checkpoint()
                    index_lock = Path(str(real_index) + '.lock')
                    fd = os.open(index_lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
                    try:
                        current_index = chat.read_bytes(real_index) if real_index.exists() else None
                        need(current_index == initial_index, 'concurrent-index-change')
                        need(self.git(repo,'branch','--show-current') == branch
                             and self.git(repo,'rev-parse','HEAD') == head, 'concurrent-branch-change')
                        for relative, expected in entries.items():
                            need(sha(sync_path(repo,relative)) == expected, 'sync-input-changed')
                        with os.fdopen(fd, 'wb') as stream:
                            stream.write(Path(index).read_bytes()); stream.flush(); os.fsync(stream.fileno())
                        fd = None
                        self.git(repo, 'update-ref', 'refs/heads/' + branch, commit, head)
                        os.replace(index_lock, real_index)
                    finally:
                        if fd is not None: os.close(fd)
                        index_lock.unlink(missing_ok=True)
                elif not old_commit:
                    return {'status': 'no-change', 'push_verified': True}
            finally: temp.cleanup()
            commit = receipt['commit']
            destination()
            current = self.git(repo, 'ls-remote', '--exit-code', remote, 'refs/heads/' + branch).split()[0]
            need(current in {remote_head, commit}, 'remote-moved-before-push')
            if current != commit:
                self.git(repo, 'push', remote, commit + ':refs/heads/' + branch)
            actual = self.git(repo, 'ls-remote', '--exit-code', remote, 'refs/heads/' + branch).split()[0]
            need(actual == commit, 'push-unverified')
            # Some Git versions update the matching tracking ref during push.
            tracked = self.git(repo, 'rev-parse', tracking)
            need(tracked in {remote_head, commit}, 'tracking-ref-moved-after-push')
            self.git(repo, 'update-ref', tracking, commit, tracked)
            return {'status': 'executed', 'commit': commit, 'push_verified': True}

    def execute(self, operation_id):
        with lock(self.state_path.parent / 'maintenance.lock'):
            self.state = chat.load(self.state_path)
            need(self.state['policy_digest'] == digest(policy(self.policy_path)), 'maintenance-policy-revoked')
            need(self.state['implementation_digest'] == implementation_digest(self.policy), 'maintenance-implementation-drift')
            need(not self.state['finished'], 'maintenance-already-finished')
            need(self.remaining() > 0, 'maintenance-budget-exhausted')
            op = next((o for o in self.policy['operations'] if o['id'] == operation_id), None)
            need(op is not None, 'unknown-maintenance-operation')
            previous = self.state['operations'].get(operation_id)
            if previous and previous['status'] in ('executed', 'no-change', 'blocked', 'error'):
                return previous
            receipt = previous or {'status': 'intent', 'kind': op['kind'], 'target': op['target']}
            self.state['operations'][operation_id] = receipt; self.checkpoint()
            try:
                if op['kind'].startswith('artifact-'): result = self.artifact(op)
                else:
                    table = 'products' if op['kind'] == 'product-update' else 'workspaces'
                    target = self.policy[table][op['target']]
                    result = ({'checkins-refresh': lambda: self.checkins(target),
                               'tracker-refresh': lambda: self.tracker(target),
                               'workbook-refresh': lambda: self.workbook(target),
                               'workspace-preview': lambda: self.workspace_preview(target),
                               'workspace-backfill': lambda: self.workspace_backfill(target, op['files']),
                               'repository-sync': lambda: self.repository(target, receipt),
                               'product-update': lambda: ({'status':'deferred','reason':'controller-update-barrier-required'}
                                   if Path(__file__).resolve().is_relative_to(root(target['root'])) else self.product(target))}[op['kind']])()
                receipt.update(result)
            except (ValueError, OSError, sqlite3.Error, KeyError, TypeError) as error:
                # Uncertain Git intent is retained and must be reconciled, never
                # retried as a new commit. No raw subprocess diagnostics exported.
                receipt.update(status='uncertain' if receipt.get('commit') else 'blocked',
                               reason=str(error)[:200])
            self.checkpoint()
            return receipt

    def finish(self):
        with lock(self.state_path.parent / 'maintenance.lock'):
            self.state = chat.load(self.state_path)
            need(self.state['policy_digest'] == digest(policy(self.policy_path)), 'maintenance-policy-revoked')
            self.state['finished'] = True
            self.state['status'] = ('partial' if len(self.state['operations']) < len(self.policy['operations'])
                                    or any(r['status'] not in ('executed', 'no-change')
                                           for r in self.state['operations'].values()) else 'completed')
            self.checkpoint(); return self.state


def controller_update_barrier(policy_path, state_path, workspace):
    """Called only after the native maintenance turn settled, before any snapshot.

    Updates requiring replacement of the running controller end that controller
    process through exec. Its successor resumes this same cycle and deadline.
    """
    operator = Operator(policy_path, state_path)
    with lock(operator.state_path.parent / 'maintenance.lock'):
        operator.state = chat.load(state_path)
        need(operator.state['finished'], 'maintenance-turn-not-finished')
        operator.state['report_workspace'] = str(root(workspace))
        need(not chat.paths({'workspace': workspace}, operator.state['cycle_id'])['state'].exists(), 'analysis-already-prepared')
        for op in operator.policy['operations']:
            receipt = operator.state['operations'].get(op['id'], {})
            if receipt.get('status') != 'deferred' or op['kind'] != 'product-update': continue
            target = operator.policy['products'][op['target']]; repo = root(target['root'])
            need(repo == root(operator.policy['system_home']) and Path(__file__).resolve().is_relative_to(repo), 'not-controller-update-target')
            if operator.remaining() < 900:
                receipt.update(status='blocked', reason='insufficient-controller-update-budget');operator.checkpoint();continue
            try:
                need(operator.git(repo,'remote','get-url','origin') == target['remote_url'], 'controller-origin-drift')
                operator.git(repo,'fetch','origin',target['branch'])
                before=operator.git(repo,'rev-parse','HEAD');upstream=operator.git(repo,'rev-parse','FETCH_HEAD')
            except (ValueError,OSError) as error:
                receipt.update(status='blocked',reason=str(error)[:200]);operator.checkpoint();continue
            if before == upstream:
                receipt.update(status='no-change',reason='official-source-equal');operator.checkpoint();continue
            _, behind=operator.git(repo,'merge-base','--is-ancestor',before,upstream,return_status=True)
            if behind:
                _, ahead=operator.git(repo,'merge-base','--is-ancestor',upstream,before,return_status=True)
                receipt.update(status='no-change' if ahead == 0 else 'blocked',
                               reason='local-approved-source-ahead' if ahead == 0 else 'official-source-diverged')
                operator.checkpoint();continue
            receipt.update(status='update-barrier-intent',before_head=before);operator.checkpoint()
            try:
                result=operator.product(target,controller_barrier=True)
            except (ValueError,OSError) as error:
                receipt.update(status='blocked',reason=str(error)[:200]);operator.checkpoint()
                raise ValueError('controller-update-failed-requires-reconciliation') from None
            receipt.update(result);operator.checkpoint()
            return {'restart_required':True}
        return {'restart_required':False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['inspect', 'start', 'execute', 'finish'])
    parser.add_argument('--policy', required=True); parser.add_argument('--state')
    parser.add_argument('--cycle'); parser.add_argument('--operation')
    args = parser.parse_args()
    try:
        if args.action == 'inspect':
            value = policy(args.policy)
            result = {'operations': value['operations'], 'execution_authorized': False}
        elif args.action == 'start': result = start(args.policy, args.state, args.cycle)
        else:
            operator = Operator(args.policy, args.state)
            result = operator.finish() if args.action == 'finish' else operator.execute(args.operation)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    except (ValueError, OSError, TypeError) as error:
        parser.exit(1, 'Maintenance blocked: ' + str(error) + '\n')


if __name__ == '__main__': main()
