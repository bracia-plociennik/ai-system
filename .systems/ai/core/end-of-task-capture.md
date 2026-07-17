# end-of-task-capture.md

## Purpose

`End-of-Task Capture` is the chat-end knowledge capture route for owner prompts that say the current task or conversation is done and useful knowledge should be preserved.

It is not a project-closing phase. It does not replace `contract-compliance`, checkpoint, distillation, final review, final check, commit readiness, owner approvals, privacy checks, evidence, validation, stop conditions, or workspace selection.

Default behavior is capture review/proposal. Durable writes are allowed only when the owner explicitly requests capture and the target, scope, privacy/scope check, evidence, workspace, and write permission are clear.

## Trigger Grammar

Use End-of-Task Capture when the command includes completion/capture intent, such as:

- `to koniec zadania`
- `koniec taska`
- `kończymy ten task`
- `zamykamy ten task`
- `dziękuję, utrwal wiedzę`
- `utrwal wiedzę z tej rozmowy`
- `zrób końcowe utrwalenie wiedzy`
- `end task and capture knowledge`
- `done, capture learnings`
- `finish this task and preserve learnings`

Do not route generic review, checkpoint, distillation, final check, commit-readiness, or contract-compliance prompts here unless they also include completion/capture intent and no higher-precedence route applies.

## Precedence Rules

Apply this order before End-of-Task Capture:

1. Explicit owner-approved write instructions and change requests.
2. Explicit formal procedures: distillation, checkpoint, final check, and named validation or sync commands.
3. `final review`, `code review`, `find blockers`, and `find findings` as review routes.
4. Commit readiness, push readiness, contract compliance, and Knowledge Capture Gate through `.systems/ai/core/contract-compliance.md`.
5. End-of-Task Capture.

Existing commands stay unchanged:

- `Zrób distillation` routes to distillation, not End-of-Task Capture.
- `Zrób checkpoint` routes to checkpoint, not End-of-Task Capture.
- `Zrób final check` routes to final check, not End-of-Task Capture.
- `Zrób final review` routes to final review, not final check.

If a command contains both completion wording and explicit procedure wording, route by the explicit procedure first and include End-of-Task Capture as supporting output only when useful.

## Required Output

When a scoped Distillation State record exists, include its state, derived `is_distilled` value, source artifacts, quality evidence, owner disposition, and recommended next route. Chat completion wording alone cannot set `completed`.

Use this output block when the matched route is End-of-Task Capture or when a higher-precedence route includes it as supporting output:

```text
End-of-Task Capture

- Trigger detected:
- Matched route:
- Precedence check:
- Work mode:
- Source scope reviewed:
- Completion state:
- Capture targets:
- Writes allowed:
- Owner approval:
- Privacy/scope check:
- Distillation needed:
- Checkpoint needed:
- Memory/status updates:
- System Insight candidates:
- External Memory candidates:
- Skipped capture:
- Residual risk:
```

## Capture Targets

Allowed targets are:

- `status/evidence`
- `workspace-memory`
- `primary-entity-memory`
- `client-memory`
- `owned-asset-memory`
- `project-memory`
- `distillation`
- `checkpoint`
- `system-insights`
- `external-memory`
- `proposal-only`
- `none`

Use `proposal-only` when the owner signaled completion but did not approve durable capture, or when target, scope, privacy, status, evidence, selected workspace, or write permission is unclear.

Use `none` only when nothing useful changed or all relevant knowledge is already captured in the correct artifact.

## Routing

End-of-Task Capture complements `.systems/ai/core/contract-compliance.md`; it does not replace the required closure gate.

Use target-specific policy:

- `status/evidence` for source-backed state, validation, blocker, acceptance, or next-safe-action changes.
- `workspace-memory`, `primary-entity-memory`, `client-memory`, `owned-asset-memory`, or `project-memory` for local durable facts and decisions at the narrowest correct owner scope.
- `distillation` for compressed summaries of completed stages, large notes, or stale context.
- `checkpoint` for safe-resume state after major decisions, long pauses, substantial triage, stale state, or final closure.
- `system-insights` only for anonymized reusable operating lessons and skill candidates.
- `external-memory` only for AI System product/process improvement proposals.

Do not write AI System runtime state into a project git worktree. For project work, use `.systems/ai/core/project-state.md` and route to the selected workspace `project-state/` namespace unless the owner explicitly approves colocated local-only state.

## Safety Boundaries

End-of-Task Capture must not:

- mark `PASS` automatically;
- run final check automatically;
- close a project without explicit owner approval;
- update status from chat-only claims;
- create commits, pushes, external writes, TaskNotes, memory, checkpoints, distillations, System Insights, or External Memory automatically;
- bypass `contract-compliance`, privacy, workspace selection, risk, permissions, validation, evidence, stop conditions, or owner approvals;
- write raw client data, client names, people names, company names, domains, secrets, credentials, contracts, amounts, production identifiers, repo-specific facts, or project-specific details into `system-insights/`;
- write frontend, backend, SEO, ads, smart-contract, product, or client-work lessons into `external-memory/`.

If scope, target, privacy, evidence, selected workspace, status, or write permission is unclear, stop with proposal-only capture and ask for the missing decision.

## Distillation State

End-of-Task Capture may propose a transition or a formal distillation/checkpoint route for an existing state record. It does not create distillation or change the state automatically. A `completed` state requires the accepted distillation artifact and normal capture permissions.

## Response And Trace

Every substantive End-of-Task Capture response must include the `Execution Trace` and `Co dalej?` footer from `.systems/ai/core/response-contract.md`.

The trace should mention:

- whether End-of-Task Capture was the matched route or supporting output;
- source scope reviewed;
- durable writes performed or explicitly skipped;
- residual risk.
