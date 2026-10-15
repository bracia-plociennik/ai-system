"""Public installer behavior on artificial homes; never reads provider credentials."""
import copy
import fcntl
import json
import os
from pathlib import Path
import sys
from unittest import mock
import unittest
import test_agent_context as fixtures
ROOT = fixtures.ROOT
sys.path.insert(0, str(ROOT / '.systems/scripts'))
import agent_adapters as adapter

class Adapters(fixtures.AgentContext):
    def setUp(self):
        super().setUp()
        self.asset = self.personal / 'owned-assets/asset'
        self.asset.mkdir(parents=True)
        for rel in adapter.SOURCE_FILES:
            self.put(self.system / rel, (ROOT / rel).read_text())
        self.agents = self.home / '.codex/AGENTS.md'
        self.registration.unlink()

    def plan(self):
        return adapter.build_plan(self.system, 'personal', 'asset', user_home=self.home,
                                  codex_home=self.home / '.codex')

    def inspect(self):
        return adapter.inspect_adapter(user_home=self.home, codex_home=self.home / '.codex')

    def test_plan_read_only_apply_idempotent_disable_restore(self):
        self.put(self.agents, '# My instructions\n')
        before = sorted(str(x) for x in self.home.rglob('*'))
        plan = self.plan()
        self.assertEqual(before, sorted(str(x) for x in self.home.rglob('*')))
        with self.assertRaises(adapter.ContextError): adapter.apply_plan(plan)
        self.assertEqual(adapter.apply_plan(plan, approved=True)['status'], 'applied')
        self.assertTrue(self.inspect()['active'])
        self.assertEqual(adapter.apply_plan(plan, approved=True)['status'], 'noop')
        self.agents.write_text(self.agents.read_text() + '\nNew personal rule.\n')
        adapter.disable_adapter(user_home=self.home, approved=True)
        self.assertFalse(self.inspect()['active'])
        adapter.restore_receipt(Path(plan['receipt']), approved=True, user_home=self.home)
        self.assertEqual(self.agents.read_text(), '# My instructions\n\nNew personal rule.\n')
        self.assertFalse(self.registration.exists())
        self.assertEqual(adapter.restore_receipt(Path(plan['receipt']), approved=True)['status'], 'noop')

    def test_each_interrupted_apply_can_resume_without_duplicate_fragment(self):
        original = adapter.atomic_write
        for fail_at in range(1, 6):
            with self.subTest(fail_at=fail_at):
                plan = self.plan(); calls = [0]
                def interrupted(*args, **kwargs):
                    calls[0] += 1
                    if calls[0] == fail_at: raise OSError('synthetic interruption')
                    return original(*args, **kwargs)
                with mock.patch.object(adapter, 'atomic_write', side_effect=interrupted):
                    with self.assertRaises(OSError): adapter.apply_plan(plan, approved=True)
                if Path(plan['receipt']).exists():
                    self.assertNotEqual(json.loads(Path(plan['receipt']).read_text())['status'], 'applied')
                adapter.apply_plan(plan, approved=True)
                self.assertTrue(self.inspect()['active'])
                self.assertEqual(self.agents.read_text().count(adapter.START), 1)
                adapter.restore_receipt(Path(plan['receipt']), approved=True)

    def test_each_interrupted_restore_can_resume_and_keeps_external_edits(self):
        original = adapter.atomic_write
        for fail_at in range(1, 5):
            with self.subTest(fail_at=fail_at):
                self.put(self.agents, '# Kept\n')
                plan = self.plan(); adapter.apply_plan(plan, approved=True)
                self.agents.write_text(self.agents.read_text() + '\nLater rule\n')
                calls = [0]
                def interrupted(*args, **kwargs):
                    calls[0] += 1
                    if calls[0] == fail_at: raise OSError('synthetic interruption')
                    return original(*args, **kwargs)
                with mock.patch.object(adapter, 'atomic_write', side_effect=interrupted):
                    with self.assertRaises(OSError): adapter.restore_receipt(Path(plan['receipt']), approved=True)
                adapter.restore_receipt(Path(plan['receipt']), approved=True)
                self.assertEqual(self.agents.read_text(), '# Kept\n\nLater rule\n')
                self.assertFalse(self.registration.exists())

    def test_user_edit_after_plan_or_inside_fragment_is_never_overwritten(self):
        self.put(self.agents, '# Kept')
        plan = self.plan(); self.agents.write_text('# Changed')
        with self.assertRaises(adapter.ContextError): adapter.apply_plan(plan, approved=True)
        self.assertEqual(self.agents.read_text(), '# Changed')
        plan = self.plan(); adapter.apply_plan(plan, approved=True)
        changed = self.agents.read_text().replace('AI System startup marker:', 'User changed startup marker:')
        self.assertNotEqual(changed, self.agents.read_text())
        self.agents.write_text(changed)
        with self.assertRaises(adapter.ContextError): adapter.restore_receipt(Path(plan['receipt']), approved=True)
        self.assertEqual(self.agents.read_text(), changed)

    def test_source_change_disables_current_claim_but_preserves_restore(self):
        plan = self.plan(); adapter.apply_plan(plan, approved=True)
        with (self.system / adapter.SOURCE_FILES[0]).open('a') as out: out.write('\nChanged policy\n')
        self.assertFalse(self.inspect()['active'])
        with self.assertRaises(adapter.ContextError): adapter.apply_plan(plan, approved=True)
        adapter.restore_receipt(Path(plan['receipt']), approved=True)
        self.assertFalse(self.agents.exists())

    def test_shadows_unsafe_links_budget_and_other_tools(self):
        self.put(self.home / '.codex/AGENTS.override.md', 'Override')
        with self.assertRaises(adapter.ContextError): self.plan()
        (self.home / '.codex/AGENTS.override.md').unlink()
        self.put(self.agents, 'x' * 16384)
        with self.assertRaises(adapter.ContextError): self.plan()
        self.agents.unlink(); self.agents.symlink_to(self.system / 'ai-system.local.json')
        with self.assertRaises(adapter.ContextError): self.plan()
        for tool in ('claude-code', 'generic'):
            out = adapter.inspect_adapter(tool=tool)
            self.assertEqual(out['native_verification'], 'unverified')
            self.assertFalse(out['activation_supported'])

    def test_editor_during_apply_is_preserved_and_activation_stays_incomplete(self):
        self.put(self.agents, '# Original')
        plan = self.plan(); original = adapter.atomic_write
        def editor(path, data, *args, **kwargs):
            result = original(path, data, *args, **kwargs)
            if Path(path) == self.registration and json.loads(data)['enabled'] is False:
                self.agents.write_text('# Concurrent user edit')
            return result
        with mock.patch.object(adapter, 'atomic_write', side_effect=editor):
            with self.assertRaises(adapter.ContextError): adapter.apply_plan(plan, approved=True)
        self.assertEqual(self.agents.read_text(), '# Concurrent user edit')
        self.assertFalse(json.loads(self.registration.read_text())['enabled'])

    def test_editor_during_restore_is_preserved(self):
        self.put(self.agents, '# Original')
        plan = self.plan(); adapter.apply_plan(plan, approved=True)
        original = adapter.atomic_write
        def editor(path, data, *args, **kwargs):
            result = original(path, data, *args, **kwargs)
            if Path(path) == self.registration and json.loads(data)['enabled'] is False:
                self.agents.write_text(self.agents.read_text() + '\nConcurrent edit\n')
            return result
        with mock.patch.object(adapter, 'atomic_write', side_effect=editor):
            with self.assertRaises(adapter.ContextError): adapter.restore_receipt(Path(plan['receipt']), approved=True)
        self.assertIn('Concurrent edit', self.agents.read_text())
        self.assertFalse(json.loads(self.registration.read_text())['enabled'])

    def pending_plan(self):
        plan = self.plan(); original = adapter.atomic_write
        def interrupt(path, *args, **kwargs):
            if Path(path) == self.agents: raise OSError('synthetic interruption')
            return original(path, *args, **kwargs)
        with mock.patch.object(adapter, 'atomic_write', side_effect=interrupt):
            with self.assertRaises(OSError): adapter.apply_plan(plan, approved=True)
        return plan

    def test_resume_rechecks_management_role(self):
        plan = self.pending_plan()
        self.put(self.system / 'ai-system.local.json', json.dumps(dict(schema_version=1, role='development')))
        with self.assertRaises(adapter.ContextError): adapter.apply_plan(plan, approved=True)
        self.assertFalse(json.loads(self.registration.read_text())['enabled'])

    def test_resume_rechecks_source_capability(self):
        plan = self.pending_plan()
        (self.system / '.systems/ai/capabilities/agent-startup-v1.json').unlink()
        with self.assertRaises(adapter.ContextError): adapter.apply_plan(plan, approved=True)
        self.assertFalse(json.loads(self.registration.read_text())['enabled'])

    def test_restore_and_refresh_allow_known_previous_fragment_text(self):
        plan = self.plan(); adapter.apply_plan(plan, approved=True)
        original = adapter.fragment
        def next_template(*args):
            return original(*args).replace('One human/', 'One verified human/')
        with mock.patch.object(adapter, 'fragment', side_effect=next_template):
            fresh = self.plan()
            self.assertEqual(fresh['old_fragment'], plan['fragment'])
            adapter.restore_receipt(Path(plan['receipt']), approved=True)
        self.assertFalse(self.agents.exists())

    def test_boolean_receipt_version_is_rejected(self):
        plan = self.plan(); adapter.apply_plan(plan, approved=True)
        receipt = Path(plan['receipt']);value = json.loads(receipt.read_text());value['schema_version'] = True
        receipt.write_text(json.dumps(value))
        with self.assertRaises(adapter.ContextError): self.inspect()

    def test_concurrent_lock_and_no_secret_backup(self):
        self.put(self.home / '.codex/auth.json', 'SYNTHETIC_SECRET_NEVER_READ')
        self.put(self.agents, 'SYNTHETIC_PRIVATE_RULE')
        plan = self.plan()
        with adapter.writer_lock(self.home):
            with self.assertRaises(adapter.ContextError): adapter.apply_plan(plan, approved=True)
        adapter.apply_plan(plan, approved=True)
        receipt = Path(plan['receipt']).read_text()
        self.assertNotIn('SYNTHETIC_SECRET_NEVER_READ', receipt)
        self.assertNotIn('SYNTHETIC_PRIVATE_RULE', receipt)

# Context cases are tested in their own suite, not inherited under installer fixtures.
for name in list(fixtures.AgentContext.__dict__):
    if name.startswith('test_'): setattr(Adapters, name, None)
if __name__ == '__main__': unittest.main()
