"""Pure, source-bound finalization projection. Records never grant authority."""
import hashlib
import re
from pathlib import Path

CONTRACT = "task-finalization-v1"


def safe_path(root, relative):
    root = Path(root).absolute()
    rel = Path(relative)
    if rel.is_absolute() or not rel.parts or any(x in ("..", ".") for x in rel.parts):
        raise ValueError("Expected contained relative path")
    target = root / rel
    if any(x.is_symlink() for x in (target, *target.parents)):
        raise ValueError("Symlink not supported")
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError("Path escapes root")
    return target


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_inputs(root, inventory):
    if not isinstance(inventory, dict) or not inventory:
        raise ValueError("Complete input fingerprints required")
    changed = []
    for name, expected in inventory.items():
        path = safe_path(root, name)
        if not isinstance(expected, str) or not re.fullmatch(r"[a-f0-9]{64}", expected):
            raise ValueError("Invalid fingerprint")
        if not path.is_file() or sha(path) != expected:
            changed.append(name)
    return changed


def preview(record, root):
    """Inspect caller evidence, never execute operations or authenticate approval."""
    keys = {"contract", "work_id", "kind", "dod", "approval_reference", "inputs", "steps"}
    if not isinstance(record, dict) or set(record) != keys or record["contract"] != CONTRACT:
        raise ValueError("Unsupported finalization record")
    if record["kind"] not in ("spor", "document", "code"):
        raise ValueError("Unknown adapter")
    for key in ("work_id", "dod", "approval_reference"):
        if not isinstance(record[key], str) or not record[key].strip():
            raise ValueError("Missing work scope")
    steps = record["steps"]
    if not isinstance(steps, list) or not steps:
        raise ValueError("Steps required")
    ids = [x.get("id") for x in steps if isinstance(x, dict)]
    if len(ids) != len(steps) or len(set(ids)) != len(ids) or any(not isinstance(x, str) or not x for x in ids):
        raise ValueError("Unique step identities required")
    lookup = {x["id"]: x for x in steps}
    for step in steps:
        if set(step) != {"id", "depends_on", "status", "evidence"}:
            raise ValueError("Unsupported step fields; commands are not accepted")
        if step["status"] not in ("pending", "running", "succeeded", "failed", "uncertain", "excluded"):
            raise ValueError("Unknown execution state")
        deps = step["depends_on"]
        if not isinstance(deps, list) or len(set(deps)) != len(deps) or any(x not in lookup for x in deps):
            raise ValueError("Invalid dependencies")
        if not isinstance(step["evidence"], dict):
            raise ValueError("Invalid evidence")
        if step["status"] == "succeeded" and not step["evidence"]:
            raise ValueError("Success needs readback evidence")
    visiting, visited, ordered = set(), set(), []
    def visit(name):
        if name in visiting:
            raise ValueError("Dependency cycle")
        if name in visited:
            return
        visiting.add(name)
        for dependency in lookup[name]["depends_on"]:
            visit(dependency)
        visiting.remove(name)
        visited.add(name)
        ordered.append(name)
    for name in ids:
        visit(name)
    changed = check_inputs(root, record["inputs"])
    completed, actionable, blocked = [], [], []
    for step in (lookup[name] for name in ordered):
        state = step["status"]
        if state == "excluded":
            continue
        if state == "succeeded":
            if changed or check_inputs(root, step["evidence"]):
                blocked.append({"id": step["id"], "reason": "stale-input-or-readback"})
            elif any(x not in completed and lookup[x]["status"] != "excluded" for x in step["depends_on"]):
                blocked.append({"id": step["id"], "reason": "dependency-not-completed"})
            else:
                completed.append(step["id"])
        elif changed:
            blocked.append({"id": step["id"], "reason": "inputs-changed"})
        elif state in ("running", "uncertain", "failed"):
            blocked.append({"id": step["id"], "reason": "inspect-before-retry:" + state})
        elif all(x in completed or lookup[x]["status"] == "excluded" for x in step["depends_on"]):
            actionable.append(step["id"])
        else:
            blocked.append({"id": step["id"], "reason": "dependency-not-verified"})
    return {"contract": CONTRACT, "work_id": record["work_id"], "completed": completed,
            "next_steps": actionable, "blocked": blocked, "changed_inputs": changed,
            "status": "ready-for-review" if not actionable and not blocked else "incomplete",
            "permission_granted": False, "formal_closure": False,
            "evidence_role": "supporting-only; reviewer verifies actual provenance and required gates"}
