# ASYS-POPS-015 - Life Alignment Cards dla SPOR V4

## Status

- Status: implementation
- Change request: `ASYS-CR-006-life-alignment-cards`
- Owner approval: `owner-approved` in the task request
- Cross-system impact: no

## Definition Of Done

- Daily and Weekly V4 accept the additive alignment contract without a schema-version bump.
- Daily and Weekly renderers show the question, normalized answer, counters, card, and resolution state.
- Daily/Weekly thresholds and UNKNOWN exclusion are covered by regression tests.
- An unresolved red card blocks TaskNote writes before Task Vault mutation.
- Valid plan-change and owner-override resolutions reopen writes; invalid resolutions are rejected.
- Redacted projections remove answer and resolution data.
- Existing V3/V4 artifacts remain valid and unchanged.

## Artifact QA

Phase 1 architecture, phase 2 plan, phase 3 specification, then phase 5 quality closure. Implementation artifacts are kept in the project-local workflow workspace.
