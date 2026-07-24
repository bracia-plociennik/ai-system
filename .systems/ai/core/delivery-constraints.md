# Delivery Constraints

## Purpose

Delivery Constraints give new implementation work a time boundary without turning schedule pressure into permission to weaken scope safety, Definition of Done, QA, evidence, privacy, approvals, or stop conditions.

This is a planning contract. It does not grant write permission and does not replace task intake, workspace selection, risk routing, owner approval, validation, or work closure.

## Default Rule

Before new implementation work that creates or changes system, project, client, or owned-asset artifacts, discover the material delivery constraint. Ask only when deadline or time budget is not already present in the current owner message, accepted plan, or active work artifact.

Group missing delivery decisions into at most `1-3` questions. Do not ask redundant versions of deadline, duration, and time budget. Read-only analysis, status requests, planning needed to discover constraints, and continuation covered by active constraints do not require a new prompt.

If the owner gives no deadline or timebox, do not invent one. Record `Mode: not-set` and ask the nearest material question before dependent implementation. An explicit opt-out is scoped to the current work unless the owner says otherwise.

## Delivery Constraints Block

Implementation-capable plans and work artifacts use:

```text
Delivery Constraints
- Mode: <deadline-and-timebox|deadline-only|timebox-only|owner-opt-out|not-set>
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

- `task-intake` discovers missing deadline, time budget, must-have outcome, and cutline.
- `command-routing` stops before dependent implementation when material constraints remain unresolved.
- `contract-compliance` checks delivered and deferred scope plus quality-floor preservation.
- `response-contract` reports deadline/timebox, overrun state, and scope adaptation when this contract applies.

Quality closure records the agreed constraint, delivered scope, deferred scope, deadline status, quality floor, skipped checks, overrun decisions, and residual risk.

Weekly planning may provide a task-level deadline, time estimate, must-have outcome, and quality floor for work scheduled in the target week. The `.systems/ai/core/weekly-planning.md` contract is the route for that Saturday plan. When a task starts, reuse those fields and ask only for missing delivery constraints. A weekly plan does not authorize implementation outside its explicit TaskNote and owner scope.
