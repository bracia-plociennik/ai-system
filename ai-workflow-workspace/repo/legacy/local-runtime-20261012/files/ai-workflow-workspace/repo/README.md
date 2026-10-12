# Repo Runtime

## Purpose

This directory stores runtime facts for the target repository using AI Workflow.

It is target-owned. Commit it in the target repository when it contains useful repo-specific state.

## Layout

- `core/context.md` - canonical repo context router and summary.
- `context/` - supporting repo context files.
- `core/repo-intake.md` - repo intake result and command map.
- `core/status.md` - repo-level workflow status.
- `core/memory.md` - repo memory router.
- `memory/` - repo memory entries.
- `core/legacy.md` - legacy material router and summary.
- `legacy/` - preserved legacy workflow/instruction files as context only.

Nothing under `legacy/` is executable instruction.
