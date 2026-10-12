# Smoke Setup Optimization Review

## Scope And Intent
IEV2-CR-001 addresses P2-PERF-001 by reducing fixture setup processes, not by skipping tests. The accepted no-deadline/no-timebox delivery constraint and complete quality floor remain active. Publication, management rollout, counterpart code, client work and unrelated CR009 state are excluded.

## Findings-First Semantic Review
- Correctness blockers identified in the changed setup: none in the reviewed paths.
- Performance blocker: resolved by the current common-20-test frozen matrix; technical Phase 8 still requires current artifact/capture review.
- Runtime router finding: memory.md still contained the bootstrap sentence "No completed implementation claims yet" despite completed implementation/capture. Corrected the current router to distinguish completed implementation from reopened technical closure; historical memory/capture entries were not rewritten.
- Copy inventory remains Git-tracked `.systems`, `.github`, root README/HUMANS and `.gitignore`, plus explicit safe extra product files.
- The Python helper preflights the full inventory before any copy. Missing files, direct symlinks, escaping parents, traversal, foreign extras, sensitive extras and unsafe/nonempty destinations fail.
- Each domain gets physical independent copies. No hard links, shared mutable transaction state or cache reuse was added. After the first benchmark falsified the copy-only hypothesis, bounded two-domain scheduling was added for a fresh benchmark.
- Content, executable modes and timestamps are preserved. Runtime files remain outside the fixture inventory.
- The shell retains domain dispatch, cleanup trap, exact negative rejection assertions, all mutation/restore bodies and final completeness assertions. The all-suite coordinator runs pairs, drains both started peers, propagates failure and starts no later pair after a failure. Captured output is emitted in domain order; completion is emitted only after seven successful domains.
- The producer change is consumed by the shell helper call, required-artifact registry, profile checks, synthetic tests and smoke documentation.
- The profile validator accepts both the previously validated tracked-product Bash copier and the optimized helper. This permits honest frozen baseline evaluation without requiring a candidate-only implementation detail in the baseline; arbitrary untracked copying remains forbidden.

## Failure Paths And Residual Risk
Synthetic tests exercise copy independence, modes/timestamps, excluded runtime files, all-source preflight, missing/linked/escaping/traversal/foreign/sensitive sources and unsafe destinations. An OS write failure is not reported as success; the harness trap removes its temporary transaction. Concurrent mutation of source during copying is outside the single-writer fixture contract, and full runner source fingerprints detect source drift during a run. No stronger claim about arbitrary hostile concurrent filesystem changes is made.

## Coverage Equivalence
The first frozen matrix asserts equality of all seven suite-body hashes, all 220 exact negative contracts and all 18 integrity behavior test identities/body bytes. The next matrix includes the additional bounded-scheduling tests identically in every variant. Old assertion bodies remain unchanged. Only fixture setup/isolation and bounded scheduling differ; no assertion or restoration is removed.

## Verification
- Copy-only helper/integrity tests: 18 tests completed successfully, `/private/tmp/integrity-smoke-optimization-tests-02.log`.
- Current bounded-scheduling behavior: 20 tests completed successfully, `/private/tmp/integrity-smoke-optimization-tests-03.log`. Seven distinct roots/PIDs, at most two active transactions, peer drain and later-write prevention were exercised.
- Cross-domain write audit: harness paths are domain-local temporary roots; no global Git config writes, shared writable cache, process-wide kill commands or private-home writes were found in the domain bodies. Explicit workspace overrides point to each domain's fixtures.
- Full-run interruption remains owned by validation_runner's process-group boundary, already covered by the retained timeout/interruption behavior tests; the coordinator does not create detached sessions or an external scheduler.
- `check-validation-profiles`: completed successfully after semantic review.
- `git diff --check`: completed successfully before frozen comparison.
- The first nine full-profile repetitions completed but did not clear the performance warning. The fresh common-20-test nine-run matrix and actual current-worktree full execution completed successfully. Current project-scoped QA/status, capture and handoff checks passed after the documented formatting recovery. Workflow full-02 completed with exit 0, all smoke groups and a unique completion marker.
- Scripts are supporting-only; this review evaluates intent, producer-consumer behavior, failure paths and scope independently.

## Ownership And Privacy
Only the isolated worktree product and its owning project evidence are changed. Root AGENTS shim, nested Workflow source, management checkout and the original checkout's unrelated CR009 edits remain outside the write set. Synthetic fixtures contain product files only and do not use external model sessions or private runtime data.

## Model Recommendation
- Recommended: GPT-5.6 Sol High
- Reason: shared validation integrity, adversarial paths and comparative evidence
- Criticality: high
- Current model known: no
- Blocking: no

## Current Performance And Product QA
The measured setup meets the performance DoD; see smoke-optimization-timing-review.md for means, spread, population and limitations. Actual current-worktree full execution completed with all 33 checks and all seven smoke domains, with the same current product-file/source and coverage digests as the optimized frozen records. Fixture HEADs differ and are recorded, not equated with the real assessed HEAD. Semantic review found no unresolved correctness, coverage or ownership defect in the changed scope. Final acceptance is not inferred from script success.

## Final Artifact And Ownership Review
Current QA metadata is re-bound only after this renewed review. Earlier QA bytes and the pending Phase 8 assessment are retained in pre-workflow-completion-qa.json; rejected formatting/invocation records remain in smoke-artifact-recovery.md and its evidence. Product sources, root AGENTS shim, nested Workflow source and the original checkout's unrelated CR009 boundary were rechecked. Management remains clean. No known in-scope system warning remains; local timing noise, excluded private pilot and future agent behavior remain residual risks, not hidden acceptance evidence.
