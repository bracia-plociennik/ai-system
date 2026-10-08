"""Pure inspection of execution decisions; never executes or grants authority."""
import hashlib
import json
import re
import subprocess
from pathlib import Path


class InvalidWork(ValueError):
    pass


ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
ACTIONS = {"read-only", "artifact-write", "implementation", "external", "production",
           "migration", "security", "billing", "credentials", "destructive", "permissions"}
SUPPORT = {"scoped-approval", "dependency-local-blocking", "auto-unconstrained",
           "three-stalled-attempts", "technical-phase-8", "human-material-questions"}


def text(value, label):
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise InvalidWork("missing or invalid " + label)
    return value


def identifiers(values, label):
    if not isinstance(values, list) or any(not isinstance(v, str) or not ID.fullmatch(v) for v in values):
        raise InvalidWork("invalid " + label)
    if len(set(values)) != len(values):
        raise InvalidWork("duplicate " + label)
    return values


def select_mode(requested=None, active=None, resuming=False):
    choices = {"auto": "auto", "auto mode": "auto", "human": "human",
               "human mode": "human", "human coop": "human"}
    if requested is not None:
        if not isinstance(requested, str) or requested.casefold().strip() not in choices:
            raise InvalidWork("unknown execution mode")
        return choices[requested.casefold().strip()]
    if active in {"auto", "human"}:
        return active
    if resuming or active is not None:
        raise InvalidWork("historical mode requires explicit disposition")
    return "auto"


def stalled(attempts):
    counts, seen = {}, {}
    if not isinstance(attempts, list):
        raise InvalidWork("invalid attempts")
    for attempt in attempts:
        if not isinstance(attempt, dict) or set(attempt) != {"cause", "evidence"}:
            raise InvalidWork("invalid attempt")
        cause = text(attempt["cause"], "attempt cause")
        evidence = attempt["evidence"]
        if evidence is not None and (not isinstance(evidence, str) or not re.fullmatch(r"[0-9a-f]{64}", evidence)):
            raise InvalidWork("progress evidence must be a fingerprint or null")
        if evidence and evidence not in seen.get(cause, set()):
            counts[cause] = 0
            seen.setdefault(cause, set()).add(evidence)
        else:
            counts[cause] = counts.get(cause, 0) + 1
    return {cause for cause, count in counts.items() if count >= 3}


def inspect_work(work):
    if not isinstance(work, dict) or work.get("contract") != 1 or type(work.get("contract")) is not int:
        raise InvalidWork("unsupported execution record")
    required = {"contract", "mode", "request_kind", "approval_ref", "dod", "baseline",
                "allowed_actions", "units", "decisions", "attempts", "quality_complete", "no_commit"}
    if set(work) != required:
        raise InvalidWork("incomplete or unknown execution fields")
    mode = select_mode(work["mode"])
    if work["request_kind"] not in {"analysis", "planning", "implementation"}:
        raise InvalidWork("unknown request kind")
    for field in ("quality_complete", "no_commit"):
        if type(work[field]) is not bool:
            raise InvalidWork("invalid " + field)
    text(work["dod"], "DoD")
    text(work["baseline"], "baseline")
    approval = work["approval_ref"]
    if approval is not None:
        text(approval, "approval reference")
    allowed = work["allowed_actions"]
    if not isinstance(allowed, list) or any(not isinstance(v, str) for v in allowed) or len(set(allowed)) != len(allowed):
        raise InvalidWork("invalid allowed actions")
    if set(allowed) - (ACTIONS | {"commit", "merge-main", "push", "phase-8"}):
        raise InvalidWork("unknown allowed action")
    units = work["units"]
    if not isinstance(units, list) or not units:
        raise InvalidWork("empty units")
    by_id = {}
    for unit in units:
        if not isinstance(unit, dict) or set(unit) != {"id", "dependencies", "dependencies_known", "independence_evidence", "resources", "gates_ready", "risk", "action", "state", "completion", "cause"}:
            raise InvalidWork("invalid unit")
        identifiers([unit["id"]], "unit id")
        if unit["id"] in by_id:
            raise InvalidWork("duplicate unit id")
        identifiers(unit["dependencies"], "dependencies")
        if type(unit["dependencies_known"]) is not bool or type(unit["gates_ready"]) is not bool:
            raise InvalidWork("invalid prerequisite evidence flags")
        if unit["risk"] not in {"low", "medium", "high", "critical"}:
            raise InvalidWork("unknown unit risk")
        proof = unit["independence_evidence"]
        if proof is not None and (not isinstance(proof, str) or not re.fullmatch(r"[0-9a-f]{64}", proof)):
            raise InvalidWork("invalid independence evidence fingerprint")
        resources = unit["resources"]
        if not isinstance(resources, list) or any(not isinstance(r, str) or not r or r.startswith("/") or "\\" in r or any(p in {"", ".", ".."} for p in r.split("/")) for r in resources):
            raise InvalidWork("invalid resource claims")
        if len({r.casefold() for r in resources}) != len(resources):
            raise InvalidWork("duplicate resource claim")
        if unit["action"] not in ACTIONS or unit["state"] not in {"pending", "completed", "blocked", "deferred"}:
            raise InvalidWork("invalid unit action/state")
        if unit["cause"] is not None:
            text(unit["cause"], "unit cause")
        if unit["state"] == "completed":
            completion = unit["completion"]
            if not isinstance(completion, dict) or set(completion) != {"baseline", "evidence"} or completion["baseline"] != work["baseline"]:
                raise InvalidWork("stale or missing completion baseline")
            if not isinstance(completion["evidence"], str) or not re.fullmatch(r"[0-9a-f]{64}", completion["evidence"]):
                raise InvalidWork("missing completion evidence")
        elif unit["completion"] is not None:
            raise InvalidWork("completion attached to unfinished unit")
        by_id[unit["id"]] = unit
    visiting, visited = set(), set()

    def visit(uid):
        if uid not in by_id:
            raise InvalidWork("unknown dependency")
        if uid in visiting:
            raise InvalidWork("dependency cycle")
        if uid in visited:
            return
        visiting.add(uid)
        for parent in by_id[uid]["dependencies"]:
            visit(parent)
        visiting.remove(uid)
        visited.add(uid)

    for uid in by_id:
        visit(uid)
    for unit in units:
        if unit["state"] == "completed" and any(by_id[parent]["state"] != "completed" for parent in unit["dependencies"]):
            raise InvalidWork("completed unit has unfinished prerequisite")
    blocked = {}
    for uid, unit in by_id.items():
        action = unit["action"]
        if unit["state"] == "completed" and (
                (action != "read-only" and (not approval or action not in allowed))
                or (work["request_kind"] == "analysis" and action != "read-only")
                or (work["request_kind"] == "planning" and action not in {"read-only", "artifact-write"})):
            raise InvalidWork("completion exceeds approved request scope")
        if (not unit["dependencies_known"] or not unit["independence_evidence"]
                or not unit["gates_ready"] or (action != "read-only" and not unit["resources"])):
            if unit["state"] == "completed":
                raise InvalidWork("completion lacks prerequisite/independence evidence")
            blocked[uid] = "unverified prerequisites or independence"
        if unit["risk"] == "critical":
            if unit["state"] == "completed":
                raise InvalidWork("critical work requires separate human-led evidence")
            blocked[uid] = "human-led critical route"
        if unit["state"] in {"blocked", "deferred"}:
            blocked[uid] = "declared " + unit["state"]
        elif unit["state"] != "completed":
            if action != "read-only" and (not approval or action not in allowed):
                blocked[uid] = "missing scoped approval"
            if work["request_kind"] == "analysis" and action != "read-only":
                blocked[uid] = "analysis-only scope"
            if work["request_kind"] == "planning" and action not in {"read-only", "artifact-write"}:
                blocked[uid] = "planning-only scope"
            if unit["cause"] in stalled(work["attempts"]):
                blocked[uid] = "three stalled attempts"
    queue, auto_choices, ids = [], [], set()
    if not isinstance(work["decisions"], list):
        raise InvalidWork("invalid decisions")
    for decision in work["decisions"]:
        if not isinstance(decision, dict) or set(decision) != {"id", "kind", "units", "state", "recommendation", "alternative", "impact"}:
            raise InvalidWork("invalid decision")
        identifiers([decision["id"]], "decision id")
        if decision["id"] in ids:
            raise InvalidWork("duplicate decision id")
        ids.add(decision["id"])
        identifiers(decision["units"], "decision units")
        if not decision["units"] or set(decision["units"]) - by_id.keys():
            raise InvalidWork("unknown decision unit")
        if decision["kind"] not in {"technical", "proposal", "owner"} or decision["state"] not in {"pending", "resolved"}:
            raise InvalidWork("invalid decision class/state")
        for field in ("recommendation", "alternative", "impact"):
            text(decision[field], "decision " + field)
        if decision["state"] == "resolved":
            continue
        if decision["kind"] != "proposal" and any(by_id[u]["state"] == "completed" for u in decision["units"]):
            raise InvalidWork("completion conflicts with pending decision")
        if mode == "auto" and decision["kind"] == "technical" and approval and all(
                by_id[u]["action"] in {"artifact-write", "implementation"} and u not in blocked for u in decision["units"]):
            auto_choices.append(decision["id"])
        else:
            queue.append(decision)
            if decision["kind"] != "proposal":
                for uid in decision["units"]:
                    if by_id[uid]["state"] == "completed":
                        raise InvalidWork("completion conflicts with pending blocker")
                    blocked[uid] = "pending owner decision " + decision["id"]
    # An unresolved shared resource also blocks apparently unrelated dependents.
    def overlap(left, right):
        a, b = left.casefold(), right.casefold()
        return a == b or a.startswith(b + "/") or b.startswith(a + "/")

    changed = True
    while changed:
        changed = False
        for uid, unit in by_id.items():
            sharing = any(other != uid and (unit["action"] != "read-only" or by_id[other]["action"] != "read-only")
                          and any(overlap(a, b) for a in unit["resources"] for b in by_id[other]["resources"])
                          for other in blocked)
            if uid not in blocked and (any(parent in blocked for parent in unit["dependencies"]) or sharing):
                if unit["state"] == "completed":
                    raise InvalidWork("completed unit depends on blocked work")
                blocked[uid] = "blocked dependency or shared resource"
                changed = True
    auto_choices = [did for did in auto_choices if all(u not in blocked for d in work["decisions"]
                                                     if d["id"] == did for u in d["units"])]
    complete = [uid for uid, unit in by_id.items() if unit["state"] == "completed"]
    ready = [uid for uid, unit in by_id.items() if uid not in blocked and unit["state"] == "pending"
             and all(by_id[p]["state"] == "completed" for p in unit["dependencies"])]
    # These are serial candidates, not a dispatch wave or parallel isolation proof.
    waiting = [uid for uid in by_id if uid not in complete + ready and uid not in blocked]
    all_done = len(complete) == len(units)
    quality = all_done and work["quality_complete"] and not blocked
    return {"mode": mode, "ready": ready, "waiting": waiting, "completed": complete,
            "blocked": blocked, "auto_resolvable": auto_choices, "owner_queue": queue,
            "interaction": "ask-before-dependent-work" if mode == "human" and queue else "queued-at-end" if queue else "none",
            "delivery_default": "auto-unconstrained" if mode == "auto" else "human-discovery",
            "dod_state": "complete" if quality else "needs-quality" if all_done else "incomplete",
            "declared_git_eligibility": {a: bool(approval and quality and a in allowed and not (a == "commit" and work["no_commit"]))
                                         for a in ("commit", "merge-main", "push")},
            "technical_phase_8_eligible": bool(approval and quality and "phase-8" in allowed),
            "final_owner_approval": "awaiting-owner", "evidence_role": "supporting-only; declared metadata is not authority or agent behavior proof"}


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise InvalidWork("duplicate JSON field")
            result[key] = value
        return result
    if path.is_symlink():
        raise InvalidWork("linked JSON input")
    return json.loads(path.read_text(), object_pairs_hook=pairs)


def workflow_support(root):
    """Inspect installed source pins; no installation, dispatch or QA claim."""
    result = {"status": "unsupported", "fallback": "installed-local-gates", "reason": "missing capability",
              "evidence_role": "source inspection; native behavior unverified"}
    relative = ".systems/ai/capabilities/execution-modes-v1.json"
    if root.is_symlink():
        return {**result, "status": "invalid", "reason": "linked workflow root"}
    if not root.is_dir():
        return {**result, "status": "invalid", "reason": "missing workflow root"}
    root = root.resolve()
    path = root / relative
    for candidate in [path, *path.parents]:
        if candidate == root:
            break
        if candidate.is_symlink():
            return {**result, "status": "invalid", "reason": "linked capability path"}
    if not path.exists():
        return result
    try:
        record = read_json(path)
        if set(record) != {"contract", "capability", "behaviors", "sources", "mode_mapping"} or type(record["contract"]) is not int or record["contract"] != 1 or record["capability"] != "execution-modes-v1":
            raise InvalidWork("invalid execution capability")
        mapping = record["mode_mapping"]
        if not isinstance(mapping, dict) or mapping != {"auto": "auto", "human": "human-coop"}:
            raise InvalidWork("unsupported counterpart mode mapping")
        if not isinstance(record["behaviors"], list) or any(not isinstance(v, str) for v in record["behaviors"]) or len(set(record["behaviors"])) != len(record["behaviors"]) or not SUPPORT.issubset(record["behaviors"]):
            raise InvalidWork("incomplete execution semantics")
        if not isinstance(record["sources"], dict) or not record["sources"]:
            raise InvalidWork("missing source bindings")
        required = {".systems/ai/core/execution-modes.md", ".systems/ai/core/autopilot.md", ".systems/ai/core/owner-decision-checkpoints.md", ".systems/ai/core/delivery-constraints.md"}
        if not required.issubset(record["sources"]):
            raise InvalidWork("incomplete source coverage")
        for name, checksum in record["sources"].items():
            if not name.startswith(".systems/") or "\\" in name or any(p in {"", ".", ".."} for p in name.split("/")):
                raise InvalidWork("unsafe capability source")
            candidate = root / name
            if any(p.is_symlink() for p in [candidate, *candidate.parents] if p != root and p.is_relative_to(root)):
                raise InvalidWork("linked capability source")
            if not isinstance(checksum, str) or not re.fullmatch(r"[0-9a-f]{64}", checksum) or not candidate.is_file() or hashlib.sha256(candidate.read_bytes()).hexdigest() != checksum:
                raise InvalidWork("stale capability source")
        head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=False)
        return {**result, "status": "source-bound", "fallback": "none", "reason": "declared semantics and current source pins inspected",
                "mode_mapping": mapping,
                "source_head": head.stdout.strip() if head.returncode == 0 else None,
                "capability_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    except (OSError, ValueError, TypeError) as error:
        return {**result, "status": "invalid", "reason": str(error)}
