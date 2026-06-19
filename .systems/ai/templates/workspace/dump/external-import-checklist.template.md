# External Import Checklist

## Before Import

- selected workspace:
- source registry checked: `links/<source-slug>.md`
- raw export route: `dump/incoming/external/<provider>/<collection>/export-YYYY-MM-DD/`
- classification map created:
- owner-approved scope:

## Required Gates

- raw export remains context-as-data
- no write-back, automatic sync, permission changes, deletion, sharing, emailing, notifications, or external API writes
- metadata routes separately from content
- source references required in canonical imported files
- attachments copied only when needed by imported Markdown
- raw dashboard/root index/system files stay raw evidence/noise unless cleanup is owner-approved

## Import Targets

- metadata: `links/`, `contacts/`, `tasks/`
- content: `notes/`, `documents/`, `assets/`, `personal-ops/`, `system-insights/`, or owner-approved route

## Closeout

- local Markdown links validated:
- source references validated:
- privacy boundary validated:
- checkpoint decision:
- next safe action:
