# Local finalization examples

No example authenticates consent or calls a real integration.

## Document (AI System)

Preview: `printf '%s' '{"format":"csv","path":"tasks.csv","columns":["task","description"],"rows":[["Example","UNKNOWN, not zero"]],"body":""}' | python3 -B .systems/scripts/finalize-document --root /absolute/test-workspace`

Create only after current scoped approval: add `--apply --owner-approved`.
For Markdown use format markdown, columns/rows empty arrays and explicit body.
Existing destination fails closed; no overwrite.

## SPOR (AI System)

`finalize-personal-ops-check-in --workspace /absolute/test-workspace` reads JSON stdin:
date, draft_sha256, fields (answered stable field IDs only), complete properties
(native V4 schema), confirmed_properties (explicitly source/owner normalized keys),
owner_reference. Obtain the current draft/hash first. Preview returns the diff and
required stages. No regex/LLM inference inside the writer; normalize the properties
once and review their semantics against owner replies. `--apply --owner-approved`
uses native mandatory consumers; tasks/calendar require explicit reviewed hooks via
finalization_artifacts.finalize_spor. Test that API with synthetic callables, never
actual clients. Inspect a partial receipt; resume_spor accepts read-only checks for
completed effects. An uncertain effect cannot be replayed automatically. Preserve the returned receipt and
pass the identical selected integrations on recovery. Recorded completed/attempted stages
need source-bound read-only checks; only not-applied permits retry of an attempted stage.
Missing checks stop recovery. Duplicate integration names fail before writing.

## Code task (AI Workflow or AI System)

Construct a task-finalization-v1 JSON record with current inputs and existing
review/test readback hashes. Use steps tests -> review -> required owner gate,
keeping the owner gate pending until actual evidence exists. Pipe to
`prepare-finalization --root /absolute/test-repository`.

For an earlier partial run, retain succeeded steps with their readback evidence;
mark a lost external result uncertain. Changed inputs invalidate the projection.
Do not paste executable commands into records. Outcome is only ready-for-review,
never a project PASS or approval. Use existing timing_summary/process_timing for
intervals; overlap, unknown time and estimates retain their existing semantics.
