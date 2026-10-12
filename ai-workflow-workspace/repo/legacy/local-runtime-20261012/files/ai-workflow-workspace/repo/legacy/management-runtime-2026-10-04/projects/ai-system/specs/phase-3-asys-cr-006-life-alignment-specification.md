# Phase 3 Specification - ASYS-CR-006 Life Alignment Cards

## Contract

`life_alignment_contract: last-period-alignment-v1` activates the additive Daily/Weekly fields. Values are `yes`, `no`, or `unknown`; presentation is `TAK`, `NIE`, or `UNKNOWN`.

Daily uses the last 14 and 30 answered Daily records. Weekly uses the last 4 answered Weekly records. Unknown records are excluded from both numerator and denominator. Thresholds are evaluated only after the complete window exists.

## Gate

Yellow is non-blocking. Red keeps canonical check-in writes available but blocks professional TaskNote writes until a valid plan-change or owner override resolution is present. Resolutions are episode-scoped and private.

## QA Result

`phase-3-spec-qa: accepted`; implementation may proceed.
