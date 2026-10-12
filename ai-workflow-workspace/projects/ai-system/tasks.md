# AI System Tasks Router

## Purpose

`tasks.md` is the canonical task index and router for this project.

## Task ID Format

`<PROJECT>-<AREA>-<NNN>-<slug>`

## Tasks

Task index state: historical tasks and delivered CR-011; no active implementation selected

| Task ID | Title | Risk | Status | Task Card | Spec | Quality | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ASYS-CORE-001-local-ai-system-mode` | Local AI system mode | Medium | done | none | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/specs/phase-3-ai-system-implementation-package-specification.md` | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-5-ai-system-implementation-package-quality.md` | Defines isolated root `ai-system/`, workspace, branch policy, and mode docs |
| `ASYS-WORKSPACE-002-workspace-layout-templates` | Workspace layout templates | Medium | done | none | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/specs/phase-3-ai-system-implementation-package-specification.md` | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-5-ai-system-implementation-package-quality.md` | Creates template structure under staged `ai-system/` |
| `ASYS-DUMP-003-dump-triage-owner-approval` | Dump triage and owner approval | Medium | done | none | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/specs/phase-3-ai-system-implementation-package-specification.md` | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-5-ai-system-implementation-package-quality.md` | Defines classification before file movement |
| `ASYS-MEMORY-004-memory-lifecycle` | Memory lifecycle | Medium | done | none | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/specs/phase-3-ai-system-implementation-package-specification.md` | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-5-ai-system-implementation-package-quality.md` | Defines raw memory, distillation, checkpoints, and reminders |
| `ASYS-INSIGHTS-005-system-insights-anonymization` | System insights and anonymization | Medium | done | none | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/specs/phase-3-ai-system-implementation-package-specification.md` | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-5-ai-system-implementation-package-quality.md` | Separates system insights from external memory |
| `ASYS-CLIENT-006-client-project-workspaces` | Client and project workspaces | Medium | done | none | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/specs/phase-3-ai-system-implementation-package-specification.md` | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-5-ai-system-implementation-package-quality.md` | Adds client and project directory contracts |
| `ASYS-LINKS-007-soft-integrations` | Soft integrations | Low | done | none | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/specs/phase-3-ai-system-implementation-package-specification.md` | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-5-ai-system-implementation-package-quality.md` | Adds link-based context for Mail, Notion, Drive, Notes |
| `ASYS-GUIDE-008-guide-command-routing` | Guide and command routing | Medium | done | none | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/specs/phase-3-ai-system-implementation-package-specification.md` | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-5-ai-system-implementation-package-quality.md` | Adds commands for dump, distillation, clients, and projects |
| `ASYS-VALIDATION-009-validators-quality` | Validators and quality | Medium | done | none | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/specs/phase-3-ai-system-implementation-package-specification.md` | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-5-ai-system-implementation-package-quality.md` | Adds checks for privacy boundaries and required README files |
| `ASYS-DOCS-010-human-runbook-examples` | Human runbook and examples | Low | done | none | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/specs/phase-3-ai-system-implementation-package-specification.md` | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-5-ai-system-implementation-package-quality.md` | Documents usage examples |
| `ASYS-POPS-011-daily-check-in-v3-integrity` | Daily Check-In v3 integrity fixes | Medium | deferred | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/decisions/2026-10-09-history-reconciliation.md` | none | none | unknown-historical: Historical completion assertions unverified; owner deferral retained. Original paths/status retained in the approved reconciliation and original-task-rows.json. |
| `ASYS-POPS-012-all-planned-work-to-6d-do` | All planned professional work to 6D/DO | Medium | conditional | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/decisions/2026-10-09-history-reconciliation.md` | none | none | unknown-historical: Original done claim unverified; no implementation absence inferred. Original paths/status retained in the approved reconciliation and original-task-rows.json. |
| `ASYS-POPS-013-remove-v3-compatibility` | Remove V3 compatibility | Medium | deferred | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/decisions/2026-10-09-history-reconciliation.md` | none | none | unknown-historical: Historical superseded-decision claim unverified; deferral retained. Original paths/status retained in the approved reconciliation and original-task-rows.json. |
| `ASYS-POPS-014-spor-daily-v4-weekly-check-in` | SPOR Daily V4 and Weekly Check-In | Medium-high | blocked | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/decisions/2026-10-09-history-reconciliation.md` | none | none | unknown-historical: Historical spec/QA unavailable; Phase 8 existence and POPS-015 QA do not close this task. Original paths/status retained in the approved reconciliation and original-task-rows.json. |
| `ASYS-POPS-015-life-alignment-cards` | Life Alignment Cards dla SPOR V4 | High | done | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/tasks/asys-pops-015-life-alignment-cards.md` | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/specs/phase-3-asys-cr-006-life-alignment-specification.md` | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-5-asys-cr-006-follow-up-quality.md` | CR-006 closed with refreshed Phase 7 checkpoint, scoped full validation, Phase 8 final check, and explicit owner `final-owner-yes` |
| `ASYS-CORE-016-project-orchestration` | AI System Project Orchestration V1 | High | done | none | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/specs/phase-3-asys-cr-007-project-orchestration-specification.md` | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-5-asys-cr-007-project-orchestration-quality.md` | CR-007 closed after installed-baseline Phase 8, explicit owner `final-owner-yes`, and scoped final approval evidence |

## Post-final Release Work

- `ASYS-POPS-018-overnight-schedules`: done, medium risk; implementation and installed delivery complete; CR-010 Phase 8 and owner final approval recorded in unavailable historical original (see inventory) and unavailable historical original (see inventory). No history migration or backfill.

- `ASYS-POPS-017-unified-aggregates`: done for implementation, high risk; task `tasks/asys-pops-017-unified-aggregates.md`, spec `specs/phase-3-asys-cr-009-unified-aggregates-specification.md`. Installed delivery complete; CR-009 final acceptance is a separate gate. Historical canonical sources preserved.

- `ASYS-POPS-016-spor-proposals`: in-progress, high risk; task `tasks/asys-pops-016-spor-proposals.md`, spec `specs/phase-3-asys-cr-008-spor-proposals-specification.md`. Approved read-only proposal product and thread scheduler; no historical approval changes.

- `ASYS-RELEASE-POST-branch-ai-system`: deferred until final check and owner approval.
- This release item is intentionally outside the current implementation task index.

## CR-011 Local Paths Iteration

| Task ID | Title | Risk | Status | Task Card | Spec | Quality | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ASYS-CORE-019-local-paths` | Portable local roots and transaction context | high | done | none | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/specs/recovery-phase-3-asys-core-019-local-paths-specification.md` | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/recovery-phase-5-asys-core-019-local-paths-quality.md` | CR-011 delivered; original QA is registered historical, never current source PASS; delivery-and-history.md records separate acceptance/publication |

## CR-012 Intent To Execution Brief Iteration

| Task ID | Title | Risk | Status | Task Card | Spec | Quality | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ASYS-CORE-020-intent-brief` | Interpretacja intencji w AI System | high | conditional | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/tasks/asys-core-020-intent-brief.md` | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/specs/phase-3-asys-core-020-intent-brief-specification.md` | none | archived planning snapshot; original Spec QA is historical; no current task selected or approval inferred |
| `ASYS-INT-021-intent-brief-compatibility` | Zgodność instalacji i dowody zachowania | high | conditional | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/tasks/asys-int-021-intent-brief-compatibility.md` | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/specs/phase-3-asys-int-021-intent-brief-compatibility-specification.md` | none | archived planning snapshot; original Spec QA is historical; no current task selected or approval inferred |

## Evidence eligibility and current continuation

All prior done/deferred/conditional/blocked labels retain their historical scope. Original package evidence is byte-restored pre-V1 history. CR-011 Quality and final assessment are admitted historical via `quality-assessments.json`; the actual original final-owner decision is separately bound. No report listed here grants fresh current-HEAD QA. The documented task card/spec references are committed historical inputs, not a selected new execution.

Current continuation and delivery: `implementation/dev-evidence-reconciliation-2026-10-12/delivery-and-history.md`.
Historical availability/provenance: `implementation/dev-evidence-reconciliation-2026-10-12/evidence-inventory.json` and `decisions/2026-10-09-history-reconciliation.md`.
