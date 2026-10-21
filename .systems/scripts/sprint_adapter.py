#!/usr/bin/env python3
"""System delegates Sprint to the installed, source-verified Workflow owner."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import durable_runtime as runtime

FILES={'.systems/scripts/manage-sprint','.systems/scripts/sprint_iteration.py',
       '.systems/scripts/task_resource_cleanup.py','.systems/scripts/durable_runtime.py',
       '.systems/scripts/lib/qa-evidence.py','.systems/scripts/lib/quality-record.py',
       '.systems/scripts/lib/coordinator-status.py','.systems/ai/core/sprint-iteration.md'}


def support(root, require_default=False):
    root=runtime.unlinked(root)
    version = 2 if (root/'.systems/ai/capabilities/sprint-iteration-v2.json').exists() else 1
    if require_default and version != 2:raise ValueError('default Sprint requires compatible Workflow V2')
    expected_files = FILES | ({'.systems/scripts/sprint_v2.py', '.systems/ai/core/default-sprint.md'} if version == 2 else set())
    value=runtime.read_json(root/('.systems/ai/capabilities/sprint-iteration-v'+str(version)+'.json'))
    if (set(value)!={'schema','capability','contract_version','files','authority'}
        or type(value['schema']) is not int or value['schema']!=1
        or type(value['contract_version']) is not int or value['contract_version']!=version
        or value['capability']!='sprint-iteration-v'+str(version) or value['authority']!='none'
        or not isinstance(value['files'],dict) or set(value['files'])!=expected_files):raise ValueError('incompatible installed Workflow Sprint')
    for rel,expected in value['files'].items():
        path=runtime.unlinked(root/rel)
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
            raise ValueError('Workflow Sprint source changed: '+rel)
    return {'schema':1,'supported':True,'contract_version':version,'default_sprint':version==2,'authority':'none'}


def main():
    p=argparse.ArgumentParser(description=__doc__,add_help=False)
    p.add_argument('--workflow-root',type=Path);p.add_argument('--check-support',action='store_true')
    a,rest=p.parse_known_args()
    try:
        root=a.workflow_root
        if root is None:
            if '--record' not in rest:raise ValueError('select installed Workflow or existing owning --record')
            record=runtime.read_json(rest[rest.index('--record')+1])
            canonical=Path(record['task_resource_cleanup']['canonical']['root'])
            root=canonical if (canonical/'.systems/ai/core/repository-modes.md').is_file() else canonical/'ai-workflow'
        # New selection needs V2; V1 remains usable only for explicit legacy records/starts.
        legacy_record = False
        if '--record' in rest:
            owning = runtime.read_json(rest[rest.index('--record')+1])
            legacy_record = owning.get('sprint_iteration', {}).get('schema') == 1
        result=support(root, require_default=(not a.check_support and 'start' in rest and not ('--schema' in rest and rest[rest.index('--schema')+1]=='1')))
        if not a.check_support and result['contract_version']==1 and not legacy_record and 'start' not in rest:
            raise ValueError('V2 counterpart required for default Sprint')
        if a.check_support:print(json.dumps(result,sort_keys=True));return 0
        return subprocess.run([str(root/'.systems/scripts/manage-sprint'),*rest],check=False).returncode
    except (ValueError,OSError,KeyError,IndexError,TypeError,subprocess.SubprocessError) as exc:
        print('Sprint unavailable: '+str(exc),file=sys.stderr);return 2


if __name__=='__main__':raise SystemExit(main())
