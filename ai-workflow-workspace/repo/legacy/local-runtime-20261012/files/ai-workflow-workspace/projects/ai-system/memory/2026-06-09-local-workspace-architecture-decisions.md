# Local Workspace Architecture Decisions

## Date

2026-06-09

## Summary

The owner accepted a local Mac workspace model named `ai-system`, with private runtime under `~/ai-system/ai-system-workspace/`.

## Source

- `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/distillations/phase-6-ai-system-implementation-package-distillation.md`

## Evidence

- `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/specs/phase-3-ai-system-implementation-package-specification.md`
- `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-5-ai-system-implementation-package-quality.md`
- `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/checkpoints/phase-7-checkpoint-2026-06-09-ai-system-implementation-package.md`

## Durable Decisions

- Use `core/` inside the workspace instead of `repo/`.
- Keep `external-memory/` for development of `ai-system`.
- Keep `system-insights/` for owner competence, offer, process, and work-quality lessons.
- Classify `dump/` files first and require owner approval before moving files.
- Keep real integrations soft through links and manual context in the first implementation package.
- Treat branch migration to the dedicated `ai-system` branch as post-final release work, not as part of the original implementation package.
