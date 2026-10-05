"""Pure coordination checks; native agent tools remain owned by the orchestrator."""

import copy
import re
import unicodedata
from pathlib import Path, PurePosixPath


class InvalidPlan(ValueError):
    pass


STATES = {"pending", "ready", "running", "submitted", "accepted", "blocked", "failed",
          "cancel-requested", "cancelled"}
FORBIDDEN = {".git", "ai-workflow", "ai-workflow-workspace", "capture-state", "credentials", "secrets"}


def require(condition, reason):
    if not condition:
        raise InvalidPlan(reason)


def text(value, name):
    require(isinstance(value, str) and bool(value.strip()) and not value.startswith("<"), name + " is required")


def safe_path(value, repo=None):
    text(value, "path")
    path = PurePosixPath(value)
    require(not path.is_absolute() and "\\" not in value and not any(ord(c) < 32 for c in value)
            and all(part not in ("", ".", "..") for part in value.split("/")), "unsafe relative path")
    require(not any(unicodedata.normalize("NFC", part).casefold() in FORBIDDEN
                    or part.casefold().startswith(".env") for part in path.parts), "restricted worker path")
    if repo is not None:
        root = Path(repo).resolve(strict=True)
        current = root
        for part in path.parts:
            current /= part
            require(not current.is_symlink(), "worker path contains symlink")
        require(current.resolve().is_relative_to(root), "worker path escapes repository")
    return value


def baseline(value):
    require(isinstance(value, dict), "baseline must be an object")
    require(isinstance(value.get("commit"), str) and re.fullmatch(r"[0-9a-f]{40}", value["commit"]), "invalid baseline commit")
    require(isinstance(value.get("source_digest"), str) and re.fullmatch(r"[0-9a-f]{64}", value["source_digest"]), "invalid source digest")


def positive(value, name):
    require(type(value) is int and value > 0, name + " must be a positive integer")


def occupied(unit):
    return bool(unit["agent_id"]) and not unit["termination_confirmed"]


def conflict(a, b):
    if set(a["resources"]) & set(b["resources"]):
        return True
    if a["mode"] == b["mode"] == "implementation":
        left, right = Path(a["worktree"]), Path(b["worktree"])
        if left.resolve() == right.resolve():
            return True
        try:
            if left.exists() and right.exists() and left.samefile(right):
                return True
        except OSError:
            raise InvalidPlan("worktree identity cannot be established")
    left_paths = [unicodedata.normalize("NFC", p).casefold() for p in a["write_paths"]]
    right_paths = [unicodedata.normalize("NFC", p).casefold() for p in b["write_paths"]]
    return any(x == y or x.startswith(y + "/") or y.startswith(x + "/")
               for x in left_paths for y in right_paths)


def validate_plan(plan, repo=None):
    require(isinstance(plan, dict), "run must be an object")
    require(type(plan.get("contract")) is int and plan["contract"] == 1, "unsupported run contract")
    for name in ("run_id", "coordinator_id", "approval_ref"):
        text(plan.get(name), name)
    baseline(plan.get("baseline"))
    positive(plan.get("runtime_capacity"), "runtime_capacity")
    positive(plan.get("dispatch_count", plan["runtime_capacity"]), "dispatch_count")
    require(plan.get("dispatch_count", plan["runtime_capacity"]) <= plan["runtime_capacity"], "dispatch_count exceeds runtime capacity")
    require(type(plan.get("checkpoint_open")) is bool, "checkpoint_open must be boolean")
    require(type(plan.get("workflow_parallel_supported", False)) is bool, "workflow support must be boolean")
    require(isinstance(plan.get("units"), list), "units must be a list")
    retired = plan.get("retired_attempt_ids", [])
    retired_agents = plan.get("retired_agent_ids", [])
    for name, values in (("attempts", retired), ("agents", retired_agents)):
        require(isinstance(values, list) and all(isinstance(v, str) and v.strip() for v in values)
                and len(values) == len(set(values)), "invalid retired " + name)
    ids, agents, attempts = set(), set(), set()
    for unit in plan["units"]:
        require(isinstance(unit, dict), "unit must be an object")
        text(unit.get("id"), "unit id")
        require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", unit["id"]), "unsafe unit id")
        require(unit["id"] not in ids, "duplicate unit id")
        ids.add(unit["id"])
        for name in ("goal", "dod"):
            text(unit.get(name), name)
        require(isinstance(unit.get("mode"), str) and unit["mode"] in {"read-only", "implementation"}, "invalid execution mode")
        require(isinstance(unit.get("system"), str) and unit["system"] in {"ai-system", "ai-workflow"}, "invalid system")
        require(isinstance(unit.get("status"), str) and unit["status"] in STATES, "invalid unit state")
        for name in ("dependencies", "write_paths", "resources"):
            require(isinstance(unit.get(name), list) and all(isinstance(v, str) and v.strip() for v in unit[name]), "invalid " + name)
            require(len(unit[name]) == len(set(unit[name])), "duplicate " + name)
        for path in unit["write_paths"]:
            safe_path(path, repo)
        if unit["mode"] == "read-only":
            require(not unit["write_paths"], "read-only worker declares writes")
        else:
            require(unit["write_paths"], "implementation requires a write set")
            text(unit.get("worktree"), "implementation worktree")
            tree = unit["worktree"]
            require(Path(tree).is_absolute() and tree == Path(tree).as_posix()
                    and ".." not in Path(tree).parts and not any(ord(c) < 32 for c in tree), "worktree must be absolute and normalized")
        require(type(unit.get("termination_confirmed")) is bool, "termination flag must be boolean")
        for name, seen in (("agent_id", agents), ("attempt_id", attempts)):
            require(name in unit and (unit[name] is None or isinstance(unit[name], str) and unit[name].strip()), "invalid " + name)
            if unit[name] is not None:
                require(unit[name] not in seen, "duplicate " + name)
                seen.add(unit[name])
        require("result" in unit, "result field is required")
        require(unit["result"] is None or isinstance(unit["result"], dict), "invalid result type")
        require(unit["attempt_id"] not in retired, "retired attempt reused")
        require(unit["agent_id"] not in retired_agents, "retired agent reused")
        if unit["status"] in {"pending", "ready", "blocked"}:
            require(unit["agent_id"] is None and unit["attempt_id"] is None and unit["result"] is None, "unstarted unit owns runtime identity or result")
        else:
            require(unit["agent_id"] is not None and unit["attempt_id"] is not None, "started unit lacks runtime identity")
        if unit["status"] in {"running", "cancel-requested"}:
            require(not unit["termination_confirmed"], "live state has confirmed termination")
        if unit["status"] == "cancelled":
            require(unit["termination_confirmed"], "cancelled requires confirmed termination")
        if unit["status"] in {"submitted", "accepted"}:
            result = unit["result"]
            require(isinstance(result, dict), "submitted unit lacks evidence")
            require(result.get("attempt_id") == unit["attempt_id"] and result.get("baseline") == plan["baseline"], "stale worker result")
            text(result.get("test_summary"), "test summary")
            require(isinstance(result.get("findings"), list), "findings must be a list")
            require(isinstance(result.get("evidence"), list) and result["evidence"], "worker evidence is required")
            for item in result["evidence"]:
                require(isinstance(item, dict), "evidence must be an object")
                safe_path(item.get("path"), repo)
                require(isinstance(item.get("sha256"), str) and re.fullmatch(r"[0-9a-f]{64}", item["sha256"]), "invalid evidence fingerprint")
            if unit["status"] == "accepted":
                checks = result.get("verified_checks")
                require(isinstance(checks, list) and all(isinstance(v, str) for v in checks), "invalid verified checks")
                require(result.get("verified_by") == plan["coordinator_id"] and set(checks) >= {"intent", "diff", "tests", "privacy"}, "accepted result lacks coordinator receipt")
                require(not result["findings"], "accepted result has unresolved findings")
    by_id = {u["id"]: u for u in plan["units"]}
    for unit in plan["units"]:
        require(set(unit["dependencies"]) <= ids and unit["id"] not in unit["dependencies"], "missing or self dependency")
        if unit["status"] in {"running", "submitted", "accepted", "cancel-requested"}:
            require(all(by_id[dep]["status"] == "accepted" for dep in unit["dependencies"]), "started unit has unaccepted dependency")
    visited, visiting = set(), set()

    def visit(key):
        require(key not in visiting, "dependency cycle")
        if key in visited:
            return
        visiting.add(key)
        for dep in by_id[key]["dependencies"]:
            visit(dep)
        visiting.remove(key)
        visited.add(key)

    for key in ids:
        visit(key)
    live = [u for u in plan["units"] if occupied(u)]
    require(len(live) <= plan["runtime_capacity"], "active agents exceed runtime capacity")
    if not plan.get("workflow_parallel_supported", False) and any(u["system"] == "ai-workflow" for u in live):
        require(len(live) == 1, "live snapshot bypasses Workflow linear fallback")
    for i, a in enumerate(live):
        for b in live[i + 1:]:
            require(not conflict(a, b), "active write or resource conflict")
    return copy.deepcopy(plan)


def ready_units(plan):
    plan = validate_plan(plan)
    accepted = {u["id"] for u in plan["units"] if u["status"] == "accepted"}
    return [u["id"] for u in plan["units"] if u["status"] in {"pending", "ready"} and set(u["dependencies"]) <= accepted]


def dispatchable_units(plan):
    plan = validate_plan(plan)
    if not plan["checkpoint_open"]:
        return []
    live = [u for u in plan["units"] if occupied(u)]
    capacity = plan["runtime_capacity"] - len(live)
    limit = min(capacity, plan.get("dispatch_count", capacity))
    ready = set(ready_units(plan))
    selected = []
    for unit in plan["units"]:
        if unit["id"] not in ready or len(selected) >= limit:
            continue
        if unit["system"] == "ai-workflow" and not plan.get("workflow_parallel_supported", False):
            if live or selected:
                continue
        if any(u["system"] == "ai-workflow" for u in live + selected) and not plan.get("workflow_parallel_supported", False):
            continue
        if not any(conflict(unit, other) for other in live + selected):
            selected.append(unit)
    return [u["id"] for u in selected]


def transition(plan, event):
    current = validate_plan(plan)
    require(isinstance(event, dict), "event must be an object")
    action = event.get("action")
    require(event.get("baseline") == current["baseline"], "event baseline is stale")
    if action == "reassess-capacity":
        positive(event.get("runtime_capacity"), "runtime_capacity")
        current["runtime_capacity"] = event["runtime_capacity"]
        current["dispatch_count"] = event.get("dispatch_count", event["runtime_capacity"])
        return validate_plan(current)
    if action == "rebase":
        require(not any(occupied(u) for u in current["units"]), "cannot rebase with active workers")
        baseline(event.get("new_baseline"))
        require(not any(u["status"] == "accepted" for u in current["units"]), "accepted outputs require a new run after baseline change")
        current["baseline"] = event["new_baseline"]
        if "new_source_manifest" in event:
            require(isinstance(event["new_source_manifest"], list), "new source manifest must be a list")
            current["source_manifest"] = copy.deepcopy(event["new_source_manifest"])
        current.setdefault("retired_attempt_ids", []).extend(u["attempt_id"] for u in current["units"] if u["attempt_id"])
        current.setdefault("retired_agent_ids", []).extend(u["agent_id"] for u in current["units"] if u["agent_id"])
        for unit in current["units"]:
            unit.update(status="pending", result=None, agent_id=None, attempt_id=None, termination_confirmed=False)
        return validate_plan(current)
    units = {u["id"]: u for u in current["units"]}
    require(isinstance(event.get("unit_id"), str) and event["unit_id"] in units, "unknown unit")
    unit = units[event["unit_id"]]
    if action == "start":
        require(unit["id"] in dispatchable_units(current), "unit is not dispatchable")
        text(event.get("agent_id"), "agent id")
        text(event.get("attempt_id"), "attempt id")
        require(event["attempt_id"] not in current.get("retired_attempt_ids", []), "retired attempt reused")
        require(event["agent_id"] not in current.get("retired_agent_ids", []), "retired agent reused")
        unit.update(status="running", agent_id=event["agent_id"], attempt_id=event["attempt_id"], termination_confirmed=False, result=None)
    else:
        require(event.get("attempt_id") == unit["attempt_id"] and unit["attempt_id"] is not None, "event attempt is stale")
        if action == "submit":
            require(unit["status"] == "running", "only running worker can submit")
            unit.update(status="submitted", result=copy.deepcopy(event.get("result")))
        elif action == "accept":
            require(unit["status"] == "submitted", "only submitted output can be accepted")
            unit["result"].update(verified_by=event.get("verified_by"), verified_checks=event.get("verified_checks", []))
            unit["status"] = "accepted"
        elif action == "fail":
            require(unit["status"] in {"running", "submitted"}, "unit cannot fail from this state")
            unit["status"] = "failed"
        elif action == "cancel":
            require(unit["status"] in {"running", "submitted"}, "unit cannot cancel from this state")
            unit["status"] = "cancel-requested"
        elif action == "terminated":
            require(event.get("worker_stopped") is True and not unit["termination_confirmed"], "termination must be freshly confirmed")
            require(unit["status"] in {"submitted", "accepted", "failed", "cancel-requested", "running"}, "invalid termination state")
            unit["termination_confirmed"] = True
            if unit["status"] == "cancel-requested":
                unit["status"] = "cancelled"
            elif unit["status"] == "running":
                unit["status"] = "failed"
        elif action == "retry":
            require(unit["status"] in {"failed", "cancelled"} and unit["termination_confirmed"], "retry needs confirmed failed/cancelled termination")
            current.setdefault("retired_attempt_ids", []).append(unit["attempt_id"])
            current.setdefault("retired_agent_ids", []).append(unit["agent_id"])
            unit.update(status="pending", agent_id=None, attempt_id=None, termination_confirmed=False, result=None)
        else:
            raise InvalidPlan("unsupported event action")
    return validate_plan(current)
