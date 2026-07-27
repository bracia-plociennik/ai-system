# Weekly Plan Template

This is a neutral template. It is not a TaskNote and must not be scanned as one.

```md
---
type: weekly-plan
week_id: <YYYY-Www>
week_start: <YYYY-MM-DD>
week_end: <YYYY-MM-DD>
timezone: <IANA timezone>
plan_revision: 1
plan_readiness: ready|needs-review
overload_status: clear|warning|blocked
overload_acknowledged: false
wig_kind: plan-item|standalone|none
wig_id: <stable id>
wig_title: <weekly WIG>
wig_definition_of_done: <observable result>
wig_plan_item_id:
daily_blocks_json: []
weekly_plan_items_json: []
task_generation_status: proposal-only
task_generation_references_json: []
revision_audit_json: []
---

# Weekly Plan <YYYY-Www>

## WIG tygodnia

- Kind: `plan-item|standalone|none`
- ID: `<wig_id>`
- Definition of Done: `<observable result>`
- Linked item: `<weekly_plan_item_id|none>`

## Capacity And Constraints

| Day | Fixed commitments | Available minutes | Planned minutes | Notes |
| --- | --- | ---: | ---: | --- |
| Monday |  |  |  |  |
| Tuesday |  |  |  |  |
| Wednesday |  |  |  |  |
| Thursday |  |  |  |  |
| Friday |  |  |  |  |

## Daily Blocks

Each day has `build-future`, `adapt-build-deliver`, `deliver-financial-impact`, and `adapt-promote-deliver`. Record start/end or duration, availability, and work slices in `daily_blocks_json`.

## Planned Work

For every item preserve a stable ID, stream, title, estimate, Definition of Done, optional planned date, optional deadline, optional 6D bucket, mapping, and `planned_allocations`.

## Deferred Scope

Items intentionally left unscheduled or moved beyond this week.

## Overload And Mapping Review

Warnings, unresolved estimates, invalid dates, ambiguous client/project mappings, and owner decisions.

## TaskNotes

Proposal/write status, source IDs, created paths, reused parents, subtasks, skipped writes, and revision drift.
```

## Post-Write Weekly Summary

After a successful owner-approved write or revision, re-read the saved canonical weekly plan and answer in this order:

```text
Zapisano:
- weekly plan: <path>
- TaskNotes: <paths|brak>

Plan tygodnia (read-only):
- Date range, WIG, DoD, and deadline
- Monday-Friday blocks and expected results
- Unavailable days, capacity, buffers, overload, and deferred scope
- TaskNote generation status

Walidacja targeted:
- <actual check>: przeszła|nie przeszła
```

Omit unknown values instead of guessing. This summary does not execute tasks, authorize deploys, or send external communication.
