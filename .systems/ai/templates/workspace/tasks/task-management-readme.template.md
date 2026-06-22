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

## Local Templates

- `tasknote.template.md` - AI-created TaskNote template.
- `taskforge-vault-setup.template.md` - app setup runbook template.

## Rules

- Do not create, complete, reschedule, migrate, cleanup, archive, or delete task files without exact `owner-approved` scope.
- Before writing a task file, re-read the target file and preserve unknown frontmatter/body fields.
- Do not bulk rewrite a TaskForge vault.
- Keep task titles notification-safe.
