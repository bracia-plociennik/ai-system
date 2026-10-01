"""Validate source-bound advisory recommendation history, never execute decisions."""
import hashlib
import importlib.machinery
import importlib.util
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
loader = importlib.machinery.SourceFileLoader("dream_scope", str(Path(__file__).with_name("check-dreaming-scope")))
spec = importlib.util.spec_from_loader(loader.name, loader)
scope = importlib.util.module_from_spec(spec)
sys.modules[loader.name] = scope
loader.exec_module(scope)

STATES = {"proposed", "deferred", "accepted", "rejected", "implemented", "reopened", "recurring"}
TRANSITIONS = {"proposed": {"deferred", "accepted", "rejected", "recurring"},
    "deferred": {"deferred", "accepted", "rejected", "recurring"},
    "accepted": {"accepted", "implemented", "deferred", "rejected"},
    "rejected": {"rejected", "reopened"}, "implemented": {"implemented", "reopened", "recurring"},
    "reopened": {"accepted", "deferred", "rejected", "recurring"},
    "recurring": {"accepted", "deferred", "rejected", "recurring"}}


def entries(text):
    declaration = scope.metadata_value(text, "Recommendation contract")
    if not declaration:
        return None
    if declaration != "1":
        raise ValueError("Unsupported Dream recommendation contract")
    match = re.search(r"^## Recommendation Lifecycle\s*\n```json\n(.*?)\n```", text, re.M | re.S)
    if not match:
        raise ValueError("Missing recommendation lifecycle JSON")
    result = json.loads(match[1])
    if not isinstance(result, list):
        raise ValueError("Recommendation lifecycle must be an array")
    return result


def validate(workspace, report):
    workspace, report = Path(workspace).resolve(strict=True), Path(report).resolve(strict=True)
    text = report.read_text()
    items = entries(text)
    if items is None:
        return  # Historical layouts remain immutable; no inferred lifecycle.
    scope.validate_report(workspace, report, True)
    inventory = {path for path, kind, reviewed in scope.parse_inventory(text) if kind != "repo-source" and reviewed == "yes"}
    ids = set()

    def reference(value):
        if not isinstance(value, dict) or set(value) != {"path", "sha256"}:
            raise ValueError("Reference requires exact path and SHA-256")
        name = scope.normalized_relative_path(value["path"], "Recommendation reference")
        if name not in inventory:
            raise ValueError("Recommendation reference must be a reviewed preflight inventory source")
        path = scope.validate_existing_path(workspace, name, "recommendation reference")
        path = workspace / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != value["sha256"]:
            raise ValueError("Stale recommendation reference fingerprint")
        if path.resolve() == report:
            raise ValueError("Recommendation cannot cite itself")
        return path

    for item in items:
        if not isinstance(item, dict) or set(item) != {"id", "state", "summary", "previous", "decision", "quality_evidence"}:
            raise ValueError("Invalid recommendation fields")
        identity, state = item["id"], item["state"]
        if not isinstance(identity, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)+", identity) or identity in ids:
            raise ValueError("Invalid or duplicate recommendation ID")
        ids.add(identity)
        if state not in STATES or not isinstance(item["summary"], str) or not item["summary"].strip():
            raise ValueError("Invalid recommendation state or summary")
        if item["previous"]:
            previous = entries(reference(item["previous"]).read_text())
            matches = [p for p in previous or [] if p.get("id") == identity]
            if len(matches) != 1 or state not in TRANSITIONS.get(matches[0].get("state"), set()):
                raise ValueError("Invalid recommendation history transition")
        elif state in {"implemented", "reopened", "recurring"}:
            raise ValueError("Recommendation state requires previous history")
        if state in {"accepted", "deferred", "rejected", "implemented", "reopened"}:
            reference(item["decision"])
        elif item["decision"]:
            reference(item["decision"])
        if state == "implemented":
            reference(item["quality_evidence"])
        elif item["quality_evidence"]:
            reference(item["quality_evidence"])


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    try:
        validate(args.workspace, args.report)
    except (ValueError, OSError, scope.ScopeError) as exc:
        print(f"Dream recommendation validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
