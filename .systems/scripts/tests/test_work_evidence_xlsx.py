import copy
import io
import json
import sys
import subprocess
import unittest
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import test_work_evidence_ledger as fixtures
from work_evidence import EvidenceError, digest, file_hash
from work_evidence_ledger import atomic_write
from work_evidence_xlsx import Tracker, MANUAL, load_book, literal, sheet_values


class XlsxTests(unittest.TestCase):
    def setUp(self):
        fixture = fixtures.LedgerTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.fixture = fixture
        self.tracker = Tracker(fixture.ledger)
        self.tracker.export()

    def edit(self, operation):
        book = load_book(self.tracker.path.read_bytes())
        operation(book)
        stream = io.BytesIO()
        book.save(stream)
        self.tracker.path.write_bytes(stream.getvalue())

    def row(self, **changes):
        value = dict.fromkeys(MANUAL)
        value.update(action="new", performed_on="2026-10-02", duration_seconds=600,
                     basis="owner-confirmed", client_id="sample-client", project_id="sample-project",
                     title_internal="Custom result", outcome="Mock result", status="done", activity_kind="development")
        value.update(changes)
        return [value[k] for k in MANUAL]

    def add(self, row=None):
        self.edit(lambda b: literal(b["Manual Inputs"], row or self.row()))

    def apply(self, **kwargs):
        prepared = self.tracker.prepare()
        self.tracker.apply(prepared["transaction_id"], prepared["manifest_hash"], **kwargs)
        return prepared

    def test_roundtrip_rerun_reorder_readonly(self):
        self.add()
        before = self.fixture.hashes()
        self.tracker.preview()
        self.assertEqual(before, self.fixture.hashes())
        first = self.apply()
        self.assertEqual(self.tracker.preview()["status"], "no-new-rows")
        self.tracker.apply(first["transaction_id"], first["manifest_hash"])
        self.assertEqual(len(self.fixture.ledger.committed()[0]), 1)
        self.add(self.row(title_internal="Second result"))
        self.edit(lambda b: b["Manual Inputs"].move_range("A2:Q3", rows=2))
        self.apply()
        self.assertEqual(len(self.fixture.ledger.committed()[0]), 2)

    def test_correct_void_preserve_history(self):
        self.add()
        self.apply()
        entry = next(iter(self.fixture.ledger.committed()[0].values()))
        self.add(self.row(row_id="correction", action="correct", entry_id=entry["entry_id"],
                          base_revision=1, duration_seconds=1200, reason="Owner correction"))
        self.apply()
        self.add(self.row(row_id="void", action="void", entry_id=entry["entry_id"],
                          base_revision=2, reason="Wrong work entry"))
        self.apply()
        current = self.fixture.ledger.committed()[0][entry["entry_id"]]
        self.assertEqual(current["revision"], 3)
        self.assertTrue(current["voided"])
        self.assertEqual(len(list(self.fixture.ws.rglob("r*.json"))), 3)

    def test_blank_duplicates_and_generated_edit(self):
        self.add()
        self.add()
        with self.assertRaises(EvidenceError):
            self.tracker.prepare()
        self.edit(lambda b: setattr(b["Summary"]["B3"], "value", 999))
        with self.assertRaises(EvidenceError) as error:
            self.tracker.preview()
        self.assertEqual(error.exception.category, "generated-sheet-conflict")
        self.assertEqual(self.fixture.ledger.committed()[0], {})

    def test_open_stale_approval_and_base(self):
        self.add()
        prepared = self.tracker.prepare()
        lock = self.tracker.path.with_name("~$" + self.tracker.path.name)
        lock.touch()
        with self.assertRaises(EvidenceError):
            self.tracker.apply(prepared["transaction_id"], prepared["manifest_hash"])
        lock.unlink()
        self.edit(lambda b: setattr(b["Manual Inputs"]["I2"], "value", 700))
        with self.assertRaises(EvidenceError):
            self.tracker.apply(prepared["transaction_id"], prepared["manifest_hash"])
        self.assertEqual(self.fixture.ledger.committed()[0], {})
        self.apply()
        entry = next(iter(self.fixture.ledger.committed()[0].values()))
        self.add(self.row(action="correct", entry_id=entry["entry_id"], base_revision=7, reason="Wrong base"))
        with self.assertRaises(EvidenceError):
            self.tracker.prepare()

    def test_crash_after_canonical_recovery_same_ids(self):
        self.add()
        prepared = self.tracker.prepare()
        with self.assertRaises(EvidenceError):
            self.tracker.apply(prepared["transaction_id"], prepared["manifest_hash"], failpoint="after-canonical")
        self.assertEqual(len(self.fixture.ledger.committed()[0]), 1)
        self.tracker.apply(prepared["transaction_id"], prepared["manifest_hash"])
        self.assertEqual(self.tracker.preview()["status"], "no-new-rows")

    def test_crash_after_replacement_and_manual_edit_stop(self):
        self.add()
        prepared = self.tracker.prepare()
        with self.assertRaises(EvidenceError):
            self.tracker.apply(prepared["transaction_id"], prepared["manifest_hash"], failpoint="after-workbook")
        self.tracker.apply(prepared["transaction_id"], prepared["manifest_hash"])
        self.assertEqual(len(self.fixture.ledger.committed()[0]), 1)
        self.add(self.row(title_internal="Second outcome"))
        prepared = self.tracker.prepare()
        with self.assertRaises(EvidenceError):
            self.tracker.apply(prepared["transaction_id"], prepared["manifest_hash"], failpoint="after-workbook")
        self.edit(lambda b: setattr(b["Manual Inputs"]["M3"], "value", "Owner new edit"))
        before = file_hash(self.tracker.path)
        with self.assertRaises(EvidenceError):
            self.tracker.apply(prepared["transaction_id"], prepared["manifest_hash"])
        self.assertEqual(file_hash(self.tracker.path), before)

    def test_leading_text_literal_formula_and_hyperlink_reject(self):
        for prefix in ("=", "+", "-", "@"):
            self.add(self.row(title_internal=prefix + "Custom result", outcome=prefix + "Literal output"))
        self.apply()
        book = load_book(self.tracker.path.read_bytes())
        self.assertTrue(all(book["Work Entries"].cell(i, 6).data_type == "s" for i in range(2, 6)))
        self.edit(lambda b: setattr(b["Manual Inputs"]["M2"], "value", "=1+1"))
        with self.assertRaises(EvidenceError):
            self.tracker.preview()

    def test_external_macro_dtd_zip_reject(self):
        original = self.tracker.path.read_bytes()
        for name, payload in (("xl/vbaProject.bin", b"fake"),
                              ("xl/externalLinks/evil.xml", b"<x/>"),
                              ("evil.xml", b'<!DOCTYPE x [<!ENTITY a "b">]><x>&a;</x>'),
                              ("../evil.xml", b"<x/>"),
                              ("huge.xml", b" " * 1000000)):
            stream = io.BytesIO(original)
            with zipfile.ZipFile(stream, "a", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr(name, payload)
            with self.subTest(name=name), self.assertRaises(EvidenceError):
                load_book(stream.getvalue())

    def test_privacy_and_readable_controls(self):
        self.add()
        self.apply()
        book = load_book(self.tracker.path.read_bytes())
        for sheet in book:
            self.assertEqual(sheet.freeze_panes, "A2")
            self.assertTrue(sheet.auto_filter.ref)
            self.assertGreaterEqual(sheet.row_dimensions[1].height, 30)
            values = str(sheet_values(sheet))
            self.assertNotIn(str(self.fixture.root), values)
            self.assertNotIn("private-tax", values)
        self.assertEqual(book["Summary"]["B3"].value, 10)

    def test_refresh_after_external_commit_preserves_manual_and_receipts(self):
        self.add()
        self.apply()
        self.add(self.row(title_internal="Unimported draft"))
        before = sheet_values(load_book(self.tracker.path.read_bytes())["Manual Inputs"])
        prepared = self.fixture.ledger.prepare(copy.deepcopy(self.fixture.candidate))
        self.fixture.ledger.apply(prepared["transaction_id"], prepared["manifest_hash"])
        with self.assertRaises(EvidenceError):
            self.tracker.preview()
        self.tracker.export()
        book = load_book(self.tracker.path.read_bytes())
        self.assertEqual(sheet_values(book["Manual Inputs"]), before)
        self.assertEqual(book["Import Receipts"].max_row, 2)
        self.apply()
        self.assertEqual(len(self.fixture.ledger.committed()[0]), 3)

    def test_acknowledged_row_edit_requires_new_correction_row(self):
        self.add()
        self.apply()
        self.edit(lambda b: setattr(b["Manual Inputs"]["I2"], "value", 700))
        before = self.fixture.hashes()
        with self.assertRaises(EvidenceError) as error:
            self.tracker.prepare()
        self.assertEqual(error.exception.category, "acknowledged-row-edited")
        self.assertEqual(self.fixture.hashes(), before)

    def test_prepare_snapshots_input_and_retry_reserves_same_ids(self):
        self.add()
        input_hash = file_hash(self.tracker.path)
        prepared = self.tracker.prepare()
        backup = self.fixture.ledger.runtime("xlsx/backups/" + input_hash + ".xlsx")
        self.assertEqual(file_hash(backup), input_hash)
        self.assertEqual(self.tracker.prepare(), prepared)

    def test_corrupt_view_restore_from_hash_bound_backup(self):
        self.add()
        self.apply()
        output_hash = file_hash(self.tracker.path)
        backup = self.fixture.ledger.runtime("xlsx/backups/" + output_hash + ".xlsx")
        self.tracker.path.write_bytes(b"corrupt fixture")
        with self.assertRaises(EvidenceError):
            self.tracker.preview()
        self.assertEqual(file_hash(backup), output_hash)
        atomic_write(self.tracker.path, backup.read_bytes())
        self.tracker.export()
        self.assertEqual(len(self.fixture.ledger.committed()[0]), 1)
        self.assertEqual(self.tracker.preview()["status"], "no-new-rows")

    def test_old_backup_cannot_drop_committed_import_receipts(self):
        self.add()
        input_hash = file_hash(self.tracker.path)
        self.apply()
        backup = self.fixture.ledger.runtime("xlsx/backups/" + input_hash + ".xlsx")
        atomic_write(self.tracker.path, backup.read_bytes())
        before = self.fixture.hashes()
        with self.assertRaises(EvidenceError) as error:
            self.tracker.export()
        self.assertEqual(error.exception.category, "xlsx-recovery-required")
        self.assertEqual(before, self.fixture.hashes())

    def test_cli_writes_require_approval_before_filesystem_access(self):
        cli = Path(__file__).resolve().parents[1] / "work-evidence-xlsx"
        for action in ("export", "prepare", "apply", "recover"):
            result = subprocess.run([sys.executable, "-B", str(cli), action,
                                     "--workspace", "/nonexistent/private-sentinel"],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("owner-approval-required", result.stderr)
            self.assertNotIn("private-sentinel", result.stderr)

    def test_pending_sidecar_tamper_rejected_before_canonical_write(self):
        self.add()
        prepared = self.tracker.prepare()
        path = self.fixture.ledger.runtime("xlsx/pending/" + prepared["transaction_id"] + ".json")
        pending = json.loads(path.read_text())
        pending["rows"][0][12] = "Unapproved changed title"
        path.write_text(json.dumps(pending))
        with self.assertRaises(EvidenceError) as error:
            self.tracker.apply(prepared["transaction_id"], prepared["manifest_hash"])
        self.assertEqual(error.exception.category, "projection-conflict")
        self.assertEqual(self.fixture.ledger.committed()[0], {})


if __name__ == "__main__":
    unittest.main()
