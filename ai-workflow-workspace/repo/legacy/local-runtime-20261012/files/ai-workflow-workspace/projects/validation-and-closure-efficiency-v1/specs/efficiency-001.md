# EFF-CORE-001 Execution Specification

## Architecture And Accepted Plan

Extend the existing validation runner; use a single `execution_efficiency.py` library for check identity/reuse and typed quality/work records. Do not introduce a service, scheduler, second status database, or implicit cache.
Reuse requires an explicit `--reuse-evidence` source; ordinary/full fresh mode remains the default. CI rejects reuse. Unknown check dependencies force execution.
Input coverage is declared in validation-dependencies.json; registry changes are part of identity. Runtime consumers include scope fingerprints. Repo HEAD is provenance, not an invalidator by itself.
One typed quality record contains assessed baseline, semantic DoD/findings, hashed input and evidence references, capture disposition, refresh fingerprints and whole-process intervals. Historical records remain immutable and are assessed as historical or superseded rather than silently refreshed.
Capability discovery is explicit and read-only. An installed Workflow without capabilities keeps its current full-required gates. The bounded-defect route cannot overrule that contract.

## Definition Of Done

All seven priorities have working producers/consumers, negative-path tests and documentation. Successful identical checks can reuse safely; changed inputs invalidate; failed/incomplete evidence never reuses; unknown dependencies execute. No script or generator issues semantic PASS or owner approval. History stays immutable. Timing coverage and three comparable synthetic samples per variant are reported honestly. Current semantic review remains mandatory.

## Implementation Slices

| Slice | Scope | Verification | Initial state |
| --- | --- | --- | --- |
| EFF-01 | Freeze original runner and baseline; shared identity/reuse and runner flags | focused identity, failure and CLI tests | in-progress |
| EFF-02 | Typed quality producer, lifecycle, selective refresh, environment and timing | schema, tamper, traversal and timing tests | planned |
| EFF-03 | Routing/categories, bounded eligibility and capability fallback | producer-consumer review and fixtures | planned |
| EFF-04 | Docs/wiring, equivalent benchmark, full QA and technical capture | final diff review, full validation, project-scoped Workflow checks | planned |

## Acceptance And Safety

- No deadline does not remove QA. No hidden reductions in coverage or skip flags.
- Safe local isolated fixtures only; no external models, private data or production effects.
- Preflight tools and paths before expensive commands. Local in-scope fix/retest is allowed; scope expansion stops.
- Artifact QA: shared schema validates before atomic no-clobber publication.
- Post-implementation quality: current-diff semantic/adversarial review, behavioral tests and producer-consumer audit before supporting scripts.
- Required verification: focused tests, required artifacts, full AI System chain and project-scoped installed Workflow validation at its required gates.
- Residual risk: dependency declarations may over-invalidate; missing declarations must execute, not speculate. Synthetic timing does not predict whole-agent latency.

## Architecture And Spec Review

Reviewed source-bound reuse, input inventory completeness, interruption, CI/updater freshness, historical lifecycle, owner-approval separation and old-Workflow fallback. The accepted design preserves hard gates. Implement only declared slices; behavioral QA is still required before a verdict.

## Owner Decision Checkpoint

- Decision state: clear
- Owner acceptance: current conversation, complete seven-priority plan and Phase 8 boundary.

## Optional Knowledge Capture

- Target: distillation/checkpoint after verified implementation
- Privacy/scope check: pass
