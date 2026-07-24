# Task Candidate Template

This is a proposal artifact, not a TaskForge TaskNote.

Use it when converting a check-in or Dream Report into owner-approved task proposals.

## Source

- source_type: `<check-in|dream-report|weekly-plan>`
- source_path: `<path>`
- source_field: `<Zbudowałem|Dowiozłem|Wypromowałem|owner decision queue>`

## Proposed TaskNote

- title: `<notification-safe task title>`
- status: `<open|planned|waiting|cancelled>`
- priority: `<high|normal|low|none>`
- task_method: `<legacy-5d|6d|none>`
- execution_bucket: `<do|defer|delegate|delete|dump|done|unclassified>`
- 6d_tag: `<6d/do|6d/defer|6d/delegate|6d/delete|6d/dump>`
- contexts: `<client/client-slug|owned-asset/asset-slug|workspace/workspace-slug|personal>`
- due: `<YYYY-MM-DDT23:59|blank>`
- scheduled: `<YYYY-MM-DD|blank>`
- owner_scope: `<workspace|client|owned-asset|project|personal>`
- client: `<blank-or-client-slug>`
- owned_asset: `<blank-or-owned-asset-slug>`
- project: `<blank-or-project-slug>`
- project_state: `<blank-or-project-state-path>`
- source_week_id: `<blank-or-week-id>`
- source_week_item_id: `<blank-or-weekly-item-id>`
- estimated_minutes: `<blank-or-minutes>`
- planned_allocations_json: `<blank-or-JSON-array>`

## Mapping Evidence

- match_result: `<exact|ambiguous|none>`
- mapping_note: `<Mapping requires review|blank>`

## Owner Decision

- decision: `<approve-write|revise|reject|defer>`
- approved_target_vault: `<TaskForge vault path>`
