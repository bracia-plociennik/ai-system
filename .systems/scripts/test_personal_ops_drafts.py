"""Synthetic lifecycle/failure tests. No real personal sources or calendar calls."""
import json
import os
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys
from unittest.mock import patch
from datetime import date, datetime, timedelta

import personal_ops_drafts as d


class DraftTests(unittest.TestCase):
    day = date(2026, 10, 20)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = Path(self.tmp.name) / "owner-workspace"
        self.ws.mkdir()
        self.clock = lambda: datetime(2026, 10, 20, 6, tzinfo=d.ZONE)
        self.ready = patch("personal_ops_spor_proposals.prepare", return_value={"status": "ready"})
        self.ready.start()
        self.addCleanup(self.ready.stop)
        self.addCleanup(self.tmp.cleanup)

    def payload(self, day=None):
        info = d.identity(self.ws, day or self.day)
        return {"contract": d.CONTRACT, "proposal_id": info["proposal_id"],
                "sources": ["status.md"], "fields": {key: "Nieznane — pytanie: UNKNOWN — uzupełnij" for key in d.form(info["mode"])}}

    def create(self):
        return d.create(self.ws, self.day, self.payload(), clock=self.clock)

    def test_full_daily_private_and_noncanonical_no_other_sources(self):
        before = list(self.ws.iterdir())
        result = self.create()
        self.assertEqual(before, [])
        self.assertEqual(result["metadata"]["status"], "draft")
        self.assertEqual(len(d.FIELD.findall(result["body"])), len(d.form("daily")))
        self.assertIn("ostatnim dniem mojego życia", result["body"])
        self.assertEqual((self.ws / result["path"]).stat().st_mode & 0o777, 0o600)
        self.assertEqual({p.name for p in (self.ws / "personal-ops").iterdir()}, {"check-in-drafts"})
        from personal_ops_v4 import load_v4_daily_records, load_v4_weekly_records
        self.assertEqual(load_v4_daily_records(self.ws), [])
        self.assertEqual(load_v4_weekly_records(self.ws), [])

    def test_weekly_periods_and_complete_form_are_not_canonical_window(self):
        day = date(2026, 10, 24)
        result = d.create(self.ws, day, self.payload(day), clock=lambda: datetime(2026, 10, 24, 6, tzinfo=d.ZONE))
        self.assertEqual(result["metadata"]["periods"]["review_end"], "2026-10-23")
        self.assertEqual(result["metadata"]["periods"]["plan_start"], "2026-10-26")
        self.assertEqual(len(d.FIELD.findall(result["body"])), len(d.form("weekly")))
        self.assertIn("ostatnim tygodniem mojego życia", result["body"])

    def test_rerun_never_overwrites_even_manual_edits(self):
        result = self.create()
        path = self.ws / result["path"]
        path.write_text(path.read_text() + "\nOwner note\n")
        before = path.read_bytes()
        with self.assertRaises(FileExistsError):
            self.create()
        self.assertEqual(path.read_bytes(), before)

    def test_missing_extra_fields_labels_structure_and_guessed_alignment_rejected(self):
        for transform in [lambda p: p["fields"].pop("f001"),
                          lambda p: p["fields"].update(other="value"),
                          lambda p: p["fields"].update(f001="unlabeled"),
                          lambda p: p["fields"].update(f001="Potwierdzone: x\n## replacement"),
                          lambda p: p["fields"].update({next(k for k,v in d.form("daily").items() if v["label"].startswith("Odpowiedź:")): "Potwierdzone: TAK"})]:
            payload = self.payload()
            transform(payload)
            with self.assertRaises(ValueError):
                d.create(self.ws, self.day, payload, clock=self.clock)
            self.assertFalse((self.ws / "personal-ops").exists())

    def test_no_catchup_sunday_or_date_rollover_at_commit(self):
        with self.assertRaises(ValueError):
            d.create(self.ws, date(2026, 10, 19), self.payload(date(2026, 10, 19)), clock=self.clock)
        with self.assertRaises(ValueError):
            d.identity(self.ws, date(2026, 10, 25))
        moments = iter([self.clock(), datetime(2026, 10, 21, tzinfo=d.ZONE)])
        with self.assertRaises(ValueError):
            d.create(self.ws, self.day, self.payload(), clock=lambda: next(moments))
        self.assertEqual(list(self.ws.rglob("*.md")), [])

    def test_source_error_and_existing_canonical_block_creation(self):
        with patch("personal_ops_spor_proposals.prepare", return_value={"status": "source-error"}):
            with self.assertRaises(ValueError):
                self.create()
        path = self.ws / "personal-ops/check-ins-v4/2026/2026-10-20.md"
        path.parent.mkdir(parents=True)
        path.write_text('---\ntype: daily-check-in-v4\nproperties:\n  session_date: "2026-10-20"\n---\n')
        before = path.read_bytes()
        with self.assertRaises(ValueError):
            self.create()
        self.assertEqual(path.read_bytes(), before)

    def test_field_patch_preserves_owner_notes_and_rejects_stale_hash(self):
        result = self.create()
        path = self.ws / result["path"]
        path.write_text(path.read_text() + "\nRęczna notatka właściciela\n")
        with self.assertRaises(ValueError):
            d.update(self.ws, self.day, {"f001": "Potwierdzone: owner reply"}, result["sha256"], "chat:reply", clock=self.clock)
        fresh = d.read(self.ws, self.day)
        updated = d.update(self.ws, self.day, {"f001": "Potwierdzone: owner reply"}, fresh["sha256"], "chat:reply", clock=self.clock)
        self.assertIn("Ręczna notatka właściciela", updated["body"])
        self.assertIn("Potwierdzone: owner reply", updated["body"])
        self.assertEqual(updated["metadata"]["revision"], 2)
        self.assertEqual(updated["metadata"]["status"], "draft")

    def test_linked_directory_and_file_never_escape(self):
        outside = Path(self.tmp.name) / "outside"
        outside.mkdir()
        (self.ws / "personal-ops").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(OSError):
            self.create()
        self.assertEqual(list(outside.iterdir()), [])
        (self.ws / "personal-ops").unlink()
        result = self.create()
        path = self.ws / result["path"]
        data = path.read_bytes()
        path.unlink()
        destination = outside / "secret.md"
        destination.write_bytes(data)
        path.symlink_to(destination)
        with self.assertRaises(OSError):
            d.read(self.ws, self.day)
        self.assertEqual(destination.read_bytes(), data)

    def test_crash_before_publication_leaves_no_partial_file(self):
        with patch.object(d.os, "link", side_effect=OSError("simulated filesystem failure")):
            with self.assertRaises(OSError):
                self.create()
        self.assertEqual(list(self.ws.rglob("*.md")), [])
        self.assertEqual(list(self.ws.rglob(".draft-*")), [])

    def test_crash_after_link_publication_leaves_readable_draft_without_cleanup(self):
        with patch.object(d.os, 'unlink', side_effect=OSError('crash before temp unlink')):
            with self.assertRaises(OSError):
                self.create()
        result = d.read(self.ws, self.day)
        self.assertEqual(result['metadata']['status'], 'draft')
        before = (self.ws / result['path']).read_bytes()
        self.assertEqual(len(list(self.ws.rglob('.draft-*'))), 1)
        self.assertEqual((self.ws / result['path']).read_bytes(), before)
        with self.assertRaises(FileExistsError):
            self.create()

    def test_foreign_hard_link_is_rejected(self):
        result = self.create()
        os.link(self.ws / result['path'], Path(self.tmp.name) / 'foreign-link')
        with self.assertRaises(ValueError):
            d.read(self.ws, self.day)

    def test_only_one_cooperating_writer(self):
        info = d.identity(self.ws, self.day)
        with d.directory(self.ws, info, create=True) as (fd, _), d.locked(fd):
            with self.assertRaises(BlockingIOError):
                self.create()

    def test_approval_receipt_does_not_create_canonical_and_requires_actual_saved_source(self):
        result = self.create()
        with self.assertRaises(ValueError):
            d.mark_approved(self.ws, self.day, result["sha256"], "personal-ops/check-ins-v4/2026/2026-10-20.md", "0" * 64, "chat:approval")
        self.assertFalse((self.ws / "personal-ops/check-ins-v4").exists())
        self.assertEqual(d.read(self.ws, self.day)["metadata"]["status"], "draft")

    def test_real_task_generator_rejects_draft_for_daily_and_weekly_without_any_write(self):
        result = self.create()
        path = self.ws / result["path"]
        before = {str(p): p.read_bytes() for p in self.ws.rglob('*') if p.is_file()}
        for flag in ('--check-in', '--weekly-plan'):
            run = subprocess.run([sys.executable, '-B', str(d.ROOT / '.systems/scripts/propose-task-candidates'),
                                  '--workspace', str(self.ws), flag, str(path), '--write', '--owner-approved'],
                                 capture_output=True, text=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn('not canonical TaskNote sources', run.stderr)
            self.assertEqual({str(p): p.read_bytes() for p in self.ws.rglob('*') if p.is_file()}, before)

    def test_daily_and_weekly_approved_receipts_validate_native_canonical_and_keep_source_bytes(self):
        from personal_ops_v4 import required_schema, DAILY_ALIGNMENT_QUESTION, WEEKLY_ALIGNMENT_QUESTION
        for day in (self.day, date(2026, 10, 24)):
            info = d.identity(self.ws, day)
            result = d.create(self.ws, day, self.payload(day), clock=lambda: datetime.combine(day, datetime.min.time(), tzinfo=d.ZONE))
            kind = info['mode']
            props = {key: '' for key in required_schema(kind)}
            props.update(index_contract='4', schema_version='4', artifact_kind=kind, private_index_policy='detailed-private', life_alignment_contract='last-period-alignment-v1')
            for key in ('review_state_json', 'review_process_json', 'review_outcome_json', 'review_review_json'):
                props[key] = '{}'
            if kind == 'daily':
                relative = f'personal-ops/check-ins-v4/{day.year}/{day}.md'
                props.update(session_date=str(day), closure_date=str(day-timedelta(days=1)), review_window_kind='previous-day', planned_items_json='[]', owner_overrides_json='[]', osnr_checkpoints_json='[]', task_generation_references_json='[]', planned_day_life_alignment_answer='yes')
                question = DAILY_ALIGNMENT_QUESTION
            else:
                relative = 'personal-ops/weekly-check-ins-v4/2026/2026-W43.md'
                # Owner finishes the Saturday draft on Sunday: identity is the
                # review/plan period, not the later capture timestamp.
                props.update(report_id='2026-W43', recording_date='2026-10-25', review_week_start='2026-10-19', review_week_end='2026-10-25', plan_week_start='2026-10-26', plan_week_end='2026-10-30', future_wig_json='{}', future_plan_items_json='[]', daily_blocks_json='[]', planned_week_life_alignment_answer='yes')
                question = WEEKLY_ALIGNMENT_QUESTION
            canonical = self.ws / relative
            canonical.parent.mkdir(parents=True, exist_ok=True)
            canonical.write_text(f'---\ntype: {kind}-check-in-v4\nschema_version: 4\nindex_contract: 4\nproperties:\n' + '\n'.join(f'  {key}: {json.dumps(value)}' for key,value in props.items()) + '\n---\n' + question + '\n')
            before = canonical.read_bytes()
            if kind == 'daily':
                def concurrent_change(*args):
                    canonical.write_bytes(before + b'\nconcurrent change\n')
                with patch('personal_ops_v4.load_daily', side_effect=concurrent_change):
                    with self.assertRaises(ValueError):
                        d.mark_approved(self.ws, day, result['sha256'], relative, d.digest(before), 'chat:approval')
                self.assertEqual(d.read(self.ws, day)['metadata']['status'], 'draft')
                canonical.write_bytes(before)
            updated = d.mark_approved(self.ws, day, result['sha256'], relative, d.digest(before), 'chat:current-owner-approval')
            self.assertEqual(updated['metadata']['status'], 'approved')
            self.assertEqual(updated['metadata']['canonical_source'], relative)
            self.assertEqual(canonical.read_bytes(), before)
            self.assertEqual(updated['body'], result['body'])
            with self.assertRaises(ValueError):
                d.update(self.ws, day, {'f001': 'Potwierdzone: later'}, updated['sha256'], 'chat:reply')

    def test_weekly_year_boundary_guard_matches_period_even_with_later_capture(self):
        day = date(2027, 1, 2)
        path = self.ws / 'personal-ops/weekly-check-ins-v4/2026/2026-W53.md'
        path.parent.mkdir(parents=True)
        path.write_text('---\ntype: weekly-check-in-v4\nproperties:\n  recording_date: "2027-01-03"\n  review_week_start: "2026-12-28"\n  plan_week_start: "2027-01-04"\n  plan_week_end: "2027-01-08"\n---\n')
        self.assertEqual(d.canonical_sources(self.ws, day), ['personal-ops/weekly-check-ins-v4/2026/2026-W53.md'])


if __name__ == "__main__":
    unittest.main()
