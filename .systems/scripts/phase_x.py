#!/usr/bin/env python3
"""Read-only Phase X target selection; never runs commands stored in workspace data."""
import argparse
import json
import os
from pathlib import Path
import re
import sys


def directory(raw):
    path = Path(os.path.abspath(os.path.expanduser(str(raw))))
    for parent in (path, *path.parents):
        if parent.is_symlink():
            raise ValueError('linked maintenance target/registry is not supported')
    if not path.is_dir():
        raise ValueError('maintenance target is unavailable')
    if '.worktrees' in path.parts or '.tmp' in path.parts:
        raise ValueError('temporary execution storage is not a maintenance workspace')
    return path


def targets(workspace=None, all_workspaces=False, system_home=None, findings=None):
    if all_workspaces and workspace is not None:
        raise ValueError('choose one workspace or -all')
    if not all_workspaces:
        if workspace is None:
            raise ValueError('select one resolved owning workspace explicitly')
        return [str(directory(workspace))]
    if system_home is None:
        raise ValueError('-all requires the verified installation home')
    home = directory(system_home)
    registry = home/'ai-system-workspaces.md'
    if registry.is_symlink() or not registry.is_file():
        raise ValueError('missing/linked workspace registry')
    result, seen_ids = [], set()
    for line in registry.read_text().splitlines():
        cells = [v.strip().strip('`') for v in line.strip().strip('|').split('|')]
        if len(cells) != 6 or cells[3] not in {'active', 'paused', 'archived', 'planned'}:
            continue
        identity, raw, _, state, _, _ = cells
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', identity) or identity in seen_ids:
            raise ValueError('invalid/duplicate workspace registration')
        seen_ids.add(identity)
        if state == 'planned':
            if findings is not None:findings.append({'workspace_id':identity, 'state':'pending', 'reason':'planned; not enrolled or created'})
            continue
        # Expressions are data; support only the documented HOME and installation root.
        raw = raw.replace('${HOME}', str(Path.home())).replace('${AI_SYSTEM_HOME}', str(home))
        if '$' in raw or '..' in Path(raw).parts:
            raise ValueError('unsupported workspace path expression')
        try:
            path = directory(raw if Path(raw).is_absolute() else home/raw)
        except ValueError as error:
            if findings is None:raise
            findings.append({'workspace_id':identity, 'state':'blocked', 'reason':str(error)})
            continue
        if str(path) in result or any(path.is_relative_to(Path(p)) or Path(p).is_relative_to(path) for p in result):
            raise ValueError('overlapping or duplicate registered workspaces')
        result.append(str(path))
    if not result and findings is None:
        raise ValueError('no available registered workspaces')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path)
    parser.add_argument('-all', '--all', dest='all_workspaces', action='store_true')
    parser.add_argument('--system-home', type=Path)
    args = parser.parse_args()
    try:
        findings=[]
        selected=targets(args.workspace, args.all_workspaces, args.system_home, findings)
        print(json.dumps({'phase': 'X', 'name': 'Maintenance', 'workspaces': selected, 'findings':findings,
                          'manual_only': True, 'execution_authorized': False, 'authority': 'none'}, indent=2))
        return 2 if any(f['state']=='blocked' for f in findings) else 0
    except (ValueError, OSError) as exc:
        print('Phase X unavailable: '+str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
