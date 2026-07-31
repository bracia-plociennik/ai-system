# Project State

## Purpose

`project-state/` stores AI System runtime state for projects without writing status, memory, checkpoints, distillations, or decisions into managed project repositories.

Use this contract whenever a workspace project points to a git worktree, product repository, client repository, or source-material folder that should remain clean.

## Canonical Locations

Standalone workspace projects use:

```text
AI_SYSTEM_WORKSPACE_HOME/project-state/<project-slug>/
  status.md
  memory.md
  memory/
  checkpoints/
    blocks/
      latest.md
  distillations/
  capture-state/
  decisions/
  links.md
```

Client projects use the nearest owner namespace:

```text
AI_SYSTEM_WORKSPACE_HOME/clients/<client>/project-state/<project-slug>/
```

Owned-asset projects use:

```text
AI_SYSTEM_WORKSPACE_HOME/owned-assets/<asset>/project-state/<project-slug>/
```

`links.md` records the real project source location:

- `repo-path` for git repositories;
- `source-path` for non-repo material folders;
- optional source notes and review triggers.

## Projects Directory Boundary

`projects/` may contain product repositories, client repositories, cloned repos, source folders, exported materials, or other project-owned files.

Do not assume `projects/<project-slug>/` is safe for AI System runtime files.

Do not write these AI System runtime artifacts into a project path unless the owner explicitly approves colocated local-only state:

- `status.md`;
- `memory.md`;
- `memory/`;
- `checkpoints/`;
- `distillations/`;
- `capture-state/`;
- `decisions/`.

## Git Worktree Guard

Before writing AI System project state into any project path, check whether the path is inside a git worktree.

If the project path is inside a git worktree, ask the owner to choose one of:

1. Recommended: write AI System state under `project-state/<project-slug>/` and keep the repository clean.
2. Colocated local-only: write beside the repo files only after exact `owner-approved` scope and a local `.git/info/exclude` update for the affected runtime paths.

Do not automatically edit `.gitignore` or `.git/info/exclude`.

Do not add AI System runtime files to a managed project commit.

## Runtime Creation

`init-workspace` and `update-workspace` may create only the neutral project-state namespace:

```text
AI_SYSTEM_WORKSPACE_HOME/project-state/README.md
AI_SYSTEM_WORKSPACE_HOME/project-state/project-state.md
```

Per-project state directories require exact owner-approved target scope.

When creating a per-project state entry, use `.systems/ai/templates/workspace/project-state/project-state-entry.template.md` and create the project state directories listed in this contract.

## Cleanup And Migration

If AI System runtime files already exist inside a managed project repository, do not delete or move them automatically.

Prepare a cleanup plan that lists:

- source files to migrate;
- destination under `project-state/<project-slug>/`;
- whether each source is tracked, untracked, or ignored;
- exact owner-approved move and cleanup commands required later.

Cleanup is separate from contract implementation.

## Dream Reports

Dreaming Mode may recommend project-state, status/evidence, decision, checkpoint, or project-memory updates in a Dream Report.

Those recommendations are advisory only. Do not mutate `project-state/` from Dreaming Mode; use the normal project-state route with exact owner-approved scope.

Project implementation Distillation State belongs in `project-state/<project>/capture-state/`, not in the managed project repository. Use `.systems/ai/core/distillation-state.md`; the state record stores paths and disposition, not raw project content.

## Block Checkpoints

Block-boundary checkpoints use `checkpoints/blocks/` within the nearest project, client, or owned-asset project-state namespace. Use `.systems/ai/core/block-checkpoint.md` for their contract. They are append-only resume records; `latest.md` is only a pointer to the newest record. The fallback workspace namespace is `<workspace>/checkpoints/blocks/`, whose neutral routers may be created by `init-workspace` and `update-workspace`. These records do not replace project status, memory, distillation state, or TaskNotes.
