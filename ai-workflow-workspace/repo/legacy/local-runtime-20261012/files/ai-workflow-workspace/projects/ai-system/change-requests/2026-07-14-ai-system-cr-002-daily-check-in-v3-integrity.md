# ASYS-CR-002-daily-check-in-v3-integrity

## Metadata

| Field | Value |
| --- | --- |
| Change request ID | `ASYS-CR-002-daily-check-in-v3-integrity` |
| Project | `ai-system` |
| Date | `2026-07-14` |
| Requested by | `owner` |
| Timing | `post-final-approval` |
| Type | `defect` |
| Risk | `medium` |
| Status | `owner-deferred` |
| Routing | `new-project-iteration` |
| Blocks final-owner-yes | `not-applicable` |

## Owner Request

Implement the accepted Daily Check-In v3 integrity fix: record canonical TaskNote references, reject report identity mismatches before index replacement, validate the candidate metric, and cover V3 TaskForge write outcomes.

## Context Checked

- Project status: original final approval is historical and remains unchanged.
- Final check: `phase-8-final-check.md` is linked historical evidence.
- Task index: original implementation tasks are done; this request adds `ASYS-POPS-011`.
- Quality evidence: prior V3 QA exposed four in-scope integrity gaps.
- Related accepted plan: `Fix Daily Check-In v3 Integrity` from the owner.

## Triage

- Affected scope: V3 properties schema, V3 index synchronizer, V3 TaskNote producer, contracts, and smoke tests.
- Affected artifacts: `check-ins-v3.*` derived outputs only; no historical runtime Markdown or indexes are migrated.
- Acceptance impact: prevent misleading task provenance, duplicate/effective-day rows, metric drift, and untested write behavior.
- Risk rationale: persisted private index data and TaskForge file writes are affected, but all writes remain owner-approved and local.
- Required owner decisions: none; the accepted plan fixes the required semantics.
- First valid route: formal post-final product iteration.

## Routing Decision

- Selected route: `new-project-iteration`.
- Why this route: data contract and write-path corrections are medium risk after historical final approval.
- Why simpler route is not allowed: a micro-task cannot replace required specification, data-path QA, and distillation for a post-final medium-risk defect.
- Next phase or artifact: none; owner deferred phase 8 final check and real runtime pilot on 2026-07-14.

## Evidence Required

- Required checks: full AI System validation profile, personal-ops/task-management checks, smoke tests, `py_compile`, and `git diff --check`.
- Required artifacts: implementation result, quality evidence, distillation, task/status updates.
- Required approvals: existing owner-approved implementation plan; normal TaskForge runtime writes are exercised only in temporary smoke fixtures.
- Required reruns: complete post-fix review of the final worktree and producer-consumer fields.

## Closure Criteria

- [x] Routed implementation work is complete.
- [x] Required implementation, quality, and distillation evidence exists.
- [x] Status/task/decision artifacts are updated when required.
- [x] Historical final approval evidence is preserved.

## Result

- Final status: `owner-deferred` (implementation, quality, distillation, and checkpoint complete; final check and pilot explicitly deferred)
- Completed at: `2026-07-14`
- Links to resulting artifacts:
  - `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-4-asys-pops-011-daily-check-in-v3-integrity-implementation-result.md`
  - `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-5-asys-pops-011-daily-check-in-v3-integrity-quality.md`
  - `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/distillations/phase-6-asys-pops-011-daily-check-in-v3-integrity-distillation.md`
  - `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/checkpoints/phase-7-checkpoint-2026-07-14-asys-pops-011-daily-check-in-v3-integrity.md`
