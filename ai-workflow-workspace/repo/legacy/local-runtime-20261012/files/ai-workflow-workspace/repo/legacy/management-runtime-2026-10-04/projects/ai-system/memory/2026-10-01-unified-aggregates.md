# Unified Aggregate Product Boundary

Technical source: `distillations/phase-6-asys-pops-017-unified-aggregates-distillation.md` and `quality/phase-5-asys-cr-009-unified-aggregates-quality.md`.

Unified aggregate activation is workspace-local and does not migrate canonical schema/history. Use the common reader and V4 sync after activation; V3 sync writes stop. Preserve source version/confidence separately from aggregate contract. Unknown values cannot become observed zero, and source hashes/inventories are required freshness evidence. Rollback rebuilds from current sources rather than restoring stale index copies. Other workspaces keep compatibility until separately approved.

Private migration evidence is never product memory. Publication and installed checks precede private activation; Phase 8 remains separately owner-triggered.
