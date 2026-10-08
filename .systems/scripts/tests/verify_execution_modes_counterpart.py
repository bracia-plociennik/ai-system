"""Exercise a frozen synthetic copy of an explicitly selected Workflow candidate."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from execution_modes import WORKFLOW_SOURCES, inspect_workflow_state, workflow_support

SOURCES = tuple(sorted(WORKFLOW_SOURCES))


def run(root, projection, expected=None, reject=False):
    with tempfile.TemporaryDirectory() as temp:
        state = Path(temp) / "state.json"
        state.write_text(json.dumps(projection))
        try:
            inspected = inspect_workflow_state(root, state)
        except ValueError as error:
            if reject and "Workflow rejected original projection:" in str(error):
                return
            raise
        if reject:
            raise ValueError("counterpart unexpectedly accepted invalid scenario")
        data = inspected["workflow_readiness"]
        if inspected["selection"]["scope"] != projection["execution"]["scope"] or inspected["selection"]["scope_id"] != projection["execution"]["scope_id"]:
            raise ValueError("adapter lost original source scope")
        for key, value in expected.items():
            if data.get(key) != value:
                raise ValueError("counterpart mismatch for " + key)


def preflight_cases(frozen_root, initial):
    """Build a disposable target installation; never mutate the counterpart."""
    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory) / "target"
        target.mkdir()
        workflow = target / "ai-workflow"
        import shutil
        shutil.copytree(frozen_root, workflow)
        (workflow / "AGENTS.md").write_text("# Synthetic Workflow installation\n")
        (target / "AGENTS.md").write_text("# Synthetic target\n")
        for repository in (target, workflow):
            subprocess.run(["git", "init", str(repository)], capture_output=True, check=True)
            subprocess.run(["git", "-C", str(repository), "add", "AGENTS.md"], capture_output=True, check=True)
            if repository == workflow:
                subprocess.run(["git", "-C", str(repository), "add", ".systems"], capture_output=True, check=True)
            subprocess.run(["git", "-C", str(repository), "-c", "user.name=Synthetic Test", "-c",
                            "user.email=test@example.invalid", "commit", "-m", "synthetic installation"], capture_output=True, check=True)
        runtime = target / "ai-workflow-workspace"
        repo_state = runtime / "repo/core"
        project = runtime / "projects/example-project"
        repo_state.mkdir(parents=True)
        project.mkdir(parents=True)
        (repo_state / "status.md").write_text("# Synthetic repo status\n")
        (repo_state / "repo-intake.md").write_text("# Synthetic repo intake\n")
        (project / "status.md").write_text("| Field | Value |\n| --- | --- |\n| `blocking-reason` | `none` |\n")
        state = Path(directory) / "readiness.json"
        script = Path(__file__).resolve().parents[1] / "project-orchestration-preflight"

        def inspect(value, expected_code, explicit=None):
            state.write_text(json.dumps(value))
            command = [sys.executable, "-B", str(script), "--workspace", str(runtime), "--repo", str(target),
                       "--project-id", "example-project", "--workflow-state", str(state)]
            if explicit:
                command += ["--execution-mode", explicit]
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            if result.returncode != expected_code:
                raise ValueError("preflight integration failed: " + result.stdout + result.stderr)
            return json.loads(result.stdout)

        value = json.loads(json.dumps(initial))
        value["execution"].update(mode="human-coop", scope="project", scope_id="example-project", source="explicit owner project")
        result = inspect(value, 0)
        if result["workflow_execution"]["counterpart_mode"] != "human-coop":
            raise ValueError("preflight reset resumed Human mode")
        inspect(value, 1, "auto")
        value["execution"]["scope_id"] = "other-project"
        inspect(value, 1)
        value["execution"]["scope_id"] = "example-project"
        value["units"][0]["approved_actions"] = []
        inspect(value, 1)
        second = json.loads(json.dumps(initial["units"][0]))
        second.update(id="UNIT-002", resources=["files/independent"])
        value["units"].append(second)
        inspect(value, 0)
        return ["preflight-human-resume", "preflight-explicit-mode-conflict", "preflight-project-identity-conflict",
                "preflight-no-safe-unit", "preflight-independent-continuation"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workflow-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.workflow_root.is_symlink():
            raise ValueError("linked counterpart root")
        root = args.workflow_root.resolve(strict=True)
        support = workflow_support(root)
        if support["status"] != "source-bound":
            raise ValueError("counterpart sources not recognized: " + support["reason"])
        pinned = {}
        with tempfile.TemporaryDirectory() as directory:
            clone = Path(directory)
            for name in SOURCES:
                path = root / name
                if any(p.is_symlink() for p in [path, *path.parents] if p != root and p.is_relative_to(root)):
                    raise ValueError("linked counterpart source")
                content = path.read_bytes()
                pinned[name] = hashlib.sha256(content).hexdigest()
                target = clone / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
                target.chmod(path.stat().st_mode & 0o777)
            initial = json.loads((clone / ".systems/ai/templates/autopilot/execution-readiness.template.json").read_text())
            source = root

            def fresh():
                state = json.loads(json.dumps(initial))
                unit = state["units"][0]
                unit.update(dependencies_known=True, isolation_verified=True, gates_ready=True,
                            dod_testable=True, required_actions=["product-write"],
                            approved_actions=["product-write"], approval_reference="owner-approved scoped plan")
                return state

            scenarios = []
            state = fresh()
            run(source, state, {"mode": "auto", "ready_units": ["UNIT-001"]})
            scenarios.append("approved-auto")
            state["execution"]["mode"] = "human-coop"
            run(source, state, {"mode": "human-coop", "ready_units": ["UNIT-001"]})
            scenarios.append("human-vocabulary")
            state = fresh()
            state["units"][0]["approved_actions"] = []
            run(source, state, {"ready_units": [], "result": "blocked"})
            scenarios.append("missing-action-approval")
            state = fresh()
            second = json.loads(json.dumps(state["units"][0]))
            second.update(id="UNIT-002", resources=["files/second"])
            state["units"].append(second)
            state["decisions"] = [{"id": "DEC-001", "classification": "owner-preference", "disposition": "pending",
                                   "affected_units": ["UNIT-001"], "reversible": True, "within_scope": True,
                                   "permission_covered": True, "reason": "owner choice", "override_impact": "affects only first unit"}]
            run(source, state, {"ready_units": ["UNIT-002"], "pending_decisions": ["DEC-001"]})
            scenarios.append("dependent-blocker-independent-continuation")
            state["units"][1]["dependencies"] = ["UNIT-001"]
            run(source, state, {"ready_units": []})
            scenarios.append("transitive-blocker")
            state = fresh()
            state["units"][0]["dependencies_known"] = False
            run(source, state, {"ready_units": []})
            scenarios.append("unknown-dependency")
            state = fresh()
            state["baseline"]["current"] = "changed"
            run(source, state, {"ready_units": []})
            scenarios.append("resume-baseline-drift")
            state = fresh()
            state["final_check"]["requested"] = True
            run(source, state, reject=True)
            scenarios.append("phase8-needs-explicit-scope")
            state = fresh()
            state["final_check"]["owner_yes"] = True
            run(source, state, reject=True)
            scenarios.append("metadata-cannot-grant-final-owner-yes")
            state = fresh()
            state["requested_status"] = "completed"
            run(source, state, reject=True)
            scenarios.append("incomplete-dod-not-completed")
            for scope in ("project", "session"):
                state = fresh()
                state["execution"].update(mode="human-coop", scope=scope, scope_id="explicit-" + scope,
                                          source="owner " + scope + " selection")
                run(source, state, {"mode": "human-coop", "ready_units": ["UNIT-001"]})
                scenarios.append(scope + "-scope-preserved")
            state = fresh()
            state["execution"]["mode"] = "human"
            run(source, state, reject=True)
            scenarios.append("unmapped-vocabulary-rejected")
            state = fresh()
            state["units"][0]["resources"] = []
            run(source, state, reject=True)
            scenarios.append("empty-write-resources-rejected")
            state = fresh()
            state["units"][0]["work_kind"] = "planning"
            run(source, state, reject=True)
            scenarios.append("plan-only-rejects-product-write")
            state = fresh()
            state["units"][0]["risk"] = "high"
            run(source, state, {"ready_units": ["UNIT-001"]})
            scenarios.append("explicit-local-high-risk-approval-preserved")
            state = fresh()
            state["units"][0]["required_actions"] = ["external-write"]
            run(source, state, {"ready_units": []})
            scenarios.append("product-write-does-not-cover-external-action")
            state = fresh()
            state["decisions"] = [{"id": "DEC-001", "classification": "owner-preference", "disposition": "agent-choice",
                                   "affected_units": ["UNIT-001"], "reversible": True, "within_scope": True,
                                   "permission_covered": True, "reason": "covered reversible choice", "override_impact": "local rework"}]
            run(source, state, {"ready_units": ["UNIT-001"]})
            state["execution"]["mode"] = "human-coop"
            run(source, state, reject=True)
            scenarios.append("human-material-choice-retains-owner-gate")
            scenarios.extend(preflight_cases(clone, initial))
            for name, digest in pinned.items():
                if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
                    raise ValueError("counterpart changed during inspection; refresh snapshot")
            if workflow_support(root) != support:
                raise ValueError("counterpart recognition changed during scenarios")
            print(json.dumps({"result": "candidate-protocol-scenarios-completed", "scenarios": scenarios,
                              "source_manifest": pinned, "installed_support": workflow_support(root),
                              "limitations": ["actual committed local counterpart; no rollout or owner acceptance", "pure protocol tests; no native agent behavior proof",
                                              "planning/external effects remain coordinator scope gates"]}, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print("Counterpart verification error: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
