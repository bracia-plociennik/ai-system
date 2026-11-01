"""Read-only registered System/repository context; never permission or enrollment."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from local_paths import resolve_path, LocalPathError

REGISTRATION_KEYS = {'schema_version', 'system_id', 'system_home', 'enabled', 'adapter_ids',
                     'owner_workspace_id', 'owner_asset_id'}
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*')
POLICY = ('.systems/ai/core/agent-startup.md', '.systems/ai/core/system-workflow-authority.md')
CAPABILITY_FILES = {
    'shared-workflow-v1': ('.systems/scripts/agent_context.py', '.systems/scripts/durable_runtime.py',
        '.systems/scripts/project-orchestration-preflight', '.systems/scripts/configure-shared-workflow',
        '.systems/ai/core/shared-workflow.md', '.systems/scripts/capture_parity.py'),
    'shared-installation-v1': ('.systems/scripts/durable_runtime.py',
        '.systems/scripts/resolve-workflow-env', '.systems/scripts/init-workspace',
        '.systems/scripts/update-workspace', '.systems/scripts/bootstrap-target-worktree',
        '.systems/scripts/update-from-upstream', '.systems/ai/core/shared-installation.md',
        '.systems/ai/templates/root-agents-shared.template.md'),
    'agent-startup-v1': (*POLICY, '.systems/ai/core/agent-adapters.md',
        '.systems/scripts/agent_context.py', '.systems/scripts/agent_adapters.py',
        '.systems/scripts/local_paths.py', '.systems/scripts/resolve-agent-context',
        '.systems/scripts/manage-agent-adapter', '.systems/scripts/durable_runtime.py'),
    'work-lead-v1': ('AGENTS.md', '.systems/ai/core/work-lead.md',
        '.systems/ai/core/permissions.md', '.systems/ai/core/risk-model.md',
        '.systems/ai/core/runtime-integrity.md', '.systems/scripts/lib/coordinator-status.py')}


class ContextError(ValueError):
    def __init__(self, reason, code=2):
        super().__init__(reason)
        self.code = code


def no_duplicates(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ContextError('duplicate JSON key')
        out[key] = value
    return out


def safe_bytes(path, limit=131072):
    path = Path(path)
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ContextError('linked context input')
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size > limit:
            raise ContextError('unsafe or oversized context input')
        data = stream.read(limit + 1)
        after = os.fstat(stream.fileno())
    signature = lambda x: (x.st_dev, x.st_ino, x.st_size, x.st_mtime_ns, x.st_ctime_ns)
    if len(data) > limit or signature(before) != signature(after) or signature(after) != signature(path.stat()):
        raise ContextError('context input changed during read')
    return data


def strict_json(path):
    return json.loads(safe_bytes(path), object_pairs_hook=no_duplicates,
                      parse_constant=lambda _: (_ for _ in ()).throw(ContextError('invalid JSON constant')))


def concrete(value, *, base=None, environment=None):
    try:
        value = os.fspath(value)
        if isinstance(value, str) and ('..' in Path(value).parts or any(c in value for c in '*?[]')):
            raise ContextError('context path must be concrete without traversal')
        return resolve_path(value, base=base, allow_relative=base is not None, environment=environment)
    except LocalPathError as error:
        raise ContextError(str(error)) from None


def git(path, *args):
    result = subprocess.run(['git', '-C', str(path), *args], capture_output=True, text=True,
                            env=dict(os.environ, GIT_OPTIONAL_LOCKS='0'), timeout=10)
    return result.stdout.strip() if result.returncode == 0 else None


def common_git(path):
    root = git(path, 'rev-parse', '--show-toplevel')
    common = git(path, 'rev-parse', '--path-format=absolute', '--git-common-dir')
    return (concrete(root), concrete(common)) if root and common else (None, None)


def registration(environment=None, system_home=None):
    env = dict(os.environ if environment is None else environment)
    home = concrete(env.get('HOME', str(Path.home())), environment=env)
    path = home / '.config/ai-system/installation.json'
    if not path.exists():
        raise ContextError('user installation registration unavailable', 3)
    record = strict_json(path)
    if not isinstance(record, dict) or set(record) != REGISTRATION_KEYS:
        raise ContextError('unsupported installation registration fields')
    if type(record['schema_version']) is not int or record['schema_version'] != 1:
        raise ContextError('unsupported installation registration version')
    for key in ('system_id', 'owner_workspace_id', 'owner_asset_id'):
        if not isinstance(record[key], str) or not SLUG.fullmatch(record[key]):
            raise ContextError('invalid registration identity')
    if type(record['enabled']) is not bool:
        raise ContextError('invalid enabled state')
    ids = record['adapter_ids']
    if (not isinstance(ids, list) or any(not isinstance(x, str) or x not in {'codex', 'claude-code', 'generic'} for x in ids)
            or len(ids) != len(set(ids))):
        raise ContextError('unsupported or duplicate adapter identity')
    # Self-referential system_home expansion is rejected instead of defaulting to source checkout.
    if not isinstance(record['system_home'], str) or 'AI_SYSTEM_' in record['system_home']:
        raise ContextError('system_home must derive from HOME or an absolute path')
    installed = concrete(record['system_home'], environment=env)
    for selected in (system_home, env.get('AI_SYSTEM_HOME')):
        if selected and concrete(selected, environment=env) != installed:
            raise ContextError('selected installation conflicts with user registration', 4)
    role = strict_json(installed / 'ai-system.local.json')
    if not isinstance(role, dict) or role != {'schema_version': 1, 'role': 'management'} or type(role.get('schema_version')) is not int:
        raise ContextError('registered installation must have explicit management role', 3)
    if any(not (installed / rel).is_file() for rel in POLICY):
        raise ContextError('registered installation startup policy unavailable', 3)
    env['AI_SYSTEM_HOME'] = str(installed)
    return record, installed, path, env


def workspace_registry(installed, env):
    path = installed / 'ai-system-workspaces.md'
    rows = []
    for line in safe_bytes(path).decode('utf-8').splitlines():
        if not line.startswith('|'):
            continue
        values = [x.strip().strip('`') for x in line.strip('|').split('|')]
        if len(values) != 6 or values[0] == 'workspace-id' or values[0].startswith('---'):
            continue
        ident, raw, default, state, _, _ = values
        if not SLUG.fullmatch(ident) or default not in {'yes', 'no'}:
            raise ContextError('invalid workspace registry row')
        if state != 'active':
            continue
        root = concrete(raw, base=installed, environment=env)
        if not root.is_dir():
            raise ContextError('active registered workspace unavailable', 3)
        rows.append((ident, root, default == 'yes'))
    if (not rows or len({x[0] for x in rows}) != len(rows) or len({x[1] for x in rows}) != len(rows)
            or sum(x[2] for x in rows) != 1):
        raise ContextError('ambiguous workspace registry', 4)
    return rows, path


def project_associations(rows, repo, common, env):
    matches, fingerprints = [], []
    for _, workspace, _ in rows:
        patterns = ('project-state/*/links.md', 'clients/*/project-state/*/links.md',
                    'owned-assets/*/project-state/*/links.md')
        for pattern in patterns:
            for link in sorted(workspace.glob(pattern)):
                raw = safe_bytes(link)
                values = re.findall(r'^repo-path:[ \t]*(.*?)[ \t]*$', raw.decode('utf-8'), re.M)
                if not values:
                    continue  # Non-repository source projects have no Git association.
                if len(values) != 1 or not values[0]:
                    raise ContextError('ambiguous project repository association', 4)
                local_env = dict(env, AI_SYSTEM_WORKSPACE_HOME=str(workspace))
                target = concrete(values[0].strip('`'), base=workspace, environment=local_env)
                if not target.is_dir():
                    continue  # pending repositories stay pending, never enrolled or cloned
                target_root, target_common = common_git(target)
                if target_root != target:
                    if not (target / '.git').exists():
                        continue  # Existing pending directory must not inherit its workspace Git root.
                    raise ContextError('project link does not identify a repository root', 4)
                if repo == target or common == target_common:
                    matches.append((workspace, link.parent.name, target, link.parent))
                    fingerprints.append((str(link), hashlib.sha256(raw).hexdigest()))
    if len(matches) > 1:
        raise ContextError('multiple project/workspace associations', 4)
    return matches, fingerprints


def workflow_context(repo, environment=None, *, system_home=None, shared_only=False):
    if repo is None:
        return None, None, None
    import durable_runtime
    env = os.environ if environment is None else environment
    try:
        installed = system_home or durable_runtime.registered_system(env)
        shared = durable_runtime.shared_installation(installed, repo) if installed else None
        if shared is not None and repo != shared:
            if source_consistency(shared, 'shared-installation-v1.json', 'shared-installation-v1') != 'verified-source':
                raise ContextError('shared Workflow consumer source is not verified', 3)
            selected = durable_runtime.workflow_environment(shared, mode='shared', target=repo,
                system_root=installed, environment=env)
            return shared, Path(selected['AI_WORKFLOW_WORKSPACE_HOME']), 'shared'
        if shared_only:
            return None, None, None
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        if isinstance(exc, ContextError):
            raise
        raise ContextError(str(exc), 4) from exc
    try:
        binding = durable_runtime.load(repo)
    except ValueError as exc:
        raise ContextError(str(exc), 4) from exc
    canonical = Path(binding['canonical']['root']) if binding else repo
    if (repo / '.systems/scripts/resolve-workflow-env').is_file() and (repo / '.systems/ai/core/repository-modes.md').is_file():
        home, mode = repo, 'official'
    elif (repo / 'ai-workflow/.systems/scripts/resolve-workflow-env').is_file():
        home, mode = repo / 'ai-workflow', 'target'
    elif binding and (canonical / 'ai-workflow/.systems/scripts/resolve-workflow-env').is_file():
        home, mode = canonical / 'ai-workflow', 'target'
    else:
        return None, None, None
    concrete(str(home))
    if (not (home / 'AGENTS.md').is_file() or (home / 'AGENTS.md').is_symlink()
            or git(home, 'rev-parse', '--show-toplevel') != str(home) or not git(home, 'rev-parse', 'HEAD')):
        raise ContextError('Workflow installation unavailable', 3)
    try:
        workspace = durable_runtime.resolve(repo, (os.environ if environment is None else environment).get('AI_WORKFLOW_WORKSPACE_HOME'))
    except ValueError as exc:
        raise ContextError(str(exc), 4) from exc
    return home, workspace or repo / 'ai-workflow-workspace', mode


def instruction_chain(current, repo, env, tool):
    """Observe Codex's native chain; no config mutation or implicit authority."""
    if tool != 'codex':
        return {'status': 'design-only', 'native_verification': 'unverified', 'files': [], 'bytes': 0}
    codex = concrete(env.get('CODEX_HOME', str(Path(env['HOME']) / '.codex')), environment=env)
    directories = [codex]
    if repo:
        directories.append(repo)
        cursor = repo
        for part in current.relative_to(repo).parts:
            cursor = cursor / part
            directories.append(cursor)
    files, shadows, reviewed, manual_reads, total = [], [], [], [], 0
    seen = set()
    for directory in directories:
        normal, override = directory / 'AGENTS.md', directory / 'AGENTS.override.md'
        chosen = None
        for path in (override, normal):
            if path.exists() and safe_bytes(path).strip():
                chosen = path
                break
        if chosen is None: continue
        if chosen in seen: raise ContextError('duplicate instruction path', 4)
        seen.add(chosen)
        raw = safe_bytes(chosen)
        total += len(raw)
        files.append({'path': str(chosen), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
        if chosen == override:
            shadows.append(str(override))
            # A local shared-routing entry may defer the unchanged full source
            # contract to an explicit read. This never admits global overrides.
            installed = concrete(env['AI_SYSTEM_HOME'], environment=env) if env.get('AI_SYSTEM_HOME') else None
            if installed and directory == repo and directory != codex and directory.is_relative_to(installed):
                config = installed / 'ai-workflow-workspace/shared-installation.json'
                reviews = installed / 'ai-workflow-workspace/shared-entrypoints.json'
                if config.is_file() and reviews.is_file():
                    setting, index = strict_json(config), strict_json(reviews)
                    if (setting == {'schema_version': 1, 'enabled': True, 'workflow_home': 'ai-workflow'}
                            and type(setting.get('schema_version')) is int
                            and isinstance(index, dict) and set(index) == {'schema_version', 'entries'}
                            and type(index['schema_version']) is int and index['schema_version'] == 1
                            and isinstance(index['entries'], dict)):
                        entry = index['entries'].get(str(directory.relative_to(installed)))
                        if (isinstance(entry, dict) and set(entry) == {'original_sha256', 'override_sha256'}
                                and normal.is_file()
                                and entry['original_sha256'] == hashlib.sha256(safe_bytes(normal)).hexdigest()
                                and entry['override_sha256'] == hashlib.sha256(raw).hexdigest()):
                            reviewed.append(str(override))
                            manual_reads.append(str(normal))
    issues = (['instruction override requires deliberate review'] if set(shadows) - set(reviewed) else [])
    if total > 16384: issues.append('combined automatic guidance exceeds 16 KiB')
    return {'status': 'review-required' if issues else 'within-budget', 'native_verification': 'unverified',
            'files': files, 'bytes': total, 'shadowing': shadows, 'reviewed_shared_entrypoints': reviewed,
            'required_manual_reads': manual_reads, 'issues': issues}


def source_consistency(root, capability, contract):
    """Capabilities are content claims, never executable consent or native proof."""
    if contract not in CAPABILITY_FILES:
        return 'unsupported'
    path = root / '.systems/ai/capabilities' / capability
    if not path.exists(): return 'unavailable'
    value = strict_json(path)
    required = {'schema_version', 'contract', 'source_files', 'native_verification'}
    if (not isinstance(value, dict) or set(value) != required or type(value['schema_version']) is not int
            or value['schema_version'] != 1 or value['contract'] != contract
            or not isinstance(value['source_files'], dict)
            or set(value['source_files']) != set(CAPABILITY_FILES.get(contract, ()))
            or value['native_verification'] != 'requires-installation-specific-proof'):
        return 'unsupported'
    for rel, expected in value['source_files'].items():
        if (not isinstance(rel, str) or not isinstance(expected, str) or not re.fullmatch('[0-9a-f]{64}', expected)
                or Path(rel).is_absolute() or '..' in Path(rel).parts
                or not (rel.startswith('.systems/') or rel in {'AGENTS.md','README.md','HUMANS.md'})
                or rel == str(path.relative_to(root))):
            return 'unsupported'
        if hashlib.sha256(safe_bytes(root / rel)).hexdigest() != expected: return 'mismatch'
    return 'verified-source'


def resolve_context(cwd, tool='codex', workspace=None, *, environment=None, system_home=None):
    if tool not in {'codex', 'claude-code', 'generic'}:
        raise ContextError('unsupported executor')
    record, installed, regpath, env = registration(environment, system_home)
    current = concrete(cwd, environment=env)
    if not current.is_dir():
        raise ContextError('cwd must be an existing absolute directory')
    rows, registry = workspace_registry(installed, env)
    repo, common = common_git(current)
    matches, association_hashes = project_associations(rows, repo, common, env) if repo and repo != installed else ([], [])
    default = next(root for _, root, is_default in rows if is_default)
    selected = concrete(workspace, environment=env) if workspace else None
    environment_workspace = concrete(env['AI_SYSTEM_WORKSPACE_HOME'], environment=env) if env.get('AI_SYSTEM_WORKSPACE_HOME') else None
    if selected and selected not in {x[1] for x in rows}:
        raise ContextError('explicit workspace is not registered', 4)
    owner, project_id = (matches[0][0], matches[0][1]) if matches else (None, None)
    if owner and any(x is not None and x != owner for x in (selected, environment_workspace)):
        raise ContextError('repository ownership conflicts with workspace selection', 4)
    if owner:
        selected, kind = owner, 'worktree' if repo != matches[0][2] else 'repository'
    elif repo and repo != installed:
        selected, kind = None, 'unregistered-repository'
    else:
        selected = selected or environment_workspace or default
        if selected not in {x[1] for x in rows}:
            raise ContextError('environment workspace is not registered', 4)
        kind = 'management' if current == installed or current.is_relative_to(installed / '.systems') else 'personal'
    checkout = None
    if repo and (repo / 'ai-system.local.json').exists():
        role = strict_json(repo / 'ai-system.local.json')
        if (not isinstance(role, dict) or set(role) != {'schema_version', 'role'}
                or type(role['schema_version']) is not int or role['schema_version'] != 1
                or role['role'] not in {'management', 'development'}):
            raise ContextError('invalid checkout role')
        checkout = role['role']
    wf, wf_workspace, mode = workflow_context(repo, env, system_home=installed, shared_only=not owner) if repo else (None, None, None)
    hashes = [(str(path), hashlib.sha256(safe_bytes(path)).hexdigest()) for path in
              (regpath, registry, installed / 'ai-system.local.json', *(installed / x for x in POLICY))]
    hashes += association_hashes
    if mode == 'shared':
        config = installed / 'ai-workflow-workspace/shared-installation.json'
        hashes += [(str(config), hashlib.sha256(safe_bytes(config)).hexdigest()),
                   (str(wf), git(wf, 'rev-parse', 'HEAD'))]
    digest = hashlib.sha256(''.join(sorted(f'{a}={b}\n' for a,b in hashes)).encode()).hexdigest()
    read_roots = [str(installed / '.systems/ai/core')]
    if mode == 'shared':
        read_roots += [str(wf / '.systems/ai/core'), str(wf / 'AGENTS.md')]
    if owner:
        read_roots += [str(repo), str(matches[0][3])]
    elif selected:
        read_roots += [str(selected / 'status.md')]
    unresolved = [] if record['enabled'] else ['installation disabled']
    chain = instruction_chain(current, repo, env, tool)
    unresolved += chain.get('issues', [])
    system_source = source_consistency(installed, 'agent-startup-v1.json', 'agent-startup-v1')
    workflow_source = source_consistency(wf, 'work-lead-v1.json', 'work-lead-v1') if wf else 'absent'
    if system_source != 'verified-source':
        unresolved.append('System startup source is not verified')
    if wf and workflow_source != 'verified-source':
        unresolved.append('bound Workflow consumer source is not verified')
    return dict(schema_version=1, system_id=record['system_id'], system_home=str(installed),
                checkout_role=checkout, context_kind=kind, repository_root=str(repo) if repo else None,
                workspace_root=str(selected) if selected else None, project_id=project_id,
                workflow_home=str(wf) if wf else None, workflow_workspace=str(wf_workspace) if wf_workspace else None,
                workflow_mode=mode, binding_status='resolved' if not unresolved else 'unavailable',
                contract_version=1, source_digest=digest, capabilities={'context': 'descriptive',
                'workflow': mode, 'system_source': system_source, 'workflow_source': workflow_source,
                'executor_native_verification': 'unverified', 'memory_control': 'not-assessed'},
                instruction_chain=chain,
                read_roots=read_roots, requested_write_roots=[], unresolved=unresolved, authorization_assessed=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cwd', required=True)
    parser.add_argument('--tool', choices=('codex', 'claude-code', 'generic'), required=True)
    parser.add_argument('--workspace')
    parser.add_argument('--system-home', help='explicit installation selection; registration conflicts still reject')
    parser.add_argument('--format', choices=('json', 'human'), default='json')
    args = parser.parse_args()
    try:
        out = resolve_context(args.cwd, args.tool, args.workspace, system_home=args.system_home)
        print(json.dumps(out, indent=2) if args.format == 'json' else
              '\n'.join(f'{key}: {value}' for key, value in out.items()))
        return 0 if out['binding_status'] == 'resolved' else 3
    except (ContextError, OSError, ValueError, TypeError, subprocess.SubprocessError) as error:
        code = error.code if isinstance(error, ContextError) else 3
        print(json.dumps({'schema_version': 1, 'binding_status': 'conflict' if code == 4 else 'unavailable',
                          'unresolved': [str(error)], 'authorization_assessed': False}))
        return code


if __name__ == '__main__':
    raise SystemExit(main())
