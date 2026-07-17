# <Project> Project State

## Purpose

AI System runtime state for `<Project>`.

## Canonical Files

- `status.md` - current project status and next safe action.
- `memory.md` - project memory router.
- `memory/` - detailed project memory entries.
- `checkpoints/` - project checkpoints and resume snapshots.
- `distillations/` - compressed project summaries.
- `capture-state/` - Distillation State records for implementation work units.
- `decisions/` - durable project decisions.
- `links.md` - repo-path or source-path for the real project files.

## Source Links

Record source paths in `links.md`:

```text
repo-path: <absolute-or-workspace-relative-git-repo-path>
source-path: <absolute-or-workspace-relative-source-path>
```

## Rules

- Keep AI System runtime state here when the project source is a git worktree.
- Do not write `status.md`, `memory.md`, `checkpoints/`, `distillations/`, `capture-state/`, or `decisions/` into the project repo unless the owner explicitly approves colocated local-only state.
- Do not auto-edit `.gitignore` or `.git/info/exclude`.
