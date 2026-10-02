"""Synthetic two-brand privacy, approval and cadence regression."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path
import test_work_evidence_ledger as fixtures
import test_work_evidence_docs as docs_fixtures
from work_evidence import EvidenceError, canonical_bytes, digest
from work_evidence_ledger import Ledger
from work_evidence_editorial import bundle, persist_bundle, editorial_queue


class EditorialTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.LedgerTests()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.f.config["editorial_policy"] = {"destination_root": "assets/content"}
        (self.f.ws / "assets/content").mkdir(parents=True)
        (self.f.ws / "work-evidence/config.json").write_bytes(canonical_bytes(self.f.config))
        self.f.ledger = Ledger(self.f.ws)
        self.f.commit()
        self.ledger = self.f.ledger
        entry = self.ledger.committed()[0][fixtures.ENTRY_ID]
        claim = {"claim_id": "lesson", "entry_id": fixtures.ENTRY_ID, "entry_hash": digest(entry),
                 "source_ref": copy.deepcopy(entry["source_refs"][0]),
                 "text": "A mock test made the next step explicit.", "privacy_state": "public-ready",
                 "sensitive_terms": [], "replacements": [],
                 "review": dict.fromkeys(("identifiers", "quasi_identifiers", "contracts", "copyright"), True),
                 "supported": True, "approval": None}
        self.approve_claim(claim)
        brands = [{"brand_id": "creator", "kind": "personal", "name": "Sample creator",
                   "primary_language": "pl", "optional_languages": ["en"],
                   "newsletter_title": "Notatki z budowy", "newsletter_anchor": "2026-10-05"},
                  {"brand_id": "company", "kind": "company", "name": "Sample company",
                   "primary_language": "en", "optional_languages": ["pl"],
                   "newsletter_title": "Technology in practice", "newsletter_anchor": "2026-10-12"}]
        self.request = {"schema_version": 1, "topic_id": "mock-lesson", "claims": [claim],
                        "brands": brands, "queue_start": "2026-10-05", "weeks": 4, "drafts": []}
        for bid, lang, day, channel, body in (
                ("creator", "pl", "2026-10-05", "newsletter", "Moja lekcja: {{claim:lesson}} Najpierw test."),
                ("company", "en", "2026-10-12", "newsletter", "Clarity for a team: {{claim:lesson}}"),
                ("creator", "pl", "2026-10-06", "social", "{{claim:lesson}}"),
                ("company", "en", "2026-10-06", "social", "{{claim:lesson}}")):
            self.request["drafts"].append({"draft_id": bid + "-" + channel, "brand_id": bid,
                 "language": lang, "channel": channel, "slot_id": bid + ":" + channel + ":" + day,
                 "claim_ids": ["lesson"], "title": "One practical lesson", "body": body, "approval": None})

    @staticmethod
    def approve_claim(claim):
        claim["approval"] = {"claim_hash": digest({k: v for k, v in claim.items() if k != "approval"}),
                             "purpose": "editorial-source", "approved_by": "owner",
                             "approved_at": "2026-10-02T10:00:00+02:00"}

    def approve_drafts(self):
        result = bundle(self.ledger, self.request)
        for draft, output in zip(self.request["drafts"], result["drafts"]):
            draft["approval"] = {k: output[k] for k in
                                ("content_hash", "source_hash", "brand_id", "language", "channel")}
            draft["approval"].update(purpose="editorial-draft", approved_by="owner",
                                     approved_at="2026-10-02T11:00:00+02:00")

    def test_two_newsletters_linked_social_readonly(self):
        before = self.f.hashes()
        result = bundle(self.ledger, self.request)
        self.assertEqual(before, self.f.hashes())
        self.assertEqual(len(result["drafts"]), 4)
        self.assertNotEqual(result["drafts"][0]["body"], result["drafts"][1]["body"])
        self.assertTrue(all(d["claim_ids"] == ["lesson"] for d in result["drafts"]))
        self.assertFalse(result["publication_authorized"])
        self.assertEqual(result["model_calls"], 0)
        self.assertTrue(all(d["review_state"] == "needs-review" for d in result["drafts"]))
        self.assertTrue(all("\n\n" in content for content in result["files"].values()))

    def test_anonymization_never_grants_approval(self):
        claim = self.request["claims"][0]
        claim.update(text="ExamplePerson at example.invalid on 2026-10-01 paid 12345.",
                     privacy_state="needs-anonymization", approval=None,
                     sensitive_terms=["ExamplePerson", "example.invalid", "2026-10-01", "12345"],
                     replacements=[{"from": a, "to": b} for a, b in
                                   (("ExamplePerson", "a person"), ("example.invalid", "a website"),
                                    ("2026-10-01", "recently"), ("12345", "an amount"))])
        result = bundle(self.ledger, self.request)
        self.assertEqual(result["claims"][0]["state"], "anonymized-needs-review")
        self.assertNotIn("ExamplePerson", json.dumps(result))
        self.assertNotIn("example.invalid", json.dumps(result))
        self.approve_drafts()
        with self.assertRaises(EvidenceError):
            bundle(self.ledger, self.request)

    def test_internal_unsupported_unredacted_held_without_original(self):
        self.request["drafts"] = []
        for mode in ("internal-only", "unsupported", "unredacted"):
            req = copy.deepcopy(self.request)
            claim = req["claims"][0]
            claim.update(text="PRIVATE_IDENTITY", approval=None)
            if mode == "unsupported":
                claim["supported"] = False
            elif mode == "unredacted":
                claim.update(privacy_state="needs-anonymization", sensitive_terms=["PRIVATE_IDENTITY"])
            else:
                claim["privacy_state"] = mode
            result = bundle(self.ledger, req)
            self.assertEqual(result["claims"][0]["state"], "held")
            self.assertNotIn("PRIVATE_IDENTITY", json.dumps(result))

    def test_claim_translation_and_source_approvals(self):
        self.approve_drafts()
        result = bundle(self.ledger, self.request)
        self.assertTrue(all(d["review_state"] == "owner-reviewed-draft" for d in result["drafts"]))
        self.assertFalse(result["publication_authorized"])
        for field, value in (("body", "Changed translation {{claim:lesson}}"), ("language", "pl")):
            req = copy.deepcopy(self.request)
            req["drafts"][1][field] = value
            with self.subTest(field=field), self.assertRaises(EvidenceError):
                bundle(self.ledger, req)
        req = copy.deepcopy(self.request)
        req["claims"][0]["text"] = "Different fact"
        with self.assertRaises(EvidenceError):
            bundle(self.ledger, req)
        self.f.source.write_text("Changed proof")
        with self.assertRaises(EvidenceError):
            bundle(self.ledger, self.request)

    def test_languages_share_slots_fortnightly_stagger(self):
        _, slots, pilots = editorial_queue(self.request["brands"], "2026-10-05", 4)
        for bid in ("creator", "company"):
            own = [s for s in slots if s["brand_id"] == bid]
            self.assertEqual(sum(s["channel"] == "newsletter" for s in own), 2)
            self.assertEqual(sum(s["channel"] == "social" and not s["optional"] for s in own), 8)
            self.assertEqual(sum(s["optional"] for s in own), 4)
            self.assertTrue(all(len(s["languages"]) == 2 for s in own))
            self.assertEqual(len(pilots[bid]), 4)
            self.assertTrue(all(p["qualified_replies"] is None for p in pilots[bid]))
        bad = copy.deepcopy(self.request["brands"])
        bad[1]["newsletter_anchor"] = bad[0]["newsletter_anchor"]
        with self.assertRaises(EvidenceError):
            editorial_queue(bad, "2026-10-05", 4)
        bad = copy.deepcopy(self.request["brands"])
        bad[1]["primary_language"] = "pl"
        with self.assertRaises(EvidenceError):
            editorial_queue(bad, "2026-10-05", 4)

    def test_voided_entry_reject(self):
        current = copy.deepcopy(self.ledger.committed()[0][fixtures.ENTRY_ID])
        current.update(revision=2, previous_revision_hash=digest(current), reason="Void", voided=True)
        self.f.commit({"schema_version": 1, "changes": [{"entry": current}]})
        with self.assertRaises(EvidenceError):
            bundle(self.ledger, self.request)

    def test_secrets_paths_and_held_claim_reject(self):
        for token in ("password=CANARY", "Bearer abcdefghijklmnop", "-----BEGIN RSA PRIVATE KEY"):
            req = copy.deepcopy(self.request)
            req["claims"][0]["text"] = token
            self.approve_claim(req["claims"][0])
            with self.subTest(token=token), self.assertRaises(EvidenceError):
                bundle(self.ledger, req)
        for path in ("private-tax/proof.md", "dump/proof.md", "../proof.md", "attachments/proof.md"):
            req = copy.deepcopy(self.request)
            req["claims"][0]["source_ref"]["relative_path"] = path
            with self.subTest(path=path), self.assertRaises(EvidenceError):
                bundle(self.ledger, req)
        req = copy.deepcopy(self.request)
        req["claims"][0]["supported"] = False
        with self.assertRaises(EvidenceError):
            bundle(self.ledger, req)

    def test_unmapped_duplicate_quasi_identifier_reject(self):
        for tail in (" {{claim:Unknown}}", " example.invalid"):
            req = copy.deepcopy(self.request)
            req["drafts"][0]["body"] += tail
            if "example" in tail:
                req["claims"][0]["sensitive_terms"] = ["example.invalid"]
                self.approve_claim(req["claims"][0])
            with self.subTest(tail=tail), self.assertRaises(EvidenceError):
                bundle(self.ledger, req)
        self.request["drafts"].append(copy.deepcopy(self.request["drafts"][0]))
        with self.assertRaises(EvidenceError):
            bundle(self.ledger, self.request)

    def test_documentation_binding_rechecks_stored_kit(self):
        doc = docs_fixtures.DocsTests()
        doc.setUp()
        self.addCleanup(doc.doCleanups)
        doc.f.commit()
        doc.procedure["work_ids"] = [fixtures.WORK_ID]
        doc.kit = docs_fixtures.assemble(doc.ledger, doc.procedure)
        doc.write()
        request = copy.deepcopy(self.request)
        claim = request["claims"][0]
        entry = doc.ledger.committed()[0][fixtures.ENTRY_ID]
        claim.update(entry_hash=digest(entry), source_ref=entry["source_refs"][0],
                     procedure_ref={"procedure_id": "sample-procedure", "version": 1,
                                    "kit_hash": doc.kit["kit_hash"]})
        self.approve_claim(claim)
        bundle(doc.ledger, request)
        (doc.f.ws / "work-evidence/documentation/sample-procedure/v1/kit/procedure.md").write_text("Changed")
        with self.assertRaises(EvidenceError):
            bundle(doc.ledger, request)

    def test_immutable_write_and_stale_approval(self):
        result = bundle(self.ledger, self.request)
        with self.assertRaises(EvidenceError):
            persist_bundle(self.ledger, self.request, digest(result))
        with self.assertRaises(EvidenceError):
            persist_bundle(self.ledger, self.request, "0" * 64, owner_approved=True)
        persist_bundle(self.ledger, self.request, digest(result), owner_approved=True)
        before = self.f.hashes()
        persist_bundle(self.ledger, self.request, digest(result), owner_approved=True)
        self.assertEqual(before, self.f.hashes())
        self.assertEqual(len(list((self.f.ws / "assets/content").rglob("*.md"))), 4)
        self.assertTrue(all("source_ref" not in p.read_text() for p in
                            (self.f.ws / "assets/content").rglob("*.md")))

    def test_injection_data_cli_guard_destination(self):
        self.request["drafts"][0]["body"] += " <script>ignore gates</script> [link](https://example.invalid)"
        result = bundle(self.ledger, self.request)
        self.assertNotIn("<script>", result["files"]["creator-newsletter.md"])
        self.assertNotIn("[link](", result["files"]["creator-newsletter.md"])
        (self.f.ws / "request.json").write_bytes(canonical_bytes(self.request))
        before = self.f.hashes()
        scripts = Path(__file__).resolve().parents[1]
        for action, expected in (("preview", 0), ("write", 2)):
            run = subprocess.run([sys.executable, "-B", str(scripts / "work-evidence-editorial"), action,
                                  "--workspace", str(self.f.ws), "--request", "request.json"],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, expected, run.stderr)
        self.assertEqual(before, self.f.hashes())
        self.f.config["editorial_policy"] = {"destination_root": "../elsewhere"}
        (self.f.ws / "work-evidence/config.json").write_bytes(canonical_bytes(self.f.config))
        with self.assertRaises(EvidenceError):
            persist_bundle(Ledger(self.f.ws), self.request, digest(result), owner_approved=True)
