"""Anonymous work-evidence invariants; no runtime sources or network."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from work_evidence import (
    EvidenceError, actual_seconds, file_hash, read_json, safe_path,
    validate_config, validate_entry, validate_registry, validate_session,
)

ENTRY_ID = "00000000-0000-4000-8000-000000000001"
WORK_ID = "00000000-0000-4000-8000-000000000002"


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "confirmation.json"
        self.source.write_text('{"duration_seconds":0}\n', encoding="utf-8")
        self.config = {
            "schema_version": 1, "workspace_id": "sample-workspace",
            "source_roots": {"operational": str(self.root)},
            "ledger_roots": [str(self.root)],
        }
        self.registry = {"schema_version": 1, "entities": [
            {"id": "sample-client", "kind": "client", "aliases": ["Example"]},
            {"id": "sample-project", "kind": "project", "aliases": [],
             "parent_id": "sample-client"}], "task_bindings": []}
        self.entry = {
            "schema_version": 1, "entry_id": ENTRY_ID, "work_id": WORK_ID,
            "revision": 1, "previous_revision_hash": None,
            "owner_workspace": "sample-workspace", "performed_on": "2026-10-02",
            "recorded_at": "2026-10-02T10:00:00+02:00", "actor_kind": "human",
            "client_id": "sample-client", "project_id": "sample-project",
            "title_internal": "Documented sample outcome", "activity_kind": "development",
            "outcome": "Mock assertion verified", "status": "done",
            "duration": {"seconds": 0, "basis": "owner-confirmed",
                         "evidence_ref": 0, "session_id": None},
            "timing": {"kind": "date", "date": "2026-10-02"},
            "source_refs": [{"root_alias": "operational", "relative_path": "confirmation.json",
                             "sha256": file_hash(self.source),
                             "observed_at": "2026-10-02T10:00:00+02:00",
                             "fact_date": "2026-10-02", "evidence_level": "owner-attested"}],
            "visibility": "internal",
        }

    def validate(self, entry=None):
        return validate_entry(entry or self.entry, self.config, self.registry)

    def test_zero_unknown_estimate_are_distinct(self):
        validate_config(self.config, self.root)
        self.assertEqual(actual_seconds(self.validate()), 0)
        for basis, amount in (("unknown", None), ("estimated", 600)):
            entry = copy.deepcopy(self.entry)
            entry["duration"].update(basis=basis, seconds=amount, evidence_ref=None)
            self.assertIsNone(actual_seconds(self.validate(entry)))

    def test_negative_boolean_fractional_and_unknown_positive_fail(self):
        for value in (-1, True, 0.5):
            entry = copy.deepcopy(self.entry)
            entry["duration"]["seconds"] = value
            with self.subTest(value=value), self.assertRaises(EvidenceError):
                self.validate(entry)
        self.entry["duration"]["basis"] = "unknown"
        self.entry["duration"]["seconds"] = 600
        with self.assertRaises(EvidenceError):
            self.validate()

    def test_actual_requires_provenance_including_zero(self):
        self.entry["duration"]["evidence_ref"] = None
        with self.assertRaises(EvidenceError):
            self.validate()

    def test_owner_task_binding_and_client_project_conflicts(self):
        self.entry["owner_workspace"] = "other-workspace"
        with self.assertRaises(EvidenceError):
            self.validate()
        self.registry["task_bindings"] = [
            {"task_ref": "tasks/sample.md", "owner_workspace": owner, "work_id": WORK_ID}
            for owner in ("sample-workspace", "other-workspace")]
        with self.assertRaises(EvidenceError):
            validate_registry(self.registry)

    def test_alias_and_cycle_conflicts(self):
        self.registry["entities"].append({"id": "second-client", "kind": "client",
                                         "aliases": ["example"]})
        with self.assertRaises(EvidenceError):
            validate_registry(self.registry)
        self.registry["entities"].pop()
        self.registry["entities"][0]["parent_id"] = "sample-project"
        with self.assertRaises(EvidenceError):
            validate_registry(self.registry)

    def test_no_schema_migration_or_unrecognized_fields(self):
        before = self.source.read_bytes()
        for field, value in (("schema_version", 2), ("schema_version", True),
                             ("planned_duration", 600), ("visibility", "public-ready")):
            entry = copy.deepcopy(self.entry)
            entry[field] = value
            with self.subTest(field=field), self.assertRaises(EvidenceError):
                self.validate(entry)
        self.assertEqual(self.source.read_bytes(), before)

    def test_safe_path_negative_space(self):
        for relative in ("../confirmation.json", "/etc/passwd", "a/../confirmation.json",
                         "a\\b", ".env", "private-tax/file.json", "dump/file.md",
                         "secrets.txt", "./confirmation.json", "a//b"):
            with self.subTest(relative=relative), self.assertRaises(EvidenceError):
                safe_path(self.root, relative, must_exist=False)
        (self.root / "link").symlink_to(self.source)
        with self.assertRaises(EvidenceError):
            safe_path(self.root, "link")

    def test_stale_source_fails_without_echoing_content(self):
        self.source.write_text("PRIVATE_CANARY", encoding="utf-8")
        with self.assertRaises(EvidenceError) as raised:
            self.validate()
        self.assertNotIn("PRIVATE_CANARY", str(raised.exception))

    def test_overnight_and_dst_intervals_use_utc(self):
        for start, end, expected in (
            ("2026-10-02T23:30:00+02:00", "2026-10-03T00:30:00+02:00", 3600),
            ("2026-10-25T02:30:00+02:00", "2026-10-25T02:30:00+01:00", 3600),
        ):
            entry = copy.deepcopy(self.entry)
            entry["performed_on"] = start[:10]
            entry["duration"].update(basis="measured", seconds=expected)
            entry["timing"] = {"kind": "interval", "start": start, "end": end,
                               "timezone": "Europe/Warsaw"}
            self.assertEqual(actual_seconds(self.validate(entry)), expected)

    def test_dst_nonexistent_and_missing_offsets_reject(self):
        for start in ("2026-03-29T02:30:00+01:00", "2026-10-02T10:00:00"):
            entry = copy.deepcopy(self.entry)
            entry["performed_on"] = start[:10]
            entry["duration"].update(basis="measured", seconds=0)
            entry["timing"] = {"kind": "interval", "start": start, "end": start,
                               "timezone": "Europe/Warsaw"}
            with self.assertRaises(EvidenceError):
                self.validate(entry)

    def test_aggregate_preserved_and_date_not_inferred(self):
        self.entry["timing"] = {"kind": "aggregate", "start_date": "2026-10-01",
                                "end_date_exclusive": "2026-10-04"}
        self.validate()
        self.entry["performed_on"] = "2026-10-05"
        with self.assertRaises(EvidenceError):
            self.validate()

    def test_json_duplicate_and_nonfinite_reject(self):
        for raw in ('{"a":1,"a":2}', '{"a":NaN}'):
            self.source.write_text(raw, encoding="utf-8")
            with self.assertRaises(EvidenceError):
                read_json(self.source)

    def test_session_allocations_and_malformed_choices(self):
        session = {key: copy.deepcopy(self.entry[key]) for key in
                   ("schema_version", "owner_workspace", "performed_on", "recorded_at",
                    "timing", "duration", "source_refs")}
        session["session_id"] = "00000000-0000-4000-8000-000000000003"
        session["duration"].update(seconds=60, session_id=session["session_id"])
        session["allocations"] = [{"entry_id": ENTRY_ID, "seconds": 60}]
        validate_session(session, self.config)
        session["allocations"][0]["seconds"] = 61
        with self.assertRaises(EvidenceError):
            validate_session(session, self.config)
        for field in ("status", "actor_kind"):
            broken = copy.deepcopy(self.entry)
            broken[field] = []
            with self.assertRaises(EvidenceError):
                self.validate(broken)


if __name__ == "__main__":
    unittest.main(verbosity=2)
