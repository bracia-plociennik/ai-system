"""Anonymous private-register tests; no taxpayer or real legal policy."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path
from decimal import Decimal

import test_work_evidence_ledger as fixtures
from work_evidence import EvidenceError, canonical_bytes, digest, file_hash, safe_path
from work_evidence_tax_evidence import TaxRegister, amount


class TaxEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.LedgerTests()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.f.commit()
        self.home = self.f.ws / "private-tax/sample-taxpayer"
        (self.home / "evidence").mkdir(parents=True)
        self.home.chmod(0o700)
        self.source = self.home / "evidence/proof.txt"
        self.source.write_text("TAX_PRIVATE_CANARY", encoding="utf-8")
        self.config = {"schema_version": 1, "taxpayer_id": "sample-taxpayer",
                       "owner_workspace": "sample-workspace", "currencies": ["PLN"],
                       "source_roots": {"tax-evidence": "evidence"},
                       "allowed_workspaces": {"sample-workspace": str(self.f.ws)}}
        (self.home / "config.json").write_bytes(canonical_bytes(self.config))
        self.ref = {"root_alias": "tax-evidence", "relative_path": "proof.txt",
                    "sha256": file_hash(self.source), "observed_at": "2026-10-02T10:00:00+02:00",
                    "evidence_state": "asserted"}
        key = "sample-workspace:" + fixtures.ENTRY_ID
        self.work_ref = {"owner_workspace": "sample-workspace", "entry_id": fixtures.ENTRY_ID,
                         "entry_hash": digest(self.f.ledger.committed()[0][fixtures.ENTRY_ID]),
                         "kit_hash": None}
        self.bundle = {"schema_version": 1, "taxpayer_id": "sample-taxpayer", "tax_year": 2026,
                       "ip_items": [{"ip_id": "sample-ip", "taxpayer_id": "sample-taxpayer",
                                     "rights_holder_id": "sample-taxpayer", "description": "Private sample IP"}],
                       "rights": [{"right_id": "sample-right", "ip_id": "sample-ip",
                                   "taxpayer_id": "sample-taxpayer", "kind": "ownership",
                                   "effective_start": "2026-01-01", "end_exclusive": None,
                                   "source_refs": [self.ref], "evidence_state": "asserted"}],
                       "finance": [{"finance_id": "sample-invoice", "taxpayer_id": "sample-taxpayer",
                                    "category": "invoice", "amount": "100.00", "currency": "PLN",
                                    "date": "2026-10-02", "source_refs": [self.ref],
                                    "evidence_state": "asserted"}],
                       "allocations": [{"allocation_id": "sample-allocation", "finance_id": "sample-invoice",
                                        "ip_id": "sample-ip", "amount": "80.00", "currency": "PLN",
                                        "work_refs": [key]}], "work_refs": [self.work_ref]}
        self.register = TaxRegister(self.f.ws, "sample-taxpayer")

    def test_packet_readonly_unknown_eligibility_and_dedup(self):
        self.bundle["work_refs"].append(copy.deepcopy(self.work_ref))
        before = self.f.hashes()
        value = self.register.packet(self.bundle)
        self.assertEqual(value["unique_work_references"], 1)
        self.assertEqual(value["eligibility"], "unknown")

        self.assertEqual(value["allocated_amounts"], {"sample-invoice": "80.00"})
        self.assertEqual(before, self.f.hashes())
        self.assertEqual(value["gaps"], [{"category": "missing-documentation",
                                        "id": "sample-workspace:" + fixtures.ENTRY_ID}])
        self.assertNotIn("TAX_PRIVATE_CANARY", json.dumps(value))

    def test_decimal_only_bounded_no_negative_or_implicit_zero(self):
        for value in (True, 1.5, -1, "-1", "NaN", "Infinity", "1e2", "01", "1x2",
                      "1." + "1"*13, "9"*25):
            with self.subTest(value=value), self.assertRaises(EvidenceError):
                amount(value)
        self.assertEqual(amount("0.00"), Decimal("0.00"))
        self.assertIsNone(amount(None, nullable=True))
        self.bundle["finance"][0]["amount"] = None
        value = self.register.packet(self.bundle)
        self.assertIn("missing-amount", [gap["category"] for gap in value["gaps"]])

    def test_overallocation_taxpayer_currency_and_period_gaps(self):
        for target, key, value, expected in (
            ("allocations", "amount", "101", "over-allocation"),
            ("allocations", "currency", "EUR", "allocation-currency-conflict"),
            ("finance", "currency", "GBP", "unsupported-currency"),
            ("finance", "taxpayer_id", "other-taxpayer", "taxpayer-conflict"),
            ("finance", "date", "2025-10-02", "finance-period-conflict"),
            ("ip_items", "rights_holder_id", "other-taxpayer", "rights-holder-review-required"),
            ("rights", "effective_start", "2027-01-01", "missing-effective-rights"),
        ):
            changed = copy.deepcopy(self.bundle)
            changed[target][0][key] = value
            with self.subTest(expected=expected):
                packet = self.register.packet(changed)
                self.assertEqual(packet["state"], "blocked")
                self.assertIn(expected, [gap["category"] for gap in packet["gaps"]])

    def test_missing_rights_and_financial_proof(self):
        self.bundle["rights"] = []
        self.bundle["finance"][0]["source_refs"] = []
        value = self.register.packet(self.bundle)
        categories = [gap["category"] for gap in value["gaps"]]
        self.assertIn("missing-effective-rights", categories)
        self.assertIn("missing-finance-evidence", categories)

    def test_source_drift_traversal_symlink(self):
        self.source.write_text("Changed proof", encoding="utf-8")
        with self.assertRaises(EvidenceError):
            self.register.packet(self.bundle)
        for path in ("../config.json", ".env", "secrets.txt"):
            changed = copy.deepcopy(self.ref)
            changed["relative_path"] = path
            with self.subTest(path=path), self.assertRaises(EvidenceError):
                self.register.source(changed)
        link = self.home / "evidence/link.txt"
        link.symlink_to(self.source)
        changed = copy.deepcopy(self.ref)
        changed.update(relative_path="link.txt", sha256=file_hash(self.source))
        with self.assertRaises(EvidenceError):
            self.register.source(changed)

    def test_config_owner_permission_and_stale_write(self):
        self.home.chmod(0o755)
        with self.assertRaises(EvidenceError):
            TaxRegister(self.f.ws, "sample-taxpayer")
        self.home.chmod(0o700)
        changed = copy.deepcopy(self.config)
        changed["owner_workspace"] = "unknown"
        (self.home / "config.json").write_bytes(canonical_bytes(changed))
        with self.assertRaises(EvidenceError):
            TaxRegister(self.f.ws, "sample-taxpayer")
        with self.assertRaises(EvidenceError):
            self.register.packet(self.bundle)

    def test_work_owner_hash_and_void_fail(self):
        for key, value in (("owner_workspace", "unapproved"), ("entry_hash", "0"*64)):
            changed = copy.deepcopy(self.bundle)
            changed["work_refs"][0][key] = value
            with self.subTest(key=key), self.assertRaises(EvidenceError):
                self.register.packet(changed)
        entry = self.f.ledger.committed()[0][fixtures.ENTRY_ID]
        changed = copy.deepcopy(entry)
        changed.update(revision=2, previous_revision_hash=digest(entry), voided=True, reason="Invalid entry")
        self.f.commit({"schema_version": 1, "changes": [{"entry": changed}]})
        with self.assertRaises(EvidenceError):
            self.register.packet(self.bundle)

    def test_private_projection_no_public_tax_paths_or_canary(self):
        from work_evidence_report import report
        policy = {"schema_version": 1, "report_id": "sample", "recipient_id": "sample-client",
                  "client_ids": ["sample-client"], "project_ids": [], "start": "2026-10-01",
                  "end_exclusive": "2026-11-01", "coverage_attested": False, "texts": [], "recurring_care": []}
        self.assertNotIn("TAX_PRIVATE_CANARY", json.dumps(report(self.f.ledger, policy)["files"]))
        with self.assertRaises(EvidenceError):
            safe_path(self.f.ws, "private-tax/sample-taxpayer/evidence/proof.txt")

    def test_immutable_packet_stale_approval_and_unapproved_cli(self):
        value = self.register.packet(self.bundle)
        expected = digest(value)
        self.register.write(self.bundle, expected, owner_approved=True)
        before = self.f.hashes()
        self.register.write(self.bundle, expected, owner_approved=True)
        self.assertEqual(before, self.f.hashes())
        self.bundle["finance"][0]["amount"] = "200.00"
        with self.assertRaises(EvidenceError):
            self.register.write(self.bundle, expected, owner_approved=True)
        scripts = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable, "-B", str(scripts / "work-evidence-tax-evidence"),
                                 "write", "--workspace", "/missing", "--taxpayer", "sample",
                                 "--bundle", "missing.json"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)["category"], "owner-approval-required")

    def test_documented_kit_reference_no_replay_claim(self):
        from test_work_evidence_docs import DocsTests
        from work_evidence_docs import assemble, persist
        docs = DocsTests()
        docs.setUp()
        self.addCleanup(docs.doCleanups)
        procedure = copy.deepcopy(docs.procedure)
        procedure["source_refs"] = copy.deepcopy(self.f.entry["source_refs"])
        for group in ("inputs", "derivatives"):
            procedure[group][0]["source_sha256"] = procedure["source_refs"][0]["sha256"]
        procedure["work_ids"] = [fixtures.WORK_ID]
        kit = assemble(self.f.ledger, procedure)
        persist(self.f.ledger, procedure, kit["kit_hash"], owner_approved=True)
        self.bundle["work_refs"][0].update(kit_hash=kit["kit_hash"], procedure_id=procedure["procedure_id"],
                                           procedure_version=1)
        value = self.register.packet(self.bundle)
        self.assertEqual(value["state"], "evidence-only")
        self.assertEqual(value["eligibility"], "unknown")

        kit_file = self.f.ledger.runtime("documentation/" + procedure["procedure_id"]
                                        + "/v1/kit/procedure.md", exists=True)
        kit_file.write_text("Changed documentation", encoding="utf-8")
        with self.assertRaises(EvidenceError):
            self.register.packet(self.bundle)

    def test_invalid_nullable_date_and_currency_types(self):
        for value in ("", False, 0):
            changed = copy.deepcopy(self.bundle)
            changed["rights"][0]["end_exclusive"] = value
            with self.subTest(value=value), self.assertRaises(EvidenceError):
                self.register.packet(changed)
        for value in (None, [], True, ""):
            changed = copy.deepcopy(self.bundle)
            changed["finance"][0]["currency"] = value
            with self.subTest(value=value), self.assertRaises(EvidenceError):
                self.register.packet(changed)

    def test_two_workspaces_references_no_time_copy(self):
        other = self.f.root / "other-workspace"
        (other / "work-evidence").mkdir(parents=True)
        config = copy.deepcopy(self.f.config)
        config.update(workspace_id="other-workspace", ledger_roots=[str(other)])
        (other / "work-evidence/config.json").write_bytes(canonical_bytes(config))
        (other / "work-evidence/entities.json").write_bytes(canonical_bytes(self.f.registry))
        ledger = fixtures.Ledger(other)
        entry = copy.deepcopy(self.f.entry)
        entry.update(owner_workspace="other-workspace", entry_id="00000000-0000-4000-8000-000000000077",
                     work_id="00000000-0000-4000-8000-000000000078")
        prepared = ledger.prepare({"schema_version": 1, "changes": [{"entry": entry}]})
        ledger.apply(prepared["transaction_id"], prepared["manifest_hash"])
        self.config["allowed_workspaces"]["other-workspace"] = str(other)
        (self.home / "config.json").write_bytes(canonical_bytes(self.config))
        register = TaxRegister(self.f.ws, "sample-taxpayer")
        self.bundle["work_refs"].append({"owner_workspace": "other-workspace", "entry_id": entry["entry_id"],
                                        "entry_hash": digest(entry), "kit_hash": None})
        before = self.f.hashes()
        value = register.packet(self.bundle)
        self.assertEqual(value["unique_work_references"], 2)
        self.assertNotIn("actual_human_seconds", value)
        self.assertEqual(before, self.f.hashes())
