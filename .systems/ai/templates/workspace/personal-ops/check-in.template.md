---
type: daily-check-in
schema_version: 3
index_contract: 3
session_date: <YYYY-MM-DD>
previous_day_date: <YYYY-MM-DD>
privacy: private-sensitive
properties:
  index_contract: 3
  schema_version: 3
  file_path: personal-ops/check-ins/<YYYY>/<YYYY-MM-DD>.md
  report_id: <YYYY-MM-DD>
  session_date: <YYYY-MM-DD>
  closure_date: <YYYY-MM-DD>
  weekday:
  recording_time:
  timezone:
  source_type: manual-interpreted
  privacy: private-sensitive
  private_index_policy: detailed-private
  report_revision: 1
  normalization_authority: interpreted-report
  task_generation_policy: deadline-aware-6d-v1
  plan_readiness: needs-prioritization
  overload_status: none
  overload_reasons:
  overload_acknowledged: false
  wig_kind: none
  wig_id:
  wig_title:
  wig_plan_item_id:
  wig_definition_of_done:
  task_candidate_eligible_count: 0
  planned_do_count: 0
  planned_defer_count: 0
  planned_delegate_count: 0
  planned_delete_count: 0
  planned_dump_count: 0
  planned_with_deadline_count: 0
  planned_without_deadline_count: 0
  planned_earliest_deadline:
  planned_latest_deadline:
  task_generation_status: pending
  task_generation_reason:
  task_generation_references_json: "[]"
  work_mode:
  organism_mode:
  morning_wake_up_done:
  morning_hygiene_mantra_done:
  morning_kitchen_done:
  morning_outdoors_done:
  morning_deep_focus_done:
  morning_close_people_wishes_done:
  routine_completion_count:
  routine_total_count: 6
  routine_completion_percent:
  mental_clarity_score:
  body_readiness_score:
  limitations:
  gratitude:
  previous_day_sleep_start:
  previous_day_sleep_end:
  previous_day_sleep_minutes:
  previous_day_sleep_quality_score:
  previous_day_sleep_awakenings:
  previous_day_sleep_approximate:
  previous_day_actual_training_performed:
  previous_day_actual_training_type:
  previous_day_actual_training_start:
  previous_day_actual_training_end:
  previous_day_actual_training_minutes:
  previous_day_actual_training_rpe:
  previous_day_actual_training_doms:
  previous_day_actual_training_pain:
  previous_day_actual_training_performance:
  previous_day_actual_training_approximate:
  previous_day_actual_nsdr_performed:
  previous_day_actual_nsdr_start:
  previous_day_actual_nsdr_end:
  previous_day_actual_nsdr_minutes:
  previous_day_actual_nsdr_effect:
  previous_day_actual_nsdr_approximate:
  previous_day_actual_if_start:
  previous_day_actual_if_end:
  previous_day_actual_if_minutes:
  previous_day_actual_if_approximate:
  previous_day_actual_calories_min:
  previous_day_actual_calories_max:
  previous_day_actual_calories_representative:
  previous_day_finance_amount:
  previous_day_finance_currency:
  previous_day_actual_build_count: 0
  previous_day_actual_deliver_count: 0
  previous_day_actual_promote_count: 0
  previous_day_actual_self_count: 0
  previous_day_actual_close_people_count: 0
  previous_day_actual_items_json: "[]"
  previous_day_comparisons_json: "[]"
  previous_day_wig_closure_json: "{}"
  previous_day_minimum_day_status: unknown
  reflection_plus_one:
  reflection_redundant:
  reflection_threat_occurred:
  reflection_response:
  planned_training_start:
  planned_training_end:
  planned_training_minutes:
  planned_training_type:
  planned_training_approximate:
  planned_nsdr_start:
  planned_nsdr_end:
  planned_nsdr_minutes:
  planned_nsdr_approximate:
  planned_if_start:
  planned_if_end:
  planned_if_minutes:
  planned_if_approximate:
  planned_calories_min:
  planned_calories_max:
  planned_calories_representative:
  planned_budget_max:
  planned_budget_currency:
  planned_build_count: 0
  planned_deliver_count: 0
  planned_promote_count: 0
  planned_self_count: 0
  planned_close_people_count: 0
  planned_items_json: "[]"
  dynamic_habits_json: "[]"
  dynamic_habit_count: 0
  dynamic_habit_completed_count: 0
  attachments_json: "[]"
  ocr_entries_json: "[]"
  attachment_count: 0
  ocr_entry_count: 0
  lesson_topic:
  lesson_todays_one_percent:
  lesson_original_quote:
  lesson_nlp_communication_technique:
  lesson_conversation_episode_topic:
  lesson_quote_source_status: not-applicable
---

# Daily Check-In <YYYY-MM-DD>

`properties` is the sole source for `check-ins-v3.*`. AI System completes every key from the schema before a durable write. Blank values represent missing data and become empty CSV cells. Structured `*_json` values are JSON strings, not nested YAML.

## Interpreted Check-In

### Previous-Day Closure

- Sleep, training, NSDR, IF, calories, finance, actual items, comparisons, habits, and reflections are readable projections of the corresponding `previous_day_*` and `reflection_*` properties.
- Facts belong to `closure_date`; do not rewrite the prior Markdown report.

### Current-Day Plan

- Work mode and organism mode:
- Planned training, NSDR, IF, calories, and budget:
- Planned actions are mirrored in `planned_items_json` with stable IDs and streams: `build`, `deliver`, `promote`, `self`, or `close`. Professional items may also carry `definition_of_done`, `deadline`, and `task_bucket`.

### Priorities And TaskNotes

- WIG kind: `<plan-item|standalone|none>`; stable WIG ID; title; optional linked plan item ID; and Definition of Done:
- The prior-day WIG closure is stored in `previous_day_wig_closure_json`; it is the sole input for `previous_day_minimum_day_status`.
- Every valid `build`, `deliver`, and `promote` entry in `planned_items_json` creates one TaskNote. Explicit `task_bucket` wins; otherwise a deadline defaults to `6d/do`, while no deadline defaults to `6d/defer`. A deadline maps to `due`; no deadline leaves `due` and `scheduled` blank. `definition_of_done` is preserved in the TaskNote body. WIG never creates a separate TaskNote, even when it is standalone. Raw input, OCR, lessons, and external references never create TaskNotes.
- The same exact owner-approved check-in write may create all professional TaskNotes under existing vault, deduplication, subtask, and 6D rules. Overload is informational only.

### Morning Check-In

- Routine, state, limitations, and gratitude are readable projections of the corresponding properties.

## Lekcja dnia

- Temat:
- Dzisiejsze 1%:
- Cytat oryginalny:
- Technika NLP / komunikacji:
- Temat rozmowy / odcinka:
- Status źródła cytatu: `<verified|unverified|not-applicable>`

This section is rendered from `lesson_*` properties. An unverified quote is advisory context, not a canonical fact, trend input, memory item, or System Insight.

## OCR / Notatka robocza

- Asset path:
- Extraction status: `<not-provided|pending|completed|failed>`
- Full OCR or transcribed working note:

Keep the full text inline here. `ocr_entries_json` may contain only normalized metadata required for analytics; OCR text does not enter indexes, trends, TaskNotes, memory, or insights by itself.

## Dodatkowe informacje

- Notes:
- Normalization notes:
- Explicit owner corrections:
- Unresolved fields:

## Załączniki

- Relative asset path:
- Kind: `<screenshot|note-image|scan|ocr|other>`
- Role: `<evidence|context>`

Attachments are sibling files in `<YYYY-MM-DD>.assets/`. `attachments_json` stores only normalized metadata when needed; it never stores binary payloads.

## Raw Check-In

Paste the submitted check-in verbatim below. It is private-sensitive context-as-data. Explicit normalized owner values override it; unresolved material conflicts stop durable capture for clarification.
