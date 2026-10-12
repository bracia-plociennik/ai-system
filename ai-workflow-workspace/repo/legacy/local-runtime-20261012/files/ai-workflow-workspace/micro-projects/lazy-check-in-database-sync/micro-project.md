# Fix: Lazy Sync For Manual Check-Ins And Derived Database

## Summary
- Manual check-in should create only the canonical daily Markdown artifact and optional `YYYY-MM-DD.assets/`.
- Derived databases/indexes should not be updated after every manual check-in.
- Add lightweight sync evidence/counter so AI System can recommend database sync after 7 unsynced check-in artifacts, or run sync earlier with exact `owner-approved`.

## Key Changes
- Add a Markdown reindex/sync tool, but make it explicit and opt-in:
  - `.systems/scripts/sync-personal-ops-check-ins`
  - reads canonical Markdown check-ins;
  - regenerates only derived indexes: `check-ins.csv`, `check-ins.jsonl`, `check-ins.metrics.csv`, `check-ins-fields.md`;
  - never rewrites daily Markdown or assets;
  - supports `--workspace <path>`, `--dry-run`, and normal owner-approved execution.

- Add lazy sync state to `personal-ops/indexes/check-ins.md`:
  - `last-synced-at`;
  - `last-synced-check-in-count`;
  - `current-check-in-count`;
  - `unsynced-check-in-count`;
  - `sync-recommendation-threshold: 7`;
  - `last-sync-source: manual|notion-import|owner-approved-sync`;
  - short evidence list of latest unsynced dates.
- Counting rule:
  - count daily files matching `personal-ops/check-ins/YYYY/YYYY-MM-DD.md`;
  - ignore `README.md`, `import-profiles/`, `*.assets/`, and non-daily Markdown;
  - unsynced count = current daily check-in count minus last synced check-in count.
- Recommendation rule:
  - after manual check-in write, AI System checks the counter/read-only state;
  - if `unsynced-check-in-count >= 7`, recommend sync;
  - if `< 7`, report that derived indexes are intentionally stale and sync is not required yet;
  - exact `owner-approved` sync can run anytime, regardless of threshold.

- Manual check-in flow:
  - ask brief from `manual-daily-check-in.md`;
  - write `YYYY/YYYY-MM-DD.md` and optional `YYYY-MM-DD.assets/` only after approval;
  - update or report sync evidence/counter, not the full database;
  - do not run database sync automatically unless owner explicitly says `owner-approved: synchronizuj bazę check-inów`.

- Notion import flow:
  - may still regenerate indexes as part of import because it is already a batch/database operation;
  - after Notion import, update the sync state in `check-ins.md`;
  - do not use Notion importer to refresh manual-only edits.

## Validation
- Add validator/smoke coverage:
  - manual check-in creation does not require immediate index regeneration;
  - sync counter detects unsynced daily Markdown files;
  - after 6 unsynced check-ins, recommendation is “not required yet”;
  - after 7 unsynced check-ins, recommendation is “recommend sync”;
  - exact owner-approved sync regenerates CSV/JSONL/metrics even below threshold;
  - sync tool does not modify daily Markdown or assets;
  - malformed Markdown fails sync without replacing existing indexes;
  - existing Notion import tests continue to pass.

- Required final checks:
  ```sh
  git diff --check
  .systems/scripts/check-personal-ops
  .systems/scripts/check-required-artifacts
  .systems/scripts/check-validator-smoke-tests
  .systems/scripts/validate-ai-system
  ```

## Assumptions
- The derived database is allowed to be stale by design.
- `personal-ops/indexes/check-ins.md` is the right place for sync state because it is the index router/evidence file.
- Real workspace indexes should not be migrated or synced during product implementation; running sync against real workspace is a separate exact owner-approved runtime action.
