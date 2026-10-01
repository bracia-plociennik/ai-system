# AI System Tasks Router

## Purpose

`tasks.md` is the canonical task index and router for this project.

## Task ID Format

`<PROJECT>-<AREA>-<NNN>-<slug>`

## Tasks

Task index state: `phase-2-project-plan-pass`

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
| `ASYS-POPS-011-daily-check-in-v3-integrity` | Daily Check-In v3 integrity fixes | Medium | deferred | none | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/specs/phase-3-asys-pops-011-daily-check-in-v3-integrity-specification.md` | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-5-asys-pops-011-daily-check-in-v3-integrity-quality.md` | Implementation, quality, distillation, and checkpoint complete; owner deferred phase 8 and real runtime pilot on 2026-07-14 |
| `ASYS-POPS-012-all-planned-work-to-6d-do` | All planned professional work to 6D/DO | Medium | done | none | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/specs/phase-3-asys-pops-012-all-planned-work-to-6d-do-specification.md` | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-5-asys-pops-012-all-planned-work-to-6d-do-quality.md` | Post-final enhancement completed; all professional plan items create 6D/DO TaskNotes; standalone or linked WIG has no task emission |
| `ASYS-POPS-013-remove-v3-compatibility` | Remove V3 compatibility | Medium | deferred | none | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/change-requests/2026-07-14-ai-system-cr-004-remove-v3-compatibility.md` | none | Superseded by the later compatibility-preserving product decision; retained as historical decision evidence |
| `ASYS-POPS-014-spor-daily-v4-weekly-check-in` | SPOR Daily V4 and Weekly Check-In | Medium-high | in-progress | none | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/specs/phase-3-asys-pops-014-spor-v4-specification.md` | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-5-asys-pops-014-quality.md` | Phase 8 evidence exists; no separate task closure is inferred here |
| `ASYS-POPS-015-life-alignment-cards` | Life Alignment Cards dla SPOR V4 | High | done | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/tasks/asys-pops-015-life-alignment-cards.md` | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/specs/phase-3-asys-cr-006-life-alignment-specification.md` | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-5-asys-cr-006-follow-up-quality.md` | CR-006 closed with refreshed Phase 7 checkpoint, scoped full validation, Phase 8 final check, and explicit owner `final-owner-yes` |
| `ASYS-CORE-016-project-orchestration` | AI System Project Orchestration V1 | High | done | none | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/specs/phase-3-asys-cr-007-project-orchestration-specification.md` | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-5-asys-cr-007-project-orchestration-quality.md` | CR-007 closed after installed-baseline Phase 8, explicit owner `final-owner-yes`, and scoped final approval evidence |

## Post-final Release Work

- `ASYS-POPS-017-unified-aggregates`: done for implementation, high risk; task `tasks/asys-pops-017-unified-aggregates.md`, spec `specs/phase-3-asys-cr-009-unified-aggregates-specification.md`. Installed delivery complete; CR-009 final acceptance is a separate gate. Historical canonical sources preserved.

- `ASYS-POPS-016-spor-proposals`: in-progress, high risk; task `tasks/asys-pops-016-spor-proposals.md`, spec `specs/phase-3-asys-cr-008-spor-proposals-specification.md`. Approved read-only proposal product and thread scheduler; no historical approval changes.

- `ASYS-RELEASE-POST-branch-ai-system`: deferred until final check and owner approval.
- This release item is intentionally outside the current implementation task index.
