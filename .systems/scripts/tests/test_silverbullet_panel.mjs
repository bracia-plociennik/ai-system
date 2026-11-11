import assert from 'node:assert/strict';
import {panelToday,panelDate,panelRows,panelSelect,panelCompare} from '../../ai/templates/workspace/tasks/silverbullet-panel-ui.mjs';
assert.equal(panelToday(new Date('2026-10-24T22:30:00Z')),'2026-10-25');
assert.equal(panelToday(new Date('2026-10-25T23:30:00Z')),'2026-10-26');
assert.equal(panelDate('2026-02-30'),'');assert.equal(panelDate('2026-02-28'),'2026-02-28');
const rows=panelRows([
{name:'today',category:'DO',status:'open',scheduled:'2026-11-11',clientValue:'',projectValue:''},
{name:'past',category:'do',status:'open',scheduled:'2026-11-10'},
{name:'future',category:'defer',status:'planned',scheduled:'2026-11-12'},
{name:'done',category:'do',status:'done',scheduled:'2026-11-11'},
{name:'cancel',category:'delete',status:'cancelled',scheduled:'2026-11-11'},
{name:'bad',category:'dump',status:'open',scheduled:'2026-02-30'},
{name:'unknown',category:'legacy',status:'open'},
]);
assert.deepEqual(panelSelect(rows,'daily',false,'2026-11-11').map(r=>r.name),['today']);
assert.deepEqual(panelSelect(rows,'daily',true,'2026-11-11').map(r=>r.name),['today','done']);
assert.deepEqual(panelSelect(rows,'due',false,'2026-11-11').map(r=>r.name),['past','future']);
assert.deepEqual(panelSelect(rows,'done').map(r=>r.name),['done']);
assert.equal(panelSelect(rows,'all').length,6);assert.equal(panelSelect(rows,'all',true).length,7);
const human={name:'z',title:'Z',author:'human',completed:false,priority:'normal',scheduled:''};
const ai={...human,name:'a',title:'A',author:'ai',priority:'high'};
assert(panelCompare(human,ai)<0);assert(panelCompare(human,ai,'importance')>0);
assert.equal(rows[0].client,'');assert.equal(rows[6].category,'unassigned');
console.log('Panel date, filter, identity projection and sort contract: passed');
