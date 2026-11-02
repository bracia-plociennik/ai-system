"""Prepare selected confirmed SPOR items for one native SilverBullet task stage.

Selection and hashes are data, never consent. No module path comes from input.
"""
import copy
import hashlib
import importlib.machinery
import importlib.util
import json
from pathlib import Path
from datetime import date
from finalization_support import safe_path, sha
from spor_preflight import normalize_plan
from task_store import TaskStore


def generator():
    loader=importlib.machinery.SourceFileLoader('spor_native_task_projection',str(Path(__file__).parent/'propose-task-candidates'))
    spec=importlib.util.spec_from_loader(loader.name,loader)
    module=importlib.util.module_from_spec(spec);loader.exec_module(module)
    return module


def prepare_task_request(workspace,request,item_ids):
    """Derive references before canonical; retain the prepared bytes in memory."""
    workspace=Path(workspace)
    if (not isinstance(item_ids,list) or not item_ids or any(not isinstance(x,str) or not x for x in item_ids)
            or len(set(item_ids))!=len(item_ids)):
        raise ValueError('Explicit unique new task item IDs required')
    request=normalize_plan(request);props=request['properties'];mode=props['artifact_kind']
    key='planned_items_json' if mode=='daily' else 'future_plan_items_json'
    if key not in request['confirmed_properties']:
        raise ValueError('New tasks require confirmed plan items')
    items=json.loads(props[key]);selected=[x for x in items if x['id'] in item_ids]
    if len(selected)!=len(item_ids):raise ValueError('Unknown new task item ID')
    native=generator()
    for item in selected:
        try:mapping=native.explicit_item_mapping(item,workspace,Path('candidate'),'SPOR item')
        except SystemExit as exc:raise ValueError(str(exc)) from exc
        if not mapping or not (mapping.get('scope')=='workspace' or any(mapping.get(k) for k in ('client','owned_asset','project','project_state'))):
            raise ValueError('Explicit owner mapping required for new task')
        if item.get('task_bucket') not in {'do','defer','delegate','delete','dump','daily'}:
            raise ValueError('Explicit task bucket required for new task')
    if mode=='daily':
        day=date.fromisoformat(request['date']);relative=f'personal-ops/check-ins-v4/{day.year}/{day}.md'
        project=native.candidates_from_v4_daily
    elif mode=='weekly':
        monday=date.fromisoformat(props['review_week_start']);week=monday.isocalendar()
        relative=f'personal-ops/weekly-check-ins-v4/{week.year}/{week.year}-W{week.week:02}.md'
        project=native.candidates_from_v4_weekly
    else:raise ValueError('Unsupported SPOR task mode')
    projection=copy.deepcopy(props);projection[key]=json.dumps(selected)
    # Empty label sets disable heuristic matching; canonical mapping is authoritative.
    labels={x:[] for x in ('client','owned_asset','project_state','taskforge_project')}
    try:values=project(workspace/relative,workspace,labels,properties=projection)
    except SystemExit as exc:raise ValueError(str(exc)) from exc
    if len(values)!=len(selected):raise ValueError('Only explicit Build/Deliver/Promote tasks are supported')
    store=TaskStore.load(workspace);plan=store.prepare_candidates(values)
    references=[str(Path(x['path']).relative_to(workspace)) for x in plan['entries']]
    old=json.loads(props.get('task_generation_references_json') or '[]')
    if not isinstance(old,list) or len(set(old))!=len(old):raise ValueError('Invalid existing task references')
    props['task_generation_references_json']=json.dumps(list(dict.fromkeys([*old,*references])))
    # This describes preparation, not a completed creation or owner permission.
    props['task_generation_status']='prepared'
    for field in ('task_generation_references_json','task_generation_status'):
        if field not in request['confirmed_properties']:request['confirmed_properties'].append(field)
    binding={'artifact_path':relative,'items_key':key,'items':props[key],
             'references':props['task_generation_references_json']}
    return request,{'plan':plan,'binding':binding}


def new_tasks_readiness(workspace,candidate,fingerprint,prepared):
    """Source-bound pure creation readiness, also supporting exact-source reuse."""
    from spor_integration_preflight import existing_tasks_readiness
    store=TaskStore.load(workspace);plan=prepared['plan'];store.check_prepared(plan)
    props=candidate['properties'];binding=prepared['binding']
    if (candidate['path']!=binding['artifact_path'] or props[binding['items_key']]!=binding['items']
            or props['task_generation_references_json']!=binding['references']):
        raise ValueError('Prepared tasks do not match final SPOR candidate')
    config='tasks/task-store.local.md';inputs={config:sha(safe_path(workspace,config))}
    new=[]
    for entry in plan['entries']:
        relative=str(Path(entry['path']).relative_to(workspace))
        inputs[relative]=entry['expected_sha256']
        if entry['expected_sha256'] is None:new.append(relative)
    refs=json.loads(props['task_generation_references_json'])
    existing=[x for x in refs if x not in new]
    if existing:
        subset=copy.deepcopy(candidate);subset['properties']['task_generation_references_json']=json.dumps(existing)
        inputs.update(existing_tasks_readiness(workspace,subset,fingerprint)['inputs'])
    return {'status':'ready','candidate_sha256':fingerprint,'inputs':inputs,
            'task_population':{'contract':'silverbullet-task-population-v1',
                'task_dir':str(store.task_dir.relative_to(workspace)),'snapshot':plan['snapshot'],'targets':new},
            'creation_manifest':[{'path':str(Path(x['path']).relative_to(workspace)),
                'before_sha256':x['expected_sha256'],
                'after_sha256':hashlib.sha256(x['body'].encode()).hexdigest() if x['body'] is not None else x['expected_sha256'],
                'task_id':x['value'].get('task_id')} for x in plan['entries']],
            'preview':{'create':new,'reuse':[str(Path(x['path']).relative_to(workspace)) for x in plan['entries'] if x['expected_sha256'] is not None]}}


def check_task_population(workspace,proof):
    if (not isinstance(proof,dict) or set(proof)!={'contract','task_dir','snapshot','targets'}
            or proof['contract']!='silverbullet-task-population-v1' or not isinstance(proof['targets'],list)):
        raise ValueError('Invalid task population proof')
    store=TaskStore.load(workspace)
    if store.profile!='silverbullet-v1' or safe_path(workspace,proof['task_dir'])!=store.task_dir:
        raise ValueError('Unselected task population')
    if store.creation_snapshot()[0]!=proof['snapshot']:raise ValueError('Task population changed before canonical')
    for relative in proof['targets']:store.creation_target(safe_path(workspace,relative))
