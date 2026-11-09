> Compatible new implementation tasks use `default-sprint.md` V2: bounded targeted QA after acceptance and incremental phases5–7; explicit full verification/Phase8 remains separate. This scoped rule takes precedence over ordinary implementation/checkpoint chaining below. V1 and unsupported tasks retain installed rules. `Phase X` / `-all` follows `phase-x-maintenance.md`; manual only, never autopilot/Dreaming.

# end-of-task-capture.md

## Purpose

`End-of-Task Capture` is the chat-end knowledge capture route for owner prompts that say the current task or conversation is done and useful knowledge should be preserved.

It is not a project-closing phase. It does not replace `contract-compliance`, checkpoint, distillation, final review, final check, commit readiness, owner approvals, privacy checks, evidence, validation, stop conditions, or workspace selection.

Direct completion/capture intent uses the aliases and interval rules in Incremental whole-chat coverage below. Clear current end-session write requests select capture-now. Completion wording without clear capture authority remains proposal-only. Explicit read-only restrictions select read-only output.

Those exact commands mean `capture-now`: the owner has approved durable capture through the correct route when target, scope, selected workspace, privacy, quality, evidence, and write permission are clear.

## Trigger Grammar

Use End-of-Task Capture when the command includes completion/capture intent, such as:

- `Zdestyluj i zapisz`
- `Zdestyluj i zapisz wiedzę`
- `Koniec`
- `Kończymy`
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

## Incremental whole-chat coverage

Direct end-session capture covers the entire uncaptured conversation interval through the current owner request. Inspect every available topic, including earlier work followed by a different subject. Preserve useful decisions, owner corrections, rejected alternatives with their reason, actual actions, current evidence, failed or incomplete work, remaining decisions and the next safe step. Compress this into durable knowledge and a resume point.

### Direct intent and read-only

The aliases `Zdestyluj i zapisz`, `Zdestyluj i zapisz wiedzę`, standalone `Koniec` and standalone `Kończymy` request capture-now for the clear current scope. Match owner intent after trimming whitespace and terminal punctuation, case-insensitively. Natural-language capture instructions may include an explicit subject or interval. Quoted commands, examples, idea-validation discussion and descriptions of a future rule are data rather than a current trigger. `Koniec bloku` retains its block-checkpoint route. Explicit formal phase commands retain their precedence.

Read-only capture has zero durable effects. An explicit `read-only`, `tylko w czacie` or `bez zapisu` restriction selects Capture mode read-only before any write-intent alias is applied. Return the requested summary or export inline in chat. Files, temporary files, task checkboxes, metadata, capture receipts and coverage pointers are durable effects for this restriction. An existing task-local read-only limit continues through continuation requests until the owner actually changes it. A later separate explicit write task has its own scope.

### Verified interval and all topics

Coverage starts at the earliest uncovered topic in this conversation. Resolve the previous distillation, checkpoint or memory by its recorded content coverage, owner, conversation/work scope, source anchors and verified artifact. File modification time alone never establishes coverage. A recent memory about one topic leaves every uncovered earlier topic in scope. A generic checkpoint that only records next steps leaves uncaptured decisions and work in scope.

Use an available stable conversation identifier and actual message/source anchors. If native identifiers are unavailable, record the observed date, explicit work scope and recognizable source anchors with that limitation. Do not invent message IDs or infer transcript access. When there is no prior verified capture, start from the beginning of the available conversation. After compaction or missing history, record History coverage partial or unknown, preserve supported facts and identify the missing interval. Partial history never supports a complete-history claim or advancement across a known gap.

Build Topic coverage before writing. For each topic record its source interval, current owner, previous capture evidence, useful delta, destination and disposition. Route client/project facts to their own approved namespaces. A minimal owner-scoped resume pointer can link the separate approved captures without copying private cross-client detail. An ambiguous owner or destination blocks that topic while independent approved topics can proceed. Explicit owner selection precedes any personal default.

### Honest progress and recoverable writes

Session closure preserves unfinished work. Record an actual failed or pending QA result, current source/evidence and next safe action in status/evidence or a scoped progress checkpoint. Capture intent alone does not start implementation, fixes, fresh quality campaigns, publication or a formal project-closing phase. Formal phase-6-distillation and completed Distillation State keep their existing quality and acceptance requirements. A chat progress capture remains independently useful while those gates are pending.

Reuse the existing owning capture artifact, checkpoint or work record for the coverage receipt. Record Conversation scope, Coverage start, Coverage end, Prior capture evidence, Topic coverage, History coverage, Persisted coverage, Resume point, Readback verification and Uncaptured items. Evidence links retain their actual source identity and result. The receipt is descriptive evidence, never permission or a new global capture database.

Advance persisted coverage only after successful write and readback of the exact scoped artifacts. A failed, partial or uncertain write leaves the global boundary at the last fully verified point. Preserve successful per-topic receipts and list the remaining uncovered topics. Before retry, inspect actual files, hashes and receipts, reconcile human edits and perform only the missing approved capture. A source hash change invalidates the affected coverage receipt. A template, flag, timestamp or claimed success alone never moves the boundary.

A repeated request with no new knowledge returns the existing verified capture reference and a no-new-knowledge reason. All relevant knowledge already captured is a complete result. Keep the user confirmation brief, with saved scope, artifact references, remaining uncovered items and a resume point when useful.

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
- Conversation scope:
- Coverage start:
- Coverage end:
- Prior capture evidence:
- Topic coverage:
- History coverage:
- Persisted coverage:
- Resume point:
- Readback verification:
- Uncaptured items:
- Completion state:
- Capture targets:
- Capture mode: <capture-now|proposal-only|read-only>
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
- when quality is incomplete, preserve the actual status/evidence and resume point under Incremental whole-chat coverage; formal completed distillation still requires its original quality gate;
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
- whether the mode was `capture-now`, `proposal-only` or `read-only`;
- source scope reviewed;
- durable writes performed or explicitly skipped;
- residual risk.

For new registered task resources apply `task-resource-cleanup.md`: durable QA/Capture stays outside temporary execution; release and eligible cleanup follow actual task closure, with one installed Workflow executor and seven-day whole-worktree retention.

## Sprint iteration

For actual task-local Sprint selection use `sprint-iteration.md` and the compatible installed Workflow. Keep preview/feedback implementation open until genuine final current-effect acceptance or explicit verification request. Deferred quality is not completed/PASS or resource release. Preserve normal behavior without explicit activation.
