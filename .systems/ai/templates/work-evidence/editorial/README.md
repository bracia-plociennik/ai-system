# Editorial Request

Request: schema_version=1, topic_id, claims, brands, queue_start (Monday), weeks
(1-8), drafts. Configure existing local destination_root under editorial_policy;
no automatic init or cloud export. See work_evidence_editorial.py for strict fields.
Claims explicitly bind committed entry/hash and one of its source refs, optional
procedure ID/version/kit hash, derivative text, sensitive_terms, replacements,
privacy_state, supported, review checklist and owner source approval.
Source approval hashes every claim field except approval, purpose editorial-source.
Never omit known identifiers or combined quasi-identifiers from human review.

Brands declare ID/kind/name, primary/optional languages, newsletter title and
anchor; two anchors differ by seven modulo fourteen days. Variants share slots.
Draft body uses {{claim:ID}} for every declared claim; other prose is commentary
and still requires semantic review. Include draft_id/brand/language/channel/slot/
claim_ids/title/body/approval. Null approval leaves needs-review. Source and draft
approvals are separate. Approved draft purpose is editorial-draft, never publish.
Original request/private provenance is not a shareable export. Review queue and
language metrics are local and advisory; do not infer real audience success.
