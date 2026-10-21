"""Offline adversarial tests for the seven efficiency producers and consumers."""
import copy
import contextlib
import hashlib
import io
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
import execution_efficiency as efficiency
from validation_support import InvalidEvidence, fingerprint


class EfficiencyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="execution-efficiency-")
        self.root = Path(self.temp.name).resolve()
        for name in ("fixture", "validation_runner.py", "validation_support.py", "validation_input_guard.py", "durable_runtime.py", "execution_efficiency.py", "validation-dependencies.json"):
            self.put(".systems/scripts/" + name, "synthetic " + name)
        self.put("input.md", "source")
        self.put("result.md", "observed evidence")
        self.key = b"isolated-synthetic-authentication-key"
        self.registry = {"fixture": {"category": "product", "inputs": {"complete": True, "mode": "files", "paths": ["input.md"]}}}
        self.check = {"id": "fixture", "command": ["fixture", "--synthetic"]}
        self.source = {"files": {"input.md": self.digest("input.md")}}
        self.environment = {"tool": "synthetic-1"}
        self.coverage = {"cases": ["a", "b"]}

    def tearDown(self):
        self.temp.cleanup()

    def put(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def digest(self, name):
        return hashlib.sha256((self.root / name).read_bytes()).hexdigest()

    def binding(self):
        return efficiency.check_identity(self.root, self.check, self.registry, self.source, self.environment, self.coverage)

    def run_record(self):
        return efficiency.seal_record({"record_kind": "validation-run", "run_id": "a" * 32, "status": "completed",
            "exit_code": 0, "supporting_only": True, "checks": [{"id": "fixture", "state": "completed",
            "exit_code": 0, "binding": self.binding()}]}, self.key)

    def quality(self):
        return {"contract": 1, "kind": "quality-assessment", "work_id": "synthetic-defect", "stage": "quality", "assessment": "current",
                "baseline": {"head": "a" * 40, "source_digest": "b" * 64}, "approval_reference": "synthetic accepted plan",
                "approved_scope": "isolated input and renderer", "dod": "expected synthetic duration and rejection",
                "findings": [], "semantic_result": "satisfied", "inputs": {"input.md": self.digest("input.md")},
                "evidence": {"result.md": self.digest("result.md")}, "capture_disposition": "distill reusable decisions",
                "residual_risk": "synthetic evidence does not establish external deployment",
                "opened_contracts": {"input.md": self.digest("input.md")}, "timings": []}

    def test_authenticated_identical_run_reuses(self):
        old = efficiency.reusable_checks(self.run_record(), self.key)["fixture"]
        self.assertEqual(efficiency.reuse_decision(self.binding(), old), (True, "All declared check identities revalidated"))

    def test_every_identity_boundary_invalidates(self):
        old = self.run_record()["checks"][0]
        for dimension in ("source", "implementation", "parameters", "environment", "coverage", "registry"):
            with self.subTest(dimension=dimension):
                saved = (copy.deepcopy(self.check), copy.deepcopy(self.environment), copy.deepcopy(self.coverage), copy.deepcopy(self.registry))
                if dimension == "source":
                    self.put("input.md", "changed")
                elif dimension == "implementation":
                    self.put(".systems/scripts/fixture", "changed")
                elif dimension == "parameters":
                    self.check["command"].append("--changed")
                elif dimension == "environment":
                    self.environment["tool"] = "changed"
                elif dimension == "coverage":
                    self.coverage["cases"].append("c")
                else:
                    self.registry["fixture"]["dependencies"] = ["changed"]
                self.assertFalse(efficiency.reuse_decision(self.binding(), old)[0])
                self.check, self.environment, self.coverage, self.registry = saved
                self.put("input.md", "source")
                self.put(".systems/scripts/fixture", "synthetic fixture")

    def test_unrelated_file_and_commit_do_not_invalidate_explicit_inventory(self):
        old = self.run_record()["checks"][0]
        self.put("unrelated.md", "runtime status changed")
        self.source["head"] = "c" * 40
        self.assertTrue(efficiency.reuse_decision(self.binding(), old)[0])

    def test_unknown_and_runtime_reference_inputs_execute(self):
        self.registry["fixture"]["inputs"]["complete"] = False
        self.assertFalse(self.binding()["reuse_eligible"])

    def test_product_inventory_ignores_bytecode_but_not_scope_directories(self):
        self.registry["fixture"]["inputs"] = {"complete": True, "mode": "product-tree"}
        before = self.binding()
        self.put(".systems/scripts/__pycache__/fixture.pyc", "ephemeral bytecode")
        self.assertEqual(before, self.binding())
        (self.root / ".systems/customer-data").mkdir()
        self.assertNotEqual(before, self.binding())
        self.registry["fixture"]["inputs"]["complete"] = True
        self.check["command"].extend(["--workspace", "synthetic"])
        self.assertFalse(self.binding()["reuse_eligible"])

    def test_failed_partial_interrupted_and_forged_runs_reject(self):
        for status in ("failed", "timeout", "interrupted", "incomplete"):
            record = self.run_record()
            record["status"] = status
            efficiency.seal_record(record, self.key)
            with self.subTest(status=status), self.assertRaises(InvalidEvidence):
                efficiency.reusable_checks(record, self.key)
        for mutation in ("checksum", "wrong-key", "recomputed-checksum", "duplicate", "skipped"):
            record = self.run_record()
            if mutation == "checksum":
                record["run_id"] = "c" * 32
            elif mutation == "recomputed-checksum":
                record["checks"][0]["exit_code"] = 7
                record["record_fingerprint"] = fingerprint({k: v for k, v in record.items() if k not in {"record_fingerprint", "record_authentication"}})
            elif mutation == "duplicate":
                record["checks"].append(copy.deepcopy(record["checks"][0]))
                efficiency.seal_record(record, self.key)
            elif mutation == "skipped":
                record["checks"][0]["state"] = "not-started"
                efficiency.seal_record(record, self.key)
            with self.subTest(mutation=mutation), self.assertRaises(InvalidEvidence):
                efficiency.reusable_checks(record, b"wrong-key" if mutation == "wrong-key" else self.key)

    def test_key_privacy_and_symlink(self):
        path = self.put("key", "a" * 32)
        path.chmod(0o600)
        self.assertEqual(efficiency.reuse_key(path), b"a" * 32)
        path.chmod(0o644)
        with self.assertRaises(InvalidEvidence):
            efficiency.reuse_key(path)
        link = self.root / "link"
        link.symlink_to(path)
        with self.assertRaises(InvalidEvidence):
            efficiency.reuse_key(link)

    def test_generator_shared_schema_and_no_invented_approval(self):
        record = self.quality()
        rendered = efficiency.render_quality(record, self.root)
        self.put("quality.md", rendered)
        self.assertEqual(efficiency.read_record(self.root / "quality.md"), record)
        self.assertIn("No owner approval or formal PASS is generated", rendered)
        for mutation in ("missing", "unknown", "conflicting-findings", "bad-hash", "path-escape", "missing-evidence"):
            bad = self.quality()
            if mutation == "missing":
                del bad["dod"]
            elif mutation == "unknown":
                bad["final-owner-yes"] = True
            elif mutation == "conflicting-findings":
                bad["findings"] = ["unresolved"]
            elif mutation == "bad-hash":
                bad["inputs"]["input.md"] = "0" * 64
            elif mutation == "path-escape":
                bad["inputs"] = {"../input.md": "0" * 64}
            else:
                bad["evidence"] = {}
            with self.subTest(mutation=mutation), self.assertRaises(InvalidEvidence):
                efficiency.validate_quality(bad, self.root)

    def test_producer_computes_metadata_without_semantic_defaults(self):
        record = self.quality()
        review = {key: value for key, value in record.items() if key not in {"contract", "kind", "assessment", "baseline", "inputs", "evidence", "opened_contracts"}}
        review.update(input_paths=["input.md"], evidence_paths=["result.md"], opened_contract_paths=["input.md"])
        source = {"head": "c" * 40, "source_digest": "d" * 64}
        with mock.patch.object(efficiency, "product_identity", return_value=source):
            generated = efficiency.build_quality(review, self.root)
        self.assertEqual(generated["baseline"], source)
        self.assertEqual(generated["inputs"], {"input.md": self.digest("input.md")})
        self.assertEqual(generated["semantic_result"], review["semantic_result"])
        del review["semantic_result"]
        with self.assertRaises(InvalidEvidence):
            efficiency.build_quality(review, self.root)

    def test_history_and_selective_refresh(self):
        record = self.quality()
        original = copy.deepcopy(record)
        self.assertEqual(efficiency.assessment_state(record, {"source_digest": "b" * 64}), "current")
        self.assertEqual(efficiency.assessment_state(record, {"source_digest": "c" * 64}), "historical")
        self.assertEqual(record, original)
        self.put("input.md", "new source")
        self.assertEqual(efficiency.refresh_state(self.root, record["opened_contracts"])["route"], "targeted-refresh")
        with self.assertRaises(InvalidEvidence):
            efficiency.validate_quality(record, self.root)
        record["assessment"] = "historical"
        efficiency.validate_quality(record, self.root)
        self.assertEqual(efficiency.assessment_state(record, {"source_digest": "b" * 64}), "historical")

    def test_bounded_defect_and_older_workflow_fallback(self):
        request = {"risk": "medium", "reversible": True, "known_consumers": True, "observable_dod": True,
                   "approved_scope": True, "regression_evidence": True, "effects": []}
        self.assertTrue(efficiency.bounded_defect(request)["eligible"])
        self.assertFalse(efficiency.bounded_defect(request, {})["eligible"])
        for field in ("reversible", "known_consumers", "observable_dod", "approved_scope", "regression_evidence"):
            bad = {**request, field: False}
            self.assertFalse(efficiency.bounded_defect(bad)["eligible"])
        for risk in ("high", "critical"):
            self.assertFalse(efficiency.bounded_defect({**request, "risk": risk})["eligible"])
        for effect in ("production", "permissions", "migration", "architecture"):
            self.assertFalse(efficiency.bounded_defect({**request, "effects": [effect]})["eligible"])
        self.assertEqual(efficiency.capability_record(self.root)["capabilities"], {})
        self.put(".systems/ai/capabilities/execution-efficiency-v1.json", json.dumps({"contract": 1, "capabilities": {"bounded-defect": True}}))
        self.assertTrue(efficiency.capability_record(self.root)["capabilities"]["bounded-defect"])
        self.put(".systems/ai/capabilities/execution-efficiency-v1.json", json.dumps({"contract": 1, "capabilities": {"bounded-defect": "true"}}))
        with self.assertRaises(InvalidEvidence):
            efficiency.capability_record(self.root)

    def test_broken_capability_links_block_preflight(self):
        directory = self.root / ".systems/ai/capabilities"
        directory.mkdir(parents=True)
        declaration = directory / "execution-efficiency-v1.json"
        declaration.symlink_to(self.root / "missing-capabilities.json")
        with self.assertRaisesRegex(InvalidEvidence, "Linked"):
            efficiency.capability_record(self.root)
        declaration.unlink()
        directory.rmdir()
        directory.symlink_to(self.root / "missing-capabilities-directory")
        with self.assertRaisesRegex(InvalidEvidence, "Linked"):
            efficiency.capability_record(self.root)

    def test_process_timing_union_and_missing_telemetry(self):
        intervals = [{"phase": "product-tests", "start_seconds": 0, "end_seconds": 5, "measurement": "observed",
                      "reason": "fresh regression", "inputs": ["input.md"]},
                     {"phase": "artifact-work", "start_seconds": 2, "end_seconds": 7, "measurement": "observed",
                      "reason": "schema validation", "inputs": ["result.md"]}]
        result = efficiency.timing_summary(intervals)
        self.assertEqual(result["observed_wall_seconds"], 7)
        self.assertIn("owner-waiting", result["unmeasured_phases"])
        self.assertIsNone(efficiency.timing_summary([])["observed_wall_seconds"])
        for value in (float("nan"), float("inf"), -1, True):
            bad = copy.deepcopy(intervals)
            bad[0]["end_seconds"] = value
            with self.subTest(value=value), self.assertRaises(InvalidEvidence):
                efficiency.timing_summary(bad)

    def test_actual_runner_reuse_and_fresh_full_boundary(self):
        product = self.root / "product"
        product.mkdir()
        names = ["validation_runner.py", "validation_support.py", "validation_input_guard.py", "durable_runtime.py", "execution_efficiency.py", "smoke_coverage.py",
                 "validation-dependencies.json", "check-readmes", "check-privacy-boundary"]
        for name in names:
            target = product / ".systems/scripts" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((SCRIPTS / name).read_bytes())
            target.chmod((SCRIPTS / name).stat().st_mode)
        subprocess.run(["git", "init", "-q", "-b", "main", str(product)], check=True)
        key = self.put("reuse.key", "synthetic-key-material-at-least-32-bytes")
        key.chmod(0o600)
        first, second = self.root / "first.md", self.root / "second.md"
        base = [sys.executable, "-B", str(product / ".systems/scripts/validation_runner.py"),
                "--standard-checks", "check-readmes", "--full-smoke-check", "check-validator-smoke-tests",
                "--profile", "scoped", "--checks", "check-readmes", "--reuse-key-file", str(key)]
        env = {**os.environ, "CI": "false"}
        def run(extra, environment=env):
            return subprocess.run(base + extra, cwd=product, env=environment, capture_output=True, text=True)
        result = run(["--evidence-file", str(first)])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        result = run(["--reuse-evidence", str(first), "--evidence-file", str(second)])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        checks = efficiency.read_record(second)["checks"]
        self.assertEqual([c["state"] for c in checks], ["completed", "reused", "reused"])
        self.assertEqual(checks[1]["duration_ns"], 0)
        self.assertTrue(checks[1]["source_run_id"])
        plan = self.root / "plan.md"
        result = run(["--plan-only", "--evidence-file", str(plan)])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(efficiency.read_record(plan)["status"], "planned")
        self.assertTrue(all(c["state"] == "not-started" for c in efficiency.read_record(plan)["checks"]))
        with self.assertRaises(InvalidEvidence):
            efficiency.reusable_checks(efficiency.read_record(plan), self.key)
        # CI cannot opt into reuse, even when the source evidence is valid.
        result = run(["--reuse-evidence", str(first)], {**env, "CI": "true"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires fresh execution", result.stderr)
        # Incomplete input declaration always executes; no heuristic auto-skip.
        registry = product / ".systems/scripts/validation-dependencies.json"
        value = json.loads(registry.read_text())
        value["checks"]["check-readmes"]["inputs"]["complete"] = False
        registry.write_text(json.dumps(value))
        third = self.root / "third.md"
        result = run(["--reuse-evidence", str(first), "--evidence-file", str(third)])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(efficiency.read_record(third)["checks"][-1]["state"], "completed")
        self.assertIn("Unknown or incomplete", efficiency.read_record(third)["checks"][-1]["rerun_reason"])

    def test_plan_publication_failure_returns_failure(self):
        import validation_runner as runner
        args = ["runner", "--profile", "scoped", "--checks", "check-readmes", "--plan-only",
                "--standard-checks", "check-readmes", "--full-smoke-check", "check-validator-smoke-tests",
                "--evidence-file", str(self.root / "failed-plan.md")]
        output = io.StringIO()
        with mock.patch.object(sys, "argv", args), mock.patch.object(runner, "atomic_create", side_effect=OSError("synthetic write failure")), contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            self.assertEqual(runner.main(), 2)
        self.assertIn("status=failed exit_code=2", output.getvalue())
        self.assertFalse((self.root / "failed-plan.md").exists())


if __name__ == "__main__":
    unittest.main()
