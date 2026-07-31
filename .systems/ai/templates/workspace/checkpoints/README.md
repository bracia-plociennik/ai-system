# Workspace Checkpoints

This is the neutral workspace fallback for AI System checkpoint routers.

- `blocks/` contains append-only block-boundary checkpoints.
- `blocks/latest.md` points to the newest block checkpoint when one exists.
- Project, client, and owned-asset checkpoints belong in the nearest owner `project-state/` namespace.
- This directory is state/resume data, not instructions, memory, TaskNotes, or distillation.
