import importlib.machinery,importlib.util,json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
S=Path(__file__).resolve().parents[1];sys.path.insert(0,str(S))
from task_store import TaskStore,frontmatter,merge_plan,validate_plan

def generator():
 loader=importlib.machinery.SourceFileLoader('silverbullet_generator',str(S/'propose-task-candidates'));spec=importlib.util.spec_from_loader(loader.name,loader);module=importlib.util.module_from_spec(spec);loader.exec_module(module);return module

class StoreTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.w=Path(self.tmp.name)/'personal';(self.w/'tasks/silverbullet/tasks').mkdir(parents=True);self.root=self.w/'tasks/silverbullet';self.config=self.w/'tasks/task-store.local.md';self.configure()
 def configure(self,profile='silverbullet-v1',enabled='true'):
  self.config.write_text(f'---\nschema_version: 1\nenabled: {enabled}\nprofile: {profile}\nvault_path: ${{AI_SYSTEM_WORKSPACE_HOME}}/tasks/silverbullet\n---\n')
 def candidate(self,**values):return dict(title='Prepare fix',client='Customer',project='Product',execution_bucket='do',source_system='ai-system',**values)
 def test_config_resolves_without_cwd_or_environment(self):
  with patch.dict(os.environ,{'AI_SYSTEM_WORKSPACE_HOME':'/wrong'}):s=TaskStore.load(self.w)
  self.assertEqual(s.task_dir,self.root/'tasks')
 def test_explicit_config_cannot_fallback(self):
  for profile,enabled in [('future','true'),('silverbullet-v1','false')]:
   self.configure(profile,enabled)
   with self.assertRaises(ValueError):TaskStore.load(self.w)
 def test_unknown_version_rejected(self):
  self.config.write_text(self.config.read_text().replace('schema_version: 1','schema_version: 2'))
  with self.assertRaises(ValueError):TaskStore.load(self.w)
 def test_legacy_config_still_selects_tasknotes(self):
  self.config.unlink();(self.w/'tasks/TaskNotes/Tasks').mkdir(parents=True);(self.w/'tasks/taskforge-vault.local.md').write_text(f'---\nenabled: true\nvault_path: {self.w}/tasks\n---\n');self.assertEqual(TaskStore.load(self.w).profile,'tasknotes-v1')
 def test_generator_config_prefers_neutral(self):
  g=generator();self.assertEqual(g.selected_task_config(self.w),self.config)
 def test_new_task_matches_ui(self):
  s=TaskStore.load(self.w);files,*_=s.write_candidates([self.candidate(due='2026-10-22T15:00',definition_of_done='Tests pass',tags=['6d/do','AI'],contexts=['x'],projects=['x'])]);p=files[0];text=p.read_text();data=frontmatter(text)
  self.assertEqual(p,self.root/'tasks/Customer/Product/Prepare fix.md');self.assertEqual(data['category'],'do');self.assertEqual(data['scheduled'],'2026-10-22');self.assertEqual(data['source_deadline'],'2026-10-22T15:00');self.assertFalse({'due','tags','contexts','projects'}&data.keys());self.assertIn('# Prepare fix\n- Category: do\n- DoD: Tests pass\n- Deadline: 2026-10-22',text);self.assertIn('## TODO\n- [ ] Prepare fix',text);self.assertIn('## Evidence\n\n## Working dump',text)
 def test_ids_are_created_only_for_real_new_tasks(self):
  import uuid
  s=TaskStore.load(self.w);value=self.candidate(source_session_date='2026-10-30',source_plan_item_id='stable')
  self.assertNotIn('task_id:',s.render(value));files,*_=s.write_candidates([value]);data=frontmatter(files[0].read_text())
  self.assertEqual(str(uuid.UUID(data['task_id'])),data['task_id']);self.assertIn('created_at',data)
  original=files[0].read_bytes();self.assertEqual(s.write_candidates([value])[1],1);self.assertEqual(files[0].read_bytes(),original)
 def test_ai_creator_is_forced_and_dedup_preserves_human_creator(self):
  s=TaskStore.load(self.w);value=self.candidate(source_session_date='2026-11-01',source_plan_item_id='creator')
  files,*_=s.write_candidates([{**value,'author':'human'}]);path=files[0]
  self.assertEqual(frontmatter(path.read_text())['author'],'ai')
  path.write_text(path.read_text().replace('author: "ai"','author: "human"')+'Owner note stays\n')
  before=path.read_bytes();self.assertEqual(s.write_candidates([value])[1],1);self.assertEqual(path.read_bytes(),before)
 def test_five_assignable_categories_match_ui(self):
  s=TaskStore.load(self.w)
  for category in ['do','defer','delegate','delete','dump']:
   value=s.candidate(self.candidate(category=category,scheduled='2026-10-20'));self.assertEqual(value['category'],category)
 def test_daily_input_is_computed_view_not_new_category(self):
  s=TaskStore.load(self.w)
  files,*_=s.write_candidates([self.candidate(category='daily',scheduled='2026-10-20')]);data=frontmatter(files[0].read_text())
  self.assertEqual(data['category'],'do');self.assertEqual(data['scheduled'],'2026-10-20');self.assertEqual(data['status'],'open')
  with self.assertRaises(ValueError):s.candidate(self.candidate(category='daily'))
 def test_done_requires_real_category_and_explicit_status(self):
  s=TaskStore.load(self.w)
  for field in ['category','execution_bucket']:
   value=self.candidate();value[field]='done'
   with self.assertRaisesRegex(ValueError,'done-is-status'):s.write_candidates([value])
  self.assertEqual(list(s.tasks()),[])
  files,*_=s.write_candidates([self.candidate(category='defer',status='done')]);data=frontmatter(files[0].read_text());self.assertEqual(data['category'],'defer');self.assertEqual(data['status'],'done')
 def test_explicit_status_is_independent_from_category(self):
  s=TaskStore.load(self.w)
  for status in ['waiting','archived','blocked','OPEN']:
   data=frontmatter(s.render(self.candidate(category='do',status=status)));self.assertEqual(data['status'],status.lower());self.assertEqual(data['category'],'do')
  for status in ['open\ncategory: done','status: done',{'value':'open'}]:
   with self.assertRaisesRegex(ValueError,'invalid-task-status'):s.candidate(self.candidate(status=status))
 def test_legacy_daily_done_files_remain_unchanged_and_readable(self):
  s=TaskStore.load(self.w)
  for category in ['daily','done']:
   p=s.task_dir/(category+'.md');p.write_text('---\ntype: task\ntitle: Legacy\ncategory: '+category+'\ncustom: untouched\n---\nPrivate note\n');before=p.read_bytes()
   self.assertTrue(any(path==p and meta['category']==category for path,meta in s.tasks()));self.assertEqual(p.read_bytes(),before)
 def test_real_date_validation(self):
  s=TaskStore.load(self.w)
  for value in ['2026-02-31','tomorrow','2026-10-22T99:10']:
   with self.assertRaises(ValueError):s.candidate(self.candidate(scheduled=value))
 def test_source_identity_repeat_preserves_user_edits(self):
  s=TaskStore.load(self.w);value=self.candidate(source_session_date='2026-10-20',source_plan_item_id='build-1');paths,*_=s.write_candidates([value]);p=paths[0];p.write_text(p.read_text()+'Custom user note\n');before=p.read_bytes();self.assertEqual(s.write_candidates([value])[1],1);self.assertEqual(p.read_bytes(),before)
 def test_weekly_identity_and_dream_candidates_independent(self):
  s=TaskStore.load(self.w)
  first=self.candidate(source_week_id='2026-W43',source_week_item_id='item-1');s.write_candidates([first]);self.assertEqual(s.write_candidates([first])[1],1)
  a=self.candidate(source_dream_report='/dream/one.md');a['title']='Idea A';b=dict(a,title='Idea B');self.assertEqual(len(s.write_candidates([a,b])[0]),2);self.assertEqual(s.write_candidates([a,b])[1],2)
 def test_collision_cannot_overwrite_ui_task(self):
  s=TaskStore.load(self.w);s.write_candidates([self.candidate()]);p=s.task_dir/'Customer/Product/Prepare fix.md';before=p.read_bytes()
  with self.assertRaisesRegex(ValueError,'collision'):s.write_candidates([self.candidate()])
  self.assertEqual(p.read_bytes(),before)
 def test_symlink_cannot_escape(self):
  s=TaskStore.load(self.w);outside=self.w/'outside';outside.mkdir();(s.task_dir/'Customer').symlink_to(outside,target_is_directory=True)
  with self.assertRaises(ValueError):s.write_candidates([self.candidate()])
  self.assertEqual(list(outside.iterdir()),[])
 def test_non_tasks_and_attachments_excluded(self):
  (self.root/'tasks/note.md').write_text('# note');(self.root/'tasks/attachments').mkdir();(self.root/'tasks/attachments/private.md').write_text('---\ntype: task\n---\nsecret');self.assertEqual(list(TaskStore.load(self.w).tasks()),[])
 def test_missing_names_and_unsafe_segments(self):
  s=TaskStore.load(self.w);v=self.candidate();v.update(client='',project='',title='../unsafe/path');files,*_=s.write_candidates([v]);self.assertTrue(files[0].is_relative_to(s.task_dir/'bez-klienta/bez-projektu'));self.assertEqual(len(list(s.tasks())),1)
 def test_link_race_no_overwrite(self):
  s=TaskStore.load(self.w);real_link=os.link
  def competing(src,dst,**kw):Path(dst).write_text('UI winner');return real_link(src,dst,**kw)
  with patch('task_store.os.link',competing),self.assertRaisesRegex(ValueError,'collision'):s.write_candidates([self.candidate()])
  self.assertEqual((s.task_dir/'Customer/Product/Prepare fix.md').read_text(),'UI winner');self.assertFalse(list(s.task_dir.rglob('.ai-system-create-*')))
 def test_spor_reads_shared_selected_store_without_private_body(self):
  from personal_ops_spor_proposals import supporting_sources
  s=TaskStore.load(self.w);s.write_candidates([self.candidate()]);company=self.w.parent/'company';(company/'tasks').mkdir(parents=True);(company/'tasks/task-store.local.md').write_text(f'---\nschema_version: 1\nenabled: true\nprofile: silverbullet-v1\nvault_path: {self.root}\n---\n');warnings=[]
  result=supporting_sources(company,None,[{'properties':{'planned_items':[{'mapping':{'client':'Customer','project':'Product'}}]}}],warnings)
  tasks=[r for r in result if r['kind']=='open-task'];self.assertEqual(len(tasks),1);self.assertEqual(tasks[0]['metadata']['project'],'Product');self.assertEqual(tasks[0]['metadata']['category'],'do');self.assertNotIn('Working dump',str(tasks))
 def test_generator_cli_legacy_source_writes_only_silverbullet(self):
  import subprocess
  source=self.w/'2026-10-20.md';source.write_text('# Check-In\n\n## 1. Plan dnia\n### Zbudowałem\nCustomer Product new feature\n### Dowiozłem\n\n### Wypromowałem\n\n## 2. Review\n')
  cmd=[sys.executable,str(S/'propose-task-candidates'),'--workspace',str(self.w),'--check-in',str(source)]
  dry=subprocess.run(cmd+['--json'],capture_output=True,text=True);self.assertEqual(dry.returncode,0,dry.stderr);values=json.loads(dry.stdout);self.assertTrue(values);self.assertTrue(all('category' in c and 'tags' not in c and 'due' not in c for c in values));self.assertEqual(list(TaskStore.load(self.w).tasks()),[])
  actual=subprocess.run(cmd+['--write','--owner-approved'],capture_output=True,text=True);self.assertEqual(actual.returncode,0,actual.stderr);self.assertTrue(list(TaskStore.load(self.w).tasks()));self.assertFalse((self.root/'TaskNotes').exists())
 def test_dreaming_source_covers_future_tasks_owner_only(self):
  from dreaming_config_draft import draft
  from dreaming_universal_sources import inventory,read
  company=self.w.parent/'company';company.mkdir();s=TaskStore.load(self.w);s.write_candidates([self.candidate()])
  value,gaps=draft(str(self.w.parent),('personal',self.w),('company',company),self.w/'system',self.w/'workflow','gpt-test',Path(sys.executable).resolve(),'test-version','current-test-owner-scope')
  source=next(v for v in value['sources'] if v['prefix']=='tasks/silverbullet/tasks');self.assertEqual(source['audiences'],['personal']);self.assertEqual(source['ownership_fields'],{'type':'task'})
  one=inventory(value);self.assertEqual(len(one),1);self.assertIn(b'type: "task"',read(source,one[0]));s.write_candidates([dict(self.candidate(),title='Future task')]);self.assertEqual(len(inventory(value)),2)
 def test_wep_generic_task_role_and_dump_exclusion(self):
  from work_evidence_ledger import source_candidate
  s=TaskStore.load(self.w);paths,*_=s.write_candidates([self.candidate()]);p=paths[0];p.write_text(p.read_text()+'password: synthetic-secret\n');ref={'root_alias':'silverbullet','relative_path':str(p.relative_to(self.root)),'sha256':__import__('hashlib').sha256(p.read_bytes()).hexdigest(),'observed_at':'2026-10-20T08:00:00+02:00','fact_date':'2026-10-20','evidence_level':'local-test'}
  result=source_candidate(ref,{'source_roots':{'silverbullet':str(self.root)}},role='task',fact_date='2026-10-20')
  self.assertEqual(result['source_role'],'task');self.assertFalse(result['canonical_entry_created']);self.assertIsNone(result['duration_seconds']);self.assertNotIn('synthetic-secret',str(result))
 def plan(self,extra=False):
  steps=[{'id':'start','text':'Rozpocząć plan'}]
  if extra:steps.append({'id':'verify','text':'Sprawdzić wynik'})
  steps.append({'id':'finish','text':'Zakończyć: Evidence i rzeczywisty stan WEP'})
  return {'id':'fixture-plan','stages':steps}
 def created(self,plan=False):
  s=TaskStore.load(self.w);v=self.candidate()
  if plan:v['plan']=self.plan()
  files,*_=s.write_candidates([v]);p=files[0];return s,p,frontmatter(p.read_text())['task_id']
 def sha(self,p):return __import__('hashlib').sha256(p.read_bytes()).hexdigest()
 def test_create_complete_plan_and_repeat_preserves_human_edits(self):
  s,p,tid=self.created(True);text=p.read_text();self.assertIn('ai-system-plan:fixture-plan:start',text);self.assertNotIn('- [ ] Prepare fix',text)
  p.write_text(text.replace('author: "ai"','author: "human"')+'Manual note\n');before=p.read_bytes()
  self.assertEqual(s.write_candidates([dict(self.candidate(),plan=self.plan())])[1],1);self.assertEqual(p.read_bytes(),before)
 def test_plan_preview_no_locks_or_writes(self):
  s,p,tid=self.created();lock=s.root/'.ai-system-task-store.lock';lock.unlink();before=p.read_bytes();mtime=p.stat().st_mtime_ns
  result=s.write_plan(tid,self.plan(),self.sha(p));self.assertTrue(result['changed']);self.assertFalse(result['writes']);self.assertFalse(lock.exists());self.assertEqual(p.read_bytes(),before);self.assertEqual(p.stat().st_mtime_ns,mtime)
 def test_plan_update_preserves_every_non_todo_byte_and_file_mode(self):
  s,p,tid=self.created();p.write_text(p.read_text().replace('author: "ai"','author: "human"').replace('status: "open"','status: "waiting"').replace('---\n#','custom: "manual"\n---\n#')+'## TODO\n- [x] raw dump checkbox\n')
  p.chmod(0o640);before=p.read_text();result=s.write_plan(tid,self.plan(),self.sha(p),apply=True);after=p.read_text()
  self.assertTrue(result['writes']);self.assertEqual(before.split('## TODO',1)[0],after.split('## TODO',1)[0]);self.assertEqual(before.split('## Evidence',1)[1],after.split('## Evidence',1)[1]);self.assertEqual(p.stat().st_mode&0o777,0o640)
 def test_retry_and_extension_preserve_manual_checked_text(self):
  s,p,tid=self.created(True);p.write_text(p.read_text().replace('- [ ] Rozpocząć plan','- [x] Owner changed label'))
  before=p.read_bytes();result=s.write_plan(tid,self.plan(),self.sha(p),apply=True);self.assertFalse(result['changed']);self.assertEqual(p.read_bytes(),before)
  result=s.write_plan(tid,self.plan(True),self.sha(p),apply=True);self.assertTrue(result['writes']);text=p.read_text();self.assertIn('- [x] Owner changed label',text);self.assertLess(text.index('Sprawdzić wynik'),text.index('Zakończyć:'));self.assertEqual(text.count('ai-system-plan:fixture-plan:start'),1)
 def test_completed_plan_requires_explicit_reopen_before_extension(self):
  s,p,tid=self.created(True);p.write_text(p.read_text().replace('- [ ] Zakończyć:','- [x] Zakończyć:'));before=p.read_bytes()
  with self.assertRaisesRegex(ValueError,'reopening'):s.write_plan(tid,self.plan(True),self.sha(p),apply=True)
  self.assertEqual(p.read_bytes(),before)
 def test_stale_hash_duplicate_uuid_and_missing_task_are_refused(self):
  s,p,tid=self.created();old=self.sha(p);p.write_text(p.read_text()+'Owner edit\n');before=p.read_bytes()
  with self.assertRaisesRegex(ValueError,'version-conflict'):s.write_plan(tid,self.plan(),old,apply=True)
  self.assertEqual(p.read_bytes(),before)
  copy=s.task_dir/'duplicate.md';copy.write_bytes(before)
  with self.assertRaisesRegex(ValueError,'ambiguous-task'):s.write_plan(tid,self.plan(),self.sha(p),apply=True)
  copy.unlink()
  with self.assertRaisesRegex(ValueError,'missing-or-ambiguous'):s.write_plan('00000000-0000-0000-0000-000000000000',self.plan(),self.sha(p),apply=True)
 def test_concurrent_native_edit_detected_before_replace(self):
  s,p,tid=self.created();real=__import__('task_store').read_task_fd;count=0
  def changed(*args):
   nonlocal count
   count+=1
   if count==3:p.write_text(p.read_text()+'UI edit wins\n')
   return real(*args)
  with patch('task_store.read_task_fd',side_effect=changed),self.assertRaisesRegex(ValueError,'version-conflict'):s.write_plan(tid,self.plan(),self.sha(p),apply=True)
  self.assertTrue(p.read_text().endswith('UI edit wins\n'));self.assertNotIn('ai-system-plan:fixture-plan:start',p.read_text());self.assertFalse(list(p.parent.glob('.ai-system-plan-*')))
 def test_invalid_plan_and_malformed_markdown_no_mutation(self):
  s,p,tid=self.created();original=p.read_text()
  for value in [{},{'id':'../escape','stages':[]},{'id':'a','stages':[]},{'id':'a','stages':[{'id':'start','text':'a'},{'id':'finish','text':'bad\n## Evidence'}]}]:
   with self.assertRaises(ValueError):s.write_plan(tid,value,self.sha(p),apply=True)
   self.assertEqual(p.read_text(),original)
  for text in [original.replace('## TODO','## OTHER'),original.replace('## TODO','## TODO\n## TODO')]:
   p.write_text(text)
   with self.assertRaises(ValueError):s.write_plan(tid,self.plan(),self.sha(p),apply=True)
   self.assertEqual(p.read_text(),text)
 def test_crlf_and_raw_dump_headings_preserved(self):
  s,p,tid=self.created();p.write_bytes((p.read_text()+'## TODO\nraw\n').replace('\n','\r\n').encode());before=p.read_bytes().split(b'## Working dump',1)[1]
  s.write_plan(tid,self.plan(),self.sha(p),apply=True);self.assertEqual(p.read_bytes().split(b'## Working dump',1)[1],before)
 def test_linked_task_and_foreign_profile_cannot_be_updated(self):
  s,p,tid=self.created();outside=self.w/'outside.md';outside.write_bytes(p.read_bytes());p.unlink();p.symlink_to(outside);before=outside.read_bytes()
  with self.assertRaises(ValueError):s.write_plan(tid,self.plan(),self.sha(p),apply=True)
  self.assertEqual(outside.read_bytes(),before)
  (self.root/'TaskNotes/Tasks').mkdir(parents=True)
  with self.assertRaisesRegex(ValueError,'profile-required'):TaskStore(self.root,'tasknotes-v1').write_plan(tid,self.plan(),'0'*64)
 def test_plan_cli_preview_apply_and_stale_hash(self):
  import subprocess
  s,p,tid=self.created();before=p.read_bytes();digest=self.sha(p);input=self.w/'plan.json';input.write_text(json.dumps(self.plan()))
  cmd=[sys.executable,str(S/'task-store'),'plan','--workspace',str(self.w),'--task-id',tid,'--input',str(input)]
  missing=subprocess.run(cmd,capture_output=True,text=True);self.assertNotEqual(missing.returncode,0);self.assertEqual(p.read_bytes(),before)
  preview=subprocess.run(cmd+['--expected-sha256',digest],capture_output=True,text=True);self.assertEqual(preview.returncode,0,preview.stderr);self.assertFalse(json.loads(preview.stdout)['writes']);self.assertEqual(p.read_bytes(),before)
  applied=subprocess.run(cmd+['--expected-sha256',digest,'--owner-approved'],capture_output=True,text=True);self.assertEqual(applied.returncode,0,applied.stderr);self.assertTrue(json.loads(applied.stdout)['writes'])
  updated=p.read_bytes();stale=subprocess.run(cmd+['--expected-sha256',digest,'--owner-approved'],capture_output=True,text=True);self.assertNotEqual(stale.returncode,0);self.assertEqual(p.read_bytes(),updated)
 def test_malformed_managed_blocks_and_hardlinks_refused(self):
  s,p,tid=self.created(True);original=p.read_text()
  variants=[original.replace('fixture-plan:end','fixture-plan:other'),original.replace('fixture-plan:finish','fixture-plan:start'),original.replace('- [ ] Rozpocząć plan','- [ ] unmarked\n- [ ] Rozpocząć plan')]
  for text in variants:
   p.write_text(text)
   with self.assertRaises(ValueError):s.write_plan(tid,self.plan(True),self.sha(p),apply=True)
   self.assertEqual(p.read_text(),text)
  p.write_text(original);os.link(p,self.w/'hardlink')
  with self.assertRaisesRegex(ValueError,'unsupported-task-file'):s.write_plan(tid,self.plan(True),self.sha(p),apply=True)
  self.assertEqual(p.read_text(),original)
if __name__=='__main__':unittest.main()
