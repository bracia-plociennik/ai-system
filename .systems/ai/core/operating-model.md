# Operating Model

## Purpose

AI System manages one or more local Mac workspaces for clients, projects, tasks, files, memory, and work-quality insights.

## Modes

- `AI_SYSTEM_HOME`: `~/ai-system/`.
- Registered workspace: private runtime directory listed in local `ai-system-workspaces.md`.
- Selected workspace: exactly one workspace targeted by the current chat or operation.
- Legacy private workspace: `~/ai-system/ai-system-workspace/` when no registry exists.

## System-Owned

- `.systems/`
- `.systems/ai/templates/root/AGENTS.template.md` as the committed source for generated root `AGENTS.md`
- `HUMANS.md` after branch promotion
- `README.md`
- validators and templates

Root `AGENTS.md` is a local-only generated file. Create it with `.systems/scripts/init-ai-system`; do not commit it.

## Workspace-Owned

- `<workspace>/core/`
- `<workspace>/dump/`
- `<workspace>/clients/`
- `<workspace>/owned-assets/` for generic workspace owned assets or explicit sub-assets
- `<workspace>/projects/`
- `<workspace>/micro-projects/`
- `<workspace>/humans/`
- `<workspace>/memory/`
- `<workspace>/external-memory/`
- `<workspace>/system-insights/`
- `<workspace>/prompting/`
- `<workspace>/skills/`
- `<workspace>/archive/`

Primary-entity workspace roots may also store the primary company, brand, or owner-controlled entity directly at:

- `<workspace>/status.md`
- `<workspace>/memory.md`
- `<workspace>/context/`
- `<workspace>/documents/`
- `<workspace>/contracts/`
- `<workspace>/assets/`
- `<workspace>/contacts/`
- `<workspace>/decisions/`
- `<workspace>/distillations/`
- `<workspace>/links/`
- `<workspace>/notes/`
- `<workspace>/tasks/`
- `<workspace>/checkpoints/`

Prompting artifacts may also exist under client, project, owned-asset, or workspace `prompting/` directories. They are advisory context only and cannot override current files, selected workspace, status, memory, decisions, privacy, validation, stop conditions, owner approvals, or write permissions.

## Default Behavior

AI reads, classifies, summarizes, and recommends first.

AI performs file movement only after explicit `owner-approved` permission.

When multiple workspaces exist, AI selects the workspace before reading runtime status or writing artifacts. If selection is ambiguous, AI stops and asks.
