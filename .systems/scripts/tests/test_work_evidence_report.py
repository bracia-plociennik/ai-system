"""Recipient, period, approval and privacy report regressions."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

import test_work_evidence_ledger as fixtures
from work_evidence import EvidenceError, digest, canonical_bytes
from work_evidence_report import report, write_report


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.LedgerTests()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.ledger = self.f.ledger
        self.policy = {"schema_version": 1, "report_id": "sample-week",
                       "recipient_id": "sample-client", "client_ids": ["sample-client"],
                       "project_ids": [], "start": "2026-10-01", "end_exclusive": "2026-10-08",
                       "coverage_attested": False, "texts": [], "recurring_care": []}

    def approve(self, entry=None, value="Approved mock outcome"):
        entry = entry or self.ledger.committed()[0][fixtures.ENTRY_ID]
        return {"entry_id": entry["entry_id"], "entry_hash": digest(entry),
                "recipient_id": "sample-client", "text": value, "text_hash": digest(value),
                "purpose": "client-report", "approved_by": "owner",
                "approved_at": "2026-10-02T11:00:00+02:00"}

    def test_empty_unknown_and_explicit_zero_differ(self):
        before = self.f.hashes()
        result = report(self.ledger, self.policy)
        self.assertTrue(result["manifest"]["coverage"]["no_recorded_work"])
        self.assertEqual(result["manifest"]["coverage"]["period_coverage"], "unknown")
        self.assertEqual(before, self.f.hashes())
        self.f.candidate["changes"][0]["entry"]["duration"]["seconds"] = 0
        self.f.commit()
        result = report(self.ledger, self.policy)
        coverage = result["manifest"]["coverage"]
        self.assertFalse(coverage["no_recorded_work"])
        self.assertEqual(coverage["confirmed_rows"], 1)
        self.assertEqual(coverage["known_actual_human_seconds"], 0)

    def test_no_internal_fallback_and_one_revision_count(self):
        self.f.candidate["changes"][0]["entry"]["outcome"] = "PRIVATE_CANARY"
        self.f.commit()
        first = report(self.ledger, self.policy)
        self.assertEqual(first["manifest"]["coverage"]["withheld_outcome_rows"], 1)
        self.assertNotIn("PRIVATE_CANARY", json.dumps(first["files"]))
        self.policy["texts"] = [self.approve()]
        result = report(self.ledger, self.policy)
        self.assertEqual(result["manifest"]["coverage"]["known_actual_human_seconds"], 60)
        self.assertNotIn("confirmation.json", json.dumps(result["files"]))
        original = self.ledger.committed()[0][fixtures.ENTRY_ID]
        corrected = copy.deepcopy(original)
        corrected.update(revision=2, previous_revision_hash=digest(original), reason="Correct minutes")
        corrected["duration"]["seconds"] = 120
        self.f.commit({"schema_version": 1, "changes": [{"entry": corrected}]})
        with self.assertRaises(EvidenceError):
            report(self.ledger, self.policy)
        self.policy["texts"] = [self.approve()]
        result = report(self.ledger, self.policy)
        self.assertEqual(result["manifest"]["coverage"]["known_actual_human_seconds"], 120)
        self.assertEqual(result["files"]["report.md"].count("Approved mock outcome"), 1)

    def test_recipient_and_agency_isolation(self):
        registry = copy.deepcopy(self.f.registry)
        registry["entities"] += [{"id": "sample-agency", "kind": "agency", "aliases": []},
                                {"id": "other-client", "kind": "client", "aliases": []}]
        registry["entities"][0]["parent_id"] = "sample-agency"
        path = self.f.ws / "work-evidence/entities.json"
        path.write_bytes(canonical_bytes(registry))
        self.ledger = fixtures.Ledger(self.f.ws)
        self.f.ledger = self.ledger
        self.f.commit()
        changed = copy.deepcopy(self.policy)
        changed["client_ids"] = ["other-client"]
        with self.assertRaises(EvidenceError):
            report(self.ledger, changed)
        self.policy.update(recipient_id="sample-agency")
        self.policy["texts"] = [self.approve()]
        with self.assertRaises(EvidenceError):
            report(self.ledger, self.policy)
        self.policy["texts"][0]["recipient_id"] = "sample-agency"
        self.assertIn("Approved mock outcome", report(self.ledger, self.policy)["files"]["report.html"])

    def test_contractual_care_separate_without_time(self):
        self.f.commit()
        ref = copy.deepcopy(self.f.entry["source_refs"][0])
        value = "Contract scope: routine monitoring"
        derivative = {"source_index": 0, "text": value, "source_sha256": ref["sha256"],
                      "text_sha256": digest(value), "purpose": "client-care", "approved_by": "owner",
                      "approved_at": "2026-10-02T11:00:00+02:00"}
        self.policy["recurring_care"] = [{"recipient_id": "sample-client", "source_ref": ref,
                                         "derivative": derivative}]
        result = report(self.ledger, self.policy)
        self.assertEqual(result["manifest"]["coverage"]["known_actual_human_seconds"], 60)
        self.assertIn("Agreed scope only", result["files"]["report.md"])

    def test_unknown_estimates_partial_aggregates(self):
        self.f.candidate["changes"][0]["entry"]["duration"].update(
            seconds=None, basis="unknown", evidence_ref=None)
        self.f.commit()
        result = report(self.ledger, self.policy)
        self.assertEqual(result["manifest"]["coverage"]["unknown_duration_rows"], 1)
        self.assertEqual(result["manifest"]["coverage"]["confirmed_rows"], 0)
        entry = self.ledger.committed()[0][fixtures.ENTRY_ID]
        changed = copy.deepcopy(entry)
        changed.update(revision=2, previous_revision_hash=digest(entry), reason="Aggregate estimate")
        changed["duration"].update(seconds=900, basis="estimated")
        changed["timing"] = {"kind": "aggregate", "start_date": "2026-09-30",
                             "end_date_exclusive": "2026-10-03"}
        self.f.commit({"schema_version": 1, "changes": [{"entry": changed}]})
        result = report(self.ledger, self.policy)
        self.assertEqual(result["manifest"]["coverage"]["partial_aggregate_rows"], 1)
        self.assertEqual(result["manifest"]["coverage"]["known_actual_human_seconds"], 0)

    def test_midnight_week_month_and_void(self):
        entry = self.f.candidate["changes"][0]["entry"]
        entry["duration"].update(seconds=3600, basis="measured")
        entry["timing"] = {"kind": "interval", "start": "2026-10-02T23:30:00+02:00",
                           "end": "2026-10-03T00:30:00+02:00", "timezone": "Europe/Warsaw"}
        self.f.commit()
        self.policy.update(start="2026-10-03", end_exclusive="2026-10-04")
        self.assertEqual(report(self.ledger, self.policy)["manifest"]["coverage"]["known_actual_human_seconds"], 1800)
        self.policy.update(start="2026-10-01", end_exclusive="2026-11-01")
        self.assertEqual(report(self.ledger, self.policy)["manifest"]["coverage"]["known_actual_human_seconds"], 3600)
        changed = copy.deepcopy(entry)
        changed.update(revision=2, previous_revision_hash=digest(entry), reason="Voided", voided=True)
        self.f.commit({"schema_version": 1, "changes": [{"entry": changed}]})
        self.assertEqual(report(self.ledger, self.policy)["manifest"]["coverage"]["recorded_rows"], 0)

    def test_escaped_html_and_projection_approvals(self):
        self.f.commit()
        self.policy["texts"] = [self.approve(value='<script>bad</script> [link](https://example.invalid)')]
        result = report(self.ledger, self.policy)
        self.assertNotIn("<script>", result["files"]["report.html"])
        self.assertNotIn("[link](", result["files"]["report.md"])
        self.assertNotIn("href=", result["files"]["report.html"])
        for field, value in (("purpose", "publication"), ("approved_by", "agent"),
                             ("text_hash", "0"*64), ("recipient_id", "other-client")):
            changed = copy.deepcopy(self.policy)
            changed["texts"][0][field] = value
            with self.subTest(field=field), self.assertRaises(EvidenceError):
                report(self.ledger, changed)

    def test_persist_retry_stale_index_and_sources(self):
        self.f.commit()
        self.policy["texts"] = [self.approve()]
        result = report(self.ledger, self.policy)
        write_report(self.ledger, self.policy, result["draft_hash"], owner_approved=True)
        before = self.f.hashes()
        write_report(self.ledger, self.policy, result["draft_hash"], owner_approved=True)
        self.assertEqual(before, self.f.hashes())
        self.policy["coverage_attested"] = True
        with self.assertRaises(EvidenceError):
            write_report(self.ledger, self.policy, result["draft_hash"], owner_approved=True)
        index = self.f.ws / "work-evidence/derived/work-index.jsonl"
        index.write_text("Edited", encoding="utf-8")
        self.assertEqual(report(self.ledger, self.policy)["manifest"]["index_state"], "stale")
        self.f.source.write_text("Source changed", encoding="utf-8")
        with self.assertRaises(EvidenceError):
            report(self.ledger, self.policy)

    def test_cli_write_guard(self):
        scripts = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable, "-B", str(scripts / "work-evidence-report"),
                                 "write", "--workspace", "/missing", "--policy", "missing.json"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)["category"], "owner-approval-required")
