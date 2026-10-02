#!/usr/bin/env python3
"""Strict local work-evidence v1 contracts. Sources are data, never instructions."""
from __future__ import annotations

import hashlib
import json
import re
import uuid
from datetime import date, datetime, timezone
from pathlib import Path, PurePosixPath
from zoneinfo import ZoneInfo

VERSION = 1
ACTUAL_BASES = {"measured", "owner-confirmed"}
STATUSES = {"done", "partial", "blocked", "waiting", "unknown"}
FORBIDDEN_PARTS = {
    ".git", ".aws", ".ssh", ".env", "private-tax", "credentials",
    "secrets", "attachments", "dump", "raw-check-in", "working-dump",
}
ID_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]{0,95}\Z")
SHA_PATTERN = re.compile(r"[a-f0-9]{64}\Z")
MAX_SOURCE_BYTES = 2 * 1024 * 1024


class EvidenceError(ValueError):
    """Safe diagnostic: no input values or source content in messages."""

    def __init__(self, category, field="record"):
        self.category = category
        self.field = field
        super().__init__(f"{category}: {field}")


def require(condition, category, field):
    if not condition:
        raise EvidenceError(category, field)


def shape(value, required, optional=(), field="record"):
    require(isinstance(value, dict), "invalid-shape", field)
    require(set(required) <= set(value), "missing-field", field)
    require(set(value) <= set(required) | set(optional), "unsupported-field", field)


def version(value):
    require(type(value.get("schema_version")) is int and value["schema_version"] == VERSION,
            "unsupported-version", "schema_version")


def identifier(value, field):
    require(isinstance(value, str) and ID_PATTERN.fullmatch(value), "invalid-identity", field)
    return value


def uuid_id(value, field):
    try:
        require(isinstance(value, str) and str(uuid.UUID(value)) == value,
                "invalid-identity", field)
    except (ValueError, TypeError, AttributeError):
        raise EvidenceError("invalid-identity", field) from None
    return value


def sha(value, field):
    require(isinstance(value, str) and SHA_PATTERN.fullmatch(value), "invalid-hash", field)
    return value


def iso_date(value, field):
    try:
        require(isinstance(value, str) and date.fromisoformat(value).isoformat() == value,
                "invalid-date", field)
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        raise EvidenceError("invalid-date", field) from None


def instant(value, field, zone=None):
    try:
        result = datetime.fromisoformat(value)
        require(result.tzinfo is not None and result.utcoffset() is not None,
                "offset-required", field)
        require(result.microsecond == 0, "fractional-time", field)
        if zone:
            localized = result.astimezone(ZoneInfo(zone))
            require(localized.replace(tzinfo=None) == result.replace(tzinfo=None)
                    and localized.utcoffset() == result.utcoffset(),
                    "timezone-offset-conflict", field)
        return result
    except (ValueError, TypeError, KeyError):
        raise EvidenceError("invalid-timestamp", field) from None


def text(value, field, limit=10000, empty=False):
    require(isinstance(value, str) and (empty or bool(value.strip()))
            and len(value) <= limit and "\x00" not in value,
            "invalid-text", field)
    return value


def choice(value, allowed, field):
    require(isinstance(value, str) and value in allowed, "invalid-choice", field)
    return value


def seconds(value, field, nullable=False):
    require((nullable and value is None) or (type(value) is int and value >= 0),
            "invalid-duration", field)
    return value


def canonical_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                       allow_nan=False) + "\n").encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    def unique_pairs(pairs):
        result = {}
        for key, val in pairs:
            require(key not in result, "duplicate-key", "json")
            result[key] = val
        return result
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"),
                          object_pairs_hook=unique_pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(EvidenceError("nonfinite", "json")))
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise EvidenceError("unreadable-json", "source") from None


def safe_path(root, relative, *, must_exist=True):
    require(isinstance(relative, str) and "\\" not in relative,
            "unsafe-path", "relative_path")
    part = PurePosixPath(relative)
    require(not part.is_absolute() and bool(part.parts)
            and all(p not in {"", ".", ".."} for p in part.parts),
            "unsafe-path", "relative_path")
    require(relative == part.as_posix(), "unsafe-path", "relative_path")
    lowered = {p.lower() for p in part.parts}
    require(not lowered & FORBIDDEN_PARTS
            and not any(p.startswith(".env") or p.endswith((".pem", ".key", ".sql", ".heic"))
                        or "credential" in p or "secret" in p for p in lowered),
            "forbidden-source", "relative_path")
    root = Path(root).resolve(strict=True)
    candidate = root.joinpath(*part.parts)
    # Reject all symlink components, including in-root symlinks, to avoid alias races.
    current = root
    for component in part.parts:
        current = current / component
        require(not current.is_symlink(), "symlink-source", "relative_path")
    resolved = candidate.resolve(strict=must_exist)
    require(resolved.is_relative_to(root), "root-escape", "relative_path")
    if must_exist:
        require(resolved.is_file() and resolved.stat().st_size <= MAX_SOURCE_BYTES,
                "unsupported-source", "relative_path")
    return resolved


def validate_config(config, workspace=None):
    shape(config, {"schema_version", "workspace_id", "source_roots", "ledger_roots"},
          {"timezone", "report_policy", "editorial_policy"})
    version(config)
    identifier(config["workspace_id"], "workspace_id")
    require(isinstance(config["source_roots"], dict), "invalid-shape", "source_roots")
    for alias, root in config["source_roots"].items():
        identifier(alias, "root_alias")
        require(isinstance(root, str) and Path(root).is_absolute()
                and Path(root).is_dir() and not Path(root).is_symlink(),
                "invalid-root", "source_roots")
        require(not set(p.lower() for p in Path(root).parts) & FORBIDDEN_PARTS,
                "forbidden-source", "source_roots")
    require(isinstance(config["ledger_roots"], list) and bool(config["ledger_roots"]),
            "missing-root", "ledger_roots")
    for root in config["ledger_roots"]:
        require(isinstance(root, str) and Path(root).is_absolute() and Path(root).is_dir()
                and not Path(root).is_symlink(), "invalid-root", "ledger_roots")
        if workspace:
            require(Path(root).resolve().is_relative_to(Path(workspace).resolve()),
                    "owner-root-conflict", "ledger_roots")
    require(len(set(config["ledger_roots"])) == len(config["ledger_roots"]),
            "duplicate-root", "ledger_roots")
    try:
        ZoneInfo(config.get("timezone", "Europe/Warsaw"))
    except (KeyError, ValueError):
        raise EvidenceError("invalid-timezone", "timezone") from None
    return config


def validate_source(ref, config, *, verify=True):
    shape(ref, {"root_alias", "relative_path", "sha256", "observed_at", "fact_date", "evidence_level"})
    require(ref["root_alias"] in config["source_roots"], "unknown-root", "root_alias")
    sha(ref["sha256"], "source_hash")
    instant(ref["observed_at"], "observed_at")
    if ref["fact_date"] is not None:
        iso_date(ref["fact_date"], "fact_date")
    choice(ref["evidence_level"], {"owner-attested", "local-test", "production-readback"}, "evidence_level")
    path = safe_path(config["source_roots"][ref["root_alias"]], ref["relative_path"])
    if verify:
        require(file_hash(path) == ref["sha256"], "stale-source", "source_hash")
    return path


def validate_registry(registry):
    shape(registry, {"schema_version", "entities", "task_bindings"})
    version(registry)
    require(isinstance(registry["entities"], list), "invalid-shape", "entities")
    ids, aliases = {}, {}
    for entity in registry["entities"]:
        shape(entity, {"id", "kind", "aliases"}, {"parent_id"})
        identifier(entity["id"], "entity_id")
        choice(entity["kind"], {"agency", "client", "project", "domain"}, "kind")
        require(entity["id"] not in ids, "duplicate-identity", "entity_id")
        require(isinstance(entity["aliases"], list), "invalid-shape", "aliases")
        ids[entity["id"]] = entity
        for alias in entity["aliases"]:
            text(alias, "alias", 256)
            key = (entity["kind"], alias.casefold())
            require(key not in aliases, "ambiguous-alias", "aliases")
            aliases[key] = entity["id"]
    for entity in ids.values():
        if entity.get("parent_id") is not None:
            identifier(entity["parent_id"], "parent_id")
            require(entity["parent_id"] in ids and entity["parent_id"] != entity["id"],
                    "unknown-parent", "parent_id")
            visited, current = set(), entity
            while current.get("parent_id") is not None:
                require(current["id"] not in visited, "parent-cycle", "parent_id")
                visited.add(current["id"])
                current = ids[current["parent_id"]]
    require(isinstance(registry["task_bindings"], list), "invalid-shape", "task_bindings")
    tasks = set()
    for binding in registry["task_bindings"]:
        shape(binding, {"task_ref", "owner_workspace", "work_id"})
        text(binding["task_ref"], "task_ref", 1000)
        identifier(binding["owner_workspace"], "owner_workspace")
        uuid_id(binding["work_id"], "work_id")
        require(binding["task_ref"] not in tasks, "ambiguous-task-owner", "task_ref")
        tasks.add(binding["task_ref"])
    return ids


def validate_timing(timing, duration, performed_on):
    kind = timing.get("kind") if isinstance(timing, dict) else None
    if kind == "date":
        shape(timing, {"kind", "date"})
        require(iso_date(timing["date"], "date") == iso_date(performed_on, "performed_on"),
                "date-conflict", "timing")
    elif kind == "interval":
        shape(timing, {"kind", "start", "end", "timezone"})
        start = instant(timing["start"], "start", timing["timezone"])
        end = instant(timing["end"], "end", timing["timezone"])
        elapsed = int((end.astimezone(timezone.utc) - start.astimezone(timezone.utc)).total_seconds())
        require(elapsed >= 0, "reversed-interval", "timing")
        require(start.date() == iso_date(performed_on, "performed_on"), "date-conflict", "timing")
        require(duration["basis"] == "measured" and duration["seconds"] == elapsed,
                "duration-conflict", "timing")
    elif kind == "aggregate":
        shape(timing, {"kind", "start_date", "end_date_exclusive"})
        start = iso_date(timing["start_date"], "start_date")
        end = iso_date(timing["end_date_exclusive"], "end_date_exclusive")
        require(start < end and start <= iso_date(performed_on, "performed_on") < end,
                "date-conflict", "timing")
        require(duration["basis"] != "measured", "aggregate-not-measured", "duration")
    else:
        raise EvidenceError("invalid-timing-kind", "timing")


def validate_entry(entry, config, registry, *, verify_sources=True):
    required = {
        "schema_version", "entry_id", "revision", "previous_revision_hash",
        "owner_workspace", "work_id", "performed_on", "recorded_at", "actor_kind",
        "client_id", "project_id", "title_internal", "activity_kind", "outcome",
        "status", "duration", "timing", "source_refs", "visibility",
    }
    shape(entry, required, {"reason", "voided", "task_ref"})
    version(entry)
    uuid_id(entry["entry_id"], "entry_id")
    uuid_id(entry["work_id"], "work_id")
    require(type(entry["revision"]) is int and entry["revision"] >= 1, "invalid-revision", "revision")
    if entry["revision"] == 1:
        require(entry["previous_revision_hash"] is None and not entry.get("voided", False),
                "invalid-chain", "previous_revision_hash")
    else:
        sha(entry["previous_revision_hash"], "previous_revision_hash")
        text(entry.get("reason"), "reason")
    require(type(entry.get("voided", False)) is bool, "invalid-void", "voided")
    require(entry["owner_workspace"] == config["workspace_id"],
            "owner-conflict", "owner_workspace")
    iso_date(entry["performed_on"], "performed_on")
    instant(entry["recorded_at"], "recorded_at")
    choice(entry["actor_kind"], {"human", "automation", "waiting"}, "actor_kind")
    entities = validate_registry(registry)
    for field, kinds in (("client_id", {"client"}), ("project_id", {"project"})):
        value = entry[field]
        require(value is None or (isinstance(value, str) and value in entities
                and entities[value]["kind"] in kinds), "unknown-entity", field)
    project = entities.get(entry["project_id"], {})
    if project.get("parent_id") is not None:
        require(project["parent_id"] == entry["client_id"], "client-project-conflict", "project_id")
    if entry.get("task_ref") is not None:
        matches = [b for b in registry["task_bindings"] if b["task_ref"] == entry["task_ref"]]
        require(len(matches) == 1 and matches[0]["owner_workspace"] == entry["owner_workspace"]
                and matches[0]["work_id"] == entry["work_id"], "task-binding-conflict", "task_ref")
    text(entry["title_internal"], "title_internal", 500)
    identifier(entry["activity_kind"], "activity_kind")
    text(entry["outcome"], "outcome", empty=True)
    choice(entry["status"], STATUSES, "status")
    require(entry["visibility"] == "internal", "separate-projection-required", "visibility")
    duration = entry["duration"]
    shape(duration, {"seconds", "basis", "evidence_ref", "session_id"})
    seconds(duration["seconds"], "seconds", nullable=True)
    choice(duration["basis"], ACTUAL_BASES | {"estimated", "unknown"}, "basis")
    require((duration["seconds"] is None) == (duration["basis"] == "unknown"),
            "unknown-duration-conflict", "seconds")
    if duration["session_id"] is not None:
        uuid_id(duration["session_id"], "session_id")
    require(isinstance(entry["source_refs"], list), "invalid-shape", "source_refs")
    for ref in entry["source_refs"]:
        validate_source(ref, config, verify=verify_sources)
    if duration["basis"] in ACTUAL_BASES:
        require(type(duration["evidence_ref"]) is int
                and 0 <= duration["evidence_ref"] < len(entry["source_refs"]),
                "actual-evidence-required", "evidence_ref")
        level = entry["source_refs"][duration["evidence_ref"]]["evidence_level"]
        if duration["basis"] == "owner-confirmed":
            require(level == "owner-attested", "basis-evidence-conflict", "evidence_ref")
    else:
        require(duration["evidence_ref"] is None, "basis-evidence-conflict", "evidence_ref")
    validate_timing(entry["timing"], duration, entry["performed_on"])
    return entry


def actual_seconds(entry):
    if (not entry.get("voided", False) and entry["actor_kind"] == "human"
            and entry["duration"]["basis"] in ACTUAL_BASES):
        return entry["duration"]["seconds"]
    return None


def validate_session(session, config, *, verify_sources=True):
    shape(session, {"schema_version", "session_id", "owner_workspace", "performed_on",
                    "recorded_at", "timing", "duration", "allocations", "source_refs"})
    version(session)
    uuid_id(session["session_id"], "session_id")
    require(session["owner_workspace"] == config["workspace_id"], "owner-conflict", "session")
    iso_date(session["performed_on"], "performed_on")
    instant(session["recorded_at"], "recorded_at")
    duration = session["duration"]
    shape(duration, {"seconds", "basis", "evidence_ref", "session_id"})
    seconds(duration["seconds"], "session_seconds")
    choice(duration["basis"], ACTUAL_BASES, "session_basis")
    require(duration["session_id"] == session["session_id"], "session-conflict", "session_id")
    require(isinstance(session["source_refs"], list), "invalid-shape", "source_refs")
    for ref in session["source_refs"]:
        validate_source(ref, config, verify=verify_sources)
    index = duration["evidence_ref"]
    require(type(index) is int and 0 <= index < len(session["source_refs"]),
            "actual-evidence-required", "session_evidence")
    if duration["basis"] == "owner-confirmed":
        require(session["source_refs"][index]["evidence_level"] == "owner-attested",
                "basis-evidence-conflict", "session_evidence")
    validate_timing(session["timing"], duration, session["performed_on"])
    require(isinstance(session["allocations"], list), "invalid-shape", "allocations")
    ids, total = set(), 0
    for allocation in session["allocations"]:
        shape(allocation, {"entry_id", "seconds"})
        uuid_id(allocation["entry_id"], "entry_id")
        seconds(allocation["seconds"], "allocation_seconds")
        require(allocation["entry_id"] not in ids, "duplicate-allocation", "entry_id")
        ids.add(allocation["entry_id"])
        total += allocation["seconds"]
    require(total <= duration["seconds"], "session-overallocated", "allocations")
    return session
