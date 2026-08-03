# Check-Ins v3 Index

This router is for official Properties + Raw Audit V3 indexes. It may include native reports and an owner-created immutable legacy snapshot. A normal daily check-in write must refresh this router and the five companion indexes before the post-write summary. It may be stale only during diagnostics, repair, or an explicitly failed durable-first refresh.

- last-synced-at:
- last-synced-check-in-count: 0
- last-synced-native-check-in-count: 0
- current-check-in-count: 0
- current-native-check-in-count: 0
- current-legacy-check-in-count: 0
- unsynced-native-check-in-count: 0
- unsynced-check-in-count: 0
- sync-recommendation-threshold: 7
- last-sync-source:

Generated artifacts: `check-ins-v3.csv`, `check-ins-v3.jsonl`, `check-ins-v3.metrics.csv`, `check-ins-v3-fields.md`, and `check-ins-v3.trends.md`.

`unsynced-native-check-in-count` is the diagnostic freshness value. `unsynced-check-in-count` is a compatibility alias with the same value. `last-synced-check-in-count` is total-reporting evidence only; if `last-synced-native-check-in-count` is absent, native freshness starts from `0` until the first V3 sync. A non-zero value after a normal write is a failed or incomplete refresh, not an acceptable steady state.

Active non-V3 `check-ins.*` indexes are retired. One owner-approved migration archives them only after a successful official V3 sync; canonical daily Markdown and `.assets/` remain in place.
