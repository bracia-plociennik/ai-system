# TaskForge Vault Setup

Use this runbook before relying on TaskForge as an operational task store.

## Vault

- vault-path: `<private-local-path>`
- source-of-truth: `local-markdown-task-store`
- canonical-task-format: `TaskNotes`
- inline-tasks: `inbox/lightweight-capture-only`

## TaskForge App Settings

### Vault & Storage

- connect TaskForge to the selected Obsidian vault
- set Vault Location to the selected vault path
- configure Task Locations in Task Defaults

### Task Defaults

- Default Quick Add Date Type: `Due Date`
- Default Quick Add List: `None`
- Include Created Date: `on`
- Inherit Dates on Subtasks: `off`
- Tasks Overdue on Due Date: `off`
- Default Task Type: `Task File`

### Inline Tasks

- Use Daily Note as Default: `off`
- Default File: `TaskForge`
- New Tasks Header: `## Tasks`
- Archive in same file: `off`
- Default Archive File: `TaskForge-Archive`

### Task Files

- enable Task Files / TaskNotes
- default TaskNotes folder: `TaskNotes/Tasks/`
- archive folder for completed tasks: `TaskNotes/Archive`
- Task identification:
  - mode: `By Property`
  - property: `status`
  - value: `<blank>` to match any status
- Use Title as Filename: `on`
- filename pattern fallback if title filename is disabled: `YYYY-MM-DD-short-slug.md`
- allowed statuses: `open`, `planned`, `in-progress`, `waiting`, `on-hold`, `done`, `cancelled`
- allowed priorities: `highest`, `high`, `normal`, `low`, `lowest`, `none`
- Use Body Template: `off` in V1
- AI-created TaskNotes still use body sections: `Outcome`, `Context`, `Next Action`, `Evidence`, `Notes`
- Optional TaskNotes plugin import path: `.obsidian/plugins/tasknotes/data.json`
- field mappings should keep defaults unless owner approves remapping:
  - title: `title`
  - status: `status`
  - priority: `priority`
  - due date: `due`
  - scheduled date: `scheduled`
  - recurrence: `recurrence`
  - reminders: `reminders`
  - projects: `projects`
  - contexts: `contexts`
  - tags: `tags`
  - date created: `dateCreated`
  - completed date: `completedDate`
  - recurrence anchor: `recurrence_anchor`
  - complete instances: `complete_instances`
- exclude archive, raw, dump, private, or unrelated folders from scanning when supported

### 5D Custom Lists

- `DO`: filter `Tags contains 5d/do`; default tag `5d/do`; default status `open`; default priority `high`
- `DEFER`: filter `Tags contains 5d/defer`; default tag `5d/defer`; default status `planned`; default priority `normal`
- `DELEGATE`: filter `Tags contains 5d/delegate`; default tag `5d/delegate`; default status `waiting`; default priority `normal`
  - TaskForge 2.6.x may show `On Hold` instead of `Waiting`; use `On Hold` as the app-level default only when `Waiting` is unavailable.
- `DELETE`: filter `Tags contains 5d/delete`; default tag `5d/delete`; default status `cancelled`; default priority `none`
- `DUMP`: filter `Tags contains 5d/dump`; default tag `5d/dump`; default status `open`; default priority `none`

Keep `TaskNotes/Tasks/` as the canonical file storage route. Do not use folders such as `DOs/` or `DEFERs/` as the primary 5D classification.

## Manual Verification

- create a real test TaskNote by copying the fenced example from `tasknote.template.md` into `TaskNotes/Tasks/<filename>.md`
- confirm TaskForge sees the task
- edit status or date in TaskForge
- confirm Markdown/YAML changed
- re-read the file through AI System
- confirm no task write occurs without exact owner approval
- confirm `tasks/tasknote.template.md` is not visible as a task in TaskForge

## Boundaries

- no app automation in V1
- no connector/API sync in V1
- no bulk rewrite of the vault
- no migration without a separate owner-approved plan
