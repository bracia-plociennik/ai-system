#!/usr/bin/env python3
"""Delegate to the one installed Workflow executor; never duplicate deletion."""
import argparse
import hashlib
import json
import os
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
CACHE_PROFILE = 'next-webpack-cache-v1'
CACHE_FILES = {'.systems/scripts/task_resource_cleanup.py', '.systems/scripts/durable_runtime.py',
               '.systems/scripts/manage-task-resources', '.systems/scripts/lib/task-resource-activity.py',
               '.systems/scripts/tests/task-resource-cleanup.py', '.systems/ai/core/task-resource-cleanup.md'}


def select_workflow(canonical):
    canonical = runtime.unlinked(canonical)
    official = (canonical / '.systems/ai/core/repository-modes.md').is_file()
    if official and os.environ.get('AI_WORKFLOW_MODE') == 'official':
        return canonical
    system = runtime.registered_system()
    shared = runtime.shared_installation(system, canonical) if system is not None else None
    return shared if shared is not None else canonical if official else canonical / 'ai-workflow'


def support(root, require_sprint=False, require_cache=False):
    root = runtime.unlinked(root)
    manifest = runtime.read_json(root / '.systems/ai/capabilities/task-resource-cleanup-v1.json')
    if (set(manifest) != {'schema','capability','contract_version','files','authority'}
            or type(manifest['schema']) is not int or manifest['schema'] != 1 or type(manifest['contract_version']) is not int or manifest['contract_version'] != 1
            or manifest['capability'] != 'task-resource-cleanup-v1' or manifest['authority'] != 'none'
            or not isinstance(manifest['files'],dict) or set(manifest['files']) not in (FILES, FILES | {'.systems/scripts/sprint_iteration.py'}, FILES | {'.systems/scripts/sprint_iteration.py', '.systems/scripts/sprint_v2.py', '.systems/ai/core/default-sprint.md'})):
        raise ValueError('unsupported installed Workflow cleanup capability')
    for relative, expected in manifest['files'].items():
        path = runtime.unlinked(root / relative)
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('installed Workflow cleanup source differs: ' + relative)
    has_sprint = '.systems/scripts/sprint_iteration.py' in manifest['files']
    if (require_sprint or b'import sprint_iteration' in (root/'.systems/scripts/task_resource_cleanup.py').read_bytes()) and not has_sprint:
        raise ValueError('Sprint-aware cleanup requires the complete Sprint guard dependency')
    if '.systems/scripts/sprint_v2.py' in manifest['files']:
        import sprint_adapter
        sprint_adapter.support(root, require_default=True)
    result = {'supported':True, 'contract_version':1, 'authority':'none'}
    if require_cache:
        cache = runtime.read_json(root / '.systems/ai/capabilities/next-webpack-cache-v1.json')
        if (set(cache) != {'schema', 'capability', 'contract_version', 'files', 'authority'}
                or type(cache['schema']) is not int or cache['schema'] != 1
                or type(cache['contract_version']) is not int or cache['contract_version'] != 1
                or cache['capability'] != CACHE_PROFILE or cache['authority'] != 'none'
                or not isinstance(cache['files'], dict) or set(cache['files']) != CACHE_FILES):
            raise ValueError('unsupported installed webpack cache capability')
        for relative, expected in cache['files'].items():
            if hashlib.sha256(runtime.unlinked(root / relative).read_bytes()).hexdigest() != expected:
                raise ValueError('installed webpack cache source differs: ' + relative)
        result['cache_profile'] = CACHE_PROFILE
    return result


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
            root=select_workflow(canonical)
        require_sprint = False
        require_cache = False
        if '--profile' in rest:
            if rest[rest.index('--profile')+1] != CACHE_PROFILE:
                raise ValueError('unsupported cache profile request')
            require_cache = True
        if '--record' in rest:
            value = runtime.read_json(rest[rest.index('--record')+1])
            if not isinstance(value, dict) or not isinstance(value.get('task_resource_cleanup', {}), dict):
                raise ValueError('invalid owning resource policy')
            require_sprint = 'sprint_iteration' in value
            require_cache = require_cache or value.get('task_resource_cleanup', {}).get('schema') == 2
        result=support(root, require_sprint=require_sprint, require_cache=require_cache)
        if args.check_support:
            print(json.dumps(result,sort_keys=True));return 0
        return subprocess.run([str(root/'.systems/scripts/manage-task-resources'),*rest],check=False).returncode
    except (ValueError,OSError,KeyError,IndexError,TypeError,subprocess.SubprocessError) as exc:
        print('Task cleanup retained: '+str(exc),file=sys.stderr);return 2


if __name__=='__main__':
    raise SystemExit(main())
