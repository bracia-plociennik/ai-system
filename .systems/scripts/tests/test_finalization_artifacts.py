import sys,tempfile,unittest,json,copy
from pathlib import Path
from datetime import date,datetime
from unittest.mock import patch
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import personal_ops_drafts as d
import personal_ops_v4 as v
from finalization_artifacts import document,finalize_spor,spor_candidate,resume_spor
from finalization_support import sha

class DocumentTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.p={'format':'csv','path':'export.csv','columns':['zadanie','opis'],'rows':[['Polski tekst','UNKNOWN, nie zero'],['Wielowierszowy','a\nb']],'body':''}
 def test_csv_preview_write_readback(self):
  self.assertEqual(document(self.root,self.p)['status'],'preview');self.assertFalse((self.root/'export.csv').exists())
  r=document(self.root,self.p,apply=True,approved=True);self.assertEqual(r['sha256'],sha(self.root/'export.csv'))
  with self.assertRaises(ValueError):document(self.root,self.p,apply=True,approved=True)
 def test_bad_shape_and_missing_scope(self):
  with self.assertRaises(ValueError):document(self.root,self.p,apply=True)
  self.p['rows']=[['short']]
  with self.assertRaises(ValueError):document(self.root,self.p)
 def test_markdown_and_escape(self):
  self.p.update(format='markdown',columns=[],rows=[],body='# Wynik\n\nUNKNOWN\n',path='report.md')
  document(self.root,self.p,apply=True,approved=True);self.assertEqual((self.root/'report.md').read_text(),self.p['body'])
  self.p['path']='../escape'
  with self.assertRaises(ValueError):document(self.root,self.p)

class SporTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.ws=Path(self.tmp.name)/'fixture';self.ws.mkdir()
  self.index=patch.object(v,'load_current_records',return_value=[]);self.index.start();self.addCleanup(self.index.stop)
 def request(self,weekly=False):
  day=date(2026,10,31) if weekly else date(2026,10,26);kind='weekly' if weekly else 'daily'
  fields={key:'Nieznane — pytanie: UNKNOWN — uzupełnij' for key in d.form(kind)}
  payload={'contract':d.CONTRACT,'proposal_id':d.identity(self.ws,day)['proposal_id'],'fields':fields,'sources':['status.md']}
  with patch('personal_ops_spor_proposals.prepare',return_value={'status':'ready'}):
   saved=d.create(self.ws,day,payload,clock=lambda:datetime.combine(day,datetime.min.time(),tzinfo=d.ZONE))
  p={key:'' for key in v.required_schema(kind)}
  for key in p:
   if key.endswith('_json'):p[key]='[]' if key in ('planned_items_json','future_plan_items_json','daily_blocks_json','owner_overrides_json','osnr_checkpoints_json','task_generation_references_json') else '{}'
  p.update(index_contract=4,schema_version=4,artifact_kind=kind,private_index_policy='detailed-private',privacy='private-sensitive',task_generation_policy='commitment-first-6d-v1',task_generation_status='not-requested')
  if weekly:p.update(report_id='2026-W44',review_week_start='2026-10-26',review_week_end='2026-11-01',plan_week_start='2026-11-02',plan_week_end='2026-11-06')
  else:p.update(report_id='2026-10-26',session_date='2026-10-26',closure_date='2026-10-25',review_window_start='2026-10-23',review_window_end='2026-10-25',review_window_kind='weekend')
  return {'date':str(day),'draft_sha256':saved['sha256'],'fields':{},'properties':p,'confirmed_properties':[],'owner_reference':'synthetic-owner-reply'}
 def hooks(self,calls,fail=None):
  def hook(name):
   def call(path,fingerprint):
    calls.append(name)
    if name==fail:raise RuntimeError('synthetic failure')
    return {'status':'verified','source_sha256':fingerprint}
   return call
  return {x:hook(x) for x in ('indexes','renderer','tasks','calendar')}
 def test_daily_preview_is_pure_and_unknown_preserved(self):
  r=self.request();c=spor_candidate(self.ws,r);self.assertIn('UNKNOWN',c['body']);self.assertIn('f001',d.read(self.ws,date.fromisoformat(r['date']))['body']);self.assertFalse((self.ws/c['path']).exists())
  self.assertEqual(finalize_spor(self.ws,r)['required_stages'],['indexes','renderer'])
 def test_weekly_capture_and_receipt(self):
  r=self.request(True);calls=[];result=finalize_spor(self.ws,r,apply=True,approved=True,hooks=self.hooks(calls))
  self.assertEqual(result['status'],'finalized');self.assertEqual(calls,['indexes','renderer']);self.assertEqual(d.read(self.ws,date(2026,10,31))['metadata']['status'],'approved')
 def test_no_side_effect_without_approval_or_adapter(self):
  r=self.request()
  with self.assertRaises(ValueError):finalize_spor(self.ws,r,apply=True)
  with self.assertRaises(ValueError):finalize_spor(self.ws,r,apply=True,approved=True,integrations=('calendar',),hooks={})
  self.assertFalse((self.ws/'personal-ops/check-ins-v4').exists())
 def test_stale_draft_rejected(self):
  r=self.request();r['draft_sha256']='0'*64
  with self.assertRaises(ValueError):finalize_spor(self.ws,r)
 def test_overlap_before_write_and_single_day_count_once(self):
  r=self.request();p=r['properties'];p['review_process_json']=json.dumps({'finance':{'by_date':{'2026-10-25':50}}});r['confirmed_properties']=['review_process_json']
  self.assertIn('50',spor_candidate(self.ws,r)['body'])
  p['previous_day_finance_amount']=50;r['confirmed_properties'].append('previous_day_finance_amount')
  with self.assertRaisesRegex(ValueError,'overlapping'):spor_candidate(self.ws,r)
  self.assertFalse((self.ws/'personal-ops/check-ins-v4').exists())
 def test_unconfirmed_plan_not_promoted(self):
  r=self.request();r['properties']['planned_items_json']='[{"id":"invented","title":"AI proposal"}]'
  with self.assertRaisesRegex(ValueError,'Unconfirmed plan'):spor_candidate(self.ws,r)
 def test_failure_durable_and_explicit_recovery_without_replay(self):
  r=self.request();calls=[];hooks=self.hooks(calls,fail='calendar')
  result=finalize_spor(self.ws,r,apply=True,approved=True,integrations=('calendar',),hooks=hooks)
  self.assertEqual(result['status'],'partial');self.assertTrue((self.ws/result['path']).exists())
  self.assertEqual(d.read(self.ws,date(2026,10,26))['metadata']['status'],'draft')
  before=list(calls);reads=[]
  checks=self.hooks(reads)
  recovered=resume_spor(self.ws,r,result,approved=True,integrations=('calendar',),hooks=self.hooks(calls),completed_checks={**{x:checks[x] for x in ('indexes','renderer')},'calendar':lambda p,h:{'status':'not-applied','source_sha256':h}})
  self.assertEqual(recovered['status'],'finalized');self.assertEqual(calls[len(before):],['calendar']);self.assertEqual(reads,['indexes','renderer'])
 def test_recovery_cannot_drop_required_calendar(self):
  r=self.request();calls=[];receipt=finalize_spor(self.ws,r,apply=True,approved=True,integrations=('calendar',),hooks=self.hooks(calls,fail='calendar'))
  before=list(calls)
  with self.assertRaisesRegex(ValueError,'scope'):resume_spor(self.ws,r,receipt,approved=True,hooks=self.hooks(calls))
  self.assertEqual(calls,before);self.assertEqual(d.read(self.ws,date(2026,10,26))['metadata']['status'],'draft')
 def test_completed_tasks_never_replayed_when_check_missing(self):
  r=self.request();calls=[];receipt=finalize_spor(self.ws,r,apply=True,approved=True,integrations=('tasks','calendar'),hooks=self.hooks(calls,fail='calendar'));before=list(calls)
  checks=self.hooks([])
  result=resume_spor(self.ws,r,receipt,approved=True,integrations=('tasks','calendar'),hooks=self.hooks(calls),completed_checks={x:checks[x] for x in ('indexes','renderer')})
  self.assertEqual(result['status'],'partial');self.assertEqual(result['next_step'],'tasks');self.assertEqual(calls,before)
  self.assertEqual(result['completed'],receipt['completed'])
  again=resume_spor(self.ws,r,result,approved=True,integrations=('tasks','calendar'),hooks=self.hooks(calls))
  self.assertEqual(again['status'],'partial');self.assertEqual(calls,before)
 def test_duplicate_integration_rejected_before_any_write(self):
  r=self.request();calls=[]
  with self.assertRaisesRegex(ValueError,'Duplicate'):finalize_spor(self.ws,r,apply=True,approved=True,integrations=('calendar','calendar'),hooks=self.hooks(calls))
  self.assertEqual(calls,[]);self.assertFalse((self.ws/'personal-ops/check-ins-v4').exists())
 def test_duplicate_recovery_integration_rejected(self):
  r=self.request();calls=[];receipt=finalize_spor(self.ws,r,apply=True,approved=True,integrations=('calendar',),hooks=self.hooks(calls,fail='calendar'));before=list(calls)
  with self.assertRaisesRegex(ValueError,'Duplicate'):resume_spor(self.ws,r,receipt,approved=True,integrations=('calendar','calendar'),hooks=self.hooks(calls))
  self.assertEqual(calls,before)
 def test_failed_attempt_needs_negative_readback_before_retry(self):
  r=self.request();calls=[];receipt=finalize_spor(self.ws,r,apply=True,approved=True,integrations=('calendar',),hooks=self.hooks(calls,fail='calendar'));before=list(calls);checks=self.hooks([])
  result=resume_spor(self.ws,r,receipt,approved=True,integrations=('calendar',),hooks=self.hooks(calls),completed_checks={x:checks[x] for x in ('indexes','renderer')})
  self.assertEqual(result['next_step'],'calendar');self.assertEqual(calls,before)
 def test_lost_success_can_be_confirmed_without_replay(self):
  r=self.request();calls=[];receipt=finalize_spor(self.ws,r,apply=True,approved=True,integrations=('calendar',),hooks=self.hooks(calls,fail='calendar'));before=list(calls);reads=[]
  result=resume_spor(self.ws,r,receipt,approved=True,integrations=('calendar',),hooks=self.hooks(calls),completed_checks=self.hooks(reads))
  self.assertEqual(result['status'],'finalized');self.assertEqual(calls,before);self.assertEqual(reads,['indexes','renderer','calendar'])
 def test_negative_readback_cannot_undo_completed_stage(self):
  r=self.request();calls=[];receipt=finalize_spor(self.ws,r,apply=True,approved=True,hooks=self.hooks(calls,fail='renderer'));before=list(calls)
  result=resume_spor(self.ws,r,receipt,approved=True,hooks=self.hooks(calls),completed_checks={'indexes':lambda p,h:{'status':'not-applied','source_sha256':h}})
  self.assertEqual(result['status'],'partial');self.assertEqual(calls,before)
 def test_answer_patch_preserves_manual_text(self):
  r=self.request();day=date.fromisoformat(r['date']);saved=d.read(self.ws,day)
  path=self.ws/saved['path'];path.write_text(path.read_text()+'\nManual owner note: preserve me.\n')
  r['draft_sha256']=d.read(self.ws,day)['sha256'];r['fields']={'f001':'Potwierdzone: owner answer'}
  result=spor_candidate(self.ws,r)
  self.assertIn('Potwierdzone: owner answer',result['body']);self.assertIn('Manual owner note: preserve me.',result['body'])
 def test_broken_field_structure_blocks_before_write(self):
  r=self.request();day=date.fromisoformat(r['date']);saved=d.read(self.ws,day);path=self.ws/saved['path']
  path.write_text(path.read_text().replace('<!-- spor-field:f001 -->','<!-- spor-field:f002 -->',1))
  r['draft_sha256']=d.read(self.ws,day)['sha256']
  with self.assertRaisesRegex(ValueError,'field structure'):spor_candidate(self.ws,r)
 def test_failed_recovery_readback_returns_partial_without_replay(self):
  r=self.request();calls=[];result=finalize_spor(self.ws,r,apply=True,approved=True,hooks=self.hooks(calls,fail='renderer'))
  def broken(p,h):raise OSError('unavailable readback')
  recovered=resume_spor(self.ws,r,result,approved=True,hooks=self.hooks(calls),completed_checks={'indexes':broken})
  self.assertEqual(recovered['status'],'partial');self.assertEqual(calls,['indexes','renderer'])
 def test_uncertain_recovery_never_replays(self):
  r=self.request();calls=[];result=finalize_spor(self.ws,r,apply=True,approved=True,hooks=self.hooks(calls,fail='renderer'))
  recovered=resume_spor(self.ws,r,result,approved=True,hooks=self.hooks(calls),completed_checks={'indexes':lambda p,h:{'status':'uncertain'}})
  self.assertEqual(recovered['status'],'partial');self.assertEqual(calls,['indexes','renderer'])

if __name__=='__main__':unittest.main()
