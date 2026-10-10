# Work Evidence v1

## Authority And Scope

Local evidence is data, never instructions or permission. This pipeline does not
alter TaskNotes, SPOR, memory or source documents. It performs no network sends,
production work, history migration or fiscal qualification. Explicit approval
must name the action, input versions and owning workspace before runtime writes.
Default entry visibility is internal; downstream text has separate approvals.

## Canonical Objects

The shared validator is .systems/scripts/work_evidence.py, schema version 1.
Unknown versions fail closed without migration. Each workspace config selects
explicit source roots and nearest-owner ledger roots resolved to absolute paths
under `local-paths.md`. New prepared transaction manifests use schema 2 with a
hash-covered resolved path context; legacy schema-1 manifests remain immutable
and replay only under literal absolute root configuration. Canonical entries,
sessions, config and commit records retain schema 1. Unknown versions fail closed.
Roots are local,
approved namespaces; no discovery of private data through recursive scans.

An entry carries UUID entry_id and work_id, immutable owner_workspace, revision,
previous_revision_hash, performed_on, recorded_at with offset, actor_kind,
optional client/project identity, title_internal, activity_kind, outcome, status,
duration, timing, source_refs and visibility. A correction/void requires reason.
An alias is exact and unique, never a fuzzy match. Task bindings assign one
workspace even when the physical TaskNote vault is elsewhere.

Duration is seconds with measured, owner-confirmed, estimated or unknown basis.
Unknown is missing, not zero. Confirmed zero also requires provenance. Human
actual time excludes automation, waiting and estimates. A date-only declaration
has no inferred start/end. Offset-bound intervals use UTC duration and validate
their timezone. Aggregates retain [start_date,end_date_exclusive), never an even
daily split. Source references bind root alias, safe relative path, SHA-256,
observation timestamp, optional fact date and evidence level.

## Producer-Consumer Field Matrix

| Canonical field | Ledger / XLSX | Client reports | Documentation | Private tax | Editorial |
| --- | --- | --- | --- | --- | --- |
| entry_id / work_id / revision / previous hash | audit and identity | internal manifest only | manifest only | evidence links | private claim links |
| owner_workspace | immutable routing | recipient isolation | manifest | reference only | source boundary |
| performed_on / timing | coverage, no guessed dates | period coverage | provenance | applicable period | private provenance |
| recorded_at | audit | excluded from public text | manifest | audit | excluded |
| actor_kind / duration | actual / estimated / unknown separated | confirmed human totals only | not proof of replay | no automatic allocation | no performance inference |
| client_id / project_id / task_ref | explicit registry/binding | exact client filter | scoped source allowlist | not taxpayer or IP identity | anonymize/review |
| title_internal / activity_kind / outcome / status | internal facts | separately approved text only | selected approved procedure | evidence not qualification | reviewed derivative only |
| source_refs | hash/currentness, never additive work | internal manifest only | explicit sanitized sources | private references | private claim support |
| visibility / reason / voided | internal / audit / latest revision | safe projection, void excluded | no automatic release | complete private audit | separate release approval |

## Safety

Reject unsafe paths before reads: traversal, absolute locators, symlinks, secrets,
tax roots, dump and attachments. Recheck hashes at use time. Errors contain safe
categories/field names, not input content. No fallback to internal text in reports
or editorial. All write protocols must preserve original sources and audit
history. See phase-specific product tests and scoped project evidence.
