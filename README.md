# AI System

## Purpose

AI System is a local Mac workspace system for managing clients, projects, tasks, materials, memory, and personal work-quality insights.

This branch is the dedicated `ai-system` branch. The system-owned files live at the repository root, and private client/workspace data belongs in the ignored `ai-system-workspace/` directory.

## Local Paths

Recommended system root:

```text
~/ai-system/
```

Recommended private workspace:

```text
~/ai-system/ai-system-workspace/
```

`ai-system-workspace/` is private local runtime. Do not commit customer data, secrets, contracts, private notes, exports, or working files.

## Layout

- `AGENTS.md` - execution contract for AI assistants.
- `HUMANS.md` - human-facing runbook.
- `.systems/` - system rules, templates, examples, skills, and validators.
- `.github/` - validation workflow configuration.

## First Commands

```text
Initialize my local AI System workspace.
```

```text
Review dump/incoming and classify files. Do not move, rename, copy, or delete anything without owner-approved.
```

## Safety

- AI classifies before acting.
- File movement needs owner approval.
- External integrations are links or manual context in v1.
- `system-insights` must be anonymized.
- `external-memory` is only for improving AI System itself.
