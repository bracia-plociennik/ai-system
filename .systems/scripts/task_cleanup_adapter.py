#!/usr/bin/env python3
"""Delegate to the one installed Workflow executor; never duplicate deletion."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import durable_runtime as runtime

FILES = {
 '.systems/scripts/manage-task-resources', '.systems/scripts/task_resource_cleanup.py',
 '.systems/scripts/durable_runtime.py', '.systems/scripts/lib/task-resource-activity.py',
 '.systems/ai/core/task-resource-cleanup.md', '.systems/scripts/resolve-workflow-env',
 '.systems/scripts/bootstrap-target-worktree', '.systems/scripts/lib/quality-record.py',
 '.systems/scripts/lib/execution-efficiency.py', '.systems/scripts/lib/validation-timing.py',
 '.systems/scripts/init-workspace',
}


def support(root, require_sprint=False):
    root = runtime.unlinked(root)
    manifest = runtime.read_json(root / '.systems/ai/capabilities/task-resource-cleanup-v1.json')
    if (set(manifest) != {'schema','capability','contract_version','files','authority'}
            or type(manifest['schema']) is not int or manifest['schema'] != 1 or type(manifest['contract_version']) is not int or manifest['contract_version'] != 1
            or manifest['capability'] != 'task-resource-cleanup-v1' or manifest['authority'] != 'none'
            or not isinstance(manifest['files'],dict) or set(manifest['files']) not in (FILES, FILES | {'.systems/scripts/sprint_iteration.py'})):
        raise ValueError('unsupported installed Workflow cleanup capability')
    for relative, expected in manifest['files'].items():
        path = runtime.unlinked(root / relative)
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('installed Workflow cleanup source differs: ' + relative)
    has_sprint = '.systems/scripts/sprint_iteration.py' in manifest['files']
    if (require_sprint or b'import sprint_iteration' in (root/'.systems/scripts/task_resource_cleanup.py').read_bytes()) and not has_sprint:
        raise ValueError('Sprint-aware cleanup requires the complete Sprint guard dependency')
    return {'supported':True, 'contract_version':1, 'authority':'none'}


def main():
    p=argparse.ArgumentParser(description=__doc__,add_help=False)
    p.add_argument('--workflow-root',type=Path)
    p.add_argument('--check-support',action='store_true')
    args, rest=p.parse_known_args()
    try:
        root=args.workflow_root
        if root is None:
            if '--canonical' in rest:
                canonical=Path(rest[rest.index('--canonical')+1])
            elif '--record' in rest:
                record=runtime.read_json(rest[rest.index('--record')+1])
                canonical=Path(record['task_resource_cleanup']['canonical']['root'])
            else:
                raise ValueError('select installed --workflow-root, canonical repository or owning --record')
            root=canonical if (canonical/'.systems/ai/core/repository-modes.md').is_file() else canonical/'ai-workflow'
        require_sprint = False
        if '--record' in rest:
            value = runtime.read_json(rest[rest.index('--record')+1])
            require_sprint = 'sprint_iteration' in value
        result=support(root, require_sprint=require_sprint)
        if args.check_support:
            print(json.dumps(result,sort_keys=True));return 0
        return subprocess.run([str(root/'.systems/scripts/manage-task-resources'),*rest],check=False).returncode
    except (ValueError,OSError,KeyError,IndexError,TypeError,subprocess.SubprocessError) as exc:
        print('Task cleanup retained: '+str(exc),file=sys.stderr);return 2


if __name__=='__main__':
    raise SystemExit(main())
