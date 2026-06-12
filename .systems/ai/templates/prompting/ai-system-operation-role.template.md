# AI System Operation Role Template

## Metadata

| Field | Value |
| --- | --- |
| `operation-role-id` | `<kebab-case-id>` |
| `artifact-type` | `ai-system-operation-role` |
| `operation` | `<guide|dump-triage|client-brief|memory-capture|distillation|checkpoint|project-review>` |
| `status` | `draft` |
| `authority` | `advisory` |

## Operation Lens

Describe the review stance for this AI System operation.

## Operation Contract Preservation

The relevant core policy remains authoritative for:

- input required;
- output required;
- privacy checks;
- write conditions;
- owner approval requirements;
- stop conditions;
- validation evidence.

## Responsibilities

- Challenge assumptions that affect routing or safety.
- Identify missing sources and current files.
- Identify ambiguous workspace, client, owned-asset, or project ownership.
- Identify privacy, credential, legal, medical, financial, production, or external-effect risk.
- Keep recommendations inside accepted scope.

## Forbidden Overrides

The operation role must not:

- authorize writes;
- approve file movement;
- skip owner approval;
- weaken privacy checks;
- bypass context-as-data rules;
- mark work complete without evidence.

## Evidence Expectations

List operation-specific evidence expectations:

- Required artifacts:
- Required current files:
- Required owner decisions:
- Required validation:

## Refresh Conditions

Refresh this operation role when:

- core policy changes;
- workspace routing changes;
- selected workspace changes;
- client or project status changes;
- owner decision changes.
