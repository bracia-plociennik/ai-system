# Phase 3 Specification - AI System Implementation Package

## Spec Result

`PASS`

## Package Scope

Prepare the `ai-system` local workspace variant as an isolated staging system under the repository root directory:

```text
ai-system/
```

Implementation must not modify root AI Workflow files such as `AGENTS.md`, `HUMANS.md`, `README.md`, `.github/`, `.gitignore`, or the existing root `.systems/**`.

The isolated `ai-system/` directory will later be promoted to a dedicated branch after final check and owner approval.

## In Scope

- Local mode documentation for `~/ai-system/` and `~/ai-system/ai-system-workspace/`.
- Staging root under `ai-system/` with local system docs, template entrypoints, scripts, and examples.
- Workspace templates for `core/`, `dump/`, `clients/`, `projects/`, `micro-projects`, `humans`, `memory`, `external-memory`, `system-insights`, `skills`, and `archive`.
- README contract for every generated directory.
- Dump triage policy: classify first, owner approval before moving, copying, deleting, or renaming.
- Memory lifecycle: raw memory, distillation, checkpoints, reminders, archive.
- `external-memory` for improving `ai-system`.
- `system-insights` for anonymized owner competence, offer, process, and work-quality lessons.
- Soft integrations as links and manual context only.
- Guide and command routing for local workspace operations.
- Validators for required README files and privacy boundaries.
- Human runbook and examples.
- Branch promotion instructions for moving `ai-system/` contents to a future branch root.

## Out Of Scope

- Running phase 4 in this autopilot run.
- Creating branch `ai-system` before final project closure.
- Editing root AI Workflow files outside `ai-system/`.
- Editing existing root `.systems/**`.
- Real Mail, Notion, Google Drive, or Notes API access.
- Real customer data fixtures.
- Automatic destructive file operations.
- Storing private customer data in `.systems/`.

## Acceptance Criteria

- `ai-system` mode is clear enough for a user to initialize and use a local workspace.
- `ai-system-workspace/` is documented as private local runtime.
- All implementation files are scoped under `ai-system/`.
- Root AI Workflow files remain unchanged except workflow runtime artifacts under `ai-workflow-workspace/**`.
- Dump flow has explicit classification and owner approval states.
- Memory and distillation rules are clear at workspace, client, and project levels.
- `system-insights` requires anonymization.
- `external-memory` is reserved for `ai-system` improvements.
- Every generated directory template includes README guidance.
- Validation commands pass after implementation.
- Final branch migration is documented as post-final release work.

## Required Implementation Boundaries

- Do not implement real external integrations.
- Do not process real client files in tests.
- Do not start phase 4 without owner command.
- Do not modify root `AGENTS.md`, `HUMANS.md`, `README.md`, `.github/`, `.gitignore`, or existing root `.systems/**`.
- Keep examples synthetic.
- Implement the local system as staged docs/templates/scripts/examples under `ai-system/`.

## Required Staging Layout

```text
ai-system/
  README.md
  agents.template.md
  humans.template.md
  .gitignore
  .systems/
    README.md
    ai/
      core/
      templates/
      skills/
      examples/
    scripts/
```

Use lowercase `agents.template.md` and `humans.template.md` while staged under `ai-system/` because the current workflow naming validator only exempts root `AGENTS.md` and root `HUMANS.md`. Branch promotion may rename them to uppercase root entrypoints after the `ai-system` branch is created.

## Required Local Workspace Template

The staged system must define a future private workspace:

```text
~/ai-system/ai-system-workspace/
```

and template or document this runtime layout:

```text
ai-system-workspace/
  README.md
  core/
  dump/
  clients/
  projects/
  micro-projects/
  humans/
  memory/
  external-memory/
  system-insights/
  skills/
  archive/
```

Every generated directory must have a `README.md` contract.

## Verification Commands

```sh
git diff --check
.systems/scripts/validate-workflow
.systems/scripts/check-naming
.systems/scripts/check-required-artifacts
.systems/scripts/check-status-consistency
.systems/scripts/check-qa-evidence
```

Additional isolated-system commands expected after implementation:

```sh
ai-system/.systems/scripts/validate-ai-system
ai-system/.systems/scripts/check-readmes
ai-system/.systems/scripts/check-privacy-boundary
```

## Rollback Notes

The implementation should be reversible by removing or reverting `ai-system/` plus workflow runtime artifacts. No real customer data or external accounts should be affected.
