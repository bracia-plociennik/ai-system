# Upgrade With Master Prompt Tasks Router

## Purpose

`tasks.md` is the canonical task index and router for this project.

Detailed task cards live in `tasks/`.

Task cards do not replace specifications in `specs/` or QA evidence in `quality/`.

## Task ID Format

`UWMP-<AREA>-<NNN>-<slug>`

## Tasks

Task index state: `done`

| Task ID | Title | Risk | Status | Task Card | Spec | Quality | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `UWMP-SYSTEM-001-prompt-composition-contract` | Milestone 1 Prompt Composition product contract | `high` | `done` | `none` | `ai-workflow-workspace/projects/upgrade-with-master-prompt/specs/phase-3-uwmp-system-001-prompt-composition-contract-specification.md` | `ai-workflow-workspace/projects/upgrade-with-master-prompt/quality/phase-8-final-check.md` | Final owner approval received; new scope requires post-final change request or new owner-approved task/project. |

## Rules

- Keep `tasks.md` as the task index/router.
- An empty task table is valid only before `phase-2-project-plan` is completed.
- After `phase-2-project-plan` is `PASS` or `completed`, add concrete task rows with valid task IDs.
- Store detailed task cards in `tasks/` when extra task-level context is useful.
- Do not store implementation specifications here; use `specs/`.
- Do not store QA evidence here; use `quality/`.
