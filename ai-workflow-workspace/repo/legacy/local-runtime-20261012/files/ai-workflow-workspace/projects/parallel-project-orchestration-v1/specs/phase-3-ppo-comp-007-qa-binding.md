# PPO-COMP-007: qa-binding

## Scope
- Project/task identity: parallel-project-orchestration-v1:PPO-COMP-007
- Risk: high
- Owner approval: decisions/2026-10-04-compatibility-owner-approval.md
- DoD: Complete immutable snapshot plus real HEAD/tree/index/live proof; unsupported cases require fresh QA.
- Acceptance/failure matrix: Partial staging, extra ignored file, dependency drift, modes, raw parent mismatch, hook mutation, tracked runtime or missing target proof.
- Producer-consumer boundary: product helper, CLI/preflight or capture consumer, contract/template, positive and negative fixtures.
- Constraints: no deadline/timebox; no counterpart edits, runtime migration, installation, commit/push or final-owner-yes.
- Implementation slice: bounded serial writes in the isolated product worktree; coordinator owns index and all shared runtime routers.
- Quality route: findings-first formal Phase 5, integrated regression, current fingerprints, then accepted Phase 6 and Phase 7.
- Residual risk: cooperative local controls cannot prove hostile-host safety or native sandbox enforcement.

