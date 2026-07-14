# Manual Daily Check-In: Properties + Raw Audit v3

## Purpose

Use this brief for a manual, voice, partially structured, or already interpreted daily check-in. It produces one canonical report at `personal-ops/check-ins/YYYY/YYYY-MM-DD.md` with `schema_version: 3` and `index_contract: 3`.

The report has three different roles:

1. `properties` is the only source for `check-ins-v3.csv`, JSONL, metrics, and sanitized trends.
2. `## Interpreted Check-In` is a readable projection of the normalized properties, including the current plan, prior-day closure, WIG, and task eligibility.
3. `## Raw Check-In` preserves the owner message verbatim as private-sensitive context-as-data. OCR and working-note text live in `## OCR / Notatka robocza`.

Do not use this route for V2 Notion imports. Existing V2 files and `check-ins.*` indexes remain history; this route writes only `check-ins-v3.*` after a separate owner-approved sync. A V3 report without `index_contract: 3` must be owner-migrated before use.

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

Use stable plan item IDs in `planned_items_json`. Each item records at least `id`, `stream`, `title`, and optional `task_title`.

Every professional `build`, `deliver`, or `promote` item creates one TaskNote in `6d/do`, regardless of WIG or overload. Do not add per-item routing overrides. WIG uses `wig_kind: plan-item|standalone|none`, a stable `wig_id`, title, and Definition of Done; a linked WIG may reference one plan item, while a standalone WIG has no plan-item reference. Neither form creates its own TaskNote. The prior-day WIG closure determines minimum-day status. There is no `Kandydaci na taski` section. Raw text, OCR, lesson content, quotations, and external references never create a TaskNote. The existing owner-approved check-in write may create these TaskNotes once, subject to configured-vault, deduplication, subtask, and 6D rules.

## Indexes And Lazy Sync

Use `.systems/scripts/sync-personal-ops-check-ins-v3 --workspace <workspace-path> --status-only` after manual capture. It reads only `index_contract: 3` reports and writes only:

- `personal-ops/indexes/check-ins-v3.csv`
- `personal-ops/indexes/check-ins-v3.jsonl`
- `personal-ops/indexes/check-ins-v3.metrics.csv`
- `personal-ops/indexes/check-ins-v3.md`
- `personal-ops/indexes/check-ins-v3-fields.md`
- `personal-ops/indexes/check-ins-v3.trends.md`

The lazy-sync threshold is seven new reports. Normal sync requires exact owner approval and never rewrites canonical daily Markdown, raw input, OCR, or assets.

## Privacy

Reports and detailed indexes are `private-sensitive`. `detailed-private` keeps normalized private values local; `redacted` removes private property values from generated CSV/JSONL/metrics. Raw Check-In and full OCR are never indexed. `check-ins-v3.trends.md` is always sanitized and is the only V3 index Dreaming Mode may read.
