"""Local artifact adapters; actual current owner scope is checked by the caller."""
import csv
import difflib
import io
import json
import os
from datetime import date
from pathlib import Path
from finalization_support import safe_path,sha


def publish(root, relative, data, *, approved=False, guard=None):
    target=safe_path(root,relative)
    if not approved:
        raise ValueError("Caller must verify actual owner scope before apply")
    if guard:
        guard()
    if target.exists():
        raise ValueError("Existing artifact requires explicit reconciliation")
    import secrets
    rootfd=os.open(Path(root).absolute(),os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    fd=rootfd;temporary=None
    try:
        parts=Path(relative).parts
        for part in parts[:-1]:
            try:os.mkdir(part,0o700,dir_fd=fd)
            except FileExistsError:pass
            nxt=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
            if fd!=rootfd:os.close(fd)
            fd=nxt
        temporary='.finalize-'+secrets.token_hex(16)
        handle=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=fd)
        with os.fdopen(handle,'wb') as f:
            f.write(data);f.flush();os.fsync(f.fileno())
        if guard:guard()
        os.link(temporary,parts[-1],src_dir_fd=fd,dst_dir_fd=fd,follow_symlinks=False)
        os.fsync(fd)
        handle=os.open(parts[-1],os.O_RDONLY|os.O_NOFOLLOW,dir_fd=fd)
        with os.fdopen(handle,'rb') as f:
            if f.read()!=data:raise ValueError('Readback mismatch; preserve artifact')
    finally:
        if temporary:
            try:os.unlink(temporary,dir_fd=fd)
            except FileNotFoundError:pass
        if fd!=rootfd:os.close(fd)
        os.close(rootfd)
    return {'path':relative,'sha256':sha(target),'status':'saved-and-readback'}


def document(root, request, *, apply=False, approved=False):
    if set(request)!={'format','path','columns','rows','body'}:
        raise ValueError("Unsupported document request")
    if request['format']=='csv':
        columns,rows=request['columns'],request['rows']
        if not isinstance(columns,list) or not columns or len(set(columns))!=len(columns) or any(not isinstance(x,str) or not x for x in columns):
            raise ValueError("Explicit unique CSV columns required")
        if not isinstance(rows,list) or any(not isinstance(r,list) or len(r)!=len(columns) or any(not isinstance(x,str) for x in r) for r in rows):
            raise ValueError("CSV shape/type mismatch")
        out=io.StringIO(newline='');w=csv.writer(out);w.writerow(columns);w.writerows(rows)
        text=out.getvalue()
        if list(csv.reader(io.StringIO(text)))!=[columns,*rows]:raise ValueError('CSV roundtrip failed')
    elif request['format']=='markdown':
        text=request['body']
        if not isinstance(text,str) or not text.strip() or request['columns'] or request['rows']:raise ValueError('Invalid Markdown input')
    else:raise ValueError('Supported formats: csv, markdown')
    target=safe_path(root,request['path'])
    if target.exists():raise ValueError('Existing artifact; no implicit overwrite')
    if not apply:return {'status':'preview','body':text,'permission_granted':False}
    return publish(root,request['path'],text.encode('utf-8'),approved=approved)


def spor_candidate(workspace, request):
    import personal_ops_drafts as drafts
    import personal_ops_v4 as v4
    from personal_ops_aggregates_v4 import observations,budget_facts
    required={'date','draft_sha256','fields','properties','confirmed_properties','owner_reference'}
    if set(request)!=required or not request['owner_reference']:raise ValueError('Invalid normalization package')
    day=date.fromisoformat(request['date']);saved=drafts.read(workspace,day)
    if saved['sha256']!=request['draft_sha256'] or saved['metadata']['status']!='draft':raise ValueError('Stale draft or lifecycle conflict')
    fields=request['fields']
    if not isinstance(fields,dict):raise ValueError('Field patch must be an object')
    mode=saved['metadata']['mode']
    if saved['metadata'].get('template_sha256')!=drafts.digest(drafts.template(mode).encode()):
        raise ValueError('Template changed; explicit reconciliation required')
    matches=list(drafts.FIELD.finditer(saved['body']))
    if len(matches)!=len(drafts.form(mode)) or {m[1] for m in matches}!=set(drafts.form(mode)):
        raise ValueError('Edited field structure requires manual reconciliation')
    if fields:drafts.validate_fields(mode,fields,initial=False)
    props=dict(request['properties']);confirmed=request['confirmed_properties']
    if not isinstance(confirmed,list) or any(x not in props for x in confirmed):raise ValueError('Invalid confirmed property list')
    # The model performs normalization once; only explicit properties are accepted.
    # List attestation is supporting data, not proof of consent or semantic correctness.
    structural={'index_contract','schema_version','artifact_kind','report_id','session_date','closure_date','review_window_start','review_window_end','review_window_kind','review_week_start','review_week_end','plan_week_start','plan_week_end','privacy','private_index_policy','task_generation_policy','task_generation_status','life_alignment_contract'}
    for key,value in props.items():
        if key not in confirmed and value not in ('',None,'{}','[]','unknown') and key not in structural:
            raise ValueError(('Unconfirmed plan property: ' if key in ('planned_items_json','future_plan_items_json','planned_schedule_json','future_wig_json','daily_blocks_json') else 'Property needs explicit owner/source normalization: ')+key)
    mode=saved['metadata']['mode'];period=saved['metadata']['periods']
    for key in ('planned_items_json','future_plan_items_json','planned_schedule_json','future_wig_json','daily_blocks_json'):
        if key in props and props[key] not in ('[]','{}','') and key not in confirmed:
            raise ValueError('Unconfirmed plan property: '+key)
    if mode=='daily':
        if props.get('session_date')!=str(day) or props.get('review_window_start')!=period['review_start'] or props.get('review_window_end')!=period['review_end']:raise ValueError('Daily period mismatch')
        rel=f'personal-ops/check-ins-v4/{day.year}/{day}.md'
    else:
        if props.get('review_week_start')!=period['review_start'] or props.get('plan_week_start')!=period['plan_start'] or props.get('plan_week_end')!=period['plan_end']:raise ValueError('Weekly period mismatch')
        monday=date.fromisoformat(props['review_week_start']);week=monday.isocalendar()
        rel=f'personal-ops/weekly-check-ins-v4/{week.year}/{week.year}-W{week.week:02}.md'
    target=safe_path(workspace,rel)
    if target.exists():raise ValueError('Canonical exists; explicit reconciliation required')
    body=drafts.FIELD.sub(lambda m:'<!-- spor-field:'+m[1]+' -->\n'+fields.get(m[1],m[2])+'\n<!-- /spor-field -->',saved['body'])
    body=__import__('re').sub(r'^<!-- (?:spor-field:f\d{3}|/spor-field) -->\n?','',body,flags=__import__('re').MULTILINE)
    body=body.replace('— szkic do uzupełnienia','— zapis właściciela',1)
    body=body.replace('Szkic niezatwierdzony; nie jest źródłem faktów ani zatwierdzonym planem.','Canonical po uzupełnieniu właściciela; propozycje AI zachowują swoje oznaczenie.',1)
    body=body.replace('- Szkic nie zasila indeksów, TaskNotes ani kalendarza. Zapis canonical wymaga aktualnego zatwierdzenia właściciela.','- Zakres dalszych zapisów wynika z aktualnej zgody właściciela.')
    props.setdefault('life_alignment_contract','last-period-alignment-v1')
    top={'type':mode+'-check-in-v4','schema_version':4,'index_contract':4,'report_id':props.get('report_id')}
    (v4.validate_daily if mode=='daily' else v4.validate_weekly)(top,props,target,body)
    # Reuse the actual budget consumer before any canonical write.
    obs=observations(props,{})
    if obs:
        first=min(date.fromisoformat(x['period_start']) for x in obs);last=max(date.fromisoformat(x['period_end']) for x in obs)
        for metric in ('spending','calories'):
            budget_facts([*v4.load_current_records(workspace),{'session_date':str(day),'aggregate_observations':obs}],first,last,metric)
    text='---\n'+'\n'.join(k+': '+json.dumps(v,ensure_ascii=False) for k,v in top.items())+'\nproperties:\n'+'\n'.join('  '+k+': '+json.dumps(v,ensure_ascii=False) for k,v in props.items())+'\n---\n\n'+v4.ensure_working_dump(body)
    return {'path':rel,'body':text,'draft':saved,'properties':props,'diff':''.join(difflib.unified_diff(saved['body'].splitlines(True),body.splitlines(True),fromfile='draft',tofile='canonical-view'))}


def native_spor_hooks(workspace):
    """Known mandatory product consumers. No tasks/calendar are enabled implicitly."""
    import subprocess
    import personal_ops_v4 as v4
    scripts=Path(__file__).resolve().parent
    def run(stage):
        def call(path,fingerprint):
            top,props,body=v4.parse_frontmatter(path)
            if sha(path)!=fingerprint:raise ValueError('Changed native input')
            if stage=='indexes':
                args=[str(scripts/'sync-personal-ops-check-ins-v4'),'--workspace',str(workspace),'--post-write']
            elif props['artifact_kind']=='daily':
                args=[str(scripts/'render-personal-ops-daily-summary-v4'),'--workspace',str(workspace),'--date',props['session_date']]
            else:
                args=[str(scripts/'render-personal-ops-weekly-summary'),'--workspace',str(workspace),'--week',props['report_id']]
            result=subprocess.run(args,capture_output=True,text=True,timeout=120)
            if result.returncode or not result.stdout.strip():raise ValueError('Native stage failed: '+stage)
            if sha(path)!=fingerprint:raise ValueError('Source changed during native stage')
            return {'status':'verified','source_sha256':fingerprint,'output':result.stdout}
        return call
    return {stage:run(stage) for stage in ('indexes','renderer')}


def finalize_spor(workspace, request, *, apply=False, approved=False, integrations=(), hooks=None):
    import personal_ops_drafts as drafts
    hooks=native_spor_hooks(workspace) if hooks is None else hooks
    stages=spor_stages(integrations)
    candidate=spor_candidate(workspace,request)
    if not apply:return {'status':'preview','path':candidate['path'],'diff':candidate['diff'],'required_stages':stages,'permission_granted':False}
    if not approved:raise ValueError('Actual owner scope required')
    if any(x not in hooks for x in stages):raise ValueError('Missing explicit trusted stage adapter')
    def guard():
        current=drafts.read(workspace,date.fromisoformat(request['date']))
        if current['sha256']!=request['draft_sha256']:raise ValueError('Draft changed before persistence')
    receipt=publish(workspace,candidate['path'],candidate['body'].encode(),approved=approved,guard=guard)
    receipt.update(recovery_contract='spor-finalization-recovery-v1', required_stages=stages,
                   draft_sha256=request['draft_sha256'], date=request['date'])
    done=['canonical'];attempted=[];current=receipt['sha256']
    try:
        for stage in stages:
            path=safe_path(workspace,candidate['path'])
            if sha(path)!=current:raise ValueError('Canonical changed between stages')
            # Hooks are reviewed Python callables supplied by the caller, never payload commands.
            attempted.append(stage)
            result=hooks[stage](path,current)
            if not isinstance(result,dict) or result.get('status')!='verified' or result.get('source_sha256')!=current:raise ValueError('Stage not independently verified: '+stage)
            done.append(stage)
        if sha(path)!=current:raise ValueError('Canonical changed after readback')
        drafts.mark_approved(workspace,date.fromisoformat(request['date']),request['draft_sha256'],candidate['path'],current,request['owner_reference'])
        return {**receipt,'status':'finalized','completed':done+['draft-receipt'],'attempted':attempted}
    except Exception:
        # Durable-first. Do not retry unknown external effects or erase valid source.
        return {**receipt,'status':'partial','completed':done,'attempted':attempted,'next_step':stages[len(done)-1] if len(done)<=len(stages) else 'draft-receipt','reason':'Inspect preserved source and actual stage effect before recovery'}


def spor_stages(integrations):
    if not isinstance(integrations,(tuple,list)) or any(x not in ('tasks','calendar') for x in integrations):
        raise ValueError('Unknown integration')
    if len(set(integrations))!=len(integrations):
        raise ValueError('Duplicate integration')
    return ['indexes','renderer',*integrations]


def resume_spor(workspace, request, receipt, *, approved=False, integrations=(), hooks=None, completed_checks=None):
    """Reverify completed/attempted effects; never infer that a missing result is absent."""
    import personal_ops_drafts as drafts
    import personal_ops_v4 as v4
    hooks={} if hooks is None else hooks
    completed_checks={} if completed_checks is None else completed_checks
    stages=spor_stages(integrations)
    if (receipt.get('recovery_contract')!='spor-finalization-recovery-v1'
            or receipt.get('required_stages')!=stages
            or receipt.get('draft_sha256')!=request['draft_sha256']
            or receipt.get('date')!=request['date']):
        raise ValueError('Recovery scope or source identity mismatch; explicit reconciliation required')
    completed=receipt.get('completed');attempted=receipt.get('attempted')
    if (not isinstance(completed,list) or not isinstance(attempted,list)
            or completed!=['canonical',*stages[:len(completed)-1]]
            or not completed or attempted!=stages[:len(attempted)]
            or len(attempted) not in (len(completed)-1,len(completed))):
        raise ValueError('Invalid recovery progress')
    day=date.fromisoformat(request['date']);saved=drafts.read(workspace,day)
    if (not approved or not request.get('owner_reference') or saved['sha256']!=request['draft_sha256']
            or saved['metadata']['status']!='draft'):
        raise ValueError('Current scoped approval and unchanged draft required')
    if receipt['path'] not in drafts.canonical_sources(workspace,day):raise ValueError('Recovery canonical identity mismatch')
    path=safe_path(workspace,receipt['path'])
    if sha(path)!=receipt['sha256']:raise ValueError('Changed canonical; reconcile')
    top,props,body=v4.parse_frontmatter(path)
    (v4.validate_daily if saved['metadata']['mode']=='daily' else v4.validate_weekly)(top,props,path,body)
    done=list(completed);attempted=list(attempted)
    def partial(stage,reason):
        return {**receipt,'status':'partial','completed':list(done),'attempted':list(attempted),'next_step':stage,'reason':reason}
    for stage in stages:
        if sha(path)!=receipt['sha256']:raise ValueError('Recovery source changed')
        check=completed_checks.get(stage)
        if stage in attempted or check is not None:
            if check is None:return partial(stage,'Read-only effect check required; do not replay')
            try:result=check(path,receipt['sha256'])
            except Exception:return partial(stage,'Readback failed; inspect, do not replay')
            if (not isinstance(result,dict) or result.get('source_sha256')!=receipt['sha256']
                    or sha(path)!=receipt['sha256']):
                return partial(stage,'Effect uncertain; inspect, do not replay')
            if result.get('status')=='verified':
                if stage not in attempted:attempted.append(stage)
                if stage not in done:done.append(stage)
                continue
            if stage in done or result.get('status')!='not-applied':
                return partial(stage,'Effect uncertain; inspect, do not replay')
            # Only actual source-bound negative readback permits retry of an attempted mutation.
        if stage not in hooks:return partial(stage,'Missing trusted pending stage adapter')
        if sha(path)!=receipt['sha256']:raise ValueError('Recovery source changed before mutation')
        if stage not in attempted:attempted.append(stage)
        try:result=hooks[stage](path,receipt['sha256'])
        except Exception:return partial(stage,'Stage failed; inspect actual effect before recovery')
        if not isinstance(result,dict) or result.get('status')!='verified' or result.get('source_sha256')!=receipt['sha256']:
            return partial(stage,'Stage result uncertain; inspect before recovery')
        done.append(stage)
    if sha(path)!=receipt['sha256']:raise ValueError('Recovery source changed before receipt')
    try:drafts.mark_approved(workspace,day,request['draft_sha256'],receipt['path'],receipt['sha256'],request['owner_reference'])
    except Exception:return partial('draft-receipt','Receipt failed; preserve source and verified progress')
    return {**receipt,'status':'finalized','completed':done+['draft-receipt'],'attempted':attempted}
