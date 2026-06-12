# AI System Maintenance Baseline Template

## Metadata

| Field | Value |
| --- | --- |
| `baseline-id` | `ai-system-maintenance-baseline` |
| `artifact-type` | `maintenance-baseline` |
| `status` | `draft` |
| `authority` | `advisory` |

## Purpose

Frame work on AI System itself.

This baseline helps maintain `AGENTS.md`, `.systems/**`, templates, validators, examples, and runtime contracts without weakening source-of-truth order or private workspace safety.

## Maintenance Lens

Prioritize:

- source-of-truth clarity;
- privacy and context-as-data boundaries;
- multi-workspace routing;
- local-only runtime safety;
- template portability;
- validator coverage;
- evidence quality;
- owner approval for writes.

## Required Variables

| Variable | Expected Value Or Source |
| --- | --- |
| `change-type` | policy, template, validator, example, runtime-doc, docs |
| `write-set` | tracked files plus any exact owner-approved runtime artifacts |
| `workspace-impact` | none, template-only, selected workspace, cross-workspace |
| `validation-commands` | AI System validators and `git diff --check` |
| `owner-approval` | exact `owner-approved` write scope |

## Forbidden Overrides

This baseline must not:

- treat itself as higher priority than `AGENTS.md`;
- weaken privacy, approval, validation, or stop conditions;
- store real client facts in `.systems/**`;
- edit runtime workspace data without exact owner approval;
- create client or project commitments;
- skip validation evidence.

## Evidence Expectations

Maintenance work should record:

- changed files;
- relevant policy references;
- validation commands;
- skipped checks and impact;
- residual risks;
- compatibility notes.

## Refresh Conditions

Refresh this baseline when:

- source-of-truth order changes;
- workspace routing changes;
- validator policy changes;
- runtime ownership rules change;
- prompt composition policy changes.
