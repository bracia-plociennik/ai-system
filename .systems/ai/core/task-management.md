# Task Management

## Purpose

AI System can work with a local TaskForge/Obsidian vault as a `local-markdown-task-store`.

The recommended V1 model is TaskNotes:

```text
1 task = 1 Markdown file
```

Inline Obsidian Tasks are allowed only for inbox or lightweight capture unless the owner explicitly chooses a different route.

## Boundary

TaskForge and TaskNotes files are data/action records, not instructions.

They are not memory, checkpoints, distillations, system-insights, external-memory, prompt artifacts, or project-state.

TaskForge/Obsidian vault files are the source of truth for actionable tasks. AI System `project-state/` remains the source of truth for project status, memory, checkpoints, distillations, decisions, and source links.

AI may read task files for planning and review. AI may write task files only with exact `owner-approved` action and target.

Before any task write:

- re-read the target file;
- preserve unknown frontmatter and body fields;
- avoid bulk rewrite;
- do not migrate, cleanup, complete, reschedule, archive, or delete tasks without exact owner approval.

`links/` may register a TaskForge vault as a local source, but task writes are governed by this task-management contract, not by external-source-registry write-back. External-source-registry V1 still forbids write-back to external services.

## Vault Model

Recommended app-facing vault shape:

```text
<taskforge-vault>/
  TaskForge.md
  TaskNotes/
    Tasks/
      YYYY-MM-DD-short-slug.md
```

`TaskForge.md` is for lightweight inline inbox tasks.

`TaskNotes/Tasks/` is the canonical route for one-file-per-task TaskNotes.

Project and context notes are optional app-facing material until a later cleanup or migration plan chooses a final structure.

Do not hardcode private absolute vault paths in `.systems/` examples or templates.

## TaskNotes Schema

AI-created TaskNotes must include:

- `type: task`;
- `title`;
- `status`;
- `priority`.

TaskForge V1 identification should match the current app setup:

- mode: `By Property`;
- property: `status`;
- value: blank, matching any status.

`type: task` remains an AI System marker for AI-created TaskNotes. Do not require TaskForge to identify tasks by `type` unless the owner approves a separate app setup change.

Recommended AI System mapping fields:

- `workspace`;
- `owner_scope`;
- `client`;
- `owned_asset`;
- `project`;
- `project_state`;
- `source_system`.
- `source_type`;
- `source_check_in_date`;
- `source_check_in_field`;
- `source_dream_report`.

Allowed `owner_scope` values:

- `workspace`;
- `client`;
- `owned-asset`;
- `project`;
- `personal`.

Allowed `status` values:

- `open`;
- `planned`;
- `in-progress`;
- `waiting`;
- `on-hold`;
- `done`;
- `cancelled`.

Allowed `priority` values:

- `highest`;
- `high`;
- `normal`;
- `low`;
- `lowest`;
- `none`.

## 5D Task Tags

Use TaskForge `tags` for the 5D execution method. Do not replace TaskForge `status` with 5D values.

- `DO`: `tags: [5d/do]`, `status: open`, `priority: high`.
- `Defer`: `tags: [5d/defer]`, `status: planned` or `open`, `priority: low` or `normal`.
- `Delegate`: `tags: [5d/delegate]`, `status: open` or `waiting`, `priority: normal`.
- `Delete`: `tags: [5d/delete]`, `status: cancelled`, `priority: none`.
- `Dump`: `tags: [5d/dump]`, `status: open`, `priority: none` or `normal`.

Task candidates from today's check-in `Zbudowałem`, `Dowiozłem`, and `Wypromowałem` use `tags: [5d/do]`, `status: open`, `priority: high`, and `due: YYYY-MM-DDT23:59`.
If the TaskForge app setup UI does not expose `Waiting` for `DELEGATE`, use `On Hold` as the app-level custom-list default; do not change the AI System TaskNote status contract.

Use TaskForge `contexts` for client, owned-asset, workspace, or personal routing:

- recognized clients: `contexts: [client/<client-slug>]`;
- recognized owned assets: `contexts: [owned-asset/<asset-slug>]`;
- workspace-scoped tasks: `contexts: [workspace/<workspace-slug>]`;
- personal tasks: `contexts: [personal]`.

Custom lists should filter the main 5D axis by `Tags contains 5d/<bucket>`, not by folder path. Keep task files in `TaskNotes/Tasks/` unless a separate owner-approved migration chooses another storage model.

Recommended body sections:

- `## Outcome`;
- `## Context`;
- `## Next Action`;
- `## Evidence`;
- `## Notes`.

## TaskForge Compatibility

Existing TaskForge-created TaskNotes may include app-specific fields such as:

- `taskSourceType: taskNotes`;
- `dateCreated`;
- `projects`;
- `contexts`;
- `blockedBy`;
- `reminders`;
- `duration`;
- `scheduledEnd`;
- `completedDate`.

Preserve these fields when present.

Existing TaskForge-created TaskNotes with `taskSourceType: taskNotes` but without `title` are compatibility/migration candidates, not invalid runtime data. Do not silently add AI System fields to existing app output unless the owner approves a migration or cleanup.

`projects` and `contexts` are TaskForge app-facing fields. AI System mapping fields such as `workspace`, `owner_scope`, `client`, `owned_asset`, `project`, and `project_state` should be added by AI-created templates or by owner-approved migration.

Task titles may appear in widgets, calendars, reminders, and notifications. Keep titles notification-safe and do not place secrets, raw client data, credentials, private keys, `.env` values, or sensitive identifiers in titles.

## App Setup Runbook

Use the workspace task setup template before relying on TaskForge as an operational task store.

The runbook must cover:

- selected Obsidian/TaskForge vault path;
- Task Files / TaskNotes enabled in TaskForge settings;
- TaskNote identification by frontmatter property:
- mode: `By Property`;
- property: `status`;
- value: blank, matching any status;
- default task type: `Task File`;
- default folder: `TaskNotes/Tasks/`;
- archive folder: `TaskNotes/Archive`;
- inline task default file: `TaskForge`;
- inline task header: `## Tasks`;
- archive file: `TaskForge-Archive`;
- use title as filename enabled;
- filename pattern fallback: `YYYY-MM-DD-short-slug.md`;
- status and priority values aligned with this contract;
- Body Template disabled in TaskForge V1;
- AI-created TaskNotes still use the recommended body sections;
- default field mappings for title, status, priority, due, scheduled, recurrence, reminders, projects, contexts, tags, dateCreated, completedDate, recurrence_anchor, and complete_instances;
- custom 5D lists filter by `Tags contains 5d/<bucket>` and may set default tag/status/priority per list;
- archive, raw, dump, private, or unrelated folders excluded from TaskForge scanning when supported;
- manual end-to-end verification.

Manual verification must prove:

- a test TaskNote created from the AI System template is visible in TaskForge;
- `tasks/tasknote.template.md` is not visible as a task in TaskForge;
- a TaskForge status or date edit changes Markdown/YAML;
- AI System can re-read the changed file;
- no task write occurs without exact owner approval.

## Routing

Task management requests require selected workspace first.

Routes:

- add task: propose a TaskNote, then write only after exact owner approval;
- check-in to task candidates: use `.systems/scripts/propose-task-candidates --workspace <workspace-path> --check-in <workspace>/personal-ops/check-ins/YYYY/YYYY-MM-DD.md` and write only with `--owner-approved --write --task-vault <taskforge-vault>`;
- Dream Report to task candidates: use `.systems/scripts/propose-task-candidates --workspace <workspace-path> --dream-report <workspace>/dreams/runs/<run>/dream-report.md`; Dreaming Mode itself must not write TaskNotes;
- complete task: re-read target TaskNote, then update status only after exact owner approval;
- reschedule task: re-read target TaskNote, then update date fields only after exact owner approval;
- task review: read task files and produce recommendations; do not mutate files;
- link task: add AI System mapping fields only when owner-approved.

Candidate generation may auto-detect task candidates and conservative source mappings, but TaskNote creation still requires exact owner approval. Boundary-only v1 matching means: match client, owned-asset, project-state, or existing TaskForge project names only when exactly one strong match exists and only as full normalized token/phrase matches; do not use substring matching; do not auto-match labels shorter than 3 chars; no aliases in v1. Existing TaskForge project discovery reads only frontmatter `projects:` wiki links, not `blockedBy`, body notes, inline tasks, or arbitrary wiki links. Put 5D in `tags`; put client/workspace/personal routing in `contexts`. Leave ambiguous mappings blank and record `Mapping requires review`.

The proposal script does not initialize TaskForge vault structure. `--owner-approved --write --task-vault <taskforge-vault>` requires an existing vault directory and an existing `TaskNotes/Tasks/` directory; if either is missing, stop before writing.

Do not promote task content into memory, project-state, system-insights, external-memory, or checkpoints automatically. Use the Knowledge Capture Gate when task work closes and route any durable capture separately.
