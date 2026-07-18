#!/usr/bin/env python3
"""Strict parser and schema validator for Personal Ops index contract 3."""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / ".systems/ai/templates/workspace/personal-ops/check-in-properties-v3.schema.json"

CURRENT_TASK_GENERATION_POLICY = "deadline-aware-6d-v1"
HISTORICAL_TASK_GENERATION_POLICY = "all-professional-do-v1"
HISTORICAL_NATIVE_CUTOFF = date(2026, 7, 17)
LEGACY_ADDITIVE_PROPERTY_KEYS = frozenset({
    "planned_do_count",
    "planned_defer_count",
    "planned_delegate_count",
    "planned_delete_count",
    "planned_dump_count",
    "planned_with_deadline_count",
    "planned_without_deadline_count",
    "planned_earliest_deadline",
    "planned_latest_deadline",
})

def load_schema() -> list[dict[str, Any]]:
    raw = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    fields = raw.get("fields")
    if not isinstance(fields, list) or not fields:
        raise ValueError(f"Invalid properties schema: {SCHEMA_PATH}")
    keys = [field.get("key") for field in fields]
    if len(keys) != len(set(keys)) or not all(isinstance(key, str) for key in keys):
        raise ValueError(f"Properties schema has duplicate or invalid keys: {SCHEMA_PATH}")
    return fields


def _scalar(raw: str) -> Any:
    value = raw.strip()
    if value == "":
        return ""
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "Null", "~"}:
        return ""
    if value.startswith('"') and value.endswith('"'):
        try:
            return json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid quoted YAML scalar: {value}") from exc
    return value


def parse_frontmatter_and_properties(text: str, source: Path) -> tuple[dict[str, Any], dict[str, Any], str]:
    if not text.startswith("---\n"):
        raise ValueError(f"Missing frontmatter: {source}")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError(f"Missing closing frontmatter: {source}")
    frontmatter_text = text[4:end]
    body = text[end + 5 :]
    top: dict[str, Any] = {}
    properties: dict[str, Any] = {}
    in_properties = False
    for line in frontmatter_text.splitlines():
        if not line.strip():
            continue
        nested = re.match(r"^  ([a-z][a-z0-9_]*)\s*:\s*(.*)$", line)
        if nested:
            if not in_properties:
                raise ValueError(f"Unexpected nested frontmatter field in {source}: {line}")
            properties[nested.group(1)] = _scalar(nested.group(2))
            continue
        if line.startswith((" ", "\t")):
            raise ValueError(f"Unsupported frontmatter indentation in {source}: {line}")
        if ":" not in line:
            raise ValueError(f"Malformed frontmatter line in {source}: {line}")
        key, value = line.split(":", 1)
        key = key.strip()
        if key == "properties":
            if value.strip():
                raise ValueError(f"properties must be a YAML map in {source}")
            in_properties = True
            continue
        in_properties = False
        top[key] = _scalar(value)
    return top, properties, body


def _validate_type(value: Any, spec: dict[str, Any], key: str, historical: bool = False) -> None:
    if value == "":
        return
    kind = spec["type"]
    if kind == "string":
        if not isinstance(value, str):
            raise ValueError(f"Property {key} must be a string")
    elif kind == "boolean":
        if not isinstance(value, bool):
            raise ValueError(f"Property {key} must be true, false, or empty")
    elif kind == "integer":
        if isinstance(value, bool) or not re.fullmatch(r"-?\d+", str(value)):
            raise ValueError(f"Property {key} must be an integer or empty")
    elif kind == "number":
        if isinstance(value, bool):
            raise ValueError(f"Property {key} must be a number or empty")
        try:
            float(str(value))
        except ValueError as exc:
            raise ValueError(f"Property {key} must be a number or empty") from exc
    elif kind == "date":
        try:
            date.fromisoformat(str(value))
        except ValueError as exc:
            raise ValueError(f"Property {key} must use YYYY-MM-DD") from exc
    elif kind == "time":
        if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", str(value)):
            raise ValueError(f"Property {key} must use HH:MM")
    elif kind == "datetime":
        try:
            datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"Property {key} must be an ISO datetime") from exc
    elif kind == "json":
        try:
            json.loads(str(value))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Property {key} must be a JSON scalar string") from exc
    elif kind == "enum":
        allowed = spec.get("values", [])
        if historical and key == "task_generation_policy":
            allowed = [*allowed, HISTORICAL_TASK_GENERATION_POLICY]
        if str(value) not in allowed:
            raise ValueError(f"Property {key} has unsupported value: {value}")
    else:
        raise ValueError(f"Unsupported schema type for {key}: {kind}")


def validate_properties(top: dict[str, Any], properties: dict[str, Any], source: Path, historical: bool = False) -> dict[str, Any]:
    by_key = validate_property_map(properties, source, historical=historical)
    if str(top.get("schema_version", "")) != "3" or str(top.get("index_contract", "")) != "3":
        raise ValueError(f"Expected schema_version: 3 and index_contract: 3 in {source}")
    for key, spec in by_key.items():
        _validate_type(properties[key], spec, key, historical=historical)
    if str(properties["index_contract"]) != "3" or str(properties["schema_version"]) != "3":
        raise ValueError(f"Properties must repeat schema_version: 3 and index_contract: 3 in {source}")
    if top.get("type") != "daily-check-in":
        raise ValueError(f"type must be daily-check-in in {source}")
    if not top.get("session_date"):
        raise ValueError(f"session_date is required in top-level frontmatter for {source}")
    if str(top["session_date"]) != str(properties["session_date"]):
        raise ValueError(f"session_date must match properties in {source}")
    if not top.get("previous_day_date"):
        raise ValueError(f"previous_day_date is required in top-level frontmatter for {source}")
    if str(top["previous_day_date"]) != str(properties["closure_date"]):
        raise ValueError(f"previous_day_date must match properties.closure_date in {source}")
    try:
        source_date = date.fromisoformat(source.stem)
    except ValueError as exc:
        raise ValueError(f"Report filename must be YYYY-MM-DD.md in {source}") from exc
    if source.parent.name != source_date.strftime("%Y"):
        raise ValueError(f"Report year directory must match filename date in {source}")
    if str(properties["report_id"]) != str(properties["session_date"]):
        raise ValueError(f"report_id must equal session_date in {source}")
    if source_date.isoformat() != str(properties["session_date"]):
        raise ValueError(f"Report filename date must equal session_date in {source}")
    if properties["session_date"] and properties["closure_date"]:
        session = date.fromisoformat(str(properties["session_date"]))
        closure = date.fromisoformat(str(properties["closure_date"]))
        if (session - closure).days != 1:
            raise ValueError(f"closure_date must be exactly one day before session_date in {source}")
    _validate_task_candidate_eligible_count(properties, source, historical=historical)
    return by_key


def validate_property_map(properties: dict[str, Any], source: Path, historical: bool = False) -> dict[str, dict[str, Any]]:
    """Validate the complete V3 property shape without assuming a Markdown report.

    The one-time legacy snapshot has the same schema as a native report, but it is
    not a canonical Markdown file and intentionally has different task/WIG semantics.
    """
    fields = load_schema()
    by_key = {field["key"]: field for field in fields}
    missing = sorted(set(by_key) - set(properties))
    unknown = sorted(set(properties) - set(by_key))
    if missing:
        raise ValueError(f"Missing required properties in {source}: {', '.join(missing)}")
    if unknown:
        raise ValueError(f"Unknown properties in {source}: {', '.join(unknown)}")
    for key, spec in by_key.items():
        _validate_type(properties[key], spec, key, historical=historical)
    return by_key


def project_historical_properties(properties: dict[str, Any], source: Path) -> dict[str, Any]:
    """Project additive fields for a retired report without changing its source."""
    missing = set(load_schema_field_keys()) - set(properties)
    if missing - LEGACY_ADDITIVE_PROPERTY_KEYS:
        raise ValueError(
            f"Historical report has non-additive missing properties in {source}: "
            f"{', '.join(sorted(missing - LEGACY_ADDITIVE_PROPERTY_KEYS))}"
        )
    projected = dict(properties)
    for key in missing:
        projected[key] = ""
    validate_property_map(projected, source, historical=True)
    return projected


def load_schema_field_keys() -> set[str]:
    return {field["key"] for field in load_schema()}


def _json_array(value: Any, key: str, source: Path) -> list[Any]:
    try:
        decoded = json.loads(str(value))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Property {key} must be a JSON array in {source}") from exc
    if not isinstance(decoded, list):
        raise ValueError(f"Property {key} must be a JSON array in {source}")
    return decoded


def _json_object(value: Any, key: str, source: Path) -> dict[str, Any]:
    try:
        decoded = json.loads(str(value))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Property {key} must be a JSON object in {source}") from exc
    if not isinstance(decoded, dict):
        raise ValueError(f"Property {key} must be a JSON object in {source}")
    return decoded


TASK_BUCKETS = {"do", "defer", "delegate", "delete", "dump"}


def _normalize_task_bucket(value: Any, source: Path, item_id: str) -> str:
    raw = str(value or "").strip().lower()
    if not raw:
        return ""
    if raw.startswith(("5d/", "6d/")):
        raw = raw.split("/", 1)[1]
    if raw not in TASK_BUCKETS:
        raise ValueError(f"Unsupported task_bucket '{value}' for {item_id} in {source}")
    return raw


def _validate_planned_item(item: dict[str, Any], source: Path) -> None:
    item_id = str(item.get("id", "")).strip()
    stream = str(item.get("stream", "")).strip().lower()
    if stream in {"build", "deliver", "promote"} and not str(item.get("title", "")).strip():
        raise ValueError(f"Professional planned item requires a non-empty title for {item_id} in {source}")
    deadline = str(item.get("deadline", "")).strip()
    if deadline:
        normalized = deadline.replace(" ", "T", 1) if " " in deadline and "T" not in deadline else deadline
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", deadline):
            try:
                date.fromisoformat(deadline)
            except ValueError as exc:
                raise ValueError(f"Invalid deadline '{deadline}' for {item_id} in {source}") from exc
        else:
            try:
                datetime.fromisoformat(normalized.replace("Z", "+00:00"))
            except ValueError as exc:
                raise ValueError(f"Invalid deadline '{deadline}' for {item_id} in {source}") from exc
    _normalize_task_bucket(item.get("task_bucket", ""), source, item_id)
    for key in ("title", "task_title", "definition_of_done"):
        if key in item and not isinstance(item[key], str):
            raise ValueError(f"Planned item {key} must be a string for {item_id} in {source}")


def _normalize_deadline(value: Any, source: Path, item_id: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
        try:
            date.fromisoformat(raw)
        except ValueError as exc:
            raise ValueError(f"Invalid deadline '{raw}' for {item_id} in {source}") from exc
        return f"{raw}T23:59"
    normalized = raw.replace(" ", "T", 1) if " " in raw and "T" not in raw else raw
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"Invalid deadline '{raw}' for {item_id} in {source}") from exc
    timespec = "minutes" if parsed.second == 0 and parsed.microsecond == 0 else "seconds"
    return parsed.isoformat(timespec=timespec)


def _planned_task_metrics(items: list[dict[str, Any]], source: Path) -> dict[str, Any]:
    metrics: dict[str, Any] = {
        "planned_do_count": 0,
        "planned_defer_count": 0,
        "planned_delegate_count": 0,
        "planned_delete_count": 0,
        "planned_dump_count": 0,
        "planned_with_deadline_count": 0,
        "planned_without_deadline_count": 0,
        "planned_earliest_deadline": "",
        "planned_latest_deadline": "",
    }
    deadlines: list[str] = []
    for item in items:
        stream = str(item.get("stream", "")).strip().lower()
        if stream not in {"build", "deliver", "promote"}:
            continue
        item_id = str(item.get("id", "")).strip()
        deadline = _normalize_deadline(item.get("deadline", ""), source, item_id)
        bucket = _normalize_task_bucket(item.get("task_bucket", ""), source, item_id)
        bucket = bucket or ("do" if deadline else "defer")
        metrics[f"planned_{bucket}_count"] += 1
        if deadline:
            metrics["planned_with_deadline_count"] += 1
            deadlines.append(deadline)
        else:
            metrics["planned_without_deadline_count"] += 1
    if deadlines:
        metrics["planned_earliest_deadline"] = min(deadlines)
        metrics["planned_latest_deadline"] = max(deadlines)
    return metrics


def _validate_planned_task_metrics(properties: dict[str, Any], items: list[dict[str, Any]], source: Path) -> None:
    expected = _planned_task_metrics(items, source)
    for key, value in expected.items():
        actual = str(properties[key])
        expected_value = str(value)
        if actual != expected_value:
            raise ValueError(f"{key} must equal {expected_value} from planned_items_json in {source}; got {actual}")


def _minimum_day_status_from_wig_closure(closure: dict[str, Any], source: Path) -> str:
    if not closure:
        return "unknown"
    wig_id = str(closure.get("wig_id", "")).strip()
    status = str(closure.get("status", "")).strip()
    if not wig_id:
        raise ValueError(f"previous_day_wig_closure_json requires wig_id in {source}")
    if status == "completed-as-planned":
        return "completed"
    if status == "completed-differently":
        return "completed" if closure.get("owner_approved") is True else "not-completed"
    if status in {"partial", "not-completed", "replaced"}:
        return "not-completed"
    if status == "unknown":
        return "unknown"
    raise ValueError(f"Unsupported prior-day WIG closure status '{status}' in {source}")


def _validate_task_candidate_eligible_count(properties: dict[str, Any], source: Path, historical: bool = False) -> None:
    """Keep the source properties metric aligned with V3 TaskNote candidate policy."""
    items = _json_array(properties["planned_items_json"], "planned_items_json", source)
    if not all(isinstance(item, dict) for item in items):
        raise ValueError(f"planned_items_json must contain objects only in {source}")
    item_ids = [str(item.get("id", "")).strip() for item in items]
    if any(not item_id for item_id in item_ids) or len(item_ids) != len(set(item_ids)):
        raise ValueError(f"planned_items_json requires unique non-empty item IDs in {source}")
    policy = str(properties["task_generation_policy"])
    if policy != CURRENT_TASK_GENERATION_POLICY and not (historical and policy == HISTORICAL_TASK_GENERATION_POLICY):
        raise ValueError(f"Unsupported V3 task_generation_policy in {source}: {policy}")
    wig_kind = str(properties["wig_kind"])
    wig_id = str(properties["wig_id"]).strip()
    wig_title = str(properties["wig_title"]).strip()
    wig_plan_item_id = str(properties["wig_plan_item_id"]).strip()
    wig_definition = str(properties["wig_definition_of_done"]).strip()
    if wig_kind == "plan-item":
        if not wig_id or not wig_title or not wig_definition or wig_plan_item_id not in item_ids:
            raise ValueError(f"plan-item WIG requires ID, title, Definition of Done, and a valid plan item in {source}")
    elif wig_kind == "standalone":
        if not wig_id or not wig_title or not wig_definition or wig_plan_item_id:
            raise ValueError(f"standalone WIG requires ID, title, Definition of Done, and no plan item in {source}")
    elif wig_kind == "none":
        if wig_id or wig_title or wig_plan_item_id or wig_definition:
            raise ValueError(f"none WIG must not carry WIG values in {source}")
    else:
        raise ValueError(f"Unsupported WIG kind '{wig_kind}' in {source}")

    expected_readiness = "ready" if wig_kind in {"plan-item", "standalone"} else "needs-prioritization"
    if str(properties["plan_readiness"]) != expected_readiness:
        raise ValueError(f"plan_readiness must be {expected_readiness} for WIG kind {wig_kind} in {source}")
    closure = _json_object(properties["previous_day_wig_closure_json"], "previous_day_wig_closure_json", source)
    expected_minimum = _minimum_day_status_from_wig_closure(closure, source)
    if str(properties["previous_day_minimum_day_status"]) != expected_minimum:
        raise ValueError(
            f"previous_day_minimum_day_status must equal {expected_minimum} from prior-day WIG closure in {source}"
        )
    expected = 0
    for item in items:
        stream = str(item.get("stream", "")).strip().lower()
        _validate_planned_item(item, source)
        if stream in {"build", "deliver", "promote"}:
            expected += 1

    if not historical:
        _validate_planned_task_metrics(properties, items, source)

    try:
        actual = int(str(properties["task_candidate_eligible_count"]))
    except ValueError as exc:
        raise ValueError(f"task_candidate_eligible_count must be an integer in {source}") from exc
    if actual != expected:
        raise ValueError(
            f"task_candidate_eligible_count must equal {expected} from eligible planned items in {source}; got {actual}"
        )


def csv_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def decoded_json_properties(properties: dict[str, Any]) -> dict[str, Any]:
    decoded: dict[str, Any] = {}
    for key, value in properties.items():
        decoded[key] = json.loads(str(value)) if key.endswith("_json") and value != "" else value
    return decoded


def redacted_properties(properties: dict[str, Any], schema: dict[str, dict[str, Any]]) -> dict[str, Any]:
    redacted = dict(properties)
    for key, spec in schema.items():
        if spec.get("private"):
            redacted[key] = ""
    return redacted
