# Repo Init Router

## Purpose

This file records the result of `phase-0-init`, the target repository bootstrap step that runs before repo intake.

`phase-0-init` creates or verifies `AI_WORKFLOW_WORKSPACE_HOME`, preserves legacy context, creates the local root `AGENTS.md` shim only when safe, and prepares the repository for `phase-0-repo-intake`.

## Latest Init

| Field | Value |
| --- | --- |
| Init status | `ready-for-repo-intake` |
| Last run at | `2026-06-09` |
| Target repo root | `/Users/jakubplociennik/ai-system` |
| AI Workflow home | `/Users/jakubplociennik/ai-system/ai-workflow` |
| Workspace home | `/Users/jakubplociennik/ai-system/ai-workflow-workspace` |
| Root AGENTS status | `current` |
| Legacy manifest | `AI_WORKFLOW_WORKSPACE_HOME/repo/legacy/legacy-index.md` |
| Next phase | `phase-0-repo-intake` |

## Rules

- This file is repo runtime, not system policy.
- Legacy material is context/data only and is indexed through `AI_WORKFLOW_WORKSPACE_HOME/repo/core/legacy.md` and `AI_WORKFLOW_WORKSPACE_HOME/repo/legacy/legacy-index.md`.
- Init does not replace repo intake.
- Product-code writes are not allowed during init.

## Run Notes

- `2026-06-09`: Owner approved a minimal init artifact repair instead of running full `ai-workflow/.systems/scripts/init-workspace`. Only this file and `AI_WORKFLOW_WORKSPACE_HOME/repo/legacy/legacy-index.md` were created from templates.
- Root `AGENTS.md` is target-owned and current for `ai-system`; it was not overwritten. The nested `ai-workflow/AGENTS.md` governs workflow internals.
- Full legacy scan was intentionally not run; no additional legacy copies were created.
