# Daily Check-In Index

## Purpose

Router for generated daily check-in indexes.

## Canonical Source

Markdown files in:

```text
AI_SYSTEM_WORKSPACE_HOME/personal-ops/check-ins/
```

are the source of truth.

## Derived Indexes

- `check-ins.csv` - spreadsheet-like analytical index.
- `check-ins.jsonl` - optional richer machine index.
- `check-ins.metrics.csv` - analytics-grade derived metrics for pattern analysis.
- `check-ins-fields.md` - field dictionary and source-label audit trail.
- `check-ins-conflicts.md` - duplicate date/source conflicts, when present.

If Markdown and an index disagree, Markdown wins.

## Lazy Sync State

- last-synced-at:
- last-synced-check-in-count: 0
- current-check-in-count: 0
- unsynced-check-in-count: 0
- sync-recommendation-threshold: 7
- last-sync-source: manual
- latest-unsynced-dates: none
- sync-recommendation: not required yet

Indexes may be stale by design after manual check-ins.

The threshold counts newly added daily files against `last-synced-check-in-count`. It does not detect edits to older daily Markdown and does not reliably detect deleted daily files as a stale-index event. If an existing day is edited or deleted, run owner-approved sync manually when index freshness matters.

Use:

```text
.systems/scripts/sync-personal-ops-check-ins --workspace <workspace-path> --status-only
```

Run sync without `--dry-run` only with exact owner approval.
