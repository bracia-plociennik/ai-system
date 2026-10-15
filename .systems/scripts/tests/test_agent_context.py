"""Context resolution on synthetic homes; public behavior and non-mutation."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / '.systems/scripts'))
import agent_context as context


class AgentContext(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.system = self.home / 'system'
        self.personal = self.system / 'personal'
        self.company = self.system / 'company'
        self.env = dict(os.environ, HOME=str(self.home))
        self.env.pop('AI_SYSTEM_HOME', None)
        self.env.pop('AI_SYSTEM_WORKSPACE_HOME', None)
        for p in (self.system, self.personal, self.company):
            p.mkdir(parents=True, exist_ok=True)
        self.repo(self.system)
        for rel in context.POLICY:
            self.put(self.system / rel, (ROOT / rel).read_text())
        import hashlib
        for rel in context.CAPABILITY_FILES['agent-startup-v1']:
            self.put(self.system / rel, (ROOT / rel).read_text())
        self.put(self.system / '.systems/ai/capabilities/agent-startup-v1.json', json.dumps(dict(
            schema_version=1, contract='agent-startup-v1',
            source_files={rel: hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
                          for rel in context.CAPABILITY_FILES['agent-startup-v1']},
            native_verification='requires-installation-specific-proof')))
        self.put(self.system / 'ai-system.local.json', json.dumps(dict(schema_version=1, role='management')))
        self.put(self.system / 'ai-system-workspaces.md', '| workspace-id | path | default | status | scope | notes |\n| --- | --- | --- | --- | --- | --- |\n| personal | personal | yes | active | private | synthetic |\n| company | company | no | active | company | synthetic |\n')
        self.record = dict(schema_version=1, system_id='synthetic-system', system_home='${HOME}/system',
                           enabled=True, adapter_ids=['codex'], owner_workspace_id='personal', owner_asset_id='asset')
        self.registration = self.home / '.config/ai-system/installation.json'
        self.put(self.registration, json.dumps(self.record))
        self.app = self.company / 'projects/application'
        self.repo(self.app)
        self.link = self.company / 'project-state/application/links.md'
        self.put(self.link, 'repo-path: ${AI_SYSTEM_WORKSPACE_HOME}/projects/application\n')

    def put(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value)

    def repo(self, path):
        path.mkdir(parents=True, exist_ok=True)
        subprocess.run(['git', 'init', '-q', str(path)], check=True)
        subprocess.run(['git', '-C', str(path), '-c', 'user.name=Synthetic', '-c', 'user.email=synthetic@example.invalid',
                        'commit', '--allow-empty', '-qm', 'fixture'], check=True)

    def resolve(self, cwd=None, **kw):
        return context.resolve_context(str(cwd or self.app), environment=kw.pop('environment', self.env), **kw)

    def test_registered_project_wins_over_personal_default(self):
        out = self.resolve()
        self.assertEqual(out['workspace_root'], str(self.company))
        self.assertEqual(out['project_id'], 'application')
        self.assertEqual(out['context_kind'], 'repository')
        self.assertFalse(out['authorization_assessed'])
        self.assertEqual(out['requested_write_roots'], [])
        self.assertNotIn(str(self.personal), out['read_roots'])

    def test_nonrepository_source_links_do_not_block_registered_or_unknown_repositories(self):
        doc = self.company / 'clients/example/project-state/documents/links.md'
        self.put(doc, 'source-path: ${AI_SYSTEM_WORKSPACE_HOME}/dump/materials\n')
        before = doc.read_bytes()
        out = self.resolve()
        self.assertEqual(out['project_id'], 'application')
        self.assertEqual(out['workspace_root'], str(self.company))
        unknown = self.home / 'unknown'; self.repo(unknown)
        out = self.resolve(unknown)
        self.assertEqual(out['context_kind'], 'unregistered-repository')
        self.assertIsNone(out['workspace_root'])
        self.assertIsNone(out['project_id'])
        self.assertEqual(doc.read_bytes(), before)

    def test_empty_or_duplicate_declared_repository_links_remain_conflicts(self):
        malformed = self.company / 'project-state/invalid/links.md'
        for value in ('repo-path:   \nsource-path: unused\n',
                      'repo-path: first\nrepo-path: second\n'):
            with self.subTest(value=value):
                self.put(malformed, value)
                with self.assertRaises(context.ContextError):
                    self.resolve()

    def test_pending_directory_does_not_inherit_owning_workspace_git_identity(self):
        self.repo(self.company)
        pending = self.company / 'projects/pending'; pending.mkdir(parents=True)
        self.put(self.company / 'project-state/pending/links.md',
                 'repo-path: ${AI_SYSTEM_WORKSPACE_HOME}/projects/pending\nsource-availability: pending\n')
        before = sorted(pending.iterdir())
        self.assertEqual(self.resolve()['project_id'], 'application')
        unknown = self.home / 'unknown'; self.repo(unknown)
        self.assertEqual(self.resolve(unknown)['context_kind'], 'unregistered-repository')
        self.assertEqual(self.resolve(pending)['context_kind'], 'unregistered-repository')
        self.assertEqual(sorted(pending.iterdir()), before)
        # An actual broken Git marker remains a conflict, never silently accepted.
        (pending / '.git').mkdir()
        with self.assertRaises(context.ContextError):
            self.resolve()

    def test_management_and_personal_have_no_workflow_self_clone(self):
        out = self.resolve(self.system)
        self.assertEqual(out['context_kind'], 'management')
        self.assertEqual(out['checkout_role'], 'management')
        self.assertIsNone(out['workflow_home'])
        self.assertEqual(out['workspace_root'], str(self.personal))

    def test_subdirectory_and_worktree_keep_identity_and_actual_root(self):
        sub = self.app / 'src'; sub.mkdir()
        self.assertEqual(self.resolve(sub)['repository_root'], str(self.app))
        tree = self.home / '.worktrees/application'
        subprocess.run(['git', '-C', str(self.app), 'worktree', 'add', '-q', '-b', 'synthetic-tree', str(tree)], check=True)
        out = self.resolve(tree)
        self.assertEqual(out['context_kind'], 'worktree')
        self.assertEqual(out['repository_root'], str(tree))
        self.assertEqual(out['workspace_root'], str(self.company))

    def test_explicit_or_env_owner_conflicts_fail_without_redirect(self):
        with self.assertRaises(context.ContextError) as error:
            self.resolve(workspace=str(self.personal))
        self.assertEqual(error.exception.code, 4)
        with self.assertRaises(context.ContextError):
            self.resolve(environment=dict(self.env, AI_SYSTEM_WORKSPACE_HOME=str(self.personal)))

    def test_unknown_repository_does_not_enroll_or_load_default_workspace(self):
        unknown = self.home / 'unknown'; self.repo(unknown)
        before = sorted(unknown.iterdir())
        out = self.resolve(unknown)
        self.assertEqual(out['context_kind'], 'unregistered-repository')
        self.assertIsNone(out['workspace_root'])
        self.assertIsNone(out['project_id'])
        self.assertEqual(sorted(unknown.iterdir()), before)

    def test_official_workflow_and_nested_workflow_are_distinguished(self):
        for root in (self.app, self.app / 'ai-workflow'):
            self.put(root / '.systems/scripts/resolve-workflow-env', '# synthetic')
            self.put(root / '.systems/ai/core/repository-modes.md', '# synthetic')
            self.put(root / 'AGENTS.md', '# synthetic')
        self.assertEqual(self.resolve()['workflow_mode'], 'official')
        (self.app / '.systems/scripts/resolve-workflow-env').unlink()
        self.repo(self.app / 'ai-workflow')
        self.assertEqual(self.resolve()['workflow_mode'], 'target')

    def test_invalid_registration_keys_types_duplicates_and_variables(self):
        for change in ({'approved': True}, {'schema_version': True}, {'schema_version': 99},
                       {'system_home': '${UNKNOWN}/system'}, {'system_home': '${AI_SYSTEM_HOME}'},
                       {'enabled': 'yes'}, {'adapter_ids': ['codex', 'codex']}):
            with self.subTest(change=change):
                self.put(self.registration, json.dumps(dict(self.record, **change)))
                with self.assertRaises((context.ContextError, context.LocalPathError)):
                    self.resolve()
        self.put(self.registration, '{"schema_version":1,"schema_version":1}')
        with self.assertRaises(context.ContextError):
            self.resolve()

    def test_missing_disabled_mismatched_and_development_installation(self):
        with self.assertRaises(context.ContextError):
            self.resolve(environment=dict(self.env, AI_SYSTEM_HOME=str(self.home / 'elsewhere')))
        self.put(self.system / 'ai-system.local.json', json.dumps(dict(schema_version=1, role='development')))
        with self.assertRaises(context.ContextError):
            self.resolve()
        self.put(self.system / 'ai-system.local.json', json.dumps(dict(schema_version=1, role='management')))
        self.put(self.registration, json.dumps(dict(self.record, enabled=False)))
        self.assertEqual(self.resolve()['binding_status'], 'unavailable')
        self.registration.unlink()
        with self.assertRaises(context.ContextError) as error:
            self.resolve()
        self.assertEqual(error.exception.code, 3)

    def test_symlink_and_traversal_are_rejected(self):
        self.registration.rename(self.registration.with_suffix('.original'))
        self.registration.symlink_to(self.registration.with_suffix('.original'))
        with self.assertRaises(context.ContextError):
            self.resolve()
        with self.assertRaises(context.ContextError):
            context.concrete(str(self.home / '..' / 'foreign'))



class StartupObservations(AgentContext):
    def test_registered_development_role_is_local_not_management(self):
        self.put(self.app / 'ai-system.local.json', json.dumps(dict(schema_version=1,role='development')))
        out = self.resolve()
        self.assertEqual(out['checkout_role'], 'development')
        self.assertEqual(out['binding_status'], 'resolved')
        self.assertEqual(out['requested_write_roots'], [])

    def test_missing_consumer_and_unknown_capability_are_inspect_only(self):
        for rel in ('.systems/scripts/resolve-workflow-env','.systems/ai/core/repository-modes.md','AGENTS.md'):
            self.put(self.app / rel, '# Synthetic')
        out = self.resolve()
        self.assertEqual(out['workflow_mode'], 'official')
        self.assertEqual(out['binding_status'], 'unavailable')
        self.assertIn('bound Workflow consumer source is not verified', out['unresolved'])
        self.assertEqual(context.source_consistency(self.system, 'unknown.json', 'unknown-v9'), 'unsupported')

    def test_shadow_and_budget_are_observed_without_mutation(self):
        self.put(self.app / 'AGENTS.md', '# Normal')
        self.put(self.app / 'AGENTS.override.md', '# Override')
        out = self.resolve()
        self.assertEqual(out['binding_status'], 'unavailable')
        self.assertEqual(out['instruction_chain']['files'][0]['path'], str(self.app / 'AGENTS.override.md'))
        (self.app / 'AGENTS.override.md').unlink()
        self.put(self.app / 'AGENTS.md', 'x' * 16385)
        self.assertEqual(self.resolve()['binding_status'], 'unavailable')
        self.assertEqual((self.app / 'AGENTS.md').stat().st_size, 16385)

    def test_source_fingerprint_ignores_head_and_detects_relevant_bytes(self):
        path = self.system / '.systems/ai/capabilities/agent-startup-v1.json'
        import hashlib
        rel = context.POLICY[0]
        for name in context.CAPABILITY_FILES['agent-startup-v1']:
            self.put(self.system / name, (ROOT / name).read_text())
        self.put(path, json.dumps(dict(schema_version=1, contract='agent-startup-v1',
            source_files={name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in context.CAPABILITY_FILES['agent-startup-v1']},
            native_verification='requires-installation-specific-proof')))
        self.assertEqual(self.resolve()['capabilities']['system_source'], 'verified-source')
        subprocess.run(['git', '-C', str(self.system), '-c', 'user.name=Synthetic', '-c',
                        'user.email=synthetic@example.invalid', 'commit', '--allow-empty', '-qm', 'unrelated'], check=True)
        self.assertEqual(self.resolve()['capabilities']['system_source'], 'verified-source')
        with (self.system / rel).open('a') as out: out.write('\nChanged\n')
        self.assertEqual(self.resolve()['capabilities']['system_source'], 'mismatch')

# Avoid running the base cases twice through inheritance.
for _name in list(AgentContext.__dict__):
    if _name.startswith('test_'): setattr(StartupObservations, _name, None)

if __name__ == '__main__': unittest.main()
