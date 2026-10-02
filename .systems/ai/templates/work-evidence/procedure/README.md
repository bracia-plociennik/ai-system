# Reproducibility Kit v1

Author a workspace-local JSON procedure, never a product fixture with private data.
Use work-evidence-documentation preview before owner-approved write with the
exact returned kit hash. Preview does not execute steps or write a journal.

Required fields: schema_version, procedure_id, version, work_ids, target_outcome,
skills, environment (tool to exact version), prerequisites, inputs, steps
(id/action/expected), tests (id/assertion), stop_conditions, rollback, limits,
source_refs and derivatives.

Inputs/derivatives need source_index, source_sha256, text, text_sha256 (canonical
JSON string digest), purpose=documentation, approved_by=owner and approved_at.
Source bodies and private paths are not copied into the shareable kit.
Review the literal procedure text before disclosure; text approval is not approval
to run commands. Only the selected mocked environment is permitted in the pilot.

Write is immutable by procedure/version. Rebuild after a material source change
requires a new version and approval; previous replay evidence is retained.
Only record-replay with signed human evidence and separately hash-bound owner
verification can claim replay-passed. Local tests are not a human replay.
Signature verification and actual human independence remain owner review duties.
