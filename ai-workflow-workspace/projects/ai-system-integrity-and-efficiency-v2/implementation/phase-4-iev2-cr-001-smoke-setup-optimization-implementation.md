# Smoke Setup Optimization Implementation

## Metadata
- Project: ai-system-integrity-and-efficiency-v2
- Change request: IEV2-CR-001-smoke-setup-optimization
- Date: 2026-10-01
- Scope: isolated smoke setup and bounded all-domain scheduling
- Implementation state: complete; current Quality completed; technical Phase 8 follows capture and artifact checks

## Changes
- Added a standard-library fixture copier with complete tracked-product preflight, safe explicit extras, containment checks and metadata-preserving independent file copies.
- Replaced per-file shell subprocesses without changing any domain assertion/mutation/restore body.
- Added all-suite scheduling with at most two domain subprocesses. The coordinator drains each started pair, retains output in domain order, stops future pairs on failure and emits completion only after all seven domains succeed.
- Added five fixture/scheduling regression tests, retaining all original 15 integrity tests.
- Wired the helper into required artifacts and profile validation, preserving the validated old copier as a legitimate frozen benchmark reference.
- Added documentation of isolation, failure behavior and bounded scheduling.

## Evidence And Recovery
- Copy-only hypothesis: all nine full runs completed on equivalent 18-test populations, but the remaining 5.37 percent monolithic overhead did not satisfy the performance DoD. Retained rather than marketed as complete success.
- Current behavior tests: 20 completed successfully; copy equivalence, independent mutation, metadata, preflight failures, unsafe destinations, bounded subprocesses, drained failure and no later writes.
- Current frozen comparison: same seven suite-body hashes and 220 negative contracts in every variant; common 20-test regression body. All nine current repetitions and actual current-worktree full execution completed; see the current timing review.
- Current memory router's obsolete bootstrap sentence was corrected. Historical memory, previous Phase 8 and failed evidence remain retained.

## Boundaries
No coverage pruning, hard links, shared writable cache, scheduler, external model session, counterpart product change, private runtime migration, push or management update. Root AGENTS and unrelated CR009 work are excluded.

## Delivery Constraints
Owner opt-out: no deadline and no timebox. Complete semantic/product QA, comparable measurements, current artifact validation and final owner gate remain required.
