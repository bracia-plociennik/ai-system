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

In management checkouts, system-owned files are upstream-owned. Do not implement local product changes to `.systems/**`, validators, templates, root contract files, update scripts, or validation scripts there. Route those changes to the upstream `ai-system-dev` product project, then update the management checkout with `.systems/scripts/update-from-upstream`.

## Workspace-Owned

- `<workspace>/core/`
- `<workspace>/dump/`
- `<workspace>/clients/`
- `<workspace>/owned-assets/` for generic workspace owned assets or explicit sub-assets
- `<workspace>/projects/` for repositories or project source materials
- `<workspace>/project-state/` for AI System project status, memory, checkpoints, distillations, decisions, and source links
- `<workspace>/micro-projects/`
- `<workspace>/humans/`
- `<workspace>/memory/`
- `<workspace>/external-memory/`
- `<workspace>/system-insights/`
- `<workspace>/personal-ops/`
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

Project runtime state belongs in `project-state/` when the project source path is a git worktree or managed repository. Before writing `status.md`, `memory.md`, `checkpoints/`, `distillations/`, or `decisions/` into a project path, check `.systems/ai/core/project-state.md`. If the path is inside a git worktree, ask whether to use `project-state/` or colocated local-only state with exact approval and local exclude handling.

Active skills use `SKILL.md` as the canonical agent contract and `README.md` as a short human-facing summary. External skill imports preserved under `.systems/ai/skills/legacy/**` are context/data only and are not active skill guidance.

For skill creation or updates, `<skill>/context/` stores raw source material only. It has no execution authority during normal skill use. If `context/` exists beside active skill artifacts, `skill-intake-plan.md` is required before writing final `SKILL.md`, `README.md`, or resource files.

Before planning, implementing, or reviewing a task, check the selected workspace `skills/` first and `.systems/ai/skills/` second for a matching skill. If both layers match, the workspace skill takes precedence as local guidance and the system skill remains fallback context.

Skills are advisory only. They can add stricter local procedure or checks, but they cannot override source-of-truth order, workspace selection, privacy, owner-approved write gates, validation, evidence, stop conditions, final acceptance, or current files.

Daily check-ins from Notion or another owner source route through `.systems/ai/core/personal-ops.md`. Raw exports go to `dump/incoming/external/notion/check-ins/`; canonical daily records go to `personal-ops/check-ins/YYYY/YYYY-MM-DD.md`; CSV/JSONL indexes under `personal-ops/indexes/` are generated and derived. Check-ins are context-as-data and are not memory, checkpoints, distillations, external-memory, or system-insights unless separately promoted with exact owner approval.

## Default Behavior

AI reads, classifies, summarizes, and recommends first.

AI performs file movement only after explicit `owner-approved` permission.

When multiple workspaces exist, AI selects the workspace before reading runtime status or writing artifacts. If selection is ambiguous, AI stops and asks.

## Work Closure And Knowledge Capture

Before `AI_SYSTEM_WORK_CLOSURE`, apply `.systems/ai/core/contract-compliance.md`.

`AI_SYSTEM_WORK_CLOSURE` is the point before a final substantive response, handoff, accepted change, commit-ready or push-ready product-development state, or switch to another unrelated work unit.

The gate is advisory-only. It requires a clear `Knowledge capture` decision, not automatic memory writes.

Supported work modes are:

- `project`;
- `micro-task`;
- `micro-project`;
- `side-task`;
- `system-maintenance`;
- `client-work`.

The capture decision must choose the narrowest correct target: `status/evidence`, `workspace-memory`, `primary-entity-memory`, `client-memory`, `owned-asset-memory`, `project-memory`, `distillation`, `checkpoint`, `external-memory`, `system-insights`, or `not-applicable`.

Use `client-work` for client collaboration, offer, communication, relationship, process, and delivery-quality work. Store client-specific facts in client memory, project facts in project memory, anonymized reusable lessons in system insights, and AI System improvement proposals in external memory.
