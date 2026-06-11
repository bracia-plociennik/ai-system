# <Owned Asset>

## Entity

- Type: `<owned-company|personal-brand|owned-product|owned-offer|owned-asset>`
- Slug: `<owned-asset-slug>`
- Owner: `<owner-slug>`
- Status: `initialized`

## Purpose

Owned-asset workspace for `<Owned Asset>`.

Treat this as an owner-controlled asset with the same operational rigor as a client workspace, but do not classify it as an external client.

## Boundaries

- Owned-asset materials belong here.
- Private owner context belongs in `<workspace>/humans/` or workspace memory.
- External client materials belong in `<workspace>/clients/`.
- Cross-client or cross-asset lessons promoted from this workspace must be anonymized before entering `system-insights/`.

## Core Files

- `status.md` - current asset status.
- `memory.md` - owned-asset memory router.

## Directories

- `context/`
- `dump/`
- `memory/`
- `checkpoints/`
- `distillations/`
- `contacts/`
- `projects/`
- `documents/`
- `contracts/`
- `assets/`
- `links/`
- `notes/`
- `decisions/`
- `tasks/`
- `archive/`

## Privacy

This workspace may contain private owner-controlled business or brand data. Do not promote raw content to `system-insights`.

## Owned Asset Dump

Use `dump/incoming/` for files already known to belong to this owned asset.

Files in owned-asset dump still require classification before movement into `documents/`, `assets/`, `projects/`, `contracts/`, `memory/`, or `archive/`.
