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
V4_ROUTER = "personal-ops/indexes/check-ins-v4.md"


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], dict[str, Any], str]:
    return parse_frontmatter_and_properties(path.read_text(encoding="utf-8"), path)


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
        if_data = review_process.get("if")
        if isinstance(if_data, dict):
            calories = _numeric_json_value(if_data.get("calories"))
            if calories is not None:
                normalized["previous_day_actual_calories_representative"] = calories
                if "approximate" in if_data:
                    normalized["previous_day_actual_calories_approximate"] = str(if_data["approximate"]).lower()

    return normalized


def required_schema(kind: str) -> list[str]:
    raw = json.loads(V4_SCHEMA.read_text(encoding="utf-8"))
    return list(raw["daily_required" if kind == "daily" else "weekly_required"])


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


def validate_daily(top: dict[str, Any], properties: dict[str, Any], path: Path) -> None:
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
    items = json_value(properties, "planned_items_json", [])
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        raise ValueError(f"planned_items_json must be an array of objects: {path}")
    ids = [str(item.get("id", "")) for item in items]
    if any(not item_id for item_id in ids) or len(ids) != len(set(ids)):
        raise ValueError(f"planned_items_json contains missing or duplicate IDs: {path}")
    if properties.get("plan_vs_reality_gap", "") != "":
        gap = int(str(properties["plan_vs_reality_gap"]))
        if gap < 0 or gap > 5:
            raise ValueError(f"plan_vs_reality_gap must be 0-5: {path}")
    if properties.get("recovery_cost", "") != "":
        cost = int(str(properties["recovery_cost"]))
        if cost < -2 or cost > 2:
            raise ValueError(f"recovery_cost must be -2..2: {path}")


def validate_weekly(top: dict[str, Any], properties: dict[str, Any], path: Path) -> None:
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
    validate_daily(top, properties, path)
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
    validate_weekly(top, properties, path)
    return top, properties, body


def load_v4_daily_records(workspace: Path) -> list[dict[str, Any]]:
    root = workspace / V4_DAILY_ROOT
    if not root.is_dir():
        return []
    records = []
    seen: set[str] = set()
    for path in sorted(root.glob("*/*.md")):
        top, properties, _ = parse_frontmatter(path)
        validate_daily(top, properties, path)
        session = str(properties["session_date"])
        if session in seen:
            raise ValueError(f"duplicate V4 session_date: {session}")
        seen.add(session)
        records.append(properties)
    return records


def load_official_v4_records(workspace: Path) -> list[dict[str, Any]]:
    router = workspace / V4_ROUTER
    index = workspace / V4_INDEX
    if not router.exists() and not index.exists():
        return load_v4_daily_records(workspace)
    if not router.is_file() or not index.is_file():
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
