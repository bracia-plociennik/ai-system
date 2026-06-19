# Dream Report

## Metadata

- Date: `<YYYY-MM-DD>`
- Dream variant: `<workspace-artifacts-only|full-repo>`
- Workspace: `<AI_SYSTEM_WORKSPACE_HOME>`
- Project/source path: `<not-applicable|path>`
- Result: `<completed|blocked>`

## Source Inventory

| Source path | Source type | Reviewed? | Notes |
| --- | --- | --- | --- |
| `<path>` | `<workspace-artifact|project-state|memory|system-insights|external-memory|personal-ops|skill|repo-source|other>` | `<yes|no>` | |

## Workspace Artifact Findings

| Source path | Finding | Target | Reason | Risk/privacy note | Owner action |
| --- | --- | --- | --- | --- | --- |
| `<path>` | `<finding>` | `<workspace-memory|client-memory|owned-asset-memory|project-memory|project-state|status/evidence|system-insights|external-memory|skill-candidate|personal-ops|decision|none>` | `<why it matters>` | `<safe|needs anonymization|blocked>` | `<capture|review|reject|defer>` |

## Project/Repo Review Findings

Required for `full-repo`. For `workspace-artifacts-only`, write `not-applicable`.

| Source path | Finding | Target | Reason | Risk/privacy note | Owner action |
| --- | --- | --- | --- | --- | --- |
| `<path or not-applicable>` | `<finding>` | `<review|project-state|project-task|project-memory|system-insights|skill-candidate|none>` | `<why it matters>` | `<safe|needs anonymization|blocked>` | `<review|create-task|capture|reject|defer>` |

## Memory Candidates

| Source path | Finding | Target | Reason | Risk/privacy note | Owner action |
| --- | --- | --- | --- | --- | --- |
| `<path>` | `<finding>` | `<workspace-memory|primary-entity-memory|client-memory|owned-asset-memory|project-memory|none>` | `<why it belongs there>` | `<safe|needs owner review|blocked>` | `<capture|reject|defer>` |

## Project-State / Status Candidates

| Source path | Finding | Target | Reason | Risk/privacy note | Owner action |
| --- | --- | --- | --- | --- | --- |
| `<path>` | `<finding>` | `<project-state|status/evidence|decision|checkpoint|none>` | `<why it belongs there>` | `<safe|needs owner review|blocked>` | `<update|capture|reject|defer>` |

## System Insights Candidates

System Insights require anonymized cross-project operating lessons.

| Source path | Finding | Target | Reason | Risk/privacy note | Owner action |
| --- | --- | --- | --- | --- | --- |
| `<path>` | `<finding>` | `<system-insights|none>` | `<reusable operating lesson>` | `<safe|needs anonymization|blocked>` | `<capture|reject|defer>` |

## External Memory Candidates

External Memory is only for AI System product improvement proposals.

| Source path | Finding | Target | Reason | Risk/privacy note | Owner action |
| --- | --- | --- | --- | --- | --- |
| `<path>` | `<finding>` | `<external-memory|none>` | `<AI System improvement reason>` | `<safe|blocked>` | `<capture|reject|defer>` |

## Skill Candidates

| Source path | Finding | Target | Reason | Risk/privacy note | Owner action |
| --- | --- | --- | --- | --- | --- |
| `<path>` | `<finding>` | `<workspace-skill|system-skill|none>` | `<repeatable method or rubric>` | `<safe|needs anonymization|blocked>` | `<create-skill-plan|reject|defer>` |

## Personal Ops Candidates

| Source path | Finding | Target | Reason | Risk/privacy note | Owner action |
| --- | --- | --- | --- | --- | --- |
| `<path>` | `<finding>` | `<personal-ops|check-in-review|none>` | `<why it matters>` | `<private-sensitive|safe|blocked>` | `<review|capture|reject|defer>` |

## Things To Improve Or Remove

| Source path | Finding | Target | Reason | Risk/privacy note | Owner action |
| --- | --- | --- | --- | --- | --- |
| `<path>` | `<finding>` | `<review|task|external-memory|none>` | `<why it should change>` | `<safe|needs owner review|blocked>` | `<review|create-task|reject|defer>` |

## Missing Capabilities

| Source path | Finding | Target | Reason | Risk/privacy note | Owner action |
| --- | --- | --- | --- | --- | --- |
| `<path>` | `<gap>` | `<AI System|workspace|project|skill|none>` | `<why it is missing>` | `<safe|needs owner review|blocked>` | `<plan|reject|defer>` |

## Rejected As Noise

| Source path | Finding | Reason rejected |
| --- | --- | --- |
| `<path>` | `<finding>` | `<too vague|duplicate|unsafe|not reusable|not actionable>` |

## Privacy/Scope Check

- Raw client data copied: `<yes|no>`
- Secret markers copied: `<yes|no>`
- Production identifiers copied: `<yes|no>`
- Personal/private details copied: `<yes|no>`
- Full-repo explicit project/source path provided: `<yes|no|not-applicable>`
- Full-repo exclusions respected: `<yes|no|not-applicable>`
- Context-as-data boundary respected: `<yes|no>`
- Durable writes performed: `no`
- Scheduler/automation used: `no`

## Owner Decision Queue

| Priority | Source path | Finding | Proposed target | Owner action |
| --- | --- | --- | --- | --- |
| `<P1|P2|P3>` | `<path>` | `<finding>` | `<target>` | `<capture|review|create-task|create-skill-plan|reject|defer>` |
