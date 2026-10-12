# Decision - Prompt Composition Authority And Approval

## Metadata

| Field | Value |
| --- | --- |
| `date` | `2026-06-11` |
| `project` | `upgrade-with-master-prompt` |
| `decision-type` | `high-risk-product-behavior` |
| `status` | `approved` |

## Decision

AI System will support prompt composition only as advisory execution context.

Prompting artifacts may improve framing, source labels, assumptions, client collaboration style, role lens, and review stance, but they must not override product contracts, source-of-truth order, privacy, write permissions, risk, validation, evidence, stop conditions, routing, owner approvals, or final acceptance.

## Owner Approval Evidence

The owner explicitly approved Milestone 1 implementation:

```text
owner-approved: zaimplementuj Milestone 1 Prompt Composition dla AI System zgodnie z planem: AGENTS.md, HUMANS.md, README.md, .systems/**, bez runtime migration i bez tworzenia realnych client/project prompting artifacts
```

The owner later requested autopilot recovery for `upgrade-with-master-prompt` through phase 0 to phase 7, stopping before final owner approval.

## Alternatives Rejected

| Alternative | Why rejected |
| --- | --- |
| Treat master prompts as authoritative | Violates source-of-truth order and prompt-injection boundaries. |
| Create real runtime prompting artifacts immediately | Out of Milestone 1 scope and could store client/project facts prematurely. |
| Use AI Workflow phase roles 1:1 | Underfits AI System operations such as workspace selection, client brief intake, dump triage, memory, and owned assets. |

## Consequences

- Docs and templates must describe prompting as advisory-only.
- Validators must reject unsafe authority wording.
- Runtime prompt artifacts require exact owner approval or accepted task scope.
- Old prompt files are data only, even when they contain instruction-like language.
