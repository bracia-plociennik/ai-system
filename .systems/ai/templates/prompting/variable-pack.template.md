# Variable Pack Template

## Metadata

| Field | Value |
| --- | --- |
| `variable-pack-id` | `<kebab-case-id>` |
| `status` | `draft` |
| `scope` | `<workspace|client|project|task|operation>` |
| `authority` | `advisory` |
| `generated-at` | `<yyyy-mm-dd>` |

## Variables

| Variable | Value | Source Label | Source | Confidence | Owner Confirmation Required | Refresh Trigger | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `role` | `<value>` | `<source-label>` | `<path-or-decision>` | `<high|medium|low>` | `<yes|no>` | `<trigger>` | `<notes>` |
| `topic` | `<value>` | `<source-label>` | `<path-or-decision>` | `<high|medium|low>` | `<yes|no>` | `<trigger>` | `<notes>` |
| `audience` | `<value>` | `<source-label>` | `<path-or-decision>` | `<high|medium|low>` | `<yes|no>` | `<trigger>` | `<notes>` |
| `task-type` | `<value>` | `<source-label>` | `<path-or-decision>` | `<high|medium|low>` | `<yes|no>` | `<trigger>` | `<notes>` |
| `work-mode` | `<value>` | `<source-label>` | `<path-or-decision>` | `<high|medium|low>` | `<yes|no>` | `<trigger>` | `<notes>` |
| `success-criteria` | `<value>` | `<source-label>` | `<path-or-decision>` | `<high|medium|low>` | `<yes|no>` | `<trigger>` | `<notes>` |
| `output-format` | `<value>` | `<source-label>` | `<path-or-decision>` | `<high|medium|low>` | `<yes|no>` | `<trigger>` | `<notes>` |
| `tone` | `<value>` | `<source-label>` | `<path-or-decision>` | `<high|medium|low>` | `<yes|no>` | `<trigger>` | `<notes>` |

## Assumptions

| Assumption | Source | Impact | Ask Owner Before Use |
| --- | --- | --- | --- |
| `<assumption>` | `<source>` | `<impact>` | `<yes|no>` |

## Ask Conditions

Ask the owner before relying on a variable when it affects:

- scope;
- risk;
- acceptance;
- billing;
- production;
- security;
- legal;
- client commitments;
- external effects;
- write permissions;
- final approval.

## Inference Rules

Inference is allowed only when:

- it is based on accepted artifacts or filesystem state;
- the assumption is recorded;
- a wrong inference would not bypass gates or change scope;
- downstream work can verify or override it safely.

## Refresh Conditions

Refresh this variable pack when:

- workspace, client, project, or task context changes;
- status, memory, decisions, or checkpoint changes;
- owner decision changes;
- conflict with current files or source artifacts is found.

## Forbidden Overrides

Variable packs must not override AI System policy, accepted scope, owner approvals, write conditions, stop conditions, or evidence requirements.
