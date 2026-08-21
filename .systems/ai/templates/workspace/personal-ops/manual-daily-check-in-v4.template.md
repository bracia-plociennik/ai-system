---
type: daily-check-in-v4
schema_version: 4
index_contract: 4
session_date: <YYYY-MM-DD>
closure_date: <YYYY-MM-DD>
properties:
  index_contract: 4
  schema_version: 4
  artifact_kind: daily
  report_id: <YYYY-MM-DD>
  session_date: <YYYY-MM-DD>
  closure_date: <YYYY-MM-DD>
  review_window_start: <YYYY-MM-DD>
  review_window_end: <YYYY-MM-DD>
  review_window_kind: previous-day
  privacy: private-sensitive
  private_index_policy: detailed-private
  work_mode:
  organism_mode:
  planned_schedule_variant: standard
  daily_plan_contract: per-day-schedule-v1
  planned_schedule_json: "[]"
  readable_body_contract: spor-readable-v1
  current_state_json: "{}"
  wig_title:
  wig_definition_of_done:
  wig_plan_item_id:
  planned_items_json: "[]"
  review_state_json: "{}"
  review_process_json: "{}"
  review_outcome_json: "{}"
  review_review_json: "{}"
  owner_overrides_json: "[]"
  osnr_checkpoints_json: "[]"
  plan_vs_reality_gap:
  recovery_cost:
  task_generation_policy: commitment-first-6d-v1
  task_generation_status: proposal-only
  task_generation_references_json: "[]"
---

# Daily Check-In V4 <YYYY-MM-DD>

## Plan na dziś

Use `planned_items_json` as the machine-readable source. Each professional item must reference a `block_id` from `planned_schedule_json` and may include `definition_of_done`, `deadline`, and `mapping`. The per-day schedule is canonical for this date; local variants are legacy fallback only. Meal rows use `kind: meal` and unique `meal_slot` values `1`, `2`, and `3`.

After a successful post-write refresh, render the chat-only plan with:

```text
.systems/scripts/render-personal-ops-daily-summary-v4 --workspace <workspace> --date <YYYY-MM-DD>
```

Paste its output verbatim. The linked WIG receives separate `WIG` and stream markers. The output includes the chronological table with meals, six macro blocks, full spending and calorie calculations, TaskNote status, warnings, and the read-only disclaimer.

## STATE

Current state and previous review window are kept in the JSON properties above. Add a concise, non-empty readable summary for the current STATE here.

`current_state_json` is the private source for the post-write `Stan i kierunek dnia` projection. Use this shape without filling missing values from Raw Check-In:

```json
{"mental":{"score":4,"note":""},"body":{"score":4,"note":""},"constraints":[{"title":"","mitigation":""}],"work_mode_reason":"","organism_mode_reason":"","self":[],"close_ones":[]}
```

## PROCESS

Summarize the reviewed PROCESS here. Training, NSDR, IF, nutrition, budget, habits, checkpoints, and Owner's Overrides remain private-sensitive.

## OUTCOME

Record readable outcome facts for the review window without reinterpreting missing values.

## REVIEW

Summarize REVIEW here. Keep the full owner message in `## Raw Check-In`; quotes and external references remain advisory unless separately verified.

## Raw Check-In

<paste owner message verbatim>

<!-- ai-system:working-dump:start -->
## Working Dump
<!-- ai-system:working-dump:end -->
