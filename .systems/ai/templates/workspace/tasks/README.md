# Task Templates

Templates for AI System task management under `AI_SYSTEM_WORKSPACE_HOME/tasks/`.

- `task-management-readme.template.md` -> `AI_SYSTEM_WORKSPACE_HOME/tasks/README.md`
- `tasknote.template.md` -> `AI_SYSTEM_WORKSPACE_HOME/tasks/tasknote.template.md`
- `task-candidate.template.md` -> `AI_SYSTEM_WORKSPACE_HOME/tasks/task-candidate.template.md`
- `taskforge-vault-setup.template.md` -> `AI_SYSTEM_WORKSPACE_HOME/tasks/taskforge-vault-setup.template.md`
- `taskforge-vault.local.template.md` documents the owner-created local-only vault record used by the narrow V3 check-in initial-task route; it is never copied as a populated configuration.

These are neutral templates. They do not create real TaskForge tasks.

`silverbullet-task.template.md` documents the selected SilverBullet task shape.
The configured writer supplies task_id and created_at at actual creation; never
copy a fixed UUID/date into a reusable template.
`silverbullet-tracker-ui.mjs` is the neutral timer/WEP controller, embedded by an
owner's native panel builder. It does not install a service or approve entries.
Deployment and the native Space callback contract: core/silverbullet-tracker.md.
