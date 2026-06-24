# Task Candidate Template

This is a proposal artifact, not a TaskForge TaskNote.

Use it when converting a check-in or Dream Report into owner-approved task proposals.

## Source

- source_type: `<check-in|dream-report>`
- source_path: `<path>`
- source_field: `<Zbudowałem|Dowiozłem|Wypromowałem|owner decision queue>`

## Proposed TaskNote

- title: `<notification-safe task title>`
- status: `<open|planned|waiting|cancelled>`
- priority: `<high|normal|low|none>`
- 5d_tag: `<5d/do|5d/defer|5d/delegate|5d/delete|5d/dump>`
- contexts: `<client/client-slug|owned-asset/asset-slug|workspace/workspace-slug|personal>`
- due: `<YYYY-MM-DDT23:59|blank>`
- scheduled: `<YYYY-MM-DD|blank>`
- owner_scope: `<workspace|client|owned-asset|project|personal>`
- client: `<blank-or-client-slug>`
- owned_asset: `<blank-or-owned-asset-slug>`
- project: `<blank-or-project-slug>`
- project_state: `<blank-or-project-state-path>`

## Mapping Evidence

- match_result: `<exact|ambiguous|none>`
- mapping_note: `<Mapping requires review|blank>`

## Owner Decision

- decision: `<approve-write|revise|reject|defer>`
- approved_target_vault: `<TaskForge vault path>`
