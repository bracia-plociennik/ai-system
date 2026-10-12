"""Offline consumer regressions: unrelated HEAD drift versus real runtime drift."""
import copy
import json
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from orchestration_compatibility import Blocked, digest, fingerprint
from runtime_source_binding import runtime_snapshot, verify_runtime_snapshot
from qa_source_binding import verify_snapshot, snapshot
from capture_parity import validate_formal, collection


class RuntimeBindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name).resolve()
        self.repo = self.base / 'repo'
        self.repo.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.name', 'Synthetic test')
        self.git('config', 'user.email', 'synthetic@example.invalid')
        self.put('unrelated.md', 'initial')
        self.git('add', 'unrelated.md')
        self.git('commit', '-qm', 'synthetic baseline')
        for name in ('dispatcher.py', 'test_dispatcher.py', 'prompt.md'):
            self.put('scheduler/' + name, 'synthetic source ' + name)
        self.unit = self.base / 'service'
        self.unit.write_text('synthetic schedule')
        self.exclusions = [dict(path=n, kind=k, reason='reviewed synthetic output') for n,k in
                           [('quality','directory'),('evidence','directory'),('distillations','directory'),('ledger.jsonl','file')]]
        self.value = runtime_snapshot(self.repo, 'scheduler', 'work', 'scheduler', self.exclusions, [str(self.unit)])
        self.install_capture()

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.check_output(['git','-C',str(self.repo),*args],text=True,stderr=subprocess.DEVNULL).strip()

    def put(self, name, text):
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def qa_text(self, value):
        return ('# Synthetic QA\n\n- QA verification contract: full-qa-verification-v3\n\n'
                '## Current QA Run\n\n- Artifact kind: implementation-quality\n'
                '- Project/task identity: scheduler:work\n'
                '- Source snapshot SHA-256: '+value['sha256']+'\n'
                '- Verdict: PASS\n- Gate Decision: PASS\n\n'
                '### Definition Of Done Validation\nSynthetic namespace and dependency scope reviewed.\n'
                '### Intent / Plan / Spec Compliance\nSynthetic accepted scope.\n'
                '### Review Completeness Gate\n- Status: complete\n- Closure freshness: current\n'
                '- Required-field mapping: complete\n'
                '### Quality Gate\n- 100% DoD satisfied: yes\n- No known bug in scope: yes\n- Quality result: PASS\n')

    def install_capture(self):
        self.snap = self.put('scheduler/evidence/snapshot.json',json.dumps(self.value))
        self.qa = self.put('scheduler/quality/current.md',self.qa_text(self.value))
        dist = self.put('scheduler/distillations/accepted.md','- Work ID: work\n- Owning project: scheduler\n- Acceptance: accepted\n')
        self.proof = dict(work_id='work',project='scheduler',source_root=str(self.repo),source_head=self.value['body']['head'],
            evidence_root='scheduler',qa_refs=[dict(path='quality/current.md',sha256=fingerprint(self.qa),snapshot_path='evidence/snapshot.json',snapshot_sha256=fingerprint(self.snap))],
            task_ids=['work'],distillation_sha256=fingerprint(dist))
        self.capture = self.repo/'capture-state/work.md'
        self.write_capture()

    def write_capture(self):
        self.put('capture-state/work.md','- Capture schema: 3\n- Work ID: work\n- State: completed\n'
                 '- Distillation artifact: scheduler/distillations/accepted.md\n- Privacy/scope check: pass\n'
                 '- `is_distilled` derived value: true\n\n## Capture Verification\n```json\n'+json.dumps(self.proof)+'\n```\n')

    def current(self):
        self.assertEqual(validate_formal(self.capture,self.repo),dict(state='completed',current_quality=True))
        self.assertFalse(collection(self.repo,'capture-state')['errors'])

    def blocked(self):
        with self.assertRaises((Blocked,ValueError,KeyError,OSError,subprocess.CalledProcessError)):
            validate_formal(self.capture,self.repo)
        self.assertIn('work.md',collection(self.repo,'capture-state')['errors'])

    def test_unrelated_commits_and_dirty_index_do_not_invalidate(self):
        qa_before = self.qa.read_bytes()
        capture_before = self.capture.read_bytes()
        for i in range(3):
            self.put('unrelated.md',str(i))
            self.git('add','unrelated.md');self.git('commit','-qm','unrelated')
            self.current()
        self.put('unrelated.md','dirty staged');self.git('add','unrelated.md')
        self.current()
        self.assertEqual(self.qa.read_bytes(),qa_before)
        self.assertEqual(self.capture.read_bytes(),capture_before)

    def test_current_head_code_edit_rejected(self):
        self.put('scheduler/dispatcher.py','different');self.blocked()

    def test_prompt_edit_rejected(self):
        self.put('scheduler/prompt.md','different');self.blocked()

    def test_unit_edit_rejected(self):
        self.unit.write_text('different');self.blocked()

    def test_unit_mode_change_rejected(self):
        self.unit.chmod(self.unit.stat().st_mode ^ 0o100);self.blocked()

    def test_runtime_mode_change_rejected(self):
        p=self.repo/'scheduler/dispatcher.py';p.chmod(p.stat().st_mode ^ 0o100);self.blocked()

    def test_added_source_rejected(self):
        self.put('scheduler/new-import.py','new');self.blocked()

    def test_deleted_source_rejected(self):
        (self.repo/'scheduler/dispatcher.py').unlink();self.blocked()

    def test_deleted_dependency_rejected(self):
        self.unit.unlink();self.blocked()

    def test_symlink_source_rejected(self):
        p=self.repo/'scheduler/dispatcher.py';p.unlink();p.symlink_to(self.unit);self.blocked()

    def test_symlink_dependency_rejected(self):
        q=self.base/'other';q.write_text(self.unit.read_text());self.unit.unlink();self.unit.symlink_to(q);self.blocked()

    def test_new_symlink_rejected(self):
        (self.repo/'scheduler/new').symlink_to(self.unit);self.blocked()

    def test_excluded_output_and_ledger_can_change(self):
        self.put('scheduler/evidence/new.json','new derived evidence')
        self.put('scheduler/quality/new.md','unreferenced QA')
        self.put('scheduler/ledger.jsonl','mutable administrative state')
        self.current()

    def test_exclusion_kind_drift_rejected(self):
        (self.repo/'scheduler/ledger.jsonl').mkdir();self.blocked()

    def test_excluded_symlink_root_rejected(self):
        (self.repo/'scheduler/ledger.jsonl').symlink_to(self.unit);self.blocked()

    def test_qa_tamper_rejected(self):
        self.qa.write_text(self.qa.read_text()+'changed');self.blocked()

    def test_snapshot_tamper_rejected(self):
        v=copy.deepcopy(self.value);v['body']['exclusions'].append(dict(path='dispatcher.py',kind='file',reason='bad'))
        self.snap.write_text(json.dumps(v));self.blocked()

    def test_rehashed_snapshot_cannot_reuse_old_qa(self):
        v=copy.deepcopy(self.value);v['body']['exclusions'].append(dict(path='dispatcher.py',kind='file',reason='bad'));v['sha256']=digest(v['body'])
        self.snap.write_text(json.dumps(v));self.proof['qa_refs'][0]['snapshot_sha256']=fingerprint(self.snap);self.write_capture();self.blocked()

    def test_head_relabel_rejected(self):
        self.proof['source_head']='0'*40;self.write_capture();self.blocked()

    def test_task_relabel_rejected(self):
        self.proof['task_ids']=['other'];self.write_capture();self.blocked()

    def test_repo_identity_drift_rejected(self):
        v=copy.deepcopy(self.value);v['body']['repository_identity']=[0,0];v['sha256']=digest(v['body'])
        with self.assertRaises(Blocked):verify_runtime_snapshot(v,self.repo)

    def test_snapshot_wrong_role_rejected(self):
        v=copy.deepcopy(self.value);v['body']['role']='other';v['sha256']=digest(v['body'])
        with self.assertRaises(Blocked):verify_runtime_snapshot(v,self.repo)

    def test_escape_and_overlap_rejected(self):
        for exclusions in ([dict(path='../escape',kind='file',reason='bad')], [dict(path='quality',kind='directory',reason='out'),dict(path='quality/a',kind='file',reason='out')]):
            with self.assertRaises(Blocked):runtime_snapshot(self.repo,'scheduler','work','scheduler',exclusions)

    def test_empty_namespace_rejected(self):
        for p in (self.repo/'scheduler').glob('*'):
            if p.is_file():p.unlink()
        with self.assertRaises(Blocked):runtime_snapshot(self.repo,'scheduler','work','scheduler',self.exclusions)

    def test_missing_reason_rejected(self):
        with self.assertRaises(Blocked):runtime_snapshot(self.repo,'scheduler','work','scheduler',[dict(path='quality',kind='directory',reason='')])

    def test_duplicate_dependency_rejected(self):
        with self.assertRaises(Blocked):runtime_snapshot(self.repo,'scheduler','work','scheduler',self.exclusions,[str(self.unit),str(self.unit)])

    def test_unknown_snapshot_binding_does_not_fall_back(self):
        v=copy.deepcopy(self.value);v['body']['binding']='unknown';v['sha256']=digest(v['body'])
        with self.assertRaises(Blocked):verify_snapshot(v,self.repo)

    def test_legacy_schema_two_still_rejects_stale_head(self):
        self.capture.write_text(self.capture.read_text().replace('Capture schema: 3','Capture schema: 2'))
        self.put('unrelated.md','another');self.git('add','unrelated.md');self.git('commit','-qm','another')
        with self.assertRaisesRegex(Blocked,'HEAD stale'):validate_formal(self.capture,self.repo)

    def test_legacy_schema_one_snapshot_still_rejects_namespace_changes(self):
        # Use isolated source-only repo: original full-population verifier is unchanged.
        source=self.base/'source';source.mkdir();subprocess.run(['git','init','-q',str(source)],check=True)
        for key,val in [('user.name','Synthetic'),('user.email','synthetic@example.invalid')]:subprocess.run(['git','-C',str(source),'config',key,val],check=True)
        (source/'input').write_text('source');subprocess.run(['git','-C',str(source),'add','input'],check=True)
        subprocess.run(['git','-C',str(source),'commit','-qm','baseline'],check=True)
        v=snapshot(source,'project','task');self.assertEqual(verify_snapshot(v,source)['binding'],'same-head')
        (source/'input').write_text('changed')
        with self.assertRaises(Blocked):verify_snapshot(v,source)


if __name__ == '__main__':
    unittest.main()
