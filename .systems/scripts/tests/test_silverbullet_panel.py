"""Read-only task projections and conservative session conflict isolation."""
import json,sys,unittest,uuid
from datetime import timedelta
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from test_silverbullet_tracker import TrackerFixture
from test_silverbullet_tracker_http import HttpTests
from task_store import TaskStore
from silverbullet_tracker import TrackerError

class PanelTests(TrackerFixture,unittest.TestCase):
 def test_done_read_only_unknown_dates_and_identity_conflict(self):
  self.task.write_text(self.task.read_text().replace('status: open','status: done'))
  legacy=self.task.with_name('Legacy.md');legacy.write_text('---\ntype: task\nstatus: done\n---\nUnknown dates\n')
  copy=self.task.with_name('Task.conflicted-test.md');copy.write_bytes(self.task.read_bytes())
  before={p:p.read_bytes() for p in self.vault.rglob('*.md')};data=self.tracker.store.completed()
  self.assertEqual(len(data['tasks']),3);self.assertEqual(data['identity_conflicts'],2);self.assertFalse(data['writes'])
  self.assertTrue(all(t['completed_at'] is None and t['wep_approval_status']=='not_checked' for t in data['tasks']))
  self.assertEqual({p:p.read_bytes() for p in before},before)
 def test_done_malformed_scalar_metadata_cannot_break_projection(self):
  self.task.write_text('---\ntype: task\nstatus: done\ntask_id: ["bad"]\nauthor: ["ai"]\ncompleted_at: ["date"]\n---\nNotes\n')
  row=self.tracker.store.completed()['tasks'][0]
  self.assertIsNone(row['task_id']);self.assertIsNone(row['completed_at']);self.assertEqual(row['identity_status'],'missing-or-invalid')
 def test_current_navigation_uses_uuid_and_reports_missing_or_duplicates(self):
  self.stopped();new=self.task.with_name('Renamed.md');self.task.rename(new)
  run=self.tracker.state()['runs'][0];self.assertTrue(run['path'].endswith('Renamed.md'));self.assertFalse(run.get('context_error'))
  copy=new.with_name('Copy.md');copy.write_bytes(new.read_bytes());self.assertTrue(self.tracker.state()['runs'][0]['context_error'])
  new.unlink();copy.unlink();self.assertTrue(self.tracker.state()['runs'][0]['context_error'])
 def test_disjoint_measured_day_does_not_block_clean_preview(self):
  self.stopped();self.time+=timedelta(days=2);other=str(uuid.uuid4());self.event('start',other,self.other_id);self.time+=timedelta(minutes=1);self.event('stop',other,self.other_id)
  with self.tracker.db() as db:db.execute('UPDATE runs SET review=1 WHERE id=?',(other,))
  self.assertEqual(self.preview()['total_seconds'],600)
 def test_same_day_review_blocks(self):
  self.stopped();other=str(uuid.uuid4());self.event('start',other,self.other_id);self.time+=timedelta(minutes=1);self.event('stop',other,self.other_id)
  with self.tracker.db() as db:db.execute('UPDATE runs SET review=1 WHERE id=?',(other,))
  with self.assertRaisesRegex(TrackerError,'resolve-time-conflicts'):self.preview()
 def test_unknown_offline_day_and_active_review_remain_global(self):
  self.stopped();self.time+=timedelta(days=2);other=str(uuid.uuid4());self.event('start',other,self.other_id)
  with self.tracker.db() as db:db.execute('UPDATE runs SET review=1 WHERE id=?',(other,))
  with self.assertRaisesRegex(TrackerError,'resolve-time-conflicts'):self.preview()
  self.time+=timedelta(minutes=1);self.event('stop',other,self.other_id,replay=True)
  with self.assertRaisesRegex(TrackerError,'resolve-time-conflicts'):self.preview()
 def test_unconfirmed_replay_event_keeps_hold_even_with_measured_segments(self):
  self.stopped();self.time+=timedelta(days=2);other=str(uuid.uuid4());self.event('start',other,self.other_id);self.time+=timedelta(minutes=1);self.event('stop',other,self.other_id)
  self.event('stop',other,self.other_id,replay=True,version=0)
  with self.assertRaisesRegex(TrackerError,'resolve-time-conflicts'):self.preview()
 def test_measured_clock_anomaly_retains_hold(self):
  self.stopped();self.time+=timedelta(days=2);other=str(uuid.uuid4());self.event('start',other,self.other_id);self.time+=timedelta(minutes=1);self.event('stop',other,self.other_id)
  with self.tracker.db() as db:
   db.execute('UPDATE runs SET review=1 WHERE id=?',(other,))
   row=db.execute('SELECT id,payload FROM events WHERE run_id=? LIMIT 1',(other,)).fetchone();payload=json.loads(row['payload']);payload['occurred_at']='2026-01-01T00:00:00Z';db.execute('UPDATE events SET payload=? WHERE id=?',(json.dumps(payload),row['id']))
  with self.assertRaisesRegex(TrackerError,'resolve-time-conflicts'):self.preview()

class DoneHttpTests(HttpTests):
 def test_done_route_is_authenticated_read_only_no_query(self):
  status,body,_=self.call('GET','tasks/done');self.assertEqual(status,200);self.assertFalse(body['writes'])
  with self.assertRaises(TrackerError):self.call('GET','tasks/done?task_id=other')
  with self.assertRaises(TrackerError):self.app.handle('GET','/.task-tracker/api/v1/tasks/done',{},b'')
