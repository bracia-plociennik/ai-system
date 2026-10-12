# AI System Change Requests Router

## Purpose

This file indexes project-local change requests for the `ai-system` project.

## Change Request Index

| ID | Timing | Type | Status | Route |
| --- | --- | --- | --- | --- |
| `ASYS-CR-001-compact-contracts` | `pre-final-approval` | `acceptance-gap` | `done` | `phase-fix-loop` |
| `ASYS-CR-002-daily-check-in-v3-integrity` | `post-final-approval` | `defect` | `owner-deferred` | `new-project-iteration` |
| `ASYS-CR-003-all-planned-work-to-6d-do` | `post-final-approval` | `follow-up-enhancement` | `in-progress` | `new-project-iteration` |
| `ASYS-CR-005-spor-daily-weekly` | `post-final-approval` | `feature / contract evolution` | `in-progress` | `new-project-iteration` |
| `ASYS-CR-006-life-alignment-cards` | `post-final-approval` | `feature / behavioral contract` | `done` | `new-project-iteration` |
| `ASYS-CR-007-project-orchestration` | `post-final-approval` | `follow-up-enhancement` | `done` | `new-project-iteration` |
| `ASYS-CR-008-spor-proposals` | `post-final-approval` | `follow-up-enhancement` | `in-progress` | `new-project-iteration` |
| `ASYS-CR-009-unified-aggregates` | `post-final-approval` | `follow-up-enhancement` | `done` | `new-project-iteration` |
| `ASYS-CR-010-overnight-schedules` | `post-final-approval` | `defect` | `done` | `new-project-iteration` |

| `ASYS-CR-011-local-paths` | `post-final-approval` | `follow-up-enhancement` | `done` | `new-project-iteration` |

## Active Change Request

No change request is selected. CR-011 delivery and separate original acceptance are recorded in `implementation/dev-evidence-reconciliation-2026-10-12/delivery-and-history.md`. Independent historical rows retain their last-known dispositions, not current source acceptance.

CR-009 closed on 2026-10-01 after status/scope reconciliation, fresh full Quality with smoke, technical capture/checkpoint and scoped Phase 8. Explicit owner final-owner-yes is applied in `history/asys-cr-009/25ee186/evidence/recovery-phase-8-final-check.md`. No independent open CR is auto-selected or closed.

CR-006 was closed on 2026-09-25 after current product QA, a refreshed checkpoint, project-scoped full validation, Phase 8 final check, and explicit owner `final-owner-yes`. CR-007 was closed separately after installed-baseline Phase 8 and its own owner `final-owner-yes`. Other in-progress change requests remain independent and are not selected as the active change request.

## Completed Change Requests

- `ASYS-CR-010-overnight-schedules`
  - Entry: `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/change-requests/2026-10-02-ai-system-cr-010-overnight-schedules.md`
  - Quality: `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-5-asys-pops-018-overnight-schedules-quality.md`
  - Checkpoint: `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/checkpoints/phase-7-checkpoint-2026-10-02-overnight-schedules.md`
  - Final check and owner approval: unavailable historical original (inventory records its original name) and unavailable historical original (inventory records its original name)
- `ASYS-CR-009-unified-aggregates`
  - Entry: `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/change-requests/2026-10-01-ai-system-cr-009-unified-aggregates.md`
  - Quality: `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/history/asys-cr-009/25ee186/evidence/recovery-phase-5-asys-pops-017-unified-aggregates-quality.md`
  - Checkpoint: `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/checkpoints/phase-7-checkpoint-2026-10-01-cr-009-completion.md`
  - Final check/owner decision: `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/history/asys-cr-009/25ee186/evidence/recovery-phase-8-final-check.md`
- `ASYS-CR-001-compact-contracts`
  - Entry: unavailable historical original (inventory records its original name)
  - Spec: unavailable historical original (inventory records its original name)
  - Spec QA: unavailable historical original (inventory records its original name)
  - Implementation result: unavailable historical original (inventory records its original name)
  - Quality: unavailable historical original (inventory records its original name)
- `ASYS-CR-006-life-alignment-cards`
  - Entry: `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/change-requests/2026-09-15-ai-system-cr-006-life-alignment-cards.md`
  - Quality: `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-5-asys-cr-006-follow-up-quality.md`
  - Checkpoint: `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/checkpoints/phase-7-checkpoint-2026-09-25-asys-cr-006-follow-up.md`
  - Final check: `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-8-asys-cr-006-final-check.md`
- `ASYS-CR-007-project-orchestration`
  - Entry: `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/change-requests/2026-09-28-ai-system-cr-007-project-orchestration.md`
  - Quality: `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-5-asys-cr-007-project-orchestration-quality.md`
  - Checkpoint: `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/checkpoints/phase-7-checkpoint-2026-09-28-asys-cr-007-project-orchestration.md`
  - Technical final check: `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-8-asys-cr-007-final-check-installed-2026-09-28.md`
  - Owner approval and closure: `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-8-asys-cr-007-final-owner-approval-2026-09-28.md`

## CR-012 Intent To Execution Brief

Archived planning entry: `change-requests/2026-10-09-ai-system-cr-012-intent-to-execution-brief.md`. It does not select active work. Subsequent independent product delivery and original planning boundaries are distinguished in `implementation/dev-evidence-reconciliation-2026-10-12/delivery-and-history.md`.

## CR-011 delivered evidence

- Original historical final: `quality/cr-011-final-2026-10-09/phase-8-final-check.md`.
- Actual original owner decision: `quality/phase-8-cr-011-final-owner-approval-2026-10-09.md`.
- Subsequent delivery receipt: `implementation/dev-evidence-reconciliation-2026-10-12/delivery-and-history.md`.
- Historical QA admission: `quality-assessments.json`, never current feature PASS.

Unavailable links for older CRs are explicitly recorded in the inventory; their earlier done labels are last-known historical states, not newly verified acceptance.
