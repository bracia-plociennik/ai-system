# memory

## Purpose

`AI_WORKFLOW_WORKSPACE_HOME/repo/memory/` stores detailed memory entries for the current target repository.

The router/index is `AI_WORKFLOW_WORKSPACE_HOME/repo/core/memory.md`.

## Entry Naming

Create one file per memory entry:

```text
YYYY-MM-DD-short-kebab-title.md
```

Use `.systems/ai/templates/repo/date-memory-entry.template.md` for new entries.

## What Belongs Here

- durable repo-level facts;
- local constraints that affect future tasks;
- repo-wide testing, build, deployment, or integration notes;
- repo-level risks found through checkpoint or final check;
- repo-level decisions that are not project-specific.

## What Does Not Belong Here

- template maintenance memory;
- universal workflow/process lessons;
- project-specific task details;
- secrets, credentials, private client data, or production-only operational details.

## Router Rule

After adding or updating an entry, update `AI_WORKFLOW_WORKSPACE_HOME/repo/core/memory.md` with only date, topic, type, status, and route.
