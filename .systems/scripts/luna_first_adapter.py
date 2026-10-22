#!/usr/bin/env python3
"""Use the explicitly selected source-verified Workflow model-routing consumer."""
import argparse,hashlib,json,os
from pathlib import Path
import subprocess,sys
FILES={'.systems/scripts/luna_first.py','.systems/scripts/manage-luna-first','.systems/ai/core/luna-first.md'}

def safe(path):
    p=Path(os.path.abspath(os.path.expanduser(str(path))))
    if any(x.is_symlink() for x in (p,*p.parents)):raise ValueError('linked consumer path')
    return p


def support(root):
    root=safe(root);p=root/'.systems/ai/capabilities/luna-first-v1.json'
    value=json.loads(p.read_text())
    if set(value)!={'schema','capability','contract_version','authority','files'} or type(value['schema']) is not int or value['schema']!=1 or value['capability']!='luna-first-v1' or value['contract_version']!=1 or value['authority']!='none' or set(value['files'])!=FILES:raise ValueError('incompatible model-routing consumer')
    for rel,h in value['files'].items():
        f=safe(root/rel)
        if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest()!=h:raise ValueError('changed model-routing consumer: '+rel)
    return {'schema':1,'supported':True,'capability':'luna-first-v1','execution_authorized':False}


def main():
    p=argparse.ArgumentParser(description=__doc__,add_help=False);p.add_argument('--workflow-root',required=True);p.add_argument('--check-support',action='store_true');a,rest=p.parse_known_args()
    try:
        result=support(a.workflow_root)
        if a.check_support:print(json.dumps(result));return 0
        return subprocess.run([sys.executable,'-B',str(safe(a.workflow_root)/'.systems/scripts/luna_first.py'),*rest],check=False).returncode
    except (ValueError,OSError,KeyError,TypeError) as exc:print('Luna-first unavailable: '+str(exc),file=sys.stderr);return 2


if __name__=='__main__':raise SystemExit(main())
