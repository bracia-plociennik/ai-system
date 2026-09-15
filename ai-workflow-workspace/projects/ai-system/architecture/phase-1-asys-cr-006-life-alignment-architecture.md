# Phase 1 Architecture QA - ASYS-CR-006

## Decision

Add a marker-aware private metric to V4. Keep V3 and unmarked V4 compatible. A shared read-only calculator owns normalization, windows, cards, episode resolution, and the professional-write gate. Renderers consume that result; the TaskNote generator checks it before any vault mutation.

## Privacy

Daily answers are private metric fields. Resolution objects are private detailed-index fields. Redacted projection removes both. Raw Check-In, Working Dump, trends, memory, insights, and TaskNotes never receive the answer or rationale.

## QA Result

`phase-1-architecture-qa: accepted`; no unresolved P1/P2 decision.
