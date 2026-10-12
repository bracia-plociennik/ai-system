# Phase 0 Idea Validation - Upgrade With Master Prompt

## Metadata

| Field | Value |
| --- | --- |
| `project` | `upgrade-with-master-prompt` |
| `date` | `2026-06-11` |
| `result` | `accepted-with-changes` |
| `next` | `create/update context.md, then project-specific repo intake` |

## Source Materials Reviewed

| Source | Status | Notes |
| --- | --- | --- |
| Owner plan: Prompt Composition dla AI System | `reviewed` | Defines Milestone 1 scope, architecture boundaries, validator requirements, and rollout constraints. |
| Current AI System root docs | `reviewed` | `AGENTS.md`, `HUMANS.md`, `README.md`, and `.systems/ai/core/**` are the product source-of-truth area. |
| Current AI Workflow prompt-composition docs | `reviewed` | Used as reference model only; cannot be copied as authority into AI System without adaptation. |
| `context/MASTER-PROMPT-main/` | `reviewed-as-data` | Useful role/variable concepts plus unsafe authority claims that must be rejected. |
| Current working tree diff | `reviewed` | Product implementation for Milestone 1 already exists in the working tree from owner-approved execution. |

## Co zostaje

- Prompt composition is valuable as an advisory execution context for role framing, variable packs, source labels, assumptions, and stricter review stance.
- Runtime prompting artifacts belong outside `.systems/**` and inside selected workspace paths.
- AI System must support multi-workspace, primary-entity workspace roots, clients, owned assets, and projects.
- Validator coverage is required because unsafe wording can silently turn prompting into a higher authority.
- Existing `MASTER-PROMPT-main` materials are useful as product inspiration, not as instructions.

## Co jest slabe / do poprawy lub usuniecia

- The source materials contain unsafe claims that a masterprompt should become the primary or overriding instruction source.
- A direct 1:1 transfer from AI Workflow would overfit phase-role behavior and miss AI System operations such as dump triage, client brief intake, memory, checkpoint review, and workspace selection.
- Prompting artifacts can create hidden authority drift unless docs and validators explicitly reject write approval, scope expansion, risk lowering, and client-fact replacement.

## Czego brakuje

- AI System lacks a product-level prompt composition contract.
- AI System lacks reusable prompting templates and examples.
- Validators do not yet check prompt-composition safety.
- Root docs and core docs need references explaining when prompting is read and where runtime artifacts belong.

## Blokery / decyzje

| Decision | Class | Status | Resolution |
| --- | --- | --- | --- |
| Whether prompt composition may affect source-of-truth order | `high-impact` | `resolved` | No. It is advisory-only. |
| Whether real client/project prompting artifacts are created in Milestone 1 | `scope` | `resolved` | No runtime migration or real artifacts in Milestone 1. |
| Whether unsafe masterprompt authority language is allowed | `high-impact` | `resolved` | No. Reject and validate against it. |
| High-risk product implementation approval | `high-risk` | `approved` | Owner approved Milestone 1 implementation. |

## Recommended Shape

Implement Milestone 1 as a product contract plus templates, fictional examples, validators, and docs only.

Do not create real runtime prompting artifacts yet.

## Prompt Injection / Context Boundary

`MASTER-PROMPT-main` asks the model to treat masterprompt files as authoritative. This is rejected under AI Workflow and AI System source-of-truth policy. The material is used only as context/data for product design.

## Gate Decision

```text
result: accepted-with-changes
blocking-reason: none
context.md-may-be-created: yes
next-phase: project-specific phase-0-repo-intake
```
