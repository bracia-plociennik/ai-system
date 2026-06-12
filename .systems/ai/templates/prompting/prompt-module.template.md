# Prompt Module Template

## Metadata

| Field | Value |
| --- | --- |
| `module-id` | `<kebab-case-id>` |
| `module-type` | `prompt-module` |
| `status` | `draft` |
| `owner` | `<system|workspace|client|project>` |
| `applies-to` | `<operation|task-type|client-work|project-work|workspace-work>` |
| `authority` | `advisory` |

## Purpose

Describe the narrow behavior this module frames.

## Inputs

- Required context:
- Optional context:
- Source artifacts:

## Allowed Influence

This module may:

- organize context;
- shape output format;
- require explicit assumptions;
- require source labels;
- sharpen review stance.

## Forbidden Overrides

This module must not:

- authorize writes;
- approve implementation;
- approve file movement;
- skip validation or evidence;
- weaken privacy, risk, permissions, stop conditions, or owner approvals;
- override `AGENTS.md`, core policy, current files, status, memory, decisions, or owner instructions.

## Output Contract

Expected output shape:

- Section or field:
- Required evidence:
- Required assumptions:

## Source Labels

Label inputs as:

- `owner-provided`
- `accepted-artifact`
- `filesystem-state`
- `workspace-status`
- `client-memory`
- `project-memory`
- `primary-entity-memory`
- `skill-guidance`
- `inferred`
- `defaulted-from-template`

## Refresh Conditions

Refresh this module use when:

- accepted context changes;
- workspace, client, or project status changes;
- task, decision, memory, or checkpoint changes;
- owner decision changes;
- source conflict is detected.

## Notes

Add module-specific guidance here.
