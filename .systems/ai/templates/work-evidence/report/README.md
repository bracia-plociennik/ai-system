# Local Client Report

Use work-evidence-report preview with explicit workspace-relative policy JSON.
Policy fields: schema_version=1, report_id, registered recipient_id, client_ids,
project_ids (empty means all their projects), start, end_exclusive,
coverage_attested (false unless owner confirms completeness), texts, recurring_care.

Each text has entry_id, entry_hash, recipient_id, text, text_hash, purpose=
client-report, approved_by=owner and approved_at with UTC offset. No fallback
to internal notes. Hashes use canonical work-evidence digest, not display text.

Care rows have recipient_id, source_ref and derivative. Derivative approval has
source_index=0, text, source_sha256, text_sha256, purpose=client-care,
approved_by=owner, approved_at. It describes contractual scope without time claims.

write requires --owner-approved and --expected-hash from current preview.
Only client-draft is intended for recipient review; private-manifest stays local.
Empty/unknown coverage does not prove no work. No send, tracking, cloud/API sync.
