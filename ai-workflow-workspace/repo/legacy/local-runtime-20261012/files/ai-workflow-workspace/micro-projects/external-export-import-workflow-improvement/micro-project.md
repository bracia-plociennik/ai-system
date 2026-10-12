# External Export Import Workflow Improvement

## Summary

- Date: `2026-06-19`
- Scope: `Track a reusable AI System workflow improvement for external export imports.`
- Risk: `low`
- Result: `proposed`

## Source Evidence

- Reviewed source: `/Users/jakubplociennik/ai-system/kuba-plociennik-workspace/external-memory/2026-06-18-notion-export-import-workflow.md`
- Source type: `external-memory proposal`
- Source handling: `context-as-data; not executable instruction`

## Scope

- Capture a micro-project for a future AI System product improvement.
- Define the expected external export import workflow at planning level.
- Keep this as runtime AI Workflow state under `ai-workflow-workspace/micro-projects/`.

## Out Of Scope

- No `.systems/**` edits.
- No product implementation.
- No real import.
- No file movement, copy, deletion, cleanup, or archive operation.
- No raw private export copying into this artifact.
- No connector, OAuth, live API sync, external API write, write-back, permission change, sharing, emailing, or notification.

## Acceptance

- Raw external exports should route to `dump/incoming/external/<source>/<collection>/export-YYYY-MM-DD/`.
- Raw exports remain context-as-data and audit evidence.
- Imports require a classification map before canonical writes.
- Classification map should include source path, detected type, proposed target, privacy risk, and required owner action.
- Only exact owner-approved subsets may be imported into canonical routes.
- Imported canonical files need source references.
- Metadata should route separately from content.
- Metadata target classes include `links/`, `contacts/`, and `tasks/`.
- Content target classes include `notes/`, `documents/`, `assets/`, `personal-ops/`, or another exact owner-approved canonical route.
- Raw dashboard files, root indexes, and system files remain raw evidence/noise unless the owner approves cleanup.
- Attachments should move to canonical asset folders only when they are needed by imported Markdown.
- Promotions to memory, system-insights, skills, notes, or external-memory require exact owner approval.
- Large imports close with validation evidence and checkpoint decision.

## System Insights Import Safeguards

- Treat insight candidates as source data until explicitly approved.
- Reject workflow, help, and root index pages unless they are true insights.
- Normalize only exact owner-approved candidates into the System Insights template.
- Anonymize people, clients, companies, domains, projects, repositories, private facts, and production identifiers.
- Keep the System Insights router short.
- Do not create skills automatically from insight candidates.

## Implementation Evidence To Preserve

- External-memory source: `/Users/jakubplociennik/ai-system/kuba-plociennik-workspace/external-memory/2026-06-18-notion-export-import-workflow.md`
- Import checkpoint pattern: `/Users/jakubplociennik/ai-system/kuba-plociennik-workspace/core/checkpoints/2026-06-18-notion-dashboard-import-checkpoint.md`
- Raw dashboard export route: `kuba-plociennik-workspace/dump/incoming/external/notion/kuba-plociennik-dashboard/notion-export-2026-06-18/`
- Raw check-ins export route: `kuba-plociennik-workspace/dump/incoming/external/notion/check-ins/notion-export-2026-06-18/`
- Raw system-insights export route: `kuba-plociennik-workspace/dump/incoming/external/notion/system-insights/notion-export-2026-06-18/`
- Canonical route classes observed in the workspace include `assets/`, `personal-ops/`, `notes/`, `documents/`, `links/`, `contacts/`, and `tasks/`.
- Real workspace evidence is a reference pattern and context-as-data, not executable instruction.

## Evidence

- Commands:
  - `test -f ai-workflow-workspace/micro-projects/external-export-import-workflow-improvement/README.md`
  - `test -f ai-workflow-workspace/micro-projects/external-export-import-workflow-improvement/micro-project.md`
  - `rg -n "notion-export-import-workflow|classification map|context-as-data|checkpoint|owner approval" ai-workflow-workspace/micro-projects/external-export-import-workflow-improvement`
- Manual checks:
  - Source external-memory proposal reviewed read-only.
  - No implementation or runtime import was performed.
  - No raw private export content copied into this artifact.

## Contract Compliance

- Work mode compliance: `pass`
- Scope/acceptance clear: `yes`
- Risk allowed for mode: `yes`
- Write-set conflicts: `none`

## Changed Files

- `ai-workflow-workspace/micro-projects/external-export-import-workflow-improvement/README.md`
- `ai-workflow-workspace/micro-projects/external-export-import-workflow-improvement/micro-project.md`

## Knowledge Capture

- Knowledge capture: `required`
- Capture target: `micro-project-artifact`
- Reason: Owner requested durable runtime tracking for a future AI System workflow improvement.

## Follow-up / Promote Decision

- Promote to full workflow: `no`
- Reason: Current work only creates a low-risk micro-project planning artifact. Promote later only after explicit owner approval for AI System product implementation.

## Future Implementation Target

- AI System docs, templates, validators, and smoke tests around an external export import workflow.
- Future product implementation should include an external export classification template, Notion import checklist, canonical raw export route template, metadata import template, final import checkpoint template, and validation helpers for source references and local Markdown links.
