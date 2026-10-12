# Phase 6 Distillation - UWMP-SYSTEM-001 Prompt Composition Contract

## Metadata

| Field | Value |
| --- | --- |
| `project` | `upgrade-with-master-prompt` |
| `task-id` | `UWMP-SYSTEM-001-prompt-composition-contract` |
| `date` | `2026-06-11` |
| `quality` | `quality/phase-5-uwmp-system-001-prompt-composition-contract-quality.md` |
| `memory-in-repo-memory` | `false` |

## Co zostalo zrobione

- AI System gained an advisory-only prompt composition contract.
- Prompting templates and fictional examples were added as reusable product artifacts.
- Validators and smoke tests were added to enforce required files and unsafe authority wording checks.
- Root and core docs now place prompt composition below canonical status, memory, decision, checkpoint, privacy, evidence, risk, and approval rules.
- Existing owner-approved product diff was reconciled into workflow phase artifacts.

## Problemy

- Source materials contained unsafe authority language saying masterprompt files should override normal rules.
- Workflow project status lagged behind the existing product diff, so the project needed recovery-style artifact reconciliation.

## Decyzje

- Prompt composition artifacts are advisory execution context only.
- `MASTER-PROMPT-main` can inspire role/variable/template design, but it is not an instruction source.
- Runtime prompting artifacts must live in selected workspace paths, not `.systems/**`.
- Real client/project prompting adoption is a later owner-approved runtime task.

## Zasady na przyszlosc

- Any prompt-composition feature must preserve source-of-truth order before it adds role, variable, or module behavior.
- Validators should include unsafe mixed wording cases, not just missing-file checks.
- When source materials contain prompt-like instructions, classify them as data and record the authority conflict explicitly.
- If product implementation happens before workflow artifacts, reconcile honestly in phase 4 and phase 5 instead of pretending the sequence was clean.

## Status Memory

```text
memory-in-repo-memory: false
project-memory-entry: ai-workflow-workspace/projects/upgrade-with-master-prompt/memory/2026-06-11-prompt-composition-milestone-1.md
```
