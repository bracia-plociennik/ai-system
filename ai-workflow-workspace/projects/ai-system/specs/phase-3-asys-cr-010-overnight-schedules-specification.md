# Overnight Schedules Architecture, Plan And Specification

## Source, Scope And Architecture

DoD source: explicit owner-approved midnight repair and its preceding 23:10-07:30 acceptance example. Implementation writes planned: yes, upstream AI System and scoped technical Workflow artifacts only. Baseline: 25ee186, clean main. Installed nested Workflow governs phases but is not modified. Earlier specifications/final assessments remain immutable.

Shared `schedule_interval_minutes(row, path)` in personal_ops_v4.py converts strict HH:MM into a session-day minute axis. `end_day_offset` is optional, exactly integer 0 or 1 (not bool, float, string or null). Start belongs to session_date; end belongs to session_date + offset. Require 0 < duration <= 1440. No implicit midnight rollover. Clock duration is a planning wall-clock duration, not measured elapsed sleep across DST.

Validator, renderer overlap checks, budget meal-slot projection and proposal capacity/checkpoints consume the helper. Renderer labels next-day ends without printing 24:xx. Proposal OSNR uses the final min(5, duration) minutes, with explicit start/end offsets when next-day endpoints occur. Local compatibility rows still work without a kind. No historical artifacts, local settings, canonical records, TaskNotes, indexes, scheduler or nested Workflow source changes.

## Implementation Slice Plan

Source: this scoped spec and owner request. Packaging: skipped, one dependent task.

| Slice id | Goal | Expected files/areas | Acceptance check | Evidence required | Status |
| --- | --- | --- | --- | --- | --- |
| S1 | Shared interval and consumers | parser, renderer, calculator, proposals | 500-minute sleep; correct overnight overlap/meal refusal and OSNR | focused regressions | pending |
| S2 | Contract and regressions | Personal Ops/template, SPOR runners | explicit opt-in, backward compatibility and failure cases | full consumer tests and diff review | pending |
| S3 | Quality and delivery | scoped evidence/capture, Git, official updater | full QA, scoped publication and installed regressions | command outputs and technical capture | pending |

Stop rule: unapproved scope, private mutation, new dependency, failing unrelated gate or unknown concurrent writer stops delivery rather than weakening validation.

## Acceptance Conditions

1. 23:10-07:30 with end_day_offset 1 loads and yields 500 wall-clock minutes; renderer identifies next day.
2. Default/explicit zero same-day rows behave as before; end <= start without offset, malformed clocks, invalid offset types/range, zero duration and spans over 24 hours fail.
3. Meal projection cannot reinterpret next-day meal ends as same-day six-slot macro packages. Sleep does not inflate professional capacity; overnight work keeps last-five-minute OSNR, including endpoints near midnight.
4. Existing privacy/read-only/source semantics and native V4 synchronization/task preflight remain valid; no migration or history rewrite.
5. Required product QA, semantic full diff review, scoped Workflow evidence validation, commit/push and official update succeed before delivery is called complete.

## Plan Quality Contract

- Plan classification: implementation-capable.
- Artifact QA route: scoped architecture/plan QA then phase-3-spec-qa before product edits.
- Artifact QA trigger: complete spec reviewed against owner intent and all producer/consumer fields.
- Implementation Quality Closure route: phase-5-quality, then phase-6-distillation and phase-7-checkpoint; Phase 8 excluded.
- Required verification: check-spor-v4, check-spor-proposals, Personal Ops/V4, Weekly/V4, Task Management, py_compile, git diff --check, validate-ai-system --profile full with smoke, validate-workflow --profile full --project ai-system; installed SPOR tests after updater.
- Quality-ready criteria: complete DoD, no P0/P1/material P2, current review/evidence, no unrelated changes.
- Owner opt-out: none for quality.
- Not-applicable reason: none.
- Blocking decision: none.
- Next route: scoped artifact QA, then phase-4-implementation.

## Delivery Constraints

- Mode: owner-opt-out.
- Deadline: none. Time budget: none. Timezone: Europe/Warsaw.
- Must-have outcome: explicit overnight acceptance and correct downstream behavior with regressions and installed delivery.
- Should-have scope: none. Stretch scope: none.
- Explicitly deferred scope: history/settings backfill, actual sleep DST arithmetic, multi-day events, new schema version, TaskNote generator changes, Phase 8.
- Quality floor: complete semantic and consumer QA, privacy and unchanged history.
- Cutline rule: do not reduce must-have or QA; stop if scope needs expansion.
- Overrun checkpoint: no time boundary; report scope blockers.
- Owner override: scope-bound no deadline/timebox.

## Risk, Decisions And Capture

Medium/full-project; safe synthetic local fixtures only. Invalid next-day macro projections remain unavailable rather than fabricated. Rollback: revert scoped product commit via normal reviewed change, not destructive Git reset. Explicit owner counterpart decision: no, AI System only. Unknowns blocking: none; non-blocking: wall-clock vs DST distinction disclosed in docs. Knowledge capture required in this iteration only; no private user records. Model recommendation: GPT-5.6 Sol High; multiple shared consumers and adversarial validation; current model known no; Blocking no.

Instruction refresh: performed-full after context transition and target change; root/nested AGENTS, intake, risk, permissions, routing, slicing, delivery, phase gates and current project/repo status read. Historical repo intake paths are stale; live root/shim/main baseline governs. Skills used: none (no matching Python/SPOR skill in workspace/system frontmatter).

## Optional Knowledge Capture

Defer technical capture to distillation/checkpoint; privacy scope pass.

## Owner Decision Checkpoint

Clear; exact implementation/publication approval and counterpart answer recorded in CR-010. No further blocking decision.
