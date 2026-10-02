"""Synthetic documentation/replay boundaries; no real human success claim."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

import test_work_evidence_ledger as fixtures
from work_evidence import EvidenceError, digest, file_hash, canonical_bytes
from work_evidence_docs import assemble, persist, record_replay, verify_replay


class DocsTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.LedgerTests()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.ledger = self.f.ledger
        ref = copy.deepcopy(self.f.entry["source_refs"][0])
        approved = {"source_index": 0, "text": "Use anonymous mock input only",
                    "source_sha256": ref["sha256"], "text_sha256": digest("Use anonymous mock input only"),
                    "purpose": "documentation", "approved_by": "owner",
                    "approved_at": "2026-10-02T10:00:00+02:00"}
        self.procedure = {"schema_version": 1, "procedure_id": "sample-procedure", "version": 1,
                          "work_ids": [], "target_outcome": "Mock result reproducible",
                          "skills": ["Python programmer"], "environment": {"python": "3.14"},
                          "prerequisites": ["Isolated local environment"],
                          "inputs": [approved], "steps": [{"id": "run", "action": "Run local mock",
                                                          "expected": "Anonymous result"}],
                          "tests": [{"id": "assert-result", "assertion": "Expected result matches"}],
                          "stop_conditions": ["Missing mock input: stop"],
                          "rollback": ["Discard isolated test workspace"], "limits": ["Mock only"],
                          "source_refs": [ref], "derivatives": [copy.deepcopy(approved)]}
        self.kit = assemble(self.ledger, self.procedure)

    def human(self):
        signed = self.f.root / "replay-attestation.md"
        signed.write_text("Synthetic attestation fixture, not a real pilot", encoding="utf-8")
        ref = copy.deepcopy(self.procedure["source_refs"][0])
        ref.update(relative_path=signed.name, sha256=file_hash(signed))
        record = {"schema_version": 1, "tester_id": "sample-programmer", "tester_role": "programmer",
                  "consent": True, "kit_hash": self.kit["kit_hash"],
                  "environment": {"python": "3.14"}, "start": "2026-10-02T10:00:00+02:00",
                  "end": "2026-10-02T11:00:00+02:00", "successful_assertions": ["assert-result"],
                  "failed_steps": [], "ambiguous_steps": [], "help_requested": False,
                  "kind": "human", "signed_evidence_ref": ref, "signed_at": "2026-10-02T11:10:00+02:00"}
        approval = {"kit_hash": self.kit["kit_hash"], "replay_hash": digest(record),
                    "signed_evidence_sha256": ref["sha256"], "approved_by": "owner",
                    "approved_at": "2026-10-02T11:20:00+02:00", "purpose": "human-replay",
                    "human_evidence_verified": True}
        return record, approval

    def write(self):
        return persist(self.ledger, self.procedure, self.kit["kit_hash"], owner_approved=True)

    def test_preview_readonly_no_original_paths_or_source_body(self):
        before = self.f.hashes()
        value = assemble(self.ledger, self.procedure)
        self.assertEqual(before, self.f.hashes())
        content = json.dumps(value["files"])
        self.assertNotIn("confirmation.json", content)
        self.assertNotIn("duration_seconds", content)
        self.assertEqual(value["state"], "documented")
        self.assertEqual(json.loads(value["files"]["identity.json"])["kit_hash"], value["kit_hash"])

    def test_required_sections_and_work_link(self):
        for field in ("prerequisites", "rollback", "tests", "source_refs"):
            altered = copy.deepcopy(self.procedure)
            altered[field] = []
            with self.subTest(field=field), self.assertRaises(EvidenceError):
                assemble(self.ledger, altered)
        self.procedure["work_ids"] = [fixtures.WORK_ID]
        with self.assertRaises(EvidenceError):
            assemble(self.ledger, self.procedure)
        self.f.commit()
        self.assertEqual(len(assemble(self.ledger, self.procedure)["binding"]["source_state"]["entries"]), 1)

    def test_immutable_and_stale_source(self):
        self.write()
        before = self.f.hashes()
        self.write()
        self.assertEqual(before, self.f.hashes())
        changed = copy.deepcopy(self.procedure)
        changed["target_outcome"] = "Different target"
        with self.assertRaises(EvidenceError):
            persist(self.ledger, changed, assemble(self.ledger, changed)["kit_hash"], owner_approved=True)
        self.f.source.write_text("PRIVATE_CANARY", encoding="utf-8")
        with self.assertRaises(EvidenceError) as raised:
            assemble(self.ledger, self.procedure)
        self.assertNotIn("PRIVATE_CANARY", str(raised.exception))

    def test_approval_binding_and_unsafe_sources(self):
        for key, value in (("purpose", "publication"), ("approved_by", "agent"),
                           ("text_sha256", "0"*64), ("source_sha256", "0"*64)):
            changed = copy.deepcopy(self.procedure)
            changed["inputs"][0][key] = value
            with self.subTest(key=key), self.assertRaises(EvidenceError):
                assemble(self.ledger, changed)
        for path in ("private-tax/proof.md", "../proof.md", "dump/proof.md"):
            changed = copy.deepcopy(self.procedure)
            changed["source_refs"][0]["relative_path"] = path
            with self.subTest(path=path), self.assertRaises(EvidenceError):
                assemble(self.ledger, changed)

    def test_automated_assisted_failed_and_incomplete_replay_block(self):
        record, approval = self.human()
        for key, value in (("kind", "automated"), ("tester_id", "owner"), ("consent", False),
                           ("help_requested", True), ("failed_steps", ["run"]),
                           ("ambiguous_steps", ["run"]), ("successful_assertions", []),
                           ("successful_assertions", [{}]), ("environment", {"python": "wrong"}),
                           ("kit_hash", "0"*64)):
            changed = copy.deepcopy(record)
            changed[key] = value
            with self.subTest(key=key), self.assertRaises(EvidenceError):
                verify_replay(self.ledger, self.procedure, self.kit["kit_hash"], changed, approval)

    def test_signed_evidence_and_owner_approval_required(self):
        record, approval = self.human()
        for key, value in (("approved_by", "agent"), ("human_evidence_verified", False),
                           ("purpose", "documentation"), ("replay_hash", "0"*64),
                           ("signed_evidence_sha256", "0"*64)):
            changed = copy.deepcopy(approval)
            changed[key] = value
            with self.subTest(key=key), self.assertRaises(EvidenceError):
                verify_replay(self.ledger, self.procedure, self.kit["kit_hash"], record, changed)
        (self.f.root / "replay-attestation.md").write_text("Changed", encoding="utf-8")
        with self.assertRaises(EvidenceError):
            verify_replay(self.ledger, self.procedure, self.kit["kit_hash"], record, approval)

    def test_timestamp_order(self):
        record, approval = self.human()
        changed = copy.deepcopy(record)
        changed["signed_at"] = changed["start"]
        approval["replay_hash"] = digest(changed)
        with self.assertRaises(EvidenceError):
            verify_replay(self.ledger, self.procedure, self.kit["kit_hash"], changed, approval)
        record, approval = self.human()
        approval["approved_at"] = record["start"]
        with self.assertRaises(EvidenceError):
            verify_replay(self.ledger, self.procedure, self.kit["kit_hash"], record, approval)

    def test_human_fixture_persist_and_exact_retry(self):
        self.write()
        record, approval = self.human()
        value = record_replay(self.ledger, self.procedure, self.kit["kit_hash"], record, approval,
                              owner_approved=True)
        self.assertEqual(value["state"], "replay-passed")
        self.assertIn("attestation", value["evidence"])
        before = self.f.hashes()
        record_replay(self.ledger, self.procedure, self.kit["kit_hash"], record, approval, owner_approved=True)
        self.assertEqual(before, self.f.hashes())

    def test_missing_and_changed_kit_never_pass(self):
        record, approval = self.human()
        with self.assertRaises((EvidenceError, FileNotFoundError)):
            record_replay(self.ledger, self.procedure, self.kit["kit_hash"], record, approval, owner_approved=True)
        self.write()
        path = self.f.ws / "work-evidence/documentation/sample-procedure/v1/kit/procedure.md"
        path.write_text("Altered", encoding="utf-8")
        before = self.f.hashes()
        with self.assertRaises(EvidenceError):
            record_replay(self.ledger, self.procedure, self.kit["kit_hash"], record, approval, owner_approved=True)
        self.assertEqual(before, self.f.hashes())

    def test_data_not_execution_and_cli_guard(self):
        self.procedure["steps"][0]["action"] = "<script>bad</script> [link](https://example.invalid)"
        content = assemble(self.ledger, self.procedure)["files"]["procedure.md"]
        self.assertNotIn("<script>", content)
        self.assertNotIn("[link](", content)
        scripts = Path(__file__).resolve().parents[1]
        for action in ("write", "record-replay"):
            result = subprocess.run([sys.executable, "-B", str(scripts / "work-evidence-documentation"),
                                     action, "--workspace", "/does-not-exist", "--procedure", "missing.json"],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stderr)["category"], "owner-approval-required")
