# Phase 4 - ASYS-CR-006 Life Alignment Implementation

## Implementation Slice Plan

1. Contract slice: add marker-aware schema fields, validation, normalization, shared counting and red-card gate.
2. Projection slice: expose private alignment fields in V4 indexes without leaking them to public trends.
3. Output slice: add the read-only alignment CLI and Daily/Weekly renderer sections.
4. Task slice: run the gate before Task Vault writes and add threshold/privacy/legacy regressions.
5. Quality slice: run targeted validators, full AI System validation, diff review, commit, push, update-from-upstream, and repeat targeted checks.

## Scope Boundaries

- No historical backfill or rewrite.
- No V3 schema change.
- No runtime workspace writes.
- No public trend, memory, insight, or TaskNote propagation of alignment answers.

## Execution Evidence

- Instruction refresh: performed-targeted before source edits.
- Baseline: upstream `main`, clean worktree, HEAD `5abd884`.
- Knowledge capture: not required; contract, code, tests, and workflow artifacts are durable sources.
