# ASYS-CR-006 - Life Alignment Cards

## Intake

- **Co zostaje:** SPOR V4 STATE / PROCESS / OUTCOME / REVIEW, istniejące V3+V4 read model, renderery i TaskNotes.
- **Co jest słabe:** brak jawnego sygnału, czy plan jest zgodny z długoterminowym kierunkiem życia oraz brak agregacji tego sygnału.
- **Czego brakuje:** odpowiedzi TAK/NIE/UNKNOWN, progów ostrzegawczych, epizodów czerwonej kartki i blokady nowych profesjonalnych TaskNotes.
- **Blokery / decyzje:** UNKNOWN wyłącza się z mianownika; Daily liczy 14/30 odpowiedzi, Weekly 4; red wymaga zmiany planu albo owner override.
- **Rekomendowany routing:** post-final change request, AI System upstream only, task `ASYS-POPS-015`.

## Approved Contract

- Marker: `life_alignment_contract: last-period-alignment-v1`.
- Daily property: `planned_day_life_alignment_answer`.
- Weekly property: `planned_week_life_alignment_answer`.
- Optional resolution: `life_alignment_resolution_json`.
- Historical V4 artifacts without the marker remain valid and evaluate as UNKNOWN.
- No backfill, public trend promotion, memory promotion, or TaskNote creation from the answer.

## Thresholds

- Daily: yellow at `11/14 NIE`, red at `23/30 NIE`.
- Weekly: yellow at `2/4 NIE`, red at `3/4 NIE`.
- Red blocks professional TaskNote writes until a plan-change resolution or non-empty owner override is valid.

## Delivery Contract

- Timebox: 4 hours, `Europe/Warsaw`.
- Must-have: parser/schema, shared calculator and CLI, both renderers, TaskNote gate, privacy projection, regression tests.
- Cutline: defer extended examples and documentation before validation, privacy, or gate tests.
- Overrun: stop without commit and report completed scope and QA state.
