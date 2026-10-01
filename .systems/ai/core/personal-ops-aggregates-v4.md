# Unified Personal Ops Aggregates V4

`personal-ops-aggregate-v4-v1` is a derived read contract, independent of canonical Daily/Weekly schema versions. Original Markdown and approved source versions remain unchanged. A unified Daily JSONL row contains `properties`, source schema/path/hash, per-field provenance/confidence, dated observations, excluded-field dispositions and private legacy extensions. Weekly canonical records remain a separate stream; never add weekly facts to daily sums.

## Mapping And Privacy

The aggregate dictionary accounts for all V3 schema fields, V4 index fields and explicitly registered additive fields. Unknown nonempty fields block migration. Known JSON structures are preserved after excluded-evidence/credential checks. Legacy archive enrichment uses an explicit safe-field allowlist and source-path matching; original archive dates are metadata, not new sessions. Raw Check-In, Working Dump, OCR, interpreted input and attachment payloads/paths are excluded. Redacted rows contain no private values, observations or legacy extensions. Public trends contain only counts for explicitly allowed work/organism categories; no raw labels, subjective scores, health, finance, calories, reflections or Life Alignment.

Unknown imported defaults stay preserved with confidence `unknown`, but are blanked in analytical reads. Do not infer numeric scores from old descriptions, completed outcomes from presence flags, WIG from minimum-day, or historical Life Alignment answers. Conflicting metric values stop activation/arithmetic. Dated facts deduplicate by metric/period; partial overlaps require reconciliation. Multi-day totals remain totals; untyped calorie aggregates are excluded from daily arithmetic and disclosed with coverage. Incomplete budgets show known subtotals and unknown full balances, never fictional zero intake.

## Storage And Freshness

One atomic directory symlink `personal-ops/indexes/check-ins-v4-active` selects an immutable generation under `generations-v4/`. This single filesystem pointer is used instead of two independent JSON/symlink pointers. Resolve once and verify all output hashes. Stable `check-ins-v4.*` links point through the same pointer. The generation includes JSONL, CSV, metrics, trends, router, dictionary and manifest. Same-count source edits invalidate freshness; native source inventory changes require sync. Readers never fall back to mixed V3+V4 after activation.

`personal-ops/aggregate-sources-v4/` stores hashed historical aggregate input and migration journal. Unified sync retains this history and adds current native V4; changed historical sources require explicit reconciliation. V3 sync writes are retired for migrated workspaces. Unmigrated workspaces retain existing mixed readers and validators. A shared nonblocking writer lock serializes migration/sync/rollback.

## Commands And Cutover

Read-only default: `.systems/scripts/migrate-personal-ops-aggregates-v4 --workspace <path> --json`.

After owner approval and installed QA: add `--apply --owner-approved`. Build candidate, recheck frozen hashes, preserve old outputs in a dated archive with hashes, select the candidate atomically, then retire prior active aggregates. Interrupted archival resumes idempotently from the journal. No TaskNotes, canonical sources or other workspace data are written. Sync with `.systems/scripts/sync-personal-ops-check-ins-v4 --workspace <path> --post-write`; `--status-only` verifies hashes without writing.

Rollback requires `--rollback --owner-approved`. Rebuild old compatible outputs from current canonical sources before withdrawing unified mode, retaining any check-ins created after activation. Archived evidence and generations remain recoverable. Do not copy a stale archive over new facts. Publication and official updater verification precede owner-local activation.
