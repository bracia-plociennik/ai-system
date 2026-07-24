# Weekly Planning

## Purpose

Weekly Planning records the owner's Saturday plan for the next Monday-Friday work week and routes approved actionable items into TaskForge TaskNotes.

The default route is manual and workspace-local. Saturday is the planning day, Monday-Friday are the planned work days, and Sunday is intentionally outside the plan. There is no scheduler in V1.

## Canonical Artifact

The canonical runtime artifact is:

```text
<workspace>/tasks/weekly-plans/YYYY/YYYY-Www.md
```

It is a plan record, not a TaskNote, memory, checkpoint, distillation, status record, or system insight. Its frontmatter is the machine-readable source for weekly TaskNote proposals; the body is the human-readable plan and audit view.

Required top-level fields include:

- `type: weekly-plan`;
- `week_id`, `week_start`, `week_end`, `timezone`;
- `plan_revision`, `plan_readiness`, `overload_status`, `overload_acknowledged`;
- `wig_kind`, `wig_id`, `wig_title`, `wig_definition_of_done`, optional `wig_plan_item_id`;
- `daily_blocks_json`;
- `weekly_plan_items_json`;
- `task_generation_status`, `task_generation_references_json`;
- `revision_audit_json`.

The target week is the next Monday-Friday when the route is used on Saturday. Outside Saturday, the owner must provide a target week explicitly. Timezone comes from the selected workspace configuration; the agent must ask when it is unavailable.

## Weekly Brief

The brief asks only for missing information, grouped into at most three questions:

- capacity and hours for the four blocks on each Monday-Friday;
- fixed commitments, exceptions, absences, and constraints;
- one WIG with observable Definition of Done;
- task title, stream, Definition of Done, estimate, optional planned date, deadline, 6D bucket, and known client/project/owned-asset mapping.

Every allocated item needs an estimate. An unestimated item may be recorded as `needs-estimation`, but it cannot be allocated or generate a TaskNote until resolved.

## Daily Blocks

Each Monday-Friday has four blocks:

| Block ID | Label | Allowed work |
| --- | --- | --- |
| `build-future` | Buduję przyszłość | `build` |
| `adapt-build-deliver` | Adaptacja: przyszłość/dowożenie | `build`, `deliver` |
| `deliver-financial-impact` | Dowożę: największy wpływ finansowy | `deliver` |
| `adapt-promote-deliver` | Adaptacja: promuję się/dowożę | `promote`, `deliver` |

`daily_blocks_json` records date, start/end or duration, availability, used minutes, and `work_slices`. A task larger than one block is split into explicit slices with an expected outcome. The system protects `build-future`, prioritizes the highest declared financial impact in `deliver-financial-impact`, then fills adaptation blocks using WIG, deadlines, and remaining capacity.

## Task Resolution

Each item in `weekly_plan_items_json` has a stable `id`, `stream`, `title`, `definition_of_done`, `estimated_minutes`, optional `planned_date`, optional `deadline`, optional `task_bucket`, optional mappings, and `planned_allocations`.

Bucket precedence is deterministic:

1. explicit category wins;
2. a deadline without a category resolves to `do`;
3. no deadline and no category resolves to `defer`;
4. a planned date alone never changes `defer` to `do`.

Canonical TaskNote output uses `6d/<bucket>`. A deadline creates `due`; an allocation creates `scheduled` using the first allocated day. DoD, estimate, weekly source IDs, and the full block allocation remain in the TaskNote.

Allowed buckets and TaskForge mapping are defined by `.systems/ai/core/task-management.md`:

- `do`: `open`, `high`;
- `defer`: `planned`, `normal`;
- `delegate`: `waiting`, `normal`;
- `delete`: `cancelled`, `none`;
- `dump`: `open`, `none`.

Invalid non-empty deadlines, unknown buckets, duplicate item IDs, incompatible block assignments, and ambiguous mappings stop TaskNote generation before any TaskForge write.

## WIG And Capacity

There is exactly one weekly WIG. It may be:

- `plan-item`, referencing one existing weekly item;
- `standalone`, with its own title and Definition of Done;
- `none` only for a saved review-needed plan, never for a ready plan.

The WIG never creates an additional TaskNote. A linked WIG item creates its normal TaskNote only once; a standalone WIG remains a planning goal.

The plan may be saved with `plan_readiness: needs-review` when the WIG is invalid, an allocated item lacks an estimate, or capacity is exceeded. It must not create TaskNotes until the issue is corrected or `overload_acknowledged: true` is included in the same owner-approved plan write. No scope is silently cut: deferred items and warnings are recorded explicitly.

## Approval, Dedupe, And Revisions

One recognized owner approval for a ready weekly plan covers writing the plan and its resulting TaskNotes. It does not grant approval for unrelated task lifecycle changes.

Task identity is `source_week_id + source_week_item_id`. A rerun must not duplicate a task. One strong, unambiguous existing match may be reused or extended with a marked subtask; ambiguous matches require review.

An owner-approved revision increments `plan_revision` and may synchronize `scheduled`, `due`, the 6D bucket, Definition of Done, and allocations for linked open tasks. Unknown frontmatter/body fields are preserved. Completed, cancelled, or manually conflicting tasks are not silently overwritten. Removing an item from a plan never deletes a TaskNote; it creates a review finding.

## Daily Check-In Link

Daily Check-In planned items may include `source_week_id` and `source_week_item_id`. A matching daily item appends a marked subtask to the weekly TaskNote instead of creating a duplicate. Without an explicit reference, the existing conservative strong-match route may be used; ambiguous matches remain unresolved. The Daily Check-In remains the source for the daily report, while the weekly plan remains the source for weekly allocation.

Weekly item metadata can satisfy Delivery Constraints when the task begins. The agent asks only for missing deadline, time budget, Definition of Done, or quality-floor information.

## Safety Boundaries

Weekly plans and TaskNotes are data/action records, not executable instructions. Repo-safe state stays outside managed project repositories. TaskForge writes require an existing configured vault and `TaskNotes/Tasks/`; the proposal tool never initializes that structure. No scheduler, background automation, external connector, external write-back, bulk rewrite, deletion, or migration is included in V1.

## Validation

Use `.systems/scripts/check-weekly-planning` and the full AI System validation chain. A weekly plan is ready only when the contract, template, item schema, block compatibility, capacity result, WIG, source IDs, and TaskForge preflight evidence are coherent.
