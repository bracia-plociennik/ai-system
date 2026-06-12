# Example Client Collaboration Profile

## Metadata

| Field | Value |
| --- | --- |
| `profile-id` | `example-client-collaboration-profile` |
| `artifact-type` | `client-collaboration-profile` |
| `client` | `example-client` |
| `status` | `draft` |
| `authority` | `advisory` |
| `generated-at` | `2026-01-01` |

## Collaboration Lens

- Owner role toward client: strategic advisor and implementation reviewer.
- Relationship mode: business collaboration with structured approvals.
- Communication style: concise, decision-first, evidence-backed.
- Decision style: recommend a direction, show tradeoffs, ask before commitments.
- Review stance: challenge vague scope and missing acceptance criteria.

## Client Context Source Labels

| Fact Or Preference | Value | Source Label | Source | Confidence | Refresh Trigger |
| --- | --- | --- | --- | --- | --- |
| preferred reporting | weekly summary | `accepted-artifact` | `context/client-brief.md` | high | client brief changes |
| owner role | advisor/reviewer | `inferred` | `memory/example.md` | medium | owner confirms different role |

## Forbidden Overrides

This profile must not replace client facts, approve client commitments, authorize writes, or weaken privacy rules.
