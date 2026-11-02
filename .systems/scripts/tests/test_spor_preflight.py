import copy
import json
import sys
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import test_finalization_artifacts as fixtures
from finalization_artifacts import finalize_spor, spor_candidate, publish
from finalization_support import sha
from spor_preflight import check_calendar_identities
from spor_integration_preflight import calendar_readiness, existing_tasks_readiness


class PreflightTests(unittest.TestCase):
    setUp = fixtures.SporTests.setUp
    request = fixtures.SporTests.request
    hooks = fixtures.SporTests.hooks
    preflights = fixtures.SporTests.preflights

    def apply(self, request, preflights=None, integrations=('calendar',)):
        calls = []
        result = finalize_spor(self.ws, request, apply=True, approved=True,
                               integrations=integrations, preflights=preflights,
                               hooks=self.hooks(calls))
        return result, calls

    def assert_no_canonical(self):
        self.assertFalse((self.ws / 'personal-ops/check-ins-v4').exists())

    def test_missing_preflight_blocks_before_first_write(self):
        r = self.request()
        with self.assertRaisesRegex(ValueError, 'Missing read-only'):
            self.apply(r)
        self.assert_no_canonical()

    def test_bad_monday_period_blocks_before_access(self):
        r = self.request()
        r['properties']['review_window_kind'] = 'previous-three-days'
        probes = []
        with self.assertRaisesRegex(ValueError, 'Monday'):
            self.apply(r, {'calendar': lambda *args: probes.append(args)})
        self.assertEqual(probes, [])
        self.assert_no_canonical()

    def test_access_failure_blocks_without_partial_artifact(self):
        r = self.request()
        def unavailable(*args):
            raise PermissionError('synthetic unavailable transport')
        with self.assertRaises(PermissionError):
            self.apply(r, {'calendar': unavailable})
        self.assert_no_canonical()

    def test_unready_wrong_source_and_empty_evidence_block(self):
        r = self.request()
        for override in ({'status': 'blocked'}, {'candidate_sha256': '0'*64}, {'inputs': {}}):
            def bad(candidate, h):
                return {**self.preflights()['calendar'](candidate, h), **override}
            with self.subTest(override=override), self.assertRaises(ValueError):
                self.apply(r, {'calendar': bad})
            self.assert_no_canonical()

    def test_stale_local_proof_blocks(self):
        r = self.request()
        def stale(candidate, h):
            return {'status': 'ready', 'candidate_sha256': h,
                    'inputs': {candidate['draft']['path']: '0'*64}}
        with self.assertRaisesRegex(ValueError, 'Stale'):
            self.apply(r, {'calendar': stale})
        self.assert_no_canonical()

    def test_mutated_request_in_preflight_blocks(self):
        r = self.request()
        def changed(candidate, h):
            r['fields']['f001'] = 'Potwierdzone: changed after review'
            return self.preflights()['calendar'](candidate, h)
        with self.assertRaisesRegex(ValueError, 'package changed'):
            self.apply(r, {'calendar': changed})
        self.assert_no_canonical()

    def test_cross_probe_input_drift_and_new_absence_file_block(self):
        r = self.request()
        for initially_present in (True, False):
            dependency = self.ws / 'input.md'
            if initially_present:
                dependency.write_text('before')
            elif dependency.exists():
                dependency.unlink()
            def first(candidate, h):
                result = self.preflights()['tasks'](candidate, h)
                result['inputs']['input.md'] = sha(dependency) if initially_present else None
                return result
            def second(candidate, h):
                dependency.write_text('after')
                return self.preflights()['calendar'](candidate, h)
            with self.subTest(initially_present=initially_present), self.assertRaisesRegex(ValueError, 'inputs changed'):
                self.apply(r, {'tasks': first, 'calendar': second}, ('tasks', 'calendar'))
            self.assert_no_canonical()

    def test_all_readiness_precedes_single_write_and_single_effect(self):
        r = self.request()
        probes = []
        def ready(name):
            def check(candidate, h):
                self.assert_no_canonical()
                probes.append(name)
                return self.preflights()[name](candidate, h)
            return check
        with patch('finalization_artifacts.publish', wraps=publish) as writer:
            result, calls = self.apply(r, {x: ready(x) for x in ('tasks', 'calendar')}, ('tasks', 'calendar'))
        self.assertEqual(probes, ['tasks', 'calendar'])
        self.assertEqual(writer.call_count, 1)
        self.assertEqual(calls, ['indexes', 'renderer', 'tasks', 'calendar'])
        self.assertEqual(result['status'], 'finalized')

    def test_preview_never_writes_or_calls_mutations(self):
        r = self.request()
        before = {p: p.read_bytes() for p in self.ws.rglob('*') if p.is_file()}
        calls = []
        result = finalize_spor(self.ws, r, integrations=('calendar',),
                               hooks=self.hooks(calls), preflights=self.preflights())
        self.assertEqual(result['status'], 'preview')
        self.assertEqual(calls, [])
        self.assertEqual(before, {p: p.read_bytes() for p in self.ws.rglob('*') if p.is_file()})

    def test_linked_deadline_and_latest_dod_normalize_once_without_input_edit(self):
        r = self.request()
        p = r['properties']
        p.update(wig_plan_item_id='report', wig_deadline='2026-10-26T10:10',
                 planned_items_json=json.dumps([{'id': 'report', 'definition_of_done': 'old'}]))
        r['confirmed_properties'] = ['wig_plan_item_id', 'wig_deadline', 'planned_items_json']
        r['plan_item_updates'] = {'report': {'definition_of_done': 'Published; tests unknown'}}
        original = copy.deepcopy(r)
        candidate = spor_candidate(self.ws, r)
        item = json.loads(candidate['properties']['planned_items_json'])[0]
        self.assertEqual(item['deadline'], '2026-10-26T10:10')
        self.assertEqual(item['definition_of_done'], 'Published; tests unknown')
        self.assertEqual(original, r)
        self.assertIn('UNKNOWN', candidate['body'])

    def test_conflicting_deadline_or_unconfirmed_item_update_blocks(self):
        r = self.request()
        r['properties'].update(wig_plan_item_id='report', wig_deadline='2026-10-26T10:10',
                               planned_items_json='[{"id":"report","deadline":"2026-10-26T11:20"}]')
        r['confirmed_properties'] = ['wig_plan_item_id', 'wig_deadline', 'planned_items_json']
        with self.assertRaisesRegex(ValueError, 'Conflicting WIG'):
            spor_candidate(self.ws, r)
        r['properties']['wig_deadline'] = ''
        r['plan_item_updates'] = {'missing': {'definition_of_done': 'invented'}}
        with self.assertRaisesRegex(ValueError, 'invalid plan item'):
            spor_candidate(self.ws, r)
        self.assert_no_canonical()

    def test_renamed_calendar_slot_blocks_before_save(self):
        r = self.request()
        def renamed(candidate, h):
            check_calendar_identities([{'block_id': 'external-absence'}], ['private-unavailable'])
        with self.assertRaisesRegex(ValueError, 'removed or renamed'):
            self.apply(r, {'calendar': renamed})
        self.assert_no_canonical()
        check_calendar_identities([{'block_id': 'private-unavailable'}], ['private-unavailable'])

    def test_invalid_wig_deadline_blocks_before_write(self):
        r = self.request()
        r['properties'].update(wig_plan_item_id='report', wig_deadline='not-a-date',
                               planned_items_json='[{"id":"report"}]')
        r['confirmed_properties'] = ['wig_plan_item_id', 'wig_deadline', 'planned_items_json']
        with self.assertRaisesRegex(ValueError, 'Invalid WIG deadline'):
            self.apply(r, self.preflights())
        self.assert_no_canonical()


class ConsumerTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.ws = Path(self.tmp.name)

    def calendar_fixture(self):
        root = self.ws / 'personal-ops/calendar'
        root.mkdir(parents=True)
        (self.ws/'calendar.md').write_text('```json\n' + json.dumps({
            'enabled': True, 'calendar_id': 'synthetic', 'add_google_meet': False,
            'automatic_deletion': False}) + '\n```')
        (root/'state.json').write_text(json.dumps({'schema_version': 1,
            'calendar_id': 'synthetic', 'events': {}}))
        calls = []
        class API:
            def validate_calendar(self): calls.append('calendar-access')
            def search(self, days): calls.append('search'); return []
            def read(self, identity): calls.append('read'); return {}
            def create(self, *args): raise AssertionError('remote write')
        def reconcile(plan, api, state, persist, **kwargs):
            self.assertFalse(kwargs['apply']); self.assertFalse(kwargs['adopt'])
            self.assertFalse(hasattr(api, 'create'))
            api.validate_calendar(); api.search(plan['days']); api.read('existing')
            return {'mode': 'dry-run', 'conflicts': []}
        adapter = SimpleNamespace(CONFIG='calendar.md', CALENDAR_ID='synthetic', STATE_NAME='state.json',
            Source=lambda *args: args, legacy_receipts=lambda ws: {}, reconcile=reconcile,
            resolve_plan=lambda *args: {'days': ['2026-10-26'], 'dependencies': {}})
        candidate = {'path': 'canonical.md', 'properties': {'artifact_kind': 'daily', 'session_date': '2026-10-26'}}
        return adapter, API(), calls, candidate

    def test_calendar_full_readiness_is_pure(self):
        adapter, api, calls, candidate = self.calendar_fixture()
        before = {p: p.read_bytes() for p in self.ws.rglob('*') if p.is_file()}
        result = calendar_readiness(self.ws, candidate, 'a'*64, adapter, api, date(2026, 10, 26))
        self.assertEqual(result['status'], 'ready')
        self.assertEqual(calls, ['calendar-access', 'search', 'read'])
        self.assertEqual(before, {p: p.read_bytes() for p in self.ws.rglob('*') if p.is_file()})

    def test_calendar_transport_or_conflicts_stop_preflight(self):
        adapter, api, _, candidate = self.calendar_fixture()
        api.validate_calendar = lambda: (_ for _ in ()).throw(PermissionError('synthetic'))
        with self.assertRaises(PermissionError):
            calendar_readiness(self.ws, candidate, 'a'*64, adapter, api, date(2026, 10, 26))
        adapter.reconcile = lambda *args, **kw: {'mode': 'dry-run', 'conflicts': [{'reason': 'duplicate'}]}
        with self.assertRaisesRegex(ValueError, 'conflict'):
            calendar_readiness(self.ws, candidate, 'a'*64, adapter, api, date(2026, 10, 26))

    def test_calendar_proof_binds_bytes_actually_read(self):
        adapter, api, _, candidate = self.calendar_fixture()
        path = self.ws/'personal-ops/calendar/state.json'
        original = sha(path)
        old_reconcile = adapter.reconcile
        def concurrent(*args, **kwargs):
            path.write_text(path.read_text() + '\n')
            return old_reconcile(*args, **kwargs)
        adapter.reconcile = concurrent
        result = calendar_readiness(self.ws, candidate, 'a'*64, adapter, api, date(2026, 10, 26))
        self.assertEqual(result['inputs']['personal-ops/calendar/state.json'], original)
        self.assertNotEqual(sha(path), original)

    def test_existing_tasks_readiness_preserves_unknown_notes_and_lifecycle(self):
        tasks = self.ws/'tasks'; tasks.mkdir()
        vault = tasks/'vault'; (vault/'tasks').mkdir(parents=True)
        (tasks/'task-store.local.md').write_text('---\nschema_version: 1\nenabled: true\nprofile: silverbullet-v1\nvault_path: '+str(vault)+'\n---\n')
        target = vault/'tasks/one.md'
        target.write_text('---\ntype: task\nstatus: open\nauthor: human\n---\n## Checkpoint OSNR\nUNKNOWN\nManual note\n')
        candidate = {'properties': {'task_generation_references_json': json.dumps([str(target.relative_to(self.ws))])}}
        before = target.read_bytes()
        self.assertEqual(existing_tasks_readiness(self.ws, candidate, 'a'*64)['status'], 'ready')
        self.assertEqual(target.read_bytes(), before)
        target.write_text(target.read_text().replace('status: open', 'status: done'))
        with self.assertRaisesRegex(ValueError, 'Closed task'):
            existing_tasks_readiness(self.ws, candidate, 'a'*64)


if __name__ == '__main__':
    unittest.main()
