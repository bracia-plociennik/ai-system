# Phase 2 Project Plan - Prompt Composition Milestone 1

## Metadata

| Field | Value |
| --- | --- |
| `project` | `upgrade-with-master-prompt` |
| `date` | `2026-06-11` |
| `result` | `PASS` |
| `architecture` | `architecture/phase-1-architecture.md` |
| `architecture-qa` | `quality/phase-1-architecture-qa.md` |

## Planning Summary

Milestone 1 is one tightly coupled product task. Splitting contract, docs, templates, examples, validators, and validation integration would increase risk because the validator must verify the final docs/templates together.

## Lista kolejnosci wykonywania

1. ✅ `UWMP-SYSTEM-001-prompt-composition-contract` - implement the advisory prompt composition product contract, templates, examples, validators, docs references, validation integration, quality evidence, distillation, and checkpoint.

## Task Contract

### `UWMP-SYSTEM-001-prompt-composition-contract`

| Field | Value |
| --- | --- |
| Title | Milestone 1 Prompt Composition product contract |
| Goal | Add advisory-only prompt composition support to AI System without changing source-of-truth order or creating real runtime artifacts. |
| Scope | Root docs, `.systems/ai/core/**` references, `.systems/ai/templates/prompting/**`, `.systems/ai/examples/prompting/**`, `.systems/scripts/check-prompt-composition`, `.systems/scripts/check-validator-smoke-tests`, `check-required-artifacts`, and `validate-ai-system`. |
| Out-of-scope | Runtime migration, real client/project prompting artifacts, product behavior outside docs/templates/validators, stage/commit/push, phase 8. |
| Definition of Done | Contract exists; templates exist; fictional examples exist; root/core docs reference advisory-only prompting; validators reject unsafe authority wording; smoke tests cover missing files, unsafe wording, and safe advisory wording; standard validation passes. |
| Dependencies | Owner-approved Milestone 1 plan; phase-1 architecture PASS; high-risk approval decision recorded. |
| Risk | `high` |
| Main risk | Prompt artifacts could accidentally gain authority over system rules, writes, risk, evidence, or approvals. |
| Start condition | Spec QA PASS and high-risk approval recorded. |
| End condition | Quality PASS, distillation written, checkpoint written, phase 8 not run. |
| Readiness | `ready` |
| User decision required before implementation | `no`, approval already recorded in `decisions/2026-06-11-prompt-composition-approval.md`. |

## Dependency Map

| Dependency | Type | Status | Notes |
| --- | --- | --- | --- |
| Owner-approved Milestone 1 plan | `blocking` | `satisfied` | Explicit owner approval exists. |
| Architecture QA PASS | `blocking` | `satisfied` | `quality/phase-1-architecture-qa.md`. |
| High-risk approval | `blocking` | `satisfied` | Decision artifact recorded. |
| Repo command map | `blocking` | `satisfied` | Project intake records safe validation commands. |

## Tasks package

No packages created.

| Package ID | Scope | Tasks | Status |
| --- | --- | --- | --- |
| n/a | n/a | n/a | n/a |

Tasks not packaged:

- `UWMP-SYSTEM-001-prompt-composition-contract`

Conflicts found:

- none

Packaging rationale:

- The project has one solo execution block.
- There are no independent tasks to package.
- Phase 2.9 packaging QA is skipped because no packages exist.

## Parallel Work

Parallel execution is not recommended. This project has one product task and a shared validator/docs write set.

## Gate Decision

```text
result: PASS
blocking-reason: none
next-phase: phase-2-plan-qa
```
