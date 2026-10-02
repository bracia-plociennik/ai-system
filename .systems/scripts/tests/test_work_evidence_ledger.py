import copy
import json
import os
import subprocess
import sys
from pathlib import Path

from test_work_evidence import ContractTests, ENTRY_ID, WORK_ID
from work_evidence import EvidenceError, canonical_bytes, digest, file_hash
from work_evidence_ledger import Ledger, coverage, period_entries, source_candidate, overlap_warnings


class LedgerTests(ContractTests):
    def setUp(self):
        super().setUp()
        self.ws = self.root / "sample-workspace"
        self.ws.mkdir()
        home = self.ws / "work-evidence"
        home.mkdir()
        self.config["ledger_roots"] = [str(self.ws)]
        (home / "config.json").write_bytes(canonical_bytes(self.config))
        (home / "entities.json").write_bytes(canonical_bytes(self.registry))
        self.ledger = Ledger(self.ws)
        self.candidate = {"schema_version": 1, "changes": [
            {"row_id": "row-one", "entry": copy.deepcopy(self.entry)}]}
        self.candidate["changes"][0]["entry"]["duration"]["seconds"] = 60

    def hashes(self):
        return {str(p.relative_to(self.root)): file_hash(p)
                for p in self.root.rglob("*") if p.is_file() and not p.is_symlink()}

    def commit(self, candidate=None, failpoint=None):
        prepared = self.ledger.prepare(candidate or self.candidate)
        result = self.ledger.apply(prepared["transaction_id"], prepared["manifest_hash"],
                                   failpoint=failpoint)
        return prepared, result

    def test_preview_readonly_even_without_index(self):
        before = self.hashes()
        output = self.ledger.preview(self.candidate)
        self.assertFalse(output["persistent_ids_reserved"])
        self.assertEqual(self.hashes(), before)

    def test_crash_at_each_stage_retry_exactly_once(self):
        for point in ("after-record-0", "before-manifest", "after-manifest",
                      "before-projection", "after-projection"):
            with self.subTest(point=point):
                # Compensating revisions preserve history between test stages.
                current = self.ledger.committed()[0].get(ENTRY_ID)
                if current:
                    updated = copy.deepcopy(current)
                    updated.update(revision=current["revision"] + 1,
                                   previous_revision_hash=digest(current), reason="Test correction")
                    self.candidate["changes"][0]["entry"] = updated
                prepared = self.ledger.prepare(self.candidate)
                with self.assertRaises(EvidenceError):
                    self.ledger.apply(prepared["transaction_id"], prepared["manifest_hash"],
                                      failpoint=point)
                before_retry = self.ledger.committed()[0]
                if point in ("after-record-0", "before-manifest"):
                    self.assertEqual(before_retry.get(ENTRY_ID), current)
                self.ledger.apply(prepared["transaction_id"], prepared["manifest_hash"])
                hashes = self.hashes()
                self.ledger.apply(prepared["transaction_id"], prepared["manifest_hash"])
                self.assertEqual(len(self.ledger.committed()[0]), 1)
                self.assertEqual(coverage(list(self.ledger.committed()[0].values()))["actual_human_seconds"], 60)
                # Progress timestamps may change; immutable canonical bytes must not.
                immutable = {k:v for k,v in hashes.items() if "work-log" in k or "commits/" in k}
                self.assertEqual(immutable, {k:v for k,v in self.hashes().items() if k in immutable})

    def test_prepare_rerun_reserves_same_ids(self):
        for field in ("entry_id", "work_id"):
            self.candidate["changes"][0]["entry"][field] = ""
        first = self.ledger.prepare(self.candidate)
        second = self.ledger.prepare(self.candidate)
        self.assertEqual(first, second)
        self.ledger.apply(first["transaction_id"], first["manifest_hash"])
        third = self.ledger.prepare(self.candidate)
        self.assertEqual(third["transaction_id"], first["transaction_id"])
        self.assertEqual(len(self.ledger.committed()[0]), 1)

    def test_stale_source_and_manifest_block_before_canonical(self):
        prepared = self.ledger.prepare(self.candidate)
        with self.assertRaises(EvidenceError):
            self.ledger.apply(prepared["transaction_id"], "0"*64)
        self.source.write_text("changed", encoding="utf-8")
        with self.assertRaises(EvidenceError):
            self.ledger.apply(prepared["transaction_id"], prepared["manifest_hash"])
        self.assertEqual(self.ledger.committed()[0], {})

    def test_exclusive_writer_and_stale_lock(self):
        prepared = self.ledger.prepare(self.candidate)
        with self.ledger.lock():
            with self.assertRaises(EvidenceError):
                self.ledger.apply(prepared["transaction_id"], prepared["manifest_hash"])
        lock = self.ws / "work-evidence/writer.lock"
        lock.write_bytes(canonical_bytes({"pid": 2147483647, "created_at": "2000-01-01"}))
        expected = file_hash(lock)
        with self.assertRaises(EvidenceError):
            self.ledger.prepare(self.candidate)
        with self.assertRaises(EvidenceError):
            self.ledger.recover_lock("0"*64)
        self.ledger.recover_lock(expected)
        self.assertFalse(lock.exists())

    def test_correction_void_and_rebuild(self):
        self.commit()
        original = copy.deepcopy(self.ledger.committed()[0][ENTRY_ID])
        corrected = copy.deepcopy(original)
        corrected.update(revision=2, previous_revision_hash=digest(original), reason="Owner correction")
        corrected["duration"]["seconds"] = 120
        self.commit({"schema_version": 1, "changes": [{"row_id": "row-correct", "entry": corrected}]})
        self.assertEqual(self.ledger.rebuild()["coverage"]["actual_human_seconds"], 120)
        index = (self.ws / "work-evidence/derived/work-index.jsonl").read_bytes()
        self.ledger.rebuild()
        self.assertEqual((self.ws / "work-evidence/derived/work-index.jsonl").read_bytes(), index)
        void = copy.deepcopy(corrected)
        void.update(revision=3, previous_revision_hash=digest(corrected), reason="Duplicate", voided=True)
        self.commit({"schema_version": 1, "changes": [{"row_id": "row-void", "entry": void}]})
        self.assertEqual(self.ledger.rebuild()["coverage"]["actual_human_seconds"], 0)
        self.assertEqual(len(list((self.ws / "work-log").rglob("r*.json"))), 3)

    def test_stale_ledger_and_duplicate_work_reject(self):
        prepared = self.ledger.prepare(self.candidate)
        other = copy.deepcopy(self.entry)
        other.update(entry_id="00000000-0000-4000-8000-000000000010",
                     work_id="00000000-0000-4000-8000-000000000011")
        self.commit({"schema_version": 1, "changes": [{"entry": other}]})
        with self.assertRaises(EvidenceError):
            self.ledger.apply(prepared["transaction_id"], prepared["manifest_hash"])
        other["entry_id"] = "00000000-0000-4000-8000-000000000012"
        with self.assertRaises(EvidenceError):
            self.ledger.preview({"schema_version": 1, "changes": [{"entry": other}]})

    def test_period_overnight_split_and_partial_aggregate(self):
        entry = copy.deepcopy(self.entry)
        entry["duration"].update(seconds=3600, basis="measured")
        entry["timing"] = {"kind": "interval", "start": "2026-10-02T23:30:00+02:00",
                           "end": "2026-10-03T00:30:00+02:00", "timezone": "Europe/Warsaw"}
        output = period_entries([entry], "2026-10-03", "2026-10-04")
        self.assertEqual(output["exact"][0]["actual_seconds"], 1800)
        entry["timing"] = {"kind": "aggregate", "start_date": "2026-10-01",
                           "end_date_exclusive": "2026-10-04"}
        output = period_entries([entry], "2026-10-03", "2026-10-04")
        self.assertEqual(output["exact"], [])
        self.assertIsNone(output["partly_overlapping_aggregates"][0]["actual_seconds"])

    def test_identical_blank_rows_need_disambiguation(self):
        item = {"entry": copy.deepcopy(self.entry)}
        with self.assertRaises(EvidenceError):
            self.ledger.preview({"schema_version": 1, "changes": [item, copy.deepcopy(item)]})

    def test_cli_preview_and_unapproved_write(self):
        path = self.ws / "candidate.json"
        path.write_bytes(canonical_bytes(self.candidate))
        scripts = Path(__file__).resolve().parents[1]
        before = self.hashes()
        for action, expected in (("preview", 0), ("prepare", 2)):
            result = subprocess.run([sys.executable, "-B", str(scripts / ("work-evidence-" + action)),
                                     "--workspace", str(self.ws), "--input", "candidate.json"],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, expected, result.stderr)
        self.assertEqual(self.hashes(), before)

    def test_missing_and_edited_index_explicitly_labeled(self):
        self.assertEqual(self.ledger.index_status()["status"], "missing")
        self.commit()
        self.assertEqual(self.ledger.index_status()["status"], "current")
        index = self.ws / "work-evidence/derived/work-index.jsonl"
        index.write_text("edited", encoding="utf-8")
        self.assertEqual(self.ledger.index_status()["status"], "stale")
        self.assertEqual(self.ledger.index_status()["canonical_coverage"]["actual_human_seconds"], 60)

    def test_config_changed_after_constructor_blocks(self):
        path = self.ws / "work-evidence/config.json"
        value = copy.deepcopy(self.config)
        value["timezone"] = "UTC"
        path.write_bytes(canonical_bytes(value))
        with self.assertRaises(EvidenceError):
            self.ledger.prepare(self.candidate)
        self.assertFalse((self.ws / "work-log").exists())

    def test_selected_osnr_adapter_never_guesses_time_or_private_text(self):
        note = self.root / "checkpoint.md"
        note.write_text("O: mock tested\nS: DONE\nN: review\nR: tomorrow\n"
                        "## Raw Check-In\nRAW_CANARY\n## Working Dump\nDUMP_CANARY", encoding="utf-8")
        ref = copy.deepcopy(self.entry["source_refs"][0])
        ref.update(relative_path="checkpoint.md", sha256=file_hash(note))
        before = self.hashes()
        result = source_candidate(ref, self.config, role="checkpoint", fact_date="2026-10-02")
        self.assertIsNone(result["duration_seconds"])
        self.assertTrue(result["requires_owner_confirmation"])
        self.assertNotIn("CANARY", json.dumps(result))
        self.assertEqual(self.hashes(), before)

    def test_session_correction_budget_and_human_only_totals(self):
        entry = copy.deepcopy(self.candidate["changes"][0]["entry"])
        sid = "00000000-0000-4000-8000-000000000090"
        entry["duration"]["session_id"] = sid
        session = {k:copy.deepcopy(entry[k]) for k in
                   ("schema_version","owner_workspace","performed_on","recorded_at",
                    "timing","duration","source_refs")}
        session["session_id"] = sid
        session["allocations"] = [{"entry_id": ENTRY_ID, "seconds": 60}]
        self.commit({"schema_version":1,"changes":[{"entry":entry}],"sessions":[session]})
        corrected = copy.deepcopy(entry)
        corrected.update(revision=2, previous_revision_hash=digest(entry), reason="Correct actual allocation")
        corrected["duration"]["seconds"] = 40
        self.commit({"schema_version":1,"changes":[{"entry":corrected}]})
        corrected.update(revision=3, previous_revision_hash=digest(corrected), reason="Over-allocation")
        corrected["duration"]["seconds"] = 61
        with self.assertRaises(EvidenceError):
            self.ledger.preview({"schema_version":1,"changes":[{"entry":corrected}]})
        automated = copy.deepcopy(self.entry)
        automated["actor_kind"] = "automation"
        automated["duration"]["seconds"] = 1000
        self.assertEqual(coverage([entry, automated])["actual_human_seconds"], 60)

    def test_standard_tasknote_osnr_and_duplicate_labels(self):
        note = self.root / "tasknote.md"
        note.write_text("## Checkpoint OSNR\n- O \u2014 Outcome: mock tested\n"
                        "- S \u2014 Status: DONE\n- N \u2014 Next: owner review\n"
                        "- R \u2014 Resume: event\n## TODO\n- [ ] next action\n",
                        encoding="utf-8")
        ref = copy.deepcopy(self.entry["source_refs"][0])
        ref.update(relative_path="tasknote.md", sha256=file_hash(note))
        result = source_candidate(ref, self.config, role="tasknote", fact_date="2026-10-02")
        self.assertEqual(result["osnr_hints"], {"O": "Outcome: mock tested",
                         "S": "Status: DONE", "N": "Next: owner review", "R": "Resume: event"})
        self.assertIsNone(result["duration_seconds"])
        note.write_text(note.read_text(encoding="utf-8") + "O: conflicting outcome\n",
                        encoding="utf-8")
        ref["sha256"] = file_hash(note)
        result = source_candidate(ref, self.config, role="tasknote", fact_date="2026-10-02")
        self.assertNotIn("O", result["osnr_hints"])
