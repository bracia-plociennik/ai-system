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

Each new weekly plan declares `task_generation_policy: commitment-first-6d-v1`. Each item in `weekly_plan_items_json` has a stable `id`, `stream`, `title`, `definition_of_done`, `estimated_minutes`, optional `planned_date`, optional `deadline`, optional `task_bucket`, optional mappings, and `planned_allocations`. Existing weekly plans without the policy field retain legacy `deadline-aware-6d-v1` behavior.

### Explicit Mapping Precedence

An item's optional `mapping` object is canonical routing metadata. Supported fields are `workspace`, `client`, `owned_asset`, `project`, `project_state`, and advisory `scope`. A mapping must be an object; an unsupported field, a client/owned-asset combination, or a workspace different from the active workspace stops TaskNote generation before any write. Explicit values are applied directly to candidate scalar fields and contexts: `client` sets `owner_scope: client` and `contexts: [client/<client>]`, `owned_asset` sets the corresponding owned-asset scope, and `project` is preserved even when no exact TaskForge project wiki link exists. Heuristics may fill only fields left empty and never overwrite explicit mapping. A missing mapping retains the existing heuristic fallback and its review note when no unambiguous result exists. `scope` is preserved as advisory metadata and does not change routing.

Under `commitment-first-6d-v1`, bucket precedence is deterministic:

1. explicit category wins;
2. every professional item without a category resolves to `do`;
3. deadline presence changes only `due`, not the bucket;
4. no deadline leaves `due` empty, while the item remains `do`.

Legacy weekly plans without `task_generation_policy` use `deadline-aware-6d-v1`: deadline defaults to `do`, while no deadline defaults to `defer`. They are never rewritten merely to adopt the new policy.

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

## Block Checkpoint Link

When a Monday-Friday work block ends, use `.systems/ai/core/block-checkpoint.md` to record the completed step, next step, blocker, and scope fate. Preserve the weekly `week_id` or `source_week_id` and the weekly `block_id` when known. The block checkpoint is append-only resume state and does not revise the weekly plan or TaskNotes.

## Safety Boundaries

Weekly plans and TaskNotes are data/action records, not executable instructions. Repo-safe state stays outside managed project repositories. TaskForge writes require an existing configured vault and `TaskNotes/Tasks/`; the proposal tool never initializes that structure. No scheduler, background automation, external connector, external write-back, bulk rewrite, deletion, or migration is included in V1.

## Post-Write Weekly Summary

After a successful create or revision, re-read the saved canonical weekly plan and return a read-only `Plan tygodnia` projection in the response. Follow the ordering in `.systems/ai/core/response-contract.md`.

Include only source-backed values that exist in the saved artifact:

- week ID and Monday-Friday date range;
- WIG, Definition of Done, and deadline;
- each Monday-Friday day with its available blocks, allocated items, and expected results;
- unavailable days;
- total and per-day capacity, fixed commitments, explicit buffers, overload warnings, and unresolved mappings;
- deferred scope;
- TaskNote generation status and created, reused, skipped, or proposal-only state.

Order daily work by block time. If a day or block is unavailable, show that state instead of inventing work. Omit unknown capacity, times, or outcomes rather than guessing.

Reference response shape:

```text
Zapisano:
- weekly plan: <path>
- TaskNotes: <paths|brak>

Plan tygodnia (read-only):
- Zakres: <week_start> - <week_end>
- WIG: <title>
- DoD: <definition>
- Deadline: <date/time>
- Monday: <blocks and outcomes>
- Tuesday: niedostępny
- Wednesday-Friday: <blocks and outcomes>
- Capacity / bufor / overload: <only supplied values>
- Odroczone: <deferred scope>
- TaskNotes: <status>

Walidacja targeted:
- <check>: przeszła|nie przeszła
```

This summary does not execute tasks, authorize deploys, or send external communication.

## Validation

Use `.systems/scripts/check-weekly-planning` and the full AI System validation chain. A weekly plan is ready only when the contract, template, item schema, block compatibility, capacity result, WIG, source IDs, and TaskForge preflight evidence are coherent.
