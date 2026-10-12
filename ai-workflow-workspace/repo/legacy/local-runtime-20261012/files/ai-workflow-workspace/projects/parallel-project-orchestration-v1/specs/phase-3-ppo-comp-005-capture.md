# PPO-COMP-005: capture

## Scope
- Project/task identity: parallel-project-orchestration-v1:PPO-COMP-005
- Risk: high
- Owner approval: decisions/2026-10-04-compatibility-owner-approval.md
- DoD: Shared collection validation; schema2 current owning QA and unique accepted owned distillation.
- Acceptance/failure matrix: Schema1 historical not current PASS; duplicate claim by invalid sibling; foreign namespace; stale QA/hash/head; unaccepted distillation.
- Producer-consumer boundary: product helper, CLI/preflight or capture consumer, contract/template, positive and negative fixtures.
- Constraints: no deadline/timebox; no counterpart edits, runtime migration, installation, commit/push or final-owner-yes.
- Implementation slice: bounded serial writes in the isolated product worktree; coordinator owns index and all shared runtime routers.
- Quality route: findings-first formal Phase 5, integrated regression, current fingerprints, then accepted Phase 6 and Phase 7.
- Residual risk: cooperative local controls cannot prove hostile-host safety or native sandbox enforcement.

