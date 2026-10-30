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
from local_paths import resolve_path
from task_identity import new_identity

PROFILES = {'tasknotes-v1', 'silverbullet-v1'}
CATEGORIES = {'do': ('open','high'), 'defer': ('planned','normal'),
              'delegate': ('waiting','normal'), 'delete': ('cancelled','none'),
              'dump': ('open','none')}
MAX_TASK = 1024 * 1024


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
    for kind,fields in [('weekly',('source_week_id','source_week_item_id')),
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

    def candidate(self,value):
        """Project an existing source candidate into the selected app's field contract."""
        result=dict(value)
        if self.profile!='silverbullet-v1':return result
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
        primary=['type','title','status','priority','client','project','category','scheduled']
        provenance=['workspace','owner_scope','owned_asset','project_state','source_system','source_type',
                    'source_check_in_date','source_check_in_field','source_session_date','source_plan_item_id',
                    'source_week_id','source_week_item_id','source_week_plan','estimated_minutes','weekly_allocations_json',
                    'source_dream_report','candidate_key','source_candidate_id','source_deadline',
                    'task_id','created_at','completed_at','reopened_at']
        lines=['---']+[key+': '+json.dumps(value.get(key,''),ensure_ascii=False) for key in primary]
        lines += [key+': '+json.dumps(value[key],ensure_ascii=False) for key in provenance if key in value]
        dod=str(value.get('definition_of_done') or '').replace('\r','').replace('\n','\n  ')
        lines += ['---','# '+value['title'],'- Category: '+value['category'],'- DoD: '+dod,
                  '- Deadline: '+value['scheduled'],'','## Checkpoint OSNR','- O — Outcome:',
                  '- S — Status:','- N — Next:','- R — Resume:','','## TODO','- [ ] '+value['title'],
                  '','## Evidence','','## Working dump','']
        return '\n'.join(lines)

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
                directory.mkdir(parents=True,exist_ok=True);safe_path(self.task_dir,directory)
                # O_EXCL prevents overwriting a task created by the UI concurrently.
                data=self.render({**value, **new_identity()})
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
