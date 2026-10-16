"""Shared bounded I/O policy. Standalone; never executes content or crawls globals."""
import hashlib
import json
import os
import re
import stat
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

class GuardError(ValueError):
    pass

def need(test, code):
    if not test: raise GuardError(code)

def hash_bytes(data): return hashlib.sha256(data).hexdigest()
def hash_object(data): return hash_bytes(json.dumps(data, ensure_ascii=False, sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def fields(value, keys): need(isinstance(value,dict) and set(value)==set(keys),"invalid-policy-shape")
def identity(value): need(isinstance(value,str) and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",value),"invalid-identity")
def rel(value,empty=False):
    need(isinstance(value,str) and (value or empty) and not value.startswith("/") and "\\" not in value and "\0" not in value and not re.match(r"[A-Za-z]:",value),"unsafe-path")
    need(value=="" or all(x not in {"",".",".."} for x in value.split("/")),"unsafe-path")

def registry(value):
    fields(value,{"schema_version","owner_workspace_id","authority_ref","profile","roots","limits","sharing"})
    need(type(value['schema_version']) is int and value['schema_version']==1,"unsupported-policy")
    identity(value['owner_workspace_id']);need(isinstance(value['authority_ref'],str) and value['authority_ref'],"missing-authority-reference")
    need(value['profile'] in ['narrow-only','work-materials'],"unknown-profile")
    fields(value['limits'],{'files','file_bytes','total_bytes','entries','chunk_bytes'})
    ceilings={'files':1000,'file_bytes':1048576,'total_bytes':67108864,'entries':10000,'chunk_bytes':16384}
    for key,limit in value['limits'].items():need(type(limit) is int and 0<limit<=ceilings[key],"unsafe-limit")
    fields(value['sharing'],{'recipient','mode','authority_ref'})
    need(value['sharing']['mode'] in ['none','counts-only','reviewed-text'],"invalid-sharing")
    need(value['sharing']['mode']=='none' or (isinstance(value['sharing']['recipient'],str) and value['sharing']['recipient'] and isinstance(value['sharing']['authority_ref'],str) and value['sharing']['authority_ref']),"missing-sharing-authority")
    need(isinstance(value['roots'],list) and value['roots'],"empty-roots")
    ids=set();locators=[]
    for root in value['roots']:
        fields(root,{'source_root_id','locator','kind','bindings'})
        identity(root['source_root_id']);need(root['source_root_id'] not in ids,"duplicate-root");ids.add(root['source_root_id'])
        need(root['kind'] in ['workspace','workflow','repository'],"invalid-root-kind")
        path=Path(root['locator']);need(path.is_absolute(),"missing-absolute-locator")
        # Reject links in all locator ancestors, even when the final target is missing.
        for part in [path,*path.parents]:need(not part.is_symlink(),"linked-root")
        for prior in locators:
            need(path!=prior,"aliased-root")
            if path.exists() and prior.exists():need(not os.path.samefile(path,prior),"aliased-root")
        locators.append(path)
        need(isinstance(root['bindings'],list) and root['bindings'],"missing-project-ownership")
        prefixes=[]
        for binding in root['bindings']:
            fields(binding,{'prefix','project_id','owner_workspace_id','source_class'})
            rel(binding['prefix'],True);identity(binding['project_id']);identity(binding['owner_workspace_id'])
            need(binding['source_class'] in ['work','source','personal-trends','secret','raw-personal','raw-export','attachment','unknown'],"unknown-class")
            prefix=binding['prefix']
            for prior in prefixes:need(not (prefix==prior or not prefix or not prior or prefix.startswith(prior+'/') or prior.startswith(prefix+'/')),"overlapping-project-ownership")
            prefixes.append(prefix)
    # Nested repositories are valid only with explicitly disjoint read scopes.
    scoped=[]
    for root in value['roots']:
        for binding in root['bindings']:
            path=Path(root['locator'])/binding['prefix']
            for other_id,prior in scoped:
                if other_id==root['source_root_id']:continue
                need(not (path==prior or path in prior.parents or prior in path.parents),'overlapping-read-scopes')
                if path.exists() and prior.exists():need(not os.path.samefile(path,prior),'aliased-read-scope')
            scoped.append((root['source_root_id'],path))
    return value

DENY_SEGMENTS={'.git','.venv','node_modules','vendor','dist','build','.cache','credentials','secrets','health','finance','financial','budget','calories','medical','.obsidian','dreams'}
SECRET=re.compile(rb'(?i)(?:-----BEGIN .*PRIVATE KEY|\b(?:api[_-]?key|password|secret|access[_-]?token)\s*[:=]|\b(?:sk-[a-z0-9_-]{12,}|gh[pousr]_[a-z0-9]{12,})|raw[- ]check[- ]in|sleep[_ -]hours\s*[:=]|calories\s*[:=])')
TEXT={'.md','.txt','.json','.jsonl'}
CODE={'.py','.js','.ts','.tsx','.jsx','.php','.css','.html','.sh','.yaml','.yml','.toml'}

def classification(policy,path,binding):
    parts=tuple(x.lower() for x in PurePosixPath(path).parts);name=parts[-1]
    if any(x in DENY_SEGMENTS for x in parts) or name=='.env' or name.startswith('.env.') or Path(name).suffix in {'.pem','.key','.p12','.pfx'}:return 'excluded','secret-or-private-path'
    if ('dump' in parts and 'incoming' in parts) or ('personal-ops' in parts and not name.endswith('.trends.md')) or any('ocr' in x or x.endswith('.assets') for x in parts):return 'excluded','raw-private-class'
    kind=binding['source_class']
    if kind not in {'work','source','personal-trends'}:return 'excluded','unapproved-class'
    if policy['profile']=='narrow-only' and kind in {'work','source'}:return 'excluded','narrow-profile'
    suffix=PurePosixPath(path).suffix.lower()
    if suffix not in TEXT and not (kind=='source' and suffix in CODE):return 'unsupported','unsupported-format'
    return 'pending','eligible'

def open_root(locator):
    # Resolve every ancestor with dirfds; no root replacement through a symlink.
    path=Path(locator);fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY)
    try:
        for part in path.parts[1:]:
            newer=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=newer
        return fd
    except BaseException:os.close(fd);raise

def read_file(locator,path,limit,*,prescreen=True):
    rel(path);directory=open_root(locator)
    try:
        for part in path.split('/')[:-1]:
            newer=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=directory);os.close(directory);directory=newer
        fd=os.open(path.split('/')[-1],os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=directory)
        try:
            before=os.fstat(fd);need(stat.S_ISREG(before.st_mode) and before.st_nlink==1,'unsafe-file-identity')
            need(before.st_size<=limit,'file-budget')
            data=b''
            while len(data)<=limit:
                chunk=os.read(fd,min(65536,limit+1-len(data)))
                if not chunk:break
                data+=chunk
            after=os.fstat(fd);current=os.stat(path.split('/')[-1],dir_fd=directory,follow_symlinks=False)
            need((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns) and (current.st_dev,current.st_ino)==(before.st_dev,before.st_ino),'source-race')
            # A held dirfd can still name a directory that has been replaced at
            # its registered locator. Reopen every ancestor without following
            # links and compare the current path before disclosing these bytes.
            fresh=open_root(locator)
            try:
                for part in path.split('/')[:-1]:
                    newer=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fresh);os.close(fresh);fresh=newer
                bound=os.stat(path.split('/')[-1],dir_fd=fresh,follow_symlinks=False)
                need((bound.st_dev,bound.st_ino,bound.st_size,bound.st_mtime_ns,bound.st_ctime_ns)==(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns),'source-race')
            finally:os.close(fresh)
            need(len(data)<=limit,'file-budget');need(not prescreen or not SECRET.search(data),'suspected-secret')
            try:data.decode('utf-8')
            except UnicodeDecodeError:raise GuardError('unsupported-encoding') from None
            return data
        finally:os.close(fd)
    finally:os.close(directory)

def inspect(value, *, read=False):
    registry(value);inventory=[];contents={};complete=True;entries=0;total=0;files=0
    for root in value['roots']:
        for binding in root['bindings']:
            if binding['owner_workspace_id']!=value['owner_workspace_id']:continue
            prefix=binding['prefix'];start=Path(root['locator'])/prefix
            todo=[start]
            while todo:
                path=todo.pop();entries+=1
                if entries>value['limits']['entries']:complete=False;todo=[];break
                relative=path.relative_to(root['locator']).as_posix();relative='' if relative=='.' else relative
                row={'source_root_id':root['source_root_id'],'relative_path':relative or prefix or 'root-unavailable','project_id':binding['project_id'],'disposition':'pending','reason_code':'eligible','source_ref':None,'read_receipt':None,'analysis_receipt':None}
                try:
                    # Metadata-only traversal does not follow links or inspect denied subtrees.
                    info=path.lstat()
                    if stat.S_ISLNK(info.st_mode):row.update(disposition='blocked',reason_code='linked-source');inventory.append(row);continue
                    if stat.S_ISDIR(info.st_mode):
                        parts=tuple(x.lower() for x in Path(relative).parts)
                        if relative and (any(x in DENY_SEGMENTS for x in parts) or ('dump' in parts and 'incoming' in parts) or ('personal-ops' in parts and 'indexes' not in parts)):
                            row.update(disposition='excluded',reason_code='private-directory');inventory.append(row);continue
                        # Ensure all parents still point to real directories before metadata enumeration.
                        fd=open_root(str(path))
                        try:
                            names=[]
                            with os.scandir(fd) as children:
                                for child in children:
                                    if len(names)+entries>=value['limits']['entries']:
                                        complete=False;break
                                    names.append(child.name)
                            names.sort()
                        finally:os.close(fd)
                        todo.extend(path/x for x in reversed(names));continue
                    disposition,reason=classification(value,relative,binding)
                    row.update(disposition=disposition,reason_code=reason)
                    if disposition=='pending':
                        if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1:row.update(disposition='blocked',reason_code='unsafe-file-identity')
                        elif info.st_size>value['limits']['file_bytes']:row.update(disposition='unsupported',reason_code='file-budget')
                        elif files>=value['limits']['files'] or total+info.st_size>value['limits']['total_bytes']:row.update(reason_code='run-budget');complete=False
                        elif read:
                            data=read_file(root['locator'],relative,value['limits']['file_bytes']);total+=len(data);files+=1
                            ref=dict(source_root_id=root['source_root_id'],relative_path=relative,project_id=binding['project_id'],owner_workspace_id=value['owner_workspace_id'],sha256=hash_bytes(data),byte_count=len(data),observed_at=datetime.now(timezone.utc).isoformat(),fact_date='unknown',evidence_level='observed',source_class=binding['source_class'])
                            row['source_ref']=ref;row['read_receipt']={'source_hash':ref['sha256'],'byte_count':len(data),'policy_digest':hash_object(value),'coverage':'complete'}
                            contents[(root['source_root_id'],relative)]=data
                except FileNotFoundError:row.update(disposition='missing',reason_code='missing-source')
                except (OSError,GuardError) as error:row.update(disposition='blocked',reason_code=str(error) if isinstance(error,GuardError) else 'unavailable-source')
                inventory.append(row)
    return {'inventory':inventory,'enumeration_complete':complete,'policy_digest':hash_object(value)},contents
