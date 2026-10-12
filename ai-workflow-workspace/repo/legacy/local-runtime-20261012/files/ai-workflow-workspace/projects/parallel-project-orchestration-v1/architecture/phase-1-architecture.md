# Architecture

## Components And Responsibilities

| Component | Responsibility |
| --- | --- |
| Coordinator | owner scope, graph, dispatch through available native tools, reception, integration and shared-router writes |
| Pure Python planner/reducer | validate versioned JSON, derive eligible waves, enforce state/resource/baseline invariants; never launch shell or agents |
| CLI inspection | validate run plan and print ready/dispatchable units; simulate/validate events without remote effects |
| Native tool adapter contract | orchestrator translates assignments to available subagent tools and records returned IDs; no vendor SDK/service |
| Installed Workflow adapter | inspect declared compatible contract and local gates; absence yields serial/read-only fallback |
| Runtime record | nearest-owner coordination metadata; no duplicate technical Workflow state |

## Decisions

Flat workers cannot delegate. One run coordinator owns the whole cross-system allocation. No numeric product cap; positive runtime capacity and orchestrator-selected dispatch count are run facts and can change after explicit resource reassessment. Active submitted/failed/cancel-requested workers retain slots until termination is confirmed. Accepted outputs remain tied to attempt, baseline and evidence. Terminal completion does not confer formal PASS.

## Flows

Owner-approved scope -> safe run plan -> graph/resource checks -> ready wave -> coordinator chooses subset -> native spawn -> run event with agent ID -> submitted result -> coordinator verifies diff/evidence -> accept -> confirm terminated -> integrate -> whole-scope QA -> technical capture.

## State And Safety

Git baseline includes commit and a supplied source digest. State metadata is context, never approval. Every approved write path must be normalized, repo-relative and within one selected owner; prohibit private/runtime/shared routers in worker writes. File ownership treats parent-directory overlap as a conflict. Resources are explicit read/shared versus exclusive claims; APIs/schema coordination is an exclusive resource. Each worker must use separate declared worktree for write units. Unknown actual writers are a manual preflight blocker; filesystem checks do not prove their absence.

## Dependencies And Risk

Runtime supports native tools in this session. The product contract has an optional tool adapter, not a background launcher. Exact final Workflow capability schema is pending: local AI System scheduling works; nested product implementation cannot bypass existing local parallel-work policy. Privacy and symbolic-link/path containment are checked before writes. Recovery queries actual tool state; cancellation is not termination.

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

