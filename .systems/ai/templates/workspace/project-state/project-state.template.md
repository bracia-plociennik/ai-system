# Project State Router

`AI_SYSTEM_WORKSPACE_HOME/project-state/project-state.md` indexes AI System runtime state for projects.

Detailed project state lives under `AI_SYSTEM_WORKSPACE_HOME/project-state/<project-slug>/`.

## Index

| Project | Status | Source route | State route | Updated |
| --- | --- | --- | --- | --- |
| n/a | n/a | n/a | n/a | n/a |

## Rules

- `projects/` contains canonical owner repositories. Auxiliary worktrees use `.worktrees/`; disposable task files use `.tmp/` under `workspace-directory-layout.md`. Existing materials are preserved until explicit relocation approval.
- `project-state/` stores AI System runtime state.
- Use `links.md` inside each project-state entry to point to the real repo or source folder.
- Before writing runtime files into a git worktree, ask the owner to choose `project-state/` or colocated local-only state with exact approval.
