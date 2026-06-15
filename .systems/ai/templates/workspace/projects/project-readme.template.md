# <Project>

## Purpose

Project source or materials folder for `<Project>`.

This folder may be a git repository, source tree, export folder, or owner-approved material folder.

## AI System State

Store AI System runtime state outside this folder by default:

```text
<workspace>/project-state/<project-slug>/
```

Use that project-state entry for:

- status;
- memory;
- checkpoints;
- distillations;
- decisions;
- links to this source path.

If this folder is a git worktree, ask before colocating AI System runtime files here. Do not auto-edit `.gitignore` or `.git/info/exclude`.
