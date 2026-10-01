"""Loss-accounted, private V4 aggregate generations; canonical schemas unchanged."""

from __future__ import annotations

import csv
import fcntl
import hashlib
import importlib.machinery
import importlib.util
import io
import json
import os
import re
import shutil
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from personal_ops_properties_v3 import load_schema as v3_fields
from personal_ops_v4 import daily_index_fields, load_v4_daily_records, json_value

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = "personal-ops-aggregate-v4-v1"
ACTIVE = "personal-ops/indexes/check-ins-v4-active"
STORE = "personal-ops/aggregate-sources-v4"
FILES = ("check-ins-v4.jsonl", "check-ins-v4.csv", "check-ins-v4.metrics.csv",
         "check-ins-v4.md", "check-ins-v4.trends.md", "check-ins-v4-fields.md")
EXCLUDED = {"attachments_json", "ocr_entries_json"}
EXTRA = set("artifact_kind current_state_json daily_plan_contract readable_body_contract planned_macro_profile planned_schedule_variant planned_training_focus review_window_scope routine_completion_status source_week_id task_generation_reason earliest_deadline latest_deadline wig_deadline wig_id wig_kind wig_contingency_deadline previous_day_actual_calories_approximate previous_day_finance_approximate life_alignment_resolution_json life_alignment_contract".split())
LEGACY_EXTRA = set("source_provider source_row_id day_mode energy_subjective mental_subjective body_subjective routine_state_subjective limitations_subjective minimum_day_done habit_count_done habit_count_total has_built has_delivered has_promoted has_body_action has_spirit_action has_close_people_action has_gratitude has_threat has_plus_one has_redundant date_weekday_conflict dynamic_habit_done_count dynamic_habit_partial_count dynamic_habit_not_completed_count dynamic_habit_unknown_count".split())
V2_FIELDS = LEGACY_EXTRA | set("date file_path sleep_start sleep_end sleep_hours if_start if_end if_hours training_start training_end training_minutes nsdr_start nsdr_end nsdr_minutes attachment_count ocr_count screenshot_count note_image_count schema_version session_date previous_day_date timezone normalization_authority report_revision task_generation_status private_index_policy plan_readiness overload_status overload_reasons overload_acknowledged wig_plan_item_id wig_definition_of_done must_do_plan_item_ids task_candidate_eligible_count source_type source_label privacy_class weekday recording_time work_mode organism_mode minimum_day_status private_finance_present private_calories_present private_health_present private_attachment_present planned_training_start planned_training_end planned_training_type planned_training_minutes actual_training_start actual_training_end actual_training_type actual_training_performed actual_training_minutes actual_training_rpe planned_nsdr_start planned_nsdr_end planned_nsdr_minutes actual_nsdr_start actual_nsdr_end actual_nsdr_minutes actual_nsdr_effect actual_nsdr_performed planned_if_start planned_if_end planned_if_minutes actual_if_start actual_if_end actual_if_minutes planned_calories_min planned_calories_max planned_calories_representative planned_budget_max planned_budget_currency actual_calories_min actual_calories_max actual_calories_representative finance_amount finance_currency finance_approximate sleep_quality_score sleep_awakenings sleep_approximate mental_clarity_score body_readiness_score health_notes routine_wakeup routine_hygiene_mantra routine_kitchen routine_outdoors routine_deep_focus routine_close_people_wishes routine_done_count routine_total_count routine_completion_percent reflection_plus_one reflection_redundant reflection_threat reflection_response closure_notes planned_item_count actual_item_count comparison_count planned_build_count planned_deliver_count planned_promote_count planned_self_count planned_close_people_count actual_build_count actual_deliver_count actual_promote_count actual_self_count actual_close_people_count dynamic_habit_count v3_closure_session_date v3_closure_session_path".split())
V2_EXCLUDED = set("sleep_raw planned_training_raw actual_training_raw planned_nsdr_raw actual_nsdr_raw planned_if_raw actual_if_raw planned_budget_raw finance_raw attachment_paths_json interpreted_input".split())
SECRET = re.compile(r"(?i)(-----BEGIN .*PRIVATE KEY|(?:password|passwd|api[_ -]?key|secret|access[_ -]?token|authinfo|credential)\s*[:=]\s*\S+|sk-[A-Za-z0-9]{16,})")
FORBIDDEN_KEY = re.compile(r"(?i)(raw|working_dump|ocr|attachment|password|credential|api_key|access_token|secret)")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative_source(workspace: Path, relative: str) -> Path:
    path = workspace / relative
    if Path(relative).is_absolute() or not path.resolve().is_relative_to(workspace.resolve()):
        raise ValueError("aggregate source escapes workspace")
    if not path.is_file():
        raise ValueError(f"aggregate source missing: {relative}")
    return path


def write_namespace(workspace: Path, path: Path):
    expected = workspace.resolve() / path.relative_to(workspace)
    if path.resolve() != expected:
        raise ValueError("aggregate write namespace contains a symlink")


def script_module(name: str):
    loader = importlib.machinery.SourceFileLoader(name.replace("-", "_"), str(ROOT / ".systems/scripts" / name))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def mapping() -> dict:
    fields = {f["key"]: f for f in v3_fields()}
    fields.update({f["key"]: f for f in daily_index_fields()})
    for key in EXTRA:
        fields.setdefault(key, {"key": key, "private": True, "metric": False, "type": "string"})
    return {key: {"target": f"properties.{key}", "disposition": "exclude-private-evidence" if key in EXCLUDED else "preserve",
                  "private": bool(field.get("private", True)), "metric": bool(field.get("metric")),
                  "rule": "source-value-and-confidence-v1"} for key, field in fields.items()}


def clean_structured(value):
    if isinstance(value, dict):
        audit_keys = {"owner_raw_plan_vs_reality_gap", "attachment_count", "ocr_count", "screenshot_count", "note_image_count", "private_attachment_present"}
        if any(FORBIDDEN_KEY.search(str(key)) and key not in audit_keys for key in value):
            raise ValueError("excluded evidence/secret field nested in structured aggregate data")
        return {k: clean_structured(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_structured(v) for v in value]
    if isinstance(value, str) and SECRET.search(value):
        raise ValueError("possible credential in structured aggregate source; private review required")
    return value


def meaningful(value) -> bool:
    return value is not None and str(value).strip().lower() not in {"", "unknown", "null", "none", "n/a"}


def number(value):
    if isinstance(value, dict):
        value = value.get("value")
    if isinstance(value, bool) or not meaningful(value):
        return None
    try:
        result = float(value)
        return result if result == result and abs(result) != float("inf") else None
    except (ValueError, TypeError):
        return None


def observations(props: dict, confidence: dict) -> list[dict]:
    """Normalize known metric aliases; retain the complete structured source too."""
    closure = str(props.get("closure_date", ""))
    start, end = str(props.get("review_window_start", closure)), str(props.get("review_window_end", closure))
    result = []

    def add(metric, value, key, first=None, last=None, approximate=False):
        value = number(value)
        if value is None or confidence.get(key, "direct") == "unknown":
            return
        first, last = first or start, last or end
        date.fromisoformat(first)
        date.fromisoformat(last)
        if first > last:
            raise ValueError("invalid observation period")
        row = {"metric": metric, "value": value, "period_start": first, "period_end": last,
               "source_field": key, "confidence": confidence.get(key, "direct"), "approximate": bool(approximate)}
        existing = [r for r in result if r["metric"] == metric and r["period_start"] == first and r["period_end"] == last]
        if any(r["value"] != value for r in existing):
            raise ValueError(f"conflicting aggregate metric {metric} in session {props.get('session_date')}")
        if not existing:
            result.append(row)

    for metric, key in (("spending", "previous_day_finance_amount"), ("calories", "previous_day_actual_calories_representative"),
                        ("sleep_quality", "previous_day_sleep_quality_score"), ("sleep_minutes", "previous_day_sleep_minutes")):
        add(metric, props.get(key), key, approximate=str(props.get(key.replace("representative", "approximate"), "")).lower() == "true")

    def dated_entries(obj):
        if not isinstance(obj, dict):
            return []
        dated = obj.get("by_date", obj.get("days", obj.get("values_by_date")))
        if isinstance(dated, dict):
            return [(str(k), v) for k, v in dated.items()]
        if isinstance(dated, list):
            return [(str(v.get("date", "")), v) for v in dated if isinstance(v, dict)]
        return [(str(k), v) for k, v in obj.items() if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(k))]

    def day_key(raw):
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
            return raw
        names = {"friday": 4, "saturday": 5, "sunday": 6}
        if raw in names and start and end:
            current, last = date.fromisoformat(start), date.fromisoformat(end)
            matches = []
            while current <= last:
                if current.weekday() == names[raw]:
                    matches.append(current.isoformat())
                current += timedelta(days=1)
            if len(matches) == 1:
                return matches[0]
        return None

    process = json_value(props, "review_process_json", {})
    if isinstance(process, dict):
        for section, metric, key in (("nutrition", "calories", "calories"), ("if", "calories", "calories"), ("finance", "spending", "amount")):
            obj = process.get(section, {})
            if not isinstance(obj, dict):
                continue
            value = obj.get(key)
            if number(value) is not None:
                add(metric, value, "review_process_json", approximate=obj.get("approximate", False))
            dated = dated_entries(obj)
            if isinstance(value, dict) and number(value) is None:
                dated += list(value.items())
            dated += [(k, v) for k, v in obj.items() if k in {"friday", "saturday", "sunday"}]
            for raw, entry in dated:
                day = day_key(raw)
                if day:
                    add(metric, entry.get(key, entry.get("value")) if isinstance(entry, dict) else entry,
                        "review_process_json", day, day, isinstance(entry, dict) and entry.get("approximate", entry.get("approx", False)))
    state = json_value(props, "review_state_json", {})
    if isinstance(state, dict):
        sleep = state.get("sleep", {})
        def add_sleep(obj, first=None, last=None):
            if isinstance(obj, dict):
                add("sleep_quality", obj.get("quality", obj.get("quality_score")), "review_state_json", first, last)
                add("sleep_minutes", obj.get("minutes", obj.get("duration_minutes")), "review_state_json", first, last, obj.get("approximate", False))
                add("actual_sleep_minutes", obj.get("actual_sleep_minutes"), "review_state_json", first, last, obj.get("approximate", False))
                add("time_in_bed_minutes", obj.get("minutes_in_bed"), "review_state_json", first, last, obj.get("approximate", False))
        add_sleep(sleep)
        for raw, entry in dated_entries(state) + dated_entries(sleep):
            day = day_key(raw)
            if day:
                add_sleep(entry.get("sleep", entry) if isinstance(entry, dict) else entry, day, day)
        for raw in ("friday", "saturday", "sunday"):
            day = day_key(raw)
            entry = state.get(raw, sleep.get(raw) if isinstance(sleep, dict) else None)
            if day and isinstance(entry, dict):
                add_sleep(entry.get("sleep", entry), day, day)
    return result


def make_row(workspace: Path, props: dict, source: str, source_version: str, legacy=None, extensions=None) -> dict:
    field_map = mapping()
    unknown = [k for k, v in props.items() if k not in field_map and meaningful(v)]
    if unknown:
        raise ValueError("unmapped nonempty aggregate fields: " + ", ".join(sorted(unknown)))
    confidence = (legacy or {}).get("field_confidence", {})
    redacted = props.get("private_index_policy") == "redacted"
    values, provenance, excluded = {}, {}, []
    source_path = relative_source(workspace, source)
    source_hash = digest(source_path)
    for key, value in props.items():
        if key in EXCLUDED or key not in field_map or redacted and field_map[key]["private"]:
            excluded.append(key)
            continue
        certainty = confidence.get(key, "direct" if meaningful(value) else "unknown")
        if key.endswith("_json") and meaningful(value):
            clean_structured(json.loads(value) if isinstance(value, str) else value)
        else:
            clean_structured(value)
        values[key] = value
        provenance[key] = {"confidence": certainty, "source_field": key, "rule": "source-value-and-confidence-v1"}
    original = {"path": source, "sha256": source_hash, "schema_version": source_version}
    if legacy:
        original["legacy_contract"] = legacy.get("origin", {}).get("source_contract")
        original["source_range"] = clean_structured(legacy.get("origin", {}).get("source_range", "unknown"))
    row = {"aggregate_contract": CONTRACT, "properties": values, "source": original, "provenance": provenance,
           "excluded_fields": sorted(excluded), "observations": observations(values, {k: p["confidence"] for k, p in provenance.items()}),
           "extensions": {} if redacted else clean_structured(extensions or {})}
    if legacy and not redacted:
        row["extensions"]["legacy_minimum_day_done"] = legacy.get("legacy_minimum_day_done", "")
    return row


def legacy_extensions(workspace: Path) -> tuple[dict, dict]:
    by_source, hashes = {}, {}
    for path in sorted((workspace / "personal-ops/archive/indexes/v2").glob("*/check-ins.csv")):
        if not path.resolve().is_relative_to(workspace.resolve()):
            raise ValueError("legacy archive escapes workspace")
        rel = path.relative_to(workspace).as_posix()
        hashes[rel] = digest(path)
        with path.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                source = row.get("file_path")
                if not source:
                    continue
                unknown = [k for k, v in row.items() if meaningful(v) and k not in V2_FIELDS | V2_EXCLUDED and not k.startswith("habit_")]
                if unknown:
                    raise ValueError("unmapped V2 archive fields: " + ", ".join(unknown))
                safe = {k: clean_structured(v) for k, v in row.items() if meaningful(v) and (k in V2_FIELDS or k.startswith("habit_"))}
                # Counts of private evidence are retained; its contents and paths are not.
                by_source.setdefault(source, []).append({"values": safe, "archive_date": row.get("date"), "source": rel, "sha256": hashes[rel], "date_basis": "source-path; archive_date is not a session/fact date"})
    return by_source, hashes


def build_initial(workspace: Path) -> tuple[list, dict, list]:
    old = script_module("sync-personal-ops-check-ins-v3")
    v3, _ = old.load_records(workspace)
    extra, hashes = legacy_extensions(workspace)
    history = []
    for record in v3:
        props = record["properties"]
        source = str(props["file_path"])
        row = make_row(workspace, props, source, "2" if record["record_kind"] == "legacy" else "3",
                       record.get("legacy_metadata"), {"legacy_v2": extra[source]} if source in extra else {})
        history.append(row)
    rows = history + native_rows(workspace)
    unmatched = set(extra) - {r["source"]["path"] for r in rows}
    if unmatched:
        raise ValueError("legacy archive sources without matched session: " + ", ".join(sorted(unmatched)))
    check_rows(rows)
    for row in rows:
        hashes[row["source"]["path"]] = row["source"]["sha256"]
    for path in (workspace / "personal-ops/archive/check-ins-v3-migration").glob("*"):
        if path.is_file():
            hashes[path.relative_to(workspace).as_posix()] = digest(path)
    for directory in ("check-ins", "check-ins-v3"):
        for path in (workspace / "personal-ops" / directory).glob("*/*.md"):
            hashes[path.relative_to(workspace).as_posix()] = digest(relative_source(workspace, path.relative_to(workspace).as_posix()))
    return sorted(rows, key=lambda r: r["properties"]["session_date"]), hashes, history


def native_rows(workspace: Path) -> list:
    rows = []
    for props in load_v4_daily_records(workspace):
        source = f"personal-ops/check-ins-v4/{str(props['session_date'])[:4]}/{props['session_date']}.md"
        rows.append(make_row(workspace, props, source, "4"))
    return rows


def check_rows(rows):
    sessions = set()
    facts = {}
    for row in rows:
        session = str(row["properties"].get("session_date", ""))
        date.fromisoformat(session)
        if session in sessions:
            raise ValueError(f"duplicate effective aggregate session {session}")
        sessions.add(session)
        for fact in row["observations"]:
            key = fact["metric"], fact["period_start"], fact["period_end"]
            # Equal repeated facts deduplicate in consumers; different values need owner review.
            if key in facts and facts[key] != fact["value"]:
                raise ValueError(f"unresolved historical fact conflict {key[0]}:{key[1]}:{key[2]}")
            facts[key] = fact["value"]


def is_unified(workspace: Path) -> bool:
    return (workspace / ACTIVE).is_symlink() or (workspace / ACTIVE).exists()


def active_root(workspace: Path) -> Path:
    pointer = workspace / ACTIVE
    if not pointer.is_symlink():
        raise ValueError("unified aggregate active pointer must be a symlink")
    root = pointer.resolve()
    allowed = (workspace / "personal-ops/indexes/generations-v4").resolve()
    if root.parent != allowed or not root.is_dir():
        raise ValueError("invalid unified aggregate generation pointer")
    return root


def verify_sources(workspace: Path, hashes: dict):
    for source, expected in hashes.items():
        if digest(relative_source(workspace, source)) != expected:
            raise ValueError(f"aggregate source changed: {source}; refresh/reconciliation required")


def read_generation(workspace: Path, fresh=True) -> tuple[list, dict]:
    root = active_root(workspace)
    for name in (*FILES, "manifest.json"):
        if (root / name).is_symlink():
            raise ValueError("unified aggregate generation contains a symlink")
    manifest = json.loads((root / "manifest.json").read_text())
    if manifest.get("contract") != CONTRACT or set(manifest.get("outputs", {})) != set(FILES):
        raise ValueError("invalid unified aggregate manifest")
    if manifest.get("generation") != root.name:
        raise ValueError("unified aggregate generation identity mismatch")
    for name, expected in manifest["outputs"].items():
        if digest(root / name) != expected:
            raise ValueError(f"unified aggregate output hash mismatch: {name}")
    if fresh:
        verify_sources(workspace, manifest["sources"])
        expected_native = {r["source"]["path"] for r in native_rows(workspace)}
        if expected_native != set(manifest["native_sources"]):
            raise ValueError("unified aggregate native source inventory changed; refresh required")
        historical_inventory = {p.relative_to(workspace).as_posix() for d in ("check-ins", "check-ins-v3") for p in (workspace / "personal-ops" / d).glob("*/*.md")}
        expected_history = {s for s in manifest["sources"] if s.startswith(("personal-ops/check-ins/", "personal-ops/check-ins-v3/"))}
        if historical_inventory != expected_history:
            raise ValueError("historical source inventory changed; reconciliation required")
    rows = [json.loads(line) for line in (root / FILES[0]).read_text().splitlines() if line]
    if len(rows) != manifest["record_count"] or any(r.get("aggregate_contract") != CONTRACT for r in rows):
        raise ValueError("unified aggregate row contract/count mismatch")
    check_rows(rows)
    expected_id = hashlib.sha256(json.dumps([rows, manifest["sources"], manifest["mapping"]], sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:24]
    if expected_id != root.name:
        raise ValueError("unified aggregate content identity mismatch")
    return rows, manifest


def read_properties(workspace: Path) -> list:
    rows, _ = read_generation(workspace)
    return [{**{k: "" if r["provenance"][k]["confidence"] == "unknown" else v for k, v in r["properties"].items()},
             "aggregate_observations": r["observations"], "aggregate_provenance": r["provenance"], "aggregate_source_path": r["source"]["path"]} for r in rows]


def budget_facts(records: list, start: date, end: date, metric: str) -> tuple[list, dict]:
    """Deduplicate dated observations and count a whole-period amount at most once."""
    selected = {}
    uncertain = []
    for row in records:
        if "aggregate_observations" not in row:
            continue
        for fact in row["aggregate_observations"]:
            first, last = fact["period_start"], fact["period_end"]
            if fact["metric"] != metric or first > end.isoformat() or last < start.isoformat():
                continue
            key = first, last
            if first < start.isoformat() or last > end.isoformat() or metric == "calories" and first != last:
                uncertain.append(fact)
                continue
            if key in selected and selected[key]["value"] != fact["value"]:
                raise ValueError(f"conflicting budget fact {metric}:{first}")
            selected[key] = {**fact, "session_date": row["session_date"]}
    ordered = sorted(selected.values(), key=lambda f: (f["period_end"], f["period_start"]))
    covered = set()
    result = []
    for fact in ordered:
        first, last = date.fromisoformat(fact["period_start"]), date.fromisoformat(fact["period_end"])
        days = {(first + timedelta(days=i)).isoformat() for i in range((last-first).days+1)}
        if days & covered:
            raise ValueError(f"overlapping budget periods for {metric}; owner reconciliation required")
        result.append(fact)
        covered |= days
    expected = {(start + timedelta(days=i)).isoformat() for i in range(max(0, (end-start).days+1))}
    return result, {"known_dates": sorted(covered), "missing_dates": sorted(expected-covered), "unallocated_aggregates": uncertain,
                    "status": "complete" if expected <= covered and not uncertain else "partial-known-subtotal"}


@contextmanager
def writer_lock(workspace: Path):
    directory = workspace / "personal-ops/indexes"
    for relative in ("personal-ops/indexes", "personal-ops/indexes/generations-v4", STORE, "personal-ops/archive/indexes"):
        write_namespace(workspace, workspace / relative)
    directory.mkdir(parents=True, exist_ok=True)
    write_namespace(workspace, directory / ".personal-ops-v4.lock")
    with (directory / ".personal-ops-v4.lock").open("a") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError("another Personal Ops aggregate writer is active") from exc
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def csv_text(rows, fields):
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields)
    writer.writeheader()
    for row in rows:
        writer.writerow({k: json.dumps(row[k], ensure_ascii=False, sort_keys=True) if isinstance(row.get(k), (dict, list)) else row.get(k, "") for k in fields})
    return out.getvalue()


def build_outputs(rows, generation):
    field_map = mapping()
    exported = [{**r["properties"], "aggregate_contract": CONTRACT, "source_schema_version": r["source"]["schema_version"],
                 "provenance_json": r["provenance"], "observations_json": r["observations"], "legacy_extensions_json": r["extensions"]} for r in rows]
    keys = sorted((set(field_map) - EXCLUDED) | {"aggregate_contract", "source_schema_version", "provenance_json", "observations_json", "legacy_extensions_json"})
    metrics = sorted({k for k, v in field_map.items() if v["metric"] and k not in EXCLUDED} | {"session_date", "closure_date", "source_schema_version", "observations_json"})
    metric_values = [{**p, **{k: "" for k, v in r["provenance"].items() if v["confidence"] == "unknown"}}
                     for p, r in zip(exported, rows)]
    native_count = sum(r["source"]["schema_version"] == "4" for r in rows)
    router = f"# Unified Check-Ins V4 Index\n\ncontract: {CONTRACT}\ngeneration: {generation}\nrecord-count: {len(rows)}\nnative-v4-check-in-count: {native_count}\nlast-synced-v4-check-in-count: {native_count}\nunsynced-v4-check-in-count: 0\nsource: hashed canonical properties and immutable historical import\n"
    # Only categorical values on an explicit allowlist; never interpolate source text.
    modes, organisms = {}, {}
    for row in rows:
        p = row["properties"]
        if p.get("private_index_policy") == "redacted":
            continue
        for key, counts, allowed in (("work_mode", modes, {"growth", "normal", "reputation_defense"}), ("organism_mode", organisms, {"normal", "full_power", "regeneration", "recovery"})):
            if p.get(key) in allowed and row["provenance"].get(key, {}).get("confidence") != "unknown":
                counts[p[key]] = counts.get(p[key], 0) + 1
    trends = f"# Sanitized V4 Personal Ops Trends\n\ncontract: {CONTRACT}\nreport-count: {len(rows)}\nwork-mode-counts: {json.dumps(modes, sort_keys=True)}\norganism-mode-counts: {json.dumps(organisms, sort_keys=True)}\n"
    dictionary = "# V4 Aggregate Field Dictionary\n\nAggregate version does not replace source schema version. Private local exports only.\n\n| Source key | Target | Disposition | Rule |\n| --- | --- | --- | --- |\n" + "".join(f"| {k} | {v['target']} | {v['disposition']} | {v['rule']} |\n" for k, v in sorted(field_map.items()))
    return dict(zip(FILES, ("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows), csv_text(exported, keys), csv_text(metric_values, metrics), router, trends, dictionary)))


def atomic_json(path: Path, payload):
    temp = path.with_name(path.name + ".pending")
    if path.is_symlink() or temp.is_symlink():
        raise ValueError("aggregate JSON output contains a symlink")
    with temp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)
    sync_directory(path.parent)


def sync_directory(path: Path):
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def stage_generation(workspace, rows, hashes, history, source):
    content_id = hashlib.sha256(json.dumps([rows, hashes, mapping()], sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:24]
    directory = workspace / "personal-ops/indexes/generations-v4" / content_id
    write_namespace(workspace, directory)
    directory.parent.mkdir(parents=True, exist_ok=True)
    if not directory.exists():
        stage = directory.with_name(".stage-" + content_id)
        write_namespace(workspace, stage)
        if stage.exists():
            shutil.rmtree(stage)
        stage.mkdir()
        outputs = build_outputs(rows, content_id)
        for name, text in outputs.items():
            (stage / name).write_text(text, encoding="utf-8", newline="")
        manifest = {"contract": CONTRACT, "generation": content_id, "record_count": len(rows), "sources": hashes,
                    "native_sources": sorted(r["source"]["path"] for r in rows if r["source"]["schema_version"] == "4"),
                    "outputs": {name: digest(stage / name) for name in outputs}, "history_sha256": hashlib.sha256(json.dumps(history, sort_keys=True).encode()).hexdigest(),
                    "mapping": mapping(), "source": source, "created_at": datetime.now(timezone.utc).isoformat()}
        atomic_json(stage / "manifest.json", manifest)
        for path in stage.iterdir():
            with path.open("rb") as handle:
                os.fsync(handle.fileno())
        sync_directory(stage)
        os.replace(stage, directory)
        sync_directory(directory.parent)
    else:
        manifest = json.loads((directory / "manifest.json").read_text())
        for name, expected in manifest["outputs"].items():
            if digest(directory / name) != expected:
                raise ValueError("existing aggregate candidate is corrupt")
    return directory


def select_generation(workspace, directory):
    pointer = workspace / ACTIVE
    temp = pointer.with_name(pointer.name + ".pending")
    temp.unlink(missing_ok=True)
    temp.symlink_to(os.path.relpath(directory, pointer.parent), target_is_directory=True)
    os.replace(temp, pointer)
    sync_directory(pointer.parent)


def verify_native_inventory(workspace, rows):
    expected = {r["source"]["path"] for r in rows if r["source"]["schema_version"] == "4"}
    actual = {r["source"]["path"] for r in native_rows(workspace)}
    if actual != expected:
        raise ValueError("native source inventory changed during candidate preparation")


def refresh(workspace, source="post-write-check-in"):
    with writer_lock(workspace):
        store = workspace / STORE
        history = json.loads((store / "history.json").read_text())
        stored = json.loads((store / "manifest.json").read_text())
        if digest(store / "history.json") != stored["history_file_sha256"]:
            raise ValueError("historical aggregate input hash mismatch")
        verify_sources(workspace, stored["historical_sources"])
        historical_inventory = {p.relative_to(workspace).as_posix() for d in ("check-ins", "check-ins-v3") for p in (workspace / "personal-ops" / d).glob("*/*.md")}
        expected_history = {s for s in stored["historical_sources"] if s.startswith(("personal-ops/check-ins/", "personal-ops/check-ins-v3/"))}
        if historical_inventory != expected_history:
            raise ValueError("historical source inventory changed; reconciliation required")
        rows = history + native_rows(workspace)
        check_rows(rows)
        hashes = {**stored["historical_sources"], **{r["source"]["path"]: r["source"]["sha256"] for r in rows}}
        directory = stage_generation(workspace, rows, hashes, history, source)
        verify_sources(workspace, hashes)
        verify_native_inventory(workspace, rows)
        select_generation(workspace, directory)
        return {"generation": directory.name, "record_count": len(rows), "unsynced": 0}


def migration(workspace, apply=False):
    if is_unified(workspace):
        if apply:
            with writer_lock(workspace):
                finish_archive(workspace)
        rows, manifest = read_generation(workspace)
        return {"status": "already-active", "generation": manifest["generation"], "record_count": len(rows)}
    rows, hashes, history = build_initial(workspace)
    if any(p.is_symlink() for p in (workspace / "personal-ops/indexes").glob("check-ins*")):
        raise ValueError("unmigrated aggregate indexes contain unsupported symlinks")
    report = {"status": "dry-run", "contract": CONTRACT, "record_count": len(rows), "historical_count": len(history),
              "native_count": len(rows) - len(history), "unmapped_fields": [], "conflicts": [], "mapping": mapping(),
              "source_count": len(hashes), "excluded_evidence_fields": sorted(EXCLUDED)}
    if not apply:
        return report
    with writer_lock(workspace):
        # Re-read under lock; no candidate may activate against a changed inventory.
        locked_rows, locked_hashes, locked_history = build_initial(workspace)
        if (rows, hashes, history) != (locked_rows, locked_hashes, locked_history):
            raise ValueError("migration input changed during preparation")
        directory = stage_generation(workspace, rows, hashes, history, "owner-approved-migration")
        store = workspace / STORE
        store.mkdir(parents=True, exist_ok=True)
        atomic_json(store / "history.json", history)
        historical_sources = {k: v for k, v in hashes.items() if k not in {r["source"]["path"] for r in rows if r["source"]["schema_version"] == "4"}}
        atomic_json(store / "manifest.json", {"contract": CONTRACT, "history_file_sha256": digest(store / "history.json"), "historical_sources": historical_sources})
        archive = workspace / "personal-ops/archive/indexes" / ("unified-v4-" + directory.name)
        write_namespace(workspace, archive)
        archive.mkdir(parents=True, exist_ok=True)
        index = workspace / "personal-ops/indexes"
        old_files = sorted(p for p in index.glob("check-ins*") if p.is_file() and not p.is_symlink())
        for path in old_files:
            write_namespace(workspace, archive / path.name)
            shutil.copy2(path, archive / path.name)
            with (archive / path.name).open("rb") as handle:
                os.fsync(handle.fileno())
        sync_directory(archive)
        journal = {"contract": CONTRACT, "generation": directory.name, "archive": archive.relative_to(workspace).as_posix(),
                   "prior_outputs": {p.name: digest(p) for p in old_files}, "status": "prepared"}
        atomic_json(store / "migration.json", journal)
        verify_sources(workspace, hashes)
        verify_native_inventory(workspace, rows)
        select_generation(workspace, directory)
        finish_archive(workspace)
    return {**report, "status": "active-and-archived", "generation": directory.name, "archive": journal["archive"]}


def finish_archive(workspace):
    store = workspace / STORE
    journal = json.loads((store / "migration.json").read_text())
    archive = workspace / journal["archive"]
    write_namespace(workspace, archive)
    if not archive.resolve().is_relative_to((workspace / "personal-ops/archive/indexes").resolve()):
        raise ValueError("archive journal escapes approved namespace")
    index = workspace / "personal-ops/indexes"
    for name, expected in journal["prior_outputs"].items():
        if Path(name).name != name or not name.startswith("check-ins") or digest(archive / name) != expected:
            raise ValueError("rollback archive hash/name mismatch")
        write_namespace(workspace, archive / name)
        path = index / name
        if path.exists() and not path.is_symlink():
            if digest(path) != expected:
                raise ValueError("prior active index changed during archival")
            path.unlink()
    for name in FILES:
        path = index / name
        expected = "check-ins-v4-active/" + name
        if path.is_symlink():
            if os.readlink(path) != expected:
                raise ValueError("conflicting V4 compatibility link")
        elif not path.exists():
            path.symlink_to(expected)
        else:
            raise ValueError("unexpected V4 compatibility file")
    journal["status"] = "active-and-archived"
    sync_directory(index)
    atomic_json(store / "migration.json", journal)


def rollback(workspace):
    with writer_lock(workspace):
        journal = json.loads((workspace / STORE / "migration.json").read_text())
        archive = workspace / journal["archive"]
        write_namespace(workspace, archive)
        if not archive.resolve().is_relative_to((workspace / "personal-ops/archive/indexes").resolve()):
            raise ValueError("rollback journal archive escapes workspace")
        for name, expected in journal["prior_outputs"].items():
            write_namespace(workspace, archive / name)
            if Path(name).name != name or not name.startswith("check-ins") or digest(archive / name) != expected:
                raise ValueError("rollback archive hash/name mismatch")
        # Rebuild compatibility outputs from current sources before withdrawing V4-only mode.
        old = script_module("sync-personal-ops-check-ins-v3")
        records, fields = old.load_records(workspace)
        native = native_rows(workspace)
        sync = script_module("sync-personal-ops-check-ins-v4")
        v4_props = [r["properties"] for r in native]
        stage = workspace / "personal-ops/indexes/.rollback-v4"
        stage.mkdir(exist_ok=True)
        # Write rebuilt files while unified readers still resolve their immutable generation.
        index = workspace / "personal-ops/indexes"
        for name in FILES:
            path = index / name
            if path.is_symlink():
                path.unlink()
        old.write_indexes(records, fields, workspace, False, "owner-approved-rollback")
        outputs = {index / name: text for name, text in dict(zip(FILES[:5], (sync.render_jsonl(v4_props), sync.render_csv(v4_props, daily_index_fields()), sync.render_csv(v4_props, daily_index_fields(), True), sync.render_router(len(native), workspace, "rollback"), sync.render_trends(v4_props)))).items()}
        sync.write_index_set_atomic(outputs)
        for name, expected in journal["prior_outputs"].items():
            if name.startswith("check-ins-v3") or name in FILES:
                continue
            if digest(archive / name) != expected:
                raise ValueError("rollback archive corrupt")
            shutil.copy2(archive / name, index / name)
        (workspace / ACTIVE).unlink()
        stage.rmdir()
        journal["status"] = "rolled-back-with-current-sources"
        atomic_json(workspace / STORE / "migration.json", journal)
    return {"status": journal["status"], "native_count": len(native), "historical_count": len(records)}
