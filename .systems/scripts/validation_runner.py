"""Execute declared validators and produce truthful supporting-only evidence."""
from __future__ import annotations

import argparse
import json
import os
import hashlib
import platform
import re
import shutil
import signal
import subprocess
import sys
import time
import uuid
from pathlib import Path

sys.dont_write_bytecode = True
from validation_support import InvalidEvidence, atomic_create, contained_file, fingerprint, git_output, product_identity, safe_destination
from smoke_coverage import population
from validation_input_guard import Guard, InputChanged
from execution_efficiency import check_identity, environment_identity, read_record, reuse_key, reusable_checks, reuse_decision, seal_record

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".systems/scripts"
REGISTRY = SCRIPTS / "validation-dependencies.json"
REQUIRED_TOOLS = ("bash", "git", "python3", "rg")


class PlanningComplete(Exception):
    """Leave execution through the shared evidence-publication and exit path."""


def require_tools():
    missing = [name for name in REQUIRED_TOOLS if shutil.which(name) is None]
    if missing:
        raise InvalidEvidence("Missing validation dependencies: " + ", ".join(missing) +
                              ". Install required tools before validation (rg is provided by ripgrep).")


def selected_checks(names, registry):
    result, visiting = [], set()
    def visit(name):
        if name not in registry or not (SCRIPTS / name).is_file() or not os.access(SCRIPTS / name, os.X_OK):
            raise InvalidEvidence(f"Unknown scoped check: {name}")
        if name in visiting:
            raise InvalidEvidence("Cyclic validation dependency")
        if name in result:
            return
        visiting.add(name)
        for dependency in registry[name]["dependencies"]:
            visit(dependency)
        visiting.remove(name)
        result.append(name)
    for name in names:
        visit(name)
    return result


def scope_coverage(path, registry, selected):
    if not path:
        return {"eligibility": "unverified", "reason": "No source-bound scope manifest"}
    product_paths = (".systems", ".github", "README.md", "HUMANS.md", ".gitignore")
    if not re.fullmatch(r"[0-9a-f]{40}", git_output(ROOT, "rev-parse", "HEAD")):
        raise InvalidEvidence("Runtime eligibility requires a recorded product baseline")
    if git_output(ROOT, "diff", "HEAD", "--name-only", "--", *product_paths) or git_output(ROOT, "ls-files", "--others", "--exclude-standard", "--", *product_paths):
        raise InvalidEvidence("Changed shared product source requires full validation")
    manifest = json.loads(Path(path).read_text())
    required = {"scope_contract", "workspace", "owned_root", "inputs", "required_checks", "semantic_evidence", "privacy_evidence", "product_source_digest"}
    if set(manifest) != required or manifest["scope_contract"] != 1:
        raise InvalidEvidence("Invalid scope manifest fields")
    workspace = Path(manifest["workspace"]).resolve(strict=True)
    owned = manifest["owned_root"]
    if not isinstance(owned, str) or not (re.fullmatch(r"project-state/[a-z0-9]+(?:-[a-z0-9]+)*", owned) or owned in {"capture-state", "checkpoints/blocks"}):
        raise InvalidEvidence("Scope is not a canonical runtime namespace")
    if not isinstance(manifest["inputs"], dict) or not manifest["inputs"]:
        raise InvalidEvidence("Scope manifest requires hashed inputs")
    directory = workspace / owned
    if not directory.is_dir() or directory.is_symlink():
        raise InvalidEvidence("Missing or linked owned namespace")
    inventory = {str(p.relative_to(workspace)) for p in directory.rglob("*") if p.is_file() or p.is_symlink()}
    if set(manifest["inputs"]) != inventory:
        raise InvalidEvidence("Scope manifest must cover the complete owned namespace")
    for name, checksum in manifest["inputs"].items():
        if not name.startswith(owned + "/"):
            raise InvalidEvidence("Scope input belongs to a foreign runtime")
        actual = contained_file(workspace, name)
        if hashlib.sha256(actual.read_bytes()).hexdigest() != checksum:
            raise InvalidEvidence("Stale scope input fingerprint")
    for key in ("semantic_evidence", "privacy_evidence"):
        evidence = manifest[key]
        if not isinstance(evidence, dict) or set(evidence) != {"path", "sha256"}:
            raise InvalidEvidence("Missing semantic/privacy evidence")
        actual = contained_file(workspace, evidence["path"])
        if hashlib.sha256(actual.read_bytes()).hexdigest() != evidence["sha256"]:
            raise InvalidEvidence("Stale semantic/privacy evidence")
    if manifest["product_source_digest"] != product_identity(ROOT)["source_digest"]:
        raise InvalidEvidence("Stale product source in scope manifest")
    required_checks = selected_checks(manifest["required_checks"], registry)
    consumers = set()
    for name in manifest["inputs"]:
        local = name[len(owned) + 1:]
        if (owned == "capture-state" and re.fullmatch(r"[^/]+\.md", local)) or re.fullmatch(r"capture-state/[^/]+\.md", local):
            consumers.add("check-distillation-state")
        elif (owned == "checkpoints/blocks" and re.fullmatch(r"[^/]+\.md", local)) or re.fullmatch(r"checkpoints/blocks/[^/]+\.md", local):
            consumers.add("check-block-checkpoint")
        else:
            raise InvalidEvidence("Undeclared runtime consumer; full profile required")
    if not consumers.issubset(manifest["required_checks"]):
        raise InvalidEvidence("Scope omits a required runtime consumer")
    if not set(required_checks).issubset(selected):
        raise InvalidEvidence("Incomplete scoped dependency coverage")
    if any(not registry[name].get("runtime_capable") for name in manifest["required_checks"]):
        raise InvalidEvidence("Shared source validation requires full profile")
    return {"eligibility": "runtime-checkpoint-candidate", "required_checks": required_checks,
            "scope_fingerprint": fingerprint(manifest), "workspace": str(workspace), "owned_root": owned}


def stop_process(process):
    if process:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            pass
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()


def render(record):
    lines = ["# Validation Execution Record", "", "- Script evidence role: `supporting-only`",
             "- Semantic QA result: not-provided-by-script", "- Final verdict: not-issued-by-script",
             "- Residual risk: command success cannot establish semantic PASS or final acceptance", "",
             "```json", json.dumps(record, indent=2, sort_keys=True), "```", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=["standard", "full", "fast", "scoped"])
    parser.add_argument("--checks", default="")
    parser.add_argument("--evidence-file")
    parser.add_argument("--scope-manifest")
    parser.add_argument("--validation-input-root", action="append", default=[], help="additional complete owned read-input namespace; no writer lock")
    parser.add_argument("--reuse-evidence", help="explicit authenticated successful local source run")
    parser.add_argument("--reuse-key-file", help="owner-only local key; never serialized")
    parser.add_argument("--extra-product-file", action="append", default=[], help="approved new product files for smoke fixtures")
    parser.add_argument("--timeout-seconds", type=float, default=0)
    parser.add_argument("--explain", action="store_true")
    parser.add_argument("--plan-only", action="store_true", help="preflight and print applicability without executing checks")
    parser.add_argument("--require-process-inspection", action="store_true", help="preflight a locally required ps capability")
    parser.add_argument("--default-profile", default="standard")
    parser.add_argument("--standard-checks", required=True)
    parser.add_argument("--full-smoke-check", required=True)
    args = None
    run_id = uuid.uuid4().hex
    start = time.monotonic_ns()
    record = {"run_id": run_id, "record_kind": "validation-run", "supporting_only": True,
              "status": "failed", "checks": [], "smoke_status": "not-started", "coverage": {}, "exit_code": 2}
    destination = None
    destination_parent = None
    process = None
    key = None
    reuse_source = None
    previous_checks = {}
    input_guard = None
    rc = 2
    print(f"AI_SYSTEM_VALIDATE_START run_id={run_id} supporting_only=true", flush=True)
    def interrupt(signum, frame):
        raise InterruptedError(signum)
    old_signals = {s: signal.signal(s, interrupt) for s in (signal.SIGINT, signal.SIGTERM)}
    try:
        args = parser.parse_args()
        profile = args.profile or args.default_profile
        record["profile"] = profile
        if args.timeout_seconds < 0:
            raise InvalidEvidence("Timeout must be nonnegative")
        if args.evidence_file:
            # Evidence ownership checks themselves need Git; never bypass them.
            if shutil.which("git") is None:
                require_tools()
            destination = safe_destination(args.evidence_file, ROOT)
            stat = destination.parent.stat()
            destination_parent = (stat.st_dev, stat.st_ino)
        if args.checks and profile != "scoped":
            raise InvalidEvidence("--checks is valid only with --profile scoped")
        if profile == "scoped" and not args.checks:
            raise InvalidEvidence("--profile scoped requires --checks")
        if args.scope_manifest and profile != "scoped":
            raise InvalidEvidence("--scope-manifest requires scoped profile")
        registry = json.loads(REGISTRY.read_text())["checks"]
        if profile == "scoped":
            names = [n.strip() for n in args.checks.split(",")]
            if any(not n for n in names):
                raise InvalidEvidence("--checks must be a non-empty comma-separated list")
        elif profile == "fast":
            names = ["check-privacy-boundary", "check-required-artifacts"]
        else:
            names = args.standard_checks.split(",")
        names = selected_checks(names, registry)
        if "check-privacy-boundary" not in names:
            names.insert(0, "check-privacy-boundary")
        require_tools()
        if args.require_process_inspection:
            probe = subprocess.run(["ps", "-p", str(os.getpid()), "-o", "pid="], capture_output=True, text=True)
            if probe.returncode:
                raise InvalidEvidence("Required process inspection unavailable; resolve environment before validation")
        if args.reuse_evidence and (profile == "full" or os.environ.get("CI", "").lower() in {"1", "true"}):
            raise InvalidEvidence("Full/CI validation requires fresh execution; reuse is iteration-only")
        if args.reuse_evidence and not args.reuse_key_file:
            raise InvalidEvidence("Reuse requires an explicit private authentication key")
        if args.reuse_key_file:
            key = reuse_key(args.reuse_key_file)
        if args.reuse_evidence:
            reuse_source = read_record(args.reuse_evidence)
            previous_checks = reusable_checks(reuse_source, key)
        record["source"] = product_identity(ROOT)
        environment = environment_identity()
        record["environment_digest"] = fingerprint(environment)
        record["coverage"] = scope_coverage(args.scope_manifest, registry, names) if profile == "scoped" else {"eligibility": "full-required" if profile == "full" else "iteration-only"}
        guarded_roots = list(args.validation_input_root)
        if args.scope_manifest:
            manifest = json.loads(Path(args.scope_manifest).read_text())
            guarded_roots.append(Path(manifest['workspace']) / manifest['owned_root'])
        input_guard = Guard(ROOT, guarded_roots, [args.evidence_file] if args.evidence_file else [])
        record['input_guard'] = {'contract': 'product-v1', 'state': 'started', 'runtime_scopes': len(guarded_roots)}
        skip_smoke = profile == "full" and os.environ.get("AI_SYSTEM_SKIP_SMOKE_TESTS") == "1"
        if profile == "full" and not skip_smoke:
            names.append(args.full_smoke_check)
        record["smoke_status"] = "skipped" if skip_smoke else "not-started" if profile == "full" else "not-applicable"
        if skip_smoke:
            print("AI System validation completed with smoke tests skipped; not final validation evidence without explicit owner acceptance of residual risk.", flush=True)
        commands = [("diff", ["git", "-C", str(ROOT), "diff", "--check"])]
        for name in names:
            command = [str(SCRIPTS / name)]
            if name == args.full_smoke_check:
                for extra in args.extra_product_file:
                    command += ["--extra-product-file", extra]
            if args.scope_manifest and registry.get(name, {}).get("runtime_capable"):
                command += ["--workspace", record["coverage"]["workspace"], "--owned-root", record["coverage"]["owned_root"]]
            commands.append((name, command))
        record["checks"] = [{"id": name, "state": "not-started", "command": command} for name, command in commands]
        record["coverage_digest"] = fingerprint({"checks": [name for name, _ in commands],
            "smoke_population": population(ROOT) if profile == "full" and not skip_smoke else None})
        coverage = {"digest": record["coverage_digest"], "scope": record["coverage"]}
        for check in record["checks"]:
            check["binding"] = check_identity(ROOT, check, registry, record["source"], environment, coverage)
            check["execution"] = "planned"
        record["execution_plan"] = [{"id": c["id"], "category": c["binding"]["category"],
                                     "reason": c["binding"]["reason"]} for c in record["checks"]]
        if args.explain or args.plan_only:
            print(json.dumps({"supporting_only": True, "execution_plan": record["execution_plan"]}), flush=True)
        if args.plan_only:
            raise PlanningComplete()
        for index, check in enumerate(record["checks"]):
            if args.timeout_seconds and (time.monotonic_ns() - start) / 1e9 >= args.timeout_seconds:
                raise subprocess.TimeoutExpired(check["command"], args.timeout_seconds)
            if args.explain:
                print("+ " + " ".join(check["command"]), flush=True)
            print(f"AI_SYSTEM_VALIDATE_PROGRESS run_id={run_id} check={check['id']} index={index + 1}/{len(commands)} supporting_only=true", flush=True)
            check_start = time.monotonic_ns()
            check.update(state="started", parent_id=run_id, start_offset_ns=check_start - start)
            reusable, reason = reuse_decision(check["binding"], previous_checks.get(check["id"]))
            check["rerun_reason"] = reason if reuse_source else "Fresh execution requested"
            if reuse_source and reusable:
                check.update(state="reused", execution="reused", exit_code=0, duration_ns=0,
                             source_run_id=reuse_source["run_id"])
                print(f"AI_SYSTEM_VALIDATE_REUSED run_id={run_id} check={check['id']} source_run_id={reuse_source['run_id']} supporting_only=true", flush=True)
                continue
            check["execution"] = "invalidated" if reuse_source else "executed"
            if check["id"] == args.full_smoke_check:
                record["smoke_status"] = "started"
            process = subprocess.Popen(check["command"], cwd=ROOT, start_new_session=True)
            remaining = max(0.001, args.timeout_seconds - (time.monotonic_ns() - start) / 1e9) if args.timeout_seconds else None
            code = process.wait(timeout=remaining)
            stop_process(process)
            process = None
            check.update(exit_code=code, duration_ns=time.monotonic_ns() - check_start, state="completed" if code == 0 else "failed")
            if check["id"] == args.full_smoke_check:
                record["smoke_status"] = check["state"]
            if code:
                rc = code if code > 0 else 128 - code
                raise RuntimeError(f"Validator failed: {check['id']} (exit {rc})")
        if product_identity(ROOT)["source_digest"] != record["source"]["source_digest"]:
            raise InputChanged("Source changed during validation")
        if args.scope_manifest and scope_coverage(args.scope_manifest, registry, names) != record["coverage"]:
            raise InvalidEvidence("Runtime scope changed during validation")
        for check in record["checks"]:
            if check_identity(ROOT, check, registry, record["source"], environment, coverage) != check["binding"]:
                raise InvalidEvidence("Declared check inputs changed during validation")
        if fingerprint(environment_identity()) != record["environment_digest"]:
            raise InvalidEvidence("Environment changed during validation")
        record["status"] = "completed"
        rc = 0
    except PlanningComplete:
        record["status"] = "planned"
        rc = 0
    except SystemExit as exc:
        rc = int(exc.code)
        record["status"] = "completed" if rc == 0 else "failed"
    except subprocess.TimeoutExpired:
        record["status"] = "timeout"
        rc = 124
    except InterruptedError as exc:
        record["status"] = "interrupted"
        rc = 128 + int(exc.args[0])
    except InputChanged as exc:
        record["error"] = str(exc)
        rc = 75
        print(str(exc), file=sys.stderr, flush=True)
    except (InvalidEvidence, ValueError, OSError, RuntimeError, KeyError) as exc:
        record["error"] = str(exc)
        print(str(exc), file=sys.stderr, flush=True)
    finally:
        stop_process(process)
        if input_guard is not None:
            try:
                record['input_guard'] = input_guard.finish()
            except (InputChanged, OSError, subprocess.SubprocessError) as exc:
                record['input_guard'] = {'contract': 'product-v1', 'state': 'input-changed', 'reason': str(exc)}
                record['status'] = 'failed'
                if rc == 0:
                    rc = 75
                print('VALIDATION_INPUT_GUARD state=input-changed reason=' + str(exc), file=sys.stderr, flush=True)

        for check in record["checks"]:
            if check["state"] == "started":
                check["state"] = record["status"]
                check["duration_ns"] = time.monotonic_ns() - start - check["start_offset_ns"]
            if check["state"] == "not-started":
                check["skip_reason"] = "Run ended before this check"
        if record["smoke_status"] == "started":
            record["smoke_status"] = record["status"]
        record.update(exit_code=rc, duration_ns=time.monotonic_ns() - start)
        seal_record(record, key)
        if destination:
            try:
                safe_destination(destination, ROOT)
                atomic_create(destination, render(record), destination_parent)
            except (OSError, InvalidEvidence) as exc:
                rc = 2
                record.update(status="failed", exit_code=rc, evidence_error=str(exc))
                print(f"Evidence write failed: {exc}", file=sys.stderr)
        for s, handler in old_signals.items():
            signal.signal(s, handler)
        print(f"AI_SYSTEM_VALIDATION_RESULT run_id={run_id} profile={record.get('profile', 'unknown')} status={record['status']} exit_code={rc} supporting_only=true smoke={record['smoke_status']}", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
