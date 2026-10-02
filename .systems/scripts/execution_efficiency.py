"""Fail-closed supporting evidence reuse and compact execution records."""
from __future__ import annotations

import hashlib
import hmac
import importlib.metadata
import json
import math
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

from validation_support import InvalidEvidence, contained_file, fingerprint, product_identity

CONTRACT = 1
CATEGORIES = {"product", "runtime-artifact", "integration", "environment"}
CAPABILITIES = {"source-bound-check-reuse", "project-artifact-validation", "bounded-defect",
                "historical-qa-lifecycle", "quality-record-producer", "selective-refresh", "process-timing"}
PHASES = {"discovery-refresh", "implementation", "review", "product-tests", "artifact-work",
          "artifact-rework", "owner-waiting", "publication"}


def read_record(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise InvalidEvidence("Evidence must be an existing regular file")
    text = path.read_text(encoding="utf-8")
    if text.startswith("{"):
        return json.loads(text)
    blocks = re.findall(r"^```json\n(.*?)\n```$", text, re.M | re.S)
    if len(blocks) != 1:
        raise InvalidEvidence("Evidence requires exactly one JSON record")
    return json.loads(blocks[0])


def environment_identity(tools=("bash", "git", "python3", "rg")):
    versions = {}
    for tool in tools:
        executable = shutil.which(tool)
        if executable is None:
            raise InvalidEvidence(f"Missing required tool: {tool}")
        result = subprocess.run([executable, "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode:
            raise InvalidEvidence(f"Cannot identify tool version: {tool}")
        if not result.stdout.strip():
            raise InvalidEvidence(f"Missing tool version output: {tool}")
        versions[tool] = {"path": executable, "version": result.stdout.splitlines()[0],
                          "binary_sha256": hashlib.sha256(Path(executable).read_bytes()).hexdigest()}
    # Values, including possible secrets, are never serialized. Hash all inherited
    # environment inputs: an undeclared environment change cannot silently reuse.
    return {"platform": platform.platform(), "python": sys.version, "tools": versions,
            "python_distributions": sorted((d.metadata.get("Name", ""), d.version) for d in importlib.metadata.distributions()),
            "inherited_environment_digest": fingerprint(dict(os.environ))}


def check_identity(root, check, registry, source, environment, coverage):
    spec = registry.get(check["id"], {})
    declaration = spec.get("inputs", {})
    category = spec.get("category", "environment" if check["id"] == "diff" else "integration")
    if category not in CATEGORIES:
        raise InvalidEvidence("Unknown validation category")
    result = {"category": category, "reuse_eligible": False,
              "reason": "Unknown or incomplete input declaration; execute"}
    if "--workspace" in check["command"]:
        result["reason"] = "Runtime consumer references require fresh execution"
        return result
    if declaration.get("complete") is not True:
        return result
    mode = declaration.get("mode")
    if mode == "product-tree":
        inputs = source["files"]
        directories = sorted(str(p.relative_to(root)) for p in (root / ".systems").rglob("*")
                             if p.is_dir() and not {"__pycache__", ".git"}.intersection(p.relative_to(root).parts))
    elif mode == "files":
        names = declaration.get("paths")
        if not isinstance(names, list) or not names or len(set(names)) != len(names):
            raise InvalidEvidence("Complete file inputs require a unique non-empty inventory")
        inputs = {name: hashlib.sha256(contained_file(root, name).read_bytes()).hexdigest() for name in names}
        directories = []
    else:
        return result
    implementation = {"declaration": spec, "files": {}}
    helpers = [".systems/scripts/" + check["id"], ".systems/scripts/validation_runner.py",
               ".systems/scripts/validation_support.py", ".systems/scripts/execution_efficiency.py",
               ".systems/scripts/validation-dependencies.json", *declaration.get("helpers", [])]
    for name in helpers:
        implementation["files"][name] = hashlib.sha256(contained_file(root, name).read_bytes()).hexdigest()
    identity = {"inputs_digest": fingerprint({"files": inputs, "directories": directories}),
                "implementation_digest": fingerprint(implementation), "environment_digest": fingerprint(environment),
                "coverage_digest": fingerprint(coverage), "parameters_digest": fingerprint(check["command"]),
                "root": str(root.resolve())}
    return {"category": category, "reuse_eligible": True, "reason": "Complete declared inputs",
            "identity": identity, "identity_digest": fingerprint(identity)}


def reuse_key(path):
    path = Path(path)
    if any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file():
        raise InvalidEvidence("Reuse key must be an existing unlinked private file")
    stat = path.stat()
    if stat.st_uid != os.getuid() or stat.st_mode & 0o077:
        raise InvalidEvidence("Reuse key must be owner-only (mode 0600)")
    key = path.read_bytes()
    if len(key) < 32:
        raise InvalidEvidence("Reuse key requires at least 32 bytes")
    return key


def seal_record(record, key=None):
    """Integrity checksum, not a signature or proof of execution authority."""
    unsigned = {k: v for k, v in record.items() if k not in {"record_fingerprint", "record_authentication"}}
    record["record_fingerprint"] = fingerprint(unsigned)
    if key:
        record["record_authentication"] = hmac.new(key, record["record_fingerprint"].encode(), hashlib.sha256).hexdigest()
    return record


def reusable_checks(record, key):
    if not isinstance(record, dict) or record.get("record_fingerprint") != fingerprint(
            {k: v for k, v in record.items() if k not in {"record_fingerprint", "record_authentication"}}):
        raise InvalidEvidence("Reuse evidence integrity mismatch")
    expected = hmac.new(key, record["record_fingerprint"].encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, str(record.get("record_authentication", ""))):
        raise InvalidEvidence("Reuse evidence authentication mismatch")
    if (record.get("record_kind") != "validation-run" or record.get("status") != "completed"
            or record.get("exit_code") != 0 or record.get("supporting_only") is not True
            or not re.fullmatch(r"[0-9a-f]{32}", record.get("run_id", ""))):
        raise InvalidEvidence("Only completed successful supporting validation may reuse")
    checks = record.get("checks")
    if not isinstance(checks, list) or not checks:
        raise InvalidEvidence("Reuse evidence lacks checks")
    indexed = {}
    for check in checks:
        if (not isinstance(check, dict) or check.get("state") not in {"completed", "reused"}
                or check.get("exit_code") != 0 or check.get("id") in indexed):
            raise InvalidEvidence("Incomplete, failed or duplicate reuse check")
        indexed[check["id"]] = check
    return indexed


def reuse_decision(current, previous):
    if not current.get("reuse_eligible"):
        return False, current["reason"]
    if previous is None:
        return False, "No source check evidence"
    old = previous.get("binding", {})
    if old.get("identity_digest") != current["identity_digest"] or old.get("identity") != current["identity"]:
        return False, "Changed inputs, implementation, parameters, environment or coverage"
    return True, "All declared check identities revalidated"


def capability_record(workflow):
    root = Path(workflow)
    path = root / ".systems/ai/capabilities/execution-efficiency-v1.json"
    if any(candidate.is_symlink() for candidate in (path, path.parent, path.parent.parent, path.parent.parent.parent)):
        raise InvalidEvidence("Linked execution-efficiency capability declaration")
    if not path.exists():
        return {"contract": 1, "capabilities": {}, "fallback": "installed-local-gates"}
    contained_file(Path(workflow), ".systems/ai/capabilities/execution-efficiency-v1.json")
    value = read_record(path)
    if (not isinstance(value, dict) or set(value) != {"contract", "capabilities"} or value["contract"] != 1
            or not isinstance(value["capabilities"], dict)
            or set(value["capabilities"]) - CAPABILITIES
            or any(type(v) is not bool for v in value["capabilities"].values())):
        raise InvalidEvidence("Invalid execution-efficiency capability declaration")
    return {**value, "fallback": "installed-local-gates"}


def bounded_defect(request, capabilities=None):
    required = {"risk", "reversible", "known_consumers", "observable_dod", "approved_scope", "regression_evidence", "effects"}
    if set(request) != required or request["risk"] not in {"low", "medium", "high", "critical"}:
        raise InvalidEvidence("Invalid bounded-defect request")
    for field in required - {"risk", "effects"}:
        if type(request[field]) is not bool:
            raise InvalidEvidence("Bounded eligibility requires explicit booleans")
    if not isinstance(request["effects"], list):
        raise InvalidEvidence("Effects must be explicit")
    allowed = (request["risk"] in {"low", "medium"} and not request["effects"]
               and all(request[f] for f in required - {"risk", "effects"}))
    if capabilities is not None and not capabilities.get("bounded-defect", False):
        return {"eligible": False, "route": "installed-local-gates"}
    return {"eligible": allowed, "route": "bounded-defect" if allowed else "full-local-route"}


def refresh_state(root, opened):
    if not isinstance(opened, dict) or not opened:
        raise InvalidEvidence("Refresh requires the actual opened contract inventory")
    changed = []
    for path, digest in opened.items():
        if not re.fullmatch(r"[0-9a-f]{64}", digest or ""):
            raise InvalidEvidence("Invalid opened contract fingerprint")
        if hashlib.sha256(contained_file(root, path).read_bytes()).hexdigest() != digest:
            changed.append(path)
    return {"changed_contracts": changed, "route": "targeted-refresh" if changed else "same-scope-continuation"}


def validate_quality(record, root):
    required = {"contract", "kind", "work_id", "stage", "assessment", "baseline", "approval_reference", "approved_scope",
                "dod", "findings", "semantic_result", "inputs", "evidence", "capture_disposition", "opened_contracts", "timings", "residual_risk"}
    if not isinstance(record, dict) or set(record) != required or record["contract"] != 1 or record["kind"] != "quality-assessment":
        raise InvalidEvidence("Quality record schema mismatch")
    if record["assessment"] not in {"current", "historical", "superseded"}:
        raise InvalidEvidence("Invalid assessment lifecycle")
    if record["stage"] not in {"quality", "checkpoint", "technical-final-check"}:
        raise InvalidEvidence("Invalid execution stage")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", record["work_id"] or ""):
        raise InvalidEvidence("Invalid work ID")
    if not isinstance(record["baseline"], dict) or set(record["baseline"]) != {"head", "source_digest"}:
        raise InvalidEvidence("Assessed baseline requires HEAD and source digest")
    if (not re.fullmatch(r"[0-9a-f]{40}", record["baseline"]["head"] or "")
            or not re.fullmatch(r"[0-9a-f]{64}", record["baseline"]["source_digest"] or "")):
        raise InvalidEvidence("Invalid assessed baseline identity")
    for field in ("approval_reference", "approved_scope", "dod", "capture_disposition", "residual_risk"):
        if not isinstance(record[field], str) or not record[field].strip():
            raise InvalidEvidence(f"Quality record missing {field}")
    if record["semantic_result"] not in {"satisfied", "findings", "blocked"} or not isinstance(record["findings"], list):
        raise InvalidEvidence("Semantic assessment must be supplied by reviewer")
    if record["semantic_result"] == "satisfied" and record["findings"]:
        raise InvalidEvidence("Findings and semantic result conflict")
    for kind in ("inputs", "evidence"):
        entries = record[kind]
        if not isinstance(entries, dict) or not entries:
            raise InvalidEvidence(f"Quality record requires {kind}")
        for name, digest in entries.items():
            actual = contained_file(root, name)
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise InvalidEvidence("Invalid historical input fingerprint")
            if (record["assessment"] == "current" or kind == "evidence") and hashlib.sha256(actual.read_bytes()).hexdigest() != digest:
                raise InvalidEvidence(f"Quality fingerprint mismatch: {name}")
    refresh = refresh_state(root, record["opened_contracts"])
    if record["assessment"] == "current" and refresh["changed_contracts"]:
        raise InvalidEvidence("Current quality has stale opened contracts")
    timing_summary(record["timings"])
    return record


def assessment_state(record, current_source):
    if record["assessment"] == "superseded":
        return "superseded"
    # A changed commit alone need not invalidate identical product evidence.
    return "current" if (record["assessment"] == "current" and record["baseline"]["source_digest"]
                         == current_source["source_digest"]) else "historical"


def timing_summary(intervals):
    if not isinstance(intervals, list):
        raise InvalidEvidence("Timings must be a list; missing telemetry is unknown")
    spans, by_phase, estimates = [], {}, []
    for item in intervals:
        if not isinstance(item, dict) or set(item) != {"phase", "start_seconds", "end_seconds", "measurement", "reason", "inputs"}:
            raise InvalidEvidence("Timing interval schema mismatch")
        if item["phase"] not in PHASES or item["measurement"] not in {"observed", "estimate"}:
            raise InvalidEvidence("Invalid timing phase or measurement")
        for key in ("start_seconds", "end_seconds"):
            if type(item[key]) not in {int, float} or not math.isfinite(item[key]) or item[key] < 0:
                raise InvalidEvidence("Timing values must be finite and nonnegative")
        if item["end_seconds"] < item["start_seconds"] or not item["reason"] or not isinstance(item["inputs"], list):
            raise InvalidEvidence("Timing requires ordered interval and rerun reason/inputs")
        if item["measurement"] == "estimate":
            estimates.append(item)
        else:
            spans.append((item["start_seconds"], item["end_seconds"]))
            by_phase.setdefault(item["phase"], []).append((item["start_seconds"], item["end_seconds"]))
    def union(values):
        total, end = 0, 0
        for start, stop in sorted(values):
            total += max(0, stop - max(start, end))
            end = max(end, stop)
        return total
    return {"observed_wall_seconds": union(spans) if spans else None,
            "phase_seconds": {key: union(value) for key, value in by_phase.items()},
            "estimates": estimates, "unmeasured_phases": sorted(PHASES - set(by_phase))}


def render_quality(record, root):
    validate_quality(record, root)
    return "# Execution Quality Record\n\nScript evidence role: supporting-only. No owner approval or formal PASS is generated.\n\n```json\n" + json.dumps(record, indent=2, sort_keys=True) + "\n```\n"


def build_quality(review, root):
    """Derive mechanical metadata; semantic conclusions must come from the reviewer."""
    supplied = {"work_id", "stage", "approval_reference", "approved_scope", "dod", "findings", "semantic_result",
                "capture_disposition", "timings", "residual_risk", "input_paths", "evidence_paths", "opened_contract_paths"}
    if not isinstance(review, dict) or set(review) != supplied:
        raise InvalidEvidence("Reviewer input schema mismatch; semantic fields cannot be invented")
    def inventory(key):
        names = review[key]
        if not isinstance(names, list) or not names or len(set(names)) != len(names):
            raise InvalidEvidence("Reviewer paths require a unique nonempty inventory")
        return {name: hashlib.sha256(contained_file(root, name).read_bytes()).hexdigest() for name in names}
    source = product_identity(root)
    record = {key: value for key, value in review.items() if not key.endswith("_paths")}
    record.update(contract=1, kind="quality-assessment", assessment="current",
                  baseline={"head": source["head"], "source_digest": source["source_digest"]},
                  inputs=inventory("input_paths"), evidence=inventory("evidence_paths"),
                  opened_contracts=inventory("opened_contract_paths"))
    return validate_quality(record, root)
