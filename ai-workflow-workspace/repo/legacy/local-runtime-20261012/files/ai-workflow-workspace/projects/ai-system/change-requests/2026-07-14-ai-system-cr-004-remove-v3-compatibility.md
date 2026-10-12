# ASYS-CR-004 Remove V3 Compatibility

## Metadata

| Field | Value |
| --- | --- |
| Change request ID | `ASYS-CR-004-remove-v3-compatibility` |
| Project | `ai-system` |
| Date | `2026-07-14` |
| Timing | `post-final-approval` |
| Type | `defect` |
| Risk | `medium` |
| Status | `deferred` |
| Routing | `new-project-iteration` |

## Owner Request

Remove backward compatibility for V3 in the AI System development contract. V2 remains the only historical compatibility path. Do not modify existing runtime V3 reports; the owner will migrate the July 14 report independently.

## Reconciliation

This request is retained as historical evidence but is superseded by the later owner decision to preserve V3 compatibility projections and continue the V2/V3 history. No migration or runtime rewrite was performed.

## Scope

- Make `index_contract: 3` properties strict for the current V3 contract only.
- Remove `must-do`, `legacy-wig-priority`, and `legacy-v3-no-wig` from active V3 schema, task generation, documentation, validators, and smoke fixtures.
- Restrict the historical `check-ins.*` synchronizer to V2 files.
- Reject a V3 check-in that does not use the current `index_contract: 3` route for V3 TaskNote generation.

## Out Of Scope

- No migration, rewrite, deletion, or sync of existing runtime V3 reports.
- No V2 canonical Markdown or V2 index semantic change.
- No TaskForge vault writes or TaskNote changes.

## Acceptance Criteria

- Current V3 reports always use `all-professional-do-v1` and contain no `must_do_plan_item_ids_json`.
- Historical sync ignores every `schema_version: 3` file.
- Legacy V3 check-ins are not accepted by the V3 TaskNote route.
- V2 remains supported and validated.
