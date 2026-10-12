# Upgrade With Master Prompt Project Workspace

This directory contains project-scoped workflow artifacts for `upgrade-with-master-prompt`.

## Directory Layout

- `context.md` - accepted project context after idea validation.
- `context/` - raw/supporting briefs, prompts, product notes, and project source material.
- `intake/` - idea validation and project/context initial audit artifacts.
- `architecture/` - architecture artifacts and supporting notes.
- `planning/` - project plan and packaging updates.
- `specs/` - task/package implementation specifications only.
- `quality/` - QA, quality, final-check, and gate evidence artifacts.
- `decisions/` - project-level and task-level decision records.
- `escalations/` - STOP/escalation artifacts.
- `distillations/` - task/package distillations after quality PASS.
- `checkpoints/` - project checkpoint artifacts.
- `autopilot/` - runtime autopilot runs when autopilot is active.
- `autopilot/README.md` - autopilot run router.
- `memory.md` - project memory router/index.
- `memory/` - detailed project memory entries.
- `status.md` - project-local workflow status snapshot.
- `plans.md` - planning router/index for `planning/`.
- `tasks.md` - task index/router.
- `tasks/` - optional task cards.
- `micro-tasks.md` - project-local micro-task router/index.
- `micro-tasks/` - low-risk micro-task artifacts.
- `change-requests.md` - owner change request router/index.
- `change-requests/` - pre-final and post-final owner change request artifacts.
- `code-review.md` - project-local review checklist and router.
- `reviews/` - detailed review artifacts.

## Current Canonical Artifacts

- Context: `context.md`
- Idea validation: `intake/phase-0-idea-validation.md`
- Project intake: `intake/phase-0-repo-intake.md`
- Architecture: `architecture/phase-1-architecture.md`
- Architecture QA: `quality/phase-1-architecture-qa.md`
- Project plan: `planning/phase-2-project-plan.md`
- Plan QA: `quality/phase-2-plan-qa.md`
- Task specifications: `specs/phase-3-uwmp-system-001-prompt-composition-contract-specification.md`
- Spec QA: `quality/phase-3-uwmp-system-001-prompt-composition-contract-spec-qa.md`
- Implementation result: `quality/phase-4-uwmp-system-001-prompt-composition-contract-implementation-result.md`
- Quality result: `quality/phase-5-uwmp-system-001-prompt-composition-contract-quality.md`
- Post-review quality evidence: `quality/post-review-prompt-composition-findings-quality-2026-06-12.md`
- Final review: `reviews/final-prompt-composition-review-2026-06-12.md`
- Distillation: `distillations/phase-6-uwmp-system-001-prompt-composition-contract-distillation.md`
- Initial checkpoint: `checkpoints/phase-7-checkpoint-2026-06-11-prompt-composition-milestone-1.md`
- Latest checkpoint: `checkpoints/phase-7-checkpoint-2026-06-12-post-review-prompt-composition-findings.md`
- Final check: `quality/phase-8-final-check.md`
- Final owner approval: `decisions/2026-06-12-final-owner-approval.md`
- Latest autopilot run: `autopilot/runs/autopilot-002/`

## Relationship To Global Docs

- `ai-workflow/.systems/ai/` keeps workflow rules and templates.
- This directory keeps project-specific process artifacts.
- Repository state remains the source of truth for actual implementation.
