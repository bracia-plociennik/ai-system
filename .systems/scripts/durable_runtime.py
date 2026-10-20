#!/usr/bin/env python3
"""Portable, descriptive runtime bindings for disposable task execution.

Bindings are local routing metadata, never owner consent or current QA.
"""
import argparse
import json
import os
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
    if (policy.get('schema') != 1 or policy.get('canonical') != value['canonical']
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
    if (policy.get('schema') != 1 or policy.get('canonical') != identity(canonical)
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


def execution_target(source):
    """Mirror verified target-mode layout; the nested policy clone is not the code target."""
    source = unlinked(source)
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
    p.add_argument('action', choices=['resolve', 'bind', 'guard-output'])
    p.add_argument('--target', required=True)
    p.add_argument('--requested')
    p.add_argument('--canonical')
    p.add_argument('--workspace')
    p.add_argument('--work-record')
    p.add_argument('--output')
    p.add_argument('--approved', action='store_true')
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()
    try:
        if args.action == 'bind':
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
