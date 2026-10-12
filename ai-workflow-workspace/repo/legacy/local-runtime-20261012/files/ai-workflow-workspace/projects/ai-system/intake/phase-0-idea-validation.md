# Phase 0 Idea Validation - AI System

## Source Materials Reviewed

- Owner conversation about a local Mac AI workspace.
- Current AI Workflow repository mode and workspace model.
- Existing `ai-workflow-workspace/` runtime layout.

## What Stays

- Build `ai-system` as a project inside the current `ai-workflow` repository first.
- Use branch `ai-system` only after the project is completed.
- Use `~/ai-system/ai-system-workspace/` as the future local runtime.
- Keep `.systems/` system-owned and free of customer data.
- Use `core/` in the local workspace instead of `repo/`.
- Keep `external-memory/` for improving `ai-system`.
- Keep `system-insights/` for owner competence, offer, process, and work quality.
- Require owner approval before moving files from `dump/`.

## What Needs Improvement

- Memory needs an explicit lifecycle.
- Dump triage needs an approval artifact and status flow.
- `system-insights` needs an anonymization gate.
- Every generated directory needs a README contract.

## Missing Items Added To Architecture

- Distillation reminder rules.
- Soft integration model for Mail, Notion, Google Drive, and Notes.
- Privacy boundary between `.systems/` and `ai-system-workspace/`.
- Post-final branch migration rule.

## Decisions

| Decision | Status | Result |
| --- | --- | --- |
| Use `ai-system` as project workspace in current repo | resolved | yes |
| Stop autopilot before phase 4 | resolved | yes |
| Create `ai-system` branch only after final project closure | resolved | yes |
| Start integrations as links and manual context | resolved | yes |
| Move dump files only after owner approval | resolved | yes |

## Gate Result

`accepted-with-changes`

Accepted project context may be created.

