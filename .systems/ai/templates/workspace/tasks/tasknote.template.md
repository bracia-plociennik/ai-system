# TaskNote Template

This file is a neutral template. It is not a TaskNote and must not be detected by TaskForge as a real task.

Copy the example into `TaskNotes/Tasks/<filename>.md` only after exact owner approval.

```md
---
type: task
title: "<notification-safe task title>"
status: open
priority: normal
due:
dueAt:
scheduled:
start:
tags:
  - 6d/<do|defer|delegate|delete|dump>
contexts:
  - <client/client-slug|owned-asset/asset-slug|workspace/workspace-slug|personal>
projects: []
workspace: "<workspace-slug>"
owner_scope: "<workspace|client|owned-asset|project|personal>"
client:
owned_asset:
project:
project_state:
source_system: ai-system
source_type:
source_check_in_date:
source_check_in_field:
source_session_date:
source_plan_item_id:
source_week_id:
source_week_item_id:
source_week_plan:
estimated_minutes:
weekly_allocations_json:
source_dream_report:
---

# <notification-safe task title>

## Outcome

<desired result>

## Definition Of Done

<observable completion condition when supplied by a planned check-in item>

## Weekly Allocation

<weekly plan source, allocated block slices, and expected work-slice outcomes when applicable>

## Context

<workspace/client/owned-asset/project links and source references>

## Next Action

- [ ] <next owner-approved action>

## Subtasks

- [ ] <optional scoped subtask>

## Evidence

<validation, source, or decision evidence>

## Notes

<additional non-sensitive context>
```
