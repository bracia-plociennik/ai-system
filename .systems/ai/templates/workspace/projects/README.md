# Projects Template

Only canonical owner project repositories belong here when they are not nested
under a client. Auxiliary worktrees use the selected collection root
`.worktrees/<repository-id>/<work-id>/`; disposable task files use `.tmp/<work-id>/`.
See `.systems/ai/core/workspace-directory-layout.md`. Source imports and materials
follow their existing dump/context/document routes. Preserve existing materials
and historical QA; no automatic migration or deletion.

AI System runtime state does not belong here by default. Store project status, memory, checkpoints, distillations, decisions, and source links in:

```text
../project-state/<project-slug>/
```

If a project path is a git worktree, ask before colocating AI System runtime files there. Do not auto-edit `.gitignore` or `.git/info/exclude`.
