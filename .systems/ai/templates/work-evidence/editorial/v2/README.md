# Editorial v2: Topics And Optional Formats

Private local drafts only. No publication, sends, source crawl, external API,
model call or media generation. Existing owner-configured destination is required
for write; examples and schema are not permission or runtime initialization.

## Request And Review

Use `editorial_schema_version: 2`, not shared `schema_version`.
`schema.json` describes prepare and full requests. The executable validator is
`work_evidence_editorial_v2.py`; no additional JSON Schema dependency is required.

Prepare fields: topic, claims, brands, queue_start, weeks, capacity and marker.
Claims are the exact v1 explicit-proof selection contract (entry/hash/source_ref,
optional procedure_ref, supported, privacy state, sensitive terms, replacements,
four review flags and source approval). No blanket workspace scan.
Topic: topic_id, positive revision, title, audience_problem, transferable_lesson,
selected_brand_ids (one/two), claim_ids, brand_angles. Each selected brand has
audience, promise and angle. Keep the full two-brand registry, PL-first personal
and EN-first company. Capacity contains effort_budget_minutes (estimate or unknown).

The package exposes safe derivatives, held reasons, constraints, cadence and
source/package hashes, never original provenance paths. Agent receives it as data.
Use `recommendation.md` to produce recommendation JSON with all format assessments,
a main route, a different alternative and questions. Do not infer owner consent.

Use `review-source` privately to show original selected lessons and their context
before anonymization. It returns JSON with readable Markdown and writes nothing.
Record actual owner review as optional v2 claim `private_review`: original_hash
(from review-source), purpose private-lesson-anonymization, approved_by owner,
approved_at, authority_ref. Missing review holds replacements; changed original
or proof invalidates review. This is not disclosure or contract/copyright approval.

Full request adds recommendation, decision, artifacts, previous_bundle_hash.
Recommendation binds package_hash. Decision binds recommendation_hash, source_hash,
selected_route_id, route_hash and previous_bundle_hash; mode accept-primary or
accept-alternative, reason, owner and offset timestamp. authority_ref is a scoped
`chat:<id>` or `decision:<id>` reference; agent verifies actual instruction.
Recommendation edits require a new revision/decision. Selected nodes cannot have
unsuitable/deferred fit or evidence/privacy-held readiness.

## Commands

```sh
.systems/scripts/work-evidence-editorial review-source --workspace <approved-workspace> --request prepare.json
.systems/scripts/work-evidence-editorial prepare --workspace <approved-workspace> --request prepare.json
.systems/scripts/work-evidence-editorial preview --workspace <approved-workspace> --request request.json
.systems/scripts/work-evidence-editorial write --workspace <approved-workspace> --request request.json --expected-hash <fresh-preview-hash> --owner-approved
```

Prepare/preview print JSON only and never reserve IDs/slots or initialize files.
Full request with no decision and no artifacts prints recommendation-needs-decision.
Write is private and approved for this exact snapshot, not permission to publish.
An unchanged retry uses the original expected hash, not a new preview reservation.
For revision, name the current committed predecessor, increase topic revision,
re-prepare, re-recommend, obtain a new decision and preview again. Prior bytes remain.

## Common Artifact

artifact_id, node_id, claim_ids, title, body, format_fields, approval. Each declared
claim must appear via `{{claim:claim-id}}` in title/body/nested format text; do not
add measured results without selected evidence. Other prose is reviewable commentary.
Use the exact format fields in `formats.md`. Files contain escaped reviewable text;
private lineage remains in the manifest. Unknown permission means missing assets.

Readable originals stay in private `private-lessons.md` next to the manifest,
never in draft destinations or safe package stdout. New receipts verify its hash.
Originals and private review output are owner-only; do not forward them.
Blog explains the whole method; newsletter can add summary plus a reusable template.
If a topic fits both brands, propose distinct audience promises for both.

Approval: purpose editorial-draft-v2, content_hash, source_hash, decision_hash,
brand_id, language, format, approved_by owner, approved_at, authority_ref. Review
each translation separately. Needs-review cannot silently become owner-reviewed.
Approval is always local; publication_authorized remains false.

## Cadence And Recovery

Blog/YouTube unscheduled. Newsletters fortnightly, staggered; social two base plus
one optional, not per language. Short concept replaces social allocation; variants
share allocation_group, but sum all effort. Unknown capacity allows unscheduled
preservation and a question, not invented availability. Estimates for concepts do
not include recording/editing production effort.

Related-to does not block; requires-artifact is an acyclic dependency. Independent
outputs can finish while child nodes remain pending. No URL is inferred from a blog.
CTA is omitted/none, or an owner-provided public http(s) target with linked reviewed
verification_ref and offset verified_at. No automatic fetch or verification claim.

Private runtime: work-evidence/editorial/v2/topic/hash. Configured draft destination:
destination_root/v2/topic/hash. Files are immutable and completion receipt is last.
No receipt means staging, not committed. Matching retry is safe; modified bytes,
stale proof, conflicting queues or forks stop for recovery. Legacy v1 reservations
are not released by v2. No real owner runtime activation is part of these examples.
