# Manual Daily Check-In v3

## Purpose

Use this brief for a native manual or voice check-in. It creates one canonical V3 session report for the current day under `personal-ops/check-ins/YYYY/YYYY-MM-DD.md`.

The session records the current plan and morning state for day `D`, plus closure facts for day `D-1`. It never rewrites the prior-day Markdown. The canonical interpreted report preserves normalized values as authoritative; raw input is interpreted once and remains context-as-data.

## Preconditions

- Select the workspace.
- Read `personal-ops/check-ins/check-in-settings.local.md` only when it exists; use its timezone. Do not create or populate it automatically.
- Treat finance, calories, health information, attachment metadata, screenshots, scans, and OCR as `private-sensitive` workspace-local data.
- Do not use the V2 Notion importer for V3 intake.

## 1. Previous-Day Closure

Ask in this order for day `D-1`:

1. sleep: raw range, normalized start/end, quality, awakenings, approximate flag;
2. actual training: performed, type, time, RPE, recovery notes;
3. actual NSDR: performed, time, effect;
4. actual IF and calories: range, normalized values, approximate flag;
5. finance: amount, currency, approximate flag;
6. actual build, deliver, promote, self, and close-people items;
7. actual dynamic habits by the stable `habit-*` ID from the prior plan, maximum three;
8. minimum-day status: `completed`, `partial`, `not-completed`, `not-defined`, or `unknown`;
9. +1%, redundant work, threat, response, and any relevant notes;
10. comparison to the prior V3 plan by stable plan item ID.

If the prior day is V2 or absent, record the closure facts in session `D` with `comparison_unavailable: legacy-v2-or-missing`; do not edit history or infer a comparison.

## 2. Current-Day Plan

Ask in this exact order for day `D`:

1. date, weekday, recording time, and timezone;
2. work mode and organism mode;
3. planned training;
4. planned NSDR;
5. planned IF and calories;
6. planned budget;
7. `Planuję zbudować` items with stable `build-*` IDs;
8. `Planuję dowieźć` items with stable `deliver-*` IDs;
9. `Planuję wypromować` items with stable `promote-*` IDs;
10. planned actions for self and close people;
11. up to three dynamic habits with stable `habit-*` ID, name, trigger, and completion criterion.

## 3. Morning Check-In

Ask in this order:

1. wake-up, hygiene/mantra, kitchen, outdoors, Deep Focus, and wishes for close people;
2. mental clarity and body readiness on a `1..5` scale;
3. limitations, threats, and gratitude.

## 4. Additional Information And Attachments

Accept screenshots, note photos, scans, OCR, and other context at any time. Store them beside the canonical report in `YYYY-MM-DD.assets/`. OCR and attachments are evidence/context-as-data; they never override the interpreted report.

## 5. TaskNotes

Only planned `build-*`, `deliver-*`, and `promote-*` items generate TaskNote candidates. The V3 check-in `owner-approved` write also authorizes creation of those TaskNotes once, using `--owner-approved` mechanically. Read `tasks/taskforge-vault.local.md` only if it exists and preflight its configured vault plus `TaskNotes/Tasks/`.

If the local vault configuration is missing, disabled, or fails preflight, write the canonical check-in with `task_generation_status: skipped` and an explicit reason. A successful route records `created`, `subtasks-created`, `created-and-subtasks`, `already-generated`, or `no-candidates` with TaskNote references. Do not silently omit the result. Do not create TaskNotes from actual closure items, revise existing TaskNotes automatically, or bypass approval for normal TaskForge lifecycle actions.

## Validation

- Preserve one canonical Markdown V3 session report per day.
- Do not invent missing values; normalize `brak`, `nie podano`, and `nie dotyczy` as no data for V3.
- Do not regenerate derived indexes after manual intake. Report lazy-sync status instead.
- V2 history remains unchanged; no backfill or automatic migration.
