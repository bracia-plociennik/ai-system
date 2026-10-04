"""Synthetic behavioral regressions for the pure parallel orchestration model."""

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import parallel_orchestration as orchestration


BASELINE = {"commit": "a" * 40, "source_digest": "b" * 64}
NEW_BASELINE = {"commit": "c" * 40, "source_digest": "d" * 64}
CHECKS = ["intent", "diff", "tests", "privacy"]
NO_EVENT = object()


def unit(uid="first", **changes):
    value = {
        "id": uid,
        "goal": "Implement synthetic " + uid,
        "dod": "Synthetic regression evidence reviewed",
        "dependencies": [],
        "mode": "implementation",
        "system": "ai-system",
        "write_paths": ["src/" + uid + ".py"],
        "resources": [],
        "worktree": "/private/tmp/synthetic-ppo-" + uid,
        "status": "pending",
        "attempt_id": None,
        "agent_id": None,
        "termination_confirmed": True,
        "result": None,
    }
    value.update(changes)
    return value


def plan(*units, **changes):
    value = {
        "contract": 1,
        "run_id": "synthetic-run",
        "coordinator_id": "synthetic-coordinator",
        "approval_ref": "owner-approved synthetic test scope",
        "baseline": copy.deepcopy(BASELINE),
        "runtime_capacity": 2,
        "checkpoint_open": True,
        "units": list(units) if units else [unit()],
    }
    value.update(changes)
    return value


def event(current, action, uid="first", **changes):
    value = {"action": action, "baseline": copy.deepcopy(current["baseline"])}
    if uid is not None:
        target = next(item for item in current["units"] if item["id"] == uid)
        value.update(unit_id=uid, attempt_id=target["attempt_id"])
    value.update(changes)
    return value


def result(current, uid="first", **changes):
    target = next(item for item in current["units"] if item["id"] == uid)
    value = {
        "baseline": copy.deepcopy(current["baseline"]),
        "attempt_id": target["attempt_id"],
        "evidence": [{"path": target["write_paths"][0], "sha256": "e" * 64}],
        "test_summary": "Synthetic focused checks completed",
        "findings": [],
    }
    value.update(changes)
    return value


class OrchestrationTestCase(unittest.TestCase):
    def reject_plan(self, current, repo=None):
        before = copy.deepcopy(current)
        with self.assertRaises(orchestration.InvalidPlan):
            orchestration.validate_plan(current, repo=repo)
        self.assertEqual(current, before, "Rejected validation mutated its input")

    def reject_event(self, current, incoming):
        before, event_before = copy.deepcopy(current), copy.deepcopy(incoming)
        with self.assertRaises(orchestration.InvalidPlan):
            orchestration.transition(current, incoming)
        self.assertEqual(current, before, "Rejected transition mutated the plan")
        self.assertEqual(incoming, event_before, "Rejected transition mutated the event")

    def advance(self, current, incoming):
        before, event_before = copy.deepcopy(current), copy.deepcopy(incoming)
        updated = orchestration.transition(current, incoming)
        self.assertEqual(current, before, "Transition mutated its input plan")
        self.assertEqual(incoming, event_before, "Transition mutated its input event")
        self.assertIsNot(updated, current)
        self.assertEqual(orchestration.validate_plan(updated), updated)
        return updated

    def start(self, current=None, uid="first", **changes):
        current = plan() if current is None else current
        fields = {"agent_id": "worker-" + uid, "attempt_id": "attempt-" + uid}
        fields.update(changes)
        return self.advance(current, event(current, "start", uid, **fields))

    def submit(self, current, uid="first", **changes):
        return self.advance(current, event(current, "submit", uid,
                                          result=result(current, uid, **changes)))

    def accept(self, current, uid="first"):
        return self.advance(current, event(current, "accept", uid,
                                          verified_by=current["coordinator_id"],
                                          verified_checks=list(CHECKS)))

    def terminate(self, current, uid="first"):
        return self.advance(current, event(current, "terminated", uid,
                                          worker_stopped=True))


class PlanValidationTests(OrchestrationTestCase):
    def test_protected_path_case_aliases_are_rejected(self):
        for value in (".GIT/config", "AI-WORKFLOW/core.md", "Capture-State/a.md", "Secrets/a", ".ENV.production"):
            with self.subTest(value=value):
                self.reject_plan(plan(unit(write_paths=[value])))

    def test_error_is_value_error(self):
        self.assertTrue(issubclass(orchestration.InvalidPlan, ValueError))

    def test_validation_returns_deep_copy(self):
        current = plan(unit(dependencies=[], resources=["synthetic-api"]))
        original = copy.deepcopy(current)
        validated = orchestration.validate_plan(current)
        self.assertEqual(validated, original)
        validated["baseline"]["commit"] = "f" * 40
        validated["units"][0]["resources"].append("another-resource")
        self.assertEqual(current, original)

    def test_all_top_level_fields_are_required(self):
        for field in plan():
            current = plan()
            del current[field]
            with self.subTest(field=field):
                self.reject_plan(current)

    def test_all_unit_fields_are_required(self):
        for field in unit():
            current = plan()
            del current["units"][0][field]
            with self.subTest(field=field):
                self.reject_plan(current)

    def test_invalid_top_level_types_and_values(self):
        cases = {
            "contract": [True, 0, 2, "1", None],
            "run_id": [None, "", "  ", 3],
            "coordinator_id": [None, "", "  ", []],
            "approval_ref": [None, "", "  ", False],
            "runtime_capacity": [True, False, 0, -1, 1.5, "2", None],
            "checkpoint_open": [None, 0, 1, "false"],
            "units": [None, {}, "first"],
        }
        for field, values in cases.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    self.reject_plan(plan(**{field: value}))

    def test_baseline_requires_both_strict_hex_identities(self):
        for value in (None, [], {}, {"commit": "a" * 40},
                      {"source_digest": "b" * 64}):
            with self.subTest(value=value):
                self.reject_plan(plan(baseline=value))
        for field, length in (("commit", 40), ("source_digest", 64)):
            for value in (None, True, "", "a" * (length - 1),
                          "a" * (length + 1), "g" * length):
                baseline = copy.deepcopy(BASELINE)
                baseline[field] = value
                with self.subTest(field=field, value=value):
                    self.reject_plan(plan(baseline=baseline))

    def test_invalid_unit_types_and_values(self):
        cases = {
            "id": [None, "", "  ", 7],
            "goal": [None, "", "  ", False],
            "dod": [None, "", "  ", []],
            "dependencies": [None, "other", {}, [None], [3]],
            "mode": [None, [], {}, "write", "read_only"],
            "system": [None, [], {}, "unknown", "AI-System"],
            "write_paths": [None, "src/first.py", {}, [None], [7]],
            "resources": [None, "api", {}, [None], [""], ["  "]],
            "worktree": [False, 7, "relative/worktree"],
            "status": [None, [], {}, "complete", "RUNNING"],
            "attempt_id": [False, "", "  ", 7],
            "agent_id": [False, "", "  ", []],
            "termination_confirmed": [None, 0, 1, "true"],
            "result": [False, 7, [], "done"],
        }
        for field, values in cases.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    self.reject_plan(plan(unit(**{field: value})))

    def test_unit_ids_and_graph_edges_are_unambiguous(self):
        cases = [
            plan(unit(), unit()),
            plan(unit(dependencies=["missing"])),
            plan(unit(dependencies=["first"])),
            plan(unit(dependencies=["second", "second"]), unit("second")),
            plan(unit(dependencies=["second"]), unit("second", dependencies=["first"])),
            plan(unit(dependencies=["second"]), unit("second", dependencies=["third"]),
                 unit("third", dependencies=["first"])),
        ]
        for index, current in enumerate(cases):
            with self.subTest(case=index):
                self.reject_plan(current)

    def test_read_only_cannot_claim_write_paths(self):
        self.reject_plan(plan(unit(mode="read-only")))
        current = plan(unit(mode="read-only", write_paths=[], worktree=None))
        self.assertEqual(orchestration.validate_plan(current), current)

    def test_paths_must_be_normalized_repo_relative(self):
        for path in ("", "/etc/passwd", "../outside", "src/../../outside",
                     "./src/first.py", "src//first.py", "src/./first.py",
                     "src/../first.py", "src/", "src\\first.py", ".", ".."):
            with self.subTest(path=path):
                self.reject_plan(plan(unit(write_paths=[path])))

    def test_control_characters_cannot_hide_write_paths(self):
        for path in ("src/first\n.py", "src/first\r.py", "src/first\t.py", "src/first\x00.py"):
            with self.subTest(path=repr(path)):
                self.reject_plan(plan(unit(write_paths=[path])))

    def test_nonexistent_normalized_write_target_is_allowed(self):
        with tempfile.TemporaryDirectory(prefix="ppo-paths-") as directory:
            current = plan(unit(write_paths=["future/subdirectory/new.py"]))
            self.assertEqual(orchestration.validate_plan(current, repo=Path(directory)), current)

    def test_symlink_write_target_and_ancestor_cannot_escape_repo(self):
        with tempfile.TemporaryDirectory(prefix="ppo-links-") as directory:
            root = Path(directory)
            repo, outside = root / "repo", root / "outside"
            repo.mkdir()
            outside.mkdir()
            (outside / "existing.py").write_text("synthetic fixture", encoding="utf-8")
            (repo / "linked-dir").symlink_to(outside, target_is_directory=True)
            (repo / "linked.py").symlink_to(outside / "existing.py")
            (repo / "broken.py").symlink_to(outside / "not-created.py")
            for path in ("linked-dir/existing.py", "linked-dir/new.py",
                         "linked.py", "broken.py"):
                with self.subTest(path=path):
                    self.reject_plan(plan(unit(write_paths=[path])), repo=repo)

    def test_live_worker_requires_attempt_and_agent(self):
        for field in ("attempt_id", "agent_id"):
            changes = {"status": "running", "attempt_id": "attempt-first",
                       "agent_id": "worker-first", "termination_confirmed": False}
            changes[field] = None
            with self.subTest(field=field):
                self.reject_plan(plan(unit(**changes)))

    def test_live_workers_cannot_exceed_capacity(self):
        current = self.start(plan(unit(), unit("second")))
        current = self.start(current, "second")
        current["runtime_capacity"] = 1
        self.reject_plan(current)

    def test_imported_live_snapshots_cannot_bypass_dependency_acceptance(self):
        current = plan(unit(), unit("second", dependencies=["first"], status="running",
                                   agent_id="worker-second", attempt_id="attempt-second",
                                   termination_confirmed=False))
        self.reject_plan(current)

    def test_imported_live_snapshots_cannot_bypass_resource_or_write_conflicts(self):
        for dimension in ("resources", "write_paths", "worktree"):
            first = unit(status="running", agent_id="worker-first", attempt_id="attempt-first",
                         termination_confirmed=False)
            second = unit("second", status="running", agent_id="worker-second",
                          attempt_id="attempt-second", termination_confirmed=False)
            if dimension == "resources":
                first[dimension] = second[dimension] = ["shared-api"]
            elif dimension == "write_paths":
                first[dimension], second[dimension] = ["src"], ["src/second.py"]
            else:
                second[dimension] = first[dimension]
            with self.subTest(dimension=dimension):
                self.reject_plan(plan(first, second))

    def test_retired_identity_histories_are_typed_and_unique(self):
        for field in ("retired_attempt_ids", "retired_agent_ids"):
            current = plan(**{field: ["old-id"]})
            self.assertEqual(orchestration.validate_plan(current), current)
            for value in (None, "old-id", [None], [""], ["  "], ["old-id", "old-id"]):
                with self.subTest(field=field, value=value):
                    self.reject_plan(plan(**{field: value}))

    def test_unstarted_states_have_no_current_worker_identity_or_result(self):
        for status in ("pending", "ready", "blocked"):
            for field, value in (("agent_id", "worker-first"),
                                 ("attempt_id", "attempt-first"), ("result", {})):
                changes = {"status": status, "termination_confirmed": True, field: value}
                with self.subTest(status=status, field=field):
                    self.reject_plan(plan(unit(**changes)))


class SchedulingTests(OrchestrationTestCase):
    def test_write_set_case_and_unicode_aliases_serialize_conservatively(self):
        for left, right in (("src/file.py", "SRC/FILE.PY"), ("src/common", "SRC/Common/file.py"),
                            ("src/caf\u00e9", "SRC/CAFE\u0301/file.py")):
            with self.subTest(left=left, right=right):
                current = plan(unit(write_paths=[left]), unit("second", write_paths=[right]))
                self.assertEqual(orchestration.dispatchable_units(current), ["first"])

    def test_filesystem_identity_serializes_distinct_worktree_spellings(self):
        with tempfile.TemporaryDirectory(prefix="ppo-identity-") as directory:
            root = Path(directory).resolve()
            left, right = root / "left", root / "right"
            left.mkdir()
            right.mkdir()
            current = plan(unit(worktree=str(left)), unit("second", worktree=str(right)))
            with mock.patch.object(Path, "samefile", return_value=True):
                self.assertEqual(orchestration.dispatchable_units(current), ["first"])
            with mock.patch.object(Path, "samefile", side_effect=OSError("identity unavailable")):
                with self.assertRaises(orchestration.InvalidPlan):
                    orchestration.dispatchable_units(current)

    def test_case_alias_on_case_insensitive_filesystem_is_not_isolation(self):
        with tempfile.TemporaryDirectory(prefix="ppo-case-") as directory:
            tree = Path(directory).resolve()
            alias = Path(str(tree).upper())
            if not alias.exists() or not tree.samefile(alias):
                self.skipTest("filesystem is case-sensitive")
            current = plan(unit(worktree=str(tree)), unit("second", worktree=str(alias)))
            self.assertEqual(orchestration.dispatchable_units(current), ["first"])

    def test_imported_live_snapshot_cannot_bypass_workflow_fallback(self):
        current = self.start(plan(unit(system="ai-workflow"), unit("second")))
        bad = copy.deepcopy(current)
        bad["units"][1].update(status="running", agent_id="worker-second", attempt_id="attempt-second", termination_confirmed=False)
        self.reject_plan(bad)
        good = copy.deepcopy(bad)
        good["workflow_parallel_supported"] = True
        self.assertEqual(orchestration.validate_plan(good), good)

    def test_worktree_aliases_cannot_create_false_isolation(self):
        with tempfile.TemporaryDirectory(prefix="ppo-tree-") as directory:
            root = Path(directory).resolve()
            real = root / "real"
            real.mkdir()
            alias = root / "alias"
            alias.symlink_to(real, target_is_directory=True)
            current = plan(unit(worktree=str(real)), unit("second", worktree=str(alias)))
            self.assertEqual(orchestration.dispatchable_units(current), ["first"])

    def test_worktree_paths_must_not_hide_dot_or_control_components(self):
        for value in ("/private/tmp/./tree", "/private/tmp//tree", "/private/tmp/tree\nother"):
            with self.subTest(value=value):
                self.reject_plan(plan(unit(worktree=value)))

    def test_dependencies_require_acceptance_not_submission(self):
        current = plan(unit(), unit("second", dependencies=["first"]))
        self.assertEqual(orchestration.ready_units(current), ["first"])
        current = self.submit(self.start(current))
        self.assertNotIn("second", orchestration.ready_units(current))
        current = self.accept(current)
        self.assertEqual(orchestration.ready_units(current), ["second"])

    def test_unmet_dependency_blocks_start_even_with_spare_capacity(self):
        current = plan(unit(), unit("second", dependencies=["first"]))
        self.reject_event(current, event(current, "start", "second",
                                         agent_id="worker-second", attempt_id="attempt-second"))

    def test_statuses_that_are_not_candidates_do_not_become_ready(self):
        current = plan(unit(status="blocked"), unit("second"), unit("third"))
        current = self.start(current, "second")
        current = self.terminate(self.advance(current, event(current, "cancel", "second")), "second")
        current = self.start(current, "third")
        current = self.terminate(self.advance(current, event(current, "fail", "third")), "third")
        self.assertEqual(orchestration.ready_units(current), [])
        self.assertEqual(orchestration.dispatchable_units(current), [])

    def test_ready_and_pending_candidates_are_selected_without_mutation(self):
        current = plan(unit(status="ready"), unit("second"), unit("third"))
        before = copy.deepcopy(current)
        self.assertEqual(orchestration.ready_units(current), ["first", "second", "third"])
        self.assertEqual(orchestration.dispatchable_units(current), ["first", "second"])
        self.assertEqual(current, before)

    def test_capacity_has_no_hard_coded_three_worker_limit(self):
        current = plan(*(unit("unit-" + str(index)) for index in range(6)),
                       runtime_capacity=5)
        self.assertEqual(len(orchestration.dispatchable_units(current)), 5)
        for index in range(5):
            current = self.start(current, "unit-" + str(index))
        self.assertEqual(orchestration.dispatchable_units(current), [])

    def test_capacity_counts_running_submitted_and_accepted_unterminated(self):
        current = self.start(plan(unit(), unit("second"), runtime_capacity=1))
        for phase in ("running", "submitted", "accepted"):
            with self.subTest(phase=phase):
                self.assertEqual(orchestration.dispatchable_units(current), [])
                self.reject_event(current, event(current, "start", "second",
                                                 agent_id="worker-second", attempt_id="attempt-second"))
            if phase == "running":
                current = self.submit(current)
            elif phase == "submitted":
                current = self.accept(current)
        current = self.terminate(current)
        self.assertEqual(orchestration.dispatchable_units(current), ["second"])

    def test_shared_resource_serializes_candidates(self):
        current = plan(unit(resources=["shared-api"]),
                       unit("second", resources=["shared-api"]), unit("third"),
                       runtime_capacity=3)
        self.assertEqual(orchestration.dispatchable_units(current), ["first", "third"])
        current = self.start(current)
        self.assertEqual(orchestration.dispatchable_units(current), ["third"])

    def test_parent_child_path_overlap_serializes_but_prefix_is_not_overlap(self):
        for left, right in (("src", "src/nested/file.py"),
                            ("src/nested/file.py", "src"),
                            ("src/common.py", "src/common.py")):
            current = plan(unit(write_paths=[left]), unit("second", write_paths=[right]),
                           unit("third", write_paths=["src-other/file.py"]),
                           runtime_capacity=3)
            with self.subTest(left=left, right=right):
                self.assertEqual(orchestration.dispatchable_units(current), ["first", "third"])
                current = self.start(current)
                self.assertEqual(orchestration.dispatchable_units(current), ["third"])
                self.reject_event(current, event(current, "start", "second",
                                                 agent_id="worker-second", attempt_id="attempt-second"))

    def test_missing_implementation_worktree_rejects_unresolved_write_target(self):
        self.reject_plan(plan(unit(worktree=None)))

    def test_shared_explicit_worktree_serializes_implementation(self):
        worktree = "/private/tmp/synthetic-ppo-first"
        current = plan(unit(worktree=worktree), unit("second", worktree=worktree))
        self.assertEqual(orchestration.dispatchable_units(current), ["first"])
        current = self.start(current)
        self.reject_event(current, event(current, "start", "second",
                                         agent_id="worker-second", attempt_id="attempt-second"))

    def test_read_only_units_can_share_checkout(self):
        current = plan(unit(mode="read-only", write_paths=[], worktree=None),
                       unit("second", mode="read-only", write_paths=[], worktree=None))
        self.assertEqual(orchestration.dispatchable_units(current), ["first", "second"])
        current = self.start(current)
        current = self.start(current, "second")
        self.assertEqual([item["status"] for item in current["units"]], ["running", "running"])

    def test_checkpoint_boundary_stops_dispatch_and_start(self):
        current = plan(checkpoint_open=False)
        self.assertEqual(orchestration.dispatchable_units(current), [])
        self.reject_event(current, event(current, "start", agent_id="worker-first",
                                         attempt_id="attempt-first"))

    def test_failed_and_cancel_requested_workers_keep_resources_until_terminated(self):
        for action in ("fail", "cancel"):
            current = self.start(plan(unit(resources=["api"]),
                                      unit("second", resources=["api"])))
            current = self.advance(current, event(current, action))
            with self.subTest(action=action):
                self.assertFalse(current["units"][0]["termination_confirmed"])
                self.assertEqual(orchestration.dispatchable_units(current), [])
                self.reject_event(current, event(current, "start", "second",
                                                 agent_id="worker-second", attempt_id="attempt-second"))
                current = self.terminate(current)
                self.assertEqual(orchestration.dispatchable_units(current), ["second"])

    def test_dispatch_count_is_optional_and_limits_orchestrator_selected_batch(self):
        current = plan(*(unit("unit-" + str(index)) for index in range(6)),
                       runtime_capacity=6)
        self.assertEqual(len(orchestration.dispatchable_units(current)), 6)
        current["dispatch_count"] = 4
        self.assertEqual(orchestration.dispatchable_units(current),
                         ["unit-0", "unit-1", "unit-2", "unit-3"])
        current["dispatch_count"] = 1
        self.assertEqual(orchestration.dispatchable_units(current), ["unit-0"])
        for value in (True, False, 0, -1, 1.5, "2", 7):
            with self.subTest(dispatch_count=value):
                self.reject_plan({**current, "dispatch_count": value})

    def test_dispatch_count_respects_occupied_slots(self):
        current = plan(unit(), unit("second"), unit("third"),
                       runtime_capacity=2, dispatch_count=2)
        current = self.start(current)
        self.assertEqual(orchestration.dispatchable_units(current), ["second"])

    def test_workflow_parallelism_requires_explicit_support(self):
        current = plan(unit(system="ai-workflow"), unit("second", system="ai-workflow"))
        self.assertEqual(orchestration.dispatchable_units(current), ["first"])
        unsupported = self.start(current)
        self.assertEqual(orchestration.dispatchable_units(unsupported), [])
        self.reject_event(unsupported, event(unsupported, "start", "second",
                                             agent_id="worker-second", attempt_id="attempt-second"))
        current["workflow_parallel_supported"] = True
        self.assertEqual(orchestration.dispatchable_units(current), ["first", "second"])
        supported = self.start(current)
        supported = self.start(supported, "second")
        self.assertEqual([u["status"] for u in supported["units"]], ["running", "running"])

    def test_workflow_support_is_strict_boolean_and_false_keeps_fallback(self):
        current = plan(unit(system="ai-workflow"), unit("second", system="ai-workflow"),
                       workflow_parallel_supported=False)
        self.assertEqual(orchestration.dispatchable_units(current), ["first"])
        for value in (None, 0, 1, "true", []):
            with self.subTest(value=value):
                self.reject_plan({**current, "workflow_parallel_supported": value})


class TransitionTests(OrchestrationTestCase):
    def test_happy_path_preserves_baseline_and_releases_only_on_termination(self):
        current = plan()
        started = self.start(current)
        target = started["units"][0]
        self.assertEqual(target["status"], "running")
        self.assertEqual(target["attempt_id"], "attempt-first")
        self.assertEqual(target["agent_id"], "worker-first")
        self.assertFalse(target["termination_confirmed"])
        submitted = self.submit(started)
        self.assertEqual(submitted["units"][0]["status"], "submitted")
        accepted = self.accept(submitted)
        self.assertEqual(accepted["units"][0]["status"], "accepted")
        self.assertFalse(accepted["units"][0]["termination_confirmed"])
        stopped = self.terminate(accepted)
        self.assertTrue(stopped["units"][0]["termination_confirmed"])
        self.assertEqual(stopped["units"][0]["status"], "accepted")
        for updated in (started, submitted, accepted, stopped):
            self.assertEqual(updated["baseline"], BASELINE)

    def test_successful_transition_deep_copies_plan_and_result_event(self):
        current = self.start()
        incoming = event(current, "submit", result=result(current))
        before, event_before = copy.deepcopy(current), copy.deepcopy(incoming)
        submitted = self.advance(current, incoming)
        submitted["baseline"]["commit"] = "f" * 40
        submitted["units"][0]["write_paths"].append("another.py")
        submitted["units"][0]["result"]["evidence"][0]["sha256"] = "0" * 64
        self.assertEqual(current, before)
        self.assertEqual(incoming, event_before)

    def test_unknown_action_and_unit_are_rejected(self):
        current = plan()
        self.reject_event(current, event(current, "spawn-recursive-agent"))
        incoming = event(current, "start", agent_id="worker-first", attempt_id="attempt-first")
        incoming["unit_id"] = "missing"
        self.reject_event(current, incoming)

    def test_every_unit_event_requires_matching_baseline(self):
        pending, running = plan(), self.start()
        submitted = self.submit(running)
        failed = self.terminate(self.advance(running, event(running, "fail")))
        cases = [
            (pending, event(pending, "start", agent_id="worker-first", attempt_id="attempt-first")),
            (running, event(running, "submit", result=result(running))),
            (submitted, event(submitted, "accept", verified_by=submitted["coordinator_id"],
                              verified_checks=list(CHECKS))),
            (running, event(running, "fail")),
            (running, event(running, "cancel")),
            (running, event(running, "terminated", worker_stopped=True)),
            (failed, event(failed, "retry")),
        ]
        for current, incoming in cases:
            for mutation in ("missing", "commit", "source_digest"):
                stale = copy.deepcopy(incoming)
                if mutation == "missing":
                    del stale["baseline"]
                else:
                    stale["baseline"][mutation] = NEW_BASELINE[mutation]
                with self.subTest(action=incoming["action"], mutation=mutation):
                    self.reject_event(current, stale)

    def test_every_attempt_scoped_event_rejects_stale_or_missing_attempt(self):
        running = self.start()
        submitted = self.submit(running)
        failed = self.terminate(self.advance(running, event(running, "fail")))
        cases = [
            (running, event(running, "submit", result=result(running))),
            (submitted, event(submitted, "accept", verified_by=submitted["coordinator_id"],
                              verified_checks=list(CHECKS))),
            (running, event(running, "fail")),
            (running, event(running, "cancel")),
            (running, event(running, "terminated", worker_stopped=True)),
            (failed, event(failed, "retry")),
        ]
        for current, incoming in cases:
            for value in (None, "obsolete-attempt", "missing"):
                stale = copy.deepcopy(incoming)
                if value == "missing":
                    del stale["attempt_id"]
                else:
                    stale["attempt_id"] = value
                with self.subTest(action=incoming["action"], value=value):
                    self.reject_event(current, stale)

    def test_start_requires_unique_nonempty_attempt_and_agent(self):
        for field in ("attempt_id", "agent_id"):
            for value in (None, "", "  ", True):
                current = plan()
                fields = {"agent_id": "worker-first", "attempt_id": "attempt-first"}
                fields[field] = value
                with self.subTest(field=field, value=value):
                    self.reject_event(current, event(current, "start", **fields))
        current = self.start(plan(unit(), unit("second")))
        for fields in ({"agent_id": "worker-first", "attempt_id": "attempt-second"},
                       {"agent_id": "worker-second", "attempt_id": "attempt-first"}):
            with self.subTest(fields=fields):
                self.reject_event(current, event(current, "start", "second", **fields))

    def test_cannot_start_running_submitted_or_accepted_unit_again(self):
        running = self.start()
        submitted = self.submit(running)
        accepted = self.accept(submitted)
        for current in (running, submitted, accepted, self.terminate(accepted)):
            with self.subTest(status=current["units"][0]["status"]):
                self.reject_event(current, event(current, "start", agent_id="new-worker",
                                                 attempt_id="new-attempt"))

    def test_submission_requires_all_result_fields(self):
        current = self.start()
        for field in result(current):
            bad = result(current)
            del bad[field]
            with self.subTest(field=field):
                self.reject_event(current, event(current, "submit", result=bad))

    def test_submission_identity_must_match_run_and_attempt(self):
        current = self.start()
        for bad in (result(current, baseline=NEW_BASELINE),
                    result(current, attempt_id="obsolete-attempt")):
            with self.subTest(result=bad):
                self.reject_event(current, event(current, "submit", result=bad))

    def test_submission_rejects_malformed_evidence_and_summary(self):
        current = self.start()
        cases = [
            {"evidence": None}, {"evidence": "src/first.py"},
            {"evidence": [{}]}, {"evidence": [{"path": "src/first.py"}]},
            {"evidence": [{"path": "../private.md", "sha256": "e" * 64}]},
            {"evidence": [{"path": "/private/source.md", "sha256": "e" * 64}]},
            {"evidence": [{"path": "src/first.py", "sha256": "not-a-digest"}]},
            {"test_summary": None}, {"test_summary": ""},
            {"test_summary": "  "}, {"findings": None}, {"findings": "none"},
        ]
        for changes in cases:
            with self.subTest(changes=changes):
                self.reject_event(current, event(current, "submit", result=result(current, **changes)))

    def test_late_submission_after_failure_or_cancellation_is_rejected(self):
        running = self.start()
        receipt = event(running, "submit", result=result(running))
        for action in ("fail", "cancel"):
            current = self.advance(running, event(running, action))
            with self.subTest(action=action, terminated=False):
                self.reject_event(current, receipt)
            stopped = self.terminate(current)
            with self.subTest(action=action, terminated=True):
                self.reject_event(stopped, receipt)

    def test_pending_or_duplicate_submission_is_rejected(self):
        pending = plan()
        running = self.start(pending)
        incoming = event(running, "submit", result=result(running))
        self.reject_event(pending, incoming)
        self.reject_event(self.submit(running), incoming)

    def test_accept_requires_coordinator_and_every_semantic_check(self):
        current = self.submit(self.start())
        for verified_by in (None, "worker-first", "another-coordinator", ""):
            with self.subTest(verified_by=verified_by):
                self.reject_event(current, event(current, "accept", verified_by=verified_by,
                                                 verified_checks=list(CHECKS)))
        for missing in CHECKS:
            with self.subTest(missing=missing):
                self.reject_event(current, event(current, "accept",
                                                 verified_by=current["coordinator_id"],
                                                 verified_checks=[c for c in CHECKS if c != missing]))
        for checks in (None, "intent diff tests privacy", [], [True]):
            with self.subTest(checks=checks):
                self.reject_event(current, event(current, "accept",
                                                 verified_by=current["coordinator_id"],
                                                 verified_checks=checks))

    def test_accept_requires_submission_and_cannot_accept_twice(self):
        pending = plan()
        running = self.start(pending)
        accepted = self.accept(self.submit(running))
        for current in (pending, running, accepted):
            with self.subTest(status=current["units"][0]["status"]):
                self.reject_event(current, event(current, "accept",
                                                 verified_by=current["coordinator_id"],
                                                 verified_checks=list(CHECKS)))

    def test_rejected_findings_prevent_acceptance(self):
        current = self.submit(self.start(), findings=[
            {"severity": "P1", "status": "rejected", "message": "Synthetic DoD not met"}
        ])
        self.reject_event(current, event(current, "accept",
                                         verified_by=current["coordinator_id"],
                                         verified_checks=list(CHECKS)))

    def test_termination_requires_explicit_true_worker_stopped_confirmation(self):
        current = self.start()
        for value in (False, None, 1, "true"):
            with self.subTest(worker_stopped=value):
                self.reject_event(current, event(current, "terminated", worker_stopped=value))
        self.reject_event(current, event(current, "terminated"))

    def test_cancel_is_request_then_confirmed_cancelled(self):
        current = self.start()
        cancelled = self.advance(current, event(current, "cancel"))
        self.assertEqual(cancelled["units"][0]["status"], "cancel-requested")
        stopped = self.terminate(cancelled)
        self.assertEqual(stopped["units"][0]["status"], "cancelled")
        self.assertTrue(stopped["units"][0]["termination_confirmed"])

    def test_retry_only_after_failed_or_cancelled_and_confirmed_termination(self):
        running = self.start()
        for action in ("fail", "cancel"):
            current = self.advance(running, event(running, action))
            with self.subTest(action=action, terminated=False):
                self.reject_event(current, event(current, "retry"))
            current = self.terminate(current)
            retried = self.advance(current, event(current, "retry"))
            with self.subTest(action=action, terminated=True):
                self.assertIn(retried["units"][0]["status"], ("pending", "ready"))
                self.assertIsNone(retried["units"][0]["attempt_id"])
                self.assertIsNone(retried["units"][0]["agent_id"])
                self.assertIsNone(retried["units"][0]["result"])
                restarted = self.start(retried, attempt_id="second-attempt", agent_id="second-worker")
                self.reject_event(restarted, event(running, "submit", result=result(running)))
        for current in (plan(), running, self.submit(running),
                        self.terminate(self.accept(self.submit(running)))):
            with self.subTest(status=current["units"][0]["status"]):
                self.reject_event(current, event(current, "retry"))

    def test_retry_discards_failed_submitted_result(self):
        current = self.submit(self.start())
        current = self.advance(current, event(current, "fail"))
        current = self.terminate(current)
        retried = self.advance(current, event(current, "retry"))
        self.assertIsNone(retried["units"][0]["result"])

    def test_retry_rejects_retired_attempt_replay_but_accepts_new_attempt(self):
        original = self.start()
        current = self.terminate(self.advance(original, event(original, "fail")))
        current = self.advance(current, event(current, "retry"))
        self.assertIn("attempt-first", current["retired_attempt_ids"])
        self.reject_event(current, event(current, "start", agent_id="replacement-worker",
                                         attempt_id="attempt-first"))
        restarted = self.start(current, agent_id="replacement-worker", attempt_id="fresh-attempt")
        self.reject_event(restarted, event(original, "submit", result=result(original)))
        accepted = self.accept(self.submit(restarted))
        self.assertEqual(accepted["units"][0]["status"], "accepted")
        self.assertEqual(accepted["units"][0]["result"]["attempt_id"], "fresh-attempt")

    def test_retired_attempt_cannot_be_replayed_on_a_different_unit(self):
        current = self.start(plan(unit(), unit("second")))
        current = self.terminate(self.advance(current, event(current, "cancel")))
        current = self.advance(current, event(current, "retry"))
        self.reject_event(current, event(current, "start", "second",
                                         agent_id="worker-second", attempt_id="attempt-first"))

    def test_retry_rejects_retired_native_agent_with_fresh_attempt(self):
        current = self.start(plan(retired_agent_ids=["older-worker"],
                                  retired_attempt_ids=["older-attempt"]))
        current = self.terminate(self.advance(current, event(current, "fail")))
        current = self.advance(current, event(current, "retry"))
        self.assertEqual(current["retired_agent_ids"], ["older-worker", "worker-first"])
        self.assertEqual(current["retired_attempt_ids"], ["older-attempt", "attempt-first"])
        self.reject_event(current, event(current, "start", agent_id="worker-first",
                                         attempt_id="fresh-attempt"))
        restarted = self.start(current, agent_id="distinct-worker", attempt_id="distinct-attempt")
        accepted = self.accept(self.submit(restarted))
        self.assertEqual(accepted["units"][0]["status"], "accepted")
        self.assertEqual(accepted["units"][0]["agent_id"], "distinct-worker")
        self.assertEqual(accepted["units"][0]["attempt_id"], "distinct-attempt")


class RunWideTransitionTests(OrchestrationTestCase):
    def test_capacity_reassessment_can_increase_above_three_and_reduce_when_idle(self):
        current = plan(runtime_capacity=1)
        expanded = self.advance(current, event(current, "reassess-capacity", None,
                                               runtime_capacity=8))
        self.assertEqual(expanded["runtime_capacity"], 8)
        reduced = self.advance(expanded, event(expanded, "reassess-capacity", None,
                                               runtime_capacity=1))
        self.assertEqual(reduced["runtime_capacity"], 1)
        self.assertEqual(reduced["baseline"], BASELINE)

    def test_reassessment_rejects_invalid_or_below_occupied_capacity(self):
        current = self.start(plan(unit(), unit("second")))
        current = self.start(current, "second")
        current = self.accept(self.submit(current))
        for value in (True, False, 0, -1, 1.5, "3", None, 1):
            with self.subTest(value=value):
                self.reject_event(current, event(current, "reassess-capacity", None,
                                                 runtime_capacity=value))
        equal = self.advance(current, event(current, "reassess-capacity", None,
                                             runtime_capacity=2))
        self.assertEqual(equal["runtime_capacity"], 2)

    def test_run_wide_events_require_current_baseline(self):
        current = plan()
        for action, fields in (("reassess-capacity", {"runtime_capacity": 4}),
                               ("rebase", {"new_baseline": NEW_BASELINE})):
            for baseline in (None, NEW_BASELINE):
                with self.subTest(action=action, baseline=baseline):
                    self.reject_event(current, event(current, action, None,
                                                     baseline=baseline, **fields))

    def test_rebase_rejects_any_worker_without_termination(self):
        running = self.start()
        submitted = self.submit(running)
        states = [running, submitted, self.accept(submitted),
                  self.advance(running, event(running, "fail")),
                  self.advance(running, event(running, "cancel"))]
        for current in states:
            with self.subTest(status=current["units"][0]["status"]):
                self.reject_event(current, event(current, "rebase", None,
                                                 new_baseline=NEW_BASELINE))

    def test_rebase_invalidates_unaccepted_submission_and_ready_units(self):
        current = plan(unit(), unit("second", status="ready"),
                       unit("third", dependencies=["first"]))
        current = self.terminate(self.submit(self.start(current)))
        old_receipt = event(current, "accept", verified_by=current["coordinator_id"],
                            verified_checks=list(CHECKS))
        rebased = self.advance(current, event(current, "rebase", None,
                                               new_baseline=NEW_BASELINE))
        self.assertEqual(rebased["baseline"], NEW_BASELINE)
        self.assertEqual(rebased["units"][0]["status"], "pending")
        self.assertIsNone(rebased["units"][0]["result"])
        self.assertEqual(rebased["units"][1]["status"], "pending")
        self.assertNotIn("third", orchestration.ready_units(rebased))
        self.reject_event(rebased, old_receipt)
        self.assertEqual(current["baseline"], BASELINE)

    def test_rebase_rejects_accepted_results_and_preserves_old_run(self):
        current = self.terminate(self.accept(self.submit(self.start())))
        original = copy.deepcopy(current)
        self.reject_event(current, event(current, "rebase", None, new_baseline=NEW_BASELINE))
        self.assertEqual(current, original)
        self.assertEqual(current["units"][0]["status"], "accepted")
        self.assertEqual(current["units"][0]["result"]["baseline"], BASELINE)

    def test_rebase_new_baseline_must_be_complete_and_well_formed(self):
        current = plan()
        for baseline in (None, {}, {"commit": "c" * 40},
                         {"commit": "z" * 40, "source_digest": "d" * 64},
                         {"commit": "c" * 40, "source_digest": "short"}):
            with self.subTest(baseline=baseline):
                self.reject_event(current, event(current, "rebase", None,
                                                 new_baseline=baseline))

    def test_rebase_retires_old_attempt_even_with_new_baseline_event(self):
        current = self.terminate(self.submit(self.start()))
        rebased = self.advance(current, event(current, "rebase", None,
                                               new_baseline=NEW_BASELINE))
        self.assertIn("attempt-first", rebased["retired_attempt_ids"])
        self.assertIn("worker-first", rebased["retired_agent_ids"])
        self.reject_event(rebased, event(rebased, "start", agent_id="rebased-worker",
                                         attempt_id="attempt-first"))
        self.reject_event(rebased, event(rebased, "start", agent_id="worker-first",
                                         attempt_id="rebased-attempt"))
        restarted = self.start(rebased, agent_id="rebased-worker", attempt_id="rebased-attempt")
        accepted = self.accept(self.submit(restarted))
        self.assertEqual(accepted["units"][0]["result"]["baseline"], NEW_BASELINE)
        self.assertEqual(accepted["units"][0]["status"], "accepted")


class CliInspectionTests(OrchestrationTestCase):
    def test_cli_rejects_nonobject_event_instead_of_ignoring_it(self):
        for value in (None, [], False, "start"):
            with self.subTest(value=value):
                process = self.run_cli(plan(), incoming=value)
                self.assertNotEqual(process.returncode, 0)
                self.assertIn("event must be an object", process.stderr)

    def test_cli_rebase_uses_current_new_manifest_after_source_drift(self):
        repo, current, _ = self.repository_plan()
        current = self.terminate(self.advance(current, event(current, "fail")))
        old = copy.deepcopy(current)
        old["baseline"] = copy.deepcopy(BASELINE)
        old["source_manifest"][0]["sha256"] = "0" * 64
        incoming = event(old, "rebase", None, new_baseline=current["baseline"],
                         new_source_manifest=current["source_manifest"])
        process = self.run_cli(old, incoming, repo=repo)
        self.assertEqual(process.returncode, 0, process.stderr)
        updated = json.loads(process.stdout)["run"]
        self.assertEqual(updated["baseline"], current["baseline"])
        self.assertEqual(updated["source_manifest"], current["source_manifest"])
        self.assertEqual(updated["units"][0]["status"], "pending")
        self.assertIn("attempt-first", updated["retired_attempt_ids"])

    def test_cli_rebase_rejects_missing_stale_manifest_live_and_accepted_results(self):
        repo, live, _ = self.repository_plan()
        terminated = self.terminate(self.advance(live, event(live, "fail")))
        incoming = event(terminated, "rebase", None, new_baseline=terminated["baseline"],
                         new_source_manifest=terminated["source_manifest"])
        missing = copy.deepcopy(incoming)
        del missing["new_source_manifest"]
        self.assertNotEqual(self.run_cli(terminated, missing, repo=repo).returncode, 0)
        stale = copy.deepcopy(incoming)
        stale["new_source_manifest"][0]["sha256"] = "0" * 64
        self.assertNotEqual(self.run_cli(terminated, stale, repo=repo).returncode, 0)
        self.assertNotEqual(self.run_cli(live, incoming, repo=repo).returncode, 0)
        accepted = self.terminate(self.accept(self.submit(live)))
        self.assertNotEqual(self.run_cli(accepted, incoming, repo=repo).returncode, 0)

    def run_cli(self, current, incoming=NO_EVENT, repo=None):
        with tempfile.TemporaryDirectory(prefix="ppo-cli-") as directory:
            source = Path(directory) / "plan.json"
            source.write_text(json.dumps(current), encoding="utf-8")
            before = source.read_bytes()
            command = [sys.executable, "-B", str(SCRIPTS / "check-parallel-orchestration"),
                       "--plan", str(source)]
            if repo is not None:
                command.extend(["--repo", str(repo)])
            if incoming is not NO_EVENT:
                payload = Path(directory) / "event.json"
                payload.write_text(json.dumps(incoming), encoding="utf-8")
                event_before = payload.read_bytes()
                command.extend(["--event", str(payload)])
            process = subprocess.run(command, capture_output=True, text=True,
                                     env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                                     timeout=15, check=False)
            self.assertEqual(source.read_bytes(), before, "Inspection CLI rewrote the input plan")
            if incoming is not NO_EVENT:
                self.assertEqual(payload.read_bytes(), event_before, "Inspection CLI rewrote the event")
            return process

    def repository_plan(self):
        repo = SCRIPTS.parents[1]
        head = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
        path = ".systems/scripts/tests/test_parallel_orchestration.py"
        digest = hashlib.sha256((repo / path).read_bytes()).hexdigest()
        source_digest = hashlib.sha256((path + "=" + digest + "\n").encode()).hexdigest()
        current = self.start(plan(unit(write_paths=[path]),
                                  baseline={"commit": head, "source_digest": source_digest},
                                  source_manifest=[{"path": path, "sha256": digest}]))
        return repo, current, result(current, evidence=[{"path": path, "sha256": digest}])

    def test_cli_inspects_hypothetical_event_without_writing_or_claiming_pass(self):
        current = plan()
        process = self.run_cli(current, event(current, "start", agent_id="worker-first",
                                              attempt_id="attempt-first"))
        self.assertEqual(process.returncode, 0, process.stderr)
        output = json.loads(process.stdout)
        self.assertEqual(output["result"], "inspection-only")
        self.assertIs(output["supporting_only"], True)
        self.assertEqual(output["run"]["units"][0]["status"], "running")
        self.assertEqual(current["units"][0]["status"], "pending")

    def test_cli_repo_rejects_baseline_head_mismatch(self):
        repo = SCRIPTS.parents[1]
        head = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
        commit = "0" * 40 if head != "0" * 40 else "1" * 40
        process = self.run_cli(plan(baseline={"commit": commit, "source_digest": "b" * 64}), repo=repo)
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("HEAD", process.stderr)

    def test_cli_repo_accepts_existing_matching_receipt_evidence(self):
        repo, current, receipt = self.repository_plan()
        submitted = self.advance(current, event(current, "submit", result=receipt))
        process = self.run_cli(submitted, repo=repo)
        self.assertEqual(process.returncode, 0, process.stderr)

    def test_cli_repo_rejects_stale_evidence_already_in_plan(self):
        repo, current, receipt = self.repository_plan()
        receipt["evidence"][0]["sha256"] = "0" * 64
        submitted = self.advance(current, event(current, "submit", result=receipt))
        process = self.run_cli(submitted, repo=repo)
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("evidence", process.stderr.lower())

    def test_cli_repo_checks_newly_submitted_event_evidence_after_transition(self):
        repo, current, receipt = self.repository_plan()
        receipt["evidence"][0]["sha256"] = "0" * 64
        process = self.run_cli(current, event(current, "submit", result=receipt), repo=repo)
        self.assertNotEqual(process.returncode, 0, "CLI accepted stale evidence introduced by --event")
        self.assertIn("evidence", process.stderr.lower())

    def test_cli_repo_accepts_correctly_hashed_event_evidence(self):
        repo, current, receipt = self.repository_plan()
        process = self.run_cli(current, event(current, "submit", result=receipt), repo=repo)
        self.assertEqual(process.returncode, 0, process.stderr)

    def test_cli_repo_rejects_missing_receipt_evidence(self):
        repo, current, receipt = self.repository_plan()
        receipt["evidence"][0]["path"] = "synthetic-not-present/missing.txt"
        process = self.run_cli(current, event(current, "submit", result=receipt), repo=repo)
        self.assertNotEqual(process.returncode, 0, "CLI accepted missing evidence introduced by --event")
        self.assertIn("evidence", process.stderr.lower())

    def test_cli_repo_requires_source_manifest_and_rejects_bad_digest(self):
        repo, current, _ = self.repository_plan()
        for mutation in ("missing", "empty", "duplicate", "stale-hash", "wrong-digest"):
            bad = copy.deepcopy(current)
            if mutation == "missing":
                del bad["source_manifest"]
            elif mutation == "empty":
                bad["source_manifest"] = []
            elif mutation == "duplicate":
                bad["source_manifest"].append(copy.deepcopy(bad["source_manifest"][0]))
            elif mutation == "stale-hash":
                bad["source_manifest"][0]["sha256"] = "0" * 64
            else:
                bad["baseline"]["source_digest"] = "0" * 64
            with self.subTest(mutation=mutation):
                process = self.run_cli(bad, repo=repo)
                self.assertNotEqual(process.returncode, 0)
                self.assertIn("source", process.stderr.lower())

    def test_cli_repo_blocks_symlink_path_introduced_in_submit_event(self):
        with tempfile.TemporaryDirectory(prefix="ppo-cli-link-") as directory:
            root = Path(directory)
            repo, outside = root / "repo", root / "outside"
            repo.mkdir()
            outside.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], check=True,
                           capture_output=True, timeout=15)
            # Detached synthetic HEAD permits identity checks without making a commit.
            (repo / ".git/HEAD").write_text(BASELINE["commit"] + "\n", encoding="utf-8")
            (repo / "source.txt").write_text("synthetic source", encoding="utf-8")
            (outside / "receipt.txt").write_text("synthetic evidence", encoding="utf-8")
            (repo / "linked").symlink_to(outside, target_is_directory=True)
            source_hash = hashlib.sha256((repo / "source.txt").read_bytes()).hexdigest()
            source_digest = hashlib.sha256(("source.txt=" + source_hash + "\n").encode()).hexdigest()
            current = self.start(plan(baseline={"commit": BASELINE["commit"],
                                                "source_digest": source_digest},
                                       source_manifest=[{"path": "source.txt", "sha256": source_hash}]))
            receipt = result(current, evidence=[{"path": "linked/receipt.txt", "sha256": "e" * 64}])
            process = self.run_cli(current, event(current, "submit", result=receipt), repo=repo)
            self.assertNotEqual(process.returncode, 0)
            self.assertIn("symlink", process.stderr.lower())


if __name__ == "__main__":
    unittest.main()
