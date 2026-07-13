# Validation Profiles

## Purpose

Validation Profiles define faster local validation paths without weakening AI System safety gates.

Default `.systems/scripts/validate-ai-system` with no arguments is the `standard` profile. It is the daily iteration and ordinary post-implementation quality validator.

Profiles may reduce iteration time, but they must not change source-of-truth order, privacy, owner-approved writes, evidence requirements, contract compliance, Knowledge Capture Gate, End-of-Task Capture, final acceptance, CI behavior, or commit readiness.

## Profiles

| Profile | Intended use | Final validation evidence |
| --- | --- | --- |
| `full` | Checkpoint validation, major distillation, major verification, CI, release/final confidence checks, and high-impact AI System contract changes | yes, unless smoke tests are explicitly skipped and residual risk is reported |
| `standard` | Daily iteration, ordinary post-implementation quality closure, and normal system-maintenance checks | yes for ordinary work; no when a full-required gate applies |
| `scoped` | Local iteration for one or more explicitly selected validators | no unless the owner explicitly accepts narrow validation with residual risk |
| `fast` | Quick sanity check during editing | no |

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

`standard` runs the complete AI System validator chain except embedded `check-validator-smoke-tests`. Use it for normal daily iteration and ordinary post-implementation quality closure.

`full` runs the complete standard chain and `check-validator-smoke-tests`. Use it for checkpoint validation, major distillation, major verification, CI, release/final confidence checks, and high-impact changes to `.systems/ai/core/**`, templates, validators, validation/update scripts, root agent template, `README.md`, or `HUMANS.md`.

CI and `.systems/scripts/update-from-upstream` must call `.systems/scripts/validate-ai-system --profile full` explicitly.

If `AI_SYSTEM_SKIP_SMOKE_TESTS=1` is used with `--profile full`, the result is not eligible for final validation evidence unless the owner explicitly accepts the residual risk.

## Scoped And Fast

`scoped` runs the fast base checks plus explicitly named validators. It is for targeted local iteration and must not be described as sufficient before commit or push without explicit owner acceptance of residual risk.

`fast` runs only cheap sanity checks: `git diff --check` when inside a git repository, `check-required-artifacts`, `check-naming`, `check-privacy-boundary`, and `check-contract-compliance`. It is not final validation evidence.

## Safety Boundaries

Validation profiles must not:

- make `fast` or `scoped` sufficient before commit or push by default;
- make `standard` replace `full` for a full-required gate;
- let skipped smoke tests count as PASS or final validation evidence;
- weaken CI, privacy, evidence, contract compliance, Knowledge Capture Gate, owner approval, or final acceptance.

When narrow validation is accepted, report the profile used, checks run, checks skipped, reason, residual risk, and owner approval.
