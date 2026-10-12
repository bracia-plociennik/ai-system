# Phase 6 Distillation - ASYS-CORE-016 Project Orchestration

## Metadata

- Project: `ai-system`
- Task/package ID: `ASYS-CORE-016-project-orchestration`
- Date: `2026-09-28`
- Workflow phase: `phase-6-distillation`
- Quality artifact: `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-5-asys-cr-007-project-orchestration-quality.md`
- Implementation artifact: `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-4-asys-cr-007-project-orchestration-implementation-result.md`
- Specification: `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/specs/phase-3-asys-cr-007-project-orchestration-specification.md`
- memory-in-repo-memory: true
- Processed by checkpoint: `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/checkpoints/phase-7-checkpoint-2026-09-28-asys-cr-007-project-orchestration.md`

## What Was Done

- AI System gained a compact project-orchestration contract, coordination record template, read-only preflight, and routing/validation wiring.
- Local AI Workflow remains authoritative for project route, risk, phases, evidence, and technical memory. No nested Workflow product change was made.

## Problems Encountered

| Problem | Resolution | Future Relevance |
| --- | --- | --- |
| A path helper initially accepted symlinked Workflow status and owner aliases. | Reject symlinked or escaped status and project-state paths; cover them with synthetic fixtures. | Discovery helpers must not read a different project or owner through a path alias. |
| The helper initially required root-level `project-state/`. | Accept normalized nearest-owner client/asset paths contained in the selected workspace. | Client and asset work cannot be forced into a root-only namespace. |
| A tracked handoff decision initially contained an absolute local home path. | Add workspace-relative handoff validation and store only the relative path in CR evidence. | Cross-system evidence should be verifiable without publishing a local path. |
| Workflow validation and QA evidence have cwd/format contracts. | Run Workflow scripts from the nested clone and write Phase 5 evidence in the full current format. | A green product validator cannot replace formal Workflow evidence. |

## Decisions

| Decision | Reason | Future Impact |
| --- | --- | --- |
| AI System is the owner-facing coordinator, not a duplicate Workflow engine. | The project-local Workflow knows its own version, gates, and state. | Read local contracts for every selected target instead of hardcoding process rules centrally. |
| The orchestration record is a pointer, not approval or technical memory. | Copying state creates drift and can widen authority. | Preserve exact owner-instruction reference and link to accepted local evidence. |
| One write owner per target write set. | Concurrent writers can invalidate baselines and QA. | Unknown or overlapping writers stop target writes; resume rechecks source state. |
| Product publication approval is not target-project push approval. | Cross-project authority must remain explicit. | Future delegated work needs its own target-scoped approval for push or external effects. |

## Rules For Future Tasks

- Resolve the selected workspace, nearest owner, real Git root, installed local Workflow, project ID, and current status before selecting a route.
- Treat `inspect-local-gates` as read-only evidence, not permission, route selection, or QA.
- Let the target Workflow own technical status and distillation; AI System keeps business summary and evidence links.
- Review DoD, diff, tests, skipped checks, capture, and Git state before reporting completion. Do not accept a worker's `done` message alone.
- Recheck Git and Workflow after interruption; do not replay completed writes from a stale orchestration record.

## Memory And Insight Decision

- Project memory: yes, a concise routing rule is needed for future AI System changes; target `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/memory/2026-09-28-project-orchestration-v1.md`.
- Repo memory: no separate entry; the lesson is scoped to AI System's orchestration product.
- System Insight Candidate: none; no domain lesson is being promoted.
- Cross-system handoff: yes, a privacy-safe AI Workflow adaptation note is required by the owner decision, but it grants no counterpart write authority.
- Privacy/scope check: pass; no client source, identifiers, secrets, or production data are copied.

## Gate And Risk

- Phase 5 product QA: PASS for scoped implementation, not a Phase 8 final check.
- Owner decision checkpoint: approved plan includes this distillation and checkpoint; no new production or target-project action is authorized.
- Optional knowledge capture: project memory now; no external or System Insight promotion.
- Residual risk: V1 relies on agent judgment for instruction conflicts, route selection, concurrent writers, and semantic result review. Synthetic preflight does not prove behavior on private target repos.
