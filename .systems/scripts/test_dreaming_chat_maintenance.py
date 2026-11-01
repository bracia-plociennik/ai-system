"""Behavioral maintenance controls; all repositories and tracker data are synthetic."""
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import time
import unittest
import sys
from unittest.mock import patch

import dreaming_maintenance as maintenance
import dreaming_chat as chat
import dreaming_chat_dispatch as dispatch


class Maintenance(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        # Synthetic repos must not inherit runner/owner filters or credentials.
        git_config = self.root / 'gitconfig'; git_config.write_text('')
        isolated_git = patch.dict(os.environ, {'GIT_CONFIG_GLOBAL': str(git_config),
                                               'GIT_CONFIG_NOSYSTEM': '1'})
        isolated_git.start(); self.addCleanup(isolated_git.stop)
        self.home = Path(__file__).parent.parent.parent
        self.workflow = self.root / 'workflow'
        lib = self.workflow / '.systems/scripts/lib'; lib.mkdir(parents=True)
        (lib / 'dreaming-maintenance.py').write_text('# synthetic consumer')
        self.workspace = self.root / 'owner'; self.workspace.mkdir()
        self.policy = {'schema_version': 1, 'authority_ref': 'synthetic-human-plan',
            'workflow_home': str(self.workflow), 'system_home': str(self.home),
            'workspaces': {'owner': {'root': str(self.workspace),
                'remote_url': 'https://github.com/example/private.git', 'branch': 'main', 'sync_paths': ['notes.md']}},
            'products': {}, 'artifact_scopes': {},
            'operations': [{'id': 'tracker', 'kind': 'tracker-refresh', 'target': 'owner'}]}
        self.config = self.root / 'policy.json'; chat.atomic(self.config, self.policy)
        self.state = self.root / 'state.json'
        maintenance.start(self.config, self.state, 'chat-2026-11-01')

    def operator(self): return maintenance.Operator(self.config, self.state)

    def test_restart_retains_deadlines_and_policy_revocation_blocks(self):
        old = chat.load(self.state)
        again = maintenance.start(self.config, self.state, 'chat-2026-11-01', time.time() + 100)
        self.assertEqual(old['deadline'], again['deadline'])
        self.assertEqual(old['maintenance_deadline'] - old['started_at'], 2700)
        self.assertEqual(old['deadline'] - old['started_at'], 7200)
        self.policy['authority_ref'] = 'changed'; chat.atomic(self.config, self.policy)
        with self.assertRaisesRegex(ValueError, 'maintenance-policy-revoked'): self.operator()

    def test_unknown_shell_and_wildcard_inventory_rejected(self):
        for operation in [{'id': 'shell', 'kind': 'shell', 'target': 'owner'},
                          {'id': 'shell', 'kind': 'tracker-refresh', 'target': 'owner', 'argv': ['true']}]:
            self.policy['operations'] = [operation]; chat.atomic(self.config, self.policy)
            with self.assertRaises(ValueError): maintenance.policy(self.config)
        with self.assertRaises(ValueError): maintenance.sync_path(self.workspace, '*.md', exists=False)
        self.policy['schema_version']=True;chat.atomic(self.config,self.policy)
        with self.assertRaises(ValueError):maintenance.policy(self.config)

    def test_deadline_and_clock_rollback_block_operations(self):
        state = chat.load(self.state); state['maintenance_deadline'] = time.time() - 1; chat.atomic(self.state, state)
        with self.assertRaisesRegex(ValueError, 'budget-exhausted'): self.operator().execute('tracker')
        state['maintenance_deadline'] = time.time() + 200; state['last_seen_at'] = time.time() + 10
        chat.atomic(self.state, state)
        with self.assertRaisesRegex(ValueError, 'clock-rollback'): self.operator().execute('tracker')

    def test_concurrent_start_is_not_replayed(self):
        with maintenance.lock(self.root / 'maintenance.lock'):
            with self.assertRaisesRegex(ValueError, 'already-running'): self.operator().execute('tracker')

    def test_tracker_reads_existing_confirmed_state_without_changing_database(self):
        folder = self.workspace / 'work-evidence/silverbullet-tracker'; folder.mkdir(parents=True)
        file = folder / 'state.sqlite3'; db = sqlite3.connect(file)
        db.executescript("CREATE TABLE runs(state TEXT,review INTEGER); INSERT INTO runs VALUES('stopped',0);"
                        "CREATE TABLE meta(key TEXT,value TEXT); INSERT INTO meta VALUES('version','4');"
                        "CREATE TABLE approvals(state TEXT); INSERT INTO approvals VALUES('committed');")
        db.commit(); db.close(); before = file.read_bytes()
        receipt = self.operator().execute('tracker')
        self.assertEqual(receipt['status'], 'executed'); self.assertEqual(file.read_bytes(), before)
        projection = chat.load(folder / 'maintenance-projection.json')
        self.assertFalse(projection['time_or_approval_mutated']); self.assertEqual(projection['committed_approvals'], 1)
        self.assertEqual(self.operator().execute('tracker'), receipt)

    def test_missing_tracker_does_not_initialize_database(self):
        receipt = self.operator().execute('tracker')
        self.assertEqual(receipt['status'], 'blocked')
        self.assertFalse((self.workspace / 'work-evidence').exists())
        self.assertEqual(self.operator().finish()['status'], 'partial')

    def test_symlinks_secret_paths_and_binary_sync_are_blocked(self):
        for path in ['../outside.md', '.env', 'secrets/key.md', 'db.sqlite3', '*.md']:
            with self.subTest(path=path), self.assertRaises(ValueError):
                maintenance.sync_path(self.workspace, path, exists=False)
        (self.workspace / 'notes.md').symlink_to(self.config)
        with self.assertRaises(ValueError): maintenance.sync_path(self.workspace, 'notes.md')

    def test_active_controller_never_updates_itself(self):
        with self.assertRaisesRegex(ValueError, 'executing-controller-update-deferred'):
            self.operator().product({'root': str(self.home)})

    def test_native_prompt_keeps_execution_in_same_chat(self):
        state = chat.load(self.state)
        prompt = dispatch.maintenance_prompt({'maintenance_policy': str(self.config)}, state, self.state)
        self.assertIn('bez codex exec', prompt)
        self.assertIn(str(state['maintenance_deadline']), prompt)
        self.assertIn('metadane nie zastępują zgody', prompt)

    def test_configuration_and_implementation_drift_stop_current_stage(self):
        file = self.workflow / '.systems/scripts/lib/dreaming-maintenance.py'
        file.write_text('# changed policy')
        with self.assertRaisesRegex(ValueError, 'implementation-drift'): self.operator()

    def git_fixture(self):
        repo = self.workspace
        bare = self.root / 'remote.git'
        def run(*args):
            return subprocess.check_output(['git', *args], stderr=subprocess.DEVNULL, text=True).strip()
        run('init', '--bare', str(bare)); run('-C', str(repo), 'init', '-b', 'main')
        run('-C', str(repo), 'config', 'user.email', 'synthetic@example.invalid')
        run('-C', str(repo), 'config', 'user.name', 'Synthetic QA')
        (repo / 'notes.md').write_text('Original documented result.\n')
        (repo / 'unrelated.md').write_text('Unrelated owner material.\n')
        run('-C', str(repo), 'add', 'notes.md', 'unrelated.md')
        run('-C', str(repo), 'commit', '-m', 'Synthetic initial')
        run('-C', str(repo), 'remote', 'add', 'origin', str(bare))
        run('-C', str(repo), 'push', '-u', 'origin', 'main')
        operator = self.operator()
        original_command = operator.command
        def command(argv, cwd, **kw):
            if argv[:3] == ['gh', 'repo', 'view']:
                self.assertEqual(argv[3],self.policy['workspaces']['owner']['remote_url'].removesuffix('.git'))
                return json.dumps({'isPrivate': True, 'nameWithOwner': 'example/private'})
            if argv[0] == 'git' and 'remote' in argv and 'get-url' in argv:
                return self.policy['workspaces']['owner']['remote_url']
            if argv[0] == 'git':
                argv=[str(bare) if value==self.policy['workspaces']['owner']['remote_url'] else value for value in argv]
            return original_command(argv, cwd, **kw)
        operator.command = command
        return run, operator, bare

    def test_real_git_exact_commit_preserves_unrelated_owner_changes(self):
        run, operator, bare = self.git_fixture()
        (self.workspace / 'notes.md').write_text('Updated documented result.\n')
        (self.workspace / 'unrelated.md').write_text('Uncommitted owner draft.\n')
        receipt = {}; operator.state['operations']['sync'] = receipt
        result = operator.repository(self.policy['workspaces']['owner'], receipt)
        self.assertTrue(result['push_verified'])
        head = run('-C', str(self.workspace), 'rev-parse', 'HEAD')
        self.assertEqual(head, run('--git-dir', str(bare), 'rev-parse', 'main'))
        self.assertEqual(run('-C', str(self.workspace), 'diff-tree', '--no-commit-id', '--name-only', '-r', head), 'notes.md')
        self.assertIn('unrelated.md', run('-C', str(self.workspace), 'diff', '--name-only'))
        self.assertEqual(run('-C', str(self.workspace), 'diff', '--cached', '--name-only'), '')

    def test_git_staged_work_and_sensitive_content_prevent_push(self):
        run, operator, bare = self.git_fixture()
        before = run('--git-dir', str(bare), 'rev-parse', 'main')
        (self.workspace / 'notes.md').write_text('Reviewed new text.\n')
        run('-C', str(self.workspace), 'add', 'notes.md')
        with self.assertRaisesRegex(ValueError, 'existing-staged-work'):
            operator.repository(self.policy['workspaces']['owner'], {})
        # Fixture unstage uses a direct index read, never a production reset.
        run('-C', str(self.workspace), 'read-tree', 'HEAD')
        (self.workspace / 'notes.md').write_text('api_key = syntheticcredential123456789\n')
        with self.assertRaisesRegex(ValueError, 'suspected-sync-secret'):
            operator.repository(self.policy['workspaces']['owner'], {})
        self.assertEqual(before, run('--git-dir', str(bare), 'rev-parse', 'main'))
        (self.workspace / 'notes.md').write_text('Safe reviewed text.\n')
        hook=self.workspace/'.git/hooks/pre-push';hook.write_text('#!/bin/sh\nexit 1\n');hook.chmod(0o700)
        with self.assertRaisesRegex(ValueError,'repository-hooks-require-review'):
            operator.repository(self.policy['workspaces']['owner'], {})
        self.assertEqual(before,run('--git-dir',str(bare),'rev-parse','main'))

    def test_uncertain_delivered_push_is_reconciled_without_second_commit(self):
        run, operator, bare = self.git_fixture()
        head = run('-C', str(self.workspace), 'rev-parse', 'HEAD')
        result = operator.repository(self.policy['workspaces']['owner'], {'commit': head})
        self.assertEqual(result['commit'], head)
        self.assertTrue(result['push_verified'])

    def test_push_may_already_advance_remote_tracking_ref(self):
        run, operator, bare = self.git_fixture()
        (self.workspace / 'notes.md').write_text('Safe changed note\n')
        original = operator.git
        def git(repo, *args, **kwargs):
            result = original(repo, *args, **kwargs)
            if args[0] == 'push':
                run('-C', str(repo), 'update-ref', 'refs/remotes/origin/main',
                    run('-C', str(repo), 'rev-parse', 'HEAD'))
            return result
        operator.git = git
        result = operator.repository(self.policy['workspaces']['owner'], {})
        self.assertTrue(result['push_verified'])
        self.assertEqual(result['commit'], run('--git-dir', str(bare), 'rev-parse', 'main'))

    def test_foreign_tracking_movement_after_push_is_not_overwritten(self):
        run, operator, bare = self.git_fixture()
        foreign = run('-C', str(self.workspace), 'commit-tree',
                      run('-C', str(self.workspace), 'rev-parse', 'HEAD^{tree}'),
                      '-p', 'HEAD', '-m', 'Synthetic independent update')
        (self.workspace / 'notes.md').write_text('Safe changed note\n')
        original = operator.git
        def git(repo, *args, **kwargs):
            result = original(repo, *args, **kwargs)
            if args[0] == 'push':
                run('-C', str(repo), 'update-ref', 'refs/remotes/origin/main', foreign)
            return result
        operator.git = git
        with self.assertRaisesRegex(ValueError, 'tracking-ref-moved-after-push'):
            operator.repository(self.policy['workspaces']['owner'], {})
        self.assertEqual(foreign, run('-C', str(self.workspace), 'rev-parse', 'refs/remotes/origin/main'))

    def test_public_origin_and_divergent_remote_are_blocked(self):
        run, operator, bare = self.git_fixture()
        original = operator.command
        def public(argv, cwd, **kw):
            if argv[:3] == ['gh', 'repo', 'view']:
                return json.dumps({'isPrivate': False, 'nameWithOwner': 'example/private'})
            return original(argv, cwd, **kw)
        operator.command = public
        with self.assertRaisesRegex(ValueError, 'verified-private-origin-required'):
            operator.repository(self.policy['workspaces']['owner'], {})
        operator.command = original
        def changed_push_url(argv,cwd,**kw):
            if argv[0]=='git' and 'get-url' in argv and '--push' in argv:
                return 'https://github.com/other/private.git'
            return original(argv,cwd,**kw)
        operator.command=changed_push_url
        with self.assertRaisesRegex(ValueError,'workspace-origin-drift'):
            operator.repository(self.policy['workspaces']['owner'], {})
        operator.command=original
        (self.workspace / 'notes.md').write_text('A local independent commit.\n')
        run('-C', str(self.workspace), 'add', 'notes.md')
        run('-C', str(self.workspace), 'commit', '-m', 'Unreviewed local commit')
        with self.assertRaises(ValueError): operator.repository(self.policy['workspaces']['owner'], {})

    def test_new_canonical_checkin_and_unicode_path_sync_without_unrelated_files(self):
        run, operator, bare = self.git_fixture()
        checkin = self.workspace / 'personal-ops/check-ins-v4/2026/2026-11-01.md'
        checkin.parent.mkdir(parents=True); checkin.write_text('Synthetic canonical check-in.\n')
        note = self.workspace / 'wskazówki.md'; note.write_text('Synthetic reviewed note.\n')
        (self.workspace / 'unreviewed-new.md').write_text('Not part of approved classes.\n')
        target = {**self.policy['workspaces']['owner'], 'sync_paths': ['notes.md', 'wskazówki.md'],
                  'sync_generated': ['canonical-v4-checkins']}
        receipt = {}; operator.state['operations']['sync'] = receipt
        result = operator.repository(target, receipt)
        self.assertTrue(result['push_verified'])
        names = run('-C', str(self.workspace), 'ls-tree', '-r', '--name-only', '-z', 'HEAD').split('\0')
        self.assertIn('wskazówki.md', names)
        self.assertIn(str(checkin.relative_to(self.workspace)), names)
        self.assertNotIn('unreviewed-new.md', names)

    def barrier(self):
        self.policy['products']['system'] = {'root':str(self.home), 'kind':'system', 'branch':'main',
                                           'remote_url':'https://github.com/example/system.git'}
        self.policy['operations'] = [{'id':'system-update','kind':'product-update','target':'system'}]
        chat.atomic(self.config,self.policy); self.state.unlink()
        maintenance.start(self.config,self.state,'chat-2026-11-01')
        receipt=self.operator().execute('system-update')
        self.assertEqual(receipt['status'],'deferred');self.operator().finish()

    def test_controller_update_barrier_skips_equal_source_and_keeps_original_deadline(self):
        self.barrier();old=chat.load(self.state)
        def git(_,repo,*args,**kw):
            if args==('remote','get-url','origin'):return self.policy['products']['system']['remote_url']
            return 'a'*40
        with patch.object(maintenance.Operator,'git',new=git):
            result=maintenance.controller_update_barrier(self.config,self.state,str(self.workspace))
        self.assertFalse(result['restart_required'])
        state=chat.load(self.state);self.assertEqual(state['deadline'],old['deadline'])
        self.assertEqual(state['operations']['system-update']['status'],'no-change')

    def test_controller_update_barrier_refuses_update_after_snapshot(self):
        self.barrier()
        paths=chat.paths({'workspace':str(self.workspace)},'chat-2026-11-01')
        chat.atomic(paths['state'],{'status':'prepared'})
        with self.assertRaisesRegex(ValueError,'analysis-already-prepared'):
            maintenance.controller_update_barrier(self.config,self.state,str(self.workspace))

    def test_controller_update_barrier_requests_process_replacement_only_after_official_success(self):
        self.barrier()
        def git(_,repo,*args,**kw):
            if args==('remote','get-url','origin'):return self.policy['products']['system']['remote_url']
            if args==('rev-parse','HEAD'):return 'a'*40
            if args==('rev-parse','FETCH_HEAD'):return 'b'*40
            if args[0]=='merge-base':return ('',0)
            return ''
        with patch.object(maintenance.Operator,'git',new=git),patch.object(maintenance.Operator,'product',return_value={'status':'executed','full_validation':'completed-by-official-updater'}) as update:
            result=maintenance.controller_update_barrier(self.config,self.state,str(self.workspace))
        self.assertTrue(result['restart_required']);self.assertTrue(update.call_args.kwargs['controller_barrier'])

    def test_controller_update_failure_blocks_dependent_analysis(self):
        self.barrier()
        def git(_,repo,*args,**kw):
            if args==('remote','get-url','origin'):return self.policy['products']['system']['remote_url']
            if args==('rev-parse','HEAD'):return 'a'*40
            if args==('rev-parse','FETCH_HEAD'):return 'b'*40
            if args[0]=='merge-base':return ('',0)
            return ''
        with patch.object(maintenance.Operator,'git',new=git),patch.object(maintenance.Operator,'product',side_effect=ValueError('official-full-failed')):
            with self.assertRaisesRegex(ValueError,'requires-reconciliation'):
                maintenance.controller_update_barrier(self.config,self.state,str(self.workspace))
        self.assertEqual(chat.load(self.state)['operations']['system-update']['status'],'blocked')

    def test_product_exit_zero_without_full_smoke_marker_is_not_success(self):
        script=self.workflow/'.systems/scripts/update-from-upstream';script.write_text('# synthetic official fixture')
        target={'root':str(self.workflow),'kind':'workflow','branch':'main',
                'remote_url':'https://github.com/example/workflow.git'}
        operator=self.operator()
        with patch.object(operator,'git',return_value=target['remote_url']),patch.object(operator,'command',return_value='exit zero but validation skipped'):
            with self.assertRaisesRegex(ValueError,'official-full-smoke-evidence-missing'):
                operator.product(target)

    def test_product_records_explicit_official_full_smoke_success(self):
        script=self.workflow/'.systems/scripts/update-from-upstream';script.write_text('# synthetic official fixture')
        target={'root':str(self.workflow),'kind':'workflow','branch':'main',
                'remote_url':'https://github.com/example/workflow.git'}
        operator=self.operator()
        output='AI_WORKFLOW_SMOKE_COMPLETE group=all result=pass exit_code=0\nAI_WORKFLOW_UPDATE_VALIDATION_COMPLETE result=pass'
        def git(repo,*args,**kw):return target['remote_url'] if args[0]=='remote' else 'c'*40
        with patch.object(operator,'git',side_effect=git),patch.object(operator,'command',return_value=output):
            result=operator.product(target)
        self.assertEqual(result['full_validation'],'completed-by-official-updater')
        self.assertEqual(len(result['validation_output_sha256']),64)

    def test_workbook_refresh_uses_committed_ledger_and_retains_manual_drafts(self):
        sys.path.insert(0,str(Path(__file__).parent/'tests'))
        import test_work_evidence_ledger as fixtures
        from work_evidence_xlsx import Tracker, load_book, sheet_values, MANUAL
        import io
        fixture=fixtures.LedgerTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
        ledger=fixture.ledger;before=ledger.snapshot();view=Tracker(ledger)
        target={'root':str(ledger.workspace)}
        result=self.operator().workbook(target)
        self.assertTrue(result['ledger_unchanged']);self.assertEqual(before,ledger.snapshot())
        book=load_book(view.path.read_bytes())
        draft=['']*len(MANUAL);draft[MANUAL.index('title_internal')]='Unapproved owner draft'
        book['Manual Inputs'].append(draft)
        stream=io.BytesIO();book.save(stream);view.path.write_bytes(stream.getvalue())
        self.assertEqual(self.operator().workbook(target)['status'],'no-change')
        self.assertEqual(sheet_values(load_book(view.path.read_bytes())['Manual Inputs'])[1][MANUAL.index('title_internal')],'Unapproved owner draft')
        self.assertEqual(before,ledger.snapshot())
        owner_file=view.path.with_name('~$'+view.path.name);owner_file.write_text('Workbook open in an editor')
        with self.assertRaisesRegex(ValueError,'workbook-open'): self.operator().workbook(target)
        self.assertEqual(before,ledger.snapshot())

    def test_json_credential_never_reaches_commit_or_remote(self):
        run,operator,bare=self.git_fixture()
        before=run('--git-dir',str(bare),'rev-parse','main')
        (self.workspace/'notes.md').write_text('{"api_key":"syntheticcredential123456789"}\n')
        with self.assertRaisesRegex(ValueError,'suspected-sync-secret'):
            operator.repository(self.policy['workspaces']['owner'],{})
        self.assertEqual(before,run('--git-dir',str(bare),'rev-parse','main'))

    def test_configured_git_filter_never_executes(self):
        run,operator,bare=self.git_fixture()
        marker=self.root/'filter-ran'
        script=self.root/'filter.py';script.write_text("import pathlib,sys\npathlib.Path("+repr(str(marker))+").touch()\nsys.stdout.write(sys.stdin.read())\n")
        run('-C',str(self.workspace),'config','filter.unreviewed.clean','python3 '+str(script))
        (self.workspace/'.gitattributes').write_text('notes.md filter=unreviewed\n')
        (self.workspace/'notes.md').write_text('Safe changed note\n')
        with self.assertRaisesRegex(ValueError,'repository-filters-require-review'):
            operator.repository(self.policy['workspaces']['owner'],{})
        self.assertFalse(marker.exists())

    def test_credential_guard_drift_revokes_current_operations(self):
        original=maintenance.sha
        def changed(path):
            return '0'*64 if Path(path).name=='dreaming_universal_sources.py' else original(path)
        with patch.object(maintenance,'sha',side_effect=changed):
            with self.assertRaisesRegex(ValueError,'maintenance-implementation-drift'):
                self.operator()

    def test_global_git_filter_is_still_blocked(self):
        run, operator, bare = self.git_fixture()
        marker = self.root / 'global-filter-ran'
        run('config', '--global', 'filter.unreviewed.clean', 'touch ' + str(marker))
        (self.workspace / '.gitattributes').write_text('notes.md filter=unreviewed\n')
        (self.workspace / 'notes.md').write_text('Safe changed note\n')
        with self.assertRaisesRegex(ValueError, 'repository-filters-require-review'):
            operator.repository(self.policy['workspaces']['owner'], {})
        self.assertFalse(marker.exists())


if __name__ == '__main__': unittest.main()
