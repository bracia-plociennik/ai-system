"""System/Workflow protocol parity and actual canonical consumer regressions."""
from pathlib import Path
import importlib.util
import json
import os
import sys
import tempfile
import unittest

SCRIPTS=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(SCRIPTS))
import maintenance_policy as system

WORKFLOW=Path(os.environ.get('GFM_WORKFLOW_SOURCE',str(SCRIPTS.parents[1]/'ai-workflow')))


def load_tests(loader,tests,pattern):
    # Shared portable golden corpus runs against BOTH cores without maintaining
    # a second private queue or a forked list of scenario expectations.
    source=WORKFLOW/'.systems/scripts/lib/maintenance-tests.py'
    if not source.is_file():
        return loader.loadTestsFromTestCase(AdapterTests)
    spec=importlib.util.spec_from_file_location('shared_maintenance_tests',source)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    module.m=system
    suite=unittest.TestSuite()
    for cls in (module.PolicyTests,module.CanonicalGoalTests,module.CapabilityTests):
        suite.addTests(loader.loadTestsFromTestCase(cls))
    suite.addTests(loader.loadTestsFromTestCase(AdapterTests))
    suite.addTests(loader.loadTestsFromTestCase(SystemCaptureGoalTests))
    return suite


class AdapterTests(unittest.TestCase):
    def test_portable_core_has_exact_counterpart_bytes(self):
        source=WORKFLOW/'.systems/scripts/lib/maintenance-policy.py'
        self.assertTrue(source.is_file(),'reviewed Workflow source required for integrated QA')
        actual=(SCRIPTS/'maintenance_policy.py').read_text().split('\n\n# System adapter:',1)[0]
        self.assertEqual(actual.rstrip(),source.read_text().rstrip())

    def test_same_owner_queue_parent_budget_and_readonly_review(self):
        with tempfile.TemporaryDirectory() as temp:
            owner=Path(temp);ev=owner/'evidence.md';ev.write_text('synthetic authority/independence\n')
            q=system.empty_queue(owner)
            obs=dict(id='issue',cause_key='cause',safe_summary='Independent historical index',source_refs=[str(ev)],
                goal_ref='goal',affected_scope=['goal'],first_seen='2026-01-01T00:00:00Z',last_seen='2026-01-01T00:00:00Z',
                occurrence_task_ids=[],impact='none',independence_evidence=str(ev),immediate_rule_ids=[],state='open',
                defer_reason=None,next_trigger=None,resolution_evidence=None,notification_episode=None)
            q=system.observe(q,obs,'parent','2026-01-01T00:00:00Z')
            path=str(owner/'queue.json')
            q=system.atomic_update(str(owner),path,0,lambda _:q,lambda *_:True)
            before=Path(path).read_bytes()
            for reason in ('owner-request','dreaming','milestone'):
                out=system.read_only_review(str(owner),path,str(owner/'policy.json'),reason=reason)
                self.assertEqual(len(out['issues']),1);self.assertEqual(out['mutations'],[])
                self.assertFalse(out['delivered']);self.assertEqual(out['authority'],'none')
                self.assertEqual(Path(path).read_bytes(),before)

    def test_no_verified_counterpart_means_no_shared_activation(self):
        self.assertRaises(system.Invalid,system.workflow_projection,WORKFLOW,'0'*40,{}, {}, {}, 'issue', None)



class SystemCaptureGoalTests(unittest.TestCase):
    def setUp(self):
        spec=importlib.util.spec_from_file_location('existing_capture_fixtures',SCRIPTS/'tests/test_orchestration_compatibility.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        self.fixture=module.CaptureTests();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        self.workspace,self.owner,self.record,self.source,self.qa,self.dist,self.proof=self.fixture.formal()
        from orchestration_compatibility import fingerprint
        self.fingerprint=fingerprint
        from capture_parity import goal_collection,collection
        self.select=goal_collection;self.full=collection

    def independent_old(self):
        source=self.fixture.git_repo('old-source')
        evidence=self.workspace/'project-state/example/old-evidence';(evidence/'quality').mkdir(parents=True)
        qa=evidence/'quality/old.md';qa.write_text(self.qa.read_text().replace('example:TASK-001','example:HIS-001'))
        p=dict(self.proof,work_id='old',task_ids=['HIS-001'],source_root=str(source),source_head='0'*40,
               evidence_root=str(evidence.relative_to(self.workspace)),qa_refs=[{'path':'quality/old.md','sha256':self.fingerprint(qa)}])
        record=self.record.with_name('old.md')
        record.write_text('- Capture schema: 2\n- Work ID: old\n- State: ready\n- Privacy/scope check: pass\n- `is_distilled` derived value: false\n- Distillation artifact: none\n## Capture Verification\n```json\n'+json.dumps(p)+'\n```\n')
        return record,p,qa

    def test_actual_system_consumer_independent_history_preserved_full_failure(self):
        old,_,_=self.independent_old();before=old.read_bytes()
        self.assertTrue(self.full(self.workspace,self.owner)['errors'])
        out=self.select(self.workspace,self.owner,['new'])
        self.assertEqual(out['gate_result'],'PASS',out);self.assertTrue(out['historical_invalid'])
        self.assertEqual(old.read_bytes(),before)

    def test_invalid_duplicate_or_unknown_sibling_blocks(self):
        old,_,_=self.independent_old();old.write_text(old.read_text().replace('Work ID: old','Work ID: new'))
        self.assertEqual(self.select(self.workspace,self.owner,['new'])['gate_result'],'FAIL')
        old.write_text('# Broken unknown sibling\n')
        self.assertEqual(self.select(self.workspace,self.owner,['new'])['gate_result'],'FAIL')

    def test_required_current_fail_or_shared_dependency_remains_blocking(self):
        old,p,qa=self.independent_old()
        p['source_root']=str(self.source)
        old.write_text(old.read_text().split('```json\n')[0]+'```json\n'+json.dumps(p)+'\n```\n')
        self.assertEqual(self.select(self.workspace,self.owner,['new'])['gate_result'],'FAIL')
        old.unlink()
        self.qa.write_text(self.qa.read_text().replace('- Verdict: PASS','- Verdict: FAIL'))
        self.assertEqual(self.select(self.workspace,self.owner,['new'])['gate_result'],'FAIL')

if __name__=='__main__':unittest.main()
