"""Explicit local Markdown task stores. UI availability never grants task authority."""
from __future__ import annotations
import hashlib
import tempfile
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import re
import stat
import uuid
from local_paths import resolve_path
from task_identity import new_identity

PROFILES = {'tasknotes-v1', 'silverbullet-v1'}
CATEGORIES = {'do': ('open','high'), 'defer': ('planned','normal'),
              'delegate': ('waiting','normal'), 'delete': ('cancelled','none'),
              'dump': ('open','none')}
MAX_TASK = 1024 * 1024
PLAN_ID = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')


def validate_plan(value):
    if not isinstance(value,dict) or set(value)!={'id','stages'} or not isinstance(value['id'],str) or not PLAN_ID.fullmatch(value['id']):
        raise ValueError('invalid-plan-identity')
    steps=value['stages']
    if not isinstance(steps,list) or len(steps)<2:raise ValueError('plan-requires-start-and-finish')
    ids=[]
    for step in steps:
        if (not isinstance(step,dict) or set(step)!={'id','text'} or not isinstance(step['id'],str)
                or not PLAN_ID.fullmatch(step['id']) or not isinstance(step['text'],str)
                or not step['text'].strip() or any(ord(c)<32 or c in '\x85\u2028\u2029' for c in step['text']) or '<!--' in step['text']):
            raise ValueError('invalid-plan-stage')
        ids.append(step['id'])
    if ids[0]!='start' or ids[-1]!='finish' or len(set(ids))!=len(ids):
        raise ValueError('plan-requires-unique-stages-start-first-finish-last')
    if len(json.dumps(value,ensure_ascii=False).encode())>MAX_TASK:raise ValueError('plan-exceeds-size-bound')
    return value


def plan_block(plan):
    validate_plan(plan);pid=plan['id']
    return (f'<!-- ai-system-plan:{pid}:start -->\n'+
            ''.join(f'- [ ] {s["text"]} <!-- ai-system-plan-step:{pid}:{s["id"]} -->\n' for s in plan['stages'])+
            f'<!-- ai-system-plan:{pid}:end -->\n')


def merge_plan(text,plan):
    """Splice only the canonical TODO. Raw dump and user stage lines are opaque."""
    validate_plan(plan)
    dump=re.search(r'^## Working dump[ \t]*\r?$',text,re.M)
    active=text if dump is None else text[:dump.start()]
    headings=list(re.finditer(r'^## TODO[ \t]*\r?$',active,re.M))
    if len(headings)!=1:raise ValueError('ambiguous-or-missing-todo-section')
    start=headings[0].end()
    following=re.search(r'^## ',active[start:],re.M)
    end=start+following.start() if following else len(active)
    body=text[start:end];pid=plan['id']
    opening=f'<!-- ai-system-plan:{pid}:start -->';closing=f'<!-- ai-system-plan:{pid}:end -->'
    if opening not in body and closing not in body:
        if f'ai-system-plan-step:{pid}:' in body:raise ValueError('orphan-plan-stage')
        return text[:end].rstrip('\n')+'\n\n'+plan_block(plan)+'\n'+text[end:]
    if body.count(opening)!=1 or body.count(closing)!=1:raise ValueError('ambiguous-plan-markers')
    left=body.index(opening);right=body.index(closing)
    if right<left:raise ValueError('invalid-plan-marker-order')
    block=body[left+len(opening):right]
    lines=block.splitlines(keepends=True);ids=[];finish=None
    pattern=re.compile(r'^- \[[ xX]\] .+ <!-- ai-system-plan-step:'+re.escape(pid)+r':([a-z0-9]+(?:-[a-z0-9]+)*) -->\r?\n?$')
    for i,line in enumerate(lines):
        match=pattern.fullmatch(line)
        if match:
            sid=match[1];ids.append(sid)
            if sid=='finish':finish=i
        elif 'ai-system-plan' in line or re.match(r'^\s*- \[[ xX]\]',line):
            raise ValueError('ambiguous-managed-plan-stage')
    if not ids or ids[0]!='start' or ids[-1]!='finish' or len(set(ids))!=len(ids):raise ValueError('invalid-managed-plan-stages')
    missing=[s for s in plan['stages'] if s['id'] not in ids]
    if not missing:return text
    # Extending a completed plan requires explicit reopening; never invent completion.
    if re.match(r'^- \[[xX]\]',lines[finish]):raise ValueError('completed-plan-needs-explicit-reopening')
    extra=''.join(f'- [ ] {s["text"]} <!-- ai-system-plan-step:{pid}:{s["id"]} -->\n' for s in missing)
    lines.insert(finish,extra)
    updated=body[:left+len(opening)]+''.join(lines)+body[right:]
    return text[:start]+updated+text[end:]


def read_task_fd(parent,name):
    fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent)
    with os.fdopen(fd,'rb') as stream:
        before=os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or before.st_size>MAX_TASK:raise ValueError('unsupported-task-file')
        raw=stream.read(MAX_TASK+1);after=os.fstat(stream.fileno())
        if (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns):
            raise ValueError('task-changed-during-read')
        return raw,before


def frontmatter(text):
    """Read flat scalar metadata only; bodies and nested YAML are not instructions."""
    match = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)',text,re.S)
    if not match: return {}
    result = {}
    for line in match[1].splitlines():
        found = re.match(r'^([A-Za-z_][A-Za-z_0-9-]*):[ \t]*(.*)$',line)
        if not found: continue
        key,value = found.groups()
        if key in result: raise ValueError('duplicate-task-metadata-field')
        if value.startswith('"') or value.startswith('['):
            try: value=json.loads(value)
            except (ValueError,TypeError): value=value.strip('"')
        elif value.startswith("'") and value.endswith("'"): value=value[1:-1].replace("''", "'")
        result[key]=value
    return result


def config_path(workspace):
    workspace=Path(workspace)
    current=workspace/'tasks/task-store.local.md'
    return current if current.exists() or current.is_symlink() else workspace/'tasks/taskforge-vault.local.md'


def identity(values):
    for kind,fields in [('plan',('source_plan_id',)),('weekly',('source_week_id','source_week_item_id')),
                        ('check-in',('source_session_date','source_plan_item_id')),
                        ('dream',('source_dream_report','source_candidate_id'))]:
        parts=tuple(str(values.get(k) or '') for k in fields)
        if all(parts):return (kind,*parts)
    return None


def segment(value, fallback):
    value=str(value or '').strip()
    value=re.sub(r'[\\/#@\[\]\x00-\x1f:?*<>"|]','-',value)
    # Match the UI's UTF-16 segment limit, including non-BMP input.
    value=value.strip('.').encode('utf-16-le')[:280].decode('utf-16-le',errors='ignore').strip()
    return value or fallback


def safe_path(root,path):
    root=Path(root);path=Path(path)
    if not path.is_relative_to(root) or any(p.is_symlink() for p in (path,*path.parents)):
        raise ValueError('unsafe-task-path')
    return path


class TaskStore:
    def __init__(self, root, profile='tasknotes-v1'):
        if profile not in PROFILES: raise ValueError('unsupported-task-store-profile')
        self.root=resolve_path(root)
        self.profile=profile
        self.task_dir=safe_path(self.root,self.root/('tasks' if profile=='silverbullet-v1' else 'TaskNotes/Tasks'))
        if not self.root.is_dir() or not self.task_dir.is_dir(): raise ValueError('task-store-directory-missing')

    @classmethod
    def load(cls,workspace,config=None,vault=None):
        workspace=Path(workspace);config=Path(config) if config else config_path(workspace)
        # Explicit vault retains the selected profile; absent configuration is legacy compatibility.
        values={}
        if config.exists():
            resolve_path(config)
            values=frontmatter(config.read_text(encoding='utf-8'))
            if str(values.get('enabled','')).lower() not in {'true','yes'}:raise ValueError('task-store-disabled')
        elif vault is None:raise ValueError('task-store-config-missing')
        elif config.name=='task-store.local.md':raise ValueError('task-store-config-missing')
        profile=values.get('profile','tasknotes-v1')
        if config.name=='task-store.local.md' and values.get('schema_version')!='1':
            raise ValueError('unsupported-task-store-config-version')
        root=vault if vault is not None else values.get('vault_path','')
        if not root:raise ValueError('task-store-root-missing')
        return cls(resolve_path(root,workspace=workspace,base=workspace,allow_relative=True),profile)

    def tasks(self):
        for directory,dirs,files in os.walk(self.task_dir,followlinks=False):
            dirs.sort();files.sort()
            for name in list(dirs):
                safe_path(self.task_dir,Path(directory)/name)
                if name.startswith('.') or name.endswith('.assets') or name in {'attachments','node_modules'}:dirs.remove(name)
            for name in files:
                if name.startswith('.') or not name.endswith('.md'):continue
                path=safe_path(self.task_dir,Path(directory)/name)
                if not path.is_file() or path.stat().st_size>MAX_TASK:raise ValueError('unsupported-task-file')
                values=frontmatter(path.read_text(encoding='utf-8'))
                if self.profile=='silverbullet-v1' and values.get('type')!='task':continue
                yield path,values

    def completed(self):
        """Explicit read-only DONE contract. Never create identity or infer time."""
        rows = list(self.tasks())
        scalar = lambda value: value if isinstance(value, str) and value else None
        counts = {}
        for _, meta in rows:
            identity = scalar(meta.get('task_id'))
            if identity:
                counts[identity] = counts.get(identity, 0) + 1
        result = []
        for path, meta in rows:
            if str(meta.get('status', '')).lower() != 'done':
                continue
            identity = scalar(meta.get('task_id'))
            try:
                valid = bool(identity) and str(uuid.UUID(identity)) == identity
            except (ValueError, TypeError, AttributeError):
                valid = False
            conflicted = (counts.get(identity, 0) > 1 or '.conflicted-' in path.name or
                          bool(list(path.parent.glob(path.stem + '.conflicted-*.md'))))
            state = 'conflict' if conflicted else 'ready' if valid else 'missing-or-invalid'
            result.append({'task_id': identity, 'task_ref': 'silverbullet:' + identity if valid else None,
                'source_path': path.relative_to(self.root).as_posix(), 'identity_status': state,
                'title': meta.get('title') or path.stem, 'status': 'done',
                'author': scalar(meta.get('author')) if scalar(meta.get('author')) in {'human', 'ai'} else None,
                'category': scalar(meta.get('category')), 'client': scalar(meta.get('client')),
                'project': scalar(meta.get('project')), 'scheduled': scalar(meta.get('scheduled')),
                'created_at': scalar(meta.get('created_at')), 'completed_at': scalar(meta.get('completed_at')),
                'completed_at_basis': scalar(meta.get('completed_at_basis')),
                'wep_approval_status': 'not_checked'})
        result.sort(key=lambda item: (item['completed_at'] or '', item['source_path']), reverse=True)
        return {'schema_version': 1, 'status_filter': 'done', 'writes': False, 'tasks': result,
                'identity_conflicts': sum(item['identity_status'] == 'conflict' for item in result)}

    def candidate(self,value):
        """Project an existing source candidate into the selected app's field contract."""
        result=dict(value)
        if self.profile!='silverbullet-v1':return result
        if 'plan' in result:
            validate_plan(result['plan'])
            result['source_plan_id']=result['plan']['id']
        bucket=str(result.get('category') or result.get('execution_bucket') or 'do').lower()
        if bucket=='done':raise ValueError('done-is-status-requires-real-category')
        if bucket not in CATEGORIES and bucket!='daily':raise ValueError('unsupported-task-category')
        title=str(result.get('title') or '').strip()
        if not title or len(title)>180 or '\n' in title or '\r' in title:raise ValueError('invalid-task-title')
        source_deadline=str(result.get('due') or result.get('source_deadline') or '')
        date=str(result.get('scheduled') or source_deadline or '')
        if date:
            # Source generators validate deadlines; preserve timestamp separately before day projection.
            try:
                if len(date)>10:dt.datetime.fromisoformat(date.replace('Z','+00:00'))
                else:dt.date.fromisoformat(date)
            except ValueError:raise ValueError('invalid-task-scheduled') from None
            date=date[:10]
        if bucket=='daily':
            if not date:raise ValueError('daily-task-requires-scheduled')
            bucket='do' # Daily is derived from the explicit date, never stored as a new category.
        status=result.get('status') or CATEGORIES[bucket][0]
        if not isinstance(status,str) or not re.fullmatch(r'[A-Za-z_-]+',status):raise ValueError('invalid-task-status')
        for field in ('tags','contexts','projects','due','task_method'):result.pop(field,None)
        result.update(type='task',title=title,category=bucket,scheduled=date,client=str(result.get('client') or ''),
                      project=str(result.get('project') or ''),status=status.lower(),priority=CATEGORIES[bucket][1])
        if source_deadline:
            try:
                if len(source_deadline)>10: dt.datetime.fromisoformat(source_deadline.replace('Z','+00:00'))
                else: dt.date.fromisoformat(source_deadline)
            except ValueError: raise ValueError('invalid-task-source-deadline') from None
            result['source_deadline']=source_deadline
        if result.get('source_dream_report') and not result.get('source_candidate_id'):
            result['source_candidate_id']=hashlib.sha256((str(result['source_dream_report'])+'\0'+title).encode()).hexdigest()
        result['task_method']='silverbullet-v1'
        return result

    def render(self,value):
        value=self.candidate(value)
        value['author']='ai'  # This writer creates tasks on behalf of AI; edits never use it.
        primary=['type','title','author','status','priority','client','project','category','scheduled']
        provenance=['workspace','owner_scope','owned_asset','project_state','source_system','source_type',
                    'source_check_in_date','source_check_in_field','source_session_date','source_plan_item_id',
                    'source_week_id','source_week_item_id','source_week_plan','estimated_minutes','weekly_allocations_json',
                    'source_dream_report','candidate_key','source_candidate_id','source_deadline',
                    'task_id','created_at','completed_at','reopened_at','source_plan_id']
        lines=['---']+[key+': '+json.dumps(value.get(key,''),ensure_ascii=False) for key in primary]
        lines += [key+': '+json.dumps(value[key],ensure_ascii=False) for key in provenance if key in value]
        dod=str(value.get('definition_of_done') or '').replace('\r','').replace('\n','\n  ')
        lines += ['---','# '+value['title'],'- Category: '+value['category'],'- DoD: '+dod,
                  '- Deadline: '+value['scheduled'],'','## Checkpoint OSNR','- O — Outcome:',
                  '- S — Status:','- N — Next:','- R — Resume:','','## TODO',plan_block(value['plan']).rstrip('\n') if 'plan' in value else '- [ ] '+value['title'],
                  '','## Evidence','','## Working dump','']
        return '\n'.join(lines)

    def write_plan(self,task_id,plan,expected_sha256,*,apply=False):
        """Exact task selection, read-only preview by default; cooperative guarded save."""
        validate_plan(plan)
        return self._write_todo(task_id, expected_sha256, lambda text: merge_plan(text, plan),
                                {'plan_id': plan['id']}, apply=apply)

    def write_idea(self, task_id, idea, expected_sha256, *, apply=False):
        from task_ideas import merge_idea
        if not isinstance(idea, dict):
            raise ValueError('idea input must be an object')
        return self._write_todo(task_id, expected_sha256, lambda text: merge_idea(text, idea),
                                {'idea_id': idea.get('id')}, apply=apply)

    def _write_todo(self, task_id, expected_sha256, transform, identity, *, apply=False):
        if self.profile != 'silverbullet-v1':
            raise ValueError('silverbullet-writer-profile-required')
        if not isinstance(task_id, str) or str(uuid.UUID(task_id)) != task_id:
            raise ValueError('invalid-task-id')
        if not isinstance(expected_sha256,str) or not re.fullmatch(r'[0-9a-f]{64}',expected_sha256):raise ValueError('expected-task-hash-required')
        matches=[p for p,m in self.tasks() if m.get('task_id')==task_id]
        if len(matches)!=1:raise ValueError('missing-or-ambiguous-task-identity')
        path=safe_path(self.task_dir,matches[0])
        fd=os.open(self.task_dir,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:
            for name in path.parent.relative_to(self.task_dir).parts:
                child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=child
            raw,info=read_task_fd(fd,path.name)
            if hashlib.sha256(raw).hexdigest()!=expected_sha256:raise ValueError('task-version-conflict')
            if frontmatter(raw.decode()).get('task_id')!=task_id:raise ValueError('task-identity-conflict')
            proposed=transform(raw.decode()).encode()
            if len(proposed)>MAX_TASK:raise ValueError('task-exceeds-size-bound')
            result={'task_id':task_id,**identity,'path':str(path),'changed':proposed!=raw,
                    'before_sha256':expected_sha256,'after_sha256':hashlib.sha256(proposed).hexdigest(),
                    'writes':False,'authority':'none'}
            if not apply or proposed==raw:return result
            lock=safe_path(self.root,self.root/'.ai-system-task-store.lock')
            with os.fdopen(os.open(lock,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600),'r+') as stream:
                fcntl.flock(stream,fcntl.LOCK_EX)
                latest,current=read_task_fd(fd,path.name)
                if latest!=raw or (current.st_dev,current.st_ino)!=(info.st_dev,info.st_ino):raise ValueError('task-version-conflict')
                temp='.ai-system-plan-'+uuid.uuid4().hex
                try:
                    out=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,stat.S_IMODE(info.st_mode),dir_fd=fd)
                    with os.fdopen(out,'wb') as output:
                        os.fchmod(output.fileno(),stat.S_IMODE(info.st_mode));output.write(proposed);output.flush();os.fsync(output.fileno())
                    safe_path(self.task_dir,path)
                    parent=path.parent.stat()
                    if (parent.st_dev,parent.st_ino)!=(os.fstat(fd).st_dev,os.fstat(fd).st_ino):raise ValueError('task-parent-conflict')
                    latest,current=read_task_fd(fd,path.name)
                    if latest!=raw or (current.st_dev,current.st_ino)!=(info.st_dev,info.st_ino):raise ValueError('task-version-conflict')
                    os.replace(temp,path.name,src_dir_fd=fd,dst_dir_fd=fd);os.fsync(fd)
                    observed,_=read_task_fd(fd,path.name)
                    if observed!=proposed:raise ValueError('plan-write-readback-conflict-inspect-before-retry')
                finally:
                    try:os.unlink(temp,dir_fd=fd)
                    except FileNotFoundError:pass
            result['writes']=True
            return result
        finally:os.close(fd)

    def creation_snapshot(self):
        """Read-only canonical task population; detect insertions as well as edits."""
        files={}; identities={}
        for path,_ in self.tasks():
            parent=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
            try:raw,info=read_task_fd(parent,path.name)
            finally:os.close(parent)
            meta=frontmatter(raw.decode('utf-8'))
            if meta.get('type')!='task':raise ValueError('task-population-changed-during-read')
            key=identity(meta)
            if key and key in identities:raise ValueError('ambiguous-task-source-identity')
            if key:identities[key]=(path,meta)
            files[str(path.relative_to(self.task_dir))]={'sha256':hashlib.sha256(raw).hexdigest(),'mode':stat.S_IMODE(info.st_mode)}
        roots=[(p.stat().st_dev,p.stat().st_ino,stat.S_IMODE(p.stat().st_mode)) for p in (self.root,self.task_dir)]
        digest=hashlib.sha256(json.dumps([roots,files],sort_keys=True).encode()).hexdigest()
        return digest,files,identities

    def creation_target(self,path):
        path=safe_path(self.task_dir,Path(path))
        if '..' in path.parts:raise ValueError('unsafe-task-path')
        ancestor=path.parent
        while not ancestor.exists():ancestor=ancestor.parent
        if not ancestor.is_dir() or not os.access(ancestor,os.W_OK|os.X_OK):
            raise ValueError('task-parent-not-writable')
        return path

    def prepare_candidates(self,candidates):
        """Freeze the ENTIRE create/reuse batch, UUIDs and bytes without writing."""
        if self.profile!='silverbullet-v1':raise ValueError('silverbullet-writer-profile-required')
        if not isinstance(candidates,list) or not candidates:raise ValueError('nonempty-task-batch-required')
        snapshot,files,existing=self.creation_snapshot()
        entries=[];seen_keys=set();seen_paths=set()
        for value in candidates:
            value=self.candidate(value);key=identity(value)
            if not key or key in seen_keys:raise ValueError('missing-or-duplicate-batch-task-identity')
            seen_keys.add(key)
            if key in existing:
                target,meta=existing[key]
                if str(meta.get('status','')).strip().lower() in {'done','completed','cancelled','archived','deleted'}:
                    raise ValueError('closed-task-source-cannot-be-recreated')
                body=None;expected=files[str(target.relative_to(self.task_dir))]['sha256']
            else:
                target=self.task_dir/segment(value['client'],'bez-klienta')/segment(value['project'],'bez-projektu')/(segment(value['title'],'Zadanie')+'.md')
                if target.exists():raise ValueError('task-title-path-collision')
                value={**value,**new_identity()};body=self.render(value);expected=None
                if len(body.encode())>MAX_TASK:raise ValueError('task-exceeds-size-bound')
            self.creation_target(target)
            if str(target) in seen_paths:raise ValueError('batch-task-path-collision')
            seen_paths.add(str(target))
            entries.append({'path':str(target),'expected_sha256':expected,'value':value,'body':body})
        plan={'contract':'silverbullet-create-plan-v1','task_dir':str(self.task_dir),'snapshot':snapshot,'snapshot_files':files,'entries':entries}
        plan['fingerprint']=hashlib.sha256(json.dumps(plan,sort_keys=True).encode()).hexdigest()
        return plan

    def check_prepared(self,plan):
        if not isinstance(plan,dict) or not isinstance(plan.get('entries'),list) or not plan['entries']:
            raise ValueError('invalid-task-create-plan')
        payload={k:v for k,v in plan.items() if k!='fingerprint'}
        if (plan.get('contract')!='silverbullet-create-plan-v1' or plan.get('task_dir')!=str(self.task_dir)
                or hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()!=plan.get('fingerprint')):
            raise ValueError('changed-task-create-plan')
        if self.creation_snapshot()[0]!=plan['snapshot']:raise ValueError('task-population-drift')
        paths=set();keys=set()
        for entry in plan['entries']:
            path=self.creation_target(entry['path']);expected=entry['expected_sha256']
            key=identity(entry['value'])
            if not key or key in keys or str(path) in paths:raise ValueError('duplicate-prepared-task')
            keys.add(key);paths.add(str(path))
            if expected is None:
                if path.exists():raise ValueError('task-title-path-collision')
                if self.render(entry['value'])!=entry['body']:raise ValueError('changed-prepared-task-body')
            elif not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
                raise ValueError('reused-task-version-conflict')

    def write_prepared(self,plan):
        """Commit exact prepared bytes once; caller verifies actual owner scope."""
        if self.profile!='silverbullet-v1':raise ValueError('silverbullet-writer-profile-required')
        self.check_prepared(plan)
        lock=safe_path(self.root,self.root/'.ai-system-task-store.lock')
        written=[];reused=[]
        with os.fdopen(os.open(lock,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600),'r+') as stream:
            fcntl.flock(stream,fcntl.LOCK_EX);self.check_prepared(plan)
            for entry in plan['entries']:
                path=Path(entry['path'])
                if entry['expected_sha256'] is not None:
                    reused.append(path);continue
                self.creation_target(path);path.parent.mkdir(parents=True,exist_ok=True)
                safe_path(self.task_dir,path.parent);temporary=None
                try:
                    with tempfile.NamedTemporaryFile(dir=path.parent,prefix='.ai-system-create-',delete=False) as out:
                        temporary=Path(out.name);os.fchmod(out.fileno(),0o600)
                        out.write(entry['body'].encode());out.flush();os.fsync(out.fileno())
                    safe_path(self.task_dir,path.parent)
                    os.link(temporary,path,follow_symlinks=False)
                    if path.read_bytes()!=entry['body'].encode():raise ValueError('task-create-readback-conflict')
                finally:
                    if temporary is not None:temporary.unlink(missing_ok=True)
                written.append(path)
            expected_files=dict(plan['snapshot_files'])
            for entry in plan['entries']:
                if entry['expected_sha256'] is None:
                    expected_files[str(Path(entry['path']).relative_to(self.task_dir))]={
                        'sha256':hashlib.sha256(entry['body'].encode()).hexdigest(),'mode':0o600}
            if self.creation_snapshot()[1]!=expected_files:
                raise ValueError('task-population-drift-after-create; inspect before recovery')
        return written,reused

    def write_candidates(self,candidates):
        if self.profile!='silverbullet-v1':raise ValueError('silverbullet-writer-profile-required')
        # Preflight complete candidate population before the first file mutation.
        candidates=[self.candidate(value) for value in candidates]
        written=[];skipped=0
        lock=safe_path(self.root,self.root/'.ai-system-task-store.lock')
        with os.fdopen(os.open(lock,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600),'r+') as stream:
            fcntl.flock(stream,fcntl.LOCK_EX)
            existing={}
            for path,meta in self.tasks():
                key=identity(meta)
                if key:
                    if key in existing:raise ValueError('ambiguous-task-source-identity')
                    existing[key]=path
            for value in candidates:
                key=identity(value)
                if key and key in existing:skipped+=1;continue
                directory=self.task_dir/segment(value['client'],'bez-klienta')/segment(value['project'],'bez-projektu')
                target=safe_path(self.task_dir,directory/(segment(value['title'],'Zadanie')+'.md'))
                if target.exists():raise ValueError('task-title-path-collision')
                # O_EXCL prevents overwriting a task created by the UI concurrently.
                data=self.render({**value, **new_identity()})
                if len(data.encode())>MAX_TASK:raise ValueError('task-exceeds-size-bound')
                directory.mkdir(parents=True,exist_ok=True);safe_path(self.task_dir,directory)
                temporary = None
                try:
                    with tempfile.NamedTemporaryFile(dir=directory,prefix='.ai-system-create-',delete=False) as output:
                        temporary=Path(output.name);output.write(data.encode('utf-8'));output.flush();os.fsync(output.fileno())
                    safe_path(self.task_dir,directory)
                    os.link(temporary,target,follow_symlinks=False)
                except FileExistsError:raise ValueError('task-title-path-collision') from None
                finally:
                    if temporary is not None:temporary.unlink(missing_ok=True)
                written.append(target)
                if key:existing[key]=target
        return written,skipped,[],[]
