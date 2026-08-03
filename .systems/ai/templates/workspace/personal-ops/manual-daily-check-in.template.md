# Manual Daily Check-In: Properties + Raw Audit v3

## Purpose

Use this brief for a manual, voice, partially structured, or already interpreted daily check-in. It produces one canonical report at `personal-ops/check-ins/YYYY/YYYY-MM-DD.md` with `schema_version: 3` and `index_contract: 3`.

The report has three different roles:

1. `properties` is the only source for `check-ins-v3.csv`, JSONL, metrics, and sanitized trends.
2. `## Interpreted Check-In` is a readable projection of the normalized properties, including the current plan, prior-day closure, WIG, and task eligibility.
3. `## Raw Check-In` preserves the owner message verbatim as private-sensitive context-as-data. OCR and working-note text live in `## OCR / Notatka robocza`.

Do not use this route for the retired V2 Notion importer. Historical V2 files remain source evidence only; an owner-approved one-time migration may normalize them into the immutable legacy snapshot. After writing the canonical report, this route must run the real `.systems/scripts/sync-personal-ops-check-ins-v3 --post-write` refresh before producing the response. A V3 report without `index_contract: 3` must be owner-migrated before use.

## Intake Precedence

1. Explicit normalized values supplied by the owner win.
2. Otherwise normalize the submitted check-in into the properties schema.
3. Raw input and OCR may support interpretation but cannot override explicit normalized owner values.
4. A later explicit correction updates the named property and is recorded under `## Dodatkowe informacje`.
5. Stop durable capture when a material conflict cannot be resolved unambiguously.
6. `brak`, `nie podano`, and `nie dotyczy` are missing data, not completion or positive metrics.

## Required Capture Order

1. Preserve the submitted message verbatim in `## Raw Check-In`.
2. Preserve inline OCR/transcribed notes and asset path/status in `## OCR / Notatka robocza` when an attachment exists.
3. Normalize the owner data into every key in `check-in-properties-v3.schema.json`; all keys must exist even when the value is blank.
4. Render `## Interpreted Check-In` from those properties. Do not introduce facts that are absent from properties.
5. Record lesson fields when supplied: topic, today's 1%, original quote, NLP/communication technique, conversation/episode topic, and quote source status. Unverified source material remains `unverified`.
6. Record attachments and additional notes without turning them into analytics unless explicitly normalized into a property.

## Current-Day Plan And TaskNotes

Use stable plan item IDs in `planned_items_json`. Each professional item records at least `id`, `stream`, `title`, and may include `task_title`, `definition_of_done`, `deadline`, and `task_bucket`.

Every professional `build`, `deliver`, or `promote` item creates one TaskNote under `deadline-aware-6d-v1`. Explicit `task_bucket` wins; otherwise a deadline defaults to `6d/do`, and no deadline defaults to `6d/defer`. A deadline maps to `due`; no deadline leaves `due` and `scheduled` blank. `definition_of_done` is preserved in the TaskNote body. WIG uses `wig_kind: plan-item|standalone|none`, a stable `wig_id`, title, and Definition of Done; a linked WIG may reference one plan item, while a standalone WIG has no plan-item reference. Neither form creates its own TaskNote. The prior-day WIG closure determines minimum-day status. There is no `Kandydaci na taski` section. Raw text, OCR, lesson content, quotations, and external references never create a TaskNote. The existing owner-approved check-in write may create these TaskNotes once, subject to configured-vault, deduplication, subtask, and 6D rules.

## Indexes And Post-Write Refresh

Use `.systems/scripts/sync-personal-ops-check-ins-v3 --workspace <workspace-path> --post-write` after manual capture. It reads only `index_contract: 3` reports and writes only:

- `personal-ops/indexes/check-ins-v3.csv`
- `personal-ops/indexes/check-ins-v3.jsonl`
- `personal-ops/indexes/check-ins-v3.metrics.csv`
- `personal-ops/indexes/check-ins-v3.md`
- `personal-ops/indexes/check-ins-v3-fields.md`
- `personal-ops/indexes/check-ins-v3.trends.md`

`--status-only` is diagnostic only. The seven-report threshold applies to out-of-band repair, not to a normal post-write refresh. The real refresh never rewrites canonical daily Markdown, raw input, OCR, or assets.

## Privacy

Reports and detailed indexes are `private-sensitive`. `detailed-private` keeps normalized private values local; `redacted` removes private property values from generated CSV/JSONL/metrics. Raw Check-In and full OCR are never indexed. `check-ins-v3.trends.md` is always sanitized and is the only V3 index Dreaming Mode may read.

## Post-Write Daily Summary

After a successful owner-approved write or update, re-read the saved canonical check-in and answer in this order:

```text
Zapisano:
- check-in: <path>
- TaskNotes: <paths|brak>

Plan na dziś (read-only):
- Data, WIG, DoD, deadline
- Professional plan items in chronological order
- IF as a standalone window line only; do not nest calorie or budget values under IF
- A separate six-block macro schedule with `food_blocks`, kcal, protein, fat, carbohydrates, and `configured|empty` status; select it by exact `planned_calories_representative`, and do not guess when that target is unknown
- A separate Budget section for the daily budget and monthly spending projection; weekly calorie target belongs in the macro schedule section
- Training and NSDR after the macro schedule
- Close habits, warnings, conflicts, and deferred scope when supplied

Refresh indeksów V3:
- `.systems/scripts/sync-personal-ops-check-ins-v3 --post-write`: completed|failed

Walidacja targeted:
- <actual check>: przeszła|nie przeszła
```

An explicitly linked weekly plan may supply block times. The daily artifact wins on conflict, and the conflict must be stated. Budget, calorie, and food-block values are owner-only and must come from `.systems/scripts/calculate-personal-ops-budgets` after a successful refresh. Select the food schedule by the exact planned calorie target, not by training/rest mode. If IF excludes a configured food block, state the conflict. Do not include prior-day closure, Raw Check-In, OCR, attachments, lessons, or quotations. This summary does not execute tasks, authorize deploys, or send external communication.
An incomplete food-block configuration is reported as `food_schedule.status: unavailable` with a deterministic reason and missing/invalid field list; do not show partial macro values and do not suppress valid spending or weekly calorie balances. Missing base configuration or stale indexes remains a calculator `STOP`.
