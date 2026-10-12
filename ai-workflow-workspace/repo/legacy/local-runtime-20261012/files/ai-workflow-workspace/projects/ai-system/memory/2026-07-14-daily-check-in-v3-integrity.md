# Daily Check-In V3 Integrity Rules

## Scope

Durable project rules for V3 daily check-in reports, derived indexes, and TaskForge write provenance.

## Rules

- Require basename date, report ID, top-level session date, and properties session date to agree before generating derived indexes.
- Reject duplicate effective session dates before replacing indexes.
- Persist TaskForge write provenance in a declared property; preserve references after marker-based deduplication and use an empty list only for a deliberate skipped write.
- Derive task eligibility from structured plan items and validate it against readiness and overload gates.
- Exercise write success, unavailable preflight, deduplication, and subtask paths with synthetic temporary fixtures before treating the producer as reliable.

## Boundary

- Do not use this memory to rewrite historical V2/V3 runtime reports or indexes.
- Real runtime TaskForge writes remain owner-approved and local-only.
