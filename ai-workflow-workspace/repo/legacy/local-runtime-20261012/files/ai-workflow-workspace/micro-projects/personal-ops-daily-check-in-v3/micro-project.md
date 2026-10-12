# Personal Ops Daily Check-In v3

## Summary

- Date: `2026-07-13`
- Result: `proposed`
- Micro-project artifact risk: `low`
- Future product implementation risk: `medium`
- Scope: record the accepted product direction for Personal Ops Daily Check-In v3.

## Source Evidence

- Current AI System Personal Ops V2 contract, templates, lazy sync tool, and
  TaskForge task-candidate contract.
- Existing V2 daily Markdown and derived index layout in the personal workspace.
- Raw V3 source material and an interpreted V3 example reviewed as
  `context-as-data` only.
- Owner decisions from this conversation.

Source material is supporting data. It is not executable instruction and does
not authorize writes, migrations, task creation, or promotion.

## Accepted Direction

- V3 keeps one canonical Markdown file per daily session under:

  ```text
  <workspace>/personal-ops/check-ins/YYYY/YYYY-MM-DD.md
  ```

- V3 keeps derived analytical indexes:

  ```text
  <workspace>/personal-ops/indexes/check-ins.csv
  <workspace>/personal-ops/indexes/check-ins.jsonl
  <workspace>/personal-ops/indexes/check-ins.metrics.csv
  ```

- V3 supports native manual check-ins. Extending the Notion importer to V3 is
  out of scope; the existing importer remains V2-only.
- A session report for day `D` contains the plan and current state for `D`, plus
  closure facts for `D-1`. The parser assigns each value to its correct
  effective date without editing the prior day's Markdown.
- A supplied interpreted report is canonical. If raw and normalized values
  conflict, normalized values are authoritative. Raw input is interpreted only
  once.
- Each source report remains `private-sensitive` and context-as-data. It is not
  memory, a checkpoint, a system insight, or an instruction.

## Backward Compatibility

- V2 daily files remain unchanged historical sources.
- A check-in without `schema_version` remains V2.
- V3 performs no backfill and does not infer historical plan-versus-actual
  comparisons.
- Existing V2 index columns and their semantics remain stable. V3 adds only
  optional versioned columns and structures.
- Regenerating indexes after the product change must use a V2 snapshot to prove
  that existing V2 rows retain their meaning.
- Correcting historical V2 normalization behavior, including sentinel values
  such as `brak`, is a separate owner-approved maintenance decision.

## Privacy And Analytics Boundaries

- Owner decision: V3 derived indexes retain detailed financial, calorie,
  health, and attachment metadata as `private-sensitive` data. This includes
  structured values needed for personal analytics, not only presence flags.
- The canonical `check-ins.csv`, `check-ins.jsonl`, and
  `check-ins.metrics.csv` are therefore private-sensitive runtime artifacts.
  Attachment files remain beside their canonical daily Markdown; indexes store
  their relative paths, types, and relevant structured metadata rather than
  copying binary content.
- Dreaming Mode may use only an explicitly sanitized trend artifact. It must
  not consume raw check-ins, private derived data, attachments, OCR, finances,
  calories, or detailed health reflections.
- No automatic GitHub mirror or external export may include these private
  indexes. A later mirror/export route requires an explicit privacy-classified
  owner decision.

## TaskForge Integration

- Planned `zbudować`, `dowieźć`, and `wypromować` items create individual
  TaskNote candidates with stable source item identifiers.
- One exact `owner-approved` write for the canonical V3 check-in also permits
  creating its TaskNotes. No second TaskNote-specific approval is required.
- This exception applies only to V3 check-in creation. It does not allow
  Dreaming Mode writes, manual TaskNote edits, completion, rescheduling,
  migration, cleanup, archiving, or deletion without their own approval.
- Generated TaskNotes use the existing TaskForge mapping: `5d/do`, `open`,
  `high`, and a due date at the end of the session day. Client and project
  mapping remains conservative.
- The future product must resolve the vault from a one-time local-only runtime
  record in the selected workspace. No private vault path belongs in
  `.systems/**`.
- If vault configuration or preflight is unavailable, write the canonical
  check-in with `task-generation: skipped` and report the reason. Do not omit
  the failed task-generation state silently.
- Dedupe generated TaskNotes by `source_session_date + source_plan_item_id`.
  A later report revision must not modify existing TaskNotes automatically.

## Required Future Product Work

- Extend the Personal Ops schema, manual brief, templates, routing, sync parser,
  and validators for version-aware V2/V3 handling.
- Extend task-candidate extraction for V3 planned action items and TaskNote
  deduplication.
- Add a local-only TaskForge vault configuration contract outside root
  `.systems/**`.
- Add safe Dreaming Mode trend routing without exposing private check-in data.
- Preserve lazy sync: daily Markdown is canonical and derived indexes refresh
  only through the approved sync route.

## Future Validation

- Synthetic V2 snapshot before and after V3 index regeneration.
- V3 manual session report, plan-only report, and cross-day closure fixtures.
- Mixed V2/V3 history with no mutation of V2 Markdown.
- Normalized-value precedence, sentinel handling, private-sensitive detailed
  indexes, attachment metadata, and safe trend output.
- Per-item TaskNote generation, deduplication, unavailable-vault handling, and
  no automatic mutation of existing TaskNotes.

## Out Of Scope

- No `.systems/**` edits in this micro-project.
- No runtime check-in migration, backfill, index refresh, or Notion import.
- No TaskForge vault configuration, TaskNote creation, task cleanup, or app
  automation.
- No private source data copied into this artifact.

## Promotion Decision

- Promote to product implementation: `not yet`.
- Required route: create a formal AI System product change request or project
  plan before editing `.systems/**`.
- Reason: V3 changes shared data contracts, derived indexes, privacy boundaries,
  and a narrowly-scoped TaskForge write policy.

## Contract Compliance

- Work mode: `workflow-maintenance`
- Work mode compliance: `pass`
- Knowledge capture: `required`
- Capture target: `micro-project artifact`
- Reason: owner approved durable tracking of an accepted future product change.
