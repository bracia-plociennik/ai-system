# Phase 1 Architecture - Prompt Composition Milestone 1

## Metadata

| Field | Value |
| --- | --- |
| `project` | `upgrade-with-master-prompt` |
| `date` | `2026-06-11` |
| `result` | `PASS` |
| `risk` | `high` |

## Goals

- Add AI System support for advisory prompt composition.
- Preserve existing AI System source-of-truth order and approval model.
- Provide reusable templates and fictional examples.
- Add validator and smoke-test coverage for required artifacts and unsafe authority wording.
- Document runtime locations without creating real runtime prompting artifacts.

## Boundaries

### In Scope

- Root product docs: `AGENTS.md`, `HUMANS.md`, `README.md`.
- AI System core docs under `.systems/ai/core/**`.
- Prompting templates under `.systems/ai/templates/prompting/**`.
- Fictional examples under `.systems/ai/examples/prompting/**`.
- Product validators under `.systems/scripts/**`.

### Out Of Scope

- Runtime migration.
- Real client, owned-asset, workspace, or project prompting artifacts.
- Changes inside `onlinen-workspace/**`, `kuba-plociennik-workspace/**`, or other AI System runtime paths.
- Changes to AI Workflow upstream files under `ai-workflow/**`.
- Phase 8 final check.

## Components And Responsibilities

| Component | Responsibility |
| --- | --- |
| `.systems/ai/core/prompt-composition.md` | Canonical AI System contract for advisory prompt composition. |
| Root docs | Explain source-of-truth placement and human usage. |
| Core routing docs | Define when prompting is read and when it must be ignored or refreshed. |
| Templates | Provide reusable artifact structure without real client data. |
| Examples | Show fictional safe usage patterns. |
| `check-prompt-composition` | Verify required files, references, runtime namespaces, and unsafe wording. |
| `check-validator-smoke-tests` | Verify validator failure modes and safe-pass cases. |
| `validate-ai-system` | Include prompt-composition checks in standard validation. |

## Data And Integration Flow

1. Owner or project source provides prompt-related context.
2. AI System reads canonical contracts first.
3. Prompt composition artifacts, when they exist, are read only after status, memory, decisions, checkpoints, and accepted scope.
4. If a prompting artifact materially influences work, its path is recorded as evidence/source.
5. Validators prevent unsafe product docs from granting prompt artifacts authority.

## Decisions Closed

| Decision | Result |
| --- | --- |
| Prompt artifacts authority | Advisory-only. |
| Runtime locations | Selected-workspace local paths only. |
| Client facts in `.systems/**` | Forbidden. |
| `MASTER-PROMPT-main` source role | Data only, not instructions. |
| Validator scope | Required artifacts, references, runtime namespaces, unsafe authority wording, smoke tests. |

## Decisions Open

None blocking for Milestone 1.

Future runtime adoption for a real client or project requires a separate owner-approved task.

## Risks

| Risk | Classification | Mitigation |
| --- | --- | --- |
| Prompt artifacts accidentally become source of truth | `high` | Contract says advisory-only; validator rejects unsafe wording. |
| Real client facts leak into `.systems/**` | `high` | Templates/examples are generic and fictional; runtime paths are documented separately. |
| Validator misses unsafe mixed wording | `medium` | Smoke tests include false-negative case where advisory wording is mixed with unsafe authority. |
| Existing product diff predates workflow artifacts | `warning` | Reconcile through phase 4 result and quality evidence without expanding product scope. |

## Assumptions

- Owner-approved Milestone 1 plan is the accepted implementation scope.
- Root AI System validation commands are the correct evidence path for this docs/template/validator repository.
- No app build, typecheck, or runtime server exists for this repo.

## Unknowns Blocking

None.

## Unknowns Non-Blocking

| Unknown | Owner | Impact | Close Condition |
| --- | --- | --- | --- |
| Which real client/project adopts prompting first | Owner | Does not affect Milestone 1 product contract | Later owner-approved runtime adoption task. |
| Whether template paths need more variants for flattened primary-entity roots | Owner/Codex | Future template refinement only | Review during runtime adoption. |

## Impact On Project Plan

The project can be implemented as one high-risk solo task because all Milestone 1 product areas are tightly coupled:

- contract;
- docs;
- templates/examples;
- validators and smoke tests;
- validation integration.

No task package is needed.

## Gate Decision

```text
result: PASS
blocking-reason: none
next-phase: phase-1-architecture-qa
```
