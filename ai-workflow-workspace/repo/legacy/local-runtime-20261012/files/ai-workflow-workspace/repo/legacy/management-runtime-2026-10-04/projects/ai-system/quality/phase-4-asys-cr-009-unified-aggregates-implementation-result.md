# Phase 4 Implementation Result - Unified Aggregates

Work: ASYS-POPS-017-unified-aggregates / ASYS-CR-009-unified-aggregates.

## Delivered Product Scope

The shared aggregate adapter preserves source properties with mapping dispositions, confidence, source range and hashes. Safe V2 archive enrichment remains a separate provenance-bearing extension rather than an invented observation. Structured actual facts have explicit periods; ambiguous or overlapping values stop arithmetic. Unknown defaults are preserved in detailed evidence but blanked in analytical reads and metrics exports.

The owner-gated migration CLI stages immutable generations, hashes rollback copies, atomically selects one directory pointer and archives prior active outputs. A journal supports interrupted archive completion. A shared writer lock excludes concurrent sync/migration. Unified V4 sync retains immutable history and current native sources; V3 writes are retired only in opted-in workspaces. Rollback rebuilds compatibility from current canonical sources and retains newer check-ins.

The common parser, budgets, SPOR proposals and Dreaming boundary use the unified generation. Budget results disclose coverage and unknown full balances. Unmigrated workspace behavior remains unchanged. No canonical schema, historical Markdown, TaskNotes or AI Workflow product change is included.

## Implementation Slices

S1 adapter/mapping, S2 lifecycle and S3 consumers are implemented. S4 product QA/publication/installed migration remains gated; this artifact does not claim completed private rollout.

## Evidence And Findings

- Twenty-four synthetic regressions currently pass, including mapping/private exclusions, unknown metrics, source range, dated aggregates, corruption, same-count source edits, source additions, writer locking, activation failure, interrupted archival, coverage, proposals, approval and rollback with a newer check-in. Additional adversarial cases reject write-path/lock/generation symlinks, retired V3 writes and an inventory race before first activation.
- Private read-only differential audit: all mapped historical source values match the candidate; every archive enrichment row is represented; excluded fields are explicit evidence dispositions. No private payload is captured here.
- A protected-file hash comparison covers 462 selected original check-in, weekly-plan, TaskNote and foreign-index files: unchanged before publication.
- Initial full product validation failed because a required root-template reference was removed. The wording was restored; the subsequent full validation passed with smoke tests. A later semantic review fixed unknown metric defaults and missing imported source-range provenance; full verification must follow those final fixes.
- Do not use output counts alone as freshness proof: source content hashes and inventories are verified on every unified read.
- Backup copies, generation contents, JSON journals and directory changes are flushed before activation/retirement so rollback evidence is not merely buffered at the cutover boundary.

## Remaining Delivery Gates

Current-baseline full product and project Workflow QA, scoped commit/push, official management updater, installed checks, workspace dry-run and target-only migration/archive verification. No formal Phase 8 is requested.

## Constraints And Capture

Deadline/timebox: owner-opt-out, none. Quality floor: full semantic review plus applicable smoke, no known P0/P1/material P2. Technical distillation/checkpoint required; no private facts in tracked evidence and no Codex memory writes.
