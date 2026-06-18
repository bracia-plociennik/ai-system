# <PRIMARY_ENTITY_LABEL> Workspace

## Purpose

Private local AI System runtime for `<PRIMARY_ENTITY_LABEL>`.

This workspace stores the primary entity directly at the workspace root.

Workspace home: `<WORKSPACE_HOME>`.

## Entity

- Slug: `<PRIMARY_ENTITY_SLUG>`
- Type: `<PRIMARY_ENTITY_TYPE>`
- Owner: `<PRIMARY_ENTITY_OWNER>`
- Operating lens: `<OPERATING_LENS>`

## Boundaries

- Primary entity materials belong directly in this workspace.
- External client materials belong in `clients/`.
- Private owner context belongs in `humans/` or `memory/` unless it has a separate private workspace.
- Product repositories under `projects/` are private source data; do not read, rewrite, summarize, or expose their contents without exact owner-approved scope.
- Project status, memory, checkpoints, distillations, decisions, and source links belong in `project-state/` by default, not inside git repositories under `projects/`.
- Cross-client or cross-entity lessons promoted to `system-insights/` must follow `.systems/ai/core/system-insights.md` and be anonymized.

## Structure

- `core/` - workspace status, workstreams, indexes, and operational notes.
- `status.md` - current primary entity status.
- `memory.md` - primary entity memory router.
- `context/` - source context and background.
- `dump/` - incoming unclassified or primary-entity-known files.
- `memory/` - detailed primary entity and broad workspace memory entries.
- `checkpoints/` - state snapshots.
- `distillations/` - compressed lessons and summaries.
- `contacts/` - contact notes and relationship context.
- `projects/` - primary entity project repositories or source materials.
- `project-state/` - AI System runtime state for primary entity projects.
- `documents/` - owner-approved primary entity documents.
- `contracts/` - owner-approved primary entity contracts.
- `assets/` - reusable entity assets.
- `links/` - links and external references.
- `notes/` - raw and working notes.
- `decisions/` - durable entity decisions.
- `tasks/` - task notes and routing.
- `clients/` - external client workspaces when this workspace owns client work.
- `micro-projects/` - small standalone work.
- `humans/` - owner-facing summaries.
- `external-memory/` - AI System improvement ideas.
- `system-insights/` - anonymized operating lessons and skill candidates, with detailed entries in `system-insights/insights/`.
- `personal-ops/` - private owner operational records such as daily check-ins and generated analytical indexes.
- `skills/` - user-defined AI skills.
- `archive/` - owner-approved archived material.

## Dump

Use `dump/incoming/` for files already known to belong to the primary entity, or when ownership is unknown or mixed inside this workspace.

When the owner already knows a file belongs to a specific external client, use `clients/<client>/dump/incoming/` instead.

Files here still require classification before movement into documents, assets, projects, contracts, memory, or archive.

## Privacy

This directory may contain private data. Do not commit it.
