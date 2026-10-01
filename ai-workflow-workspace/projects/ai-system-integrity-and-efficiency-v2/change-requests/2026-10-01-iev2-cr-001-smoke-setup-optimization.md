# IEV2-CR-001-smoke-setup-optimization

## Metadata
| Field | Value |
| --- | --- |
| Change request ID | IEV2-CR-001-smoke-setup-optimization |
| Project | ai-system-integrity-and-efficiency-v2 |
| Date | 2026-10-01 |
| Requested by | owner |
| Timing | pre-final-approval |
| Type | defect |
| Risk | high |
| Status | completed |
| Routing | phase-fix-loop |
| Blocks final-owner-yes | no |

## Owner Request
Plan and implement isolated smoke-suite optimization without reducing coverage; proceed through Phase 8. Final owner approval must bind to the completed current assessment, not an unseen future result.

## Context Checked
- Previous final check: quality/phase-8-final-check.md, FAIL for P2-PERF-001.
- Frozen timing: 198.2723 seconds monolithic versus 228.4555 isolated.
- Product baseline: 28119bf, isolated worktree; parallel CR009 excluded.
- Current task quality, distillation, checkpoint and owner decisions reviewed.

## Triage And Routing Decision
- Affected scope: fixture setup only; no assertion-body, population or domain isolation reduction.
- Risk: shared validation setup and safety boundary; explicit owner implementation request supplies scope approval.
- Route: bounded Phase 5 fix loop, implementation correction, fresh QA, distillation/checkpoint and renewed Phase 8.
- Constraints: continuation of active program no-deadline/no-timebox opt-out; quality floor unchanged.
- Counterpart: advisory handoff only; Workflow source excluded.
- Publication: local reviewable commits only; no push or management rollout.

## Implementation Plan
1. Freeze current Bash copy setup as baseline.
2. Replace per-file shell processes with a standard-library Python copier. Retain full tracked-product inventory, extra files, modes, timestamps, containment and fresh per-domain roots. No hard links or writable shared cache.
3. Add synthetic tests for equivalent copy, independent mutations, missing/linked/escaping sources, unsafe destinations and no partial copy after failed preflight.
4. Review producer-consumer behavior and compare all seven unchanged case-body hashes and 220 negative contracts.
5. Run three complete frozen full repetitions for old isolated, optimized isolated and monolithic reference, with common regression tests/environment. Report wall/child separately and retain rejected runs.
6. A remaining warning or defect means Phase 8 FAIL. Otherwise present technical acceptance awaiting current final-owner-yes.

## Measured Hypothesis Recovery
The first nine comparable runs completed on identical 18-test populations. Copy optimization alone improved old isolated mean 242.2135 seconds to 222.1238 seconds (about 8.29 percent), but remained about 5.37 percent slower than monolithic 210.7982 seconds. All records are retained; this does not clear P2-PERF-001.

The bounded follow-up replaces sequential all-domain scheduling with at most two independent transactions at a time. No body/assertion changes, shared writable fixtures, hard links or unbounded workers. Drain both started transactions on failure, stop future pairs and never emit an all-suite completion marker after failure. Add transaction/failure behavior tests to every frozen variant and repeat the full comparable matrix. This is within the owner's isolated-suite optimization scope; no additional target, write permission or publication scope is introduced.

## DoD And QA
- DoD: optimized isolated setup with unchanged assertions/coverage/safety; comparable performance no worse than monolithic reference.
- Artifact QA: plan/spec and changed evidence hash validation.
- Product QA: helper failure-path tests, current integrity tests, unchanged case bodies, full runs and source/environment/coverage-bound comparison.
- Post-implementation quality: findings-first review, ownership/privacy audit, full chain and project-scoped Workflow artifact checks.
- Residual risk: local timing noise and filesystem cost; no private runtime pilot or external model session.
- Cutline: optional documentation only, never coverage, safety or comparable measurement.

## Evidence Required
- Fixture behavior tests; frozen manifests, nine complete records, comparisons and case-body equivalence.
- Recovery review, capture/checkpoint and current quality/Phase 8.

## Result
- Final status: completed
- Completed at: 2026-10-01
- Links to resulting artifacts: quality/phase-5-iev2-cr-001-smoke-setup-optimization-quality.md; quality/smoke-optimization-timing-review.md; current Phase 8 follows capture/checkpoint and artifact verification
