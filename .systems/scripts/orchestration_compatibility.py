"""Cooperative protocol checks, never a native execution or approval backend."""

import copy
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import tempfile
import unicodedata


class Blocked(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Blocked(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def relative(value):
    require(isinstance(value, str) and value and "\\" not in value
            and not any(ord(c) < 32 for c in value), "invalid relative path")
    path = PurePosixPath(value)
    require(not path.is_absolute() and path.as_posix() == value
            and all(p not in {".", ".."} for p in value.split("/")), "unsafe relative path")
    return value


def contained(root, name, exists=True):
    relative(name)
    root = Path(root)
    require(root.is_dir() and root.resolve() == root.absolute(), "linked or missing root")
    path = root / name
    cursor = root
    for part in PurePosixPath(name).parts:
        cursor /= part
        require(not cursor.is_symlink(), "linked path")
    require(path.resolve().is_relative_to(root), "path escape")
    if exists:
        require(path.exists(), "missing path: " + name)
    return path


def identity(path):
    value = Path(path).stat()
    return [value.st_dev, value.st_ino]


def fingerprint(path):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), "not a regular file")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root, git_root=False):
    root = Path(root).absolute()
    require(root.is_dir() and root.resolve() == root, "unsafe inventory root")
    entries, total, count = {}, 0, 0

    def walk(directory):
        nonlocal total, count
        for child in sorted(directory.iterdir()):
            name = child.relative_to(root).as_posix()
            relative(name)
            if git_root and name == ".git":
                continue
            require(not child.is_symlink(), "inventory symlink")
            require(child.name != ".git", "nested Git root unsupported")
            require(child.name not in {".env", "credentials", "id_rsa", "id_ed25519"}
                    and not child.name.startswith(".env."), "sensitive inventory input")
            count += 1
            require(count <= 100000, "inventory too large")
            mode = stat.S_IMODE(child.stat().st_mode)
            if child.is_dir():
                entries[name] = {"kind": "directory", "mode": mode}
                walk(child)
            else:
                require(child.is_file(), "special inventory entry")
                total += child.stat().st_size
                require(total <= 64 * 1024 * 1024, "inventory exceeds 64MB")
                entries[name] = {"kind": "file", "mode": mode, "sha256": fingerprint(child)}

    walk(root)
    return {"root_identity": identity(root), "entries": entries}


def overlap(a, b):
    a = unicodedata.normalize("NFC", a).casefold()
    b = unicodedata.normalize("NFC", b).casefold()
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")


def access_conflict(a, b):
    for left, right in (("write_set", "write_set"), ("write_set", "read_set"), ("read_set", "write_set")):
        if any(overlap(x, y) for x in a[left] for y in b[right]):
            return True
    return any(x["name"] == y["name"] and "exclusive" in {x["mode"], y["mode"]}
               for x in a["resources"] for y in b["resources"])


def unit(source, origin="ai-system"):
    require(origin in {"ai-system", "ai-workflow"}, "unknown protocol origin")
    require(isinstance(source, dict), "unit must be an object")
    marker = "contract" if origin == "ai-system" else "schema"
    require(type(source.get(marker)) is int and source[marker] == (2 if origin == "ai-system" else 1), "unsupported unit schema")
    result = {key: copy.deepcopy(source.get(key)) for key in
              ("id", "task_id", "package_id", "slice_id", "goal", "dod", "dependencies", "read_set", "write_set", "resources")}
    require(all(isinstance(result[k], str) and result[k].strip() for k in ("id", "task_id", "goal")), "missing unit/task identity")
    require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", result["id"]), "unsafe unit ID")
    require(isinstance(result["dod"], list) and result["dod"] and all(isinstance(v, str) and v.strip() for v in result["dod"]), "missing DoD")
    for key in ("package_id", "slice_id"):
        require(result[key] is None or isinstance(result[key], str) and result[key].strip(), "invalid subidentity")
    for key in ("dependencies", "read_set", "write_set"):
        values = result[key]
        require(isinstance(values, list) and all(isinstance(v, str) for v in values) and len(values) == len(set(values)), "invalid " + key)
        if key != "dependencies":
            for path in values:
                relative(path)
    require(isinstance(result["resources"], list), "resources required")
    seen = set()
    for claim in result["resources"]:
        require(isinstance(claim, dict) and set(claim) == {"name", "mode"}
                and isinstance(claim["name"], str) and claim["name"]
                and claim["mode"] in {"shared", "exclusive"}, "untyped resource claim")
        require(claim["name"] not in seen, "duplicate resource")
        seen.add(claim["name"])
    result["contract"] = 2
    return result


def allocate(units, capacity, checkpoint, dependency_ready=()):
    require(type(capacity) is int and capacity >= 0, "unknown/invalid capacity")
    require(isinstance(checkpoint, dict) and checkpoint.get("known") is True, "unknown checkpoint")
    limit = checkpoint.get("parent_task_slots")
    require(type(limit) is int and limit > 0, "missing local checkpoint cadence")
    parents = checkpoint.get("active_tasks")
    require(isinstance(parents, list) and len(parents) == len(set(parents)), "invalid parent slots")
    require(len(parents) <= limit, "checkpoint already exceeded")
    parsed = [unit(u) for u in units]
    by_id = {u["id"]: u for u in parsed}
    require(len(by_id) == len(parsed), "duplicate unit")
    visited, active = set(), set()

    def visit(uid):
        require(uid not in active and uid in by_id, "cycle or missing dependency")
        if uid in visited:
            return
        active.add(uid)
        for dep in by_id[uid]["dependencies"]:
            visit(dep)
        active.remove(uid)
        visited.add(uid)

    for uid in by_id:
        visit(uid)
    require(not dependency_ready, "ready IDs alone are not dependency delivery/owning QA proof")
    selected = []
    for candidate in parsed:
        # Ready IDs come from the coordinator's separately reverified delivery/parent gates.
        if not set(candidate["dependencies"]) <= set(dependency_ready):
            continue
        if len(selected) >= capacity or any(access_conflict(candidate, old) for old in selected):
            continue
        task = candidate["task_id"]
        if task not in parents and len(parents) == limit:
            continue
        parents = list(set(parents) | {task})
        selected.append(candidate)
    return {"selected": [u["id"] for u in selected], "parent_tasks": sorted(parents),
            "execution_authorized": False, "supporting_only": True}


def inspect_plan(plan):
    require(isinstance(plan, dict) and type(plan.get("contract")) is int and plan["contract"] == 2, "compatibility plan contract 2 required")
    require(set(plan) == {"contract", "units", "capacity", "checkpoint", "dependency_ready", "execution_mode"}, "unknown/missing compatibility field")
    require(plan["execution_mode"] == "proposal-only", "no verified native dispatch adapter")
    require(plan["dependency_ready"] == [], "dependency gate needs actual delivery/owning QA, not ready IDs")
    return allocate(plan["units"], plan["capacity"], plan["checkpoint"])


def negotiate(workflow_root):
    root = Path(workflow_root).absolute()
    fallback = {"protocol": "unavailable", "parallel_write": False, "fallback": "serial",
                "execution_authorized": False, "supporting_only": True}
    capability = root / ".systems/ai/capabilities/parallel-task-orchestration-v1.json"
    if not capability.exists():
        return fallback
    capability = contained(root, capability.relative_to(root).as_posix())
    data = json.loads(capability.read_text())
    require(data.get("feature") == "parallel-task-orchestration-v1"
            and all(type(data.get(k)) is int and data[k] == 1 for k in
                    ("schema_version", "protocol_version", "manifest_schema", "unit_schema", "result_schema")), "unsupported capability schema")
    pins = data.get("installed_sources_sha256")
    required = {".systems/scripts/lib/parallel-orchestration.py", ".systems/scripts/plan-parallel-work",
                ".systems/scripts/manage-parallel-run", ".systems/ai/templates/orchestration/run.template.json",
                ".systems/ai/templates/orchestration/unit.template.json", ".systems/ai/templates/orchestration/result.template.json"}
    require(isinstance(pins, dict) and set(pins) == required, "incomplete capability population")
    for name, sha in pins.items():
        require(fingerprint(contained(root, name)) == sha, "capability source drift")
    require(isinstance(data.get("native_backend"), dict), "missing native capability boundary")
    # No native adapter has been independently verified in this release, irrespective of metadata.
    return dict(fallback, protocol="source-verified-v1", capability_sha256=fingerprint(capability),
                sources=pins, native_backend="unverified", reason="no verified native enforcement adapter")


def seal_result(unit_value, attempt, worker_root, before, termination, checks):
    assignment = unit(unit_value)
    require(isinstance(attempt, str) and attempt.strip(), "missing attempt")
    require(termination is True, "termination not observed")
    require(isinstance(checks, list) and checks, "required check evidence missing")
    after = inventory(worker_root)
    require(before["root_identity"] == after["root_identity"], "worker root replaced")
    changed = [p for p in set(before["entries"]) | set(after["entries"])
               if before["entries"].get(p) != after["entries"].get(p)]
    require(all(any(p == allowed or p.startswith(allowed + "/") for allowed in assignment["write_set"]) for p in changed), "unexpected worker write")
    for check in checks:
        require(isinstance(check, dict) and set(check) == {"path", "sha256"}
                and fingerprint(contained(worker_root, check["path"])) == check["sha256"], "stale check evidence")
    body = {"unit": assignment, "attempt": attempt, "root": str(Path(worker_root).absolute()),
            "before": before, "after": after, "changed": sorted(changed), "checks": copy.deepcopy(checks)}
    return {"body": body, "sha256": digest(body), "state": "submitted"}


def verify_result(receipt):
    require(isinstance(receipt, dict) and receipt.get("sha256") == digest(receipt.get("body")), "unsealed result")
    body = receipt["body"]
    require(inventory(body["root"]) == body["after"], "worker output drift")
    recomputed = seal_result(body["unit"], body["attempt"], body["root"], body["before"], True, body["checks"])
    require(recomputed["sha256"] == receipt["sha256"], "result coverage drift")
    return body


def integration_prepare(receipt, destination):
    body = verify_result(receipt)
    before = inventory(destination)
    require(before["root_identity"] != body["after"]["root_identity"], "integration destination is worker root")
    intended = copy.deepcopy(before)
    for path in body["changed"]:
        require(before["entries"].get(path) == body["before"]["entries"].get(path), "destination conflict")
        if path in body["after"]["entries"]:
            intended["entries"][path] = body["after"]["entries"][path]
        else:
            intended["entries"].pop(path, None)
    proof = {"receipt": receipt, "destination": str(Path(destination).absolute()), "before": before, "intended": intended}
    return {"body": proof, "sha256": digest(proof)}


def integration_confirm(proof, review):
    require(proof.get("sha256") == digest(proof.get("body")), "integration proof modified")
    verify_result(proof["body"]["receipt"])
    require(set(review) == {"intent", "diff", "tests", "privacy"} and all(v is True for v in review.values()), "incomplete integration review")
    require(inventory(proof["body"]["destination"]) == proof["body"]["intended"], "integration output/identity drift")
    return {"state": "integrated", "proof_sha256": proof["sha256"], "formal_pass": False}


def verify_delivery(receipt, consumer_root, read_set):
    body = verify_result(receipt)
    require(identity(consumer_root) != body["after"]["root_identity"], "mutable producer is not dependency delivery")
    target = inventory(consumer_root)["entries"]
    for path in read_set:
        relative(path)
    expected = {p: v for p, v in body["after"]["entries"].items() if any(overlap(p, q) for q in read_set)}
    actual = {p: v for p, v in target.items() if any(overlap(p, q) for q in read_set)}
    require(expected == actual and expected, "dependency copy missing, extra or stale")
    return {"receipt_sha256": receipt["sha256"], "delivery_sha256": digest(actual)}


def atomic_json(path, value):
    path = Path(path)
    require(path.parent.is_dir() and not path.is_symlink() and path.parent.resolve() == path.parent.absolute(), "unsafe persistence target")
    fd, temp = tempfile.mkstemp(prefix=".pending-", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(value, stream, sort_keys=True, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


class Ledger:
    """Local CAS control; a lock never proves native isolation or distributed ownership."""

    def __init__(self, path, coordinator, workspace):
        self.path = Path(path).absolute()
        workspace = Path(workspace).absolute()
        require(workspace.is_dir() and workspace.resolve() == workspace and not (workspace / ".git").exists(), "ledger needs private selected workspace")
        require(self.path.is_relative_to(workspace), "foreign ledger workspace")
        name = self.path.relative_to(workspace).as_posix()
        slug = r"[a-z0-9]+(?:-[a-z0-9]+)*"
        owner = rf"(?:project-state/{slug}|(?:clients|owned-assets)/{slug}(?:/project-state/{slug})?)/"
        require(re.fullmatch(rf"(?:{owner})?orchestration/runs/{slug}/ledger.json", name), "foreign ledger namespace")
        contained(workspace, self.path.parent.relative_to(workspace).as_posix())
        require(self.path.name == "ledger.json" and self.path.parent.is_dir()
                and self.path.parent.resolve() == self.path.parent and not self.path.is_symlink(), "unsafe ledger target")
        require(isinstance(coordinator, str) and coordinator, "missing coordinator")
        self.coordinator = coordinator

    def read(self):
        require(not self.path.is_symlink(), "linked ledger")
        data = json.loads(self.path.read_text())
        require(data.get("contract") == 2 and data.get("coordinator") == self.coordinator
                and data.get("root_identity") == identity(self.path.parent), "ledger identity drift")
        require(type(data.get("revision")) is int and len(data.get("events", [])) == data["revision"], "ledger revision drift")
        previous = "0" * 64
        for index, event in enumerate(data["events"], 1):
            require(event.get("revision") == index and event.get("previous") == previous
                    and event.get("sha256") == digest({k: v for k, v in event.items() if k != "sha256"}), "event history drift")
            previous = event["sha256"]
        if data["events"]:
            require(data["events"][-1].get("reservations_sha256") == digest(data["reservations"]), "reservation state/history drift")
        else:
            require(data["reservations"] == {}, "unrecorded reservation")
        return data

    def update(self, expected, action, payload):
        lock = self.path.with_suffix(".lock")
        try:
            fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError as error:
            raise Blocked("existing lock requires explicit recovery") from error
        os.close(fd)
        persisted = False
        try:
            if action == "init":
                require(expected == -1 and not self.path.exists(), "ledger already initialized")
                data = {"contract": 2, "coordinator": self.coordinator, "root_identity": identity(self.path.parent),
                        "revision": 0, "events": [], "reservations": {}}
            else:
                data = self.read()
                require(type(expected) is int and expected == data["revision"], "stale ledger revision")
                reservations = data["reservations"]
                attempt = payload.get("attempt")
                require(isinstance(attempt, str) and attempt, "missing attempt")
                if action == "reserve":
                    require(attempt not in reservations and not any(r["state"] == "unknown" for r in reservations.values()), "replay or unknown outcome")
                    assignment = unit(payload["unit"])
                    worker = Path(payload["worker_root"]).absolute()
                    preflight = inventory(worker)
                    require(payload["before"] == preflight, "stale worker preflight")
                    for old in reservations.values():
                        if old["state"] not in {"integrated", "reconciled"}:
                            require(old["before"]["root_identity"] != preflight["root_identity"], "shared worker root")
                        if old["state"] in {"submitted", "accepted", "integrating", "integrated"}:
                            verify_result(old["receipt"])
                    require(not any(r["state"] not in {"integrated", "reconciled"}
                                    and access_conflict(assignment, r["unit"]) for r in reservations.values()), "reserved resource conflict")
                    reservations[attempt] = {"state": "running", "unit": assignment, "termination": False,
                                             "worker_root": str(worker), "before": preflight}
                else:
                    require(attempt in reservations, "foreign attempt")
                    row = reservations[attempt]
                    if action == "submit":
                        require(row["state"] == "running", "invalid submit state")
                        receipt = payload["receipt"]
                        body = verify_result(receipt)
                        require(body["attempt"] == attempt and body["unit"] == row["unit"]
                                and body["before"] == row["before"] and body["root"] == row["worker_root"], "receipt identity mismatch")
                        row.update(state="submitted", receipt=receipt, termination=True)
                    elif action == "accept":
                        require(row["state"] == "submitted", "invalid accept state")
                        verify_result(row["receipt"])
                        review = payload.get("review", {})
                        require(set(review) == {"intent", "diff", "tests", "privacy"} and all(v is True for v in review.values()), "missing acceptance review")
                        row.update(state="accepted", review=review)
                    elif action == "integration-prepare":
                        require(row["state"] == "accepted" and not any(r["state"] in {"integrating", "unknown"} for r in reservations.values()), "integration reserved")
                        row.update(state="integrating", integration=integration_prepare(row["receipt"], payload["destination"]))
                    elif action == "integration-confirm":
                        require(row["state"] == "integrating", "no prepared integration")
                        row["integrated"] = integration_confirm(row["integration"], payload["review"])
                        row["state"] = "integrated"
                    elif action == "unknown":
                        require(row["state"] not in {"integrated", "reconciled"}, "cannot invalidate closed attempt silently")
                        row["state"] = "unknown"
                    elif action == "reconcile":
                        require(row["state"] == "unknown" and payload.get("termination") is True, "unknown termination")
                        proof = row.get("integration")
                        require(proof is not None, "no known integration scope; manual recovery required")
                        current = inventory(proof["body"]["destination"])
                        require(current["root_identity"] == proof["body"]["before"]["root_identity"], "recovery identity drift")
                        before, intended = proof["body"]["before"]["entries"], proof["body"]["intended"]["entries"]
                        require(all(current["entries"].get(p) in (before.get(p), intended.get(p))
                                    for p in set(before) | set(intended) | set(current["entries"])), "unknown external effects")
                        require(payload.get("reviewed_inventory") == current, "missing fresh recovery review")
                        row.update(state="reconciled", termination=True, disposition="abandoned-needs-new-review", actual=current)
                    else:
                        raise Blocked("unsupported ledger action")
                event = {"revision": data["revision"] + 1, "previous": data["events"][-1]["sha256"] if data["events"] else "0" * 64,
                         "action": action, "payload": copy.deepcopy(payload), "reservations_sha256": digest(data["reservations"])}
                event["sha256"] = digest(event)
                data["events"].append(event)
                data["revision"] += 1
            # On persistence ambiguity retain the lock. Never automatically retry an effect.
            persisted = True
            atomic_json(self.path, data)
            persisted = False
            return data
        finally:
            if not persisted:
                lock.unlink()
