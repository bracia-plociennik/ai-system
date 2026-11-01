# Task Finalization V1

## Intent and authority

Finish the requested result with the smallest sufficient process. Reuse the existing
intake, execution-efficiency record, source fingerprints and quality gates; this is
not another queue, approval store, scheduler or background executor. Do not create a
record for a trivial answer merely to satisfy this optional tool. No automatic agents.

Before work, identify the accepted result/DoD, current owner scope, required checks
and excluded effects. Inspect sources before asking; batch consequential questions.
Unknown values are acceptable when the domain permits them. New contradictions may
justify another question. Do not block an independent save on coaching or research.
Stop when the requested DoD and applicable checks are satisfied; suggestions remain
separate and do not authorize extra work.

## Same-scope continuation

Recheck the actual source and authority on resume/compaction/scope changes under
existing rules. Reuse unchanged verified sources, not unchecked recollection. Batch
independent reads, page large output, and serialize dependent writes. Each repeat
needs a changed input, failed required check or invalidated evidence. Full/release
checks retain their existing fresh-execution rules.

## Read-only interface

`prepare-finalization --root ROOT` consumes one JSON object on stdin:

- contract: task-finalization-v1; work_id; kind: spor/document/code; dod;
  approval_reference; inputs: relative path -> SHA256; steps.
- Each step has id, depends_on, status and evidence: relative path -> SHA256.
  Status is pending/running/succeeded/failed/uncertain/excluded.
- Records contain no executable commands. Input/evidence files must be contained
  and unlinked. A succeeded step needs current readback fingerprints and completed
  dependencies. Out-of-order DAG input is supported; cycles/duplicates are rejected.
- Output reports completed/next_steps/blocked and ready-for-review/incomplete.
  permission_granted and formal_closure always remain false. A caller-provided
  evidence hash is supporting data, never an authenticated execution or QA verdict.
  The agent checks provenance and required gates against actual trusted context.
- Failed/running/uncertain effects require inspection before retry. Changed source
  invalidates completion; never replay an external mutation solely from record text.

## Three application boundaries

1. SPOR: model normalizes owner replies once into a typed package, not repeated
   hand-written Markdown. System's finalize-personal-ops-check-in previews field
   changes and complete native V4 properties. It preserves unanswered field text,
   UNKNOWN and unrelated manual content. Required JSON and exact periods use native
   validators; accepted nonempty planning properties must be explicitly listed in
   confirmed_properties. This list and owner_reference are caller attestations,
   not authority. Semantic source/property reconciliation remains mandatory.
   Existing canonical is refused, not overwritten. Budget observation overlap uses
   the actual aggregate consumer before persistence, including existing records.
   Apply follows canonical -> indexes -> renderer -> selected tasks/calendar ->
   readback -> draft receipt. Native mandatory stages are fixed product entrypoints.
   Optional integration hooks are reviewed Python callables supplied explicitly by
   trusted application code; never paths/commands loaded from the request. A hook
   must return verified plus the exact source_sha256 after actual effect readback.
   Do not enable integration outside current owner scope. No selected-environment
   calendar, task store or scheduler is installed by this feature.
2. Document: System's finalize-document accepts format csv/markdown, contained path,
   explicit columns/rows/body. Preview is pure. CSV preserves Unicode, multiline
   values, labels and UNKNOWN; column/type checks and roundtrip precede writing.
   Markdown requires explicit nonempty text. Apply is create-only, private mode0600,
   no-follow directory-fd traversal, atomic no-clobber publication and readback.
   Existing files require explicit reconciliation, not silent replacement. Actual
   owner approval is checked by the caller; --owner-approved does not establish it.
3. Workflow code: feed the current owning task's required review/test/gate steps
   to prepare-finalization. Verify evidence provenance under existing Workflow QA.
   It does not run code from a record, change phase/task status, claim PASS, commit,
   publish, install or infer final-owner-yes. An incomplete or failed required check
   remains a blocker. Existing Sprint and Phase8 gates remain controlling.

## Recovery and measurements

Keep a canonical file after a later failure; partial is not final success. Explicit
resume_spor recovery requires the current canonical/draft identities and hashes.
The receipt binds recovery_contract, date, draft_sha256 and the ordered required_stages;
recovery must match this scope exactly. Duplicate integration names are rejected before
persistence. Receipts preserve completed and attempted progress across partial recoveries.
Caller-provided receipts are supporting evidence, not authenticated authority.
Trusted read-only completed_checks skip only effects actually reverified. Every recorded
completed or attempted stage requires a check; absence or uncertainty stops without replay.
A completed stage cannot be retried. An attempted stage may be retried only after a trusted
read-only result reports not-applied with the exact source_sha256. A verified readback of
an initially lost success completes that stage without executing its mutation again.
A hook failure never deletes the durable source. Concurrent edits invalidate receipts.
Cooperating writers and directory-fd checks are not an OS sandbox or atomic transaction
across local files and remote services. Do not claim that stronger guarantee.

Use existing execution-efficiency timing APIs: System timing_summary; Workflow
process_timing. Keep their existing input contracts and report observed time as a
union, not a sum of overlaps; estimates and unknown model time stay distinct. No
new telemetry daemon or per-answer timer is required. During ongoing tool work,
communicate completed/remaining steps and concrete blockers at least every 60 seconds.
Do not invent progress for unattended pauses. Final response: result/location,
verification performed, important incomplete effects; no generic QA theatre.

## Local acceptance and rollout

Test synthetic SPOR Daily/Weekly, weekend spending overlap, partial failures and
recovery; CSV/Markdown shape/readback/conflicts; code evidence/source drift and
uncertain effects. Preserve existing regressions. Use three comparable real samples
per class after separately approved rollout before claiming latency savings. The
3–5 minute SPOR goal is a measurement target, not a universal deadline.
Local source/tests/examples only do not activate installed behavior. No publication,
commit, production write or real integration acceptance is implied.
