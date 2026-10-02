"""Offline behavior tests for validation, eval and advisory-state boundaries."""
import copy
import hashlib
import importlib.machinery
import importlib.util
import json
import os
import signal
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1]
ROOT = SCRIPTS.parents[1]
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT / ".systems/ai/skills/skill-creator/scripts"))
import validation_support as support
import validation_runner as runner
import smoke_assertion as assertion
import eval_freshness
import run_eval
import smoke_fixture
import smoke_coverage as population


def load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    loader.exec_module(module)
    return module


comparison = load("comparison", SCRIPTS / "report-validation-comparison")
discovery = load("discovery", SCRIPTS / "discover-skills")


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout.strip()


def init(root):
    root.mkdir(parents=True, exist_ok=True)
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.email", "fixture@example.invalid")
    git(root, "config", "user.name", "Fixture")


class Fixtures(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="integrity-fixture-")
        self.root = Path(self.temp.name).resolve()

    def tearDown(self):
        self.temp.cleanup()

    def put(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def test_smoke_copy_equivalence_and_independence(self):
        source = self.root / "source"
        init(source)
        script = source / ".systems/scripts/fixture"
        script.parent.mkdir(parents=True)
        script.write_bytes(b"#!/bin/sh\necho fixture\n")
        script.chmod(0o755)
        os.utime(script, ns=(1000000000123456789, 1000000000987654321))
        (source / "README.md").write_text("fixture\n")
        (source / "private-runtime.md").write_text("excluded\n")
        git(source, "add", ".systems", "README.md", "private-runtime.md")
        extra = source / ".systems/extra.md"
        extra.write_text("explicit product addition\n")
        copies = [self.root / "one", self.root / "two"]
        for target in copies:
            target.mkdir()
            names = smoke_fixture.copy_fixture(source, target, [".systems/extra.md"])
            self.assertEqual(names, [".systems/extra.md", ".systems/scripts/fixture", "README.md"])
            copied = target / ".systems/scripts/fixture"
            self.assertEqual(copied.read_bytes(), script.read_bytes())
            self.assertEqual(copied.stat().st_mode, script.stat().st_mode)
            self.assertEqual(copied.stat().st_mtime_ns, script.stat().st_mtime_ns)
            self.assertNotEqual(copied.stat().st_ino, script.stat().st_ino)
            self.assertFalse((target / "private-runtime.md").exists())
        (copies[0] / ".systems/scripts/fixture").write_text("mutated\n")
        self.assertEqual((copies[1] / ".systems/scripts/fixture").read_bytes(), script.read_bytes())

    def test_smoke_copy_invalid_sources_before_any_write(self):
        for mode in ("missing", "linked", "escape", "traversal", "foreign", "secret"):
            with self.subTest(mode=mode):
                source = self.root / mode
                init(source)
                directory = source / ".systems"
                directory.mkdir()
                first = directory / "a.md"
                first.write_text("valid\n")
                last = directory / "z.md"
                last.write_text("last\n")
                git(source, "add", ".systems")
                extra = []
                if mode == "missing":
                    last.unlink()
                elif mode == "linked":
                    last.unlink()
                    last.symlink_to(first)
                elif mode == "escape":
                    outside = self.root / "outside"
                    outside.mkdir()
                    (outside / "x.md").write_text("excluded\n")
                    (directory / "linked").symlink_to(outside, target_is_directory=True)
                    extra = [".systems/linked/x.md"]
                elif mode == "traversal":
                    extra = [".systems/../README.md"]
                elif mode == "secret":
                    (directory / ".env").write_text("excluded fixture\n")
                    extra = [".systems/.env"]
                else:
                    extra = ["private-runtime.md"]
                target = self.root / (mode + "-copy")
                target.mkdir()
                with self.assertRaises(ValueError):
                    smoke_fixture.copy_fixture(source, target, extra)
                self.assertEqual(list(target.iterdir()), [])

    def test_smoke_copy_unsafe_destinations(self):
        source = self.root / "source"
        init(source)
        (source / "README.md").write_text("fixture\n")
        git(source, "add", "README.md")
        filled = self.root / "filled"
        filled.mkdir()
        (filled / "keep").write_text("keep\n")
        linked = self.root / "linked"
        linked.symlink_to(filled, target_is_directory=True)
        inside = source / "inside"
        inside.mkdir()
        for target in (filled, linked, inside):
            with self.assertRaises(ValueError):
                smoke_fixture.copy_fixture(source, target)
        self.assertEqual((filled / "keep").read_text(), "keep\n")

    def test_smoke_bounded_transactions_and_independent_roots(self):
        commands = []
        for index in range(7):
            target = self.root / str(index)
            target.mkdir()
            code = ("import json,os,time; from pathlib import Path; "
                    "start=time.monotonic_ns(); time.sleep(.05); "
                    "end=time.monotonic_ns(); Path('owned').write_text(str(os.getpid())); "
                    "print(json.dumps([start,end,os.getpid()]))")
            commands.append([sys.executable, "-c", "import os; os.chdir(" + repr(str(target)) + "); " + code])
        results = smoke_fixture.run_transactions(commands)
        self.assertEqual(len(results), 7)
        self.assertTrue(all(result.returncode == 0 for result in results))
        intervals = [json.loads(result.stdout) for result in results]
        events = sorted([(start, 1) for start, _, _ in intervals] + [(end, -1) for _, end, _ in intervals])
        active = peak = 0
        for _, change in events:
            active += change
            peak = max(peak, active)
        self.assertLessEqual(peak, 2)
        self.assertEqual(len({pid for _, _, pid in intervals}), 7)
        for index, (_, _, pid) in enumerate(intervals):
            self.assertEqual((self.root / str(index) / "owned").read_text(), str(pid))
        self.assertEqual(smoke_fixture.SUITES, tuple(population.population(ROOT)["suites"]))

    def test_smoke_transactions_drain_failed_batch_without_future_writes(self):
        marker = self.root / "drained"
        forbidden = self.root / "forbidden"
        commands = [[sys.executable, "-c", "import sys; print('expected failure'); sys.exit(7)"],
                    [sys.executable, "-c", "import time; from pathlib import Path; time.sleep(.05); Path(" + repr(str(marker)) + ").write_text('drained')"],
                    [sys.executable, "-c", "from pathlib import Path; Path(" + repr(str(forbidden)) + ").write_text('unsafe')"]]
        results = smoke_fixture.run_transactions(commands)
        self.assertEqual([result.returncode for result in results], [7, 0])
        self.assertTrue(marker.exists())
        self.assertFalse(forbidden.exists())

    def test_typed_rejection_and_complete_ownership(self):
        case = {"exit_code": 1, "diagnostic": "scope rejected", "suite": "quality"}
        assertion.verify(case, 1, "scope rejected: fixture")
        for code, text in [(0, "scope rejected"), (2, "scope rejected"), (1, "wrong failure"),
                           (126, "scope rejected"), (127, "scope rejected"), (143, "scope rejected"),
                           (1, "scope rejected\nModuleNotFoundError")]:
            with self.subTest(code=code, text=text), self.assertRaises(ValueError):
                assertion.verify(case, code, text)
        assertion.complete({"a": case}, "quality", ["a"])
        for observed in ([], ["a", "a"], ["a", "unknown"]):
            with self.assertRaises(ValueError):
                assertion.complete({"a": case}, "quality", observed)

    def test_all_declared_negative_causes_are_specific(self):
        cases = json.loads((SCRIPTS / "smoke/negative-expectations.json").read_text())["cases"]
        self.assertEqual(len(cases), 220)
        for name, case in cases.items():
            self.assertIn(case["exit_code"], (1, 2), name)
            self.assertGreater(len(case["diagnostic"]), 12, name)
            self.assertNotRegex(case["diagnostic"], r"^Invalid records:|^AI_SYSTEM_VALIDATION_RESULT|^Traceback", name)

    def test_evidence_no_clobber_link_and_foreign_owner(self):
        product = self.root / "product"
        init(product)
        target = product / "ai-workflow-workspace/evidence/run.md"
        target.parent.mkdir(parents=True)
        path = support.safe_destination(target, product)
        support.atomic_create(path, "first")
        with self.assertRaises(ValueError):
            support.safe_destination(target, product)
        with self.assertRaises(FileExistsError):
            support.atomic_create(target, "second")
        self.assertEqual(target.read_text(), "first")
        git(product, "add", ".")
        git(product, "commit", "-qm", "fixture")
        target.unlink()
        with self.assertRaises(ValueError):
            support.safe_destination(target, product)
        link = self.root / "link"
        link.symlink_to(target.parent, target_is_directory=True)
        with self.assertRaises(ValueError):
            support.safe_destination(link / "new.md", product)
        foreign = self.root / "foreign"
        init(foreign)
        with self.assertRaises(ValueError):
            support.safe_destination(foreign / "new.md", product)
        with self.assertRaises(ValueError):
            support.safe_destination(product / "README.md", product)

    def test_evidence_directory_identity_change(self):
        parent = self.root / "output"
        parent.mkdir()
        stat = parent.stat()
        parent.rename(self.root / "old")
        parent.mkdir()
        with self.assertRaises(ValueError):
            support.atomic_create(parent / "run.md", "evidence", (stat.st_dev, stat.st_ino))
        self.assertFalse((parent / "run.md").exists())

    def eval_run(self):
        source = self.put("skill/SKILL.md", "synthetic contract")
        plan = {"mode": "manual-review", "target_path": "skill", "evals": [{"id": "e1", "prompt": "sample", "expected_behavior": ["correct"]}]}
        plan_path = self.put("evals.json", json.dumps(plan))
        run = self.root / "run"
        run_eval.create_run(plan_path, run, False, None)
        metadata = eval_freshness.read(run / "e1/eval_metadata.json")
        manifest = eval_freshness.read(run / "run.json")
        grade = {"eval_id": "e1", "configuration": "with_skill", "run_fingerprint": manifest["run_fingerprint"],
                 "metadata_fingerprint": metadata["metadata_fingerprint"], "summary": {"passed": 1, "failed": 0, "total": 1, "pass_rate": 1}}
        output = self.put("run/e1/with_skill/outputs/result.md", "observed result")
        grade["result_fingerprints"] = {"outputs/result.md": hashlib.sha256(output.read_bytes()).hexdigest()}
        grade_path = self.put("run/e1/with_skill/grading.json", json.dumps(grade))
        return source, plan_path, run, grade_path

    def test_eval_stale_source_producer_and_consumer(self):
        source, plan, run, grade = self.eval_run()
        eval_freshness.validate_run(run)
        before = (run / "run.json").read_bytes()
        source.write_text("changed source")
        with self.assertRaisesRegex(ValueError, "Stale"):
            eval_freshness.validate_run(run)
        with self.assertRaisesRegex(ValueError, "Stale"):
            run_eval.create_run(plan, run, True, None)
        self.assertEqual(before, (run / "run.json").read_bytes())
        consumer = subprocess.run([sys.executable, "-B", str(ROOT / ".systems/ai/skills/skill-creator/scripts/aggregate_benchmark.py"), str(run)], capture_output=True, text=True)
        self.assertNotEqual(consumer.returncode, 0)
        self.assertIn("Stale", consumer.stderr)

    def test_eval_plan_membership_metadata_and_orphans(self):
        source = self.put("unsafe-skill/SKILL.md", "synthetic contract")
        unsafe_plan = self.put("unsafe-plan.json", json.dumps({"mode": "manual-review", "target_path": "unsafe-skill", "evals": [{"id": "e1", "prompt": "sample", "expected_behavior": ["correct"]}]}))
        foreign = self.put("foreign-result.md", "must remain unchanged")
        linked = self.root / "unsafe-run/e1/eval_metadata.json"
        linked.parent.mkdir(parents=True)
        linked.symlink_to(foreign)
        with self.assertRaisesRegex(ValueError, "Linked"):
            run_eval.create_run(unsafe_plan, self.root / "unsafe-run", True, None)
        self.assertEqual(foreign.read_text(), "must remain unchanged")
        self.assertFalse((self.root / "unsafe-run/run.json").exists())
        _, plan, run, grade = self.eval_run()
        metadata_path = run / "e1/eval_metadata.json"
        metadata = eval_freshness.read(metadata_path)
        metadata["prompt"] = "tampered"
        metadata["metadata_fingerprint"] = eval_freshness.digest({k: v for k, v in metadata.items() if k != "metadata_fingerprint"})
        metadata_path.write_text(json.dumps(metadata))
        with self.assertRaisesRegex(ValueError, "current plan"):
            eval_freshness.validate_run(run)
        shutil.rmtree(run)
        self.put("run/unknown/config/grading.json", "{}")
        with self.assertRaisesRegex(ValueError, "Orphan"):
            run_eval.create_run(plan, run, True, None)

    def test_eval_changed_output_invalidates_grade(self):
        copied = self.root / "local-scripts"
        copied.mkdir()
        original = ROOT / ".systems/ai/skills/skill-creator/scripts"
        for name in ("run_eval.py", "aggregate_benchmark.py", "eval_freshness.py", "utils.py"):
            shutil.copy2(original / name, copied / name)
        for name in ("run_eval.py", "aggregate_benchmark.py"):
            command = subprocess.run([sys.executable, str(copied / name), "--help"], capture_output=True, text=True)
            self.assertEqual(command.returncode, 0, command.stderr)
        self.assertFalse((copied / "__pycache__").exists())
        _, _, run, _ = self.eval_run()
        (run / "e1/with_skill/outputs/result.md").write_text("changed result")
        with self.assertRaisesRegex(ValueError, "result fingerprints"):
            eval_freshness.validate_run(run)

    def runner_fixture(self, fail=False, slow=False):
        product = self.root / "runner"
        init(product)
        scripts = product / ".systems/scripts"
        scripts.mkdir(parents=True)
        for name in ("validation_runner.py", "validation_support.py", "smoke_coverage.py", "execution_efficiency.py"):
            shutil.copy2(SCRIPTS / name, scripts / name)
        registry = {name: {"dependencies": [], "runtime_capable": False} for name in ("check-privacy-boundary", "check-required-artifacts", "check-smoke")}
        (scripts / "validation-dependencies.json").write_text(json.dumps({"checks": registry}))
        for name in registry:
            text = "#!/bin/sh\nexit 0\n"
            if name == "check-required-artifacts" and fail:
                text = "#!/bin/sh\necho fixture-rejected >&2\nexit 1\n"
            if name == "check-required-artifacts" and slow:
                text = "#!/bin/sh\nsleep 30 &\necho $! > child.pid\nwait\n"
            (scripts / name).write_text(text)
            (scripts / name).chmod(0o755)
        git(product, "add", ".")
        git(product, "commit", "-qm", "fixture")
        # The fixture isolates process lifecycle; use the declared minimal smoke population.
        (scripts / "smoke_coverage.py").write_text('def population(root):\n    return {"fixture": "complete"}\n')
        git(product, "add", ".")
        git(product, "commit", "-qm", "fixture population")
        command = [sys.executable, "-B", str(scripts / "validation_runner.py"), "--standard-checks", "check-privacy-boundary,check-required-artifacts", "--full-smoke-check", "check-smoke"]
        return product, command

    def runner_environment(self):
        return {k: v for k, v in os.environ.items() if k != "AI_SYSTEM_SKIP_SMOKE_TESTS"}

    def tool_path(self, missing):
        directory = self.root / "tools"
        directory.mkdir()
        for name in runner.REQUIRED_TOOLS:
            if name not in missing:
                executable = shutil.which(name)
                self.assertIsNotNone(executable, name)
                (directory / name).symlink_to(executable)
        return str(directory)

    def test_dependency_preflight_stops_before_checks_with_exact_marker(self):
        product, command = self.runner_fixture()
        evidence = self.root / "missing-tools.md"
        env = self.runner_environment()
        env["PATH"] = self.tool_path({"rg"})
        result = subprocess.run(command + ["--profile", "full", "--evidence-file", str(evidence)],
                                capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("Missing validation dependencies: rg", result.stderr)
        self.assertNotIn("Missing system skill reference", result.stdout + result.stderr)
        self.assertNotIn("command not found", result.stdout + result.stderr)
        self.assertNotIn("AI_SYSTEM_VALIDATE_PROGRESS", result.stdout)
        self.assertEqual(result.stdout.count("AI_SYSTEM_VALIDATION_RESULT"), 1)
        record = comparison.read_record(evidence)
        self.assertEqual(record["status"], "failed")
        self.assertEqual(record["exit_code"], 2)
        self.assertEqual(record["smoke_status"], "not-started")
        self.assertEqual(record["checks"], [])
        self.assertTrue(record["supporting_only"])

    def test_missing_git_reports_dependencies_without_unsafe_evidence_write(self):
        product, command = self.runner_fixture()
        evidence = self.root / "unverified-owner.md"
        env = self.runner_environment()
        env["PATH"] = self.tool_path({"git", "rg"})
        result = subprocess.run(command + ["--profile", "full", "--evidence-file", str(evidence)],
                                capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("Missing validation dependencies: git, rg", result.stderr)
        self.assertNotIn("No such file or directory", result.stderr)
        self.assertNotIn("AI_SYSTEM_VALIDATE_PROGRESS", result.stdout)
        self.assertEqual(result.stdout.count("AI_SYSTEM_VALIDATION_RESULT"), 1)
        self.assertIn("status=failed exit_code=2 supporting_only=true smoke=not-started", result.stdout)
        self.assertFalse(evidence.exists())

    def test_dependency_preflight_accepts_available_tools(self):
        env = self.runner_environment()
        env["PATH"] = self.tool_path(set())
        with mock.patch.dict(os.environ, env, clear=True):
            runner.require_tools()

    def test_spor_fixtures_do_not_require_platform_date(self):
        tool = self.put("portable-tools/date", "#!/bin/sh\necho platform-date-must-not-be-used >&2\nexit 99\n")
        tool.chmod(0o755)
        env = self.runner_environment()
        env["PATH"] = str(tool.parent) + os.pathsep + env["PATH"]
        result = subprocess.run([shutil.which("bash"), str(SCRIPTS / "check-spor-v4")],
                                capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("platform-date-must-not-be-used", result.stdout + result.stderr)

    def test_skill_check_missing_rg_is_not_a_contract_finding(self):
        env = self.runner_environment()
        env["PATH"] = self.tool_path({"rg"})
        result = subprocess.run([shutil.which("bash"), str(SCRIPTS / "check-system-skills")],
                                capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("Missing validation dependency: rg (ripgrep)", result.stderr)
        self.assertNotIn("Missing system skill reference", result.stdout + result.stderr)
        self.assertNotIn("command not found", result.stdout + result.stderr)

    def test_skill_check_available_rg_retains_missing_reference_findings(self):
        product = self.root / "skill-product"
        product.mkdir()
        # This test also runs inside smoke roots with no tracked Git inventory.
        shutil.copytree(ROOT / ".systems", product / ".systems")
        for name in ("README.md", "HUMANS.md"):
            shutil.copy2(ROOT / name, product / name)
        command = [shutil.which("bash"), str(product / ".systems/scripts/check-system-skills")]
        result = subprocess.run(command, capture_output=True, text=True, env=self.runner_environment())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        contract = product / ".systems/ai/core/operating-model.md"
        original = contract.read_text()
        self.assertIn("SKILL.md", original)
        contract.write_text(original.replace("SKILL.md", "removed-skill-reference"))
        result = subprocess.run(command, capture_output=True, text=True, env=self.runner_environment())
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("Missing system skill reference in .systems/ai/core/operating-model.md: canonical skill contract",
                      result.stdout)
        self.assertNotIn("Missing validation dependenc", result.stdout + result.stderr)

    def test_lifecycle_success_failure_and_exact_marker(self):
        for failure in (False, True):
            with self.subTest(failure=failure):
                if (self.root / "runner").exists():
                    shutil.rmtree(self.root / "runner")
                product, command = self.runner_fixture(fail=failure)
                evidence = self.root / f"run-{failure}.md"
                result = subprocess.run(command + ["--profile", "full", "--evidence-file", str(evidence)], capture_output=True, text=True, env=self.runner_environment())
                record = comparison.read_record(evidence)
                self.assertEqual(result.stdout.count("AI_SYSTEM_VALIDATION_RESULT"), 1)
                self.assertEqual(record["exit_code"], result.returncode)
                self.assertEqual(record["smoke_status"], "not-started" if failure else "completed")
                self.assertEqual(record["status"], "failed" if failure else "completed")
                self.assertTrue(record["supporting_only"])
                self.assertIn("environment_digest", record)

    def test_timeout_and_interruption_cleanup(self):
        product, command = self.runner_fixture(slow=True)
        for interrupt in (False, True):
            evidence = self.root / f"stop-{interrupt}.md"
            proc = subprocess.Popen(command + ["--profile", "full", "--timeout-seconds", "3", "--evidence-file", str(evidence)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=self.runner_environment())
            if interrupt:
                deadline = time.monotonic() + 5
                while not (product / "child.pid").exists() and time.monotonic() < deadline:
                    time.sleep(.01)
                proc.send_signal(signal.SIGTERM)
            stdout, stderr = proc.communicate(timeout=8)
            record = comparison.read_record(evidence)
            self.assertEqual(proc.returncode, 143 if interrupt else 124, stderr)
            self.assertEqual(record["status"], "interrupted" if interrupt else "timeout")
            self.assertEqual(record["smoke_status"], "not-started")
            self.assertEqual(stdout.count("AI_SYSTEM_VALIDATION_RESULT"), 1)
            pid = int((product / "child.pid").read_text())
            with self.assertRaises(ProcessLookupError):
                os.kill(pid, 0)
            (product / "child.pid").unlink()

    def test_timing_rejects_population_drift_and_partial(self):
        base = {"run_id": "r", "source": {"source_digest": "a"}, "coverage_digest": "c", "environment_digest": "e", "status": "completed", "exit_code": 0,
                "smoke_status": "completed", "duration_ns": 100, "checks": [{"id": "c", "state": "completed", "exit_code": 0, "duration_ns": 50}]}
        paths = []
        for i in range(3):
            record = copy.deepcopy(base)
            record["run_id"] = str(i)
            paths.append(self.put(f"timing-{i}.json", json.dumps(record)))
        records = comparison.validate_group(paths)
        right = copy.deepcopy(records)
        for record in right:
            record["run_id"] += "right"
        comparison.compare(records, right)
        right[0]["coverage_digest"] = "other"
        with self.assertRaises(ValueError):
            comparison.compare(records, right)
        with self.assertRaises(ValueError):
            comparison.validate_group(paths[:2])
        bad = copy.deepcopy(base)
        bad["status"] = "timeout"
        paths[0].write_text(json.dumps(bad))
        with self.assertRaises(ValueError):
            comparison.validate_group(paths)

    def test_scoped_complete_owned_inventory(self):
        product = self.root / "product"
        init(product)
        self.put("product/README.md", "frozen fixture")
        git(product, "add", ".")
        git(product, "commit", "-qm", "fixture")
        workspace = self.root / "workspace"
        record = self.put("workspace/capture-state/work.md", "synthetic state")
        review = self.put("workspace/review.md", "semantic and privacy review")
        sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        manifest = {"scope_contract": 1, "workspace": str(workspace), "owned_root": "capture-state", "inputs": {"capture-state/work.md": sha(record)},
                    "required_checks": ["check-distillation-state"], "semantic_evidence": {"path": "review.md", "sha256": sha(review)},
                    "privacy_evidence": {"path": "review.md", "sha256": sha(review)}, "product_source_digest": support.product_identity(product)["source_digest"]}
        path = self.put("scope.json", json.dumps(manifest))
        registry = json.loads((SCRIPTS / "validation-dependencies.json").read_text())["checks"]
        checks = runner.selected_checks(["check-distillation-state"], registry)
        with mock.patch.object(runner, "ROOT", product):
            self.assertEqual(runner.scope_coverage(path, registry, checks)["eligibility"], "runtime-checkpoint-candidate")
            self.put("workspace/capture-state/unlisted.md", "new")
            with self.assertRaisesRegex(ValueError, "complete owned"):
                runner.scope_coverage(path, registry, checks)
            (workspace / "capture-state/unlisted.md").unlink()
            record.write_text("changed")
            with self.assertRaisesRegex(ValueError, "Stale"):
                runner.scope_coverage(path, registry, checks)
            self.put("product/README.md", "changed source")
            with self.assertRaisesRegex(ValueError, "full validation"):
                runner.scope_coverage(path, registry, checks)

    def test_metadata_discovery_stops_before_body(self):
        path = self.put("SKILL.md", "---\nname: sample\ndescription: Use for a bounded fixture\n---\nBODY MUST NOT BE READ\n")
        self.assertEqual(discovery.metadata(path), {"name": "sample", "description": "Use for a bounded fixture"})
        workspace = self.root / "workspace"
        self.put("workspace/skills/local/SKILL.md", "---\nname: skill-creator\ndescription: Local precedence\n---\nprivate body\n")
        items = discovery.discover(workspace)
        matching = [i for i in items if i["name"] == "skill-creator"]
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0]["layer"], "workspace")
        self.assertTrue(all(i["read"] == "frontmatter-only" for i in items))
        import io
        class ObservedStream(io.StringIO):
            def __next__(self):
                value = super().__next__()
                self.observed.append(value)
                return value
        stream = ObservedStream("---\nname: observed\ndescription: selected trigger\n---\nBODY FORBIDDEN\n")
        stream.observed = []
        with mock.patch.object(Path, "open", return_value=stream):
            discovery.metadata(path)
        self.assertFalse(any("BODY" in line for line in stream.observed))
        self.assertEqual(stream.observed[-1], "---\n")

    def test_dream_identity_and_historical_boundary(self):
        import dream_recommendations as dream
        self.assertIsNone(dream.entries("# Historical report"))
        self.assertEqual(dream.entries("- Recommendation contract: `1`\n## Recommendation Lifecycle\n```json\n[]\n```"), [])
        with self.assertRaises(ValueError):
            dream.entries("- Recommendation contract: `2`")
        self.assertNotIn("implemented", dream.TRANSITIONS["proposed"])
        self.assertIn("reopened", dream.TRANSITIONS["implemented"])

    def test_dream_full_transition_fingerprints_and_inventory(self):
        import dream_recommendations as dream
        workspace = self.root / "workspace"
        item = {"id": "validation-scope-001", "state": "proposed", "summary": "bounded proposal",
                "previous": None, "decision": None, "quality_evidence": None}
        previous = self.put("workspace/dreams/runs/previous/dream-report.md", "- Recommendation contract: `1`\n## Recommendation Lifecycle\n```json\n" + json.dumps([item]) + "\n```\n")
        decision = self.put("workspace/decisions/recommendation.md", "Owner decision: accept the bounded proposal")
        names = [str(p.relative_to(workspace)) for p in (previous, decision)]
        scope_text = "- Scope contract: `1`\n- Policy mode: `narrow-only`\n## Allowed Workspace Sources\n| Source path |\n| --- |\n" + "".join(f"| `{n}` |\n" for n in names)
        scope_text += "## Excluded Workspace Paths\n| Match type | Value | Reason |\n| --- | --- | --- |\n| prefix | dump/incoming/ | raw |\n"
        self.put("workspace/dreams/dreaming-scope.local.md", scope_text)
        header = "- Recommendation contract: `1`\n- Scope contract: `1`\n- Scope policy: `dreams/dreaming-scope.local.md`\n- Scope preflight: `passed`\n- Dream variant: `workspace-artifacts-only`\n## Source Inventory\n| Source path | Source type | Reviewed? | Notes |\n| --- | --- | --- | --- |\n" + "".join(f"| `{n}` | workspace-artifact | yes | approved source |\n" for n in names)
        ref = lambda p: {"path": str(p.relative_to(workspace)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
        item.update(state="accepted", previous=ref(previous), decision=ref(decision))
        report = self.put("workspace/dreams/runs/current/dream-report.md", header + "## Recommendation Lifecycle\n```json\n" + json.dumps([item]) + "\n```\n")
        dream.validate(workspace, report)
        decision.write_text("changed decision")
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            dream.validate(workspace, report)
        decision.write_text("Owner decision: accept the bounded proposal")
        item["state"] = "implemented"
        report.write_text(header + "## Recommendation Lifecycle\n```json\n" + json.dumps([item]) + "\n```\n")
        with self.assertRaisesRegex(ValueError, "transition"):
            dream.validate(workspace, report)

    def test_updater_equal_behind_ahead_diverged(self):
        remote, source, target = self.root / "remote.git", self.root / "source", self.root / "target"
        git(self.root, "init", "--bare", "-q", str(remote))
        init(source)
        scripts = source / ".systems/scripts"
        scripts.mkdir(parents=True)
        for name in ("update-from-upstream", "lib-workspaces"):
            shutil.copy2(SCRIPTS / name, scripts / name)
        git(source, "add", ".")
        git(source, "commit", "-qm", "initial")
        git(source, "remote", "add", "origin", str(remote))
        git(source, "push", "-qu", "origin", "main")
        git(self.root, "clone", "-q", "-b", "main", str(remote), str(target))
        git(target, "config", "user.email", "fixture@example.invalid")
        git(target, "config", "user.name", "Fixture")
        def update():
            return subprocess.run([str(target / ".systems/scripts/update-from-upstream"), "--skip-validation"], capture_output=True, text=True)
        self.assertEqual(update().returncode, 0)
        (source / "remote.txt").write_text("remote")
        git(source, "add", ".")
        git(source, "commit", "-qm", "remote")
        git(source, "push", "-q")
        self.assertEqual(update().returncode, 0)
        self.assertEqual(git(source, "rev-parse", "HEAD"), git(target, "rev-parse", "HEAD"))
        (target / "local.txt").write_text("local")
        git(target, "add", ".")
        git(target, "commit", "-qm", "local")
        head = git(target, "rev-parse", "HEAD")
        result = update()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ahead", result.stdout + result.stderr)
        self.assertEqual(head, git(target, "rev-parse", "HEAD"))
        (source / "another.txt").write_text("different")
        git(source, "add", ".")
        git(source, "commit", "-qm", "diverge")
        git(source, "push", "-q")
        result = update()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("diverged", result.stdout + result.stderr)
        self.assertEqual(head, git(target, "rev-parse", "HEAD"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
