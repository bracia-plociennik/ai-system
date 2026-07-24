# Validation Profiles

## Purpose

Validation Profiles define what AI System script bundles run after `.systems/ai/core/validation-routing.md` establishes that scripts are applicable.

Default `.systems/scripts/validate-ai-system` with no arguments is the `standard` profile. It is not a default implementation command and never substitutes for semantic or product QA.

Profiles may reduce script execution time, but they must not change source-of-truth order, privacy, owner-approved writes, evidence requirements, semantic QA, product checks, contract compliance, Knowledge Capture Gate, End-of-Task Capture, final acceptance, CI behavior, or commit readiness.

## Profiles

| Profile | Intended use | Final validation evidence |
| --- | --- | --- |
| `full` | Applicable checkpoint validation, major distillation, final system verification, CI, release confidence, and high-impact AI System contract changes | supporting evidence, unless smoke tests are skipped |
| `standard` | Applicable ordinary AI System artifact quality or system-maintenance closure | supporting evidence only |
| `scoped` | Explicit targeted artifact validators after semantic review | supporting evidence only |
| `fast` | Optional quick contract sanity check outside active implementation writes | supporting evidence only |

## Script Interface

`.systems/scripts/validate-ai-system` supports:

- no arguments: same as `--profile standard`;
- `--profile full`;
- `--profile standard`;
- `--profile scoped --checks <check-a,check-b>`;
- `--profile fast`;
- `--explain` with any profile.

`--checks` is valid only with `--profile scoped`. Scoped checks must be explicit existing script basenames such as `check-personal-ops`; automatic changed-file inference is intentionally out of scope for v1.

`--explain` reports the selected profile, smoke-test behavior, final-evidence eligibility, and explicit scoped checks.

## Standard And Full

`standard` runs the complete AI System validator chain except embedded `check-validator-smoke-tests`. Use it only when validation routing marks the broad chain applicable.

`full` runs the complete standard chain and `check-validator-smoke-tests`. Use it after semantic current-diff review for checkpoint validation, major distillation, final system verification, CI, release confidence, upstream updates, and high-impact changes to `.systems/ai/core/**`, templates, validators, validation/update scripts, root agent template, `README.md`, or `HUMANS.md`.

CI and `.systems/scripts/update-from-upstream` must call `.systems/scripts/validate-ai-system --profile full` explicitly.

If `AI_SYSTEM_SKIP_SMOKE_TESTS=1` is used with `--profile full`, the result is not eligible for final validation evidence unless the owner explicitly accepts the residual risk.

## Scoped And Fast

`scoped` runs the fast base checks plus explicitly named validators. Use it after semantic artifact review for targeted validation. It must not be described as a quality verdict or as sufficient before commit or push.

`fast` runs only cheap contract sanity checks. Do not run it automatically during ordinary implementation. It is not a quality verdict.

## Personal Ops Targeted Default

Routine native V3 daily check-in writes use targeted validation by default:

- `AI_SYSTEM_WORKSPACE_HOME=<workspace-path> .systems/scripts/check-personal-ops` for check-in-only writes;
- add `AI_SYSTEM_WORKSPACE_HOME=<workspace-path> .systems/scripts/check-task-management` when the same approved write creates or updates TaskNotes;
- use `.systems/scripts/sync-personal-ops-check-ins-v3 --workspace <workspace-path> --status-only` to inspect freshness without regenerating indexes.

This targeted route follows semantic and data review. It is not a quality verdict for repository changes. Use `standard` or `full` only when validation routing marks the broad profile applicable. Targeted validation cannot skip required schema, privacy, owner-approval, TaskForge, or explicit route checks.

## Safety Boundaries

Validation profiles must not:

- run broad AI System validation solely because AI System governs an ordinary implementation;
- run before semantic QA, findings-first review, and applicable product checks;
- derive `PASS` from green scripts alone;
- make `fast` or `scoped` sufficient before commit or push by default;
- make `standard` replace `full` for a full-required gate;
- let skipped smoke tests count as PASS or final validation evidence;
- weaken CI, privacy, evidence, contract compliance, Knowledge Capture Gate, owner approval, or final acceptance.

When scripts are used, record the semantic QA result, findings/blockers, product checks, script applicability, targeted commands, `Script evidence role: supporting-only`, final verdict, skipped checks, and residual risk.
