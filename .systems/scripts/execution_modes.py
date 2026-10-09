"""Pure inspection of execution decisions; never executes or grants authority."""
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


class InvalidWork(ValueError):
    pass


ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
ACTIONS = {"read-only", "artifact-write", "implementation", "external", "production",
           "migration", "security", "billing", "credentials", "destructive", "permissions"}
PROFILE_PATH = Path(__file__).resolve().parents[1] / "ai/capabilities/workflow-execution-modes-v1.json"
WORKFLOW_SOURCES = {".systems/ai/core/" + name + ".md" for name in (
    "execution-modes", "autopilot", "owner-decision-checkpoints", "delivery-constraints",
    "permissions", "risk-model", "phase-commit-policy", "quality-review")}
WORKFLOW_SOURCES.update({".systems/scripts/check-execution-modes", ".systems/scripts/lib/execution-modes.py",
    ".systems/ai/templates/autopilot/execution-readiness.template.json",
    ".systems/ai/templates/autopilot/readiness.template.md",
    ".systems/ai/templates/autopilot/state.template.md",
    ".systems/ai/templates/autopilot/task-decisions.template.md"})


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


def resolve_selection(task=None, resumed=None, session=None, project=None, session_id=None):
    """Resolve already verified owner choices; references themselves grant no authority."""
    for choice in (task, resumed, session, project):
        if choice is None:
            continue
        if not isinstance(choice, dict) or set(choice) != {"mode", "scope", "scope_id", "source"}:
            raise InvalidWork("invalid execution selection")
        select_mode(choice["mode"])
        if choice["scope"] not in {"task", "session", "project"}:
            raise InvalidWork("invalid execution selection scope")
        text(choice["scope_id"], "execution scope ID")
        text(choice["source"], "execution selection source")
    for expected, choice in (("task", task), ("session", session), ("project", project)):
        if choice is not None and choice["scope"] != expected:
            raise InvalidWork("execution selection scope mismatch")
    selected = task or resumed
    if selected is None and session is not None:
        if not session_id or session["scope_id"] != session_id:
            raise InvalidWork("session selection does not match current session")
        selected = session
    if selected is None:
        selected = project
    if selected is None:
        return {"mode": "auto", "scope": "task", "scope_id": None, "source": "new-work-default"}
    if selected["scope"] == "session" and selected["scope_id"] != session_id:
        raise InvalidWork("resumed session selection does not match current session")
    return {**selected, "mode": select_mode(selected["mode"])}


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
    aliases = {Path("/tmp"): Path("/private/tmp"), Path("/var"): Path("/private/var")}
    if any(p.is_symlink() and aliases.get(p) != p.resolve() for p in (path, *path.parents)):
        raise InvalidWork("linked JSON input")
    return json.loads(path.read_text(), object_pairs_hook=pairs)


def workflow_profile():
    record = read_json(PROFILE_PATH)
    if not isinstance(record, dict) or set(record) != {
            "contract", "tested_commit", "mode_mapping", "delivery_mapping", "inspector", "sources"}:
        raise InvalidWork("invalid AI System compatibility profile")
    if type(record["contract"]) is not int or record["contract"] != 1 or not re.fullmatch(r"[0-9a-f]{40}", record["tested_commit"]):
        raise InvalidWork("invalid compatibility baseline")
    if record["mode_mapping"] != {"auto": "auto", "human": "human-coop"}:
        raise InvalidWork("unsupported counterpart mode mapping")
    if record["delivery_mapping"] != {"auto-unconstrained": "auto-unbounded"}:
        raise InvalidWork("unsupported counterpart delivery mapping")
    if record["inspector"] != ".systems/scripts/lib/execution-modes.py" or not isinstance(record["sources"], dict) or set(record["sources"]) != WORKFLOW_SOURCES:
        raise InvalidWork("incomplete compatibility source coverage")
    for entry in record["sources"].values():
        if not isinstance(entry, dict) or set(entry) != {"sha256", "mode"} or entry["mode"] not in {"100644", "100755"} or not isinstance(entry["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]):
            raise InvalidWork("invalid compatibility source fingerprint")
    return record


def git_bytes(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.DEVNULL)


def workflow_support(root):
    """Inspect installed source pins; no installation, dispatch or QA claim."""
    result = {"status": "unsupported", "fallback": "installed-local-gates", "reason": "unrecognized Workflow sources",
              "evidence_role": "source inspection; native behavior unverified"}
    aliases = {Path("/tmp"): Path("/private/tmp"), Path("/var"): Path("/private/var")}
    if any(p.is_symlink() and aliases.get(p) != p.resolve() for p in (root, *root.parents)):
        return {**result, "status": "invalid", "reason": "linked workflow root"}
    if not root.is_dir():
        return {**result, "status": "invalid", "reason": "missing workflow root"}
    root = root.resolve()
    try:
        record = workflow_profile()
        try:
            top = Path(git_bytes(root, "rev-parse", "--show-toplevel").decode().strip()).resolve()
            head = git_bytes(root, "rev-parse", "HEAD").decode().strip()
        except subprocess.SubprocessError:
            return {**result, "reason": "missing committed Workflow root"}
        if top != root:
            raise InvalidWork("Workflow root is not an independent Git repository")
        mismatches = []
        for name, entry in record["sources"].items():
            candidate = root / name
            if any(p.is_symlink() for p in [candidate, *candidate.parents] if p != root and p.is_relative_to(root)):
                raise InvalidWork("linked compatibility source")
            tree = git_bytes(root, "ls-tree", "HEAD", "--", name).decode().strip()
            if not tree:
                mismatches.append(name)
                continue
            mode = tree.split()[0]
            if not candidate.is_file():
                raise InvalidWork("missing live compatibility source: " + name)
            live = candidate.read_bytes()
            live_mode = "100755" if candidate.stat().st_mode & 0o111 else "100644"
            if mode != live_mode or live != git_bytes(root, "show", "HEAD:" + name) or live != git_bytes(root, "show", ":" + name):
                raise InvalidWork("uncommitted compatibility source: " + name)
            if mode != entry["mode"] or hashlib.sha256(live).hexdigest() != entry["sha256"]:
                mismatches.append(name)
        if mismatches:
            return {**result, "source_head": head, "mismatched_sources": mismatches}
        return {**result, "status": "source-bound", "fallback": "none", "reason": "reviewed actual Workflow sources match committed, index and live inputs",
                "mode_mapping": record["mode_mapping"], "delivery_mapping": record["delivery_mapping"],
                "source_head": head, "tested_commit": record["tested_commit"],
                "profile_sha256": hashlib.sha256(PROFILE_PATH.read_bytes()).hexdigest()}
    except (OSError, ValueError, TypeError, subprocess.SubprocessError) as error:
        return {**result, "status": "invalid", "reason": str(error)}


def inspect_workflow_state(root, path):
    """Run the verified pure inspector on a frozen copy of its original projection."""
    support = workflow_support(root)
    if support["status"] != "source-bound":
        raise InvalidWork("Workflow state inspection requires source-bound support: " + support["reason"])
    profile = workflow_profile()
    record = read_json(path)
    raw = path.read_bytes()
    if path.read_bytes() != raw:
        raise InvalidWork("Workflow state changed before freeze")
    source = root / profile["inspector"]
    content = source.read_bytes()
    expected = profile["sources"][profile["inspector"]]["sha256"]
    if hashlib.sha256(content).hexdigest() != expected:
        raise InvalidWork("Workflow inspector changed before freeze")
    with tempfile.TemporaryDirectory() as directory:
        frozen = Path(directory)
        inspector, state = frozen / "inspector.py", frozen / "state.json"
        inspector.write_bytes(content)
        state.write_bytes(raw)
        result = subprocess.run([sys.executable, "-I", "-B", str(inspector), "--state", str(state)],
                                capture_output=True, text=True, timeout=15, check=False)
        if result.returncode:
            raise InvalidWork("Workflow rejected original projection: " + result.stderr.strip())
        output = json.loads(result.stdout)
    if workflow_support(root) != support or read_json(path) != record or path.read_bytes() != raw:
        raise InvalidWork("Workflow sources or state changed during inspection")
    if not isinstance(output, dict) or output.get("authority") != "inspection-only":
        raise InvalidWork("unexpected Workflow inspector response")
    execution = record["execution"]
    reverse = {v: k for k, v in support["mode_mapping"].items()}
    selection = {"mode": reverse[execution["mode"]], **{k: execution[k] for k in ("scope", "scope_id", "source")}}
    return {"support": support, "selection": selection, "workflow_readiness": output,
            "state_sha256": hashlib.sha256(raw).hexdigest(),
            "evidence_role": "supporting-only; original Workflow state inspected; approval, isolation and model behavior unverified"}
