# Projects Template

Standalone project repositories, source folders, exported materials, and other project-owned files may live here when they are not nested under a client.

AI System runtime state does not belong here by default. Store project status, memory, checkpoints, distillations, decisions, and source links in:

```text
../project-state/<project-slug>/
```

If a project path is a git worktree, ask before colocating AI System runtime files there. Do not auto-edit `.gitignore` or `.git/info/exclude`.
