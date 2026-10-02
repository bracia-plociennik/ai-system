"""Cross-consumer synthetic trace with networking disabled."""
import copy
import io
import json
import socket
import unittest
from unittest.mock import patch
import test_work_evidence_tax as tax
import test_work_evidence_editorial as editorial
import test_work_evidence_xlsx as xlsx
from work_evidence import EvidenceError, canonical_bytes, digest
from work_evidence_ledger import Ledger, coverage
from work_evidence_report import report
from work_evidence_tax_evidence import TaxRegister
from work_evidence_xlsx import Tracker, load_book, literal, sheet_values


class IntegrationTests(unittest.TestCase):
    def test_ci_uses_pinned_isolated_dependencies_without_weakening_full_validation(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[3]
        workflow = (root / ".github/workflows/ai-system-validate.yml").read_text()
        self.assertIn('python3 -m venv "$RUNNER_TEMP/work-evidence-venv"', workflow)
        self.assertIn("--require-hashes --only-binary=:all:", workflow)
        self.assertIn("WORK_EVIDENCE_PYTHON=$RUNNER_TEMP/work-evidence-venv/bin/python", workflow)
        self.assertIn(".systems/scripts/validate-ai-system --profile full", workflow)
        self.assertNotIn("AI_SYSTEM_SKIP_SMOKE_TESTS", workflow)

    def test_single_owner_all_consumers_manual_roundtrip_and_staleness(self):
        calc = tax.CalculatorTests()
        calc.setUp()
        self.addCleanup(calc.doCleanups)
        f = calc.f.f
        ledger = f.ledger
        ed = editorial.EditorialTests()
        ed.setUp()
        self.addCleanup(ed.doCleanups)
        request = copy.deepcopy(ed.request)
        entry = next(iter(ledger.committed()[0].values()))
        request["claims"][0].update(entry_id=entry["entry_id"], entry_hash=digest(entry),
                                    source_ref=entry["source_refs"][0])
        ed.approve_claim(request["claims"][0])
        policy = {"schema_version": 1, "report_id": "cross-flow", "recipient_id": "sample-client",
                  "client_ids": ["sample-client"], "project_ids": [], "start": "2026-10-01",
                  "end_exclusive": "2026-11-01", "coverage_attested": False,
                  "texts": [{"entry_id": entry["entry_id"], "entry_hash": digest(entry),
                             "recipient_id": "sample-client", "text": "Mock result tested",
                             "text_hash": digest("Mock result tested"), "purpose": "client-report",
                             "approved_by": "owner", "approved_at": "2026-10-02T11:00:00+02:00"}],
                  "recurring_care": []}
        with patch.object(socket.socket, "connect", side_effect=AssertionError("Network forbidden")), \
             patch.object(socket, "create_connection", side_effect=AssertionError("Network forbidden")):
            before = f.hashes()
            packet = calc.f.register.packet(calc.f.bundle)
            arithmetic = calc.preview()
            content = editorial.bundle(ledger, request)
            monthly = report(ledger, policy)
            weekly = report(ledger, {**policy, "start": "2026-09-28", "end_exclusive": "2026-10-05"})
            self.assertEqual(f.hashes(), before)
            self.assertEqual(monthly["manifest"]["coverage"]["known_actual_human_seconds"], 60)
            self.assertEqual(weekly["manifest"]["coverage"]["known_actual_human_seconds"], 60)
            self.assertEqual(packet["unique_work_references"], 1)
            self.assertEqual(packet["eligibility"], "unknown")
            self.assertEqual(arithmetic["outputs"]["result"]["value"], "20.00")
            self.assertTrue(arithmetic["synthetic_nonlegal"])
            self.assertNotIn("TAX_PRIVATE_CANARY", json.dumps(content))
            self.assertNotIn("TAX_PRIVATE_CANARY", json.dumps(monthly["files"]))
            self.assertEqual(coverage(list(ledger.committed()[0].values()))["actual_human_seconds"], 60)
            tracker = Tracker(ledger)
            tracker.export()
            b = load_book(tracker.path.read_bytes())
            self.assertEqual(dict(sheet_values(b["Summary"])[1:])["Actual human minutes"], 1)
            row = dict.fromkeys(xlsx.MANUAL)
            row.update(action="new", performed_on="2026-10-02", duration_seconds=0,
                       basis="owner-confirmed", client_id="sample-client", project_id="sample-project",
                       title_internal="Confirmed zero-time note", outcome="Recorded", status="done",
                       activity_kind="development")
            literal(b["Manual Inputs"], [row[k] for k in xlsx.MANUAL])
            stream = io.BytesIO()
            b.save(stream)
            tracker.path.write_bytes(stream.getvalue())
            prepared = tracker.prepare()
            tracker.apply(prepared["transaction_id"], prepared["manifest_hash"])
            tracker.apply(prepared["transaction_id"], prepared["manifest_hash"])
            self.assertEqual(len(ledger.committed()[0]), 2)
            self.assertEqual(coverage(list(ledger.committed()[0].values()))["actual_human_seconds"], 60)
            # Unrelated zero-time entry never duplicates the original work.
            self.assertEqual(calc.f.register.packet(calc.f.bundle)["unique_work_references"], 1)
            self.assertEqual(tracker.preview()["status"], "no-new-rows")
            old = copy.deepcopy(ledger.committed()[0][entry["entry_id"]])
            correction = copy.deepcopy(old)
            correction.update(revision=2, previous_revision_hash=digest(old), reason="Correct actual time")
            correction["duration"]["seconds"] = 120
            prepared = ledger.prepare({"schema_version": 1, "changes": [{"entry": correction}]})
            ledger.apply(prepared["transaction_id"], prepared["manifest_hash"])
            for action in (lambda: report(ledger, policy), lambda: editorial.bundle(ledger, request),
                           lambda: calc.preview()):
                with self.assertRaises(EvidenceError):
                    action()
            self.assertEqual(ledger.rebuild()["coverage"]["actual_human_seconds"], 120)

    def test_shared_ip_references_two_owners_without_copying_time(self):
        calc = tax.CalculatorTests()
        calc.setUp()
        self.addCleanup(calc.doCleanups)
        f = calc.f.f
        other = f.root / "second-workspace"
        (other / "work-evidence").mkdir(parents=True)
        config = copy.deepcopy(f.config)
        config.update(workspace_id=other.name, ledger_roots=[str(other)])
        (other / "work-evidence/config.json").write_bytes(canonical_bytes(config))
        (other / "work-evidence/entities.json").write_bytes(canonical_bytes(f.registry))
        ledger = Ledger(other)
        entry = copy.deepcopy(f.entry)
        entry.update(owner_workspace=other.name, entry_id="00000000-0000-4000-8000-000000000090",
                     work_id="00000000-0000-4000-8000-000000000091")
        entry["duration"]["seconds"] = 120
        prepared = ledger.prepare({"schema_version": 1, "changes": [{"entry": entry}]})
        ledger.apply(prepared["transaction_id"], prepared["manifest_hash"])
        calc.f.config["allowed_workspaces"][other.name] = str(other)
        (calc.f.home / "config.json").write_bytes(canonical_bytes(calc.f.config))
        register = TaxRegister(f.ws, "sample-taxpayer")
        second = {"owner_workspace": other.name, "entry_id": entry["entry_id"],
                  "entry_hash": digest(ledger.committed()[0][entry["entry_id"]]), "kit_hash": None}
        data = copy.deepcopy(calc.f.bundle)
        data["work_refs"] += [second, copy.deepcopy(second)]
        data["allocations"][0]["work_refs"].append(other.name + ":" + entry["entry_id"])
        packet = register.packet(data)
        self.assertEqual(packet["unique_work_references"], 2)
        self.assertEqual(packet["allocated_amounts"]["sample-invoice"], "80.00")
        self.assertEqual(coverage(list(f.ledger.committed()[0].values()))["actual_human_seconds"], 60)
        self.assertEqual(coverage(list(ledger.committed()[0].values()))["actual_human_seconds"], 120)
