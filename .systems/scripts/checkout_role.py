"""Explicit local checkout identity and ownership-safe agent-contract bootstrap."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile

CONFIG = "ai-system.local.json"
TEMPLATE = ".systems/ai/templates/root/AGENTS.template.md"
ROLES = ("management", "development")


def unlinked(root, path):
    relative = path.relative_to(root)
    current = root
    for component in relative.parts:
        current /= component
        if current.is_symlink():
            raise ValueError("Linked bootstrap path: " + str(relative))
    if path.exists() and not path.is_file():
        raise ValueError("Bootstrap path is not a regular file: " + str(relative))


def read_text(root, path, limit=1024 * 1024):
    unlinked(root, path)
    if not path.exists():
        return None
    if path.stat().st_size > limit:
        raise ValueError("Oversized bootstrap input: " + str(path.relative_to(root)))
    return path.read_text(encoding="utf-8")


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate checkout configuration key: " + key)
        result[key] = value
    return result


def configuration(root):
    text = read_text(root, root / CONFIG, 16384)
    if text is None:
        return None
    record = json.loads(text, object_pairs_hook=unique_keys)
    if (not isinstance(record, dict) or set(record) != {"schema_version", "role"}
            or type(record["schema_version"]) is not int or record["schema_version"] != 1
            or record["role"] not in ROLES):
        raise ValueError("Invalid checkout configuration; expected schema_version 1 and role management|development")
    return record


def contract_kind(text):
    if text is None:
        return "missing"
    management = "generated local root agent contract" in text
    workflow = "root AI Workflow entrypoint" in text
    if management and workflow:
        return "conflict"
    if management:
        return "management"
    if workflow:
        return "workflow"
    return "custom" if text.strip() else "empty"


def compatible(role, kind):
    return ((role == "management" and kind in {"management", "missing"})
            or (role == "development" and kind in {"workflow", "custom", "missing"}))


def status(root):
    record = configuration(root)
    kind = contract_kind(read_text(root, root / "AGENTS.md"))
    role = record["role"] if record else "unconfigured"
    valid = record is None or compatible(role, kind)
    return {"role": role, "config": CONFIG, "agents": kind,
            "ready": bool(record and valid and kind != "missing"),
            "conflict": not valid, "workflow_required_in_management_root": False}


def publish(root, path, text, mode, replace=False):
    unlinked(root, path)
    descriptor, name = tempfile.mkstemp(prefix=".bootstrap-", dir=root)
    temp = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temp, mode)
        if replace:
            os.replace(temp, path)
        else:
            os.link(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def bootstrap(root, role=None, refresh=False):
    record = configuration(root)
    if record is None and role is None:
        raise ValueError("Unconfigured checkout; specify --role management|development before writes")
    if record is not None and role is not None and role != record["role"]:
        raise ValueError("Checkout role conflict; role changes require separate explicit reconciliation")
    role = role or record["role"]
    if role not in ROLES:
        raise ValueError("Unknown checkout role")
    if role == "development" and refresh:
        raise ValueError("--refresh-agents is forbidden for development")
    old_agents = read_text(root, root / "AGENTS.md")
    kind = contract_kind(old_agents)
    if not compatible(role, kind):
        raise ValueError("AGENTS role conflict or unrecognized contract; preserve it for explicit review")
    template = None
    if role == "management" and (old_agents is None or refresh):
        template = read_text(root, root / TEMPLATE)
        if contract_kind(template) != "management":
            raise ValueError("Missing or invalid management AGENTS template")
    # Preflight every input/output before publishing either local file.
    if old_agents != read_text(root, root / "AGENTS.md") or record != configuration(root):
        raise ValueError("Bootstrap inputs changed during preflight")
    if record is None:
        publish(root, root / CONFIG,
                json.dumps({"schema_version": 1, "role": role}, indent=2) + "\n", 0o600)
    if template is not None:
        publish(root, root / "AGENTS.md", template, 0o644, replace=old_agents is not None)
    result = status(root)
    result["agents_action"] = ("created" if old_agents is None else "refreshed") if template is not None else "preserved"
    if role == "development" and old_agents is None:
        result["next_action"] = "Provide the approved local development contract; no Workflow installation was performed"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", choices=ROLES, help="Required for first bootstrap; later uses local configuration")
    parser.add_argument("--refresh-agents", action="store_true", help="Refresh a recognized management contract only")
    parser.add_argument("--status", action="store_true", help="Read-only checkout role and local contract readiness")
    args = parser.parse_args()
    if args.status and (args.role or args.refresh_agents):
        parser.error("--status cannot be combined with write options")
    root = Path(__file__).resolve().parents[2]
    try:
        result = status(root) if args.status else bootstrap(root, args.role, args.refresh_agents)
        print(json.dumps(result, indent=2))
        return 1 if result["conflict"] else 0
    except (ValueError, OSError, UnicodeError) as error:
        print("STOP: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
