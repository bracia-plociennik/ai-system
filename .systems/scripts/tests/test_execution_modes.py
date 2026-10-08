"""Behavioral regressions for declared scope, decisions and source-bound fallback."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from execution_modes import InvalidWork, SUPPORT, inspect_work, read_json, select_mode, workflow_support


def unit(uid="build", dependencies=None, action="implementation"):
    return {"id": uid, "dependencies": dependencies or [], "action": action,
            "dependencies_known": True, "independence_evidence": "c" * 64,
            "resources": ["files/" + uid], "gates_ready": True, "risk": "low",
            "state": "pending", "completion": None, "cause": None}


def work():
    return {"contract": 1, "mode": "auto", "request_kind": "implementation",
            "approval_ref": "owner-approved current accepted task scope", "dod": "verified outcome",
            "baseline": "baseline-001", "allowed_actions": ["implementation", "commit", "phase-8"],
            "units": [unit()], "decisions": [], "attempts": [], "quality_complete": False, "no_commit": False}


def decision(kind="owner", units=None):
    return {"id": "choose", "kind": kind, "units": units or ["build"], "state": "pending",
            "recommendation": "retain scope", "alternative": "defer affected unit",
            "impact": "unlocks affected work"}


def complete(record):
    for item in record["units"]:
        item["state"] = "completed"
        item["completion"] = {"baseline": record["baseline"], "evidence": "a" * 64}
    record["quality_complete"] = True
    return record


class ExecutionTests(unittest.TestCase):
    def test_new_default_and_explicit_human(self):
        self.assertEqual(select_mode(), "auto")
        for name in ("human", "human mode", "Human Coop"):
            self.assertEqual(select_mode(name), "human")

    def test_resume_preserves_human(self):
        self.assertEqual(select_mode(active="human", resuming=True), "human")
        with self.assertRaises(InvalidWork):
            select_mode(resuming=True)

    def test_unknown_mode_rejected(self):
        with self.assertRaises(InvalidWork):
            select_mode("whatever")

    def test_missing_approval_blocks_implementation_but_not_independent_read(self):
        record = work()
        record["approval_ref"] = None
        record["units"].append(unit("inspect", action="read-only"))
        result = inspect_work(record)
        self.assertEqual(result["ready"], ["inspect"])
        self.assertIn("build", result["blocked"])

    def test_mode_switch_does_not_create_authority(self):
        record = work()
        record["mode"] = "human"
        record["approval_ref"] = None
        self.assertIn("build", inspect_work(record)["blocked"])

    def test_planning_never_starts_code(self):
        record = work()
        record["request_kind"] = "planning"
        self.assertEqual(inspect_work(record)["ready"], [])
        record["units"] = [unit(action="artifact-write")]
        record["allowed_actions"].append("artifact-write")
        self.assertEqual(inspect_work(record)["ready"], ["build"])

    def test_analysis_remains_read_only(self):
        record = work()
        record["request_kind"] = "analysis"
        self.assertIn("build", inspect_work(record)["blocked"])

    def test_partial_blocker_and_transitive_dependents(self):
        record = work()
        record["units"] += [unit("dependent", ["build"]), unit("independent")]
        record["decisions"] = [decision()]
        result = inspect_work(record)
        self.assertEqual(result["ready"], ["independent"])
        self.assertEqual(set(result["blocked"]), {"build", "dependent"})
        self.assertEqual(result["interaction"], "queued-at-end")
        self.assertEqual(result["dod_state"], "incomplete")

    def test_unknown_dependency_fails_closed(self):
        record = work()
        record["units"][0]["dependencies"] = ["unproven"]
        with self.assertRaises(InvalidWork):
            inspect_work(record)

    def test_unknown_independence_or_gate_blocks_only_affected_unit(self):
        for key, value in (("dependencies_known", False), ("independence_evidence", None), ("gates_ready", False), ("risk", "critical"), ("resources", [])):
            with self.subTest(key=key):
                record = work()
                record["units"][0][key] = value
                record["units"].append(unit("independent"))
                self.assertEqual(inspect_work(record)["ready"], ["independent"])

    def test_shared_resource_uncertainty_blocks_other_unit(self):
        record = work()
        record["units"] += [unit("other"), unit("independent")]
        record["units"][1]["resources"] = ["files/build/child"]
        record["decisions"] = [decision()]
        self.assertEqual(inspect_work(record)["ready"], ["independent"])

    def test_cycle_rejected(self):
        record = work()
        record["units"] = [unit("build", ["second"]), unit("second", ["build"])]
        with self.assertRaises(InvalidWork):
            inspect_work(record)

    def test_pending_prerequisite_waits_without_false_block(self):
        record = work()
        record["units"].append(unit("second", ["build"]))
        result = inspect_work(record)
        self.assertEqual(result["ready"], ["build"])
        self.assertEqual(result["waiting"], ["second"])

    def test_completed_unit_cannot_skip_prerequisite(self):
        record = work()
        record["units"].append(complete({**work(), "units": [unit("second", ["build"])]})["units"][0])
        with self.assertRaises(InvalidWork):
            inspect_work(record)

    def test_technical_choice_resolvable_in_approved_scope(self):
        record = work()
        record["decisions"] = [decision("technical")]
        self.assertEqual(inspect_work(record)["auto_resolvable"], ["choose"])

    def test_external_and_sensitive_effects_require_separate_scope(self):
        for action in ("external", "production", "migration", "billing", "security", "credentials", "permissions", "destructive"):
            with self.subTest(action=action):
                record = work()
                record["units"][0]["action"] = action
                record["decisions"] = [decision("technical")]
                self.assertEqual(inspect_work(record)["ready"], [])
                self.assertEqual(inspect_work(record)["auto_resolvable"], [])
                record["allowed_actions"].append(action)
                record["decisions"] = []
                self.assertEqual(inspect_work(record)["ready"], ["build"])

    def test_human_asks_for_material_decision(self):
        record = work()
        record["mode"] = "human"
        record["decisions"] = [decision()]
        self.assertEqual(inspect_work(record)["interaction"], "ask-before-dependent-work")

    def test_human_consults_material_technical_choice(self):
        record = work()
        record["mode"] = "human"
        record["decisions"] = [decision("technical")]
        result = inspect_work(record)
        self.assertEqual(result["auto_resolvable"], [])
        self.assertEqual(result["ready"], [])
        self.assertEqual(result["interaction"], "ask-before-dependent-work")

    def test_shared_blocker_prevents_technical_resolution(self):
        record = work()
        other = unit("other")
        other["resources"] = ["files/build"]
        record["units"].append(other)
        owner = decision(units=["other"])
        owner["id"] = "owner-choice"
        record["decisions"] = [decision("technical"), owner]
        self.assertEqual(inspect_work(record)["auto_resolvable"], [])

    def test_unresolved_technical_choice_cannot_claim_completion(self):
        record = complete(work())
        record["decisions"] = [decision("technical")]
        with self.assertRaises(InvalidWork):
            inspect_work(record)

    def test_proposal_does_not_block_complete_dod(self):
        record = complete(work())
        record["decisions"] = [decision("proposal")]
        result = inspect_work(record)
        self.assertEqual(result["dod_state"], "complete")
        self.assertEqual(len(result["owner_queue"]), 1)

    def test_unconstrained_is_auto_default(self):
        self.assertEqual(inspect_work(work())["delivery_default"], "auto-unconstrained")

    def test_three_stalled_attempts_stop_only_affected_branch(self):
        record = work()
        record["units"][0]["cause"] = "parser"
        record["units"].append(unit("independent"))
        record["attempts"] = [{"cause": "parser", "evidence": None}] * 3
        self.assertEqual(inspect_work(record)["ready"], ["independent"])

    def test_real_new_evidence_resets_stall_counter(self):
        record = work()
        record["units"][0]["cause"] = "parser"
        record["attempts"] = [{"cause": "parser", "evidence": None}] * 3 + [{"cause": "parser", "evidence": "b" * 64}]
        self.assertEqual(inspect_work(record)["ready"], ["build"])

    def test_same_fingerprint_is_not_repeated_progress(self):
        record = work()
        record["units"][0]["cause"] = "parser"
        record["attempts"] = [{"cause": "parser", "evidence": "b" * 64}] * 4
        self.assertEqual(inspect_work(record)["ready"], [])

    def test_recycled_evidence_does_not_reset_stall_counter(self):
        record = work()
        record["units"][0]["cause"] = "parser"
        record["attempts"] = [{"cause": "parser", "evidence": e * 64} for e in ("a", "b", "a", "b", "a")]
        self.assertEqual(inspect_work(record)["ready"], [])

    def test_completed_metadata_cannot_exceed_scope(self):
        record = complete(work())
        record["request_kind"] = "planning"
        with self.assertRaises(InvalidWork):
            inspect_work(record)

    def test_progress_label_is_not_evidence(self):
        record = work()
        record["attempts"] = [{"cause": "parser", "evidence": "made progress"}]
        with self.assertRaises(InvalidWork):
            inspect_work(record)

    def test_current_completion_never_replays(self):
        self.assertEqual(inspect_work(complete(work()))["ready"], [])

    def test_stale_completion_rejected(self):
        record = complete(work())
        record["baseline"] = "new-baseline"
        with self.assertRaises(InvalidWork):
            inspect_work(record)

    def test_quality_needed_before_commit_or_phase8(self):
        record = complete(work())
        record["quality_complete"] = False
        result = inspect_work(record)
        self.assertFalse(result["declared_git_eligibility"]["commit"])
        self.assertFalse(result["technical_phase_8_eligible"])

    def test_git_and_final_owner_boundaries(self):
        result = inspect_work(complete(work()))
        self.assertTrue(result["declared_git_eligibility"]["commit"])
        self.assertFalse(result["declared_git_eligibility"]["push"])
        self.assertFalse(result["declared_git_eligibility"]["merge-main"])
        self.assertTrue(result["technical_phase_8_eligible"])
        self.assertEqual(result["final_owner_approval"], "awaiting-owner")

    def test_no_commit_override(self):
        record = complete(work())
        record["no_commit"] = True
        self.assertFalse(inspect_work(record)["declared_git_eligibility"]["commit"])

    def test_no_qa_granted_by_file(self):
        self.assertIn("not authority", inspect_work(work())["evidence_role"])

    def test_pending_blocker_contradicts_completed_unit(self):
        record = complete(work())
        record["decisions"] = [decision()]
        with self.assertRaises(InvalidWork):
            inspect_work(record)

    def test_malformed_fields_and_booleans(self):
        for key, value in (("contract", True), ("quality_complete", "true"), ("allowed_actions", ["made-up"]), ("dod", "")):
            record = work()
            record[key] = value
            with self.assertRaises(InvalidWork):
                inspect_work(record)

    def test_duplicate_units_and_decisions(self):
        for key, value in (("units", [unit(), unit()]), ("decisions", [decision(), decision()])):
            record = work()
            record[key] = value
            with self.assertRaises(InvalidWork):
                inspect_work(record)

    def test_unknown_fields_rejected(self):
        record = work()
        record["final_owner_yes"] = True
        with self.assertRaises(InvalidWork):
            inspect_work(record)


class CapabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def install(self):
        names = ("execution-modes", "autopilot", "owner-decision-checkpoints", "delivery-constraints")
        sources = {}
        for name in names:
            relative = ".systems/ai/core/" + name + ".md"
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("synthetic source: " + name)
            sources[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.capability = self.root / ".systems/ai/capabilities/execution-modes-v1.json"
        self.capability.parent.mkdir(parents=True, exist_ok=True)
        self.record = {"contract": 1, "capability": "execution-modes-v1", "behaviors": sorted(SUPPORT), "sources": sources,
                       "mode_mapping": {"auto": "auto", "human": "human-coop"}}
        self.save()

    def save(self):
        self.capability.write_text(json.dumps(self.record))

    def test_old_workflow_falls_back(self):
        result = workflow_support(self.root)
        self.assertEqual(result["status"], "unsupported")
        self.assertEqual(result["fallback"], "installed-local-gates")

    def test_bound_synthetic_sources_are_not_native_proof(self):
        self.install()
        result = workflow_support(self.root)
        self.assertEqual(result["status"], "source-bound")
        self.assertIn("unverified", result["evidence_role"])

    def test_changed_source_invalidates_capability(self):
        self.install()
        (self.root / ".systems/ai/core/autopilot.md").write_text("changed")
        self.assertEqual(workflow_support(self.root)["status"], "invalid")

    def test_mode_mapping_must_be_explicit_and_supported(self):
        self.install()
        del self.record["mode_mapping"]
        self.save()
        self.assertEqual(workflow_support(self.root)["status"], "invalid")
        self.record["mode_mapping"] = {"auto": "auto", "human": "auto"}
        self.save()
        self.assertEqual(workflow_support(self.root)["status"], "invalid")

    def test_missing_behavior_and_source_rejected(self):
        self.install()
        self.record["behaviors"].pop()
        self.save()
        self.assertEqual(workflow_support(self.root)["status"], "invalid")
        self.record["behaviors"] = sorted(SUPPORT)
        del self.record["sources"][".systems/ai/core/autopilot.md"]
        self.save()
        self.assertEqual(workflow_support(self.root)["status"], "invalid")

    def test_traversal_and_absolute_source_rejected(self):
        self.install()
        for name in (".systems/../outside.md", "/outside.md", ".systems/core/./alias.md"):
            self.record["sources"][name] = "a" * 64
            self.save()
            self.assertEqual(workflow_support(self.root)["status"], "invalid")
            del self.record["sources"][name]

    def test_linked_source_rejected(self):
        self.install()
        path = self.root / ".systems/ai/core/autopilot.md"
        path.unlink()
        path.symlink_to(self.root / ".systems/ai/core/execution-modes.md")
        self.assertEqual(workflow_support(self.root)["status"], "invalid")

    def test_capability_duplicate_json_fields_rejected(self):
        self.install()
        self.capability.write_text('{"contract":1,"contract":1}')
        self.assertEqual(workflow_support(self.root)["status"], "invalid")

    def test_missing_or_linked_root_and_capability_directory_fail(self):
        self.assertEqual(workflow_support(self.root / "missing")["status"], "invalid")
        self.install()
        directory = self.capability.parent
        moved = self.root / "moved"
        directory.rename(moved)
        directory.symlink_to(moved, target_is_directory=True)
        self.assertEqual(workflow_support(self.root)["status"], "invalid")

    def test_cli_inspection_is_read_only_and_valid_json(self):
        path = self.root / "work.json"
        path.write_text(json.dumps(work()))
        before = path.read_bytes()
        script = Path(__file__).resolve().parents[1] / "check-execution-modes"
        result = subprocess.run([sys.executable, "-B", str(script), "--record", str(path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["execution"]["ready"], ["build"])
        self.assertEqual(path.read_bytes(), before)

    def test_record_duplicate_fields_and_invalid_cli_fail(self):
        path = self.root / "work.json"
        path.write_text('{"contract":1,"contract":1}')
        with self.assertRaises(InvalidWork):
            read_json(path)
        script = Path(__file__).resolve().parents[1] / "check-execution-modes"
        result = subprocess.run([sys.executable, "-B", str(script), "--record", str(path)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate JSON field", result.stderr)


if __name__ == "__main__":
    unittest.main()
