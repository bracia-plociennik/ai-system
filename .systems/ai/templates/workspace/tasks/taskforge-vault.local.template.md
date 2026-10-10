# Local TaskForge Vault Configuration

This is a copyable local-only configuration shape. Do not create a populated configuration automatically and do not commit a private vault path.

```yaml
---
enabled: false
vault_path: /absolute/private/path/to/taskforge-vault
---
```

Store an owner-approved populated copy only at `tasks/taskforge-vault.local.md`. Dry-run task proposals may read this record to discover TaskForge project values; missing, disabled, or invalid configuration produces a warning without blocking the proposal. V3 check-in task generation requires an owner-approved canonical write and an existing `TaskNotes/Tasks/` directory.

The store is Markdown; TaskForge is optional UI. An approved populated `vault_path`
may use `${AI_SYSTEM_HOME}/<workspace>/tasks`, `${HOME}/...` or `~/...` under
`local-paths.md`. Expansion produces an absolute local path and does not initialize
the directory, create tasks or grant write permission.
