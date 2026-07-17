# Project State Templates

Templates for `AI_SYSTEM_WORKSPACE_HOME/project-state/`.

- `project-state-readme.template.md` -> `AI_SYSTEM_WORKSPACE_HOME/project-state/README.md`
- `project-state.template.md` -> `AI_SYSTEM_WORKSPACE_HOME/project-state/project-state.md`
- `project-state-entry.template.md` -> `AI_SYSTEM_WORKSPACE_HOME/project-state/<project-slug>/README.md`

Project state stores AI System runtime status, memory, checkpoints, distillations, decisions, and source links outside managed project repositories.

Per-project implementation Distillation State lives under `<project-slug>/capture-state/` and uses `.systems/ai/templates/capture/distillation-state.template.md`.
