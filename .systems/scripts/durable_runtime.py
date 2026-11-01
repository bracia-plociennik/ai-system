#!/usr/bin/env python3
"""Portable, descriptive runtime bindings for disposable task execution.

Bindings are local routing metadata, never owner consent or current QA.
"""
import argparse
import json
import os
import re
from pathlib import Path
import subprocess
import sys

VERSION = 1
BINDING_NAME = 'ai-workflow-runtime.json'
OS_TEMP_ROOTS = (Path('/tmp'), Path('/var/tmp'), Path('/var/folders'))


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True,
                                   stderr=subprocess.PIPE, env=dict(os.environ, GIT_OPTIONAL_LOCKS='0')).strip()


def unlinked(path, *, exists=True):
    path = Path(os.path.abspath(os.path.expanduser(str(path))))
    for parent in (path, *path.parents):
        if parent.is_symlink():
            raise ValueError('linked runtime path')
    if exists and not path.exists():
        raise ValueError('missing runtime path')
    return path


def temporary(path):
    path = Path(path)
    return bool({'.tmp', '.worktrees'} & set(path.parts))


def durable(path):
    path = unlinked(path)
    if not path.is_dir() or temporary(path) or any(path.is_relative_to(root) for root in
                                                 OS_TEMP_ROOTS):
        raise ValueError('durable runtime cannot be temporary execution storage')
    return path


def identity(repo):
    repo = unlinked(repo)
    if Path(git(repo, 'rev-parse', '--show-toplevel')) != repo:
        raise ValueError('source must be an exact repository root')
    common = unlinked(git(repo, 'rev-parse', '--path-format=absolute', '--git-common-dir'))
    return {'root': str(repo), 'git_common': str(common)}


def binding_path(target):
    return Path(git(target, 'rev-parse', '--path-format=absolute', '--git-path', BINDING_NAME))


def read_json(path):
    def unique(pairs):
        out = {}
        for k, v in pairs:
            if k in out:
                raise ValueError('duplicate JSON field')
            out[k] = v
        return out
    path = unlinked(path)
    if not path.is_file():
        raise ValueError('runtime input must be a regular file')
    return json.loads(path.read_text(), object_pairs_hook=unique)


def load(target):
    target = unlinked(target)
    try:
        path = binding_path(target)
    except subprocess.SubprocessError:
        return None
    if not path.exists() and not path.is_symlink():
        return None
    value = read_json(path)
    if set(value) != {'schema', 'source', 'canonical', 'workspace', 'work_record'} or type(value['schema']) is not int or value['schema'] != VERSION:
        raise ValueError('unsupported runtime binding')
    if value['source'] != identity(target) or value['canonical'] != identity(value['canonical']['root']):
        raise ValueError('runtime source identity changed')
    if value['source']['git_common'] != value['canonical']['git_common']:
        raise ValueError('runtime binding belongs to a different repository')
    workspace = durable(value['workspace'])
    record = read_json(value['work_record'])
    policy = record.get('task_resource_cleanup', {})
    if (type(policy.get('schema')) is not int or policy.get('schema') not in {1, 2} or policy.get('canonical') != value['canonical']
            or policy.get('workspace') != str(workspace)):
        raise ValueError('runtime work record does not match binding')
    if not Path(value['work_record']).is_relative_to(workspace):
        raise ValueError('work record is outside owning runtime')
    return value


def resolve(target, requested=None, *, require=False):
    value = load(target)
    if value:
        if requested:
            requested = Path(requested)
            if not requested.is_absolute():
                requested = Path(target) / requested
            if unlinked(requested) != Path(value['workspace']):
                raise ValueError('environment conflicts with persistent runtime binding')
        return Path(value['workspace'])
    if require or temporary(target):
        raise ValueError('temporary source needs an explicit durable runtime binding')
    return None


def bind(target, canonical, workspace, work_record, *, dry_run=False):
    target, canonical, workspace = unlinked(target), unlinked(canonical), durable(workspace)
    record = read_json(work_record)
    policy = record.get('task_resource_cleanup', {})
    if (type(policy.get('schema')) is not int or policy.get('schema') not in {1, 2} or policy.get('canonical') != identity(canonical)
            or policy.get('workspace') != str(workspace)):
        raise ValueError('initialize the existing owning work record before binding')
    if not unlinked(work_record).is_relative_to(workspace):
        raise ValueError('work record must stay in durable runtime')
    source, canon = identity(target), identity(canonical)
    if source['git_common'] != canon['git_common']:
        raise ValueError('different Git common identity')
    value = {'schema': 1, 'source': source, 'canonical': canon,
             'workspace': str(workspace), 'work_record': str(unlinked(work_record))}
    output = unlinked(binding_path(target), exists=False)
    if output.exists():
        if read_json(output) != value:
            raise ValueError('refusing to overwrite conflicting runtime binding')
        return value
    if dry_run:
        return value
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    return value


SHARED_CONFIGURATION = 'ai-workflow-workspace/shared-installation.json'


def _small_json(path):
    path = unlinked(path)
    if not path.is_file() or path.stat().st_size > 65536:
        raise ValueError('invalid shared installation input')
    return read_json(path)


def registered_system(environment=None):
    """Read user registration; a repository marker never selects an installation."""
    env = os.environ if environment is None else environment
    home = unlinked(env.get('HOME', str(Path.home())))
    path = home / '.config/ai-system/installation.json'
    if not path.exists() and not path.is_symlink():
        return None
    record = _small_json(path)
    keys = {'schema_version', 'system_id', 'system_home', 'enabled', 'adapter_ids',
            'owner_workspace_id', 'owner_asset_id'}
    if (not isinstance(record, dict) or set(record) != keys
            or type(record['schema_version']) is not int or record['schema_version'] != 1
            or type(record['enabled']) is not bool or not isinstance(record['system_home'], str)):
        raise ValueError('invalid user System registration')
    if not record['enabled']:
        raise ValueError('registered System is disabled')
    for key in ('system_id', 'owner_workspace_id', 'owner_asset_id'):
        if not isinstance(record[key], str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', record[key]):
            raise ValueError('invalid user registration identity')
    adapters = record['adapter_ids']
    if (not isinstance(adapters, list) or any(not isinstance(a, str) or a not in {'codex', 'claude-code', 'generic'} for a in adapters)
            or len(adapters) != len(set(adapters))):
        raise ValueError('invalid user registration adapter identities')
    value = record['system_home'].replace('${HOME}', str(home))
    if value.startswith('~/'):
        value = str(home / value[2:])
    if not value.startswith('/') or any(c in value for c in '$`\n\r\0') or '..' in Path(value).parts:
        raise ValueError('System registration needs an absolute concrete path')
    root = unlinked(value)
    if env.get('AI_SYSTEM_HOME') and unlinked(env['AI_SYSTEM_HOME']) != root:
        raise ValueError('System environment conflicts with user registration')
    role = _small_json(root / 'ai-system.local.json')
    if role != {'schema_version': 1, 'role': 'management'} or type(role.get('schema_version')) is not int:
        raise ValueError('shared installation requires the registered management System')
    return root


def shared_installation(system_root, target=None):
    """Inspect an owner-enabled routing default. This is never permission."""
    root = unlinked(system_root)
    if target is not None and not unlinked(target).is_relative_to(root):
        return None
    config = root / SHARED_CONFIGURATION
    if not config.exists() and not config.is_symlink():
        return None
    value = _small_json(config)
    if (not isinstance(value, dict) or set(value) != {'schema_version', 'enabled', 'workflow_home'}
            or type(value['schema_version']) is not int or value['schema_version'] != 1
            or type(value['enabled']) is not bool or value['workflow_home'] != 'ai-workflow'):
        raise ValueError('invalid shared Workflow configuration')
    if not value['enabled']:
        return None
    home = unlinked(root / value['workflow_home'])
    identity(home)
    git(home, 'rev-parse', 'HEAD')
    for rel in ('AGENTS.md', '.systems/scripts/resolve-workflow-env',
                '.systems/ai/core/repository-modes.md', '.systems/ai/core/risk-model.md'):
        if not unlinked(home / rel).is_file():
            raise ValueError('shared Workflow installation is incomplete')
    return home


def workflow_environment(home, *, mode=None, target=None, cwd=None, workspace=None,
                         system_root=None, environment=None):
    """Common shell/Python policy home, execution root and artifact resolution."""
    env = os.environ if environment is None else environment
    home = unlinked(home)
    mode = mode or env.get('AI_WORKFLOW_MODE', 'auto')
    if mode not in {'auto', 'official', 'target', 'shared'}:
        raise ValueError('invalid AI_WORKFLOW_MODE; allowed: auto, official, target, shared')
    root = None if mode == 'official' else (unlinked(system_root) if system_root else registered_system(env))
    shared = shared_installation(root) if root is not None and home.is_relative_to(root) else None
    if mode == 'auto':
        if shared == home:
            mode = 'shared'
        else:
            try:
                nested = home.name == 'ai-workflow' and identity(home.parent)['root'] == str(home.parent)
            except (OSError, ValueError, subprocess.SubprocessError):
                nested = False
            mode = 'target' if nested else 'official'
    if mode == 'shared':
        if shared is None or shared != home:
            raise ValueError('shared Workflow is not enabled at this installation')
        selected = target or env.get('AI_WORKFLOW_TARGET_ROOT') or env.get('TARGET_REPO_ROOT')
        execution = unlinked(selected) if selected else unlinked(git(unlinked(cwd or Path.cwd()), 'rev-parse', '--show-toplevel'))
        if selected and target is None and not env.get('AI_WORKFLOW_TARGET_ROOT'):
            current = unlinked(git(unlinked(cwd or Path.cwd()), 'rev-parse', '--show-toplevel'))
            if current not in {execution, home}:
                raise ValueError('inherited Workflow target conflicts with CWD; pass an explicit target')
        identity(execution)
        if not execution.is_relative_to(root) or execution == home or execution.is_relative_to(home):
            raise ValueError('shared target must be a project repository inside the registered System')
    else:
        execution = home.parent if mode == 'target' else home
        if target and unlinked(target) != execution:
            raise ValueError('explicit target does not match this Workflow installation mode')
        if mode == 'target' and shared is not None and execution.is_relative_to(root) and home != shared:
            raise ValueError('use the configured shared Workflow instead of this nested installation')
    requested = workspace if workspace is not None else env.get('AI_WORKFLOW_WORKSPACE_HOME')
    bound = resolve(execution, requested)
    artifact_root = bound or (Path(requested) if requested else execution / 'ai-workflow-workspace')
    if not artifact_root.is_absolute():
        artifact_root = execution / artifact_root
    artifact_root = unlinked(artifact_root, exists=False)
    if mode == 'shared' and bound is None and artifact_root != execution / 'ai-workflow-workspace':
        raise ValueError('shared project artifacts require the local workspace or a verified durable binding')
    values = dict(AI_WORKFLOW_MODE_RESOLVED=mode, AI_WORKFLOW_HOME=str(home),
                  TARGET_REPO_ROOT=str(execution), AI_WORKFLOW_WORKSPACE_HOME=str(artifact_root))
    if any(any(c in value for c in '\n\r\0') for value in values.values()):
        raise ValueError('Workflow paths cannot contain record separators')
    return values


def execution_target(source):
    """Mirror verified target-mode layout; the nested policy clone is not the code target."""
    source = unlinked(source)
    if ((os.environ.get('AI_WORKFLOW_MODE') == 'shared' or os.environ.get('AI_WORKFLOW_MODE_RESOLVED') == 'shared')
            and str(source) == os.environ.get('AI_WORKFLOW_HOME')):
        return Path(workflow_environment(source, mode='shared')['TARGET_REPO_ROOT'])
    if (os.environ.get('AI_WORKFLOW_MODE') != 'official' and source.name == 'ai-workflow'
            and (source / '.systems/scripts/resolve-workflow-env').is_file()
            and (source / '.systems/ai/core/repository-modes.md').is_file()):
        try:
            identity(source.parent)  # Exact parent Git root, never an ancestor guess.
            return source.parent
        except (ValueError, OSError, subprocess.SubprocessError):
            pass
    return source


def guard_output(output, *, target=None, workspace=None):
    """Enforce the new managed-task boundary; legacy standalone data stays readable."""
    output = unlinked(output, exists=False)
    if temporary(output):
        raise ValueError('QA/Capture/checkpoint evidence cannot be stored in task scratch/worktrees')
    if target is False:
        return  # Legacy generic publication has no selected execution source.
    if target is None:
        try:
            target = git(Path.cwd(), 'rev-parse', '--show-toplevel')
        except subprocess.SubprocessError:
            return
    target = execution_target(target)
    bound = resolve(target, workspace) if temporary(target) or load(target) else None
    if bound is not None and not output.is_relative_to(bound):
        raise ValueError('managed task evidence must use its bound durable runtime')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['resolve', 'bind', 'guard-output', 'workflow-env', 'shared-home'])
    p.add_argument('--target')
    p.add_argument('--workflow-home')
    p.add_argument('--mode', choices=['auto', 'official', 'target', 'shared'])
    p.add_argument('--cwd')
    p.add_argument('--system-root')
    p.add_argument('--lines', action='store_true')
    p.add_argument('--requested')
    p.add_argument('--canonical')
    p.add_argument('--workspace')
    p.add_argument('--work-record')
    p.add_argument('--output')
    p.add_argument('--approved', action='store_true')
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()
    try:
        if args.action == 'shared-home':
            system = unlinked(args.system_root) if args.system_root else registered_system()
            value = shared_installation(system, args.target) if system else None
            if value is not None:
                print(value)
        elif args.action == 'workflow-env':
            if not args.workflow_home:
                raise ValueError('workflow-env requires --workflow-home')
            value = workflow_environment(args.workflow_home, mode=args.mode, target=args.target,
                                         cwd=args.cwd, workspace=args.workspace, system_root=args.system_root)
            print('\n'.join(k + '=' + v for k, v in value.items()) if args.lines else json.dumps(value))
        elif not args.target:
            raise ValueError('target is required')
        elif args.action == 'bind':
            if (not args.approved and not args.dry_run) or not all((args.canonical, args.workspace, args.work_record)):
                raise ValueError('binding requires explicit approved target/canonical/workspace/work-record')
            if args.requested:
                requested = Path(args.requested)
                if not requested.is_absolute():
                    requested = Path(args.target) / requested
                if unlinked(requested) != unlinked(args.workspace):
                    raise ValueError('environment conflicts with selected durable runtime')
            print(json.dumps(bind(args.target, args.canonical, args.workspace, args.work_record, dry_run=args.dry_run)))
        elif args.action == 'guard-output':
            if not args.output:
                raise ValueError('output is required')
            guard_output(args.output, target=args.target, workspace=args.workspace)
        else:
            value = resolve(args.target, args.requested)
            if value:
                print(value)
        return 0
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print('Durable runtime: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
