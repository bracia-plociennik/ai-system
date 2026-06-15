# AI System

## Purpose

AI System is a local Mac workspace system for managing clients, projects, tasks, materials, memory, and personal work-quality insights.

This branch is the dedicated `ai-system` branch. The system-owned files live at the repository root, and private client/workspace data belongs in ignored local workspace directories.

## Product Source And Management Installs

`ai-system-dev` is the product-development checkout for AI System. It is the place to change `.systems/**`, validators, templates, root contract templates, update scripts, validation scripts, `HUMANS.md`, and `README.md`.

Downloaded or installed AI System checkouts are management checkouts. Use them for workspace, client, project, dump, memory, checkpoint, prompt composition, and system-insight operations. Do not develop the AI System product inside a management checkout.

When a management checkout needs a system change, prepare that change in the upstream `ai-system-dev` product project and update the management checkout with:

```text
.systems/scripts/update-from-upstream
```

`update-from-upstream` updates system-owned repository files only. It does not modify private runtime workspaces.

After a successful system update, backfill missing neutral schema files in existing workspaces with:

```text
.systems/scripts/update-workspace --dry-run
.systems/scripts/update-workspace
```

For multiple registered workspaces:

```text
.systems/scripts/update-workspace --all --dry-run
.systems/scripts/update-workspace --all
```

`update-workspace` never overwrites existing workspace files. It reports planned creates in dry-run mode and ends normal runs with `No existing workspace files were overwritten.`

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

In the `ai-system-dev` product checkout, the local root `AGENTS.md` may intentionally be governed by the product-development workflow instead of this management template. Do not refresh it from the management template unless that is the explicit task.

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

## Knowledge Capture Gate

Before `AI_SYSTEM_WORK_CLOSURE`, AI System applies `.systems/ai/core/contract-compliance.md`.

This is a required decision point before final task closure, handoff, accepted change, commit-ready or push-ready product-development work, or switching to another work unit. It is not a rule to always write memory.

The agent must decide:

- `Work mode`: `project`, `micro-task`, `micro-project`, `side-task`, `system-maintenance`, or `client-work`;
- `Work mode compliance`: `pass`, `warning`, or `blocked`;
- `Knowledge capture`: `required` or `not-required`;
- `Capture target`: `status/evidence`, memory, distillation, checkpoint, external-memory, system-insights, or `not-applicable`;
- `Reason`: short evidence-backed reason.

Durable capture still needs the correct workspace target, privacy-safe content, and explicit owner-approved write scope unless an existing checkpoint or final-check route authorizes that exact capture.

## Repo-Safe Project State

AI System stores project runtime state outside managed project repositories.

Use:

```text
<workspace>/project-state/<project-slug>/
```

for project status, memory, memory entries, checkpoints, distillations, decisions, and `links.md`.

Use:

```text
<workspace>/projects/<project-slug>/
```

for the real repository, source folder, exported materials, or other project-owned files.

If a project path is inside a git worktree, do not write AI System `status.md`, `memory.md`, `checkpoints/`, `distillations/`, or `decisions/` there automatically. Ask whether to use `project-state/` or colocated local-only state with exact `owner-approved` scope and local `.git/info/exclude` handling.

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
Backfill missing neutral schema files in my selected workspace. Run dry-run first.
```

```text
Review selected workspace dump/incoming and classify files. Do not move, rename, copy, or delete anything without owner-approved.
```

## Safety

- AI classifies before acting.
- File movement needs owner approval.
- External integrations are links or manual context in v1.
- `system-insights` must be anonymized and stored as router entries plus detailed `insights/` files.
- `external-memory` is only for improving AI System itself.
- `project-state` keeps AI System project status, memory, and checkpoints out of managed git repositories.
- `update-workspace` only creates missing neutral schema files in existing workspaces; it must not overwrite runtime data or create `prompting/` by default.
