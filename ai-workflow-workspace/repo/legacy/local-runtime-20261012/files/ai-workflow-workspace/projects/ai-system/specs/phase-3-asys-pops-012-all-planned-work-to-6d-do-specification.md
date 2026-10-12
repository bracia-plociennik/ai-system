# Phase 3 Specification - All Planned Work To 6D/DO

## Metadata

- Project: `ai-system`
- Task: `ASYS-POPS-012-all-planned-work-to-6d-do`
- Change request: `ASYS-CR-003-all-planned-work-to-6d-do`
- Risk: `medium`
- Readiness: `ready`

## Contract

- New `all-professional-do-v1` reports create one `6d/do`, open, high-priority TaskNote for every valid `build`, `deliver`, or `promote` plan item.
- WIG is either `plan-item` or `standalone`; it has a stable ID and Definition of Done but never creates a TaskNote.
- A linked WIG references a plan item and therefore shares that item's one ordinary TaskNote. A standalone WIG has its own closure status and is never a candidate.
- Minimum day derives only from the prior-day WIG closure. `must-do` is not part of the new manual contract.
- Overload remains indexable information only; it cannot suppress candidate count or TaskNote creation.
- Existing V2 and old V3 reports remain immutable, parse with legacy semantics, and do not generate retroactive TaskNotes.

## Implementation

1. Add versioned task-generation and WIG fields to the V3 properties contract with non-mutating legacy defaults.
2. Update manual/template/docs to remove must-do, Task skip, and task bucket routing for new reports.
3. Force new-policy professional candidates to `6d/do` and decouple them from readiness/overload.
4. Add WIG closure and minimum-day derivation for linked and standalone WIGs.
5. Update validators and synthetic smoke coverage for all-professional generation, WIG variants, overload, and legacy preservation.

## Acceptance

- One candidate per qualifying professional plan item; no WIG candidate or duplicate.
- Missing or standalone WIG does not suppress TaskNotes.
- New reports cannot route a professional planned item to another 6D bucket before writing.
- V3 legacy reports remain readable without canonical rewrites.

## Owner Decision Checkpoint

- Decision state: `clear`
- Accepted plan: `Daily Check-In V3: All Planned Work To 6D/DO`
- Next route: `phase-4-implementation`
