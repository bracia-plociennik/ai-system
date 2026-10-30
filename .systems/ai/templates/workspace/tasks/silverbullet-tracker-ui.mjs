// Embedded into the task panel module. Private offline data uses native Space storage.
export const tracker = (() => {
  const api = '.task-tracker/api/v1/';
  const deviceKey = 'silverbullet-tracker-device-v1';
  let device;try{device=localStorage.getItem(deviceKey);}catch{}
  if (!device) { device = crypto.randomUUID(); try{localStorage.setItem(deviceKey, device);}catch{} }
  let io, state = {version:0,runs:[],entities:[]}, token='', online=false, pending=[];
  let busy=false, synchronizing=null, listeners=new Set(), selected=null, cachedFingerprint='';
  const drafts=new Map();
  const uuid=()=>crypto.randomUUID();
  const clone=value=>JSON.parse(JSON.stringify(value));
  const fieldStyle='font:inherit;min-height:44px;max-width:100%;padding:.4em;background:#fff;color:#111827;border:1px solid #999;border-radius:5px;box-sizing:border-box';
  const node=(tag,text,attrs={})=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;for(const[k,v]of Object.entries(attrs))n.setAttribute(k,v);return n;};
  const button=(text,fn)=>{const b=node('button',text,{type:'button'});b.style.cssText=fieldStyle+';cursor:pointer';b.addEventListener('click',async()=>{b.disabled=true;try{await fn();}catch(e){notice(e.message);}finally{b.disabled=false;}});return b;};
  let message='';
  function notice(value){message=String(value||'');notify();}
  function notify(){for(const fn of [...listeners])fn();}
  const clock=value=>new Date(value).toLocaleString('pl-PL',{timeZone:'Europe/Warsaw'});
  const day=value=>new Intl.DateTimeFormat('en-CA',{timeZone:'Europe/Warsaw',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date(value));
  const elapsed=run=>run.segments.reduce((sum,s)=>sum+Math.max(0,Math.floor((new Date(s.end||Date.now())-new Date(s.start))/1000)),0);
  const duration=seconds=>`${Math.floor(seconds/3600)}:${String(Math.floor(seconds%3600/60)).padStart(2,'0')}:${String(seconds%60).padStart(2,'0')}`;
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
    if(!response.ok){const error=new Error(result.error||'Nie udało się zapisać.');error.code=result.error;error.http=response.status;throw error;}
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
          if(e.http===409&&['stale-state','pause-current-timer-first','run-not-open','run-not-paused'].includes(e.code)){
            await write(ackPath(device,event.operation_id),{status:'rejected',error:e.code},'tracker-ack');await refresh();throw new Error('Stan zmienił się na innym urządzeniu. Odświeżono go — ponów operację.');
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
  function controlMessage(){return online?(pending.length?'Oczekuje na synchronizację':'Stan potwierdzony przez serwer'):'Offline — zdarzenia są zapisywane lokalnie';}
  function daysFor(run){
    const values={};for(const s of run.segments||[]){let cursor=new Date(s.start).getTime(),end=new Date(s.end||Date.now()).getTime();if(end-cursor>366*86400000)continue;while(cursor<end){const d=day(cursor);let lo=cursor,hi=Math.min(end,cursor+27*3600000);if(day(hi)!==d){while(hi-lo>1){const mid=Math.floor((hi+lo)/2);if(day(mid)===d)lo=mid;else hi=mid;}}const until=hi;values[d]=(values[d]||0)+Math.max(0,Math.floor((until-cursor)/1000));cursor=until;}if(end===new Date(s.start).getTime())values[day(end)]=0;}
    if(!Object.keys(values).length)values[day(new Date().toISOString())]=null;return values;
  }
  async function review(host,run,page,meta){
    const saved=drafts.get(run.id)||await read(draftPath(run.id))||{};drafts.set(run.id,saved);
    const box=node('section');box.className='tracker-wep-review';box.style.cssText='border:1px solid #999;border-radius:6px;padding:.7em;display:grid;gap:.6em';
    box.append(node('strong',run.review||run.state==='conflict'?'Rozstrzygnij konflikt czasu':'Szkic WEP — '+duration(elapsed(run))));
    if(run.events?.length){const details=node('details'),summary=node('summary','Zapisane zdarzenia');details.append(summary);for(const event of run.events)details.append(node('div',event.action+' · '+clock(event.occurred_at)+' · '+event.device_id.slice(0,8)));box.append(details);}
    const outcome=node('textarea',undefined,{'aria-label':'Wynik pracy WEP',placeholder:'Co zostało zrobione i jaki jest rezultat?'});outcome.style.cssText=fieldStyle;outcome.value=saved.outcome||'';
    const client=node('select',undefined,{'aria-label':'Klient WEP'}),project=node('select',undefined,{'aria-label':'Projekt WEP'});client.style.cssText=project.style.cssText=fieldStyle;
    const entities=state.entities||[];const match=(kind,value)=>entities.find(e=>e.kind===kind&&[e.id,...e.aliases].some(a=>String(a).toLowerCase()===String(value||'').toLowerCase()))?.id||'';
    client.append(node('option','Bez przypisania',{value:''}));for(const e of entities.filter(e=>e.kind==='client'))client.append(node('option',e.aliases[0]||e.id,{value:e.id}));client.value=saved.client_id??match('client',meta.client);
    const projects=()=>{project.replaceChildren(node('option','Bez przypisania',{value:''}));for(const e of entities.filter(e=>e.kind==='project'&&(!e.parent_id||e.parent_id===client.value)))project.append(node('option',e.aliases[0]||e.id,{value:e.id}));project.value=saved.project_id??match('project',meta.project);};projects();client.addEventListener('change',()=>{saved.project_id='';projects();});
    const unassigned=node('input',undefined,{type:'checkbox','aria-label':'Potwierdzam brak przypisania'});unassigned.checked=saved.unassigned_confirmed===true;const unassignedLabel=node('label',' Potwierdzam zapis bez nieuzupełnionego klienta/projektu');unassignedLabel.prepend(unassigned);
    const correction=node('input',undefined,{type:'checkbox','aria-label':'Popraw czas pracy'});correction.checked=saved.correct===true||!!run.review||run.state==='conflict';const correctionLabel=node('label',' Popraw czas pracy');correctionLabel.prepend(correction);
    const timeBox=node('div');timeBox.style.cssText='display:grid;gap:.3em';const dayInputs={};
    const addDay=(date,seconds)=>{if(dayInputs[date])return;const label=node('label',date+' — minuty pracy: '),input=node('input',undefined,{type:'number',min:'0',step:'0.01','aria-label':'Minuty pracy '+date});input.style.cssText=fieldStyle;input.value=saved.days?.[date]??(seconds===null?'':String(seconds/60));dayInputs[date]=input;label.append(input);timeBox.append(label);};for(const [date,seconds]of Object.entries({...Object.fromEntries(Object.keys(saved.days||{}).map(d=>[d,null])),...daysFor(run)}))addDay(date,seconds);
    const additionalDay=node('input',undefined,{type:'date','aria-label':'Dodaj dzień korekty'});additionalDay.style.cssText=fieldStyle;timeBox.append(additionalDay,button('Dodaj dzień korekty',()=>{if(!/^\d{4}-\d{2}-\d{2}$/.test(additionalDay.value))throw new Error('Wybierz dzień korekty.');addDay(additionalDay.value,null);}));
    const reason=node('textarea',undefined,{'aria-label':'Powód korekty czasu',placeholder:'Dlaczego zmieniasz zarejestrowany czas?'});reason.style.cssText=fieldStyle;reason.value=saved.reason||'';timeBox.append(reason);timeBox.hidden=!correction.checked;correction.addEventListener('change',()=>{timeBox.hidden=!correction.checked;});
    const confirmation=node('input',undefined,{type:'checkbox','aria-label':'Potwierdzam rzeczywisty czas pracy'});confirmation.checked=saved.time_confirmed===true;const confirmationLabel=node('label',' Potwierdzam, że ten czas dotyczy mojej rzeczywistej pracy');confirmationLabel.prepend(confirmation);
    const result=node('div');result.setAttribute('role','status');
    let preview=null;
    const correctionValue=()=>{const values={};for(const [d,input]of Object.entries(dayInputs)){if(input.value===''||!Number.isFinite(Number(input.value))||Number(input.value)<0)throw new Error('Uzupełnij poprawny czas dla każdego dnia; zero wpisz jawnie.');values[d]=Math.round(Number(input.value)*60);}if(!reason.value.trim())throw new Error('Podaj powód korekty czasu.');return values;};
    const snapshot=()=>{const value={outcome:outcome.value,client_id:client.value,project_id:project.value,unassigned_confirmed:unassigned.checked,correct:correction.checked,reason:reason.value,time_confirmed:confirmation.checked,days:Object.fromEntries(Object.entries(dayInputs).map(([d,i])=>[d,i.value]))};drafts.set(run.id,value);return value;};const save=async()=>write(draftPath(run.id),snapshot(),'tracker-draft');
    let timer;box.addEventListener('input',()=>{snapshot();preview=null;approve.disabled=true;clearTimeout(timer);timer=setTimeout(()=>save().catch(()=>{}),300);});
    const approve=button('Zatwierdź wpis WEP',async()=>{if(!preview)return;if(!online||pending.length)throw new Error('Najpierw zsynchronizuj zdarzenia.');const value=await call('wep/approve',{preview_id:preview.preview_id,preview_hash:preview.preview_hash});result.textContent=value.xlsx_status==='current'?'Wpis WEP zatwierdzony. Arkusz zaktualizowany.':'Wpis WEP zatwierdzony. Arkusz oczekuje na odświeżenie.';preview=null;await refresh();});approve.disabled=true;
    const prepare=button('Przygotuj podgląd WEP',async()=>{
      await save();if(!online||pending.length)throw new Error('Zatwierdzanie wymaga połączenia i synchronizacji.');
      const payload={run_id:run.id,outcome:outcome.value,client_id:client.value||null,project_id:project.value||null,unassigned_confirmed:unassigned.checked,time_confirmed:confirmation.checked};if(correction.checked){payload.correction=correctionValue();payload.reason=reason.value;}
      preview=await call('wep/preview',payload);result.replaceChildren();const overview=node('div');overview.textContent=`Do WEP: ${duration(preview.total_seconds)} · ${preview.pieces.length} odcinków · ${preview.status}. ${preview.correction?'Korekta zachowana wraz z oryginałem.':''}`;result.append(overview);for(const piece of preview.pieces)result.append(node('div',piece.day+' · '+(piece.start?clock(piece.start)+' → '+clock(piece.end)+' · ':'')+duration(piece.seconds)+' · '+(piece.basis==='measured'?'pomiar online':'czas potwierdzony przez właściciela')));const evidence=node('details');evidence.append(node('summary','Dowód i powiązanie wpisu'),node('pre',JSON.stringify({task_ref:preview.task_ref,task_work_id:preview.task_work_id,evidence:preview.evidence},null,2)));result.append(evidence);approve.disabled=false;
    });
    box.append(outcome,client,project,unassignedLabel,correctionLabel,timeBox,confirmationLabel);
    if(run.review||run.state==='conflict'){
      box.append(button('Potwierdź rozstrzygnięcie czasu',async()=>{await save();if(!online)throw new Error('Rozstrzyganie wymaga połączenia.');await dispatch('resolve',page,{run_id:run.id,correction:correctionValue(),reason:reason.value});host.dataset.run='';notify();}),button('Wyłącz tę sesję z WEP',async()=>{if(!reason.value.trim())throw new Error('Podaj powód wyłączenia.');await dispatch('discard',page,{run_id:run.id,reason:reason.value});host.dataset.run='';notify();}));
    }else box.append(prepare,approve);
    box.append(result,button('Zamknij szkic',async()=>{await save();selected=null;host.replaceChildren();host.dataset.run='';}));host.replaceChildren(box);host.dataset.run=run.id;
  }
  function controls(page,text,callback,onNavigate){
    configure(callback);let meta=taskMeta(text);const wrap=node('div');wrap.className='sb-task-tracker';wrap.style.cssText='display:grid;gap:.6em;padding:.7em 0';
    const bar=node('div'),history=node('div'),reviewHost=node('div'),noticeNode=node('div');noticeNode.setAttribute('role','status');bar.style.cssText='display:flex;flex-wrap:wrap;align-items:center;gap:.4em';wrap.append(bar,noticeNode,history,reviewHost);
    const act=action=>async()=>{const receipt=await dispatch(action,page);meta=taskMeta(String(await native('current',{page})));return receipt;};
    function render(){
      if(!wrap.isConnected)return;
      const current=view(),own=current.runs.find(r=>r.task_id===meta.task_id&&['active','paused'].includes(r.state));bar.replaceChildren(node('strong','Timer'));
      if(!own)bar.append(button('Start',act('start')));
      else{bar.append(node('span',duration(elapsed(own))));bar.append(button(own.state==='active'?'Pauza':'Wznów',act(own.state==='active'?'pause':'resume')),button('Stop',act('stop')));}
      noticeNode.textContent=[controlMessage(),message].filter(Boolean).join(' · ');history.replaceChildren();
      for(const run of current.runs.filter(r=>r.task_id===meta.task_id&&['stopped','conflict'].includes(r.state)&&!r.receipt))history.append(button((run.review||run.state==='conflict'?'Rozstrzygnij czas':'Otwórz szkic WEP')+' · '+clock(run.created||run.segments[0]?.start||new Date().toISOString()),async()=>{selected=run.id;reviewHost.dataset.run='';notify();}));
      for(const run of current.runs.filter(r=>r.task_id===meta.task_id&&r.receipt)){const row=node('div','WEP: zatwierdzono');if(run.receipt.xlsx_status==='pending')row.append(button('Odśwież arkusz',async()=>{await call('wep/refresh',{preview_id:run.receipt.preview_id});await refresh();}));history.append(row);}
      const chosen=current.runs.find(r=>r.id===selected&&r.task_id===meta.task_id);
      if(chosen&&!chosen.receipt&&reviewHost.dataset.run!==chosen.id){reviewHost.dataset.run=chosen.id;review(reviewHost,chosen,page,meta).catch(e=>notice(e.message));}
      if(chosen?.receipt){reviewHost.replaceChildren();reviewHost.dataset.run='';}
    }
    listeners.add(render);requestAnimationFrame(()=>{render();sync().catch(e=>notice(e.message));});
    const timer=setInterval(()=>{if(!wrap.isConnected){clearInterval(timer);listeners.delete(render);return;}render();},1000);return wrap;
  }
  function summary(callback,onNavigate){
    configure(callback);const wrap=node('div');wrap.className='sb-tracker-summary';wrap.style.cssText='display:grid;gap:.3em;margin:.5em 0';
    function render(){if(!wrap.isConnected)return;const current=view(),active=current.runs.find(r=>r.state==='active');wrap.replaceChildren();if(active){wrap.append(node('strong','Trwa pomiar: '+duration(elapsed(active))),button(active.path.split('/').pop()||'Otwórz zadanie',()=>onNavigate(active.path.replace(/\.md$/,''))));}
      const conflicts=current.runs.filter(r=>r.review||r.state==='conflict');for(const run of conflicts)wrap.append(button('Konflikt czasu — otwórz zadanie',()=>onNavigate(run.path.replace(/\.md$/,''))));if(!online||pending.length)wrap.append(node('small',controlMessage()));}
    listeners.add(render);requestAnimationFrame(()=>{render();sync().catch(()=>{});});const timer=setInterval(()=>{if(!wrap.isConnected){clearInterval(timer);listeners.delete(render);return;}sync().catch(()=>{});render();},5000);return wrap;
  }
  window.addEventListener('online',()=>sync().catch(e=>notice(e.message)));
  return {controls,summary,identityEdit,completionWithLifecycle,beforeCompletion,createHeaders,taskMeta,patchFields,edit,configure,sync,dispatch};
})();
