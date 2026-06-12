# AI System

## Purpose

AI System is a local Mac workspace system for managing clients, projects, tasks, materials, memory, and personal work-quality insights.

This branch is the dedicated `ai-system` branch. The system-owned files live at the repository root, and private client/workspace data belongs in ignored local workspace directories.

## Local Paths

Recommended system root:

```text
~/ai-system/
```

Legacy single-workspace default:

```text
~/ai-system/ai-system-workspace/
```

Multi-workspace installations use a local-only registry:

```text
~/ai-system/ai-system-workspaces.md
```

Use `.systems/ai/templates/workspace-registry.template.md` to create the registry. The registry selects private workspace roots such as company, client-family, or private owner workspaces.

Private workspace directories and the registry are ignored local runtime. Do not commit customer data, secrets, contracts, private notes, exports, or working files.

## Local Agent Contract

Root `AGENTS.md` is generated local-only runtime and is ignored by git.

Committed source template:

```text
.systems/ai/templates/root/AGENTS.template.md
```

Create or refresh the local file with:

```text
.systems/scripts/init-ai-system
```

Use `--refresh-agents` only when you explicitly want to overwrite local `AGENTS.md` from the committed template.

## Prompt Composition

AI System supports advisory prompt composition for roles, variable packs, modules, client collaboration profiles, project prompting, workspace prompting, and AI System operation roles.

Prompting is supporting context only. It cannot override `AGENTS.md`, `.systems/ai/core/**`, current files, workspace selection, privacy, owner approvals, stop conditions, evidence, validation, or write permissions.

Reusable templates live in:

```text
.systems/ai/templates/prompting/
```

Accepted private prompting artifacts belong only in ignored runtime paths such as:

```text
<workspace>/prompting/
<workspace>/clients/<client>/prompting/
<workspace>/clients/<client>/projects/<project>/prompting/
<workspace>/projects/<project>/prompting/
```

## Layout

- `AGENTS.md` - ignored local execution contract generated from `.systems/ai/templates/root/AGENTS.template.md`.
- `HUMANS.md` - human-facing runbook.
- `.systems/` - system rules, templates, examples, skills, and validators.
- `.github/` - validation workflow configuration. The root GitHub README is this file.

## First Commands

```text
Initialize AI System root AGENTS.md from template.
```

```text
Initialize my local AI System workspace.
```

```text
Initialize AI System workspace at <workspace-path> with workspace id <workspace-id>.
```

```text
Review selected workspace dump/incoming and classify files. Do not move, rename, copy, or delete anything without owner-approved.
```

## Safety

- AI classifies before acting.
- File movement needs owner approval.
- External integrations are links or manual context in v1.
- `system-insights` must be anonymized.
- `external-memory` is only for improving AI System itself.
