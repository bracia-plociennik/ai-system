#!/usr/bin/env python3
"""Explicit local Codex component activation, with immutable sources and owned rollback."""
import argparse,fcntl,hashlib,json,os,shutil,stat,sys,tempfile
from pathlib import Path
HOOK='Luna-first: managed tasks use the luna-first skill; keep existing gates.\n'


def digest(b):return hashlib.sha256(b).hexdigest()


def path(raw,exists=False):
    p=Path(os.path.abspath(os.path.expanduser(str(raw))))
    if any(x.is_symlink() for x in (p,*p.parents)):raise ValueError('linked installation path')
    if exists and not p.exists():raise ValueError('missing installation path')
    return p


def load(p):return json.loads(path(p,True).read_text())


def store(p,v):
    p=path(p);p.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    fd,tmp=tempfile.mkstemp(prefix='.luna-',dir=p.parent)
    try:
        with os.fdopen(fd,'wb') as f:f.write(v if isinstance(v,bytes) else (json.dumps(v,indent=2)+'\n').encode());f.flush();os.fsync(f.fileno())
        os.chmod(tmp,stat.S_IMODE(p.stat().st_mode) if p.exists() else 0o600);os.replace(tmp,p)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)


def items(root):
    root=path(root,True);out={}
    for p in sorted(root.rglob('*')):
        path(p)
        if p.is_file():out[str(p.relative_to(root))]=digest(p.read_bytes())
    return out


def plan(source,user_home,instruction_files,owner_reference):
    source=path(source,True);home=path(user_home,True)
    if not owner_reference.strip():raise ValueError('actual owner reference required by caller')
    manifest=load(source/'manifest.json');inventory=items(source);inventory.pop('manifest.json',None)
    if manifest.get('schema')!=1 or manifest.get('files')!=inventory:raise ValueError('bundle source manifest mismatch')
    ident=digest(json.dumps(inventory,sort_keys=True).encode())[:24]
    base=home/'.config/ai-system/luna-first';destination=base/'releases'/ident
    reg=base/'active.json';agents=home/'.codex/AGENTS.md';old=agents.read_bytes() if agents.exists() else b''
    if HOOK.encode() in old or reg.exists():raise ValueError('existing activation; inspect/disable before replacing')
    new=old+(b'\n' if old and not old.endswith(b'\n') else b'')+HOOK.encode()
    instruction_hashes={}
    for raw in instruction_files:
        f=path(raw,True);b=f.read_bytes()
        if len(new)+len(b)>16384:raise ValueError('combined startup guidance exceeds16KiB: '+str(f))
        instruction_hashes[str(f)]=digest(b)
    if len(new)>16384 or not instruction_hashes:raise ValueError('known instruction-chain inventory required')
    owned={str(home/'.agents/skills/luna-first'):str(destination/'skill')}
    for name in ['luna-first-luna.toml','luna-first-sol.toml']:owned[str(home/'.codex/agents'/name)]=str(source/'profiles'/name)
    for raw in [str(reg),str(destination),*owned]:
        p=path(raw)
        if p.exists():raise ValueError('existing owned target; no overwrite: '+raw)
    return {'schema':1,'source':str(source),'source_files':inventory,'manifest_sha256':digest((source/'manifest.json').read_bytes()),'destination':str(destination),'user_home':str(home),'registration':str(reg),'agents_path':str(agents),'agents_before_sha256':digest(old),'agents_before':old.decode(),'agents_after':new.decode(),'instruction_files':instruction_hashes,'owned':owned,'owner_reference':owner_reference,'execution_authorized':False}


def apply(value,approved=False):
    if not approved:raise ValueError('actual scoped owner consent required; flag is not provenance')
    expected=plan(value['source'],value['user_home'],list(value['instruction_files']),value['owner_reference'])
    if value!=expected:raise ValueError('stale or altered install plan')
    reg=path(value['registration']);reg.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    lock=os.open(reg.parent/'install.lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
    try:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if plan(value['source'],value['user_home'],list(value['instruction_files']),value['owner_reference'])!=value:raise ValueError('install plan changed under lock')
        receipt=dict(value,status='pending',installed_files={},installed_profiles={})
        store(reg,receipt)
        dest=path(value['destination']);dest.parent.mkdir(parents=True,exist_ok=True,mode=0o700);shutil.copytree(value['source'],dest)
        receipt['installed_files']=items(dest)
        for raw,target in value['owned'].items():
            p=path(raw);p.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
            if p.suffix=='.toml':
                data=path(target,True).read_bytes();fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
                with os.fdopen(fd,'wb') as f:f.write(data)
                receipt['installed_profiles'][raw]=digest(data)
            else:p.symlink_to(dest/'skill',target_is_directory=True)
        store(reg,receipt)
        # Source and original global instructions checked again before the one owned hook.
        agents=path(value['agents_path'])
        if digest(agents.read_bytes() if agents.exists() else b'')!=value['agents_before_sha256']:raise ValueError('global instructions drifted; pending install retained')
        store(agents,value['agents_after'].encode());receipt['status']='active';store(reg,receipt)
        return inspect(value['user_home'])
    finally:os.close(lock)


def inspect(user_home):
    reg=path(user_home)/'.config/ai-system/luna-first/active.json'
    if not reg.exists():return {'active':False,'status':'not-installed','execution_authorized':False}
    r=load(reg);dest=path(r['destination'],True)
    ok=r['status']=='active' and items(dest)==r['installed_files'] and HOOK.encode() in path(r['agents_path'],True).read_bytes()
    for raw,h in r['installed_profiles'].items():ok=ok and path(raw,True).is_file() and digest(path(raw,True).read_bytes())==h
    link=Path(r['user_home'])/'.agents/skills/luna-first'
    ok=ok and link.is_symlink() and os.readlink(link)==str(dest/'skill')
    return {'active':bool(ok),'status':'active' if ok else 'incomplete-or-changed','component':str(dest),'owner_reference':r['owner_reference'],'root_chat_model_changed':False,'execution_authorized':False}


def disable(user_home,approved=False):
    if not approved:raise ValueError('explicit disable approval required')
    reg=path(user_home)/'.config/ai-system/luna-first/active.json';r=load(reg);agents=path(r['agents_path'],True);data=agents.read_bytes()
    if data.count(HOOK.encode())!=1:raise ValueError('owned hook changed; inspect manually')
    # Keep foreign instructions added after activation. No reset of owner/task records.
    store(agents,data.replace(HOOK.encode(),b'',1))
    link=Path(r['user_home'])/'.agents/skills/luna-first'
    if link.is_symlink() and os.readlink(link)==str(Path(r['destination'])/'skill'):link.unlink()
    r['status']='disabled';store(reg,r)
    return {'active':False,'status':'disabled','profiles_and_evidence_preserved':True,'execution_authorized':False}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('operation',choices=['plan','apply','inspect','disable']);p.add_argument('--source');p.add_argument('--user-home',default=str(Path.home()));p.add_argument('--instruction-file',action='append',default=[]);p.add_argument('--owner-reference',default='');p.add_argument('--plan');p.add_argument('--approved',action='store_true');a=p.parse_args()
    try:
        if a.operation=='plan':out=plan(a.source,a.user_home,a.instruction_file,a.owner_reference)
        elif a.operation=='apply':out=apply(load(a.plan),a.approved)
        elif a.operation=='inspect':out=inspect(a.user_home)
        else:out=disable(a.user_home,a.approved)
        print(json.dumps(out,indent=2));return 0
    except (ValueError,OSError,KeyError,TypeError) as exc:print('Luna-first activation unavailable: '+str(exc),file=sys.stderr);return 2


if __name__=='__main__':raise SystemExit(main())
