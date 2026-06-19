# Dump Triage

## Purpose

`dump/` is the owner-controlled inbox for unclassified files.

## Intake Levels

Use `<workspace>/dump/incoming/` when ownership is unknown, mixed, or not yet trusted inside the selected workspace.

Use `<workspace>/dump/incoming/` for files already known to belong to the primary entity when the selected workspace uses a primary-entity root profile.

Use `<workspace>/clients/<client>/dump/incoming/` when the owner already knows the file belongs to that client. Client-level dump may assume `likely-client` is that client, but all other classification fields still need review.

Use `<workspace>/owned-assets/<asset>/dump/incoming/` when the owner already knows the file belongs to that owned asset inside a generic workspace or an explicit sub-asset namespace. Owned-asset-level dump may assume `likely-owned-asset` is that asset, but all other classification fields still need review.

## Flow

1. Owner places files in `<workspace>/dump/incoming/`, `<workspace>/clients/<client>/dump/incoming/`, or `<workspace>/owned-assets/<asset>/dump/incoming/` when that owned-asset namespace exists.
2. AI creates a classification proposal.
3. AI lists recommended target, confidence, risk, and reason.
4. Owner approves with `owner-approved`.
5. Only after approval may AI move, copy, link, rename, or archive files.

## External Export Imports

Manual external exports use `.systems/ai/core/external-export-import-workflow.md`.

Raw exports route to:

```text
<workspace>/dump/incoming/external/<provider>/<collection>/export-YYYY-MM-DD/
```

Use an external export classification map before canonical writes. Source registry records in `links/<source-slug>.md` describe the provider and allowed operation; they are not classification maps and do not authorize import.

Metadata routes separately from content. Metadata targets include `links/`, `contacts/`, and `tasks/`. Content targets include `notes/`, `documents/`, `assets/`, `personal-ops/`, `system-insights/`, or another exact owner-approved canonical route.

Every canonical imported file needs source references. Large imports need local Markdown link validation, validation evidence, and checkpoint decision.

## Required Classification Fields

- source path;
- detected type;
- likely client;
- likely owned asset;
- likely project;
- proposed target;
- confidence;
- privacy risk;
- required owner action.

Client-level dump may prefill `likely client` from its path, but must still classify detected type, likely project, proposed target, confidence, privacy risk, and required owner action.

Primary-entity workspace dump may prefill `likely owned asset` or primary entity from the selected workspace, but must still classify detected type, likely project, proposed target, confidence, privacy risk, and required owner action.

Owned-asset-level dump may prefill `likely owned asset` from its path, but must still classify detected type, likely project, proposed target, confidence, privacy risk, and required owner action.

## Stop Conditions

Stop when the file may contain credentials, legal content, private customer material, ambiguous ownership, or a destructive operation would be needed.
