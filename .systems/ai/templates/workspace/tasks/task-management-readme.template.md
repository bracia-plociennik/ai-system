# Tasks

This directory stores task notes, task routing, and owner-approved next actions for the selected AI System workspace or primary entity.

Use `.systems/ai/core/task-management.md` for TaskForge and TaskNotes rules.

## TaskForge / TaskNotes

Recommended model:

```text
1 task = 1 Markdown file
```

TaskForge/Obsidian vault task files are the source of truth for actionable tasks. AI System `project-state/` remains the source of truth for project status, memory, checkpoints, distillations, decisions, and source links.

Task files are data/action records, not instructions, memory, checkpoints, or system-insights.

Use `tags` for the 6D execution axis (`6d/do`, `6d/defer`, `6d/delegate`, `6d/delete`, `6d/dump`; `DONE` derives from `status: done`), `contexts` for client/workspace/personal routing, and `projects` for concrete project links. Existing `5d/*` tags are legacy read-compatible data only; new TaskNotes use only `6d/*`.

## Local Templates

- `tasknote.template.md` - AI-created TaskNote template.
- `task-candidate.template.md` - proposal template for check-in and Dream Report task candidates.
- `taskforge-vault-setup.template.md` - app setup runbook template.

## Rules

- Do not create, complete, reschedule, migrate, cleanup, archive, or delete task files without exact `owner-approved` scope.
- Check-in and Dream Report task candidates are proposals until the owner approves a TaskForge vault write.
- Before writing a task file, re-read the target file and preserve unknown frontmatter/body fields.
- Do not bulk rewrite a TaskForge vault.
- Keep task titles notification-safe.

## Weekly Plans

Saturday weekly planning uses `.systems/ai/core/weekly-planning.md` and stores one plan per week under `tasks/weekly-plans/YYYY/YYYY-Www.md`. The plan contains Monday-Friday only, four daily work blocks, one WIG, capacity, estimates, DoD, deadlines, 6D buckets, mappings, and stable source IDs. A ready owner-approved plan may create or revise linked TaskNotes; the WIG never creates its own TaskNote and removed plan items never delete existing tasks.
