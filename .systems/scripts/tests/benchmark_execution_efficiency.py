"""Three-sample local benchmark; equal selected checks, no private runtime."""
import argparse
import json
from pathlib import Path
import secrets
import statistics
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
from execution_efficiency import read_record
from smoke_fixture import copy_fixture
from validation_support import atomic_create, safe_destination

EXTRAS = [".systems/ai/core/execution-efficiency.md", ".systems/ai/templates/quality/execution-quality-record.template.json", ".systems/scripts/execution_efficiency.py",
          ".systems/scripts/prepare-quality-record", ".systems/scripts/check-execution-efficiency",
          ".systems/scripts/tests/test_execution_efficiency.py", ".systems/scripts/tests/benchmark_execution_efficiency.py"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-root", required=True, type=Path)
    parser.add_argument("--candidate-root", required=True, type=Path)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    destination = safe_destination(args.output, args.candidate_root)
    results = {"contract": 1, "supporting_only": True, "scope": "synthetic scoped scripts, not whole-agent latency",
               "samples_per_variant": 3, "cases": {}}
    with tempfile.TemporaryDirectory(prefix="efficiency-benchmark-") as temp:
        base = Path(temp).resolve()
        key = base / "reuse.key"
        key.write_bytes(secrets.token_bytes(32))
        key.chmod(0o600)
        for case in ("bounded-multi-consumer-defect", "runtime-only-closure", "shared-contract-change"):
            variants = {}
            for variant, source in (("baseline", args.baseline_root), ("candidate", args.candidate_root)):
                root = base / (case + "-" + variant)
                root.mkdir()
                copy_fixture(source, root, EXTRAS if variant == "candidate" else [])
                subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
                warm = base / (case + "-" + variant + "-warm.md")
                command = [str(root / ".systems/scripts/validate-ai-system"), "--profile", "scoped", "--checks",
                           "check-delivery-constraints,check-distillation-state"]
                if variant == "candidate":
                    command += ["--reuse-key-file", str(key)]
                preflight = subprocess.run(command + ["--evidence-file", str(warm)], cwd=root, capture_output=True, text=True)
                if preflight.returncode:
                    raise RuntimeError(preflight.stdout + preflight.stderr)
                if case == "runtime-only-closure":
                    (root / "synthetic-runtime.md").write_text("synthetic closure, product unchanged\n")
                else:
                    target = root / ("README.md" if case == "bounded-multi-consumer-defect" else ".systems/ai/core/delivery-constraints.md")
                    target.write_text(target.read_text() + "\nSynthetic benchmark source revision.\n")
                samples = []
                for sample in range(3):
                    output = base / f"{case}-{variant}-{sample}.md"
                    extra = ["--reuse-evidence", str(warm)] if variant == "candidate" else []
                    start = time.monotonic_ns()
                    result = subprocess.run(command + extra + ["--evidence-file", str(output)], cwd=root, capture_output=True, text=True)
                    wall = (time.monotonic_ns() - start) / 1e9
                    if result.returncode:
                        raise RuntimeError(result.stdout + result.stderr)
                    record = read_record(output)
                    samples.append({"wall_seconds": wall, "source_digest": record["source"]["source_digest"],
                                    "environment_digest": record["environment_digest"], "coverage_digest": record["coverage_digest"],
                                    "check_ids": [c["id"] for c in record["checks"]],
                                    "executed": sum(c["state"] == "completed" for c in record["checks"]),
                                    "reused": sum(c["state"] == "reused" for c in record["checks"]),
                                    "rerun_reasons": {c["id"]: c.get("rerun_reason", "baseline fresh execution") for c in record["checks"]}})
                if any(len({s[field] for s in samples}) != 1 for field in ("source_digest", "environment_digest", "coverage_digest")):
                    raise RuntimeError("Within-variant identity drift; no comparable timing")
                variants[variant] = {"median_wall_seconds": statistics.median(s["wall_seconds"] for s in samples), "samples": samples}
            if variants["baseline"]["samples"][0]["check_ids"] != variants["candidate"]["samples"][0]["check_ids"]:
                raise RuntimeError("Coverage population mismatch")
            results["cases"][case] = variants
    atomic_create(destination, json.dumps(results, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(destination), "cases": list(results["cases"]), "supporting_only": True}))


if __name__ == "__main__":
    main()
