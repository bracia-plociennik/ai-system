"""Behavioral regressions for declared scope, decisions and source-bound fallback."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from execution_modes import InvalidWork, WORKFLOW_SOURCES, inspect_work, inspect_workflow_state, read_json, resolve_selection, select_mode, workflow_support


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
    def test_selection_scope_and_precedence(self):
        task = {"mode": "auto", "scope": "task", "scope_id": "task-1", "source": "current owner"}
        resumed = {"mode": "human", "scope": "project", "scope_id": "project-1", "source": "recorded owner"}
        session = {"mode": "auto", "scope": "session", "scope_id": "session-1", "source": "explicit session owner"}
        project = {"mode": "auto", "scope": "project", "scope_id": "project-1", "source": "project owner"}
        self.assertEqual(resolve_selection(task, resumed, session, project, "session-1"), task)
        self.assertEqual(resolve_selection(resumed=resumed, session=session, project=project, session_id="session-1"), resumed)
        self.assertEqual(resolve_selection(session=session, project=project, session_id="session-1"), session)
        self.assertEqual(resolve_selection(project=project), project)
        self.assertEqual(resolve_selection()["mode"], "auto")

    def test_selection_rejects_cross_session_or_missing_history(self):
        session = {"mode": "human", "scope": "session", "scope_id": "previous-session", "source": "explicit owner"}
        with self.assertRaises(InvalidWork):
            resolve_selection(session=session, session_id="current-session")
        with self.assertRaises(InvalidWork):
            resolve_selection(resumed=session, session_id="current-session")
        with self.assertRaises(InvalidWork):
            resolve_selection(resumed={"scope": "task"})

    def test_selection_rejects_scope_substitution_and_unknown_mode(self):
        choice = {"mode": "human", "scope": "project", "scope_id": "project-1", "source": "owner"}
        with self.assertRaises(InvalidWork):
            resolve_selection(task=choice)
        choice["mode"] = "unrecognized"
        with self.assertRaises(InvalidWork):
            resolve_selection(project=choice)

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
        self.profile = self.root.parent / (self.root.name + "-profile.json")
        self.addCleanup(lambda: self.profile.unlink(missing_ok=True))
        self.profile_patch = patch("execution_modes.PROFILE_PATH", self.profile)
        self.profile_patch.start()
        self.addCleanup(self.profile_patch.stop)

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], stderr=subprocess.DEVNULL, text=True).strip()

    def install(self):
        sources = {}
        for relative in sorted(WORKFLOW_SOURCES):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("synthetic source: " + relative)
            if relative.endswith("scripts/lib/execution-modes.py"):
                path.write_text("import argparse,json\np=argparse.ArgumentParser()\np.add_argument('--state')\na=p.parse_args()\nr=json.load(open(a.state))\nprint(json.dumps({'authority':'inspection-only','mode':r['execution']['mode']}))\n")
            sources[relative] = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "mode": "100644"}
        self.git("init")
        self.git("add", ".systems")
        self.git("-c", "user.name=Synthetic Test", "-c", "user.email=test@example.invalid", "commit", "-m", "synthetic baseline")
        self.record = {"contract": 1, "tested_commit": self.git("rev-parse", "HEAD"),
                       "inspector": ".systems/scripts/lib/execution-modes.py", "sources": sources,
                       "mode_mapping": {"auto": "auto", "human": "human-coop"},
                       "delivery_mapping": {"auto-unconstrained": "auto-unbounded"}}
        self.save()

    def save(self):
        self.profile.write_text(json.dumps(self.record))

    def test_tested_tree_cannot_be_restamped_to_new_live_sources(self):
        self.install()
        relative='.systems/ai/core/autopilot.md';p=self.root/relative;p.write_text('new committed contract')
        self.git('add',relative);self.git('-c','user.name=Synthetic Test','-c','user.email=test@example.invalid','commit','-m','synthetic changed source')
        self.record['sources'][relative]['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();self.save()
        self.assertEqual(workflow_support(self.root)['status'],'invalid')

    def test_missing_tested_commit_and_tested_mode_rejected(self):
        self.install();self.record['tested_commit']='0'*40;self.save()
        self.assertEqual(workflow_support(self.root)['status'],'invalid')
        self.record['tested_commit']=self.git('rev-parse','HEAD')
        relative='.systems/ai/core/autopilot.md';p=self.root/relative;p.chmod(0o755)
        self.git('add',relative);self.git('-c','user.name=Synthetic Test','-c','user.email=test@example.invalid','commit','-m','synthetic mode drift')
        self.record['sources'][relative]['mode']='100755';self.save()
        self.assertEqual(workflow_support(self.root)['status'],'invalid')

    def test_old_workflow_falls_back(self):
        self.install()
        path = self.root / ".systems/ai/core/execution-modes.md"
        path.write_text("unknown historical contract")
        self.git("add", ".")
        self.git("-c", "user.name=Synthetic Test", "-c", "user.email=test@example.invalid", "commit", "-m", "unknown contract")
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

    def test_unrelated_committed_change_keeps_exact_source_support(self):
        self.install()
        (self.root / "notes.md").write_text("unrelated")
        self.git("add", "notes.md")
        self.git("-c", "user.name=Synthetic Test", "-c", "user.email=test@example.invalid", "commit", "-m", "unrelated")
        self.assertEqual(workflow_support(self.root)["status"], "source-bound")

    def test_changed_index_and_modes_fail(self):
        self.install()
        path = self.root / ".systems/ai/core/autopilot.md"
        path.chmod(0o755)
        self.assertEqual(workflow_support(self.root)["status"], "invalid")
        path.chmod(0o644)
        path.write_text("index change")
        self.git("add", ".")
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
        del self.record["delivery_mapping"]
        self.save()
        self.assertEqual(workflow_support(self.root)["status"], "invalid")
        self.record["delivery_mapping"] = {"auto-unconstrained": "auto-unbounded"}
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
        self.profile.write_text('{"contract":1,"contract":1}')
        self.assertEqual(workflow_support(self.root)["status"], "invalid")

    def test_missing_or_linked_root_and_source_directory_fail(self):
        self.assertEqual(workflow_support(self.root / "missing")["status"], "invalid")
        self.install()
        directory = self.root / ".systems/ai/core"
        moved = self.root / "moved"
        directory.rename(moved)
        directory.symlink_to(moved, target_is_directory=True)
        self.assertEqual(workflow_support(self.root)["status"], "invalid")

    def test_original_workflow_state_preserves_scope_and_never_changes_input(self):
        self.install()
        state = self.root / "projection.json"
        value = {"execution": {"mode": "human-coop", "scope": "project", "scope_id": "example-project", "source": "owner project decision"}}
        state.write_text(json.dumps(value))
        before = state.read_bytes()
        result = inspect_workflow_state(self.root, state)
        self.assertEqual(result["selection"], {**value["execution"], "mode": "human"})
        self.assertEqual(state.read_bytes(), before)
        self.assertEqual(result["workflow_readiness"]["authority"], "inspection-only")

    def test_original_workflow_state_requires_recognized_sources(self):
        self.install()
        state = self.root / "projection.json"
        state.write_text("{}")
        (self.root / ".systems/ai/core/autopilot.md").write_text("uncommitted")
        with self.assertRaises(InvalidWork):
            inspect_workflow_state(self.root, state)

    def test_input_linked_parent_fails(self):
        directory = self.root / "actual"
        directory.mkdir()
        (directory / "input.json").write_text("{}")
        (self.root / "alias").symlink_to(directory, target_is_directory=True)
        with self.assertRaises(InvalidWork):
            read_json(self.root / "alias/input.json")

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
