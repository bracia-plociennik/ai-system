# ASYS-POPS-014 SPOR Daily V4 and Weekly Check-In

## Definition Of Done

- Daily V4 captures previous-day or Monday weekend review windows with STATE / PROCESS / OUTCOME / REVIEW, OSNR, Owner's Overrides, Plan vs Reality Gap, Recovery Cost, and cadence validation.
- One private Weekly Check-In combines the previous-week retrospective and next Monday-Friday plan; TaskNotes read only future professional items.
- V3 remains unchanged and a read model combines unique V3/V4 records without double-counting Friday.
- Daily output is a deterministic `Czas | Element | DoD | DL` table plus complete state, macro, budget, warnings, and deferred sections.
- Weekly output is a deterministic scorecard and future-week allocation table.
- Targeted and full validation pass without private data entering trends.

## Delivery

- Mode: `timebox-only`
- Time budget: `8h`
- Must-have: contracts, read model, renderers, validators, and regression fixtures.
- Cutline: defer examples and expanded README text before tests or privacy controls.
- Overrun: stop without commit and report delivered/deferred scope.

## QA Route

`phase-1-architecture-qa` -> `phase-2-plan-qa` -> `phase-3-spec-qa` -> `phase-5-quality`.
