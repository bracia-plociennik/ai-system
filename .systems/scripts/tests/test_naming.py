"""Synthetic ownership and fail-closed regressions; no real private sources."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('naming_check', SCRIPTS / 'naming_check.py')
naming = importlib.util.module_from_spec(spec)
spec.loader.exec_module(naming)


class NamingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='naming-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'
        self.workspace = self.root / 'workspace'
        self.repo.mkdir()
        self.workspace.mkdir()

    def put(self, root, relative, data='synthetic source\n'):
        file = root / relative
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(data)
        return file

    def check(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return naming.check(self.repo, self.workspace)

    def git(self, *args, root=None):
        return subprocess.check_output(['git', '-C', str(root or self.workspace), *args], stderr=subprocess.DEVNULL, text=True).strip()

    def historical(self):
        file = self.put(self.workspace, 'Old input.md')
        self.git('init', '-q')
        self.git('add', '--', file.name)
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'historical input')
        return {'path': file.name, 'sha256': hashlib.sha256(file.read_bytes()).hexdigest(),
                'source_commit': self.git('rev-parse', 'HEAD'), 'disposition': 'preserved-unclassified'}

    def register(self, entries):
        return self.put(self.workspace, naming.PRESERVATION, json.dumps({'schema_version': 1, 'inputs': entries}))

    def test_source_contracts_are_root_relative(self):
        for path in ('AGENTS.md', 'HUMANS.md', '.systems/ai/templates/root/AGENTS.template.md', '.systems/ai/skills/example/SKILL.md'):
            self.put(self.repo, path)
        self.assertEqual(self.check(), [])
        self.put(self.repo, 'other/AGENTS.md')
        self.assertTrue(self.check())

    def test_nearest_owner_skills_and_raw_context(self):
        for owner in ('', 'clients/example/', 'owned-assets/example/'):
            self.put(self.workspace, owner + 'skills/example/SKILL.md')
            self.put(self.workspace, owner + 'skills/example/context/RAW_Import.md')
        self.assertEqual(self.check(), [])

    def test_noncanonical_skill_names_and_resources_reject(self):
        for path in ('skills/example/nested/SKILL.md', 'skills/Bad_Name/SKILL.md', 'skills/example/references/Bad Resource.md', 'clients/example/skills/example/SKILLS.md'):
            with self.subTest(path=path):
                file = self.put(self.workspace, path)
                self.assertTrue(self.check())
                file.unlink()

    def test_foreign_sources_and_history_remain_unchanged(self):
        files = []
        for owner in ('', 'clients/example/', 'owned-assets/example/'):
            for path in ('projects/arbitrary/AGENTS.md', 'projects/arbitrary/skills/example/SKILL.md', 'context/Original Title.md', 'documents/Imported Document.md', 'assets/Brand Book.md', 'dump/incoming/Original_Input.md', 'archive/Old Title.md', 'project-state/example/release/tests/source/HUMANS.md', 'project-state/example/release/backups/OLD_STATUS.md', 'capture-state/history/OLD_CAPTURE.md'):
                files.append(self.put(self.workspace, owner + path))
        before = {str(p): p.read_bytes() for p in files}
        self.assertEqual(self.check(), [])
        self.assertEqual(before, {str(p): p.read_bytes() for p in files})

    def test_actual_owner_and_project_state_artifacts_stay_strict(self):
        for path in ('core/Bad Status.md', 'notes/New Note.md', 'tasks/Bad_Task.md', 'dump/Bad Classification.md', 'clients/example/Bad Status.md', 'owned-assets/example/decisions/Bad Decision.md', 'project-state/example/status_BAD.md', 'project-state/example/quality/Bad QA.md', 'project-state/example/capture-state/Bad Capture.md', 'project-state/example/release/Bad Result.md', 'capture-state/Bad Capture.md'):
            with self.subTest(path=path):
                file = self.put(self.workspace, path)
                self.assertTrue(self.check())
                file.unlink()

    def test_unknown_loose_input_rejects(self):
        self.put(self.workspace, 'Unknown input.md')
        self.assertTrue(self.check())

    def test_silverbullet_task_titles_keep_native_names(self):
        relative = 'tasks/silverbullet/tasks/example-client/demo-project/Zapłacić fakturę.md'
        page = self.put(self.workspace, relative)
        original = page.read_bytes()
        self.assertEqual(self.check(), [])
        self.assertEqual(page.read_bytes(), original)
        page.unlink()
        page.symlink_to(self.put(self.root, 'outside/title.md'))
        with self.assertRaisesRegex(ValueError, 'Linked naming input'):
            self.check()

    def test_silverbullet_title_exception_is_exact_and_workspace_only(self):
        for relative in (
            'tasks/silverbullet/views/Bad View.md',
            'tasks/silverbullet/tasks/client/Bad Task.md',
            'tasks/silverbullet/tasks/client/project/nested/Bad Task.md',
            'project-state/example/tasks/silverbullet/tasks/client/project/Bad Task.md',
        ):
            with self.subTest(relative=relative):
                page = self.put(self.workspace, relative)
                self.assertTrue(self.check())
                page.unlink()
        self.put(self.repo, 'tasks/silverbullet/tasks/client/project/Bad Task.md')
        self.assertTrue(self.check())

    def test_disposable_execution_roots_are_not_managed_artifacts(self):
        outside = self.put(self.root, 'outside/Original_Input.md')
        before = outside.read_bytes()
        for slot in ('.tmp', '.worktrees'):
            for owner in ('', 'clients/example/', 'owned-assets/example/'):
                self.put(self.workspace, owner + slot + '/task/Original_Input.md')
                link = self.workspace / owner / slot / 'task/auth.json'
                link.symlink_to(outside)
        self.assertEqual(self.check(), [])
        self.assertEqual(outside.read_bytes(), before)
        self.put(self.workspace, 'project-state/example/.tmp/Bad_QA.md')
        self.assertTrue(self.check())

    def test_disposable_root_itself_cannot_redirect_owner_boundary(self):
        outside = self.root / 'outside'
        outside.mkdir()
        for slot in ('.tmp', '.worktrees'):
            with self.subTest(slot=slot):
                link = self.workspace / slot
                link.symlink_to(outside, target_is_directory=True)
                with self.assertRaisesRegex(ValueError, 'Linked naming input'):
                    self.check()
                link.unlink()

    def test_exact_historical_input_is_visible_and_immutable(self):
        entry = self.historical()
        self.register([entry])
        before = (self.workspace / entry['path']).read_bytes()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(naming.check(self.repo, self.workspace), [])
        self.assertIn('Preserved historical unclassified naming input:', out.getvalue())
        self.assertEqual((self.workspace / entry['path']).read_bytes(), before)

    def test_changed_missing_or_unproven_historical_input_fails(self):
        entry = self.historical()
        self.register([entry])
        self.put(self.workspace, entry['path'], 'changed\n')
        with self.assertRaisesRegex(ValueError, 'changed'):
            self.check()
        entry['sha256'] = hashlib.sha256((self.workspace / entry['path']).read_bytes()).hexdigest()
        self.register([entry])
        with self.assertRaisesRegex(ValueError, 'provenance'):
            self.check()
        (self.workspace / entry['path']).unlink()
        with self.assertRaisesRegex(ValueError, 'Missing'):
            self.check()

    def test_registry_cannot_admit_managed_files_or_escape(self):
        entry = self.historical()
        for path in ('status.md', 'memory.md', 'AGENTS.md', 'core/Bad Status.md', '../Old input.md', '/Old input.md', '*/Bad.md', 'normal.md'):
            with self.subTest(path=path):
                self.register([{**entry, 'path': path}])
                with self.assertRaises(ValueError):
                    self.check()

    def test_duplicate_schema_and_bad_identity_fail(self):
        entry = self.historical()
        for entries in ([entry, entry], [{**entry, 'sha256': 'bad'}], [{**entry, 'source_commit': '0' * 40}], [{**entry, 'disposition': 'approved'}]):
            self.register(entries)
            with self.assertRaises(ValueError):
                self.check()
        manifest = self.register([entry])
        manifest.write_text('{"schema_version":1,"schema_version":1,"inputs":[]}')
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            self.check()
        manifest.write_text('{"schema_version":true,"inputs":[]}')
        with self.assertRaises(ValueError):
            self.check()

    def test_links_and_source_boundary_aliases_fail_without_reading_target(self):
        outside = self.root / 'outside'
        outside.mkdir()
        self.put(outside, 'Bad Name.md')
        for relative in ('notes', 'projects', 'clients/example/projects', 'core'):
            link = self.workspace / relative
            link.parent.mkdir(parents=True, exist_ok=True)
            link.symlink_to(outside, target_is_directory=True)
            with self.subTest(relative=relative):
                with self.assertRaisesRegex(ValueError, 'Linked'):
                    self.check()
            link.unlink()
        manifest = self.workspace / naming.PRESERVATION
        manifest.parent.mkdir(exist_ok=True)
        manifest.symlink_to(self.put(outside, 'registry.json', '{}'))
        with self.assertRaisesRegex(ValueError, 'Linked'):
            self.check()

    def test_git_index_rejects_deleted_noncanonical_source(self):
        self.git('init', '-q', root=self.repo)
        file = self.put(self.repo, 'Bad Source.md')
        self.git('add', '--', file.name, root=self.repo)
        file.unlink()
        self.assertTrue(any('git-index' in error for error in self.check()))

    def test_selected_workspace_only_and_private_source_pruning(self):
        other = self.root / 'other'
        self.put(other, 'core/Bad Status.md')
        private = self.repo / 'private'
        self.put(private, 'Raw Input.md')
        self.assertEqual(naming.check(self.repo, self.workspace, [private]), [])
        self.assertTrue(naming.check(self.repo, self.workspace))

    def test_product_legacy_and_skill_context_only(self):
        self.put(self.repo, '.systems/ai/skills/legacy/old/OLD.md')
        self.put(self.repo, '.systems/ai/skills/example/context/RAW.md')
        self.assertEqual(self.check(), [])
        self.put(self.repo, '.systems/ai/core/Bad Contract.md')
        self.assertTrue(self.check())

    def test_canonical_task_titles_and_iso_week_routes(self):
        for path in ('tasks/TaskForge.md', 'tasks/TaskNotes/Tasks/A title with spaces.md',
                     'tasks/archive/old/Original Title.md',
                     'tasks/migration-reports/old/backups/Original Task.md',
                     'tasks/migration-reports/old/removed-tasknotes/Original Task.md',
                     'tasks/weekly-plans/2026/2026-W34.md',
                     'personal-ops/weekly-check-ins-v4/2026/2026-W41.md'):
            self.put(self.workspace, path)
        self.assertEqual(self.check(), [])
        for path in ('tasks/weekly-plans/2026/2026-W54.md',
                     'tasks/weekly-plans/2025/2026-W34.md',
                     'tasks/TaskNotes/Bad Task.md',
                     'tasks/migration-reports/old/Bad Report.md'):
            with self.subTest(path=path):
                file = self.put(self.workspace, path)
                self.assertTrue(self.check())
                file.unlink()

    def test_canonical_aggregate_links_are_contained_and_preserved(self):
        index = self.workspace / 'personal-ops/indexes'
        generation = index / 'generations-v4' / ('a' * 24)
        generation.mkdir(parents=True)
        for name in naming.V4_FILES:
            self.put(generation, name)
            (index / name).symlink_to('check-ins-v4-active/' + name)
        pointer = index / 'check-ins-v4-active'
        pointer.symlink_to('generations-v4/' + ('a' * 24), target_is_directory=True)
        self.assertEqual(self.check(), [])
        pointer.unlink()
        pointer.symlink_to('../outside')
        with self.assertRaisesRegex(ValueError, 'pointer target'):
            self.check()

    def test_aggregate_link_cannot_alias_another_file(self):
        index = self.workspace / 'personal-ops/indexes'
        generation = index / 'generations-v4' / ('a' * 24)
        generation.mkdir(parents=True)
        (index / 'check-ins-v4-active').symlink_to('generations-v4/' + ('a' * 24))
        (index / 'check-ins-v4.md').symlink_to('other.md')
        with self.assertRaisesRegex(ValueError, 'compatibility link'):
            self.check()


if __name__ == '__main__':
    unittest.main()
