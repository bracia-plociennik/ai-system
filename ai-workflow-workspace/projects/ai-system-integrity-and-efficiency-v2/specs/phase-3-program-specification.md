# Program Specification

## Required Behaviors
- IEV2-VAL-001-typed-negative-assertions: Exact rejection codes and cause-specific diagnostics; infrastructure errors never count as expected failures.
- IEV2-SKL-002-eval-freshness: Producer and standalone aggregator bind complete plans, inputs and grades; reject stale or orphan grades before writes.
- IEV2-VAL-003-evidence-destinations: Canonical ownership, symlink containment, immutable outputs and atomic no-clobber writes.
- IEV2-UPD-004-canonical-updater: Equal/behind only; ahead/diverged stop with local state preserved.
- IEV2-VAL-005-validation-lifecycle: Actual execution states, source digest, run ID, monotonic durations, timeout/interrupt, exactly one completion marker.
- IEV2-VAL-006-comparable-timing: At least three complete equivalent runs; parent wall time distinct from child attribution; reject source/coverage drift.
- IEV2-VAL-007-scoped-coverage: Declared dependencies, owned-runtime manifests, checkpoint eligibility and isolated smoke transactions with equivalence evidence.
- IEV2-OPS-008-bounded-recovery: Retain failed evidence, hypothesis per retry, no guard weakening, changed source invalidates closure.
- IEV2-SKL-009-metadata-discovery: Frontmatter-only candidate discovery, workspace precedence, full matched contract and traceable opened paths.
- IEV2-DRM-010-dream-lifecycle: Versioned recommendation identity and decision evidence; immutable history and advisory-only boundaries.
- IEV2-OPS-011-freshness-topology: On-demand scoped metadata and producer-consumer reports without private-content crawling.

## Test Matrix
Wrong exit/diagnostic, 126/127/signals, incomplete smoke run; changed plan/source, unknown grade, metadata tampering, unchanged rejected run; tracked/deleted-tracked product, symlink parent and collision outputs; local equal/behind/ahead/diverged repos; success/early failure/timeout/interruption actual check states; three equivalent measurements versus drift/mismatch; explicit dependencies, runtime ownership and full-required shared changes; failure hypothesis and post-fix freshness; should-trigger/near-miss/workspace precedence and actual reads; Dream transition, changed decision hash and privacy; selected-root metadata-only diagnostics.

## Implementation Slice Plan
Source: owner-approved complete plan and this spec. DoD source: per-task required behaviors above.

| slice id | goal | expected files/areas | acceptance check | evidence required | status |
| --- | --- | --- | --- | --- | --- |
| IEV2-VAL-001-typed-negative-assertions | Typed negative assertions | product scripts/contracts/templates/tests | required behavior and failure-path matrix | regression output plus semantic review | planned |
| IEV2-SKL-002-eval-freshness | Eval freshness | product scripts/contracts/templates/tests | required behavior and failure-path matrix | regression output plus semantic review | planned |
| IEV2-VAL-003-evidence-destinations | Evidence destinations | product scripts/contracts/templates/tests | required behavior and failure-path matrix | regression output plus semantic review | planned |
| IEV2-UPD-004-canonical-updater | Canonical updater | product scripts/contracts/templates/tests | required behavior and failure-path matrix | regression output plus semantic review | planned |
| IEV2-VAL-005-validation-lifecycle | Validation lifecycle | product scripts/contracts/templates/tests | required behavior and failure-path matrix | regression output plus semantic review | planned |
| IEV2-VAL-006-comparable-timing | Comparable timing | product scripts/contracts/templates/tests | required behavior and failure-path matrix | regression output plus semantic review | planned |
| IEV2-VAL-007-scoped-coverage | Scoped coverage | product scripts/contracts/templates/tests | required behavior and failure-path matrix | regression output plus semantic review | planned |
| IEV2-OPS-008-bounded-recovery | Bounded recovery | product scripts/contracts/templates/tests | required behavior and failure-path matrix | regression output plus semantic review | planned |
| IEV2-SKL-009-metadata-discovery | Metadata discovery | product scripts/contracts/templates/tests | required behavior and failure-path matrix | regression output plus semantic review | planned |
| IEV2-DRM-010-dream-lifecycle | Dream lifecycle | product scripts/contracts/templates/tests | required behavior and failure-path matrix | regression output plus semantic review | planned |
| IEV2-OPS-011-freshness-topology | Freshness and topology | product scripts/contracts/templates/tests | required behavior and failure-path matrix | regression output plus semantic review | planned |

## Stop Rule
Stop on scope expansion, private data requirement, unavailable permission or material ambiguity. Preserve failed results. Fix in-scope defects with recorded diagnosis and retest; never weaken protected assertions.

## Instruction Refresh
Full refresh: root shim, nested AGENTS, implementation slicing, risk/permissions, delivery constraints, plan quality, full QA and Phase 8; baseline dabbf3457b98cd28f44b7785f14ece51b5932017; CR-009 dirty runtime excluded by isolated worktree.

