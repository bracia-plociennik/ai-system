"""Offline updater selection, conflicts and failure behavior; no live update."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1]/'updater_validation.py'
spec = importlib.util.spec_from_file_location('updater_under_test',SCRIPT)
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class UpdaterTests(unittest.TestCase):
    def test_calories_selects_related_tests_and_safety_checks(self):
        p=updater.plan(['.systems/scripts/calculate-personal-ops-budgets'])
        self.assertIn('test_calorie_weekday_plan.py',p['tests'])
        self.assertTrue(set(updater.BASE_CHECKS)<=set(p['checks']))
        self.assertFalse(p['full_validation'])

    def test_updater_covers_own_regressions(self):
        self.assertIn('test_updater_validation.py',updater.plan(['.systems/scripts/update-from-upstream'])['tests'])

    def test_unknown_or_runtime_delta_blocks_no_automatic_full(self):
        for path in ['.systems/scripts/unmapped.py','private/data.md','../outside','-option']:
            with self.assertRaisesRegex(ValueError,'Unmapped'):
                updater.plan([path])

    def test_noop_retains_integrity_and_compatibility(self):
        p=updater.plan([])
        self.assertEqual(p['checks'],updater.BASE_CHECKS)
        self.assertEqual(p['tests'],[])

    def test_selected_git_delta_includes_deleted_and_renamed_paths(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            def git(*args):
                return subprocess.run(['git','-C',d,*args],text=True,capture_output=True,check=True).stdout.strip()
            git('init','-q');git('config','user.email','fixture@example.invalid');git('config','user.name','Fixture')
            (root/'a').write_text('initial');git('add','a');git('commit','-qm','first');base=git('rev-parse','HEAD')
            (root/'a').unlink();(root/'b').write_text('new');git('add','-A');git('commit','-qm','second')
            self.assertEqual(updater.selected_changes(root,base,'HEAD'),['a','b'])

    def test_failed_validation_never_emits_completion(self):
        with patch('sys.argv',['updater','--base','HEAD','--target','HEAD']),\
             patch.object(updater,'selected_changes',return_value=[]),\
             patch.object(updater.subprocess,'run',side_effect=subprocess.CalledProcessError(1,['validator'])):
            self.assertEqual(updater.main(),1)

    def test_updater_retains_ff_conflict_and_dirty_source_guards(self):
        source=SCRIPT.with_name('update-from-upstream').read_text()
        for marker in ['git merge --ff-only FETCH_HEAD','system_dirty','upstream relation is diverged','upstream relation is ahead']:
            self.assertIn(marker,source)
        self.assertIn('validation_mode="targeted"',source)


if __name__=='__main__':unittest.main()
