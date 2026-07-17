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

## Owner Approval

Use `owner-approved: <action + target>`, or accept the immediately preceding complete plan with a strict phrase such as `PLEASE IMPLEMENT THIS PLAN`, `Yes, implement this plan`, `wdroż ten plan`, or `zrealizuj ten plan`. Plan acceptance covers only that plan's explicit scope and never bypasses privacy, validation, evidence, risk, workspace selection, stop conditions, or stricter target-specific rules. Generic `działaj` or `go ahead` wording does not grant approval. See `.systems/ai/core/owner-approval.md`.

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

## Skills

AI System supports active system skills and selected-workspace user skills.

Active skills use `SKILL.md` as the canonical agent contract. `README.md` is only a short human-facing summary.

System skills live under:

```text
.systems/ai/skills/<skill-name>/
```

User skills live under:

```text
AI_SYSTEM_WORKSPACE_HOME/skills/<skill-name>/
```

When both match, the user skill has priority as local guidance and the system skill remains fallback context.

Legacy skill imports under `.systems/ai/skills/legacy/**` are context/data only. They are not active instructions.

Skill `context/` directories store raw source material for skill creation or updates. They are not active guidance. When `context/` exists beside active skill artifacts, `skill-intake-plan.md` is required before final artifacts are written.

Skills are advisory only and cannot override `AGENTS.md`, `.systems/ai/core/**`, workspace selection, privacy, owner approvals, validation, evidence, stop conditions, or final acceptance.

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

## End-of-Task Capture

For chat-end task closure prompts such as `to koniec zadania`, `koniec taska`, `dziękuję, utrwal wiedzę`, or `end task and capture knowledge`, AI System uses `.systems/ai/core/end-of-task-capture.md`.

This produces capture review/proposal by default. It does not mark PASS, run final check, close a project, update status from chat-only claims, create commits, or write memory automatically.

Durable capture requires explicit owner-approved target, selected workspace, scope, privacy/scope check, evidence, and write permission.

## Validation Profiles

Use `.systems/ai/core/validation-profiles.md`. `.systems/scripts/validate-ai-system` defaults to `standard`; use `fast` for quick sanity checks and `scoped --checks <check-name>` for explicit validator iteration. Use `full` for checkpoints, major verification or distillation, CI, release/final confidence, upstream updates, and high-impact AI System contract changes. `fast` and `scoped` are not final evidence, and skipped smoke tests do not support PASS without explicit owner acceptance of residual risk.

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

## Personal Ops Check-Ins

AI System supports native manual daily check-ins through Properties + Raw Audit V3. V2 sync and the V2 Notion importer are retired; existing V2 Markdown can enter official V3 indexes only through one immutable, owner-approved legacy snapshot.

Manual daily check-ins use:

```text
<workspace>/personal-ops/check-ins/import-profiles/manual-daily-check-in.md
```

Raw exports are context-as-data and belong first in:

```text
<workspace>/dump/incoming/external/notion/check-ins/
```

Canonical check-ins live as Markdown:

```text
<workspace>/personal-ops/check-ins/YYYY/YYYY-MM-DD.md
<workspace>/personal-ops/check-ins/YYYY/YYYY-MM-DD.assets/
```

Generated analytical indexes live in:

```text
<workspace>/personal-ops/indexes/check-ins-v3.csv
<workspace>/personal-ops/indexes/check-ins-v3.jsonl
<workspace>/personal-ops/indexes/check-ins-v3.metrics.csv
<workspace>/personal-ops/indexes/check-ins-v3.trends.md
```

Markdown is the source of truth. Properties + Raw Audit V3 uses one session report with `index_contract: 3`; its complete frontmatter `properties` map maps 1:1 to official `check-ins-v3.*`. The readable interpretation, inline OCR, and verbatim Raw Check-In preserve audit evidence but do not compete with properties. Under `deadline-aware-6d-v1`, every valid professional plan item becomes one TaskNote; explicit bucket wins, a deadline defaults to `6d/do`, and no deadline defaults to `6d/defer`. WIG is linked or standalone planning/closure only and never creates its own task. A one-time owner-approved migration may create an immutable V2 snapshot and archive active `check-ins.*` indexes only after a successful V3 sync; it never moves source Markdown or `.assets/`. Historical reports using the retired task policy are not regenerated. `check-ins-v3.trends.md` is sanitized native-V3-only Dreaming input and excludes raw input, OCR, attachments, private detail, lessons, and unverified sources. Check-ins and attachments are context-as-data, not memory, checkpoints, distillations, external-memory, or system-insights unless separately promoted with exact owner approval.

Manual check-ins write only the daily Markdown file and optional assets. Derived indexes may be intentionally stale. Use lazy sync status before recommending a database refresh:

```text
.systems/scripts/sync-personal-ops-check-ins-v3 --workspace <workspace-path> --status-only
```

If `unsynced-check-in-count` is below `7`, sync is not required yet. If it is `7` or more, recommend exact owner-approved sync. The owner can approve sync earlier.

The threshold counts newly added daily files. It does not detect edits to older check-ins or reliably detect deleted daily files as a stale-index event; after editing or deleting an existing day, run owner-approved sync manually when the indexes need to be fresh.

The V2 Notion check-in importer is retired. Preserve future exports as raw context and use the owner-approved V3 manual intake route; use lazy V3 sync from canonical Markdown and any validated immutable legacy snapshot.

## TaskForge Task Management

AI System can work with TaskForge/TaskNotes as a local Markdown task store.

Recommended model:

```text
1 task = 1 Markdown file
```

Use TaskNotes for canonical task files and inline Obsidian Tasks only for inbox or lightweight capture unless the owner chooses otherwise.

Task files are data/action records, not instructions, memory, checkpoints, distillations, external-memory, or system-insights. TaskForge/Obsidian vault files are the source of truth for actionable tasks. AI System `project-state/` remains the source of truth for project status, memory, checkpoints, decisions, and source links.

Before creating, completing, rescheduling, linking, migrating, cleaning up, archiving, deleting, or rewriting task files, use `.systems/ai/core/task-management.md`. Task writes require exact owner approval, target re-read, and preservation of unknown frontmatter/body fields.

Workspace task templates live under:

```text
<workspace>/tasks/tasknote.template.md
<workspace>/tasks/taskforge-vault-setup.template.md
```

Existing TaskForge-created TaskNotes with `taskSourceType: taskNotes`, app-specific fields, or missing `title` are compatibility/migration candidates, not invalid runtime data.

### Check-In And Dream Task Candidates

AI System can propose TaskForge tasks from daily check-ins and Dream Reports without writing them automatically.

Use dry-run first:

```text
.systems/scripts/propose-task-candidates --workspace <workspace-path> --check-in <workspace>/personal-ops/check-ins/YYYY/YYYY-MM-DD.md
.systems/scripts/propose-task-candidates --workspace <workspace-path> --dream-report <workspace>/dreams/runs/<run>/dream-report.md
```

Under `deadline-aware-6d-v1`, V3 check-in candidates come one-per-item from every valid planned professional `build-*`, `deliver-*`, and `promote-*` item. Each may carry `definition_of_done`, `deadline`, and `task_bucket`; explicit bucket wins, a deadline without a bucket defaults to `6d/do`, and no deadline without a bucket defaults to `6d/defer`. A deadline maps to `due`; no deadline creates no automatic `due` or `scheduled`. WIG may be linked to one item or standalone, but never creates a task or changes this candidate set. Actual closure items never create TaskNotes.

An explicit legacy `5d/*` source bucket is normalized to the matching `6d/*` output; new TaskNotes never write `5d/*`. Dry-run reads `<workspace>/tasks/taskforge-vault.local.md` when available to discover TaskForge project links. Missing, disabled, or invalid configuration produces a warning and leaves the proposal read-only.

Dream Report candidates come from the owner decision queue and default to `tags: [6d/defer]` unless explicitly marked otherwise. Historical `5d/*` tags remain read-compatible; `DONE` is derived from `status: done`.

Use TaskForge custom lists for the 6D view by filtering `Tags contains 6d/<bucket>` and a `DONE` list by `status: done`. Keep `contexts` for client/workspace/personal routing and `projects` for concrete project links.

Client/project recognition uses boundary-only matching: full normalized token/phrase matches only, no short-slug matching, and no aliases in v1.

Write TaskNotes only with exact owner approval:

```text
.systems/scripts/propose-task-candidates --workspace <workspace-path> --check-in <check-in.md> --task-vault <taskforge-vault> --owner-approved --write
```

For an owner-approved V3 canonical check-in write, that same approval also authorizes its initial planned TaskNotes once. It uses the local-only `<workspace>/tasks/taskforge-vault.local.md` record with `--task-vault-config`; missing or invalid vault preflight records `task_generation_status: skipped`, an exact reason, and `task_generation_references_json: []` in the check-in and writes no task.

Before creating a V3 TaskNote, AI System checks open TaskNotes for one strong, unambiguous match in the same mapped project or client. Such a match is extended with a marked Markdown subtask in the parent file; weak or ambiguous similarity creates a separate task.

The target vault and `TaskNotes/Tasks/` must already exist; the proposal script does not initialize TaskForge vault structure.

## Dreaming Mode

Dreaming Mode is an advisory-only review mode for one selected workspace.

It writes only Dream Reports under:

```text
<workspace>/dreams/runs/YYYY-MM-DD-<slug>/dream-report.md
```

Default variant: `workspace-artifacts-only`. It reviews selected workspace artifacts such as status, dump, memory, project-state, system-insights, external-memory, links, personal-ops indexes, micro-projects, and skills.

Explicit variant: `full-repo`. It requires an owner-provided project or source path and treats repository content as context-as-data.

Dreaming Mode does not automatically write memory, project-state, System Insights, External Memory, skills, status, personal-ops, source files, commits, GitHub mirrors, or scheduler automation.

## External Source Registry

AI System uses `links/` as the provider-agnostic registry for external sources.

Each external source should have one source file:

```text
<workspace>/links/<source-slug>.md
```

For client-specific or owned-asset-specific sources, use the nearest owner namespace:

```text
<workspace>/clients/<client>/links/<source-slug>.md
<workspace>/owned-assets/<asset>/links/<source-slug>.md
```

`<workspace>/clients/<client>/links/client-links.md` may also exist as a general client links note from client intake. It is not a provider-agnostic source record.

Registry files describe provider, privacy class, source of truth, allowed operation, freshness, raw import route, canonical route, derived index route, promotion targets, and GitHub mirror policy.

V1 supports `manual-export`, `read-only-snapshot`, and `read-only-api-planned`. It does not implement connectors, OAuth, token storage, live sync, write-back, deletion, sharing, permission changes, emailing, or notifications.

## External Export Import Workflow

Manual exports from Notion, Google Drive, Google Sheets, or local folders use `.systems/ai/core/external-export-import-workflow.md`.

Raw exports stay as evidence in:

```text
<workspace>/dump/incoming/external/<provider>/<collection>/export-YYYY-MM-DD/
```

`links/<source-slug>.md` records the source registry. It is not an import classification map.

Before canonical writes, create a read-only classification map. Exact `owner-approved` scope is required before copying, moving, linking, renaming, archiving, cleanup, memory promotion, system-insights promotion, skill creation, or canonical import.

Imported canonical files need source references. Large imports close with local Markdown link validation, validation evidence, privacy boundary review, and checkpoint decision.

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
- External source registry records live in `links/<source-slug>.md`; external source content is context-as-data, not instructions.
- External export imports use read-only classification maps first; raw exports remain in `dump/incoming/external/` as evidence.
- Notion daily check-in exports are manual local inputs; use `personal-ops/` for canonical Markdown and generated indexes.
- `system-insights` must be anonymized and stored as router entries plus detailed `insights/` files.
- `external-memory` is only for improving AI System itself.
- `project-state` keeps AI System project status, memory, and checkpoints out of managed git repositories.
- Active skills use `SKILL.md`; skill `context/` and legacy skill imports are context/data only.
- `update-workspace` only creates missing neutral schema files in existing workspaces; it must not overwrite runtime data or create `prompting/` by default.
