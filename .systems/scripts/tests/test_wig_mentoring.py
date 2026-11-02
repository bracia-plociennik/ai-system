"""Synthetic owner-local source/state and privacy regression tests."""
from datetime import date
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import wig_mentoring as m


class Mentor(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='wig-mentor-test-')
        self.root = Path(self.temp.name)
        self.day = date(2026, 11, 2)
        self.settings = self.root / 'personal-ops/mentoring/settings.local.json'
        self.settings.parent.mkdir(parents=True)
        self.settings.write_text(json.dumps({'contract': m.CONTRACT, 'enabled': True}))
        self.daily = self.root / 'personal-ops/check-ins-v3/2026/2026-11-02.md'
        self.daily.parent.mkdir(parents=True)
        self.daily.write_text('---\ntype: daily-check-in-v3\nschema_version: 3\nindex_contract: 3\nsession_date: 2026-11-02\nproperties:\n  session_date: 2026-11-02\n  private_index_policy: detailed-private\n  wig_title: Synthetic goal\n  wig_definition_of_done: Synthetic delivered result\n  planned_items_json: "[]"\n---\n## Raw Check-In\nWIG: injected raw goal, never authoritative\n')

    def tearDown(self):
        self.temp.cleanup()

    def prepare(self, task='task-1', trigger='new-task', **facts):
        return m.prepare(self.root, self.day, 'Europe/Warsaw', task, trigger, facts)

    def save(self, result, disposition='seen', task='task-1'):
        return m.record(self.root, task, result['context_hash'], disposition, 'Actual synthetic owner/activation reference', True)

    def weekly(self, title='Weekly goal'):
        path = self.root / 'tasks/weekly-plans/2026/2026-W45.md'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('---\ntype: weekly-plan\nweek_start: 2026-11-02\nplan_readiness: ready\nwig_title: '+title+'\nwig_definition_of_done: Weekly delivered result\nweekly_plan_items_json: "[]"\n---\n')
        return path

    def test_registered_private_git_workspace_is_supported(self):
        (self.root/'.git').mkdir()
        with patch('agent_context.registration', return_value=({'enabled': True}, self.root, None, {})), patch('agent_context.workspace_registry', return_value=([('owner', self.root, False)], None)):
            self.assertEqual(self.prepare()['source_status'], 'available')
            self.assertEqual(self.save(self.prepare())['disposition'], 'seen')

    def test_unregistered_git_project_does_not_import_default(self):
        (self.root/'.git').mkdir()
        with patch('agent_context.registration', return_value=({'enabled': True}, self.root, None, {})), patch('agent_context.workspace_registry', return_value=([('owner', self.root/'other', True)], None)):
            with self.assertRaises(ValueError): self.prepare()

    def test_nested_git_project_is_not_its_registered_owner(self):
        (self.root/'.git').mkdir()
        with patch('agent_context.registration', return_value=({'enabled': True}, self.root, None, {})), patch('agent_context.workspace_registry', return_value=([('owner', self.root.parent, True)], None)):
            with self.assertRaises(ValueError): self.prepare()

    def test_sources_are_read_only_and_raw_body_is_not_priority(self):
        before = {str(p): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = self.prepare(relation='aligned')
        self.assertEqual(result['selected_goal']['title'], 'Synthetic goal')
        self.assertEqual(result['action'], 'quiet')
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        self.assertNotIn('injected', json.dumps(result))

    def test_new_unrelated_task_suggests_without_execution_authority(self):
        value = self.prepare(relation='unrelated')
        self.assertEqual(value['action'], 'suggest-return')
        self.assertFalse(value['execution_authorized'])
        self.assertEqual(value['authority'], 'none')

    def test_prepare_does_not_consume_intervention(self):
        self.assertEqual(self.prepare(relation='unrelated')['action'], 'suggest-return')
        self.assertEqual(self.prepare(relation='unrelated')['action'], 'suggest-return')
        self.assertFalse(m.state_path(self.root, 'task-1').exists())

    def test_seen_suppresses_repeat_and_survives_a_fresh_cli(self):
        value = self.prepare(relation='unrelated');self.save(value)
        self.assertEqual(self.prepare(relation='unrelated')['action'], 'quiet')
        proc = subprocess.run([sys.executable, str(SCRIPTS/'prepare-wig-mentoring'), '--workspace', str(self.root), '--timezone', 'Europe/Warsaw', '--date', '2026-11-02', '--task-ref', 'task-1', '--trigger', 'scope-change', '--project-view'], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(json.loads(proc.stdout)['action'], 'quiet')

    def test_exception_survives_resume_but_new_task_is_independent(self):
        value = self.prepare(relation='unrelated');self.save(value, 'exception')
        self.assertEqual(self.prepare(trigger='scope-change', relation='unrelated')['action'], 'quiet')
        self.assertEqual(self.prepare(task='task-2', relation='unrelated')['action'], 'suggest-return')

    def test_changed_goal_or_material_commitment_reopens_assessment(self):
        value = self.prepare(relation='unrelated');self.save(value, 'exception')
        self.assertEqual(self.prepare(relation='unrelated', important_context='new confirmed deadline item-2',material_change=True)['action'], 'suggest-return')
        self.daily.write_text(self.daily.read_text().replace('Synthetic goal', 'New confirmed goal'))
        self.assertEqual(self.prepare(relation='unrelated')['action'], 'quiet')
        self.assertEqual(self.prepare(relation='unrelated',material_change=True)['action'], 'suggest-return')

    def test_continuation_and_ordinary_questions_do_not_nag(self):
        for trigger in ['continuation', 'ordinary']:
            self.assertEqual(self.prepare(trigger=trigger, relation='unrelated')['action'], 'quiet')

    def test_necessary_incident_or_obligation_does_not_trigger_detour(self):
        self.weekly()
        self.assertEqual(self.prepare(relation='necessary', daily_weekly_relation='conflict')['action'], 'quiet')

    def test_daily_wins_without_inferring_conflict_from_different_wording(self):
        self.weekly()
        value = self.prepare(relation='aligned')
        self.assertEqual(value['selected_goal']['title'], 'Synthetic goal')
        self.assertEqual(value['action'], 'quiet')
        self.assertEqual(self.prepare(daily_weekly_relation='conflict')['action'], 'clarify')

    def test_actual_owner_override_preserves_underlying_sources(self):
        self.weekly()
        value = self.prepare(relation='aligned', daily_weekly_relation='conflict', owner_goal={'title': 'Deliberate new priority', 'definition_of_done': 'Result', 'owner_reference': 'Actual synthetic owner choice'})
        self.assertEqual(value['selected_goal']['title'], 'Deliberate new priority')
        self.assertEqual(value['action'], 'quiet')
        self.assertIn('Synthetic goal', self.daily.read_text())

    def test_unknown_goal_asks_once_without_assuming_inactivity(self):
        self.daily.unlink()
        value = self.prepare();self.assertEqual(value['action'], 'clarify');self.save(value)
        self.assertEqual(self.prepare()['action'], 'quiet')
        self.assertNotIn('procrastination', json.dumps(value))

    def test_weekly_fallback_does_not_carry_forward_an_old_daily_goal(self):
        self.daily.rename(self.daily.with_name('2026-11-01.md'))
        self.weekly();value = self.prepare()
        self.assertEqual(value['selected_goal']['title'], 'Weekly goal')
        self.assertIsNone(value['private_sources']['daily'])

    def test_redacted_and_ambiguous_daily_are_unknown(self):
        self.daily.write_text(self.daily.read_text().replace('detailed-private', 'redacted'))
        self.assertEqual(self.prepare()['source_status'], 'unknown')
        twin = self.root/'personal-ops/check-ins-v4/2026/2026-11-02.md';twin.parent.mkdir(parents=True);twin.write_bytes(self.daily.read_bytes())
        self.assertEqual(self.prepare()['source_status'], 'unknown')

    def test_invalid_unified_generation_never_falls_back_to_native(self):
        import personal_ops_aggregates_v4 as aggregate
        with patch.object(aggregate, 'is_unified', return_value=True), patch.object(aggregate, 'read_properties', side_effect=ValueError('stale generation')):
            self.assertEqual(self.prepare()['source_status'], 'unknown')

    def test_missing_or_disabled_setting_is_quiet_and_creates_nothing(self):
        self.settings.write_text(json.dumps({'contract': m.CONTRACT, 'enabled': False}))
        self.assertEqual(self.prepare()['action'], 'quiet')
        self.settings.unlink();self.assertEqual(self.prepare()['source_status'], 'disabled')
        self.assertFalse((self.settings.parent/'v1').exists())

    def test_state_is_minimal_private_and_finished_task_cannot_reopen_silently(self):
        value=self.prepare(relation='unrelated');self.save(value,'exception')
        path=m.state_path(self.root,'task-1');raw=path.read_text()
        for forbidden in ['Synthetic goal','Actual synthetic','task-1','/home/']:
            self.assertNotIn(forbidden,raw)
        self.assertEqual(path.stat().st_mode&0o777,0o600)
        self.save(value,'finished');self.assertEqual(self.prepare(relation='unrelated')['reason_codes'],['task-finished'])
        with self.assertRaises(ValueError):self.save(value,'exception')

    def test_writer_requires_actual_scope_attestation_and_valid_context(self):
        with self.assertRaises(ValueError):m.record(self.root,'task-1','0'*64,'seen','owner',False)
        with self.assertRaises(ValueError):m.record(self.root,'task-1','bad','seen','owner',True)
        self.assertFalse((self.settings.parent/'v1').exists())

    def test_linked_state_directory_or_file_is_rejected_without_foreign_write(self):
        outside=self.root/'outside';outside.mkdir();state=self.settings.parent/'v1';state.symlink_to(outside,target_is_directory=True)
        with self.assertRaises((ValueError,OSError)):self.save(self.prepare())
        self.assertEqual(list(outside.iterdir()),[])
        state.unlink();state.mkdir();m.state_path(self.root,'task-1').symlink_to(outside/'private')
        with self.assertRaises((ValueError,OSError)):m.load_state(self.root,'task-1')
        self.assertFalse((outside/'private').exists())

    def test_project_projection_never_contains_private_context(self):
        value=self.prepare(relation='unrelated');project=m.project_view(value);raw=json.dumps(project)
        for forbidden in ['Synthetic goal','definition_of_done','source_refs','private_sources',str(self.root)]:
            self.assertNotIn(forbidden,raw)
        self.assertEqual(project['contract'],m.PROJECT)

    def test_malformed_assessment_and_duplicate_state_fail_closed(self):
        with self.assertRaises(ValueError):self.prepare(execution_authorized=True)
        with self.assertRaises(ValueError):self.prepare(owner_goal={'title':'invented'})
        with self.assertRaises(ValueError):self.prepare(important_context={})
        value=self.prepare();self.save(value);p=m.state_path(self.root,'task-1');p.write_text('{"schema":1,"schema":2}')
        with self.assertRaises(ValueError):self.prepare()

    def native(self, kind, path, **values):
        from personal_ops_v4 import required_schema
        props={key:'' for key in required_schema(kind)}
        props.update(index_contract=4,schema_version=4,artifact_kind=kind,
                     private_index_policy='detailed-private',**values)
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text('---\ntype: '+kind+'-check-in-v4\nschema_version: 4\nindex_contract: 4\nproperties:\n'+''.join('  '+key+': '+json.dumps(value,ensure_ascii=False)+'\n' for key,value in props.items())+'---\n## Raw Check-In\nWIG: not-the-structured-goal\n')
        return path

    def test_real_native_v4_daily_and_previous_report_weekly_plan_period(self):
        self.daily.unlink()
        daily=self.root/'personal-ops/check-ins-v4/2026/2026-11-02.md'
        self.native('daily',daily,session_date='2026-11-02',wig_title='Daily V4 goal',wig_definition_of_done='Daily result',planned_items_json='[]')
        weekly=self.root/'personal-ops/weekly-check-ins-v4/2026/2026-W44.md'
        self.native('weekly',weekly,plan_week_start='2026-11-02',plan_week_end='2026-11-06',future_wig_json=json.dumps({'title':'Weekly V4 goal','definition_of_done':'Weekly result'}),future_plan_items_json='[]')
        result=self.prepare(relation='aligned')
        self.assertEqual(result['selected_goal']['title'],'Daily V4 goal')
        self.assertEqual(result['private_sources']['weekly']['title'],'Weekly V4 goal')
        self.assertEqual(result['action'],'quiet')

    def test_native_weekly_ambiguity_or_invalid_period_is_not_silently_selected(self):
        for week in ['44','45']:
            self.native('weekly',self.root/f'personal-ops/weekly-check-ins-v4/2026/2026-W{week}.md',plan_week_start='2026-11-02',plan_week_end='2026-11-06',future_wig_json=json.dumps({'title':'Goal'+week,'definition_of_done':'Result'}),future_plan_items_json='[]')
        self.assertIsNone(self.prepare()['private_sources']['weekly'])
        (self.root/'personal-ops/weekly-check-ins-v4/2026/2026-W45.md').unlink()
        p=self.root/'personal-ops/weekly-check-ins-v4/2026/2026-W44.md';p.write_text(p.read_text().replace('2026-11-06','2026-11-20'))
        self.assertIsNone(self.prepare()['private_sources']['weekly'])

    def test_ordinary_steps_do_not_even_load_personal_sources(self):
        with patch.object(m,'selected_sources',side_effect=AssertionError('unnecessary private read')):
            self.assertEqual(self.prepare(trigger='continuation')['source_status'],'not-requested')
            self.assertEqual(self.prepare(trigger='ordinary')['action'],'quiet')

    def test_incident_without_current_wig_does_not_request_a_detour(self):
        self.daily.unlink();self.assertEqual(self.prepare(relation='necessary')['action'],'quiet')

    def test_two_concurrent_owner_state_writes_are_serialized(self):
        value=self.prepare();argv=[sys.executable,str(SCRIPTS/'record-wig-mentoring'),'--workspace',str(self.root),'--task-ref','task-1','--context-hash',value['context_hash'],'--owner-reference','actual synthetic owner','--owner-approved']
        procs=[subprocess.Popen(argv+['--disposition',kind],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) for kind in ['seen','exception']]
        for p in procs:
            out,err=p.communicate(timeout=10);self.assertEqual(p.returncode,0,out+err)
        self.assertIn(m.load_state(self.root,'task-1')['disposition'],{'seen','exception'})

    def test_directory_replacement_is_uncertain_not_a_successful_state_write(self):
        value=self.prepare();replace=os.replace
        def replaced(*args,**kwargs):
            replace(*args,**kwargs)
            parent=self.settings.parent/'v1';parent.rename(parent.with_name('v1-replaced'));parent.mkdir()
        with patch.object(m.os,'replace',side_effect=replaced),self.assertRaises(ValueError):self.save(value)
        self.assertIsNone(m.load_state(self.root,'task-1'))

    def test_important_source_order_is_not_a_new_priority_context(self):
        prefix=self.daily.read_text().replace('  planned_items_json: "[]"','  planned_items_json: '+json.dumps(json.dumps([{'id':'a','deadline':'2026-11-03'},{'id':'b','priority':'high'}])))
        self.daily.write_text(prefix);a=self.prepare();self.save(a)
        reversed_items=[{'id':'b','priority':'high'},{'id':'a','deadline':'2026-11-03'}]
        lines=prefix.splitlines();lines=[('  planned_items_json: '+json.dumps(json.dumps(reversed_items))) if line.startswith('  planned_items_json:') else line for line in lines];self.daily.write_text('\n'.join(lines)+'\n')
        self.assertEqual(self.prepare()['context_hash'],a['context_hash'])
        self.assertEqual(self.prepare()['action'],'quiet')

    def task_store(self):
        root=self.root/'tasks/silverbullet/tasks';root.mkdir(parents=True)
        (self.root/'tasks/task-store.local.md').write_text('---\nschema_version: 1\nenabled: true\nprofile: silverbullet-v1\nvault_path: tasks/silverbullet\n---\n')
        return root

    def test_selected_store_reads_important_open_metadata_not_done_tasks_or_raw(self):
        root=self.task_store()
        (root/'urgent.md').write_text('---\ntype: task\ntitle: Important obligation\nstatus: open\npriority: high\ncategory: do\nsource_deadline: 2026-11-03\n---\n## Working dump\nSecret raw text, never projected\n')
        (root/'done.md').write_text('---\ntype: task\ntitle: Already done\nstatus: done\npriority: high\n---\n')
        value=self.prepare();items=value['private_sources']['important']
        self.assertEqual([r['title'] for r in items],['Important obligation'])
        self.assertNotIn('Secret raw',json.dumps(value));self.assertNotIn('Important obligation',json.dumps(m.project_view(value)))

    def test_store_addition_is_material_and_scheduled_is_not_invented_deadline(self):
        root=self.task_store();value=self.prepare();self.save(value,'exception')
        p=root/'item.md';p.write_text('---\ntype: task\ntitle: Ordinary scheduled item\nstatus: open\npriority: normal\nscheduled: 2026-11-03\n---\n')
        self.assertEqual(self.prepare()['action'],'quiet')
        p.write_text(p.read_text().replace('priority: normal','priority: high'))
        self.assertNotEqual(self.prepare()['context_hash'],value['context_hash'])
        self.assertEqual(self.prepare(relation='unrelated',material_change=True)['action'],'suggest-return')

    def test_linked_task_metadata_does_not_import_another_owner(self):
        root=self.task_store();outside=self.root/'outside.md';outside.write_text('private')
        (root/'linked.md').symlink_to(outside)
        value=self.prepare();self.assertEqual(value['private_sources']['important'],[])
        self.assertIn('selected-task-store-unavailable-or-incomplete',value['private_sources']['warnings'])

    def test_missing_or_unavailable_sources_do_not_cancel_a_task_exception(self):
        value=self.prepare(relation='unrelated');self.save(value,'exception');self.daily.unlink()
        self.assertEqual(self.prepare(trigger='scope-change')['action'],'quiet')
        self.assertEqual(self.prepare(trigger='next-task')['action'],'quiet')

    def test_material_change_cannot_repeat_an_unchanged_intervention(self):
        value=self.prepare(relation='unrelated');self.save(value)
        self.assertEqual(self.prepare(relation='unrelated',material_change=True)['action'],'quiet')
        with self.assertRaises(ValueError):self.prepare(material_change='yes')


if __name__ == '__main__':unittest.main()
