> Compatible new implementation tasks use `default-sprint.md` V2: bounded targeted QA after acceptance and incremental phases5–7; explicit full verification/Phase8 remains separate. This scoped rule takes precedence over ordinary implementation/checkpoint chaining below. V1 and unsupported tasks retain installed rules. `Phase X` / `-all` follows `phase-x-maintenance.md`; manual only, never autopilot/Dreaming.

# Task Intake

## Intent brief and private style context

Use intent-to-execution-brief.md during existing intake: minimal inline/embedded fields with provenance and disposition; preserve original request/accepted decisions as independent QA anchors. Batch triage and current action/phase ceilings remain first. This adds no phase or approval. Use style-profile.md for optional explicitly enabled local style; recording needs actual exact-target consent and minimal provenance/privacy, observations stay tentative and current instruction overrides profile. Invalid/disabled profile supplies no preferences. Auto chooses only covered reversible options and queues protected owner decisions; Human groups material questions, settled answers not repeated and noninteractive routes stay so.


## Bounded Defect Eligibility

Use `execution-efficiency.md` for an approved reversible defect with known consumers, observable
DoD and focused regression evidence. Its single work record may consolidate scope, plan, tests,
review and capture disposition. Eligibility is not approval. A medium-risk defect is not a
micro-task; installed AI Workflow risk and phase rules still decide its execution route.
Missing capability, unknown consumers, architecture or sensitive effects require the normal route.

## Purpose

Task intake is the mandatory pre-routing lens for new work in AI System.

It is not a phase and does not grant write permission. It decides whether the request is clear, safe, complete, and ready for planning or implementation.

Use `.systems/ai/core/owner-approval.md` to determine whether direct approval or strict acceptance of the immediately preceding complete plan supplies recognized owner approval. Task intake still requires resolvable target, scope, acceptance criteria, decisions, and evidence.

For a new planning, implementation, or QA scope, include the advisory Model recommendation from `.systems/ai/core/model-selection-guidance.md`. It never blocks routing or changes any gate.

## When To Use

Use task intake before:

- selecting a workspace for runtime work when more than one workspace exists;
- creating a client or project workspace;
- briefing or updating a client workspace;
- creating a primary-entity or owned-asset workspace;
- triaging a material dump request;
- planning or implementing new work;
- accepting a change request;
- creating a side task or micro-project;
- orchestrating implementation in a selected repository through its local AI Workflow;
- capturing memory when scope or privacy is unclear;
- suggesting or creating prompt composition artifacts;
- proposing `system-insights`;
- automating or batching local file work.

If the owner asks only for status or command output, use guide or normal command routing.

## Required Summary

Use these sections:

### Co zostaje

What is clear, useful, safe, and should remain in scope.

### Co jest słabe / do poprawy lub usunięcia

What is vague, unsafe, over-scoped, duplicated, stale, or should be changed.

### Czego brakuje

Missing acceptance criteria, target workspace, ownership, privacy review, safe commands, required evidence, or owner approval.

### Blokery / decyzje

Blockers and decisions that prevent safe planning, writing, movement, distillation, or PASS.

### Rekomendowany routing

Choose one safe route:

- guide/status recovery;
- client brief intake;
- dump triage proposal;
- client workspace creation;
- primary-entity workspace creation;
- owned-asset workspace creation;
- project workspace creation;
- memory capture;
- distillation;
- prompt composition proposal;
- system-insights anonymization proposal;
- change request;
- side task or micro-project;
- project orchestration using `.systems/ai/core/project-orchestration.md` when the request names work in a managed repository;
- STOP for missing approval, ambiguous ownership, privacy risk, or unsafe external effects.

## Stop Conditions

Stop before planning or implementation when:

- the owner, primary entity, client, owned asset, project, or target path is ambiguous;
- the target workspace is ambiguous;
- acceptance criteria are missing and cannot be inferred safely;
- material may contain secrets, legal content, private customer data, or production data;
- real external effects are possible;
- requested writes lack recognized owner approval;
- prompt composition would change scope, risk, permissions, evidence, owner approvals, or client commitments;
- the request would bypass validation, evidence, privacy, or stop conditions.

## Artifact Rules

Task intake may live in the response or in the artifact already being created.

Do not create a separate task-intake artifact unless the routed work already needs one.

Never store private client details in `.systems/`.

## Delivery Constraint Discovery

Resolve task-local mode through `execution-modes.md` first. Auto records absent
deadline/timebox as `auto-unconstrained` and queues material blockers after safe
independent work. Human uses the grouped discovery below. Neither mode supplies
approval, changes an analysis/planning request into implementation or guesses ownership.

For new implementation work that will create or change system, project, client, or owned-asset artifacts, apply `.systems/ai/core/delivery-constraints.md` after discoverable repository and workspace facts are known.

Resolve an existing deadline, time budget, must-have outcome, quality floor, and cutline from the current owner message, accepted plan, or active work artifact. Human asks only material missing questions, grouped into at most `1-3` questions. Auto queues blocking outcome questions and records missing time limits without asking. Do not repeat deadline or time-budget questions when the answer is already present.

A missing constraint is not permission to invent one. In Human Mode, stop before dependent implementation unless the owner supplies the missing constraint or explicitly opts out for the current work. Auto Mode does not stop solely for absent time constraints.

For a change meeting the strict micro-change criteria in `delivery-constraints.md`, record the exception instead of asking a separate deadline/timebox question. A small file count alone is insufficient; API, schema, policy, security, external effects, and cross-module changes remain on the normal route. If the scope grows, reclassify before further writes.

## Undistilled Work Reminder

When a selected workspace and scope are known, inspect applicable Distillation State records from `.systems/ai/core/distillation-state.md` before switching to an unrelated implementation unit. Report unresolved counts and owner actions without blocking the new task automatically or changing any state.


## Goal-Focused Maintenance Integration

Use goal-focused-maintenance.md only after explicit scoped activation and verified local support. One nearest-owner private maintenance/queue.json records proven independent incidental debt; project coordination references the Workflow-owned queue rather than duplicating it. E01–E05 and actual current-goal blockers are immediate. Five distinct active project causes or the third actual affected parent task schedule one consolidated milestone summary; scans/resumes do not count or repeat receipts. One stable approved parent shares TOTAL 600 seconds incidental diagnosis/edit/review/test/record work across both adapters. No background executor, scheduler or automatic TaskNotes. Required current QA and full release/updater failures remain binding. Missing counterpart support keeps existing gates; labels are not activation or authority.

Record accepted goal/DoD/architecture, actual required identities, canonical owner, stable parent and exact approved maintenance roots. Classify unknown impact honestly; no guessed independent scope.

## Independent judgment

Use `.systems/ai/core/critical-judgment.md` for proportional, evidence-based assessment of the goal, proposed mechanism and the agent's own advice. State material objections directly with basis, consequence and a feasible recommendation; acknowledge sound ideas and uncertainty. Preserve existing authority and phase gates, short routine answers, informed permitted tradeoffs and applicable quiet handling of independent minor debt.
