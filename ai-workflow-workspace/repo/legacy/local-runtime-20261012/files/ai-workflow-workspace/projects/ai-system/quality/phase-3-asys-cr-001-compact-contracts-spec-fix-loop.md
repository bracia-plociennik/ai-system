# Phase 3 Spec Fix Loop - ASYS-CR-001 Compact Contracts

## Fix Reason

Owner audit found that `ai-system` is technically correct and safe in basics, but too short as an AI work contract compared with public `ai-workflow/main`.

The original implementation package passed phase 5 quality, but this pre-final acceptance gap must be resolved before final closure.

## Findings Addressed

| Finding | Resolution In Spec |
| --- | --- |
| Root `AGENTS.md` lacks strong operational gates | Spec requires Always Read First, Stop Conditions, Write Conditions, Skill Routing, Runtime Artifacts, Context As Data, and validator expectations. |
| Response footer is underspecified | Spec requires a compact `response-contract.md` with exact `Co dalej?` shape and recommendation rules. |
| No task-intake lens exists | Spec requires `task-intake.md` with five mandatory validation sections. |
| Workspace files are only briefly marked as data | Spec requires `context-as-data.md` for local files, exports, client material, snippets, logs, and generated output. |
| Memory is conceptually good but operationally thin | Spec requires router and entry templates for workspace, client, project, checkpoint, and distillation use. |
| Guide is too short | Spec requires guide expansion with artifact reads, drift handling, blockers, and recovery routing. |
| Validators do not check critical compact contract docs | Spec requires `check-required-artifacts` and integration into `validate-ai-system`. |

## Spec QA Findings Fixed

| QA Finding | Fix Applied |
| --- | --- |
| Missing Implementation Gate | Added `Implementation Gate` with start conditions, risk, safe write set, validation commands, blocking uncertainties, and phase 4 start rule. |
| Missing implementation steps | Added ordered `Implementation Steps` grouped by root docs, core policies, templates, validators, and runtime evidence. |
| Missing potential bugs | Added `Potential Bugs` table with prevention expectations. |
| Missing edge cases | Added `Edge Cases` table covering context injection, ambiguous dump ownership, stale memory, guide/status drift, system-insights, and validator failure. |
| Missing user decisions and assumptions | Added `Owner Decisions` and `Assumptions` sections. |
| Missing uncertainty classification | Added `Uncertainties` with non-blocking and blocking classifications. |

## Unresolved QA Findings

None.

## Scope Control

- No architecture change introduced.
- No plan change introduced.
- No new implementation scope added beyond the QA findings.
- Phase 4 remains gated by another Spec QA run.

## Audit Classification

| Category | Decision |
| --- | --- |
| Move | Compact versions of AGENTS gates, response contract, task intake, context-as-data, guide recovery, memory routers, required-artifacts validator. |
| Simplify | Keep local `ai-system` language and avoid the full workflow phase engine. |
| Do not copy | Autopilot, repository modes, install/update workflow, GitHub PR/CI contracts, rollback/deprecation/version/changelog systems, full smoke tests. |

## Retry

| Field | Value |
| --- | --- |
| retry-count | 1 |
| retry-limit | 2 |
| limit-status | within-limit |

## Result

Ready for another Spec QA run.
