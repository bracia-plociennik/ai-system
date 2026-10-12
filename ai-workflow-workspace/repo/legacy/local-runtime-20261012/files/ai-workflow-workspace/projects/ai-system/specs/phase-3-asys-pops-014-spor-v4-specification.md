# Phase 3 Specification — ASYS-POPS-014 SPOR V4

## Daily Contract

Daily V4 uses `index_contract: 4`, `review_window_kind: weekend` on Monday and `previous-day` Tuesday-Friday. Saturday and Sunday have no Daily V4 artifact. Structured properties carry STATE, PROCESS, OUTCOME, REVIEW, Owner's Overrides, OSNR, Plan vs Reality Gap, Recovery Cost, WIG, and block-aware future items.

## Weekly Contract

One private Weekly Check-In stores the previous Monday-Sunday retrospective and the next Monday-Friday plan. Only `future_plan_items_json` is eligible for TaskNotes. Friday's weekly aggregate is not merged with a later canonical Friday Daily fact.

## Read Model And Renderers

Fresh official V3 and V4 records merge by unique effective session date. The daily renderer emits `Czas | Element | DoD | DL`, preserves unallocated work, then renders IF, six macro blocks, budgets, training/NSDR, warnings, and deferred scope. The weekly renderer emits retrospective scorecard plus future allocation table. `--check-file` compares canonical output with only trailing-newline tolerance.

## Privacy And Safety

V3 source and history are not rewritten. Trends contain only sanitized operational signals. Renderers are read-only and do not authorize tasks, deployments, messages, or external actions.
