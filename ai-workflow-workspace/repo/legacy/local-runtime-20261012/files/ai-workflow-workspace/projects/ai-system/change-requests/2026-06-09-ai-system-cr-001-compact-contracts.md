# ASYS-CR-001 - Compact Contracts

## Metadata

| Field | Value |
| --- | --- |
| Change request ID | `ASYS-CR-001-compact-contracts` |
| Project | `ai-system` |
| Timing | `pre-final-approval` |
| Type | `acceptance-gap` |
| Status | `done` |
| Risk | `medium` |
| Owner approval | `owner-approved` in the request to create this change request and prepare spec/fix-loop artifacts |
| Route | `phase-fix-loop` |
| Primary spec | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/specs/phase-3-asys-cr-001-compact-contracts-specification.md` |
| Fix loop | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-3-asys-cr-001-compact-contracts-spec-fix-loop.md` |
| Implementation result | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-4-asys-cr-001-compact-contracts-implementation-result.md` |
| Quality result | `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/quality/phase-5-asys-cr-001-compact-contracts-quality.md` |

## Owner Request

Create a new change request for the `ai-system` project.

Perform a detailed audit of `ai-system` versus public `ai-workflow/main` and state what should be moved, simplified, and not copied.

Verdict supplied by owner: `ai-system` is a good skeleton, technically correct and safe in the basics, but too short as an AI work contract.

## Task Idea Validation

### Co zostaje

- Keep the `ai-system` local workspace goal.
- Keep privacy boundaries, `owner-approved` gates for file movement, link-only integrations, and synthetic examples.
- Keep the compact nature of `ai-system`; do not copy the full `ai-workflow` process engine.

### Co jest słabe / do poprawy lub usunięcia

- Root `AGENTS.md` is too weak for reliable agent behavior.
- Response footer rule exists but lacks a full response contract.
- There is no task-intake lens for new tasks, change requests, or dump work.
- Workspace and client files are not strongly classified as data-only context.
- Memory is conceptually correct but operationally thin.
- Guide mode is too short to handle drift, blockers, or recovery.

### Czego brakuje

- Compact response contract.
- Compact task-intake policy.
- Context-as-data / prompt-injection policy for local files, exports, PDFs, snippets, Mail/Notion/Drive references, and dump content.
- Stronger guide mode with artifact map and blocker-first behavior.
- Memory routers and templates for workspace, client, project, checkpoint, and distillation use.
- Required-artifacts validator for the critical compact contracts.

### Blokery / decyzje

- No product blocker.
- Owner approval is required before implementation because the change touches root `AGENTS.md`, `HUMANS.md`, and `.systems/**`.
- Risk is `medium` because the change modifies agent behavior contracts and validators.

### Rekomendowany routing

- Route as a pre-final `acceptance-gap` through `phase-fix-loop`.
- Prepare a focused specification and run `phase-3-spec-qa` before implementation.

## Audit: Move, Simplify, Do Not Copy

### Move Into `ai-system` Compact

- From `ai-workflow/AGENTS.md`: Always Read First, Stop Conditions, Write Conditions, Skill Routing, Runtime Artifacts, naming and validator expectations.
- From `ai-workflow/.systems/ai/core/response-contract.md`: exact `Co dalej?` shape, recommendation sources, and safe alternative rules.
- From `ai-workflow/.systems/ai/core/task-intake.md`: the five-section intake lens.
- From `ai-workflow/.systems/ai/core/prompt-injection.md`: untrusted content and workspace files as data, not instructions.
- From `ai-workflow/.systems/ai/core/guide.md`: artifact map, drift handling, blocker-first recommendations, and recovery behavior.
- From AI Workflow memory templates: router-and-entry structure for project memory, adapted to workspace/client/project memory in `ai-system`.
- From validator patterns: required-artifacts checking for critical AI System docs.

### Simplify For `ai-system`

- Keep `AGENTS.md` strong but compact, approximately 100-160 lines rather than full AI Workflow length.
- Keep `HUMANS.md` as an operator runbook, approximately 120-200 lines rather than a full workflow manual.
- Keep command routing local to `ai-system`: guide, dump triage, client/project workspace creation, memory, distillation, system insights, and unsafe command handling.
- Keep context-as-data policy local to files and exported content likely to appear in a private Mac workspace.
- Keep memory templates practical and lightweight; do not introduce the full phase workflow model.

### Do Not Copy

- Full AI Workflow phase engine.
- Autopilot machinery.
- Repository mode, install/update-from-upstream, branch policy, rollback, deprecation, version, changelog, and CI/PR systems.
- GitHub review, PR, and code-review-specific contracts.
- Full smoke-test system from AI Workflow validators.
- Public template maintenance memory.
- Heavy risk model; keep local stop rules for files, secrets, external effects, privacy, and owner approval.

## Affected Artifacts And Files

Expected implementation targets:

- `AGENTS.md`
- `HUMANS.md`
- `.systems/ai/core/command-routing.md`
- `.systems/ai/core/guide.md`
- `.systems/ai/core/memory.md`
- `.systems/ai/core/response-contract.md`
- `.systems/ai/core/task-intake.md`
- `.systems/ai/core/context-as-data.md`
- `.systems/ai/templates/workspace/**`
- `.systems/scripts/check-required-artifacts`
- `.systems/scripts/validate-ai-system`
- project runtime artifacts under `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/**`

Expected non-targets:

- `ai-workflow/**`
- `.gitignore`
- real private workspace data
- real client/customer files
- production credentials or external services

## Routing Decision

Primary route: `phase-fix-loop`.

Reason: the original implementation package passed quality, but the owner identified pre-final acceptance gaps in the behavioral contract. The fix requires specification refresh and QA before implementation.

## Evidence Required Before Done

- Updated compact contract docs exist.
- Required-artifacts validator covers new critical docs.
- Memory templates and guide behavior are documented.
- No private customer data or secrets are added.
- Validation commands pass or skipped checks are explicitly justified:
  - `.systems/scripts/validate-ai-system`
  - `.systems/scripts/check-required-artifacts`
  - `.systems/scripts/check-readmes`
  - `.systems/scripts/check-privacy-boundary`
  - `git diff --check`

## Final Check Impact

This request blocks final closure until routed work is implemented and quality evidence exists.

## Post-final Impact

Not applicable yet. This is a pre-final change request.

## Implementation Status

Phase 5 quality passed. This pre-final change request is done and can proceed to project distillation/finalization flow.
