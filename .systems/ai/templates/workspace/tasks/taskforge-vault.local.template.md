# Local TaskForge Vault Configuration

This is a copyable local-only configuration shape. Do not create a populated configuration automatically and do not commit a private vault path.

```yaml
---
enabled: false
vault_path: /absolute/private/path/to/taskforge-vault
---
```

Store an owner-approved populated copy only at `tasks/taskforge-vault.local.md`. V3 check-in task generation reads this record only for an owner-approved canonical V3 check-in write and requires an existing `TaskNotes/Tasks/` directory.
