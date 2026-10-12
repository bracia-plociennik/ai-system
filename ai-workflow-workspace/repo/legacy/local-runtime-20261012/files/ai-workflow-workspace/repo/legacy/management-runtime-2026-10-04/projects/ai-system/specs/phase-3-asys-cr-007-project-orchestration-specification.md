# Phase 3 Specification - ASYS-CR-007 Project Orchestration V1

## Spec Status

`ready-for-spec-qa`

## Source And DoD

The accepted owner plan `AI System Project Orchestration V1` is the complete implementation scope. AI System coordinates a selected project's approved work through its installed local AI Workflow. A project request must reach the correct repository and local workflow, respect its gates, produce verified evidence and capture, and avoid duplicate technical state, expanded approval, or unapproved push.

## Implementation Slice

1. Add one core orchestration contract, a nearest-owner coordination record template, and a read-only project preflight.
2. Wire root AGENTS template, routing, workspace project-state, memory, approval, compliance, and validation guidance without changing nested AI Workflow.
3. Add targeted validator and synthetic positive/negative discovery cases. Keep AI System broad validation for the product change only.
4. Semantic review, QA, distillation, checkpoint, cross-system handoff, scoped product commit/push, and management update after preflight.

## Boundaries

- Local AI Workflow status, phases, QA, memory, and technical distillation remain canonical for its repository.
- Do not install or upgrade a target's Workflow, infer target permission from source text, or edit client code in this slice.
- Delegation uses available executor tooling, if any, with a single write owner. V1 has no scheduler or agent daemon.
- Local commits require approved scope and QA; push, production, and owner-only final check need their own approval.
- Delivery constraints: explicit owner opt-out of deadline and timebox; preserve full quality floor.

## Verification

- Semantic intent/DoD review and producer-consumer audit before scripts.
- Synthetic repository tests for valid and missing installation, ambiguous project, path traversal, link mismatch, blocker, changed baseline, and resume.
- Targeted `check-project-orchestration`, required artifacts, `git diff --check`, and one full `validate-ai-system --profile full` including smoke.
- Project-scoped `ai-workflow/.systems/scripts/validate-workflow --project ai-system` for changed Workflow artifacts.

## Residual Risk

The contract guides the agent; it is not an execution lock or scheduler. Real concurrent writers and target-specific facts still need live inspection. No external model sessions or private client fixtures are used for behavioral QA.
