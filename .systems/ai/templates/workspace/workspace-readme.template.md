# AI System Generic Workspace: <WORKSPACE_ID>

## Purpose

Private local generic runtime for AI System.

Workspace home: `<WORKSPACE_HOME>`.

## Contents

- `core/` - workspace status, indexes, and operational notes.
- `dump/` - incoming unclassified files.
- `clients/` - client workspaces.
- `owned-assets/` - owner-controlled companies, brands, and commercial assets when they are not the primary entity of this workspace.
- `projects/` - canonical owner project repositories.
- `.worktrees/<repository-id>/<work-id>/` - optional auxiliary Git worktrees.
- `.tmp/<work-id>/` - optional disposable task files; durable QA stays in its owning evidence namespace.
- Directory placement follows `.systems/ai/core/workspace-directory-layout.md`; existing materials require explicit relocation approval.
- `project-state/` - AI System status, memory, checkpoints, distillations, decisions, and source links for projects.
- `capture-state/` - workspace-level Distillation State records and unresolved capture routing.
- `micro-projects/` - small standalone work.
- `humans/` - owner-facing summaries.
- `links/` - provider-agnostic external source registry records and references.
- `memory/` - global workspace memory.
- `external-memory/` - AI System improvement ideas, with counterpart upgrade handoffs under `external-memory/memory/`.
- `system-insights/` - anonymized operating lessons and skill candidates, with detailed entries in `system-insights/insights/`.
- `personal-ops/` - private owner operational records such as daily check-ins and generated analytical indexes.
- `tasks/` may exist for TaskForge/TaskNotes setup templates and owner-approved next-action routing when this workspace is promoted to or used as a primary entity workspace.
- `dreams/` - advisory-only Dreaming Mode reports and owner decision queues.
- `skills/` - user-defined AI skills.
- `archive/` - archived workspace material.

## Privacy

This directory may contain private data. Do not commit it.
