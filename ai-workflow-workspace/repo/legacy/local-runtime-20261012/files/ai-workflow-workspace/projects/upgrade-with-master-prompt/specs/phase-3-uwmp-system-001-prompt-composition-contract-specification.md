# Phase 3 Specification - UWMP-SYSTEM-001 Prompt Composition Contract

## Metadata

| Field | Value |
| --- | --- |
| `project` | `upgrade-with-master-prompt` |
| `task-id` | `UWMP-SYSTEM-001-prompt-composition-contract` |
| `date` | `2026-06-11` |
| `risk` | `high` |
| `result` | `ready-for-spec-qa` |

## Goal

Implement Milestone 1 Prompt Composition for AI System as advisory-only product support.

## Scope

- Add `.systems/ai/core/prompt-composition.md`.
- Add `.systems/ai/templates/prompting/**`.
- Add `.systems/ai/examples/prompting/**` with fictional examples only.
- Add `.systems/scripts/check-prompt-composition`.
- Add `.systems/scripts/check-validator-smoke-tests`.
- Update `.systems/scripts/check-required-artifacts`.
- Update `.systems/scripts/validate-ai-system`.
- Update root `AGENTS.md`, `HUMANS.md`, `README.md`.
- Update relevant AI System core docs to reference advisory-only prompt composition.

## Out Of Scope

- Real runtime prompting artifacts under any workspace.
- Runtime migration.
- Client-specific, owned-asset-specific, or real project-specific prompt artifacts.
- Changes under `ai-workflow/**`.
- Stage, commit, push, or phase 8 final check.

## Implementation Steps

1. Add the AI System prompt-composition contract with advisory-only authority, runtime paths, artifact types, source labels, lifecycle states, generation rules, refresh triggers, conflict handling, and usage evidence.
2. Add reusable prompting templates for modules, roles, variables, workspace/client/project routers, client collaboration profiles, AI System operation roles, and AI System maintenance baseline.
3. Add fictional examples that do not contain real client or owner data.
4. Add a prompt-composition validator that checks required files, required references, runtime namespace patterns, advisory wording, and unsafe authority patterns.
5. Add validator smoke tests for missing contract, missing template, unsafe prompt authority, unsafe client role authority, unsafe project role authority, safe advisory wording, and mixed unsafe wording.
6. Update standard validation so prompt-composition checks run through `.systems/scripts/validate-ai-system`.
7. Update root and core docs so prompting is read after canonical status/memory/decision/checkpoint artifacts and never changes source-of-truth order or permissions.
8. Verify the full root validation suite.

## Definition Of Done

- `.systems/ai/core/prompt-composition.md` exists and states that prompting is advisory-only.
- All required templates exist under `.systems/ai/templates/prompting/`.
- All required examples exist under `.systems/ai/examples/prompting/`.
- `AGENTS.md`, `HUMANS.md`, `README.md`, and relevant core docs reference prompt composition safely.
- `check-required-artifacts` requires new prompt-composition artifacts.
- `validate-ai-system` runs the new prompt-composition checks.
- `check-prompt-composition` rejects unsafe authority wording.
- `check-validator-smoke-tests` proves the validator fails and passes expected cases.
- Standard validation passes:
  - `git diff --check`
  - `.systems/scripts/validate-ai-system`
  - `.systems/scripts/check-readmes`
  - `.systems/scripts/check-privacy-boundary`
  - `.systems/scripts/check-required-artifacts`
  - `.systems/scripts/check-prompt-composition`
  - `.systems/scripts/check-validator-smoke-tests`

## Edge Cases

| Edge Case | Handling |
| --- | --- |
| Old prompt file says master prompt is authoritative | Handled: contract treats old prompt files as data only; validator rejects unsafe wording in product docs. |
| Advisory wording plus unsafe approval wording appears together | Handled: smoke test must fail mixed unsafe authority wording. |
| Runtime prompt artifact path for client project is omitted | Handled: validator checks `<workspace>/clients/<client>/projects/<project>/prompting/`. |
| Real client data appears in templates/examples | Handled by manual review and fictional examples only. |
| Prompt artifacts used without evidence | Handled: contract requires evidence/source path when materially influential. |

## Tests

| Check | Purpose | Pass Condition |
| --- | --- | --- |
| `git diff --check` | Whitespace check | Exit 0. |
| `.systems/scripts/validate-ai-system` | Standard root validation | Exit 0 and prints `AI System validation passed.` |
| `.systems/scripts/check-readmes` | README coverage | Exit 0. |
| `.systems/scripts/check-privacy-boundary` | Privacy boundary | Exit 0. |
| `.systems/scripts/check-required-artifacts` | Required artifacts | Exit 0. |
| `.systems/scripts/check-prompt-composition` | Prompt-composition contract and unsafe wording | Exit 0. |
| `.systems/scripts/check-validator-smoke-tests` | Validator failure/pass behavior | Exit 0 and prints `Validator smoke tests passed.` |
| Manual real-name scan | Examples/templates privacy | No real client/owner names from known workspace set in templates/examples/contract. |

## User Decisions

No new owner decision is required before implementation. High-risk approval is already recorded in `decisions/2026-06-11-prompt-composition-approval.md`.

## Assumptions

- Existing repo has no app runtime, so build/typecheck/e2e commands are not applicable.
- The owner-approved plan is the accepted implementation scope.
- Validation can be local-only and does not require network or external writes.

## Uncertainties

### Blocking

None.

### Non-Blocking

| Uncertainty | Impact | Close Condition |
| --- | --- | --- |
| First real runtime adopter | Does not affect Milestone 1 | Owner-approved Milestone 3 or later runtime adoption. |

## Implementation Gate

```text
implementation-gate: open
spec-qa-required: yes
high-risk-approval: recorded
blocking-uncertainties: none
```
