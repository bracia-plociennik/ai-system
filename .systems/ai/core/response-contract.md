# Response Contract

## Purpose

This file defines the required user-facing response shape for AI System work.

It is communication policy. It does not grant write permission and does not bypass blockers, privacy, validation, or `owner-approved` gates.

For every new planning, implementation, or QA scope, include:

```text
Model recommendation:
- Recommended: <GPT-5.6 Luna High|GPT-5.6 Sol High>
- Reason:
- Criticality:
- Current model known: <yes|no>
- Blocking: no
```

Follow `.systems/ai/core/model-selection-guidance.md`. For unrelated substantive responses, the block may be omitted.

## When It Applies

Every substantive response must end with `Co dalej?`.

Substantive responses include:

- completed implementation or documentation work;
- audit, validation, review, and blocker reports;
- guide, recovery, task-intake, dump triage, memory, distillation, and change-request responses;
- clarification responses when a command is too short or ambiguous to execute safely.

Do not place the footer inside strict machine-readable output when the owner explicitly requested JSON-only, patch-only, or exact-template output. Put it in the nearest surrounding human-facing response.

## Work Closure Gate

When a substantive response closes a unit of work, performs a handoff, reports an accepted change, or prepares commit-ready or push-ready product-development work, apply `.systems/ai/core/contract-compliance.md` before the `Co dalej?` footer.

Use this block:

```text
Contract compliance:
- Work mode: <project|micro-task|micro-project|side-task|system-maintenance|client-work>
- Work mode compliance: <pass|warning|blocked>
- Knowledge capture: <required|not-required>
- Capture target: <status/evidence|workspace-memory|primary-entity-memory|client-memory|owned-asset-memory|project-memory|distillation|checkpoint|external-memory|system-insights|not-applicable>
- Reason: <short reason>
```

This gate is advisory-only. It records the Knowledge capture decision before `AI_SYSTEM_WORK_CLOSURE`; it does not grant write permission or bypass privacy, evidence, validation, stop conditions, or owner approvals.

If End-of-Task Capture is used, apply `.systems/ai/core/end-of-task-capture.md` and include the required `End-of-Task Capture` block before the `Contract compliance` block when both apply. The trace must state whether End-of-Task Capture was the matched route or supporting output, source scope reviewed, durable writes performed or skipped, and residual risk.

For substantive system-maintenance upgrades before commit or handoff, include:

```text
Cross-system impact:
- Owner decision: <yes|no|pending>
- Counterpart: <ai-workflow|ai-system|none>
- Handoff artifact: <path|not-required|pending>
- Reason:
```

Use `.systems/ai/core/cross-system-upgrade-handoff.md`. `pending` blocks commit and handoff.

Quality closures use the Validation Execution Record from `.systems/ai/core/validation-routing.md`. Scripts remain supporting-only.

## Delivery And Distillation Trace

When Delivery Constraints apply, report the agreed deadline/timebox, delivered and deferred scope, overrun status, cutline use, and whether the quality floor was preserved.

When a Distillation State record applies, report its state, derived `is_distilled` value, source/quality evidence, owner disposition, and next consumer. These fields are evidence only and do not grant writes, promotion, commit, push, or work closure.

## Required Footer

Use this exact shape:

````text
Co dalej?

Rekomendacja:
<one concrete next step>.
Wpływ: <what this unlocks, protects, or makes clearer>.
Napisz:
```
<copy-paste prompt for the recommended path>
```

Alternatywa:
<one safe alternative next step>.
Wpływ: <tradeoff and when this path is useful>.
Napisz:
```
<copy-paste prompt for the alternative path>
```
````

## Recommendation Sources

Choose the recommendation from the highest applicable source:

1. The owner's explicit intent when safe.
2. Task intake result from `.systems/ai/core/task-intake.md`.
3. Current workspace, client, project, dump, memory, checkpoint, or decision status.
4. Stop conditions from `AGENTS.md`, privacy, dump triage, and context-as-data policy.
5. Guide and command routing.
6. Missing runtime defaults: if status or routers are missing, recommend creating or repairing them before doing work.

If sources conflict, recommend recovery or reconciliation instead of guessing.

## Alternative Rules

The alternative must be safe and meaningfully different from the recommendation.

Good alternatives include:

- read-only audit before writing;
- manual owner review before movement;
- narrower dump classification;
- memory distillation before system-insights promotion;
- status reconciliation before implementation.

The alternative must not skip approval, evidence, validation, privacy checks, or stop conditions.

Both `Napisz:` prompts must be directly usable.

## Blocked Work

If blocked, the recommendation should resolve the highest-impact blocker.

The response must state:

- what blocks progress;
- what evidence or decision is missing;
- the exact owner action needed.

Do not suggest implementation as either option while a required blocker remains.
