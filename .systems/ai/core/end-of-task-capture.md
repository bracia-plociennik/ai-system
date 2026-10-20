# end-of-task-capture.md

## Purpose

`End-of-Task Capture` is the chat-end knowledge capture route for owner prompts that say the current task or conversation is done and useful knowledge should be preserved.

It is not a project-closing phase. It does not replace `contract-compliance`, checkpoint, distillation, final review, final check, commit readiness, owner approvals, privacy checks, evidence, validation, stop conditions, or workspace selection.

Default behavior is capture review/proposal, except for the exact terminal commands `Koniec pracy` and `Koniec zadania`.

Those exact commands mean `capture-now`: the owner has approved durable capture through the correct route when target, scope, selected workspace, privacy, quality, evidence, and write permission are clear.

## Trigger Grammar

Use End-of-Task Capture when the command includes completion/capture intent, such as:

- `Koniec pracy`
- `Koniec zadania`
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

The exact terminal commands `Koniec pracy` and `Koniec zadania` are not acknowledge-only prompts. The response must execute or route the capture decision and must not merely confirm completion or ask what to do next.

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
- Capture mode: <capture-now|proposal-only>
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

For exact `Koniec pracy` or `Koniec zadania`, use `Capture mode: capture-now`. If no valuable knowledge exists, record `Capture targets: none` and a reason. If a required quality, privacy, evidence, workspace, or permission gate is unclear, preserve capture-now intent and route to the missing gate instead of degrading to an acknowledge-only response.

## Routing

End-of-Task Capture complements `.systems/ai/core/contract-compliance.md`; it does not replace the required closure gate.

For exact capture-now commands:

- when implementation quality is complete, perform the applicable owner-scoped memory, status/evidence, distillation, checkpoint, System Insights, or External Memory capture;
- when quality is incomplete, retain capture-now intent and route to quality or fix work first;
- when a Distillation State record is `ready`, route the accepted distillation and update the state only after the distillation artifact exists;
- when nothing durable changed, record `none` instead of creating empty memory.

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
- create commits, pushes, external writes, or TaskNotes automatically;
- use capture-now to write outside the current clear owner scope;
- bypass `contract-compliance`, privacy, workspace selection, risk, permissions, validation, evidence, stop conditions, or owner approvals;
- write raw client data, client names, people names, company names, domains, secrets, credentials, contracts, amounts, production identifiers, repo-specific facts, or project-specific details into `system-insights/`;
- write frontend, backend, SEO, ads, smart-contract, product, or client-work lessons into `external-memory/`.

If scope, target, privacy, evidence, selected workspace, status, or write permission is unclear for ordinary completion wording, stop with proposal-only capture and ask for the missing decision. For exact capture-now commands, retain the capture-now route while stopping on the missing gate.

## Distillation State

End-of-Task Capture may propose or execute the applicable distillation/checkpoint route for an existing state record. Exact capture-now commands may create the scoped distillation and update its state when quality, privacy, evidence, selected workspace, target, and write-permission gates are satisfied. A `completed` state requires the accepted distillation artifact to exist; chat completion wording alone never creates `completed`.

## Response And Trace

Every substantive End-of-Task Capture response must include the `Execution Trace` and `Co dalej?` footer from `.systems/ai/core/response-contract.md`.

The trace should mention:

- whether End-of-Task Capture was the matched route or supporting output;
- whether the mode was `capture-now` or `proposal-only`;
- source scope reviewed;
- durable writes performed or explicitly skipped;
- residual risk.

For new registered task resources apply `task-resource-cleanup.md`: durable QA/Capture stays outside temporary execution; release and eligible cleanup follow actual task closure, with one installed Workflow executor and seven-day whole-worktree retention.

## Sprint iteration

For actual task-local Sprint selection use `sprint-iteration.md` and the compatible installed Workflow. Keep preview/feedback implementation open until genuine final current-effect acceptance or explicit verification request. Deferred quality is not completed/PASS or resource release. Preserve normal behavior without explicit activation.
