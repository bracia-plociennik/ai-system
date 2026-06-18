# Soft Integrations

## Purpose

AI System v1 does not connect to Mail, Notion, Google Drive, Notes, or other services through APIs.

## Allowed

- links;
- exported notes;
- exported Notion daily check-in CSV files routed through `dump/incoming/external/notion/check-ins/`;
- copied snippets supplied by the owner;
- manual summaries;
- file references.

## Forbidden In V1

- API writes;
- automatic sync;
- sending emails or notifications;
- changing external tasks, pages, documents, or files.

## Check-In Mapping

Daily check-in exports from Notion are manual, local inputs in v1.

Use `.systems/ai/core/personal-ops.md` and `.systems/scripts/map-notion-check-ins` to map owner-approved CSV exports into canonical Markdown under `personal-ops/check-ins/` and derived indexes under `personal-ops/indexes/`.

The mapping does not write back to Notion and does not promote check-in content into memory, checkpoint, distillation, external-memory, or system-insights.
