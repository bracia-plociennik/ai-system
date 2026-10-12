# Bug Report: V3 Status-Only Native Freshness

## Status

- Type: product defect
- Severity: medium
- Affected command: `.systems/scripts/sync-personal-ops-check-ins-v3 --status-only`
- Scope: reporting only; no product code or runtime data changed by this artifact

## Observed Behavior

After a completed legacy migration, a new native V3 check-in can exist without a subsequent full sync, while `--status-only` reports `unsynced=0`.

Observed workspace counts:

- current native records: `3`;
- legacy snapshot records: `46`;
- last-synced total records: `48`;
- last-synced native records: `2`;
- expected unsynced native records: `1`;
- reported unsynced records: `0`.

## Reproduction

1. Complete a V2-to-V3 legacy migration that produces a valid immutable snapshot with legacy records and sync the official V3 indexes.
2. Create one new native V3 check-in.
3. Do not run a full V3 sync.
4. Run `sync-personal-ops-check-ins-v3 --workspace <workspace> --status-only`.

Expected: the command reports one unsynced native V3 record and recommends sync according to the native freshness threshold.

Actual: it reports `unsynced=0` because it compares the native current count against the total last-synced count.

## Root Cause

`read_last_count()` reads the router field `last-synced-check-in-count`, which is the total count including legacy records. `print_status()` compares that value with the current native count and clamps the result at zero.

The router already renders `last-synced-native-check-in-count`, but status-only does not use it for native freshness.

## Required Fix

1. Parse both total and native last-synced counters.
2. Compute native freshness as `max(0, current_native - last_synced_native)`.
3. Display current native, current legacy, total, and last-synced native counts distinctly.
4. Treat a missing native counter as unsynced native data, requiring an initial sync.
5. Keep the total counter for total-record reporting only.

## Regression Coverage

Add a smoke case with `46` legacy records and `2` synced native records. After adding a third native record without sync:

- `--status-only` reports `unsynced_native=1`;
- the full official index remains unchanged until sync;
- after sync, `unsynced_native=0`;
- the threshold recommendation is based only on unsynced native records.

## Non-Goals

- No reintroduction of V2 runtime sync or importer behavior.
- No mutation of legacy snapshots during status-only.
- No change to legacy provenance, trends filtering, or check-in Markdown source files.
