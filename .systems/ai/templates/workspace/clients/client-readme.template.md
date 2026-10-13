# <Client>

## Purpose

Client workspace for `<Client>`.

## Directories

- `context/`
- `dump/`
- `memory/`
- `checkpoints/`
- `distillations/`
- `capture-state/`
- `contacts/`
- `projects/`
- `project-state/`
- `documents/`
- `contracts/`
- `assets/`
- `links/`
- `notes/`
- `decisions/`
- `tasks/`
- `archive/`

## Privacy

This workspace may contain client-specific data. Do not promote raw content to `system-insights`.

## Client Dump

Use `dump/incoming/` for files already known to belong to this client.

Files in client dump still require classification before movement into `documents/`, `assets/`, `projects/`, `contracts/`, `memory/`, or `archive/`.

Use `project-state/<project>/` for AI System client-project status, memory, checkpoints, distillations, decisions, and source links when `projects/<project>/` is a canonical git repo. Auxiliary worktrees use the approved collection `.worktrees/`; disposable task files use `.tmp/`. Existing source-material folders remain preserved until an approved relocation.

Use `capture-state/` for client-level implementation Distillation State and `project-state/<project>/capture-state/` for project work. State records contain paths and disposition only, never raw client data.

Use `.systems/ai/core/task-management.md` before routing client tasks into TaskForge or TaskNotes. Task files are action records and do not replace client memory, project-state, decisions, or owner approvals.
