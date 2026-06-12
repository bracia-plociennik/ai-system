# Example Variable Pack

## Metadata

| Field | Value |
| --- | --- |
| `variable-pack-id` | `example-project-variable-pack` |
| `status` | `draft` |
| `scope` | `project` |
| `authority` | `advisory` |
| `generated-at` | `2026-01-01` |

## Variables

| Variable | Value | Source Label | Source | Confidence | Owner Confirmation Required | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `role` | website strategy reviewer | `accepted-artifact` | `status.md` | high | no | advisory lens only |
| `audience` | business owner | `inferred` | `context/example.md` | medium | yes | affects communication framing |
| `work-mode` | audit | `owner-provided` | owner prompt | high | no | used for response shape |

## Assumptions

| Assumption | Source | Impact | Ask Owner Before Use |
| --- | --- | --- | --- |
| project is pre-implementation | `status.md` | limits scope to planning/review | no |

## Forbidden Overrides

This variable pack must not override accepted scope, owner approvals, write conditions, stop conditions, or evidence requirements.
