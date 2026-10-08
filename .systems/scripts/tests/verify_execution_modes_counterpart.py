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
from execution_modes import workflow_support

SOURCES = (".systems/ai/core/execution-modes.md", ".systems/ai/core/autopilot.md",
           ".systems/ai/core/owner-decision-checkpoints.md", ".systems/ai/core/delivery-constraints.md",
           ".systems/scripts/lib/execution-modes.py", ".systems/ai/templates/autopilot/execution-readiness.template.json")


def run(source, projection, expected=None, reject=False):
    with tempfile.TemporaryDirectory() as temp:
        state = Path(temp) / "state.json"
        state.write_text(json.dumps(projection))
        result = subprocess.run([sys.executable, "-B", str(source), "--state", str(state)],
                                capture_output=True, text=True, timeout=15, check=False)
        if reject:
            if result.returncode == 0:
                raise ValueError("counterpart unexpectedly accepted invalid scenario")
        else:
            if result.returncode:
                raise ValueError("counterpart scenario failed: " + result.stderr)
            data = json.loads(result.stdout)
            for key, value in expected.items():
                if data.get(key) != value:
                    raise ValueError("counterpart mismatch for " + key)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workflow-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.workflow_root.is_symlink():
            raise ValueError("linked counterpart root")
        root = args.workflow_root.resolve(strict=True)
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
            initial = json.loads((clone / SOURCES[-1]).read_text())
            source = clone / ".systems/scripts/lib/execution-modes.py"

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
            for name, digest in pinned.items():
                if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
                    raise ValueError("counterpart changed during inspection; refresh snapshot")
            print(json.dumps({"result": "candidate-protocol-scenarios-completed", "scenarios": scenarios,
                              "source_manifest": pinned, "installed_support": workflow_support(root),
                              "limitations": ["local draft; not counterpart release acceptance", "pure protocol tests; no native agent behavior proof",
                                              "planning/external effects remain coordinator scope gates"]}, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print("Counterpart verification error: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
