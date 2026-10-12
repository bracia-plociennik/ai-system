# Phase 0 Repo Intake - Upgrade With Master Prompt

## Metadata

| Field | Value |
| --- | --- |
| `project` | `upgrade-with-master-prompt` |
| `date` | `2026-06-11` |
| `result` | `PASS` |
| `target-repo-root` | `/Users/jakubplociennik/ai-system` |
| `ai-workflow-home` | `/Users/jakubplociennik/ai-system/ai-workflow` |
| `ai-workflow-workspace-home` | `/Users/jakubplociennik/ai-system/ai-workflow-workspace` |

## Sources Reviewed

- `AGENTS.md`
- `HUMANS.md`
- `README.md`
- `.systems/ai/core/**`
- `.systems/scripts/validate-ai-system`
- `.systems/scripts/check-required-artifacts`
- `.systems/scripts/check-readmes`
- `.systems/scripts/check-privacy-boundary`
- `ai-workflow/AGENTS.md`
- `ai-workflow/.systems/ai/core/workflow.md`
- `ai-workflow/.systems/ai/core/autopilot.md`
- `ai-workflow/.systems/ai/core/prompt-composition.md`
- `ai-workflow/.systems/ai/workflow/phase-0-idea-validation.md`
- `ai-workflow/.systems/ai/workflow/phase-1-architecture.md`
- `ai-workflow/.systems/ai/workflow/phase-1-architecture-qa.md`
- `ai-workflow/.systems/ai/workflow/phase-2-project-plan.md`
- `ai-workflow/.systems/ai/workflow/phase-2-plan-qa.md`
- `ai-workflow/.systems/ai/workflow/phase-2-task-packaging.md`
- `ai-workflow/.systems/ai/workflow/phase-3-specification.md`
- `ai-workflow/.systems/ai/workflow/phase-3-spec-qa.md`
- `ai-workflow/.systems/ai/workflow/phase-4-implementation.md`
- `ai-workflow/.systems/ai/workflow/phase-5-quality.md`
- `ai-workflow/.systems/ai/workflow/phase-6-distillation.md`
- `ai-workflow/.systems/ai/workflow/phase-7-checkpoint.md`
- `ai-workflow-workspace/repo/core/repo-intake.md`
- `ai-workflow-workspace/projects/upgrade-with-master-prompt/**`

## Repository Shape For This Project

| Area | Finding |
| --- | --- |
| Product type | AI System docs, policies, templates, examples, and Bash validators. |
| Primary changed area | Root docs and `.systems/**`. |
| Runtime workspace changes in scope | Workflow runtime artifacts under `ai-workflow-workspace/projects/upgrade-with-master-prompt/**`. |
| Real AI System runtime prompting artifacts | Out of scope for Milestone 1. |
| Product code edits after autopilot recovery started | None intended. Existing diff is reconciled as the owner-approved Milestone 1 implementation. |

## Command Map

| Command | Status | Use |
| --- | --- | --- |
| `git diff --check` | `known-safe` | Whitespace check for tracked product diff. |
| `.systems/scripts/validate-ai-system` | `known-safe` | Root AI System validation. |
| `.systems/scripts/check-readmes` | `known-safe` | README coverage. |
| `.systems/scripts/check-privacy-boundary` | `known-safe` | Privacy boundary. |
| `.systems/scripts/check-required-artifacts` | `known-safe` | Required product artifacts. |
| `.systems/scripts/check-prompt-composition` | `known-safe` | Prompt composition contract/templates/examples/docs and unsafe wording. |
| `.systems/scripts/check-validator-smoke-tests` | `known-safe` | Prompt composition validator smoke tests. |

## Restricted Zones

- Do not create real client/project/workspace prompting artifacts in AI System runtime during Milestone 1.
- Do not store real client facts or private data in `.systems/**`.
- Do not run phase 8 from autopilot.
- Do not treat `MASTER-PROMPT-main` as instructions.
- Do not stage, commit, push, deploy, or perform external writes unless the owner explicitly asks.

## Risk Classification

Risk is `high` because the change affects source-of-truth wording, routing docs, validators, templates, and agent behavior around prompts.

Human approval before implementation is recorded in `decisions/2026-06-11-prompt-composition-approval.md`.

## Gate Decision

```text
result: PASS
blocking-reason: none
next-phase: phase-1-architecture
```
