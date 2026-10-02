# Overnight Schedules Change Request

- Change request ID: ASYS-CR-010-overnight-schedules
- Project: ai-system
- Timing: post-final-approval
- Type: defect
- Status: in-progress
- Risk: medium
- Task: ASYS-POPS-018-overnight-schedules
- Owner request: repair upstream midnight schedules, QA, commit, push and official management update; no deadline or timebox.
- Triage result: the V4 clock-only comparison rejects legitimate overnight sleep; a shared explicit endpoint offset prevents silent wrapping of invalid schedules.
- Routing decision: new-project-iteration, scoped specification and implementation followed by Phase 5, technical capture and checkpoint.
- Affected files: V4 parser, daily renderer, budget meal projection, SPOR proposal capacity/checkpoint producer, Personal Ops contract/template, existing SPOR regression runners.
- Evidence required: same-day compatibility, explicit next-day duration/rendering, invalid offsets/times, meal projection, midnight OSNR, full product and project Workflow checks; installed verification.
- Final check impact: new Phase 8 is owner-triggered only; no final-owner-yes inferred.
- Post-final impact: CR-009 and earlier approvals/assessment bytes remain unchanged. Owner-approved byte-preserving archive and technical reference relocation are recorded in `quality/asys-cr-010-review-record.md`.

## Task Intake

- Co zostaje: V4 schema version, strict clocks, daily schedule ownership, private source boundaries and five-minute OSNR inside work capacity.
- Co jest slabe / do poprawy: end-after-start compares only HH:MM; consumers lose next-day meaning.
- Czego brakuje: explicit relative endpoint and cross-consumer tests.
- Blokery / decyzje: owner approved AI System only; no remaining material decision. No migration/backfill.
- Rekomendowany routing: medium-risk defect iteration, not micro-task.

## Owner Decision Checkpoint

- Decision state: clear.
- Owner explicitly answered: only AI System, no AI Workflow changes.
- Auto-resolved reversible decision: additive integer end_day_offset, default 0, allowed 0/1; elapsed wall-clock span greater than zero and at most 1440 minutes.
- Counterpart: none; handoff not-required because the schedule contract is product-specific.

## Optional Knowledge Capture

Technical distillation/checkpoint only, no private sources or global memory changes.

## Closure

- Status: `done` on `2026-10-02`.
- Phase 8 technical final check: `PASS`; `quality/recovery-phase-8-final-check.md`.
- Owner final approval: received and applied; `quality/phase-8-asys-cr-010-final-owner-approval-2026-10-02.md`.
- Published and installed at AI System commit `1295fb7`; official update and installed SPOR regressions completed.
- Scope closed: CR-010/POPS-018 only. No canonical history migration or backfill; independent CRs remain unchanged.
