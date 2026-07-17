# Project State

`project-state/` stores AI System runtime state for projects without writing status, memory, checkpoints, distillations, or decisions into managed project repositories.

Use this namespace for projects whose source lives under `projects/`, client repositories, owned-asset repositories, or other source folders.

## Files

- `project-state.md` - router and index for project state entries.
- `<project-slug>/` - per-project AI System runtime state.

## Rules

- Keep real repositories and source folders in `projects/` or the owner-approved source path.
- Store AI System project status, memory, checkpoints, distillations, Distillation State, decisions, and links here.
- Use `<project>/capture-state/` for per-work implementation capture disposition; do not add `is_distilled` to project source files.
- If a project source path is a git worktree, ask before colocating runtime files there.
- Do not auto-edit `.gitignore` or `.git/info/exclude`.
