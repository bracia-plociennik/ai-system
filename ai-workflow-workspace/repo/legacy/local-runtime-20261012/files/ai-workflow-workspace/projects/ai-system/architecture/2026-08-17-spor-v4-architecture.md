# SPOR V4 Architecture

## Decisions

- V3 remains immutable and read-compatible.
- Native V4 daily reports live under `personal-ops/check-ins-v4/YYYY/`.
- Native V4 weekly reports live under `personal-ops/weekly-check-ins-v4/YYYY/`.
- V4 indexes are separate; the read model merges fresh official V3 and V4 JSONL records by unique `session_date`.
- A duplicate effective date is a STOP, not a precedence decision.
- Monday Daily is the canonical per-day source for Friday-Sunday. Saturday Weekly may contain a Friday aggregate, but readers never sum that aggregate with a later Friday Daily fact.

## Daily V4

The flat properties map adds review-window metadata, SPOR review JSON, owner overrides, OSNR checkpoints, `plan_vs_reality_gap`, `recovery_cost`, explicit `planned_schedule_variant`, and `planned_items_json` items with optional `block_id`.

## Weekly V4

The combined artifact contains separate retrospective `review_*` properties and future `plan_*` properties. Only `future_plan_items_json` is eligible for TaskNotes. The artifact is `private-sensitive` and never becomes trends input without sanitization.

## Rendering

The daily renderer uses the local schedule configuration and explicit block IDs. It renders a chronological table and preserves unallocated tasks in a separate section. The weekly renderer emits a scorecard and a Monday-Friday future allocation table.

## Privacy

V4 indexes retain private values only in detailed-private local artifacts. Sanitized trends contain aggregate operational signals and never raw review text, finances, calories, macro, sleep detail, or client facts.
