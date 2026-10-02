# Overnight Schedules Technical Distillation

- Task: ASYS-POPS-018-overnight-schedules
- Quality: PASS; `quality/phase-5-asys-pops-018-overnight-schedules-quality.md`.
- Implementation: `quality/phase-4-asys-cr-010-overnight-schedules-implementation-result.md`.
- Distillation State: `distillations/2026-10-02-overnight-schedules-distillation-state.md`, ready before this accepted distillation, completed afterwards.
- memory-in-repo-memory: true

## Durable Decisions

Use one session-relative minute axis for schedule consumers. Strict HH:MM plus integer `end_day_offset` 0/1 is additive to the existing V4 contract: start is on session_date, end on session_date plus offset. Never infer midnight rollover from clock ordering. Require positive duration at most 1440 wall-clock minutes; this is planning, not DST-adjusted measured sleep.

Renderer plain and matched rows preserve endpoint offsets and label next-day ends. Meal conflict checks retain the existing start-point/clipping policy; an overnight meal cannot be forced into a same-day macro package. Sleep is schedule context, not work capacity. OSNR endpoint day offsets prevent negative or 24:xx clocks near midnight and keep short checkpoints inside the block.

## Problems And Constraints

Do not inherit a positive offset into an omitted-offset negative fixture. Do not widen meal-overlap semantics during a midnight repair: existing clipping assertions remain authoritative unless separately approved. Tests cover exact midnight, typed offsets, zero/24-hour boundaries, canonical sync/task preflight and proposal capacity.

Historical hash-bound assessments become stale when shared source changes. The owner approved exact byte-preserving archival of the two CR-009 reports and reference updates, not new Phase 8 or a changed verdict. Their hashes and locations are in `quality/asys-cr-010-review-record.md`.

## Evidence And Follow-Up

Product full run df518f78d52241a6b1811c30b65894d6 completed with seven smoke suites; complete project Workflow QA completed with five smoke groups. The sandbox process-inspection failure is retained separately, not counted as passing evidence. No nested Workflow product changes, private sources, settings/history backfill or TaskNotes.

Future producers must supply the offset explicitly. Official update and installed regressions are separate delivery evidence. Actual DST arithmetic and multi-day scheduling require a new decision; no implicit extension follows this repair.

## Owner Decision Checkpoint

Clear: implementation, publication/update, no timebox and AI System-only scope approved. Historical archival approved separately. Phase 8/final-owner-yes remains unrequested.

## Optional Knowledge Capture

Technical project memory and Phase 7 checkpoint required; no repo-memory, External Memory, System Insights or Codex memory write. Privacy/scope pass.
