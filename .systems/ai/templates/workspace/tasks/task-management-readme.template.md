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

Use `tags` for the 5D axis (`5d/do`, `5d/defer`, `5d/delegate`, `5d/delete`, `5d/dump`), `contexts` for client/workspace/personal routing, and `projects` for concrete project links.

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
