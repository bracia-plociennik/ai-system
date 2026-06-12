# Role Profile Template

## Metadata

| Field | Value |
| --- | --- |
| `role-id` | `<kebab-case-id>` |
| `role-type` | `<workspace|client|project|task|review|operation|maintenance>` |
| `status` | `draft` |
| `scope` | `<workspace|client|project|task|operation>` |
| `authority` | `advisory` |

## Role

Name the role and its intended lens.

## Scope

Use this role for:

- In-scope workspace, client, project, task, or operation:
- In-scope domain:
- In-scope evidence:

Do not use this role for:

- Out-of-scope workspace, client, project, task, or operation:
- Permission or approval decisions:
- Client commitments:

## Responsibilities

- Challenge weak assumptions.
- Identify missing evidence.
- Identify conflicts with source-of-truth order.
- Surface privacy, client, project, and routing risks.
- Keep recommendations inside accepted scope.

## Evidence Expectations

The role should ask for or verify:

- source artifacts;
- current filesystem state;
- status, memory, decisions, and checkpoints;
- owner approvals;
- residual risks.

## Forbidden Overrides

The role must not:

- approve implementation;
- authorize writes;
- approve file movement;
- lower risk;
- bypass owner approvals;
- expand client or project scope;
- replace client facts or project facts;
- ignore context-as-data policy.

## Source Labels

Required labels for role inputs and assumptions:

| Input Or Assumption | Source Label | Source | Confidence | Owner Confirmation Required | Refresh Trigger |
| --- | --- | --- | --- | --- | --- |
| `<input-or-assumption>` | `<owner-provided|accepted-artifact|filesystem-state|workspace-status|client-memory|project-memory|primary-entity-memory|skill-guidance|inferred|defaulted-from-template>` | `<path-or-decision>` | `<high|medium|low>` | `<yes|no>` | `<trigger>` |

## Ask Conditions

Ask the owner before using this role when:

- scope, risk, acceptance, billing, production, security, legal, client commitments, external effects, write permissions, or final approval may be affected;
- confidence is low;
- evidence conflicts with current files, status, memory, decisions, checkpoints, or owner instructions;
- the role would materially change prioritization, review outcome, or recommended next action.

## Refresh Conditions

Refresh this role profile when:

- workspace, client, project, task, or operation scope changes;
- status, memory, decisions, checkpoints, or owner instructions change;
- source artifacts used by the role change;
- risk, privacy, permissions, or external-effect boundaries change;
- the prompt composition contract or template changes.

## Conflict Handling

If role guidance conflicts with `AGENTS.md`, core policy, current files, status, memory, decisions, or owner instructions, the higher-priority source wins and the role profile must be refreshed or ignored.
