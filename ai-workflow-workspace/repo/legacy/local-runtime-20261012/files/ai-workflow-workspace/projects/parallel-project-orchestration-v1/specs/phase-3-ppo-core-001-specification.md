# Task Specification PPO-CORE-001

## Metadata

- Project: parallel-project-orchestration-v1
- Task/package ID: PPO-CORE-001-contract
- Readiness: ready after Spec QA

## Implementation Plan And DoD

Contract: dynamic dispatch based on ready graph/runtime/resource/rework and checkpoint boundary; a worker never creates another worker; one coordinator controls both systems. Preserve local authority and semantic QA. Documentation agent may modify core/project-orchestration.md, templates/orchestration-record and a new parallel-run JSON template only.

## Error And Regression Verification

Missing fields, duplicate identity, cycles, unsafe paths, cross-unit ownership, stale baseline/attempt, unknown writer, cancelled/failed tool result, capacity overflow and missing isolation must be surfaced rather than guessed. Existing orchestration preflight behavior is preserved without optional inputs. Runtime records never grant approval. Fixtures are synthetic. The task completes only after its evidence is reviewed and no material blocker remains.

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

