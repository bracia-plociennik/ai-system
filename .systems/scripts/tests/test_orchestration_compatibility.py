"""Real local Git/filesystem regressions; synthetic fixtures, not native backend proof."""

import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import orchestration_compatibility as c
import qa_source_binding as q
import capture_parity as p


def assignment(uid="u-a", task="TASK-001", **changes):
    value = dict(contract=2, id=uid, task_id=task, package_id=None, slice_id=uid, goal="bounded synthetic result",
                 dod=["observed test result"], dependencies=[], read_set=[], write_set=["src"], resources=[])
    value.update(changes)
    return value


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def directory(self, name):
        value = self.root / name
        value.mkdir(parents=True)
        return value

    def git_repo(self, name="repo"):
        root = self.directory(name)
        self.run_git(root, "init", "-q")
        self.run_git(root, "config", "user.name", "Synthetic")
        self.run_git(root, "config", "user.email", "synthetic@example.invalid")
        self.run_git(root, "config", "commit.gpgsign", "false")
        self.run_git(root, "config", "core.hooksPath", "/dev/null")
        (root / "source.txt").write_text("before\n")
        self.commit(root)
        return root

    def run_git(self, root, *args):
        subprocess.run(["git", "-C", str(root), *args], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def commit(self, root):
        self.run_git(root, "add", "--all")
        self.run_git(root, "commit", "-qm", "synthetic source")

    def worker(self, name="worker"):
        root = self.directory(name)
        (root / "src").mkdir()
        (root / "src/code").write_text("before")
        (root / "src/check").write_text("focused check completed")
        return root

    def receipt(self, root, attempt="attempt-1"):
        before = c.inventory(root)
        (root / "src/code").write_text("after")
        return c.seal_result(assignment(), attempt, root, before, True,
                             [{"path": "src/check", "sha256": c.fingerprint(root / "src/check")}])


class ProtocolTests(Fixture):
    def test_missing_capability_is_serial(self):
        self.assertEqual(c.negotiate(self.directory("workflow"))["fallback"], "serial")

    def test_valid_capability_pins_do_not_attest_backend(self):
        root = self.directory("workflow")
        names = [".systems/scripts/lib/parallel-orchestration.py", ".systems/scripts/plan-parallel-work", ".systems/scripts/manage-parallel-run",
                 ".systems/ai/templates/orchestration/" + "run.template.json", ".systems/ai/templates/orchestration/unit.template.json", ".systems/ai/templates/orchestration/result.template.json"]
        pins = {}
        for name in names:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("synthetic source")
            pins[name] = c.fingerprint(path)
        path = root / ".systems/ai/capabilities/parallel-task-orchestration-v1.json"
        path.parent.mkdir(parents=True)
        data = dict(schema_version=1, feature="parallel-task-orchestration-v1", protocol_version=1, manifest_schema=1,
                    unit_schema=1, result_schema=1, installed_sources_sha256=pins, native_backend={"verification": "verified", "capacity": 1000})
        path.write_text(json.dumps(data))
        result = c.negotiate(root)
        self.assertEqual(result["protocol"], "source-verified-v1")
        self.assertFalse(result["parallel_write"])
        self.assertFalse(result["execution_authorized"])
        (root / names[0]).write_text("drift")
        with self.assertRaises(c.Blocked):
            c.negotiate(root)

    def test_explicit_workflow_mapping(self):
        value = assignment()
        value.pop("contract")
        value["schema"] = 1
        self.assertEqual(c.unit(value, "ai-workflow"), assignment())
        with self.assertRaises(c.Blocked):
            c.unit(value)

    def test_invalid_units_and_paths(self):
        for changes in ({"contract": True}, {"task_id": None}, {"dod": []}, {"write_set": ["../x"]},
                        {"read_set": ["/x"]}, {"resources": ["database"]}, {"dependencies": ["a", "a"]}):
            with self.subTest(changes=changes), self.assertRaises(c.Blocked):
                c.unit(assignment(**changes))
        for path in ("x//y", "x/./y", "x/../y", "x\\y", "x\n"):
            with self.subTest(path=path), self.assertRaises(c.Blocked):
                c.relative(path)

    def test_read_write_and_shared_resource_conflicts(self):
        a = assignment(write_set=["Src"])
        b = assignment("u-b", read_set=["src/a"], write_set=["other"])
        self.assertTrue(c.access_conflict(a, b))
        a["resources"] = [{"name": "db", "mode": "shared"}]
        b.update(read_set=[], resources=[{"name": "db", "mode": "shared"}])
        self.assertFalse(c.access_conflict(a, b))
        b["resources"][0]["mode"] = "exclusive"
        self.assertTrue(c.access_conflict(a, b))

    def test_dynamic_workers_not_parent_task_cap(self):
        units = [assignment("unit-" + str(i), write_set=["src/" + str(i)]) for i in range(12)]
        cp = dict(known=True, parent_task_slots=3, active_tasks=[])
        self.assertEqual(len(c.allocate(units, 12, cp)["selected"]), 12)
        for i, u in enumerate(units):
            u["task_id"] = "TASK-" + str(i)
        self.assertEqual(len(c.allocate(units, 12, cp)["selected"]), 3)
        self.assertEqual(c.allocate(units, 0, cp)["selected"], [])

    def test_graph_and_unknown_gates(self):
        cp = dict(known=True, parent_task_slots=3, active_tasks=[])
        for units in ([assignment(dependencies=["missing"])], [assignment(dependencies=["u-a"])], [assignment(), assignment()]):
            with self.subTest(units=units), self.assertRaises(c.Blocked):
                c.allocate(units, 3, cp)
        with self.assertRaises(c.Blocked):
            c.allocate([assignment()], None, cp)
        with self.assertRaises(c.Blocked):
            c.allocate([assignment()], 1, dict(cp, known=False))


class ResultTests(Fixture):
    def test_receipt_and_actual_integration(self):
        worker = self.worker()
        target = self.directory("target")
        shutil.copytree(worker / "src", target / "src")
        receipt = self.receipt(worker)
        proof = c.integration_prepare(receipt, target)
        with self.assertRaises(c.Blocked):
            c.integration_confirm(proof, dict(intent=True, diff=True, tests=True, privacy=True))
        shutil.copyfile(worker / "src/code", target / "src/code")
        self.assertEqual(c.integration_confirm(proof, dict(intent=True, diff=True, tests=True, privacy=True))["state"], "integrated")
        self.assertFalse(c.integration_confirm(proof, dict(intent=True, diff=True, tests=True, privacy=True))["formal_pass"])

    def test_unexpected_write_and_unknown_termination(self):
        worker = self.worker()
        before = c.inventory(worker)
        (worker / "outside").write_text("bad")
        for terminated in (False, True):
            with self.subTest(terminated=terminated), self.assertRaises(c.Blocked):
                c.seal_result(assignment(), "attempt-1", worker, before, terminated, [{"path": "src/check", "sha256": c.fingerprint(worker / "src/check")}])

    def test_modes_directories_deletions_and_symlink(self):
        worker = self.worker()
        before = c.inventory(worker)
        (worker / "src/empty").mkdir()
        (worker / "src/code").chmod(0o755)
        (worker / "src/check").unlink()
        after = c.inventory(worker)
        self.assertNotEqual(before, after)
        self.assertEqual(after["entries"]["src/empty"]["kind"], "directory")
        (worker / "escape").symlink_to(self.root)
        with self.assertRaises(c.Blocked):
            c.inventory(worker)

    def test_output_and_destination_drift(self):
        worker = self.worker()
        target = self.directory("target")
        shutil.copytree(worker / "src", target / "src")
        receipt = self.receipt(worker)
        (target / "src/code").write_text("manual conflict")
        with self.assertRaises(c.Blocked):
            c.integration_prepare(receipt, target)
        (worker / "src/code").write_text("late mutation")
        with self.assertRaises(c.Blocked):
            c.verify_result(receipt)

    def test_seal_and_dependency_coverage(self):
        worker = self.worker()
        receipt = self.receipt(worker)
        consumer = self.directory("consumer")
        shutil.copytree(worker / "src", consumer / "src")
        self.assertIn("delivery_sha256", c.verify_delivery(receipt, consumer, ["src"]))
        (consumer / "src/unexplained").write_text("extra")
        with self.assertRaises(c.Blocked):
            c.verify_delivery(receipt, consumer, ["src"])
        with self.assertRaises(c.Blocked):
            c.verify_delivery(receipt, worker, ["src"])
        bad = copy.deepcopy(receipt)
        bad["body"]["attempt"] = "forged"
        with self.assertRaises(c.Blocked):
            c.verify_result(bad)


class LedgerTests(Fixture):
    def make(self):
        path = self.directory("project-state/example/orchestration/runs/run-a") / "ledger.json"
        ledger = c.Ledger(path, "coordinator", self.root)
        ledger.update(-1, "init", {})
        worker = self.worker()
        ledger.update(0, "reserve", dict(attempt="a", unit=assignment(), worker_root=str(worker), before=c.inventory(worker)))
        receipt = self.receipt(worker, "a")
        ledger.update(1, "submit", dict(attempt="a", receipt=receipt))
        ledger.update(2, "accept", dict(attempt="a", review=dict(intent=True, diff=True, tests=True, privacy=True)))
        return ledger, worker

    def test_cas_and_duplicate_attempt_preserve_bytes(self):
        ledger, worker = self.make()
        before = ledger.path.read_bytes()
        for expected, action, payload in ((0, "unknown", {"attempt": "a"}), (3, "reserve", dict(attempt="a", unit=assignment(), worker_root=str(worker), before=c.inventory(worker)))):
            with self.subTest(action=action), self.assertRaises(c.Blocked):
                ledger.update(expected, action, payload)
            self.assertEqual(before, ledger.path.read_bytes())

    def test_lock_and_coordinator_ownership(self):
        ledger, _ = self.make()
        lock = ledger.path.with_suffix(".lock")
        lock.write_text("other coordinator")
        with self.assertRaises(c.Blocked):
            ledger.update(3, "unknown", {"attempt": "a"})
        self.assertTrue(lock.exists())
        with self.assertRaises(c.Blocked):
            c.Ledger(ledger.path, "other", self.root).read()

    def test_crash_after_replace_retains_lock_for_reconcile(self):
        ledger, _ = self.make()
        real = c.atomic_json
        def crash(path, data):
            real(path, data)
            raise OSError("synthetic lost acknowledgement")
        with mock.patch.object(c, "atomic_json", side_effect=crash), self.assertRaises(OSError):
            ledger.update(3, "unknown", {"attempt": "a"})
        self.assertEqual(ledger.read()["revision"], 4)
        self.assertTrue(ledger.path.with_suffix(".lock").exists())

    def test_unknown_effect_blocks_new_dispatch(self):
        ledger, _ = self.make()
        ledger.update(3, "unknown", {"attempt": "a"})
        other = self.worker("other")
        with self.assertRaises(c.Blocked):
            ledger.update(4, "reserve", dict(attempt="b", unit=assignment("u-b", write_set=["other"]), worker_root=str(other), before=c.inventory(other)))

    def test_history_tampering_rejected(self):
        ledger, _ = self.make()
        data = ledger.read()
        data["reservations"]["a"]["state"] = "integrated"
        ledger.path.write_text(json.dumps(data))
        with self.assertRaises(c.Blocked):
            ledger.read()

    def test_no_managed_repo_ledger(self):
        path = self.directory("projects/example/orchestration/runs/run-a") / "ledger.json"
        with self.assertRaises(c.Blocked):
            c.Ledger(path, "coordinator", self.root)

    def test_integration_unknown_then_reviewed_abandonment(self):
        ledger, worker = self.make()
        target = self.worker("target")
        ledger.update(3, "integration-prepare", dict(attempt="a", destination=str(target)))
        ledger.update(4, "unknown", dict(attempt="a"))
        with self.assertRaises(c.Blocked):
            ledger.update(5, "reconcile", dict(attempt="a", termination=False, reviewed_inventory=c.inventory(target)))
        ledger.update(5, "reconcile", dict(attempt="a", termination=True, reviewed_inventory=c.inventory(target)))
        data = ledger.read()
        self.assertEqual(data["reservations"]["a"]["state"], "reconciled")
        self.assertEqual(len(data["events"]), 6)


class BindingTests(Fixture):
    def test_first_source_commit_equivalence(self):
        repo = self.git_repo()
        (repo / "source.txt").write_text("intended\n")
        (repo / "new.txt").write_text("new\n")
        value = q.snapshot(repo, "project", "task")
        self.assertEqual(q.verify_snapshot(value, repo)["binding"], "same-head")
        self.commit(repo)
        self.assertEqual(q.verify_snapshot(value, repo)["binding"], "first-source-only-commit")

    def test_live_and_ignored_population_drift(self):
        repo = self.git_repo()
        value = q.snapshot(repo, "project", "task")
        (repo / "untracked").write_text("extra")
        with self.assertRaises(c.Blocked):
            q.verify_snapshot(value, repo)

    def test_partial_staging_rejected(self):
        repo = self.git_repo()
        (repo / "source.txt").write_text("intended\n")
        (repo / "unstaged").write_text("intended too\n")
        value = q.snapshot(repo, "project", "task")
        self.run_git(repo, "add", "source.txt")
        self.run_git(repo, "commit", "-qm", "partial")
        with self.assertRaises(c.Blocked):
            q.verify_snapshot(value, repo)

    def test_later_commit_and_runtime_chain_rejected(self):
        repo = self.git_repo()
        (repo / "source.txt").write_text("new\n")
        value = q.snapshot(repo, "project", "task")
        self.commit(repo)
        self.run_git(repo, "commit", "--allow-empty", "-qm", "later")
        with self.assertRaises(c.Blocked):
            q.verify_snapshot(value, repo)
        other = self.git_repo("runtime-repo")
        (other / "capture-state").mkdir()
        (other / "capture-state/work.md").write_text("runtime")
        value = q.snapshot(other, "project", "task")
        self.commit(other)
        with self.assertRaises(c.Blocked):
            q.verify_snapshot(value, other)

    def test_dependency_and_mode_drift(self):
        repo = self.git_repo()
        dep = self.directory("dependency")
        (dep / "input").write_text("before")
        value = q.snapshot(repo, "project", "task", [dep])
        (dep / "input").write_text("after")
        with self.assertRaises(c.Blocked):
            q.verify_snapshot(value, repo)
        value = q.snapshot(repo, "project", "task", [dep])
        (repo / "source.txt").chmod(0o755)
        with self.assertRaises(c.Blocked):
            q.verify_snapshot(value, repo)

    def test_phase_commit_optouts_and_owner_gate(self):
        for phase in ("planning-range", "phase-6", "phase-7", "phase-8"):
            self.assertEqual(q.phase_commit(phase, True, True, True, True, "yes", True), "forbidden-by-owner")
            self.assertEqual(q.phase_commit(phase, True, False, False), "not-required")
            self.assertEqual(q.phase_commit(phase, False, False, True, True, "yes", True), "blocked")
        self.assertEqual(q.phase_commit("phase-8", True, False, True, False, "yes", True), "awaiting-owner-final-yes")
        self.assertEqual(q.phase_commit("phase-7", True, False, True, False, "yes", True), "eligible-for-scoped-commit-not-executed")


class CaptureTests(Fixture):
    def formal(self):
        root = self.directory("workspace")
        source = self.git_repo()
        owner = "project-state/example/capture-state"
        records = root / owner
        records.mkdir(parents=True)
        evidence = root / "project-state/example/evidence"
        (evidence / "quality").mkdir(parents=True)
        (evidence / "distillations").mkdir()
        distillation = evidence / "distillations/work.md"
        distillation.write_text("- Work ID: new\n- Owning project: example\n- Acceptance: accepted\n")
        qa = evidence / "quality/implementation.md"
        qa.write_text("# Quality\n- QA verification contract: `full-qa-verification-v2`\n\n## Current QA Run\n"
                      "- Artifact kind: implementation-quality\n- Project/task identity: example:TASK-001\n"
                      "- Assessed source HEAD: " + q.git(source, "rev-parse", "HEAD") + "\n- Verdict: PASS\n- Gate Decision: PASS\n"
                      "### Input Artifacts\n| approved-target-source | source.txt | " + c.fingerprint(source / "source.txt") + " |\n"
                      "### Definition Of Done Validation\n| observed outcome | PASS | local fixture |\n"
                      "### Intent / Plan / Spec Compliance\n- Result: PASS\n"
                      "### Review Completeness Gate\n- Status: complete\n- Closure freshness: current\n- Required-field mapping: complete\n"
                      "### Quality Gate\n- 100% DoD satisfied: yes\n- No known bug in scope: yes\n- Quality result: PASS\n")
        data = dict(work_id="new", project="example", task_ids=["TASK-001"], source_root=str(source),
                    source_head=q.git(source, "rev-parse", "HEAD"), evidence_root=evidence.relative_to(root).as_posix(),
                    qa_refs=[dict(path="quality/implementation.md", sha256=c.fingerprint(qa))], distillation_sha256=c.fingerprint(distillation))
        record = records / "new.md"
        record.write_text("- Capture schema: 2\n- Work ID: new\n- State: completed\n- Privacy/scope check: pass\n- `is_distilled` derived value: true\n"
                          "- Distillation artifact: " + distillation.relative_to(root).as_posix() + "\n"
                          "## Capture Verification\n```json\n" + json.dumps(data) + "\n```\n")
        return root, owner, record, source, qa, distillation, data

    def test_complete_current_collection(self):
        root, owner, record, source, qa, distillation, data = self.formal()
        self.assertTrue(p.validate_formal(record, root)["current_quality"])
        self.assertFalse(p.collection(root, owner)["errors"])

    def test_current_capture_rejects_source_qa_and_distillation_drift(self):
        for target in ("source", "qa", "distillation"):
            with self.subTest(target=target):
                local = tempfile.TemporaryDirectory()
                self.addCleanup(local.cleanup)
                oldroot = self.root
                self.root = Path(local.name).resolve()
                root, owner, record, source, qa, distillation, data = self.formal()
                path = source / "source.txt" if target == "source" else qa if target == "qa" else distillation
                path.write_text("changed")
                self.assertIn("new.md", p.collection(root, owner)["errors"])
                self.root = oldroot

    def test_every_input_root_is_verified_in_current_capture(self):
        root, owner, record, source, qa, distillation, data = self.formal()
        workflow = source / "ai-workflow"
        workflow.mkdir()
        (workflow / "contract.md").write_text("installed local contract")
        text = qa.read_text().replace("### Definition Of Done Validation", "| workflow-source | contract.md | " + c.fingerprint(workflow / "contract.md") + " |\n### Definition Of Done Validation")
        prefix = record.read_text().split("## Capture Verification", 1)[0]
        def update(text):
            qa.write_text(text)
            data["qa_refs"][0]["sha256"] = c.fingerprint(qa)
            record.write_text(prefix + "## Capture Verification\n```json\n" + json.dumps(data) + "\n```\n")
        update(text)
        self.assertTrue(p.validate_formal(record, root)["current_quality"])
        (workflow / "contract.md").write_text("changed installed contract")
        with self.assertRaises(c.Blocked):
            p.validate_formal(record, root)
        update(text.replace("workflow-source", "unapproved-root"))
        with self.assertRaises(c.Blocked):
            p.validate_formal(record, root)
        update(text.replace(c.fingerprint(source / "source.txt"), "bad-fingerprint"))
        with self.assertRaises(c.Blocked):
            p.validate_formal(record, root)

    def test_shared_capture_and_goal_claims_use_registered_policy_home(self):
        root, owner, record, source, qa, distillation, data = self.formal()
        system = self.directory("shared-system")
        home = self.directory("registered-user")
        (system / "ai-system.local.json").write_text(json.dumps(dict(schema_version=1, role="management")))
        reg = home / ".config/ai-system/installation.json"
        reg.parent.mkdir(parents=True)
        reg.write_text(json.dumps(dict(schema_version=1, system_id="test", system_home=str(system),
                    enabled=True, adapter_ids=["codex"], owner_workspace_id="test", owner_asset_id="host")))
        config = system / "ai-workflow-workspace/shared-installation.json"
        config.parent.mkdir()
        config.write_text(json.dumps(dict(schema_version=1, enabled=True, workflow_home="ai-workflow")))
        target = system / "projects/target"
        target.parent.mkdir()
        source.rename(target)
        data["source_root"] = str(target)
        workflow = system / "ai-workflow"
        workflow.mkdir()
        self.run_git(workflow, "init", "-q")
        self.run_git(workflow, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "--allow-empty", "-qm", "fixture")
        for rel in ("AGENTS.md", ".systems/scripts/resolve-workflow-env", ".systems/ai/core/repository-modes.md", ".systems/ai/core/risk-model.md", "contract.md"):
            out = workflow / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text("synthetic installed policy")
        text = qa.read_text().replace("### Definition Of Done Validation", "| workflow-source | contract.md | " + c.fingerprint(workflow / "contract.md") + " |\n### Definition Of Done Validation")
        qa.write_text(text)
        data["qa_refs"][0]["sha256"] = c.fingerprint(qa)
        prefix = record.read_text().split("## Capture Verification", 1)[0]
        record.write_text(prefix + "## Capture Verification\n```json\n" + json.dumps(data) + "\n```\n")
        with mock.patch.dict(os.environ, dict(HOME=str(home), AI_SYSTEM_HOME=str(system))):
            self.assertTrue(p.validate_formal(record, root)["current_quality"])
            self.assertEqual(p.workflow_source_root(target), workflow)
            import maintenance_policy
            with mock.patch.object(maintenance_policy, "select_goal", wraps=maintenance_policy.select_goal) as select:
                claims = p.goal_collection(root, owner, ["new"])
                self.assertEqual(claims["gate_result"], "PASS")
                self.assertIn(str(workflow / "contract.md"), select.call_args.args[1][0]["source_refs"])
            self.assertFalse((target / "ai-workflow").exists())
            for rel in (".systems/scripts/resolve-workflow-env", ".systems/ai/core/repository-modes.md"):
                out = target / rel
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text("synthetic official source")
            with mock.patch.dict(os.environ, dict(AI_WORKFLOW_MODE="official")):
                self.assertEqual(p.workflow_source_root(target), target)
            self.assertEqual(p.workflow_source_root(target), workflow)
            (workflow / "contract.md").write_text("drift")
            with self.assertRaises(c.Blocked):
                p.validate_formal(record, root)
            config.write_text("{}")
            with self.assertRaises(ValueError):
                p.workflow_source_root(target)

    def test_product_only_capture_does_not_require_workflow_registration(self):
        root, owner, record, source, qa, distillation, data = self.formal()
        import durable_runtime
        with mock.patch.object(durable_runtime, "registered_system", side_effect=ValueError("unavailable")):
            self.assertTrue(p.validate_formal(record, root)["current_quality"])
            self.assertEqual(p.goal_collection(root, owner, ["new"])["gate_result"], "PASS")

    def test_official_workflow_evidence_uses_source_itself(self):
        source = self.git_repo()
        for rel in (".systems/scripts/resolve-workflow-env", ".systems/ai/core/repository-modes.md"):
            out = source / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text("synthetic official source")
        self.assertEqual(p.workflow_source_root(source), source)

    def test_shared_distillation_claim_and_missing_quality_completeness(self):
        root, owner, record, source, qa, distillation, data = self.formal()
        sibling = record.with_name("sibling.md")
        sibling.write_text("- Work ID: other\n- Distillation artifact: " + distillation.relative_to(root).as_posix() + "\n- State: bad\n- State: bad\n")
        self.assertIn("new.md", p.collection(root, owner)["errors"])
        text = qa.read_text().replace("### Quality Gate", "### Removed Gate")
        with self.assertRaises(c.Blocked):
            q.quality_gate(text)

    def test_physical_distillation_alias_claims(self):
        root, owner, record, source, qa, distillation, data = self.formal()
        alias = distillation.with_name("alias.md")
        os.link(distillation, alias)
        record.with_name("invalid-sibling.md").write_text("- Work ID: other\n- State: broken\n- Distillation artifact: " + str(alias) + "\n")
        self.assertIn("new.md", p.collection(root, owner)["errors"])

    def test_parent_completion_rechecks_plan_integration_and_capture(self):
        root, owner, record, source, qa, distillation, data = self.formal()
        directory = root / "project-state/example/orchestration/runs/run-a"
        directory.mkdir(parents=True)
        ledger = c.Ledger(directory / "ledger.json", "coordinator", root)
        worker = self.worker()
        target = self.worker("target")
        ledger.update(-1, "init", {})
        ledger.update(0, "reserve", dict(attempt="a", unit=assignment(), worker_root=str(worker), before=c.inventory(worker)))
        ledger.update(1, "submit", dict(attempt="a", receipt=self.receipt(worker, "a")))
        review = dict(intent=True, diff=True, tests=True, privacy=True)
        ledger.update(2, "accept", dict(attempt="a", review=review))
        ledger.update(3, "integration-prepare", dict(attempt="a", destination=str(target)))
        shutil.copyfile(worker / "src/code", target / "src/code")
        ledger.update(4, "integration-confirm", dict(attempt="a", review=review))
        plan = dict(contract=2, units=[assignment()], capacity=1,
                    checkpoint=dict(known=True, parent_task_slots=3, active_tasks=[]), dependency_ready=[], execution_mode="proposal-only")
        plan_path = directory / "plan.json"
        plan_path.write_text(json.dumps(plan))
        sha = c.fingerprint(plan_path)
        result = p.parent_completion(ledger, root, owner, "new", plan_path, sha)
        self.assertFalse(result["formal_pass"])
        (target / "src/code").write_text("late mutation")
        with self.assertRaises(c.Blocked):
            p.parent_completion(ledger, root, owner, "new", plan_path, sha)
        shutil.copyfile(worker / "src/code", target / "src/code")
        qa.write_text("stale QA")
        with self.assertRaises(c.Blocked):
            p.parent_completion(ledger, root, owner, "new", plan_path, sha)

    def test_schema3_consumes_same_real_commit_binding(self):
        root, owner, record, source, qa, distillation, data = self.formal()
        (source / "source.txt").write_text("intended")
        value = q.snapshot(source, "example", "TASK-001")
        frozen = qa.parent / "source-snapshot.json"
        frozen.write_text(json.dumps(value))
        text = qa.read_text().replace('`full-qa-verification-v2`', 'full-qa-verification-v3')
        text += "- Source snapshot SHA-256: " + value["sha256"] + "\n"
        qa.write_text(text)
        data["qa_refs"][0].update(sha256=c.fingerprint(qa), snapshot_path="quality/source-snapshot.json", snapshot_sha256=c.fingerprint(frozen))
        original = record.read_text().split("## Capture Verification", 1)[0].replace("Capture schema: 2", "Capture schema: 3")
        record.write_text(original + "## Capture Verification\n```json\n" + json.dumps(data) + "\n```\n")
        self.commit(source)
        self.assertTrue(p.validate_formal(record, root)["current_quality"])
        (source / "extra").write_text("unreviewed")
        with self.assertRaises(c.Blocked):
            p.validate_formal(record, root)

    def test_historical_pass_cannot_satisfy_current_binding(self):
        root, owner, record, source, qa, distillation, data = self.formal()
        value = q.snapshot(source, "example", "TASK-001")
        text = qa.read_text().replace('`full-qa-verification-v2`', 'full-qa-verification-v3')
        text += "- Source snapshot SHA-256: " + value["sha256"] + "\n"
        qa.write_text(text)
        self.assertTrue(q.verify_qa_binding(value, source, qa, "example", "TASK-001")["equivalent"])
        failed = text.replace("- Verdict: PASS", "- Verdict: FAIL").replace("- Gate Decision: PASS", "- Gate Decision: FAIL")
        qa.write_text(failed + "\n## Historical Runs\n- Verdict: PASS\n- Gate Decision: PASS\n")
        with self.assertRaises(c.Blocked):
            q.verify_qa_binding(value, source, qa, "example", "TASK-001")
        failed = text.replace("### Quality Gate", "## Historical Runs\n### Quality Gate")
        qa.write_text(failed)
        with self.assertRaises(c.Blocked):
            q.verify_qa_binding(value, source, qa, "example", "TASK-001")

    def test_fenced_qa_is_context_not_current_evidence(self):
        root, owner, record, source, qa, distillation, data = self.formal()
        raw = qa.read_text()
        qa.write_text("```markdown\n" + raw + "```\n")
        data["qa_refs"][0]["sha256"] = c.fingerprint(qa)
        prefix = record.read_text().split("## Capture Verification", 1)[0]
        record.write_text(prefix + "## Capture Verification\n```json\n" + json.dumps(data) + "\n```\n")
        with self.assertRaises(c.Blocked):
            p.validate_formal(record, root)
        with self.assertRaises(c.Blocked):
            q.quality_gate(qa.read_text())
        qa.write_text("~~~markdown\n" + raw + "~~~\n" + raw.replace("- Verdict: PASS", "- Verdict: FAIL"))
        with self.assertRaises(c.Blocked):
            p.validate_formal(record, root)

    def test_canonical_population_and_historical_quality(self):
        root = self.directory("workspace")
        owner = "project-state/example/capture-state"
        records = root / owner
        records.mkdir(parents=True)
        (records / "old.md").write_text("- Work ID: old\n- State: completed\n")
        self.assertFalse(p.collection(root, owner)["records"][0]["current_quality"])
        for unsafe in ("projects/example/capture-state", "../foreign", "project-state/../capture-state"):
            with self.subTest(owner=unsafe), self.assertRaises(c.Blocked):
                p.collection(root, unsafe)

    def test_invalid_sibling_duplicate_blocks_current_record(self):
        root = self.directory("workspace")
        owner = "project-state/example/capture-state"
        records = root / owner
        records.mkdir(parents=True)
        text = "- Capture schema: 2\n- Work ID: new\n- State: pending-quality\n- Privacy/scope check: pass\n- `is_distilled` derived value: false\n- Distillation artifact: none\n"
        (records / "new.md").write_text(text)
        self.assertFalse(p.collection(root, owner)["errors"])
        (records / "bad.md").write_text("- Work ID: new\n- State: bad\n- State: bad\n")
        self.assertIn("new.md", p.collection(root, owner)["errors"])

    def test_current_qa_and_distillation_required(self):
        root = self.directory("workspace")
        path = root / "record.md"
        path.write_text("- Capture schema: 2\n- Work ID: new\n- State: completed\n- Privacy/scope check: pass\n- `is_distilled` derived value: true\n- Distillation artifact: none\n")
        with self.assertRaises(c.Blocked):
            p.validate_formal(path, root)


if __name__ == "__main__":
    unittest.main()
