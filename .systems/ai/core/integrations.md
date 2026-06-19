# Soft Integrations

## Purpose

AI System v1 does not write to Mail, Notion, Google Drive, Google Sheets, Notes, or other external services.

Provider-agnostic source metadata belongs in `links/<source-slug>.md` under the selected workspace or nearest owner namespace. Use `.systems/ai/core/external-source-registry.md`.

## Allowed

- links;
- external source registry files in `links/`;
- exported notes;
- manual external export import workflow artifacts governed by `.systems/ai/core/external-export-import-workflow.md`;
- exported Notion daily check-in CSV files routed through `dump/incoming/external/notion/check-ins/`;
- manual daily check-in profiles routed through `personal-ops/check-ins/import-profiles/`;
- copied snippets supplied by the owner;
- manual summaries;
- file references.

## Forbidden In V1

- API writes;
- automatic sync;
- sending emails or notifications;
- deleting, archiving, sharing, or changing permissions;
- changing external tasks, pages, documents, spreadsheets, or files.

## Read-Only API Planning

Registry entries may use `allowed-operation: read-only-api-planned` to reserve future connector intent.

This does not implement connectors, OAuth, token storage, live sync, or write-back.

## Check-In Mapping

Daily check-in exports from Notion are manual, local inputs in v1.

Use `.systems/ai/core/personal-ops.md` for manual daily check-ins and `.systems/scripts/map-notion-check-ins` to map owner-approved CSV exports into canonical Markdown under `personal-ops/check-ins/` and derived indexes under `personal-ops/indexes/`.

The mapping does not write back to Notion and does not promote check-in content into memory, checkpoint, distillation, external-memory, or system-insights.

The Notion check-in mapper is not a refresh path for manual-only edits. Use `.systems/scripts/sync-personal-ops-check-ins` for derived index refresh from canonical Markdown.

Manual check-ins do not regenerate derived indexes automatically. Use `.systems/scripts/sync-personal-ops-check-ins --workspace <workspace> --status-only` for lazy sync state and exact owner-approved sync for regeneration.

## External Export Imports

For mixed exports from Notion, Google Drive, Google Sheets, or local folders, use `.systems/ai/core/external-export-import-workflow.md`.

Raw exports stay under `dump/incoming/external/<provider>/<collection>/export-YYYY-MM-DD/`. Source registry records stay in `links/<source-slug>.md`. Classification maps are read-only proposals until exact owner approval.
