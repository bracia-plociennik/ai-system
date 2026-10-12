# Unified Aggregates Technical Distillation

- Task: ASYS-POPS-017-unified-aggregates
- Quality: PASS for product scope; `quality/phase-5-asys-cr-009-unified-aggregates-quality.md`.
- memory-in-repo-memory: true

## Durable Decisions

Aggregate version and source schema version are separate. Imported history carries original values, confidence, source hashes/ranges and explicit field dispositions. Unknown defaults are evidence, not observed zero; blank them in analytics and metrics. Preserve richer archive information as provenance-bearing extensions when its semantics/date cannot safely be promoted to an observation.

One directory symlink selects all immutable exports. Flat compatibility links resolve through it, never through independently updated pointers. Flush generation files, rollback backups and journal/directory changes before activation/retirement. Shared nonblocking locking and source hashes plus inventories cover concurrent writers, same-count edits and additions.

Unified refresh joins frozen historical input with current native V4. Historical source drift requires reconciliation rather than silently retaining stale data. V3 writes are retired only after explicit workspace activation. Rollback rebuilds from current sources so newer check-ins survive; archive copies are evidence, not stale restore commands.

Consumers use shared normalized observations and per-period coverage. Duplicate equal facts count once; conflicts/overlaps stop. Untyped multi-day calorie totals cannot be divided into daily intake. Weekly remains a separate stream. Dreaming only consumes allowlisted sanitized category counts, not detailed/private aggregates.

## Problems And Reuse

Metrics-only exports can accidentally revive unknown default zeros even when JSONL provenance is correct. Test each consumer/projection, not just the richest export. Path checks must cover namespaces, pending JSON files, lock files and generation members; rejecting only the top-level directory is insufficient.

## Delivery And Follow-Up

Publication and the official updater precede target-only activation. Repeat installed checks, freeze hashes, compare archived outputs and prove idempotent sync afterward. Never backfill canonical Markdown or other workspaces as part of this route. Keep private migration manifests local and tracked evidence technical-only. Actual cutover remains pending at this product checkpoint.

## Capture And Residual Risk

Project-memory router entry links this distillation; no duplicate repo memory, System Insights or Codex memory. Older semantics remain incomparable where evidence is insufficient. A later historical source edit must be explicitly reconciled.

## Owner Decision Checkpoint

Owner-approved scoped product implementation and target migration; cross-system impact no. No Phase 8/final owner approval is inferred.
