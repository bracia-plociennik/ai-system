# Delivery Constraints

## Intent brief and private style context

Use intent-to-execution-brief.md during existing intake: minimal inline/embedded fields with provenance and disposition; preserve original request/accepted decisions as independent QA anchors. Batch triage and current action/phase ceilings remain first. This adds no phase or approval. Use style-profile.md for optional explicitly enabled local style; recording needs actual exact-target consent and minimal provenance/privacy, observations stay tentative and current instruction overrides profile. Invalid/disabled profile supplies no preferences. Auto chooses only covered reversible options and queues protected owner decisions; Human groups material questions, settled answers not repeated and noninteractive routes stay so.


## Purpose

Delivery Constraints give new implementation work a time boundary without turning schedule pressure into permission to weaken scope safety, Definition of Done, QA, evidence, privacy, approvals, or stop conditions.

This is a planning contract. It does not grant write permission and does not replace task intake, workspace selection, risk routing, owner approval, validation, or work closure.

## Default Rule

Resolve execution mode using `execution-modes.md`. For new Auto work, absent
deadline/timebox records `Mode: auto-unconstrained`, `Deadline: none` and
`Time budget: none`; no compulsory delivery question is asked. The owner outcome,
quality floor and scoped approval are still required. Human retains discovery below.
Existing approved limits remain active; mode switching does not remove them.

Before new implementation work that creates or changes system, project, client, or owned-asset artifacts, discover the material delivery constraint. In Human Mode ask only when deadline or time budget is not already present in the current owner message, accepted plan, or active work artifact.

In Human Mode group missing delivery decisions into at most `1-3` questions. Auto queues material blocking decisions without live questions. Do not ask redundant versions of deadline, duration, and time budget. Read-only analysis, status requests, planning needed to discover constraints, and continuation covered by active constraints do not require a new prompt.

An eligible micro-change may omit a separate deadline/timebox question without treating silence as an owner opt-out. It must be one bounded, reversible local change touching at most three files including tests, with a clear target, approval, and focused verification. It must not change a public API, schema, protocol, policy, routing, approval, privacy, permissions, security, migration, client or production state, external effects, dependencies, or cross-module behavior. Record `Mode: micro-exempt` and the reason in the work response. Honor any deadline or timebox the owner did provide. If the scope grows beyond these limits, stop before further writes, resolve the normal Delivery Constraints, and reclassify the entire work unit.

If the owner gives no deadline or timebox, do not invent one. In Human Mode record `Mode: not-set` and ask the nearest material question before dependent implementation. Auto records `Mode: auto-unconstrained`. An explicit opt-out is scoped to the current work unless the owner says otherwise.

## Delivery Constraints Block

Implementation-capable plans and work artifacts use:

```text
Delivery Constraints
- Mode: <deadline-and-timebox|deadline-only|timebox-only|owner-opt-out|micro-exempt|auto-unconstrained|not-set>
- Deadline: <timestamp|none>
- Timezone: <IANA timezone|none>
- Time budget: <duration|none>
- Must-have outcome: <testable result>
- Should-have scope: <list|none>
- Stretch scope: <list|none>
- Explicitly deferred scope: <list|none>
- Quality floor: <DoD/QA/acceptance boundary>
- Cutline rule: <what is reduced first>
- Overrun checkpoint: <route and owner decision>
- Owner override: <decision or none>
```

## Scope Adaptation

- Protect the must-have outcome and quality floor.
- Remove stretch scope first when the constraint is at risk.
- Defer should-have scope only when it is safe and report the deferred items.
- Do not silently change scope, acceptance criteria, architecture, privacy, risk, permissions, security, billing, migration, production, external effects, or owner approvals.
- Estimates are planning evidence, not guarantees.

Deadline pressure never authorizes skipping QA, DoD, privacy, risk, permissions, evidence, approvals, security checks, or stop conditions.

## Overrun And Opt-Out

When the deadline or timebox is at risk, stop at the overrun checkpoint. Report delivered scope, remaining scope, quality state, and the owner decision required. Do not silently extend the run or reduce the quality floor.

Supported opt-out wording includes `bez deadlinu`, `bez deadline'u`, `bez planowania z deadlinem`, `no deadline`, `without deadline`, `bez timeboxu`, and `no timebox`. Report the opt-out and residual risk in the Execution Trace.

## Routing And Evidence

- `task-intake` discovers supplied constraints and uses mode-aware missing-constraint behavior.
- `command-routing` stops dependent implementation for unresolved required outcomes/gates, not solely for missing Auto time limits.
- `contract-compliance` checks delivered and deferred scope plus quality-floor preservation.
- `response-contract` reports deadline/timebox, overrun state, and scope adaptation when this contract applies.

Quality closure records the agreed constraint, delivered scope, deferred scope, deadline status, quality floor, skipped checks, overrun decisions, and residual risk.

Weekly planning may provide a task-level deadline, time estimate, must-have outcome, and quality floor for work scheduled in the target week. The `.systems/ai/core/weekly-planning.md` contract is the route for that Saturday plan. When a task starts, reuse those fields and apply mode-aware handling of missing delivery constraints. A weekly plan does not authorize implementation outside its explicit TaskNote and owner scope.
