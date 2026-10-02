#!/usr/bin/env python3
"""Parser and compatibility read model for SPOR Personal Ops V4 artifacts."""

from __future__ import annotations

import json
import re
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from personal_ops_properties_v3 import parse_frontmatter_and_properties


REPO_ROOT = Path(__file__).resolve().parents[2]
V4_SCHEMA = REPO_ROOT / ".systems/ai/templates/workspace/personal-ops/check-in-properties-v4.schema.json"
V4_DAILY_ROOT = "personal-ops/check-ins-v4"
V4_WEEKLY_ROOT = "personal-ops/weekly-check-ins-v4"
V4_INDEX = "personal-ops/indexes/check-ins-v4.jsonl"
V4_CSV_INDEX = "personal-ops/indexes/check-ins-v4.csv"
V4_METRICS_INDEX = "personal-ops/indexes/check-ins-v4.metrics.csv"
V4_ROUTER = "personal-ops/indexes/check-ins-v4.md"
V4_TRENDS = "personal-ops/indexes/check-ins-v4.trends.md"
WORKING_DUMP_START = "<!-- ai-system:working-dump:start -->"
WORKING_DUMP_END = "<!-- ai-system:working-dump:end -->"
WORKING_DUMP_HEADING = "## Working Dump"
LIFE_ALIGNMENT_CONTRACT = "last-period-alignment-v1"
DAILY_ALIGNMENT_QUESTION = "Jeśli dzisiaj miałoby być ostatnim dniem mojego życia, czy chciałbym zrobić to, co zaplanowałem do zrobienia na dziś?"
WEEKLY_ALIGNMENT_QUESTION = "Jeśli przyszły tydzień miałby być ostatnim tygodniem mojego życia, czy chciałbym zrobić to, co zaplanowałem do zrobienia na przyszły tydzień?"


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], dict[str, Any], str]:
    return parse_frontmatter_and_properties(path.read_text(encoding="utf-8"), path)


def _working_dump_marked_block(body: str) -> re.Match[str] | None:
    pattern = re.compile(
        rf"(?ms)^{re.escape(WORKING_DUMP_START)}\n{re.escape(WORKING_DUMP_HEADING)}\n.*?^{re.escape(WORKING_DUMP_END)}\n?"
    )
    return pattern.search(body)


def working_dump_block(body: str) -> str | None:
    """Return the exact Working Dump section, preserving manual bytes."""
    marked = _working_dump_marked_block(body)
    if marked:
        return marked.group(0)
    heading = re.search(r"(?m)^## Working Dump[ \t]*\n", body)
    return body[heading.start():] if heading else None


def working_dump_text(body: str) -> str:
    """Read only the user-authored content inside Working Dump."""
    block = working_dump_block(body)
    if block is None:
        return ""
    content = re.sub(rf"(?m)^{re.escape(WORKING_DUMP_START)}\n", "", block, count=1)
    content = re.sub(rf"(?m)^{re.escape(WORKING_DUMP_END)}\n?\Z", "", content, count=1)
    content = re.sub(r"(?m)^## Working Dump[ \t]*\n", "", content, count=1)
    return content.strip("\n")


def ensure_working_dump(body: str) -> str:
    """Append an empty dump to a newly rendered artifact without rewriting it."""
    if working_dump_block(body) is not None:
        return body
    return (
        body.rstrip("\n")
        + "\n\n"
        + WORKING_DUMP_START
        + "\n"
        + WORKING_DUMP_HEADING
        + "\n"
        + WORKING_DUMP_END
        + "\n"
    )


def preserve_working_dump(existing_body: str, replacement_body: str) -> str:
    """Keep an existing manual dump byte-for-byte across canonical rewrites."""
    existing = working_dump_block(existing_body)
    if existing is None:
        return ensure_working_dump(replacement_body)
    replacement_block = working_dump_block(replacement_body)
    if replacement_block is not None:
        replacement_body = replacement_body[: replacement_body.index(replacement_block)]
    return replacement_body.rstrip("\n") + "\n\n" + existing


def json_value(properties: dict[str, Any], key: str, default: Any) -> Any:
    raw = str(properties.get(key, "") or "").strip()
    if not raw:
        return default
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"malformed {key}") from exc


def _numeric_json_value(value: Any) -> str | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        return str(Decimal(str(value)))
    except (InvalidOperation, ValueError):
        return None


def normalize_budget_facts(properties: dict[str, Any]) -> dict[str, Any]:
    """Project V4 review facts onto the legacy budget fields used by reports.

    V3 scalar properties remain canonical when present. V4 review data only
    fills missing closure facts, so mixed V3+V4 records cannot double-count or
    override an existing normalized value.
    """
    normalized = dict(properties)
    review_process = json_value(properties, "review_process_json", {})
    if not isinstance(review_process, dict):
        return normalized

    finance = review_process.get("finance")
    if (
        not str(normalized.get("previous_day_finance_amount", "") or "").strip()
        and isinstance(finance, dict)
    ):
        amount = _numeric_json_value(finance.get("amount"))
        if amount is not None:
            normalized["previous_day_finance_amount"] = amount
            if "currency" in finance:
                normalized["previous_day_finance_currency"] = str(finance["currency"])
            if "approximate" in finance:
                normalized["previous_day_finance_approximate"] = str(finance["approximate"]).lower()

    if not str(normalized.get("previous_day_actual_calories_representative", "") or "").strip():
        # V3 uses `if`; V4 readable review data uses `nutrition`. Keep both
        # routes so the version-aware budget model does not drop actual intake.
        if_data = review_process.get("if")
        if not isinstance(if_data, dict):
            if_data = review_process.get("nutrition")
        if isinstance(if_data, dict):
            calories = _numeric_json_value(if_data.get("calories"))
            if calories is not None:
                normalized["previous_day_actual_calories_representative"] = calories
                if "approximate" in if_data:
                    normalized["previous_day_actual_calories_approximate"] = str(if_data["approximate"]).lower()

    return normalized


def required_schema(kind: str) -> list[str]:
    raw = load_schema()
    return list(raw["daily_required" if kind == "daily" else "weekly_required"])


def load_schema() -> dict[str, Any]:
    raw = json.loads(V4_SCHEMA.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("V4 properties schema must be an object")
    return raw


def daily_index_fields() -> list[dict[str, Any]]:
    fields = load_schema().get("daily_index_fields")
    if not isinstance(fields, list) or not fields or any(not isinstance(field, dict) for field in fields):
        raise ValueError("V4 properties schema must define daily_index_fields")
    keys = [str(field.get("key", "")).strip() for field in fields]
    if any(not key for key in keys) or len(keys) != len(set(keys)):
        raise ValueError("V4 daily_index_fields contain missing or duplicate keys")
    required = set(required_schema("daily"))
    missing = required - set(keys)
    if missing:
        raise ValueError(f"V4 daily_index_fields omit required properties: {', '.join(sorted(missing))}")
    return fields


def project_index_properties(properties: dict[str, Any], fields: list[dict[str, Any]]) -> dict[str, Any]:
    """Apply defaults and the V4 private-index policy without exposing unknown fields."""
    by_key = {str(field["key"]): field for field in fields}
    projected = dict(properties)
    for key, field in by_key.items():
        projected.setdefault(key, field.get("default", ""))
    if str(properties.get("private_index_policy", "")) == "redacted":
        for key in list(projected):
            field = by_key.get(key)
            if field is None or bool(field.get("private")):
                projected[key] = ""
    return projected


def normalize_life_alignment_answer(value: Any) -> str:
    """Normalize Polish and English input to the private contract values."""
    raw = str(value or "").strip().lower()
    if raw in {"yes", "tak"}:
        return "yes"
    if raw in {"no", "nie"}:
        return "no"
    if raw in {"unknown", "nie wiem", "n/a", "na"} or not raw:
        return "unknown"
    raise ValueError(f"invalid life alignment answer: {value}")


def _alignment_resolution(properties: dict[str, Any], path: Path) -> dict[str, Any] | None:
    if "life_alignment_resolution_json" not in properties:
        return None
    value = json_value(properties, "life_alignment_resolution_json", None)
    if value in (None, {}, ""):
        return None
    if not isinstance(value, dict):
        raise ValueError(f"life_alignment_resolution_json must be an object: {path}")
    required = ("episode_id", "mode", "reason", "approved_at", "approved_by")
    if any(not str(value.get(key, "")).strip() for key in required):
        raise ValueError(f"life_alignment_resolution_json is incomplete: {path}")
    if value.get("mode") not in {"plan-change", "owner-override"}:
        raise ValueError(f"invalid life alignment resolution mode: {path}")
    if value.get("approved_by") != "owner":
        raise ValueError(f"life alignment resolution must be approved_by owner: {path}")
    if not re.fullmatch(r"(?:daily|weekly):red:[^\s]+", str(value["episode_id"])):
        raise ValueError(f"invalid life alignment episode_id: {path}")
    return value


def _validate_alignment(properties: dict[str, Any], body: str, path: Path, kind: str) -> None:
    marker = str(properties.get("life_alignment_contract", "") or "").strip()
    if not marker:
        return
    if marker != LIFE_ALIGNMENT_CONTRACT:
        raise ValueError(f"unsupported life_alignment_contract: {path}")
    key = "planned_day_life_alignment_answer" if kind == "daily" else "planned_week_life_alignment_answer"
    answer = normalize_life_alignment_answer(properties.get(key, "unknown"))
    if str(properties.get(key, "unknown")).strip().lower() != answer:
        raise ValueError(f"{key} must be normalized to yes, no, or unknown: {path}")
    _alignment_resolution(properties, path)
    question = DAILY_ALIGNMENT_QUESTION if kind == "daily" else WEEKLY_ALIGNMENT_QUESTION
    if question not in body:
        raise ValueError(f"life alignment question missing from REVIEW: {path}")


def validate_common(top: dict[str, Any], properties: dict[str, Any], path: Path, kind: str) -> None:
    expected_type = "daily-check-in-v4" if kind == "daily" else "weekly-check-in-v4"
    if top.get("type") != expected_type or str(top.get("schema_version")) != "4" or str(top.get("index_contract")) != "4":
        raise ValueError(f"expected {expected_type} schema/index contract 4: {path}")
    missing = [key for key in required_schema(kind) if key not in properties]
    if missing:
        raise ValueError(f"missing V4 properties: {', '.join(missing)}")
    if str(properties.get("artifact_kind")) != kind:
        raise ValueError(f"artifact_kind does not match {kind}: {path}")
    if str(properties.get("index_contract")) != "4" or str(properties.get("schema_version")) != "4":
        raise ValueError(f"properties must repeat V4 schema/index contract: {path}")
    if properties.get("private_index_policy") not in {"detailed-private", "redacted"}:
        raise ValueError(f"invalid private_index_policy: {path}")


def _clock_minutes(value: Any, label: str, path: Path) -> int:
    match = re.fullmatch(r"(\d{2}):(\d{2})", str(value or ""))
    if not match:
        raise ValueError(f"{label} must use HH:MM: {path}")
    hour, minute = int(match.group(1)), int(match.group(2))
    if hour > 23 or minute > 59:
        raise ValueError(f"{label} must use a valid clock time: {path}")
    return hour * 60 + minute


def schedule_interval_minutes(row: dict, path: Path | None = None) -> tuple[int, int]:
    """Return a wall-clock interval relative to the schedule's session day."""
    source = path or Path("planned_schedule_json")
    block_id = str(row.get("block_id", "schedule"))
    offset = row.get("end_day_offset", 0)
    if type(offset) is not int or offset not in (0, 1):
        raise ValueError(f"{block_id}.end_day_offset must be integer 0 or 1: {source}")
    start = _clock_minutes(row.get("start"), f"{block_id}.start", source)
    end = _clock_minutes(row.get("end"), f"{block_id}.end", source) + offset * 1440
    if end <= start:
        raise ValueError(f"planned_schedule_json row must end after it starts: {block_id}: {source}")
    if end - start > 1440:
        raise ValueError(f"planned_schedule_json row cannot exceed 24 hours: {block_id}: {source}")
    return start, end


def _validate_planned_schedule(properties: dict[str, Any], items: list[dict], path: Path) -> None:
    contract = str(properties.get("daily_plan_contract", "") or "").strip()
    if not contract:
        return
    if contract != "per-day-schedule-v1":
        raise ValueError(f"unsupported daily_plan_contract: {path}")
    rows = json_value(properties, "planned_schedule_json", None)
    if not isinstance(rows, list) or not rows or any(not isinstance(row, dict) for row in rows):
        raise ValueError(f"planned_schedule_json must be a non-empty array of objects: {path}")
    block_ids: set[str] = set()
    meal_slots: set[int] = set()
    for row in rows:
        block_id = str(row.get("block_id", "")).strip()
        kind = str(row.get("kind", "")).strip()
        label = str(row.get("label", "")).strip()
        if not block_id or block_id in block_ids:
            raise ValueError(f"planned_schedule_json contains missing or duplicate block_id: {path}")
        if not kind or not label:
            raise ValueError(f"planned_schedule_json rows require kind and label: {path}")
        schedule_interval_minutes(row, path)
        block_ids.add(block_id)
        if kind == "meal":
            slot = row.get("meal_slot")
            if isinstance(slot, bool) or not isinstance(slot, int) or slot not in {1, 2, 3} or slot in meal_slots:
                raise ValueError(f"meal rows require unique meal_slot 1..3: {path}")
            meal_slots.add(slot)
        elif "meal_slot" in row:
            raise ValueError(f"meal_slot is allowed only for meal rows: {path}")
    if meal_slots != {1, 2, 3}:
        raise ValueError(f"per-day schedule requires meal_slot 1, 2, and 3: {path}")
    missing_blocks = [
        str(item.get("block_id", "")).strip()
        for item in items
        if str(item.get("block_id", "")).strip() and str(item.get("block_id", "")).strip() not in block_ids
    ]
    if missing_blocks:
        raise ValueError(f"planned item references unknown per-day block_id: {', '.join(missing_blocks)}: {path}")


def _validate_readable_body(properties: dict[str, Any], body: str, path: Path) -> None:
    contract = str(properties.get("readable_body_contract", "") or "").strip()
    if not contract:
        return
    if contract != "spor-readable-v1":
        raise ValueError(f"unsupported readable_body_contract: {path}")
    for heading in ("Plan na dziś", "STATE", "PROCESS", "OUTCOME", "REVIEW"):
        match = re.search(rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)", body)
        if not match or not match.group(1).strip():
            raise ValueError(f"readable body section is missing or empty: {heading}: {path}")


def validate_daily(top: dict[str, Any], properties: dict[str, Any], path: Path, body: str = "") -> None:
    validate_common(top, properties, path, "daily")
    session = date.fromisoformat(str(properties["session_date"]))
    closure = date.fromisoformat(str(properties["closure_date"]))
    if session - closure != timedelta(days=1):
        raise ValueError(f"closure_date must be the prior calendar day: {path}")
    if session.weekday() == 0 and properties["review_window_kind"] != "weekend":
        raise ValueError(f"Monday Daily V4 must review the weekend: {path}")
    if 1 <= session.weekday() <= 4 and properties["review_window_kind"] != "previous-day":
        raise ValueError(f"Tuesday-Friday Daily V4 must review one previous day: {path}")
    if session.weekday() >= 5:
        raise ValueError(f"Daily V4 is not allowed on Saturday or Sunday: {path}")
    for key in ("planned_items_json", "review_state_json", "review_process_json", "review_outcome_json", "review_review_json", "owner_overrides_json", "osnr_checkpoints_json", "task_generation_references_json"):
        value = json_value(properties, key, None)
        if value is None:
            raise ValueError(f"{key} must be valid JSON: {path}")
    if "current_state_json" in properties:
        current_state = json_value(properties, "current_state_json", None)
        if not isinstance(current_state, dict):
            raise ValueError(f"current_state_json must be an object: {path}")
    items = json_value(properties, "planned_items_json", [])
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        raise ValueError(f"planned_items_json must be an array of objects: {path}")
    ids = [str(item.get("id", "")) for item in items]
    if any(not item_id for item_id in ids) or len(ids) != len(set(ids)):
        raise ValueError(f"planned_items_json contains missing or duplicate IDs: {path}")
    _validate_planned_schedule(properties, items, path)
    _validate_readable_body(properties, body, path)
    _validate_alignment(properties, body, path, "daily")
    if properties.get("plan_vs_reality_gap", "") != "":
        gap = int(str(properties["plan_vs_reality_gap"]))
        if gap < 0 or gap > 5:
            raise ValueError(f"plan_vs_reality_gap must be 0-5: {path}")
    if properties.get("recovery_cost", "") != "":
        cost = int(str(properties["recovery_cost"]))
        if cost < -2 or cost > 2:
            raise ValueError(f"recovery_cost must be -2..2: {path}")


def validate_weekly(top: dict[str, Any], properties: dict[str, Any], path: Path, body: str = "") -> None:
    validate_common(top, properties, path, "weekly")
    review_start = date.fromisoformat(str(properties["review_week_start"]))
    review_end = date.fromisoformat(str(properties["review_week_end"]))
    plan_start = date.fromisoformat(str(properties["plan_week_start"]))
    plan_end = date.fromisoformat(str(properties["plan_week_end"]))
    if review_end - review_start != timedelta(days=6) or review_start.weekday() != 0:
        raise ValueError(f"weekly review must cover Monday-Sunday: {path}")
    if plan_end - plan_start != timedelta(days=4) or plan_start.weekday() != 0:
        raise ValueError(f"weekly plan must cover Monday-Friday: {path}")
    for key in ("review_state_json", "review_process_json", "review_outcome_json", "review_review_json", "future_wig_json", "future_plan_items_json", "daily_blocks_json"):
        value = json_value(properties, key, None)
        if value is None:
            raise ValueError(f"{key} must be valid JSON: {path}")
    items = json_value(properties, "future_plan_items_json", [])
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        raise ValueError(f"future_plan_items_json must be an array of objects: {path}")
    ids = [str(item.get("id", "")) for item in items]
    if len(ids) != len(set(ids)) or any(not item_id for item_id in ids):
        raise ValueError(f"future_plan_items_json contains missing or duplicate IDs: {path}")
    _validate_alignment(properties, body, path, "weekly")


def daily_path(workspace: Path, report_date: date) -> Path:
    return workspace / V4_DAILY_ROOT / f"{report_date.year:04d}" / f"{report_date.isoformat()}.md"


def weekly_path(workspace: Path, week_start: date) -> Path:
    week_id = f"{week_start.isocalendar().year}-W{week_start.isocalendar().week:02d}"
    return workspace / V4_WEEKLY_ROOT / f"{week_start.year:04d}" / f"{week_id}.md"


def load_daily(workspace: Path, report_date: date) -> tuple[dict[str, Any], dict[str, Any], str]:
    path = daily_path(workspace, report_date)
    if not path.is_file():
        raise ValueError(f"missing V4 daily check-in: {path}")
    top, properties, body = parse_frontmatter(path)
    validate_daily(top, properties, path, body)
    if str(properties.get("session_date")) != report_date.isoformat():
        raise ValueError(f"V4 daily session date mismatch: {path}")
    return top, properties, body


def load_weekly(workspace: Path, week_id: str) -> tuple[dict[str, Any], dict[str, Any], str]:
    match = re.fullmatch(r"(\d{4})-W(\d{2})", week_id)
    if not match:
        raise ValueError(f"invalid week id: {week_id}")
    year, week = int(match.group(1)), int(match.group(2))
    monday = date.fromisocalendar(year, week, 1)
    path = weekly_path(workspace, monday)
    if not path.is_file():
        raise ValueError(f"missing V4 weekly check-in: {path}")
    top, properties, body = parse_frontmatter(path)
    validate_weekly(top, properties, path, body)
    return top, properties, body


def load_v4_daily_records(workspace: Path) -> list[dict[str, Any]]:
    root = workspace / V4_DAILY_ROOT
    if not root.is_dir():
        return []
    records = []
    seen: set[str] = set()
    for path in sorted(root.glob("*/*.md")):
        top, properties, body = parse_frontmatter(path)
        validate_daily(top, properties, path, body)
        session = str(properties["session_date"])
        if session in seen:
            raise ValueError(f"duplicate V4 session_date: {session}")
        seen.add(session)
        records.append(properties)
    return records


def load_v4_weekly_records(workspace: Path) -> list[dict[str, Any]]:
    root = workspace / V4_WEEKLY_ROOT
    if not root.is_dir():
        return []
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in sorted(root.glob("*/*.md")):
        top, properties, body = parse_frontmatter(path)
        validate_weekly(top, properties, path, body)
        key = str(properties["plan_week_start"])
        if key in seen:
            raise ValueError(f"duplicate V4 weekly plan_week_start: {key}")
        seen.add(key)
        records.append(properties)
    return records


def _alignment_records(workspace: Path, kind: str, report_date: date) -> list[tuple[str, str, dict[str, Any]]]:
    source = load_v4_daily_records(workspace) if kind == "daily" else load_v4_weekly_records(workspace)
    answer_key = "planned_day_life_alignment_answer" if kind == "daily" else "planned_week_life_alignment_answer"
    date_key = "session_date" if kind == "daily" else "plan_week_start"
    records: list[tuple[str, str, dict[str, Any]]] = []
    for props in sorted(source, key=lambda row: str(row.get(date_key, ""))):
        stamp = str(props.get(date_key, ""))
        if not stamp or date.fromisoformat(stamp) > report_date:
            continue
        answer = normalize_life_alignment_answer(props.get(answer_key, "unknown"))
        if str(props.get("life_alignment_contract", "")).strip() != LIFE_ALIGNMENT_CONTRACT:
            answer = "unknown"
        records.append((stamp, answer, props))
    return records


def _alignment_card(kind: str, answered_count: int, no_count: int) -> str:
    if kind == "daily":
        if answered_count < 30:
            return "yellow" if answered_count >= 14 and no_count >= 11 else "none"
        return "red" if no_count >= 23 else ("yellow" if no_count >= 11 else "none")
    if answered_count < 4:
        return "none"
    return "red" if no_count >= 3 else ("yellow" if no_count >= 2 else "none")


def _window_summary(kind: str, records: list[tuple[str, str, dict[str, Any]]], size: int) -> dict[str, Any]:
    answered = [(stamp, answer, props) for stamp, answer, props in records if answer in {"yes", "no"}]
    window = answered[-size:]
    no_count = sum(answer == "no" for _, answer, _ in window)
    card = _alignment_card(kind, len(window), no_count)
    return {"answer_count": len(window), "no_count": no_count, "card": card, "records": window}


def _resolution_for_episode(kind: str, window: dict[str, Any], records: list[tuple[str, str, dict[str, Any]]]) -> dict[str, Any] | None:
    if window["card"] != "red" or not window["records"]:
        return None
    answered = [(stamp, answer, props) for stamp, answer, props in records if answer in {"yes", "no"}]
    episode_start = window["records"][-1][0]
    previous_card = "none"
    for index in range(len(answered)):
        current_window = answered[max(0, index - (30 if kind == "daily" else 4) + 1) : index + 1]
        current_card = _alignment_card(kind, len(current_window), sum(answer == "no" for _, answer, _ in current_window))
        if current_card == "red" and previous_card != "red":
            episode_start = answered[index][0]
            break
        previous_card = current_card
    episode_id = f"{kind}:red:{episode_start}"
    for current_stamp, answer, props in reversed(records):
        if current_stamp < episode_start:
            continue
        try:
            resolution = _alignment_resolution(props, Path("life_alignment"))
        except ValueError:
            continue
        if resolution and resolution.get("episode_id") == episode_id:
            if resolution.get("mode") == "plan-change" and answer != "yes":
                continue
            return resolution
    return None


def alignment_summary(workspace: Path, report_date: date) -> dict[str, Any]:
    """Return deterministic Daily/Weekly cards and the professional-write gate."""
    result: dict[str, Any] = {}
    blocked = False
    for kind, size in (("daily", 30), ("weekly", 4)):
        records = _alignment_records(workspace, kind, report_date)
        window = _window_summary(kind, records, size)
        resolution = _resolution_for_episode(kind, window, records)
        if kind == "daily":
            recent14 = _window_summary(kind, records, 14)
            result["daily"] = {**recent14, "no_30": window["no_count"], "count_30": window["answer_count"], "card_30": window["card"], "resolution": resolution}
            blocked = blocked or window["card"] == "red" and resolution is None
        else:
            result["weekly"] = {**window, "resolution": resolution}
            blocked = blocked or window["card"] == "red" and resolution is None
    result["tasknote_gate"] = "blocked" if blocked else "open"
    return result


def load_official_v4_records(workspace: Path) -> list[dict[str, Any]]:
    from personal_ops_aggregates_v4 import is_unified, read_properties
    if is_unified(workspace):
        return read_properties(workspace)
    required_paths = [
        workspace / V4_ROUTER,
        workspace / V4_INDEX,
        workspace / V4_CSV_INDEX,
        workspace / V4_METRICS_INDEX,
        workspace / V4_TRENDS,
    ]
    router, index = required_paths[0], required_paths[1]
    if not any(path.exists() for path in required_paths):
        return load_v4_daily_records(workspace)
    if any(not path.is_file() for path in required_paths):
        raise ValueError("V4 official index set is incomplete")
    router_text = router.read_text(encoding="utf-8")
    match = re.search(r"^unsynced-v4-check-in-count:\s*(\d+)\s*$", router_text, re.MULTILINE)
    if not match or int(match.group(1)) != 0:
        raise ValueError("V4 official indexes are stale")
    records: list[dict[str, Any]] = []
    for line in index.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        properties = payload.get("properties") if isinstance(payload, dict) else None
        if not isinstance(properties, dict):
            raise ValueError("malformed V4 official JSONL row")
        records.append(properties)
    return records


def load_v3_index_records(workspace: Path) -> list[dict[str, Any]]:
    index = workspace / "personal-ops/indexes/check-ins-v3.jsonl"
    router = workspace / "personal-ops/indexes/check-ins-v3.md"
    if not index.is_file() or not router.is_file():
        raise ValueError("official V3 index set is missing")
    freshness = re.search(r"^unsynced-native-check-in-count:\s*(\d+)\s*$", router.read_text(encoding="utf-8"), re.MULTILINE)
    if not freshness or int(freshness.group(1)) != 0:
        raise ValueError("official V3 indexes are stale")
    records = []
    for line in index.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        properties = payload.get("properties") if isinstance(payload, dict) else None
        if not isinstance(properties, dict):
            raise ValueError("malformed V3 official JSONL row")
        records.append(properties)
    return records


def load_current_records(workspace: Path) -> list[dict[str, Any]]:
    from personal_ops_aggregates_v4 import is_unified, read_properties
    if is_unified(workspace):
        return read_properties(workspace)
    records = load_v3_index_records(workspace) + load_official_v4_records(workspace)
    seen: dict[str, str] = {}
    for properties in records:
        session = str(properties.get("session_date", ""))
        if not session:
            continue
        source = str(properties.get("index_contract", "unknown"))
        if session in seen:
            raise ValueError(f"duplicate effective session_date {session} across V3/V4 ({seen[session]} and {source})")
        seen[session] = source
    return sorted(records, key=lambda row: str(row.get("session_date", "")))
