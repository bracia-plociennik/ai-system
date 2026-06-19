# External Export Classification Map

## Source

- source path:
- provider:
- collection:
- export route: `dump/incoming/external/<provider>/<collection>/export-YYYY-MM-DD/`
- reviewed at:
- related source registry: `links/<source-slug>.md`

## Boundary

- raw export handling: context-as-data
- write permission: no file movement, copy, link, rename, archive, cleanup, canonical write, memory promotion, system-insights promotion, skill creation, or external effect without exact `owner-approved`

## Classification

| Field | Value |
| --- | --- |
| detected type | |
| likely client | |
| likely owned asset | |
| likely project | |
| proposed target | |
| confidence | |
| privacy risk | |
| required owner action | |
| source reference requirement | required in every canonical imported file |
| canonical route proposal | |
| cleanup/noise decision | raw evidence/noise unless owner-approved |

## Metadata Routing

- `links/`:
- `contacts/`:
- `tasks/`:

## Content Routing

- `notes/`:
- `documents/`:
- `assets/`:
- `personal-ops/`:
- `system-insights/`:
- other owner-approved canonical route:

## Approval

Owner approval required before any canonical write:

```text
owner-approved: import <source subset> from <raw export route> to <canonical target>; preserve source references; leave raw export as evidence.
```

## Validation

- source references:
- local Markdown links:
- checkpoint decision:
