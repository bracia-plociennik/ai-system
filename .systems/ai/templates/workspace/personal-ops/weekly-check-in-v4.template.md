---
type: weekly-check-in-v4
schema_version: 4
index_contract: 4
report_id: <YYYY-Www>
properties:
  index_contract: 4
  schema_version: 4
  artifact_kind: weekly
  report_id: <YYYY-Www>
  review_week_start: <YYYY-MM-DD>
  review_week_end: <YYYY-MM-DD>
  plan_week_start: <YYYY-MM-DD>
  plan_week_end: <YYYY-MM-DD>
  privacy: private-sensitive
  private_index_policy: detailed-private
  review_state_json: "{}"
  review_process_json: "{}"
  review_outcome_json: "{}"
  review_review_json: "{}"
  future_wig_json: "{}"
  future_plan_items_json: "[]"
  daily_blocks_json: "[]"
  task_generation_policy: commitment-first-6d-v1
  task_generation_status: proposal-only
---

# Weekly Check-In V4 <YYYY-Www>

## Miniony tydzień — STATE / PROCESS / OUTCOME / REVIEW

Use the four JSON properties as the canonical structured review. Do not duplicate Friday as a separate daily artifact.

## Przyszły tydzień

`future_wig_json`, `future_plan_items_json`, and `daily_blocks_json` are the only sources for the next-week operational plan and TaskNote candidates.

## Raw Weekly Check-In

<paste owner message verbatim>
