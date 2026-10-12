# Project Plan

## Task Contracts

| Task ID | Goal / DoD | Dependencies | Risk | Start / end |
| --- | --- | --- | --- | --- |
| PPO-CORE-001-contract | Flat coordinator, dynamic selection and handoff with unambiguous ownership | owner/context | high | accepted planning -> semantic contract review |
| PPO-CORE-002-run-model | Typed run, graph/resources, reducer and inspection CLI reject unsafe transitions | contract | high | schema agreed -> behavior tests |
| PPO-CORE-003-tool-adapter | Native assignments, tool IDs, termination/result receipt and fallback are executable by current orchestrator | contract/model | high | validated runs -> actual tool trial |
| PPO-CORE-004-integration | Preflight, templates, docs, validator/required artifact wiring coherent | contract/model | high | field contract -> consumer checks |
| PPO-CORE-005-quality | Synthetic sequential/parallel assessment, semantic QA, capture and checkpoint | all outputs | high | integration complete -> Phase 7 evidence |

No user decision remains for these five approved tasks. Counterpart final contract is informational for own functionality, blocking only a claim of installed cross-system interoperability. No separate packaged tasks or recursive autopilots.

## Execution And Write Ownership

First implement shared model/CLI locally. Delegate contract/template documentation and independent behavioral tests on non-overlapping files after Spec QA. Integration scripts and runtime status are coordinator-owned. Available runtime capacity and costs determine actual worker count. During simultaneous work, each executor has explicit file ownership; use forked workspace isolation when provided or read-only delegation when isolation cannot be established.

## Artifact And Product Verification

Planning gates: review architecture for state/resource/authority contradictions, plan for dependency/ownership coverage, each spec for testability. Product: graph cycles, conflicts, dynamic count, flat delegation, stale attempt/baseline, late cancelled result, failing QA, cross-system fallback, preflight behavior, resume and immutability. Full validation once after stable integration. No repeated full gate for capture-only writes unless source changes.

## Plan Quality Contract

- Plan classification: implementation-capable
- DoD source: owner-approved scope and context.md
- Testable DoD / acceptance conditions: dynamic flat delegation with owned resources, safe result reception, integration QA and no unauthorized scope changes.
- Artifact QA route: phase-3-spec-qa (architecture and project plan use their phase-specific QA first)
- Artifact QA trigger: after complete artifact review, before implementation
- Implementation Quality Closure route: phase-5-quality
- Required verification: behavior tests, actual subagent trials, adversarial review, targeted checks and one full product gate
- Quality-ready criteria: complete mappings, executable tests and no in-scope blocker
- Owner opt-out: none
- Not-applicable reason: none
- Blocking decision: none for own functionality; final Workflow interoperability remains external
- Next route: artifact QA, then scoped implementation

## Delivery Constraints

- Mode: owner-opt-out
- Deadline: none
- Time budget: none
- Must-have outcome: all approved orchestration behaviors plus tests, QA, capture and Phase 7
- Quality floor: semantic and product QA, privacy and local gates
- Cutline/deferred scope: no scope reduction; counterpart real interoperability deferred until final contract
- Overrun checkpoint: report material scope conflicts; elapsed time alone is not a blocker

## Model Recommendation

- Recommended: GPT-5.6 Sol High or current equivalent
- Reason: shared orchestration and evidence boundaries
- Criticality: high; explicit owner implementation approval exists
- Current model known: yes, inherited session model
- Blocking: no

