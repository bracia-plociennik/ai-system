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


def _validate_type(value: Any, spec: dict[str, Any], key: str) -> None:
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
        if str(value) not in spec.get("values", []):
            raise ValueError(f"Property {key} has unsupported value: {value}")
    else:
        raise ValueError(f"Unsupported schema type for {key}: {kind}")


def validate_properties(top: dict[str, Any], properties: dict[str, Any], source: Path) -> dict[str, Any]:
    fields = load_schema()
    by_key = {field["key"]: field for field in fields}
    missing = sorted(set(by_key) - set(properties))
    unknown = sorted(set(properties) - set(by_key))
    if missing:
        raise ValueError(f"Missing required properties in {source}: {', '.join(missing)}")
    if unknown:
        raise ValueError(f"Unknown properties in {source}: {', '.join(unknown)}")
    if str(top.get("schema_version", "")) != "3" or str(top.get("index_contract", "")) != "3":
        raise ValueError(f"Expected schema_version: 3 and index_contract: 3 in {source}")
    for key, spec in by_key.items():
        _validate_type(properties[key], spec, key)
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
    _validate_task_candidate_eligible_count(properties, source)
    return by_key


def _json_array(value: Any, key: str, source: Path) -> list[Any]:
    try:
        decoded = json.loads(str(value))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Property {key} must be a JSON array in {source}") from exc
    if not isinstance(decoded, list):
        raise ValueError(f"Property {key} must be a JSON array in {source}")
    return decoded


def _validate_task_candidate_eligible_count(properties: dict[str, Any], source: Path) -> None:
    """Keep the source properties metric aligned with V3 TaskNote candidate policy."""
    items = _json_array(properties["planned_items_json"], "planned_items_json", source)
    must_do = _json_array(properties["must_do_plan_item_ids_json"], "must_do_plan_item_ids_json", source)
    if not all(isinstance(item, dict) for item in items):
        raise ValueError(f"planned_items_json must contain objects only in {source}")
    item_ids = [str(item.get("id", "")).strip() for item in items]
    if any(not item_id for item_id in item_ids) or len(item_ids) != len(set(item_ids)):
        raise ValueError(f"planned_items_json requires unique non-empty item IDs in {source}")
    must_ids = [str(value).strip() for value in must_do]
    if any(not item_id for item_id in must_ids) or len(must_ids) > 2 or len(must_ids) != len(set(must_ids)):
        raise ValueError(f"must_do_plan_item_ids_json must contain at most two unique non-empty IDs in {source}")

    readiness = str(properties["plan_readiness"])
    overload = str(properties["overload_status"])
    acknowledged = properties["overload_acknowledged"] is True
    expected = 0
    if readiness == "ready":
        wig = str(properties["wig_plan_item_id"]).strip()
        if not wig or wig not in item_ids or wig in must_ids or any(item_id not in item_ids for item_id in must_ids):
            raise ValueError(f"WIG/must-do properties are inconsistent with planned_items_json in {source}")
        if overload != "warning" or acknowledged:
            for item in items:
                stream = str(item.get("stream", "")).strip().lower()
                policy = str(item.get("task", "create")).strip().lower() or "create"
                if policy not in {"create", "skip"}:
                    raise ValueError(f"Unsupported V3 Task policy for {item.get('id', '')} in {source}")
                if stream in {"build", "deliver", "promote"} and policy == "create":
                    expected += 1
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
