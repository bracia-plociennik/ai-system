# Contract Compliance

## Purpose

This policy defines the advisory work-mode compliance check and Knowledge Capture Gate for AI System.

It exists to make knowledge capture explicit before work closure without creating a mechanical requirement to write memory, distillation, or checkpoint artifacts for every task.

## Advisory Only

This gate is advisory-only. It does not replace `AGENTS.md`, privacy rules, workspace selection, owner-approved write gates, validation, required evidence, stop conditions, or final owner acceptance.

Select script evidence through `.systems/ai/core/validation-routing.md` and `.systems/ai/core/validation-profiles.md`. Semantic QA, findings-first review, product checks, and failure-path analysis come first. Scripts are supporting-only and green output does not independently create PASS.

The gate requires a decision. It does not grant permission to write. Durable writes still require the correct target, privacy-safe content, and explicit owner-approved scope unless a stricter checkpoint or final-check route already authorizes that exact capture.

End-of-Task Capture from `.systems/ai/core/end-of-task-capture.md` can precede work closure when the owner says the task is done and asks to preserve learnings. Exact `Koniec pracy` and `Koniec zadania` mean `capture-now`; other completion wording is capture review/proposal by default. It does not replace this compliance gate or permit skipped evidence, privacy, quality, risk, memory boundaries, or approvals.

## AI_SYSTEM_WORK_CLOSURE

Apply this gate before `AI_SYSTEM_WORK_CLOSURE`.

`AI_SYSTEM_WORK_CLOSURE` means any point that closes or hands off a meaningful unit of work:

- final substantive response that closes a task, review, implementation, validation, or recovery action;
- handoff to another agent, thread, session, or owner;
- accepted change, checkpoint-ready state, commit-ready state, or push-ready state;
- switching from one work unit to another unrelated work unit;
- ending a session after decisions, status, evidence, files, or memory-relevant context changed.

Do not use this gate as a reason to keep writing indefinitely. If no durable knowledge changed, record `Knowledge capture: not-required` with a short reason.

## Work Mode Compliance

Before work closure, classify the work mode:

| Work mode | Use when | Default evidence and capture boundary |
| --- | --- | --- |
| `project` | Work belongs to a selected workspace project, client project, or owned-asset project. | Project-state status/evidence, project-memory, distillation, checkpoint when needed. |
| `micro-task` | Small low-risk work inside a workspace or project that does not require a full project flow. | Final response evidence, status/evidence if state changed, durable memory only when owner-approved. |
| `micro-project` | Small local work item tracked under `<workspace>/micro-projects/`. | `status/evidence` recorded in the micro-project artifact; promote if scope or risk grows. |
| `side-task` | One-off read-only, validation, orientation, or narrow local task with no durable project record. | Final response evidence unless the owner requested durable capture. |
| `system-maintenance` | AI System product docs, templates, validators, scripts, root contract template, or update/validation behavior. | In `ai-system-dev`, validator evidence and product docs; in management checkouts, STOP and route upstream. |
| `client-work` | Client collaboration, offer, communication, relationship, process, or delivery-quality work. | client-memory for client-specific facts, project-memory for project facts, system-insights for anonymized reusable lessons. |

The selected mode must match risk, scope, approvals, write set, workspace selection, and available evidence. If it does not fit, stop or route to the safer workflow before closure.

## Required Decision Block

Before `AI_SYSTEM_WORK_CLOSURE`, the response, handoff, checkpoint, distillation, review note, or status/evidence artifact must be able to state:

```text
Contract compliance:
- Work mode: <project|micro-task|micro-project|side-task|system-maintenance|client-work>
- Work mode compliance: <pass|warning|blocked>
- Knowledge capture: <required|not-required>
- Capture target: <status/evidence|workspace-memory|primary-entity-memory|client-memory|owned-asset-memory|project-memory|distillation|checkpoint|external-memory|system-insights|not-applicable>
- Reason: <short reason>
```

If `Work mode compliance` is `blocked`, stop before claiming closure unless the current action is only recording the blocker or asking for the missing owner decision.

For a substantive AI System or AI Workflow upgrade before commit or handoff, also state:

```text
Cross-system impact:
- Owner decision: <yes|no|pending>
- Counterpart: <ai-workflow|ai-system|none>
- Handoff artifact: <path|not-required|pending>
- Reason:
```

If the decision is `pending`, stop before commit or handoff. If it is `yes`, stop unless the privacy-safe handoff exists. If it is `no`, require `Counterpart: none`, `Handoff artifact: not-required`, and a reason.

## Knowledge Capture Decision

Knowledge capture is `required` when the work produced durable knowledge or changed the state needed for safe continuation.

Capture is required when any of these are true:

- project, client, owned-asset, workspace, or primary-entity status changed;
- evidence, acceptance state, blocker state, validation result, or next safe action changed;
- a decision, constraint, preference, workaround, residual risk, rollback note, or future blocker changed;
- client communication preferences, offer rules, collaboration process, relationship context, or delivery expectations changed;
- project facts, implementation notes, risks, dependencies, or lessons changed;
- a completed stage, large memory set, or raw notes should be compressed into a distillation;
- a major decision, long pause, stale state, substantial triage, or final closure needs a checkpoint;
- an anonymized reusable lesson should become a System Insight candidate;
- an AI System product or process improvement proposal belongs in External Memory.

Knowledge capture is normally `not-required` when:

- the work was read-only orientation and no status, decision, evidence, or reusable lesson changed;
- validation was rerun and the result is already reported with no durable state change;
- the change was typo-only or formatting-only and produced no operational lesson;
- the current artifact already captured the same fact and no status changed;
- the final response is sufficient non-durable evidence for a side-task.

## Capture Targets

Use the narrowest correct target:

| Capture target | Use when |
| --- | --- |
| `status/evidence` | Status, validation, acceptance, blocker, or proof changed but no durable memory fact is needed. |
| `workspace-memory` | Broad workspace preference, recurring pattern, or workspace-level decision changed. |
| `primary-entity-memory` | Raw facts, decisions, constraints, or reusable context changed for a primary-entity workspace root. |
| `client-memory` | Client-specific facts, preferences, communication rules, offer history, relationship context, or process changed. |
| `owned-asset-memory` | Owner-controlled asset facts, decisions, constraints, brand/business context, or asset-specific lessons changed. |
| `project-memory` | Project-specific facts, decisions, implementation notes, risks, or lessons changed. |
| `distillation` | A completed stage or large memory set needs compression and stale-context separation. |
| `checkpoint` | A safe-resume state is needed after major decisions, long pauses, stale state, substantial triage, or final closure. |
| `external-memory` | The lesson is an AI System improvement proposal, not a client/project/domain lesson. |
| `system-insights` | The lesson is anonymized, reusable across future work, and suitable for skill or quality improvement. |
| `not-applicable` | No durable capture is needed or the fact is already captured in the correct artifact. |

Do not store client names, people names, domains, secrets, contract details, amounts, production identifiers, or repo/project-specific facts in `system-insights/`. Do not store product-domain lessons in `external-memory/`.

## Delivery And Distillation Compliance

For implementation-class work, closure must compare delivered and deferred scope with the active Delivery Constraints and confirm that deadline pressure did not weaken DoD, QA, privacy, risk, permissions, evidence, or approvals.

Closure must also report the scoped Distillation State record and its derived `is_distilled` value. Quality closure moves `pending-quality` to `ready` or justified `not-applicable`; `completed` requires a linked accepted distillation. An unresolved state is visible evidence, not automatic permission to write capture or a reason to claim closure without required quality evidence.

## Mode-Specific Defaults

| Work mode | Default capture target |
| --- | --- |
| `project` | `status/evidence`, `project-memory`, `distillation`, or `checkpoint` depending on what changed. |
| `micro-task` | `status/evidence` or `not-applicable`; memory only when a durable fact changed and write scope is approved. |
| `micro-project` | `status/evidence` recorded in the micro-project artifact; promote if risk or scope grows. |
| `side-task` | `not-applicable` or final response evidence unless the owner requested durable capture. |
| `system-maintenance` | validator evidence, docs evidence, `external-memory` for AI System improvement proposals, `system-insights` for anonymized operating lessons. |
| `client-work` | `client-memory` for client facts, `project-memory` for project facts, `system-insights` for anonymized reusable lessons. |

This gate does not allow writing the wrong memory type. If the correct target is ambiguous, stop and ask the owner to choose the target.

For project work, resolve the concrete project-state path through `.systems/ai/core/project-state.md` before durable capture. Do not write AI System runtime state into a project git worktree unless the owner explicitly chooses colocated local-only state.

End-of-Task Capture may help decide this target at closure, but it must not duplicate an existing checkpoint, distillation, or Knowledge Capture Gate decision.
