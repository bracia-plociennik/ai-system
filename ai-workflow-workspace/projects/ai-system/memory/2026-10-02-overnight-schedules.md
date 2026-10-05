# Overnight Schedules Product Boundary

Source: `distillations/phase-6-asys-pops-018-overnight-schedules-distillation.md`; current Quality `quality/phase-5-asys-pops-018-overnight-schedules-quality.md`.

V4 schedule rows accept an explicit integer `end_day_offset` 0/1. Default zero means same day; a positive interval up to 24 wall-clock hours is required. Use the shared `schedule_interval_minutes` helper across validation, rendering, meal projection and proposal checkpoint generation, rather than independently wrapping clock values.

Next-day rendering labels the endpoint. Sleep is not work capacity. OSNR remains in the final five minutes of work with day offsets near midnight. A next-day meal incompatible with the same-day macro template is unavailable, not guessed. Established meal clipping behavior remains unchanged.

No schema bump, history/settings migration or private write. Planning duration does not claim DST-adjusted actual sleep. Two stale CR-009 assessments are archived byte-for-byte under `history/asys-cr-009/25ee186/evidence/` with explicit owner approval; historical final-owner-yes is unchanged. CR-010 formal final check requires a separate owner trigger.

Official publication/update and installed tests must be evidenced separately from this prepublication technical capture. Do not treat a Quality PASS as proof of a later push or installation.
