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
  - date created: `dateCreated`
  - completed date: `completedDate`
  - recurrence anchor: `recurrence_anchor`
  - complete instances: `complete_instances`
- exclude archive, raw, dump, private, or unrelated folders from scanning when supported

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
