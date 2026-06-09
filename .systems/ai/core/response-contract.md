# Response Contract

## Purpose

This file defines the required user-facing response shape for AI System work.

It is communication policy. It does not grant write permission and does not bypass blockers, privacy, validation, or `owner-approved` gates.

## When It Applies

Every substantive response must end with `Co dalej?`.

Substantive responses include:

- completed implementation or documentation work;
- audit, validation, review, and blocker reports;
- guide, recovery, task-intake, dump triage, memory, distillation, and change-request responses;
- clarification responses when a command is too short or ambiguous to execute safely.

Do not place the footer inside strict machine-readable output when the owner explicitly requested JSON-only, patch-only, or exact-template output. Put it in the nearest surrounding human-facing response.

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
