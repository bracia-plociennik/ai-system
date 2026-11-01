"""Black-box routing/isolation regressions on synthetic, independently owned repos."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('shared_runtime', SCRIPTS / 'durable_runtime.py')
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


class SharedInstallation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='shared-workflow-')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.system = self.base / 'system with spaces'
        self.repo(self.system)
        self.put(self.system / 'ai-system.local.json', {'schema_version': 1, 'role': 'management'})
        self.registration = self.base / '.config/ai-system/installation.json'
        self.put(self.registration, dict(schema_version=1, enabled=True,
                 system_id='synthetic', system_home=str(self.system), adapter_ids=['codex'],
                 owner_workspace_id='owner', owner_asset_id='host'))
        self.config = self.system / 'ai-workflow-workspace/shared-installation.json'
        self.put(self.config, dict(schema_version=1, enabled=True, workflow_home='ai-workflow'))
        self.workflow = self.system / 'ai-workflow'
        self.repo(self.workflow)
        for rel in ('AGENTS.md', '.systems/ai/core/risk-model.md',
                    '.systems/ai/core/repository-modes.md'):
            self.put(self.workflow / rel, '# Synthetic trusted installation\n')
        self.scripts = self.workflow / '.systems/scripts'
        self.scripts.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SCRIPTS / 'durable_runtime.py', self.scripts)
        resolver = SCRIPTS / 'resolve-workflow-env'
        # The System product shares the same neutral consumer; shell lives in Workflow.
        if resolver.exists():
            shutil.copy2(resolver, self.scripts)
        else:
            self.put(self.scripts / 'resolve-workflow-env', '# Synthetic mode contract\n')
        self.one = self.system / 'projects/one'
        self.two = self.system / 'projects/two with spaces'
        self.repo(self.one)
        self.repo(self.two)
        self.env = {k: v for k, v in os.environ.items()
                    if not k.startswith(('AI_SYSTEM_', 'AI_WORKFLOW_', 'TARGET_REPO_ROOT'))}
        self.env.update(HOME=str(self.base), PYTHONDONTWRITEBYTECODE='1')

    def put(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value) if isinstance(value, dict) else value)

    def repo(self, path):
        path.mkdir(parents=True, exist_ok=True)
        subprocess.run(['git', 'init', '-q', str(path)], check=True)
        subprocess.run(['git', '-C', str(path), '-c', 'user.name=Synthetic',
                        '-c', 'user.email=synthetic@example.invalid', 'commit',
                        '--allow-empty', '-qm', 'fixture'], check=True)

    def resolve(self, target=None, **kw):
        return runtime.workflow_environment(self.workflow, target=target, cwd=self.one,
                                            environment=self.env, **kw)

    def test_two_repositories_share_tools_without_sharing_artifacts(self):
        for target in (self.one, self.two, self.system):
            out = self.resolve(target)
            self.assertEqual(out['AI_WORKFLOW_HOME'], str(self.workflow))
            self.assertEqual(out['TARGET_REPO_ROOT'], str(target))
            self.assertEqual(out['AI_WORKFLOW_WORKSPACE_HOME'], str(target / 'ai-workflow-workspace'))
            self.assertEqual(out['AI_WORKFLOW_MODE_RESOLVED'], 'shared')
            self.assertFalse((target / 'ai-workflow-workspace').exists() if target != self.system else False)

    def test_cwd_subdirectory_resolves_actual_git_target(self):
        child = self.two / 'src'; child.mkdir()
        out = runtime.workflow_environment(self.workflow, cwd=child, environment=self.env)
        self.assertEqual(out['TARGET_REPO_ROOT'], str(self.two))

    def test_invalid_configuration_does_not_fall_back_to_nested_clone(self):
        for bad in ({'schema_version': True, 'enabled': True, 'workflow_home': 'ai-workflow'},
                    {'schema_version': 1, 'enabled': 'yes', 'workflow_home': 'ai-workflow'},
                    {'schema_version': 1, 'enabled': True, 'workflow_home': '../elsewhere'},
                    {'schema_version': 1, 'enabled': True, 'workflow_home': 'ai-workflow', 'approved': True}):
            with self.subTest(config=bad):
                self.put(self.config, bad)
                with self.assertRaises(ValueError):
                    self.resolve(self.one)

    def test_missing_disabled_and_unavailable_installation_are_rejected_in_shared_mode(self):
        self.config.unlink()
        with self.assertRaises(ValueError):
            self.resolve(self.one, mode='shared')
        self.put(self.config, dict(schema_version=1, enabled=False, workflow_home='ai-workflow'))
        with self.assertRaises(ValueError):
            self.resolve(self.one, mode='shared')
        self.put(self.config, dict(schema_version=1, enabled=True, workflow_home='ai-workflow'))
        (self.workflow / 'AGENTS.md').unlink()
        with self.assertRaises(ValueError):
            self.resolve(self.one)

    def test_external_target_and_symlink_alias_are_rejected(self):
        outside = self.base / 'outside'; self.repo(outside)
        with self.assertRaises(ValueError):
            self.resolve(outside)
        alias = self.system / 'alias'; alias.symlink_to(self.one, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.resolve(alias)
        original = self.config.read_text(); self.config.unlink()
        alternate = self.base / 'alternate.json'; alternate.write_text(original)
        self.config.symlink_to(alternate)
        with self.assertRaises(ValueError):
            self.resolve(self.one)

    def test_non_git_target_and_installation_as_target_are_rejected(self):
        child = self.one / 'directory'; child.mkdir()
        for target in (child, self.workflow):
            with self.subTest(target=target), self.assertRaises(ValueError):
                self.resolve(target)

    def test_official_source_mode_stays_separate(self):
        out = self.resolve(mode='official')
        self.assertEqual(out['TARGET_REPO_ROOT'], str(self.workflow))
        self.assertEqual(out['AI_WORKFLOW_MODE_RESOLVED'], 'official')

    def test_workspace_override_cannot_mix_unbound_project_artifacts(self):
        with self.assertRaises(ValueError):
            self.resolve(self.one, workspace=str(self.two / 'ai-workflow-workspace'))
        out = self.resolve(self.one, workspace='ai-workflow-workspace')
        self.assertEqual(out['AI_WORKFLOW_WORKSPACE_HOME'], str(self.one / 'ai-workflow-workspace'))

    def test_inherited_output_target_cannot_override_a_different_project_cwd(self):
        env = dict(self.env, TARGET_REPO_ROOT=str(self.two))
        with self.assertRaises(ValueError):
            runtime.workflow_environment(self.workflow, cwd=self.one, environment=env)
        out = runtime.workflow_environment(self.workflow, cwd=self.one, target=self.two, environment=env)
        self.assertEqual(out['TARGET_REPO_ROOT'], str(self.two))

    def test_standalone_outside_system_does_not_depend_on_shared_configuration(self):
        standalone = self.base / 'standalone'; self.repo(standalone)
        self.config.write_text('{broken shared config')
        out = runtime.workflow_environment(standalone, cwd=standalone, environment=self.env)
        self.assertEqual(out['AI_WORKFLOW_MODE_RESOLVED'], 'official')

    @unittest.skipUnless((SCRIPTS / 'resolve-workflow-env').exists(), 'Workflow initialization consumer only')
    def test_shared_initializer_needs_no_clone_and_preserves_existing_artifacts(self):
        product = SCRIPTS.parents[1]
        shutil.copytree(product / '.systems/ai/templates', self.workflow / '.systems/ai/templates')
        shutil.copy2(SCRIPTS / 'init-workspace', self.scripts)
        existing = self.one / 'ai-workflow-workspace/repo/keep.md'
        self.put(existing, '# Existing artifact\n')
        command = [str(self.scripts / 'init-workspace'), '--target', str(self.one)]
        for round_number in range(2):
            result = subprocess.run(command, cwd=self.two, env=self.env, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(existing.read_text(), '# Existing artifact\n')
            self.assertFalse((self.one / 'ai-workflow').exists())
            self.assertFalse((self.two / 'ai-workflow-workspace').exists())
        entry = (self.one / 'AGENTS.md').read_text()
        self.assertIn('shared AI Workflow', entry)
        self.assertNotIn('git clone', entry)

    @unittest.skipUnless((SCRIPTS / 'resolve-workflow-env').exists(), 'Workflow bootstrap consumer only')
    def test_shared_bootstrap_is_idempotent_without_cloning(self):
        shutil.copytree(SCRIPTS.parents[1] / '.systems/ai/templates', self.workflow / '.systems/ai/templates')
        for name in ('bootstrap-target-worktree', 'init-workspace'):
            shutil.copy2(SCRIPTS / name, self.scripts)
        (self.one / 'ai-workflow-workspace').mkdir()
        command = [str(self.scripts / 'bootstrap-target-worktree'), '--target', str(self.one), '--approved']
        for _ in range(2):
            result = subprocess.run(command, cwd=self.two, env=self.env, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse((self.one / 'ai-workflow').exists())

    def test_durable_worktree_retains_canonical_workspace(self):
        worktree = self.system / '.worktrees/one'
        subprocess.run(['git', '-C', str(self.one), 'worktree', 'add', '-q',
                        '-b', 'synthetic', str(worktree)], check=True)
        ws = self.one / 'ai-workflow-workspace'; ws.mkdir()
        record = ws / 'record.json'
        self.put(record, {'task_resource_cleanup': {'schema': 1,
                 'canonical': runtime.identity(self.one), 'workspace': str(ws)}})
        # Fixtures use /tmp; the production durable-root rule is independently tested.
        original = runtime.OS_TEMP_ROOTS
        runtime.OS_TEMP_ROOTS = ()
        try:
            runtime.bind(worktree, self.one, ws, record)
            out = self.resolve(worktree)
            self.assertEqual(out['AI_WORKFLOW_WORKSPACE_HOME'], str(ws))
            with self.assertRaises(ValueError):
                self.resolve(worktree, workspace=str(self.two / 'ai-workflow-workspace'))
        finally:
            runtime.OS_TEMP_ROOTS = original

    @unittest.skipUnless((SCRIPTS / 'resolve-workflow-env').exists(), 'Workflow shell consumer only')
    def test_shell_exports_literal_paths_and_honors_explicit_target(self):
        command = ['bash', str(self.scripts / 'resolve-workflow-env'), '--target', str(self.two)]
        result = subprocess.run(command, cwd=self.one, env=self.env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        values = dict(line.split('=', 1) for line in result.stdout.splitlines())
        self.assertEqual(values['TARGET_REPO_ROOT'], str(self.two))
        self.assertEqual(values['AI_WORKFLOW_WORKSPACE_HOME'], str(self.two / 'ai-workflow-workspace'))


if __name__ == '__main__':
    unittest.main()
