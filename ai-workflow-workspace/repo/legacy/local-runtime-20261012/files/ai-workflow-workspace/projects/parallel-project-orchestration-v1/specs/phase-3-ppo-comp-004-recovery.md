# PPO-COMP-004: recovery

## Scope
- Project/task identity: parallel-project-orchestration-v1:PPO-COMP-004
- Risk: high
- Owner approval: decisions/2026-10-04-compatibility-owner-approval.md
- DoD: Exclusive CAS writes and atomic durable ledger with attempt history and unknown-effect reservations.
- Acceptance/failure matrix: Stale revision, existing lock, crash around replace, unknown termination, duplicate attempt, recovery without proof.
- Producer-consumer boundary: product helper, CLI/preflight or capture consumer, contract/template, positive and negative fixtures.
- Constraints: no deadline/timebox; no counterpart edits, runtime migration, installation, commit/push or final-owner-yes.
- Implementation slice: bounded serial writes in the isolated product worktree; coordinator owns index and all shared runtime routers.
- Quality route: findings-first formal Phase 5, integrated regression, current fingerprints, then accepted Phase 6 and Phase 7.
- Residual risk: cooperative local controls cannot prove hostile-host safety or native sandbox enforcement.

