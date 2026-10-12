# Phase 0 Project Context Repo Intake - AI System

## Scope

This intake reviews the current `ai-workflow` repository as the implementation environment for the future `ai-system` variant.

## Repo Facts

- Current repository is the official upstream AI Workflow repository.
- Current branch observed during planning: `dev`.
- Official repo mode has no inner `ai-workflow/` directory.
- Repo-local runtime exists under `ai-workflow-workspace/`.
- Active project is now `ai-system`.

## Safe Commands

Use the existing workflow validation commands:

```sh
git diff --check
.systems/scripts/validate-workflow
.systems/scripts/check-naming
.systems/scripts/check-required-artifacts
.systems/scripts/check-status-consistency
.systems/scripts/check-qa-evidence
```

## Restricted Zones

- Do not write implementation changes before owner starts `phase-4-implementation`.
- Do not create branch `ai-system` before final project closure.
- Do not put real customer data in `.systems/`.
- Do not introduce real API integrations in the first implementation package.

## Warnings

- Untracked `.DS_Store` files exist locally and should be cleaned or ignored before commit work.

## Gate Result

`PASS`

The project can proceed to architecture.

