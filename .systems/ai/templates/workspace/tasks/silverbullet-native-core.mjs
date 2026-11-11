import {completionEdit} from './silverbullet-task-fields.mjs';
// Embedded into the task panel module. Private offline data uses native Space storage.
export const nativeTracker = (() => {
  const api = '.task-tracker/api/v1/';
  const deviceKey = 'silverbullet-tracker-device-v1';
  let device;try{device=localStorage.getItem(deviceKey);}catch{}
  if (!device) { device = crypto.randomUUID(); try{localStorage.setItem(deviceKey, device);}catch{} }
  let io, state = {version:0,runs:[],entities:[]}, token='', online=false, pending=[];
  let busy=false, synchronizing=null, listeners=new Set(), selected=null, cachedFingerprint='';
  const drafts=new Map();
  const uuid=()=>crypto.randomUUID();
  const clone=value=>JSON.parse(JSON.stringify(value));
  let message='';
  function notice(value){message=String(value||'');notify();}
  let changeHook=null,poll=null,ticks=0;
  function notify(){for(const fn of [...listeners])fn();if(changeHook){try{Promise.resolve(changeHook("state")).catch(()=>{});}catch{}}}
  function connect(callback,changed){configure(callback);changeHook=changed||changeHook;if(!poll){poll=setInterval(()=>{if(changeHook){try{Promise.resolve(changeHook("clock")).catch(()=>{});}catch{}}if(++ticks%5===0)sync().catch(e=>notice(e.message));},1000);sync().catch(e=>notice(e.message));}return snapshot();}
  function snapshot(){return {...clone(view()),online,pending:pending.length,busy,message,device_id:device};}

  const cachedPath=`tracker-cache/${device}/state`;
  const eventPath=id=>`tracker-outbox/${device}/${id}`;
  const ackPath=(origin,id)=>`tracker-acks/${origin}/${id}`;
  const draftPath=id=>`tracker-drafts/${device}/${id}`;
  async function native(op,payload={}){if(!io)throw new Error('Panel timera nie jest jeszcze gotowy.');return await io(op,JSON.stringify(payload));}
  async function read(page,strict=false){try{const raw=String(await native('read',{page}));const match=raw.match(/^---\r?\n[\s\S]*?\r?\n---\r?\n([\s\S]*)$/);if(!match)throw new Error('Nieprawidłowy zapis kolejki offline.');return JSON.parse(match[1]);}catch(error){if(strict)throw error;return null;}}
  async function write(page,value,type='tracker-data'){await native('write',{page,text:`---\ntype: ${type}\n---\n${JSON.stringify(value)}\n`});}
  async function call(path,body){
    const response=await fetch(new URL(api+path,document.baseURI),{method:body===undefined?'GET':'POST',credentials:'same-origin',redirect:'error',signal:AbortSignal.timeout(10000),headers:body===undefined?{}:{'Content-Type':'application/json','X-Task-Tracker-CSRF':token},body:body===undefined?undefined:JSON.stringify(body)});
    let result;try{result=await response.json();}catch{throw new Error('Nieprawidłowa odpowiedź adaptera timera.');}
    if(!response.ok){const messages={'resolve-time-conflicts-first':'Najpierw rozstrzygnij wskazane konflikty czasu w panelu WEP.','task-identity-ambiguous':'Zadanie ma powtórzone ID. Rozstrzygnij konflikt plików przed pomiarem.','task-conflict-needs-resolution':'Zadanie ma nierozstrzygniętą kopię konfliktową.','authentication-required':'Sesja logowania wygasła. Zaloguj się ponownie.','state-changed-repreview':'Stan zmienił się. Przygotuj nowy podgląd WEP.','task-changed-repreview':'Zadanie zmieniło się. Przygotuj nowy podgląd WEP.'};const error=new Error(messages[result.error]||result.error||'Nie udało się zapisać.');error.code=result.error;error.http=response.status;throw error;}
    return result;
  }
  async function inventory(){
    const pages=await native('list');const list=Array.isArray(pages)?pages:[];const names=new Set(list.map(p=>typeof p==='string'?p:p.name));
    const result=[];
    for(const name of [...names].filter(n=>n.startsWith('tracker-outbox/')).sort()){
      const value=await read(name,true);if(!value?.operation_id)throw new Error('Nieprawidłowe zdarzenie kolejki offline.');
      if(!names.has(ackPath(value.device_id,value.operation_id)))result.push(value);
    }
    return result.sort((a,b)=>a.occurred_at.localeCompare(b.occurred_at)||a.operation_id.localeCompare(b.operation_id));
  }
  function optimistic(base,events){
    const result=clone(base);
    for(const event of events){
      let run=result.runs.find(r=>r.id===event.run_id);
      if(event.action==='start'&&!run){run={id:event.run_id,task_id:event.task_id,state:'active',review:0,status:'partial',segments:[],path:event.task_path||'',receipt:null,local:true};result.runs.unshift(run);}
      if(!run)continue;
      if(['start','resume'].includes(event.action)){
        if(!run.segments.some(s=>s.id===event.segment_id))run.segments.push({id:event.segment_id,start:event.occurred_at,end:null,basis:'owner-confirmed'});
        run.state='active';
      }
      if(['pause','stop','complete'].includes(event.action)){
        for(const s of run.segments)if(!s.end)s.end=event.occurred_at;
        run.state=event.action==='pause'?'paused':'stopped';if(event.action==='complete')run.status='done';
      }
      run.local=true;result.version=Math.max(result.version,event.expected_version)+1;
    }
    return result;
  }
  const view=()=>optimistic(state,pending);
  async function refresh(){
    if(!io)return;
    try{
      const current=await call('state');token=current.csrf;delete current.csrf;state=current;online=true;
      const fingerprint=JSON.stringify({...state,server_now:null});if(fingerprint!==cachedFingerprint){await write(cachedPath,state);cachedFingerprint=fingerprint;}
    }catch(e){online=false;const cached=await read(cachedPath);if(cached&&!state.runs.length)state=cached;if(e.code)message=e.code;}
    pending=await inventory();notify();
  }
  async function sync(){
    if(busy)return;
    if(synchronizing)return synchronizing;
    synchronizing=(async()=>{
      await refresh();if(!online)return;
      for(const event of [...pending]){
        try{
          const result=await call('events',{event,replay:true});
          await write(ackPath(event.device_id,event.operation_id),result,'tracker-ack');
          if(result.status==='conflict')message='Konflikt czasu: zachowano zdarzenia. Rozstrzygnij go przed WEP.';
        }catch(e){message=e.code||'Oczekiwanie na synchronizację.';break;}
      }
      await refresh();
    })().finally(()=>{synchronizing=null;});
    return synchronizing;
  }
  function configure(callback){if(callback)io=callback;}
  function taskMeta(text){
    const match=text.match(/^(?:\uFEFF)?---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/);if(!match)throw new Error('Brak nagłówka zadania.');
    const fields={};for(const line of match[1].split(/\r?\n/)){if(/^[\"'](?:type|task_id|completed_at|reopened_at|completed_at_basis|completed_event_id|reopened_at_basis|reopened_event_id)[\"']\s*:/.test(line))throw new Error('Użyj prostych, pojedynczych kluczy metadanych zadania.');const m=line.match(/^([a-z_]+):[ \t]*(.*)$/);if(!m)continue;if(Object.hasOwn(fields,m[1]))throw new Error('Powtórzone pole '+m[1]);let value=m[2].trim();try{value=JSON.parse(value);}catch{if(value.startsWith("'"))value=value.slice(1,-1).replaceAll("''","'");}fields[m[1]]=value;}
    if(fields.type!=='task')throw new Error('To nie jest zadanie.');return fields;
  }
  function patchFields(text,fields){
    const match=text.match(/^(?:\uFEFF)?---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/);taskMeta(text);let header=match[1];const nl=text.includes('\r\n')?'\r\n':'\n';
    for(const [key,value]of Object.entries(fields)){
      const expression=new RegExp('^'+key+':[ \\t]*[^\\r\\n]*','gm'),lines=[...header.matchAll(expression)];
      if(lines.length>1)throw new Error('Powtórzone pole '+key);
      const line=key+': '+JSON.stringify(value);header=lines.length?header.slice(0,lines[0].index)+line+header.slice(lines[0].index+lines[0][0].length):header+nl+line;
    }
    return text.slice(0,match.index+match[0].indexOf(match[1]))+header+text.slice(match[0].indexOf(match[1])+match[1].length);
  }
  function edit(before,after){let from=0;while(from<before.length&&from<after.length&&before[from]===after[from])from++;let tail=0;while(tail<before.length-from&&tail<after.length-from&&before[before.length-1-tail]===after[after.length-1-tail])tail++;return before===after?{unchanged:true}:{from,to:before.length-tail,insert:after.slice(from,after.length-tail)};}
  function identityEdit(text){const meta=taskMeta(text);if(meta.task_id){if(!/^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/.test(meta.task_id))throw new Error('Nieprawidłowe task_id.');return {unchanged:true};}return edit(text,patchFields(text,{task_id:uuid()}));}
  function completionWithLifecycle(text,action,fallback,serialized){
    const meta=JSON.parse(serialized||'{}');const change=completionEdit(text,action,fallback);if(change.unchanged)return change;let next=text.slice(0,change.from)+change.insert+text.slice(change.to);
    const fields=action==='complete'?{completed_at:meta.event_at,completed_at_basis:meta.basis,completed_event_id:meta.operation_id}:{completed_at:'',completed_at_basis:'',completed_event_id:'',reopened_at:meta.event_at,reopened_at_basis:meta.basis,reopened_event_id:meta.operation_id};
    if(meta.event_at)next=patchFields(next,fields);return edit(text,next);
  }
  async function identify(page){const text=await native('identity',{page});return taskMeta(String(text));}
  async function dispatch(action,page,extra={}){
    if(busy)throw new Error('Trwa zapis poprzedniej operacji.');await sync();if(busy)throw new Error('Trwa zapis poprzedniej operacji.');busy=true;
    try{
      const meta=await identify(page);await refresh();const current=view();const own=current.runs.find(r=>r.task_id===meta.task_id&&['active','paused'].includes(r.state));const active=current.runs.find(r=>r.state==='active');
      if(['start','resume'].includes(action)&&active)throw new Error('Najpierw użyj Pauzy lub Stop przy działającym timerze.');
      const event={operation_id:uuid(),device_id:device,task_id:meta.task_id,task_path:page+'.md',run_id:extra.run_id??(action==='start'?uuid():own?.id??null),action,occurred_at:new Date().toISOString(),expected_version:current.version};
      if(['start','resume'].includes(action))event.segment_id=uuid();
      if(extra.correction!==undefined)event.correction=extra.correction;if(extra.reason!==undefined)event.reason=extra.reason;
      await write(eventPath(event.operation_id),event,'tracker-event');pending=await inventory();notify();
      let result={status:'queued',event_at:event.occurred_at,basis:'owner-confirmed',run_id:event.run_id};
      if(online){
        try{
          result=await call('events',{event,replay:false});await write(ackPath(device,event.operation_id),result,'tracker-ack');
        }catch(e){
          if(e.http>=400&&e.http<500&&![401,403,408,429].includes(e.http)){
            await write(ackPath(device,event.operation_id),{status:'rejected',error:e.code},'tracker-ack');await refresh();
            if(['stale-state','pause-current-timer-first','run-not-open','run-not-paused'].includes(e.code))throw new Error('Stan zmienił się na innym urządzeniu. Odświeżono go — ponów operację.');
            throw e;
          }
          online=false;message='Zdarzenie zapisane lokalnie; oczekuje na synchronizację.';
        }
      }
      if(['stop','complete'].includes(action)&&event.run_id)selected=event.run_id;
      await refresh();return {...result,operation_id:event.operation_id};
    }finally{busy=false;notify();}
  }
  async function beforeCompletion(page,action){return dispatch(action==='complete'?'complete':'reopen',page);}
  async function createHeaders(){const current=await call('state');token=current.csrf;return {'X-Task-Tracker-CSRF':token};}
  const previews=new Map(),draftWrites=new Map(),preparing=new Set(),approving=new Set();
  const uiPreferenceKey='silverbullet-native-panel-preferences-v1';
  function preferences(){try{const p=JSON.parse(localStorage.getItem(uiPreferenceKey)||localStorage.getItem('silverbullet-panel-v2-preferences')||'{}');return {sort:['human','importance','date'].includes(p.sort)?p.sort:'human',showCompleted:p.showCompleted===true};}catch{return {sort:'human',showCompleted:false};}}
  function preference(key,value){const p=preferences();if(key==='sort'&&['human','importance','date'].includes(value))p.sort=value;else if(key==='showCompleted'&&typeof value==='boolean')p.showCompleted=value;else throw new Error('Nieznane ustawienie widoku.');try{localStorage.setItem(uiPreferenceKey,JSON.stringify(p));}catch{}notify();return p;}
  function today(at=new Date()){const p=Object.fromEntries(new Intl.DateTimeFormat('en-CA',{timeZone:'Europe/Warsaw',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(at).map(v=>[v.type,v.value]));return `${p.year}-${p.month}-${p.day}`;}
  function elapsed(run){return (run.segments||[]).reduce((sum,s)=>sum+Math.max(0,Math.floor((new Date(s.end||Date.now())-new Date(s.start))/1000)),0);}
  function duration(seconds){return `${Math.floor(seconds/3600)}:${String(Math.floor(seconds%3600/60)).padStart(2,'0')}:${String(seconds%60).padStart(2,'0')}`;}
  function daysFor(id){const run=view().runs.find(r=>r.id===id);if(!run)throw new Error('Nie ma tej sesji.');const values={};for(const s of run.segments||[]){let cursor=new Date(s.start).getTime(),end=new Date(s.end||Date.now()).getTime();if(end-cursor>366*86400000)continue;while(cursor<end){const d=today(new Date(cursor));let lo=cursor,hi=Math.min(end,cursor+27*3600000);if(today(new Date(hi))!==d){while(hi-lo>1){const mid=Math.floor((hi+lo)/2);if(today(new Date(mid))===d)lo=mid;else hi=mid;}}values[d]=(values[d]||0)+Math.max(0,Math.floor((hi-cursor)/1000));cursor=hi;}if(end===new Date(s.start).getTime())values[today(new Date(end))]=0;}if(!Object.keys(values).length)values[today()]=null;return values;}
  async function getDraft(id){if(!drafts.has(id)){const saved=await read(draftPath(id));drafts.set(id,saved&&typeof saved==='object'&&!Array.isArray(saved)?saved:{});}return clone(drafts.get(id));}
  async function saveDraft(id,value){if(!value||typeof value!=='object'||Array.isArray(value))throw new Error('Niepoprawny szkic.');await getDraft(id);if(approving.has(id))throw new Error('Trwa zatwierdzanie wpisu.');const revision=Number(drafts.get(id)?._native_revision)||0;if((Number(value._native_revision)||0)!==revision)throw new Error('Szkic zmienił się. Otwórz pole ponownie.');const next={...clone(value),_native_revision:revision+1};drafts.set(id,next);previews.delete(id);notify();const writing=(draftWrites.get(id)||Promise.resolve()).catch(()=>{}).then(()=>write(draftPath(id),next,'tracker-draft'));draftWrites.set(id,writing);await writing;return clone(next);}
  function timeCorrection(value){const days={};for(const[d,minutes]of Object.entries(value.days||{})){if(String(minutes).trim()===''||!Number.isFinite(Number(minutes))||Number(minutes)<0)throw new Error('Uzupełnij czas każdego dnia; zero wpisz jawnie.');days[d]=Math.round(Number(minutes)*60);}if(!Object.keys(days).length)throw new Error('Dodaj dzień korekty.');if(!String(value.reason||'').trim())throw new Error('Podaj powód korekty czasu.');return days;}
  function previewFor(id){const p=previews.get(id),d=drafts.get(id);return p&&p.revision===(Number(d?._native_revision)||0)?clone(p.value):null;}
  async function preparePreview(id){if(preparing.has(id)||approving.has(id))throw new Error('Trwa zapis podglądu.');preparing.add(id);try{await sync();await draftWrites.get(id);const value=await getDraft(id),revision=Number(value._native_revision)||0;previews.delete(id);if(busy||!online||pending.length||!state.runs.some(r=>r.id===id&&r.state==='stopped'))throw new Error('Poczekaj na potwierdzenie Stop i synchronizację.');const payload={run_id:id,outcome:value.outcome||'',client_id:value.client_id||null,project_id:value.project_id||null,unassigned_confirmed:value.unassigned_confirmed===true,time_confirmed:value.time_confirmed===true};if(value.correct){payload.correction=timeCorrection(value);payload.reason=value.reason;}const result=await call('wep/preview',payload);if((Number(drafts.get(id)?._native_revision)||0)!==revision)throw new Error('Szkic zmienił się. Przygotuj nowy podgląd WEP.');previews.set(id,{revision,value:result});notify();return clone(result);}finally{preparing.delete(id);}}
  async function approvePreview(id,expectedHash){const p=previewFor(id);if(!p||p.preview_hash!==expectedHash)throw new Error('Podgląd zmienił się. Przygotuj nowy.');if(busy||!online||pending.length||approving.has(id))throw new Error('Najpierw zsynchronizuj zdarzenia.');approving.add(id);try{const value=await call('wep/approve',{preview_id:p.preview_id,preview_hash:p.preview_hash});previews.delete(id);await refresh();return value;}finally{approving.delete(id);}}
  async function refreshWorkbook(id){if(!online)throw new Error('Odświeżenie arkusza wymaga połączenia.');const run=state.runs.find(r=>r.id===id);if(!run?.receipt)throw new Error('Wpis nie został zatwierdzony.');const value=await call('wep/refresh',{preview_id:run.receipt.preview_id});await refresh();return value;}
  async function selectRun(id){const run=view().runs.find(r=>r.id===id);if(!run)throw new Error('Nie ma tej sesji.');selected=id;await write(`tracker-cache/${device}/selection`,{run_id:id});notify();return clone(run);}
  let selectionLoaded=false;
  async function selectedRun(){if(!selected&&!selectionLoaded){selected=(await read(`tracker-cache/${device}/selection`))?.run_id||null;selectionLoaded=true;}return selected?clone(view().runs.find(r=>r.id===selected)||null):null;}
  async function createTask(input){if(!input||typeof input.title!=='string'||!input.title.trim()||/[\r\n]/.test(input.title)||input.title.length>180)throw new Error('Podaj tytuł w jednej linii, do 180 znaków.');const category=input.category||'do',statuses={do:'open',defer:'planned',delegate:'waiting',delete:'cancelled',dump:'open'};if(!statuses[category])throw new Error('Nieznana kategoria.');const scheduled=String(input.scheduled||'');if(scheduled&&(!/^\d{4}-\d{2}-\d{2}$/.test(scheduled)||scheduled.startsWith('0000-')||!Number.isFinite(new Date(scheduled+'T12:00:00Z').valueOf())||new Date(scheduled+'T12:00:00Z').toISOString().slice(0,10)!==scheduled))throw new Error('Podaj poprawną datę YYYY-MM-DD.');const title=input.title.trim(),client=String(input.client||'').trim(),project=String(input.project||'').trim();const segment=(v,f)=>v.trim().replace(/[\\/#@\[\]\x00-\x1f:?*<>"|]/g,'-').replace(/^\.+|\.+$/g,'').slice(0,140).trim()||f;const page=['tasks',segment(client,'bez-klienta'),segment(project,'bez-projektu'),segment(title,'Zadanie')].join('/');const response=await fetch(new URL('.fs/task-template.md',document.baseURI),{credentials:'same-origin',redirect:'error',signal:AbortSignal.timeout(15000),headers:{'X-Sync-Mode':'true'}});if(!response.ok)throw new Error('Nie można odczytać wzoru zadania.');const raw=await response.text(),fenced=raw.match(/^```markdown\r?\n([\s\S]*?)\r?\n```$/m),template=fenced?.[1].match(/^---\r?\n[\s\S]*?\r?\n---\r?\n([\s\S]*)$/);if(!template)throw new Error('Niepoprawny wzór zadania.');const priority=category==='do'?'high':['delete','dump'].includes(category)?'none':'normal';const metadata={type:'task',author:'human',title,status:statuses[category],priority,client,project,category,scheduled};const body='---\n'+Object.entries(metadata).map(([k,v])=>k+': '+JSON.stringify(v)).join('\n')+'\n---\n'+template[1].replace(/^# .+$/m,()=>'# '+title).replace(/^- Category:.*$/m,()=>'- Category: '+category).replace(/^- DoD:.*$/m,()=>'- DoD:').replace(/^- Deadline:.*$/m,()=>'- Deadline:'+(scheduled?' '+scheduled:''))+'\n';const result=await fetch(new URL('.task-create/'+(page+'.md').split('/').map(encodeURIComponent).join('/'),document.baseURI),{method:'PUT',credentials:'same-origin',redirect:'error',signal:AbortSignal.timeout(15000),headers:{'Content-Type':'text/markdown; charset=utf-8','X-Sync-Mode':'true','If-None-Match':'*',...await createHeaders()},body});if(result.status===412)throw new Error('Zadanie już istnieje. Zmień tytuł.');if(!result.ok||!result.headers.has('X-Last-Modified'))throw new Error('Nie potwierdzono utworzenia zadania (HTTP '+result.status+').');return {page};}
  async function done(){return await call('tasks/done');}
  function stopPolling(){if(poll)clearInterval(poll);poll=null;}
  window.addEventListener('online',()=>sync().catch(e=>notice(e.message)));window.addEventListener('pagehide',stopPolling);window.addEventListener('pageshow',()=>{if(io&&!poll)connect(io,changeHook);});
  return {connect,configure,snapshot,sync,dispatch,beforeCompletion,identityEdit,completionWithLifecycle,taskMeta,preferences,preference,today,elapsed,duration,daysFor,getDraft,saveDraft,timeCorrection,previewFor,preparePreview,approvePreview,refreshWorkbook,selectRun,selectedRun,createTask,done,stopPolling};
})();
