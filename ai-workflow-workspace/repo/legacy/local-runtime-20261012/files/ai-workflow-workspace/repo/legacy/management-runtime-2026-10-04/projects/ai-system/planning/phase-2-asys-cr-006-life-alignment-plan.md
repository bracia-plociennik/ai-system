# Phase 2 Plan QA - ASYS-CR-006

## Package

1. Add additive schema/template fields and marker-aware validation.
2. Add shared calculator and read-only CLI.
3. Add Daily/Weekly renderer projections.
4. Gate TaskNote writes before vault mutation.
5. Add threshold, UNKNOWN, red-card, privacy, and legacy regressions.

## Quality Contract

- DoD: contract, counters, yellow/red cards, resolution, gate, renderer output, and tests.
- Writes planned: upstream source and project-owned workflow artifacts only.
- Artifact QA: direct schema/template/fixture inspection and diff review.
- Post-implementation QA: targeted validators, smoke tests, `validate-ai-system --profile full`, and `git diff --check`.
- Residual risk: automated checks cannot judge the substantive quality of a life-direction change.

## QA Result

`phase-2-plan-qa: accepted`.
