# ASYS-CR-005 SPOR Daily V4 and Weekly Check-In

## Metadata

| Field | Value |
| --- | --- |
| Change request ID | `ASYS-CR-005-spor-daily-weekly` |
| Project | `ai-system` |
| Date | `2026-08-17` |
| Requested by | `owner` |
| Timing | `post-final-approval` |
| Type | `feature / contract evolution` |
| Risk | `medium-high` |
| Status | `ready-for-delivery` |
| Routing | `new-project-iteration` |
| Cross-system impact | `no` |

## Idea Validation

- **Keep:** SPOR STATE / PROCESS / OUTCOME / REVIEW, independent scales, OSNR-only block checkpoints, fixed WIG DoD, budget/macro projections, and TaskNotes.
- **Improve:** V3 cannot represent Monday's Friday-Sunday review; the daily renderer is not chronological; weekly planning has no retrospective contract.
- **Add:** Daily V4, one combined Weekly Check-In, V3+V4 read model, cadence rules, explicit block allocation, deterministic renderers, and duplicate-Friday protection.
- **Resolved decisions:** no historical V3 migration, one weekly artifact, Monday Daily owns Friday-Sunday facts, local schedule with explicit `block_id`, two delivery slices with an eight-hour timebox.
- **Gate result:** `accepted-with-changes`.

## Scope

Implement Daily Check-In V4, combined Weekly Check-In, compatibility read model, deterministic daily/weekly renderers, templates, validators, fixtures, and documentation. Preserve V3 source Markdown and indexes byte-for-byte. Do not add external integrations, production actions, or private runtime data.

## Evidence And QA

- Source evidence: owner SPOR briefs, screenshots, current V3 contracts, schema, sync, calculator, renderer, and AI Workflow project artifacts.
- Artifact route: phase 1 architecture QA, phase 2 plan QA, phase 3 spec QA.
- Quality route: phase 5 quality, distillation, checkpoint, final check.
- Delivery: `timebox-only`, eight hours, Europe/Warsaw; overrun stops without commit.
