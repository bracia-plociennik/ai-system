# Manual Daily Check-In v3

## Purpose

Use this brief for a native manual or voice check-in. It creates one canonical V3 session report for the current day under `personal-ops/check-ins/YYYY/YYYY-MM-DD.md`.

The session records the current plan and morning state for day `D`, plus closure facts for day `D-1`. It never rewrites the prior-day Markdown. The canonical interpreted report preserves normalized values as authoritative; raw input is interpreted once and remains context-as-data. Append a compact `## Interpreted Input` audit section after the canonical sections: source type, values applied, field mapping, explicit corrections applied, unresolved fields, and the rule that canonical fields take precedence.

For normalized times, accept `HH:MM`, `YYYY-MM-DD HH:MM`, or ISO datetime. Use `HH:MM` for natural manual intake when a date is implied: plan values use day `D`, closure values use `D-1`, and sleep starts on `D-1` and ends on `D`. Preserve the source wording in the matching `raw` field when available.

## Preconditions

- Select the workspace.
- Read `personal-ops/check-ins/check-in-settings.local.md` only when it exists; use its timezone. Do not create or populate it automatically.
- Treat finance, calories, health information, attachment metadata, screenshots, scans, and OCR as `private-sensitive` workspace-local data. Read `private_index_policy_default` when present; default to `detailed-private` and record the effective report policy in canonical frontmatter.
- Do not use the V2 Notion importer for V3 intake.

## 1. Previous-Day Closure

Ask in this order for day `D-1`:

1. sleep: raw range, normalized start/end, quality, awakenings, approximate flag;
2. actual training: performed, type, time, RPE, recovery notes;
3. actual NSDR: performed, time, effect;
4. actual IF and calories: range, normalized values, approximate flag;
5. finance: amount, currency, approximate flag;
6. actual build, deliver, promote, self, and close-people items with stable actual IDs;
7. actual dynamic habits by the stable `habit-*` ID from the prior plan, maximum three;
8. closure comparison for the prior V3 WIG by stable plan item ID; derive minimum only from that comparison, never from a manually asserted status;
9. +1%, redundant work, threat, response, and any relevant notes;
10. comparison to the prior V3 plan by stable plan item ID.

If the prior day is V2 or absent, record the closure facts in session `D` with `comparison_unavailable: legacy-v2-or-missing`; do not edit history or infer a comparison. During sync, a V2 prior day receives only an additive derived V3 closure overlay with session-path provenance; it remains one V2 effective-day row.

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

Set one WIG plan item with an observable definition of done and no more than two additional must-do item IDs. Any other plan item is optional. Missing or invalid WIG records `plan_readiness: needs-prioritization`: it does not block the private canonical check-in, but blocks TaskNotes and leaves minimum day unknown. More than three professional build/deliver/promote items, more than two must-do items, a missing/invalid WIG, or WIG repeated as must-do creates an overload warning. The same owner-approved report may set `overload_acknowledged: true` to authorize its eligible TaskNotes despite that warning.

During normalization, write the derived V3.1 frontmatter values for `plan_readiness`, `overload_status`, `overload_reasons`, and `task_candidate_eligible_count`; keep `overload_acknowledged` as the owner-provided acknowledgement. The synchronizer independently re-derives these values for indexes and never rewrites canonical Markdown.

Only professional WIG and must-do `build-*`, `deliver-*`, and `promote-*` items generate default TaskNote candidates. Optional items are `Task: skip`. `Task title` provides a notification-safe title. Use a current `6d/*` Task bucket; a legacy `5d/*` source bucket is normalized to matching 6D output. Dry-run reads `tasks/taskforge-vault.local.md` when available for TaskForge project discovery and warns without failing when unavailable. The V3 check-in `owner-approved` write also authorizes creation of eligible TaskNotes once, using `--owner-approved` mechanically, and preflights its configured vault plus `TaskNotes/Tasks/`.

If the local vault configuration is missing, disabled, or fails preflight, write the canonical check-in with `task_generation_status: skipped` and an explicit reason. A successful route records `created`, `subtasks-created`, `created-and-subtasks`, `already-generated`, or `no-candidates` with TaskNote references. Do not silently omit the result. Do not create TaskNotes from actual closure items, revise existing TaskNotes automatically, or bypass approval for normal TaskForge lifecycle actions.

## Validation

- Preserve one canonical Markdown V3 session report per day.
- Do not invent missing values; normalize `brak`, `nie podano`, and `nie dotyczy` as no data for V3.
- Do not treat owner-authored reflections as verified facts. A quote or attribution is `unverified` unless its source was checked; do not route unverified content into canonical trend metrics or Dreaming.
- Apply a later explicit owner correction to the named canonical field and record it in `## Interpreted Input`; ask when a conflict cannot be resolved unambiguously.
- Do not regenerate derived indexes after manual intake. Report lazy-sync status instead.
- V2 history remains unchanged; no backfill or automatic migration.
