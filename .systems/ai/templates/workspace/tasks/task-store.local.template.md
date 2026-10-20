# Local Markdown task store

Copy to tasks/task-store.local.md only for an explicitly approved selection.
This neutral config takes precedence over the historical TaskForge config.

```yaml
---
schema_version: 1
enabled: false
profile: silverbullet-v1
vault_path: ${AI_SYSTEM_WORKSPACE_HOME}/tasks/silverbullet
---
```

The vault and its tasks subtree must already exist. Shared stores can use an
approved ${AI_SYSTEM_HOME} or ${HOME} root expression. No UI/server or secret is
required. No automatic migration, initialization or fallback on explicit failure.
