// Strict native-editor patches. No DOM, task snapshots or field rewrites outside the named edit.
const editableCategories=["do","defer","delegate","delete"].map(k=>[k]);
const restoreKey='silverbullet_done_restore';
function scalarStatus(line) {
  const value=line.match(/^(status:[ \t]*)("[a-zA-Z_-]+"|'[a-zA-Z_-]+'|[a-zA-Z_-]+)?([ \t]*(?:#.*)?)$/);
  if(!value)throw new Error('Status ma złożony format YAML. Ustaw prosty status przed zmianą.');
  return {prefix:value[1],raw:value[2]||'',suffix:value[3],value:(value[2]||'').replace(/["']/g,'').toLowerCase()};
}
function completionState(text) {
  const header=text.match(/^(?:\uFEFF)?---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/);
  if(!header)throw new Error('Brak nagłówka YAML zadania.');
  const body=header[1],base=header[0].indexOf(body),closing=header[0].lastIndexOf('\n---')+1;
  const lines=[...body.matchAll(/^.*$/gm)].map(m=>{
    const raw=m[0].replace(/\r$/,'');const start=base+m.index,end=start+raw.length;
    return {raw,start,end,fullEnd:end+(text.slice(end,end+2)==='\r\n'?2:text[end]==='\n'?1:0)};
  });
  const types=lines.filter(l=>/^(?:type|"type"|'type')[ \t]*:/.test(l.raw));
  if(types.length!==1||!/^type:[ \t]*(?:task|"task"|'task')[ \t]*(?:#.*)?$/.test(types[0].raw))throw new Error('Ta strona nie jest jednoznacznym zadaniem type: task.');
  const statuses=lines.filter(l=>/^(?:status|"status"|'status')[ \t]*:/.test(l.raw));
  if(statuses.length>1)throw new Error('Powtórzone pole status. Popraw nagłówek przed zmianą.');
  const status=statuses[0],scalar=status?scalarStatus(status.raw):null;
  const restores=lines.filter(l=>/^(?:silverbullet_done_restore|"silverbullet_done_restore"|'silverbullet_done_restore')[ \t]*:/.test(l.raw));
  if(restores.length>1)throw new Error('Powtórzone metadane cofnięcia DONE.');
  let previous;
  if(restores.length){
    const match=restores[0].raw.match(/^silverbullet_done_restore:[ \t]*(\{.*\})[ \t]*(?:#.*)?$/);
    try{previous=JSON.parse(match?.[1]);}catch{throw new Error('Niepoprawne metadane cofnięcia DONE.');}
    if(!previous||Object.keys(previous).sort().join('|')!=='statusLine|version'||previous.version!==1)throw new Error('Nieobsługiwana wersja metadanych cofnięcia DONE.');
    if(previous.statusLine!==null){
      if(typeof previous.statusLine!=='string'||/[\r\n]/.test(previous.statusLine))throw new Error('Niepoprawny poprzedni status.');
      if(scalarStatus(previous.statusLine).value==='done')throw new Error('Poprzedni status nie może być DONE.');
    }
  }
  const legacyDone=!status&&!restores.length&&/^category:[ \t]*(?:done|"done"|'done')[ \t]*(?:#.*)?$/m.test(body);
  return {lines,body,status,scalar,restore:restores[0],previous,done:scalar?.value==='done'||legacyDone,closing,newline:text.includes('\r\n')?'\r\n':'\n'};
}
function rangeEdit(text,edits) {
  const from=Math.min(...edits.map(e=>e.from)),to=Math.max(...edits.map(e=>e.to));
  let insert=text.slice(from,to);
  for(const e of edits.sort((a,b)=>b.from-a.from))insert=insert.slice(0,e.from-from)+e.insert+insert.slice(e.to-from);
  return {from,to,insert};
}
export function completionEdit(text,action='complete',fallback='') {
  if(!['complete','undo'].includes(action))throw new Error('Nieznana operacja statusu.');
  const state=completionState(text),{status,scalar,restore,previous,closing,newline}=state;
  if((action==='complete'&&state.done)||(action==='undo'&&!state.done))return {unchanged:true};
  const edits=[];
  if(action==='complete'){
    const record=restoreKey+': '+JSON.stringify({version:1,statusLine:status?.raw??null});
    if(status){
      const from=status.start+scalar.prefix.length;
      edits.push({from,to:from+scalar.raw.length,insert:'done'+(!scalar.raw&&scalar.suffix.startsWith('#')?' ':'')});
    }
    if(restore){
      edits.push({from:restore.start,to:restore.end,insert:record});
      if(!status)edits.push({from:closing,to:closing,insert:'status: done'+newline});
    }
    else edits.push({from:closing,to:closing,insert:(!status?'status: done'+newline:'')+record+newline});
  }else if(restore){
    edits.push({from:status.start,to:previous.statusLine===null?status.fullEnd:status.end,insert:previous.statusLine??''});
    edits.push({from:restore.start,to:restore.fullEnd,insert:''});
  }else{
    if(!['open','planned','waiting','cancelled','archived'].includes(fallback))throw new Error('Brak zapisanego poprzedniego statusu. Wybierz status do przywrócenia.');
    if(status){
      const from=status.start+scalar.prefix.length;edits.push({from,to:from+scalar.raw.length,insert:fallback});
    }else edits.push({from:closing,to:closing,insert:'status: '+fallback+newline});
  }
  return rangeEdit(text,edits);
}
function metadataState(text) {
  const state=completionState(text),values={},fields={};
  for(const key of ['category','scheduled']){
    const candidates=state.lines.filter(l=>new RegExp('^(?:'+key+'|"'+key+'"|\''+key+'\')[ \\t]*:').test(l.raw));
    if(candidates.length>1)throw new Error('Powtórzone pole '+key+'.');
    const line=candidates[0];
    if(!line){values[key]='';continue;}
    const match=line.raw.match(new RegExp('^('+key+':[ \\t]*)("(?:[^"\\\\]|\\\\.)*"|\'(?:[^\']|\'\')*\'|[a-zA-Z0-9_:.+\\-]*)([ \\t]*(?:#.*)?)$'));
    if(!match)throw new Error('Pole '+key+' ma złożony format. Nie zmieniam go automatycznie.');
    let value=match[2];
    if(value.startsWith('"')){try{value=JSON.parse(value);}catch{throw new Error('Niepoprawna wartość '+key+'.');}}
    else if(value.startsWith("'"))value=value.slice(1,-1).replaceAll("''", "'");
    values[key]=key==='category'?value.toLowerCase():value;
    fields[key]={line,prefix:match[1],raw:match[2]};
  }
  return {...state,values,fields};
}
function validDay(value) {
  if(!/^\d{4}-\d{2}-\d{2}$/.test(value)||value.startsWith('0000-'))return false;
  const d=new Date(value+'T00:00:00Z');return !Number.isNaN(d.valueOf())&&d.toISOString().slice(0,10)===value;
}
export function metadataEdit(text,request) {
  if(typeof request==='string')request=JSON.parse(request);
  const {changes,expected}=request||{},state=metadataState(text);
  if(!changes||typeof changes!=='object'||!expected||typeof expected!=='object')throw new Error('Brak zakresu zmiany pól.');
  const keys=Object.keys(changes);
  if(!keys.length)return {unchanged:true};
  if(keys.some(k=>!['category','scheduled'].includes(k)))throw new Error('Nieznane pole do zmiany.');
  for(const key of keys){
    if(typeof changes[key]!=='string'||!Object.hasOwn(expected,key)||expected[key]!==state.values[key])throw new Error('Pole '+key+' zmieniło się od otwarcia formularza. Odśwież zadanie i wybierz ponownie.');
  }
  const next={...state.values,...changes};
  if(Object.hasOwn(changes,'category')&&!editableCategories.some(([k])=>k===next.category))throw new Error('Wybierz DO, DEFER, DELEGATE lub DELETE. DAILY wynika z daty, a DUMP można wybrać tylko przy tworzeniu.');
  if(Object.hasOwn(changes,'scheduled')&&next.scheduled&&!validDay(next.scheduled))throw new Error('Wybierz poprawną datę scheduled.');
  const edits=[],insertions=[];
  for(const key of keys){
    const field=state.fields[key],value=JSON.stringify(changes[key]);
    if(field){const from=field.line.start+field.prefix.length;edits.push({from,to:from+field.raw.length,insert:value});}
    else insertions.push(key+': '+value);
  }
  // Preserve completion when reclassifying historical category: done without status.
  if(state.done&&!state.status&&keys.includes('category'))insertions.push('status: done');
  if(insertions.length)edits.push({from:state.closing,to:state.closing,insert:insertions.join(state.newline)+state.newline});
  const header=text.match(/^(?:\uFEFF)?---\r?\n[\s\S]*?\r?\n---(?:\r?\n|$)/)[0],bodyStart=header.length;
  const body=text.slice(bodyStart),firstSection=body.search(/^##(?:\s|$)/m),summaryEnd=firstSection<0?body.length:firstSection;
  for(const [key,label] of [['category','Category'],['scheduled','Deadline']]){
    if(!keys.includes(key))continue;
    const matches=[...body.slice(0,summaryEnd).matchAll(new RegExp('^- '+label+':[^\\r\\n]*','gm'))];
    if(matches.length>1)throw new Error('Powtórzona linia '+label+' w nagłówku zadania.');
    if(matches.length){const m=matches[0],from=bodyStart+m.index;edits.push({from,to:from+m[0].length,insert:'- '+label+':'+(changes[key]?' '+changes[key]:'')});}
  }
  return rangeEdit(text,edits);
}

export function statusInfo(text){const s=completionState(text);return {done:s.done,hasRestore:!!s.restore};}
export function metadataValues(text){return metadataState(text).values;}
export function taskPage(text){try{completionState(text);return true;}catch{return false;}}

export {validDay};
