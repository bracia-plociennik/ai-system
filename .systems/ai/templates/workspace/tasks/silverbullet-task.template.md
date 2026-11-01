# SilverBullet task example

New-task shape; do not scan this template as a task. Use the configured writer. It supplies task_id (UUID) and created_at (UTC) at actual creation. Never hardcode identity in a reusable template.

```markdown
---
type: task
author: human
title: "Example task"
status: open
priority: high
client: ""
project: ""
category: "do"
scheduled: ""
---
# Example task
- Category: do
- DoD:
- Deadline:

## Checkpoint OSNR
- O — Outcome:
- S — Status:
- N — Next:
- R — Resume:

## TODO
- [ ] First step

## Evidence

## Working dump
```

This manual-copy example uses author human. The AI task-store writer assigns ai; later edits preserve the creator.
