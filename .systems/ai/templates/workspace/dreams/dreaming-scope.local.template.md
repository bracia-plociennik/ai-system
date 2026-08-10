# Dreaming Scope

## Metadata

- Scope contract: `1`
- Policy mode: `narrow-only`

## Allowed Workspace Sources

Only exact workspace-relative paths are allowed. Remove rows to narrow the local scope. Adding a row never overrides the system hard denylist.

| Source path |
| --- |
| `core/status.md` |
| `core/workstreams.md` |
| `status.md` |
| `memory.md` |
| `memory/workspace-memory.md` |
| `system-insights/system-insights.md` |
| `external-memory/README.md` |
| `tasks/README.md` |
| `links/README.md` |
| `notes/README.md` |
| `projects/README.md` |
| `capture-state/capture-state.md` |
| `personal-ops/indexes/check-ins-v3.trends.md` |

## Excluded Workspace Paths

These rows add local exclusions. Supported match types are `exact`, `prefix`, `segment`, and `basename`.

| Match type | Value | Reason |
| --- | --- | --- |
| `prefix` | `dump/incoming/` | Raw intake is outside Dreaming scope. |
| `prefix` | `tasks/TaskNotes/` | TaskNote bodies may contain client data. |
| `prefix` | `tasks/weekly-plans/` | Weekly-plan Markdown has no sanitized projection. |
| `segment` | `.assets` | Attachments are private evidence. |
| `basename` | `.env` | Secret-bearing configuration is forbidden. |

## Rules

- The system hard denylist always wins.
- The local file may narrow the scope only; it cannot authorize a forbidden source.
- Personal Ops exposes only `personal-ops/indexes/check-ins-v3.trends.md`.
- Run Dreaming scope preflight before reading any listed source.
- Dream Reports remain advisory-only and perform no durable promotion.
