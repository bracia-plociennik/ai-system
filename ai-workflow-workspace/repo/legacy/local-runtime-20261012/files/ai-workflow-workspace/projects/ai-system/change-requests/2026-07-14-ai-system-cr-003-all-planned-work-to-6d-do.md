# ASYS-CR-003 All Planned Work To 6D/DO

## Metadata

| Field | Value |
| --- | --- |
| Change request ID | `ASYS-CR-003-all-planned-work-to-6d-do` |
| Project | `ai-system` |
| Date | `2026-07-14` |
| Timing | `post-final-approval` |
| Type | `follow-up-enhancement` |
| Risk | `medium` |
| Status | `quality-passed` |
| Routing | `new-project-iteration` |

## Owner Request

Every new planned `build`, `deliver`, and `promote` item must create a `6d/do` TaskNote during the same owner-approved V3 check-in write. WIG may link to a plan item or be standalone, but it never emits a TaskNote. `must-do` is removed from the new model.

## Triage

- Affected scope: V3 properties, manual intake, task producer, derived indexes, contracts, validators, and smoke tests.
- Historical scope: V2 and existing V3 reports remain immutable and use legacy parsing; no retroactive TaskNote generation.
- Risk rationale: the change affects persistent private indexes and local TaskForge writes.
- Required owner decisions: resolved by the accepted owner plan, including standalone WIG closure as the source of minimum-day status.

## Routing Decision

- Selected route: `new-project-iteration`.
- Why: post-final schema and TaskForge write-path behavior cannot be handled as a micro-task.
- Required evidence: specification, spec QA, implementation result, quality evidence, distillation, checkpoint, and product validation.

## Closure Criteria

- [x] All new professional plan items write `6d/do` candidates independently of WIG or overload.
- [x] Linked and standalone WIG closure determines minimum-day status without creating TaskNotes.
- [x] Historical V2/V3 reports remain unmodified and non-retroactive.
- [x] Required validation and quality evidence exists.

## Result

- Final status: `quality-passed`
- Links: `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/specs/phase-3-asys-pops-012-all-planned-work-to-6d-do-specification.md`
- Implementation: `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-4-asys-pops-012-all-planned-work-to-6d-do-implementation-result.md`
- Quality: `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-5-asys-pops-012-all-planned-work-to-6d-do-quality.md`
