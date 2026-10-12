"""Offline canonical Capture consumers: complete product and QA dependency closure."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from orchestration_compatibility import Blocked, fingerprint, digest
from product_source_binding import product_snapshot, verify_product_snapshot
from qa_source_binding import verify_snapshot
from capture_parity import validate_formal, collection
import test_runtime_source_binding as fixtures


class ProductBindingTests(unittest.TestCase):
    git = fixtures.RuntimeBindingTests.git
    put = fixtures.RuntimeBindingTests.put
    qa_text = fixtures.RuntimeBindingTests.qa_text
    install_capture = fixtures.RuntimeBindingTests.install_capture
    write_capture = fixtures.RuntimeBindingTests.write_capture
    current = fixtures.RuntimeBindingTests.current
    blocked = fixtures.RuntimeBindingTests.blocked

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name).resolve()
        self.repo = self.base / 'repo'; self.repo.mkdir()
        self.git('init', '-q'); self.git('config', 'user.name', 'Synthetic test')
        self.git('config', 'user.email', 'synthetic@example.invalid')
        for name in ('README.md', 'HUMANS.md', '.gitignore', '.systems/scripts/code.py'):
            self.put(name, 'synthetic product ' + name)
        self.git('add', '.'); self.git('commit', '-qm', 'synthetic baseline')
        self.policy = self.base/'workflow/.systems'; self.policy.mkdir(parents=True)
        (self.policy/'contract.md').write_text('synthetic QA policy')
        self.spec = self.base/'spec.md'; self.spec.write_text('synthetic assessed DoD')
        self.value = product_snapshot(self.repo, 'scheduler', 'work', [str(self.policy)], [str(self.spec)])
        self.install_capture()

    def tearDown(self):
        self.temp.cleanup()

    def test_unrelated_commits_and_dirty_index_remain_current(self):
        qa, snapshot, capture = self.qa.read_bytes(), self.snap.read_bytes(), self.capture.read_bytes()
        for n in range(3):
            self.put('ai-workflow-workspace/status.md', str(n))
            self.git('add', 'ai-workflow-workspace'); self.git('commit', '-qm', 'unrelated runtime')
            self.current()
        self.put('ai-workflow-workspace/status.md', 'dirty'); self.git('add', 'ai-workflow-workspace')
        self.current()
        self.assertEqual((qa, snapshot, capture), (self.qa.read_bytes(), self.snap.read_bytes(), self.capture.read_bytes()))

    def test_product_change_without_commit_rejects(self):
        self.put('.systems/scripts/code.py', 'changed'); self.blocked()

    def test_product_commit_rejects(self):
        self.put('.systems/scripts/code.py', 'changed'); self.git('add', '.systems'); self.git('commit', '-qm', 'product change'); self.blocked()

    def test_product_addition_rejects(self):
        self.put('.systems/new-input.md', 'added'); self.blocked()

    def test_product_deletion_rejects(self):
        (self.repo/'.systems/scripts/code.py').unlink(); self.blocked()

    def test_product_file_mode_rejects(self):
        os.chmod(self.repo/'.systems/scripts/code.py', 0o700); self.blocked()

    def test_product_directory_mode_rejects(self):
        path=self.repo/'.systems/scripts'; os.chmod(path, (path.stat().st_mode & 0o777) ^ 0o040); self.blocked()

    def test_all_root_files_bound(self):
        for name in ('README.md', 'HUMANS.md', '.gitignore'):
            with self.subTest(name=name):
                old=(self.repo/name).read_bytes(); self.put(name, 'changed'); self.blocked(); (self.repo/name).write_bytes(old); self.current()

    def test_absent_github_becomes_present_rejects(self):
        self.put('.github/workflows/ci.yml', 'new'); self.blocked()

    def test_existing_github_namespace_complete(self):
        self.put('.github/workflows/ci.yml', 'original')
        self.value=product_snapshot(self.repo,'scheduler','work',[str(self.policy)],[str(self.spec)]); self.install_capture(); self.current()
        self.put('.github/new.yml', 'added'); self.blocked()

    def test_missing_required_product_files_reject_creation(self):
        (self.repo/'HUMANS.md').unlink()
        with self.assertRaises(Blocked): product_snapshot(self.repo,'scheduler','work',[str(self.policy)],[str(self.spec)])

    def test_unknown_tracked_path_rejects(self):
        self.put('unexpected.txt', 'unknown'); self.git('add','unexpected.txt'); self.blocked()

    def test_dependency_policy_addition_rejects(self):
        (self.policy/'added-validator.py').write_text('new QA input'); self.blocked()

    def test_dependency_policy_deletion_rejects(self):
        (self.policy/'contract.md').unlink(); self.blocked()

    def test_dependency_policy_change_rejects(self):
        (self.policy/'contract.md').write_text('changed'); self.blocked()

    def test_dependency_spec_change_rejects(self):
        self.spec.write_text('changed DoD'); self.blocked()

    def test_dependency_mode_rejects(self):
        os.chmod(self.spec, 0o700); self.blocked()

    def test_symlink_product_rejects(self):
        path=self.repo/'.systems/linked'; path.symlink_to(self.spec); self.blocked()

    def test_symlink_dependency_rejects(self):
        self.spec.unlink(); self.spec.symlink_to(self.repo/'README.md'); self.blocked()

    def test_nested_git_dependency_rejects(self):
        (self.policy/'.git').mkdir(); self.blocked()

    def test_snapshot_tamper_rejects(self):
        self.value['body']['population']['README.md']['sha256']='0'*64
        with self.assertRaises(Blocked): verify_product_snapshot(self.value,self.repo)

    def test_rehashed_scope_cannot_reuse_original_qa(self):
        value=copy.deepcopy(self.value); value['body']['dependencies']['files']=[]; value['sha256']=digest(value['body'])
        self.snap.write_text(json.dumps(value)); self.proof['qa_refs'][0]['snapshot_sha256']=fingerprint(self.snap); self.write_capture(); self.blocked()

    def test_capture_head_cannot_relabel_provenance(self):
        self.proof['source_head']='0'*40; self.write_capture(); self.blocked()

    def test_wrong_project_rejects(self):
        self.proof['project']='other'; self.write_capture(); self.blocked()

    def test_unknown_binding_no_fallback(self):
        value=copy.deepcopy(self.value); value['body']['binding']='product-scope-v2'; value['sha256']=digest(value['body'])
        with self.assertRaises(Blocked): verify_snapshot(value,self.repo)

    def test_duplicate_overlapping_alias_and_missing_dependencies_reject(self):
        for dirs,files in [([str(self.policy)],[str(self.spec),str(self.spec)]),
                           ([str(self.policy)],[str(self.policy/'contract.md')]),
                           ([],[str(self.repo/'README.md')]),([],[]),([],[str(self.base/'missing')])]:
            with self.subTest(directories=dirs,files=files):
                with self.assertRaises(Blocked): product_snapshot(self.repo,'scheduler','work',dirs,files)

    def test_changed_qa_rejects(self):
        self.qa.write_text(self.qa.read_text()+'\nchanged'); self.blocked()


if __name__ == '__main__':
    unittest.main()
