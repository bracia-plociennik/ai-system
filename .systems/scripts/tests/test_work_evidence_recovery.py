"""Selected recovery and fresh approval regressions."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path
import test_work_evidence_ledger as fixtures
from work_evidence import EvidenceError, digest, canonical_bytes, file_hash
from work_evidence_recovery import (init_preview, initialize, backup_preview,
                                    write_backup, restore_preview, restore)


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.LedgerTests()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.f.commit()
        self.ledger = self.f.ledger
        self.paths = ["work-evidence/derived/work-index.jsonl",
                      "work-log/2026/" + fixtures.ENTRY_ID + "/r0001.json"]

    def backup(self):
        value = backup_preview(self.ledger, self.paths)
        write_backup(self.ledger, self.paths, digest(value), owner_approved=True)
        return digest(value)

    def test_init_readonly_approval_identity_existing(self):
        ws = self.f.root / "fresh-workspace"
        ws.mkdir()
        config = copy.deepcopy(self.f.config)
        config.update(workspace_id=ws.name, ledger_roots=[str(ws)])
        request = {"schema_version": 1, "config": config, "entities": self.f.registry}
        before = self.f.hashes()
        value = init_preview(ws, request)
        self.assertEqual(before, self.f.hashes())
        with self.assertRaises(EvidenceError):
            initialize(ws, request, digest(value))
        initialize(ws, request, digest(value), owner_approved=True)
        before = self.f.hashes()
        with self.assertRaises(EvidenceError):
            initialize(ws, request, digest(value), owner_approved=True)
        self.assertEqual(before, self.f.hashes())

    def test_backup_readonly_immutable_hashes_scope(self):
        before = self.f.hashes()
        value = backup_preview(self.ledger, self.paths)
        self.assertEqual(before, self.f.hashes())
        with self.assertRaises(EvidenceError):
            write_backup(self.ledger, self.paths, digest(value))
        bid = self.backup()
        before = self.f.hashes()
        write_backup(self.ledger, self.paths, bid, owner_approved=True)
        self.assertEqual(before, self.f.hashes())
        for path in ("private-tax/a.json", "../file", "work-evidence/backups/x.json",
                     "work-evidence/restore-journals/x.json", "assets/content/a.md"):
            with self.subTest(path=path), self.assertRaises(EvidenceError):
                backup_preview(self.ledger, [path])

    def test_restore_reconciles_canonical_and_rebuild(self):
        bid = self.backup()
        expected = {p: file_hash(self.f.ws / p) for p in self.paths}
        (self.f.ws / self.paths[0]).write_text("Corrupt view")
        (self.f.ws / self.paths[1]).write_text("Corrupt canonical")
        value = restore_preview(self.ledger, bid)
        with self.assertRaises(EvidenceError):
            restore(self.ledger, value, digest(value))
        restore(self.ledger, value, digest(value), owner_approved=True)
        self.assertEqual({p: file_hash(self.f.ws / p) for p in self.paths}, expected)
        self.assertEqual(self.ledger.rebuild()["coverage"]["actual_human_seconds"], 60)
        self.assertEqual(file_hash(self.f.ws / self.paths[0]), expected[self.paths[0]])

    def test_newer_selected_unselected_edit_stops(self):
        bid = self.backup()
        value = restore_preview(self.ledger, bid)
        (self.f.ws / "work-evidence/other.json").write_text("New user edit")
        before = self.f.hashes()
        with self.assertRaises(EvidenceError) as raised:
            restore(self.ledger, value, digest(value), owner_approved=True)
        self.assertEqual(raised.exception.category, "newer-user-edits")
        self.assertEqual(before, self.f.hashes())

    def test_newer_revisions_never_removed(self):
        bid = self.backup()
        current = copy.deepcopy(self.ledger.committed()[0][fixtures.ENTRY_ID])
        current.update(revision=2, previous_revision_hash=digest(current), reason="New result")
        self.f.commit({"schema_version": 1, "changes": [{"entry": current}]})
        before = self.f.hashes()
        with self.assertRaises(EvidenceError) as raised:
            restore_preview(self.ledger, bid)
        self.assertEqual(raised.exception.category, "newer-canonical-records")
        self.assertEqual(before, self.f.hashes())

    def test_interrupted_restore_resume(self):
        for failpoint in ("before-receipt-0", "after-file-0"):
            with self.subTest(failpoint=failpoint):
                bid = self.backup()
                (self.f.ws / self.paths[0]).write_text("Corrupt view " + failpoint)
                preview = restore_preview(self.ledger, bid)
                with self.assertRaises(EvidenceError):
                    restore(self.ledger, preview, digest(preview), owner_approved=True, failpoint=failpoint)
                self.assertEqual(restore(self.ledger, preview, digest(preview), owner_approved=True)["state"],
                                 "restored")
                before = self.f.hashes()
                restore(self.ledger, preview, digest(preview), owner_approved=True)
                self.assertEqual(before, self.f.hashes())

    def test_interrupted_newer_edit_and_corrupt_backup(self):
        bid = self.backup()
        (self.f.ws / self.paths[0]).write_text("Corrupt view")
        preview = restore_preview(self.ledger, bid)
        with self.assertRaises(EvidenceError):
            restore(self.ledger, preview, digest(preview), owner_approved=True, failpoint="before-receipt-0")
        (self.f.ws / self.paths[0]).write_text("New user edit")
        before = self.f.hashes()
        with self.assertRaises(EvidenceError):
            restore(self.ledger, preview, digest(preview), owner_approved=True)
        self.assertEqual(before, self.f.hashes())
        self.ledger.runtime("backups/" + bid + "/files/" + self.paths[0]).write_text("Corrupt backup")
        with self.assertRaises(EvidenceError):
            restore_preview(self.ledger, bid)

    def test_concurrent_lock_cli_guard(self):
        value = backup_preview(self.ledger, self.paths)
        with self.ledger.lock(), self.assertRaises(EvidenceError):
            write_backup(self.ledger, self.paths, digest(value), owner_approved=True)
        scripts = Path(__file__).resolve().parents[1]
        for action in ("init", "backup", "restore"):
            run = subprocess.run([sys.executable, "-B", str(scripts / "work-evidence-recovery"), action,
                                  "--workspace", "/missing"], capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(json.loads(run.stderr)["category"], "owner-approval-required")
