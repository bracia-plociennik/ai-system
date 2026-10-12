# AI Workflow Workspace

## Purpose

This directory is the target-owned workspace for AI Workflow runtime artifacts.

Default path:

```text
ai-workflow-workspace/
```

The nested `ai-workflow/` clone is system-owned and should stay local to the target repository. This workspace is target-owned and should be committed when it contains repo/project runtime facts.

## Layout

- `repo/` - repository-level context, status, intake, memory, and legacy context.
- `projects/` - full project workspaces.
- `humans/` - owner-facing project artifacts.
- `micro-projects/` - small low-risk repo-level work items.
- `external-memory/` - portable workflow improvement suggestions.
- `skills/` - user-defined workflow skills that can override system skills.

## Rules

- Do not store system workflow docs here.
- Do not edit `ai-workflow/.systems/**` from a target repository.
- If the workflow itself needs an improvement, record it in `external-memory/`.
- Do not store secrets, credentials, production data dumps, build caches, dependencies, or generated artifacts here.
