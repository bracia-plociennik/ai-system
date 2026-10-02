# Local Safeguards

Use the approved isolated pinned Python. check-work-evidence accepts
WORK_EVIDENCE_PYTHON pointing to that interpreter; never auto-installs packages.
init-preview binds config/entities for one existing owner-selected workspace.
init needs exact preview hash and approval; existing namespaces are not replaced.
Interrupted initialization is operator-reviewed, never automatically erased.

backup-preview takes {"paths":[...]} with exact operational paths, not a whole
workspace or private tax/source dump export. backup needs fresh hash and approval.
Immutable copies and full operational inventory hashes remain local.
Private tax backups require a separate human-led policy.

restore-preview binds backup and current inventory/target hashes; use its result
as the reviewed local request. restore requires exact hash and approval. New
canonical revisions or edits after review stop apply. Original bytes are retained;
interrupted writes resume only the same journal. No deletion or silent merge.
Changed config/registry requires operator identity review, not generic restore.
Close Excel; owner-file detection is only a heuristic. Rebuild/re-export after
canonical/source verification. Renew consumer approvals when inputs change.
