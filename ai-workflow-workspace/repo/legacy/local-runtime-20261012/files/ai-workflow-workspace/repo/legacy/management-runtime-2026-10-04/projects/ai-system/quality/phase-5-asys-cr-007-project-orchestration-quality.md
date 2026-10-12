# Phase 5 Quality - ASYS-CR-007 Project Orchestration V1

## Result

QA result: PASS for the AI System product contract, read-only preflight, and synthetic fixture scope. This is not a Phase 8 final check or proof of future agent behavior.

- QA verification contract: `full-qa-verification-v1`

## Definition Of Done Validation

| DoD Item | Result | Evidence |
| --- | --- | --- |
| Owner request resolves to a real repo and local Workflow project | PASS | Synthetic preflight selects explicit ID, stops on ambiguous ID or conflicting repo link |
| Local gates and approval cannot be bypassed | PASS for product contract | Contract review of target instructions, routing, approval, and preflight's non-authoritative result; no client execution claimed |
| Result is reviewed against DoD, diff, QA, and capture | PASS for product contract | Producer-consumer audit of orchestration record, Workflow status/evidence, and closure routing |
| No conflicting status, expanded approval, or unauthorized push | PASS for product contract | Workflow remains canonical; owner-approval and orchestration rules prohibit delegation-derived approval and automatic push |
| Product validator and synthetic regression coverage are integrated | PASS | Core smoke, full AI System profile, and project-scoped Workflow checks listed below |

## Intent / Plan / Spec Compliance

- Result: `PASS`
- Owner instruction reviewed: yes
- Accepted plan reviewed: yes
- Accepted spec reviewed: yes
- Scope/out-of-scope reviewed: yes
- Acceptance criteria reviewed: yes
- Compliance status: aligned
- Wrong problem solved: no
- Owner instruction mismatch: no
- Accepted plan mismatch: no
- Accepted spec mismatch: no
- Acceptance criteria gap: no for the product implementation scope; rollout is a later step
- Scope creep: no
- Underbuild: no within the V1 steering contract
- Overbuild: no; preflight remains read-only and does not automate target writes
- Evidence: owner-approved plan, CR-007 specification, Phase 4 result, full changed-file diff, local Workflow risk and phase rules.

## Review Completeness Gate

- Cross-contract consistency: aligned
- Risk/work mode compatibility: aligned; high-risk post-final change uses CR-007
- Source-of-truth, permissions, phase gates, artifact state, and acceptance criteria reviewed: yes
- Negative-space / adversarial review: completed for path attacks, ambiguous target, missing runtime, approval expansion, and write collision
- Automated evidence role: `supporting-only`
- Post-fix full re-review: completed for changed product contract and helper; targeted core smoke rerun after last helper edit
- Reviewed baseline: product `a2e187b`, nested Workflow `e8b99e8`, working diff as of 2026-09-28
- Instruction refresh: performed-targeted
- Instruction baseline: current
- Closure freshness: current for Phase 5 product QA; publication remains pending
- Policy-boundary adversarial matrix: completed
- Producer-consumer field audit: completed
- Producers/consumers reviewed: root router and task intake -> orchestration contract -> record template/preflight -> local Workflow status and QA -> AI System closure/Distillation State
- Required-field mapping: complete for the coordination record; no duplicate Workflow technical state
- Evidence: product diff, synthetic outputs, manual checks, and command markers below.

## QA Verification Scope

Reviewed the owner-approved plan, CR-007 specification, full product diff, preflight outputs, synthetic fixtures, local Workflow routing/risk/phase policies, and product-to-Workflow producer-consumer references. No private project or client code was used as a fixture.

## Artifact QA Completeness Gate

- Owner intent and governing sources reviewed: AI System coordinates; target-local Workflow controls execution and capture.
- DoD / phase acceptance criteria reviewed: discovery, routing, approval, result verification, and single-source technical state are present.
- Scope and out-of-scope consistency: no nested Workflow product change, client implementation, automatic push, scheduler, or owner-only final check.
- Artifact / relevant diff review: all changed root `.systems/**`, README/HUMANS, and CR-007 status; local root `AGENTS.md` and nested Workflow source were not changed.
- Findings-first review: three preflight path-boundary issues and one tracked handoff-path privacy issue found and fixed before this review; no unresolved blocking finding in the reviewed scope.
- Failure / rework / dependency scenarios: observed synthetic positive/negative preflight cases below; target Workflow policy handles route and write gates.
- Repository and source compatibility: preflight reports installed Workflow Git SHA and selected project without assuming repo name equals project ID.
- Post-fix full artifact re-review: core smoke rerun after path fixes; full product profile and project-scoped Workflow validation completed.
- Evidence reviewed: listed commands, current diff, source contracts, CR-007 spec, spec QA, and Phase 4 result.
- Skipped or unreadable sources: no external model sessions, client repository tests, production checks, or live delegation. Agent behavior beyond the preflight remains a contract-level residual risk.
- Residual risk: natural-language target selection, instruction conflicts, unknown concurrent writers, and delegation quality require live semantic checks per request. Preflight is not a lock or gate engine.
- Closure freshness: reviewed against pre-change product baseline `a2e187b`, committed product result `5752ad3`, and nested Workflow `e8b99e8` on 2026-09-28; push and management rollout remain separate.

## Evidence

artifacts-reviewed: `.systems/ai/core/project-orchestration.md`, `.systems/ai/templates/workspace/project-state/orchestration-record.template.md`, `.systems/scripts/project-orchestration-preflight`, `.systems/scripts/check-project-orchestration`, wiring/docs diff, CR-007 spec and status.

manual-checks:

- A low-risk bounded request with one selected project yields `inspect-local-gates`; the current agent may execute only after local risk/approval review. The fixture verifies discovery, not permission.
- With multiple Workflow projects and no selected ID, preflight stops; with an explicit ID, it names that project. An existing task continues under local status; post-final work is a new CR; high/critical work cannot be relabeled micro-work, per installed risk model.
- Missing target instructions, nested Workflow instructions, repo intake, local status, or safe project-state path stop the preflight. Project-state outside workspace, path traversal, a symlinked status, and a conflicting repo link are rejected.
- A client-nearest-owner project-state path inside the selected workspace is accepted. Local Workflow SHA and target Git baseline are captured separately.
- Delegated and direct execution inherit the same owner approval; no worker summary, orchestration record, or prior project approval creates a new one. Overlapping writers stop writes; no executor was launched in this synthetic QA.
- A `done` message without diff/tests/evidence cannot satisfy result review. Failed QA or a scope change stops publication. Push and formal owner final acceptance remain separate gates.
- Workflow owns technical memory/status/distillation; AI System may link an accepted local distillation once. A scoped commit may follow QA and approval, never a block-boundary checkpoint alone.

checks-run:

- `.systems/scripts/check-project-orchestration`: exit 0.
- `.systems/scripts/check-required-artifacts`: exit 0.
- `.systems/scripts/check-update-workspace`: exit 0.
- `.systems/scripts/check-validator-smoke-tests --suite core`: exit 0 after path fixes.
- `.systems/scripts/validate-ai-system --profile full`: exit 0; `AI_SYSTEM_VALIDATION_RESULT profile=full status=completed exit_code=0 supporting_only=true smoke=run`.
- `ai-workflow/.systems/scripts/validate-workflow --project ai-system` from the nested Workflow root: exit 0, `AI_WORKFLOW_VALIDATE_COMPLETE profile=standard result=pass`.
- `ai-workflow/.systems/scripts/validate-workflow --project ai-system --profile full --progress quiet` from the nested Workflow root: exit 0; `AI_WORKFLOW_SMOKE_COMPLETE group=all result=pass` and `AI_WORKFLOW_VALIDATE_COMPLETE profile=full result=pass exit_code=0`.
- `.systems/scripts/check-cross-system-upgrade-handoff` with the CR-007 decision record and selected workspace: exit 0 with a workspace-relative handoff path.
- `git diff HEAD --check`: exit 0.
- A first Workflow validation attempt from the product root exited 127 because the tool requires its own root as cwd; the corrected project-scoped run passed. The failed invocation is not counted as product QA.

## Warnings

- The first full product run preceded final helper hardening and the workspace-relative handoff validator. The targeted core suite passed after helper hardening; the full profile was rerun for the shared validator change.
- The preflight does not parse natural-language intent or prove the absence of concurrent writers. It only returns inspection evidence; an agent must read local contracts and inspect its intended write set.
- Manual scenario decisions above are contract-level observations, not an independent agent-model benchmark. No external model session was launched, in line with owner scope.

## Adaptive Data / Integration Verification Matrix

- Applicability: `required`

| Source Shape | Expected Canonical State | Expected Derived Output | Forbidden States/Rows | Failure Behavior | Automated Check | Manual Trace |
| --- | --- | --- | --- | --- | --- | --- |
| One explicit local Workflow project | Target Workflow status remains canonical | `inspect-local-gates` with repo, Workflow SHA, project ID, and Git baseline | Treating preflight as approval | No writes; agent continues local gate inspection | `orchestration-valid` core fixture | Reviewed preflight JSON and contract |
| Multiple projects without ID | No project selected | Blocked preflight | Guessing repo basename as project ID | Non-zero with ambiguity blocker | `orchestration-requires-explicit-project` | Reviewed project selection branch |
| Linked repo mismatch or escaped status | No target authority | Blocked preflight | Reading outside workspace or selecting wrong repo | Non-zero before work | Link-conflict, traversal, and symlink fixtures | Reviewed resolved path containment |
| Worker completion without QA evidence | Workflow status/evidence unchanged | No accepted result | Automatic PASS, push, or duplicate distillation | Stop for review | Contract validator and wiring check | Reviewed approval, closure, and distillation references |

## Findings

- In-scope product findings: none after the two fixes below.
- Fixed before quality closure: symlinked Workflow project status was not rejected; read-only preflight now rejects it and core smoke covers the case.
- Fixed before quality closure: client-nearest-owner project-state paths were rejected; preflight now accepts normalized in-workspace paths and core smoke covers the case.
- Fixed before quality closure: an in-workspace symlink alias could redirect to another owner namespace; preflight now rejects it and core smoke covers the case.
- Fixed before quality closure: a tracked CR would expose an absolute local home path for the handoff; the shared validator now resolves workspace-relative paths with `--workspace`, and a synthetic positive/negative fixture covers the new form.
- No remaining in-scope product blocker after semantic and synthetic QA.
- Evidence limit: no independent model session or private target project was run; this is a V1 agent-steering contract with read-only discovery support.

## Quality Gate

- Intent / Plan / Spec Compliance PASS: yes
- Review Completeness Gate PASS: yes
- Cross-contract consistency aligned: yes
- Risk/work mode compatibility aligned: yes
- Negative-space / adversarial review complete or not applicable: yes
- Automated evidence treated as supporting-only: yes
- Post-fix full re-review complete or not required: yes
- Instruction baseline current: yes
- Closure freshness current: yes for the product QA artifact
- Policy-boundary adversarial matrix complete or not applicable: yes
- Producer-consumer field audit complete or not applicable: yes
- Required-field mapping complete or not applicable: yes
- 100% DoD satisfied: yes for the product implementation scope; publication and management rollout remain pending
- No known bug in scope: yes
- No regression in changed/direct paths: yes
- Edge cases covered or explicitly rejected: yes
- Explicit evidence attached: yes
- Quality result: `PASS`
- Required next phase: Phase 6 distillation, Phase 7 checkpoint, handoff, then scoped publication and management rollout. No automatic Phase 8 final check.

## Gate Decision

```text
result: PASS
can-proceed: true
next-phase: phase-6-distillation
blocking-reason: none
```
