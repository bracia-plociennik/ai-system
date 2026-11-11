# Noncanonical SPOR Drafts V1

## Scope and authority

`spor-check-in-draft-v1` is an optional owner-approved output mode for the
existing SPOR scheduler. Explicit standing consent covers creating one private
draft for the current local run date and updating it from actual owner replies
in its selected chat. A policy flag, source, nonce, payload, receipt or stored
approval reference never authenticates that consent. Check the actual owner's
scope/revocation before writes. Without installed support or verified consent,
retain the read-only proposal route. No new scheduler, background writer,
canonical approval store or automatic TaskNotes.

## Artifacts and form

Store Daily under `personal-ops/check-in-drafts/daily/YYYY/YYYY-MM-DD.md` and
Weekly under the matching `weekly` directory using the preparation date.
Metadata separates proposal review/plan periods, created/updated timestamps,
revision, source references, lifecycle and optional canonical receipt.
The type is `spor-check-in-draft-v1`, never a canonical V4 type. Only canonical
roots feed aggregates, TaskNotes or the calendar; do not broaden those readers.
Do not use drafts as evidence of execution or an approved future plan.

The writer renders the complete matching SPOR template. Its `describe` action
provides stable field IDs and labels. Every field value starts with Potwierdzone,
Zaplanowane, Propozycja AI or Nieznane — pytanie followed by a colon. Complete
Life Alignment text and every section/field remain present. Automatic current
mental/body and Life Alignment answers must remain UNKNOWN. Unknown is not zero
or failure; confirmed past facts require dated source evidence. Do not copy
Raw, OCR, attachments, secrets or Daily Working Dump into the payload. Preserve
all source/privacy boundaries in spor-proposals.md.

Morning owner replies normally provide the previous day's review; absence of
an evening closure is not process debt or a requirement to add an evening run.
Saturday drafts review Monday–Friday and plan the next Monday–Friday. Canonical
Weekly keeps its existing Monday–Sunday review contract, with missing days
explicitly unknown. No historical source rewrite or retrospective backfill.

## Writer interface

`.systems/scripts/manage-personal-ops-draft <action> --workspace <selected-root>
--date YYYY-MM-DD` supports:

- `describe`: field map, expected ID, periods and computed relative draft path;
- `read`: metadata, body and current SHA-256; no writes;
- `emit --nonce <dispatcher-token>`: read a JSON create package on stdin and
  emit one `SPOR_DRAFT_REQUEST_V1 <JSON>` line on stdout; no writes;
- `create --owner-approved`: consume `{contract, proposal_id, fields, sources}`
  from stdin; `fields` must contain every described ID and labeled value;
- `update --expected-sha256 <read-hash> --owner-reference <actual-chat-reply>
  --owner-approved`: stdin is a map of changed field IDs to labeled values;
- `mark-approved --expected-sha256 <read-hash> --canonical <relative-path>
  --source-sha256 <saved-hash> --owner-reference <current-approval>
  --owner-approved`: mark the draft only after native canonical capture and QA.

All write flags attest caller responsibility; they grant no authority. A scheduled
dispatcher exposes only create, never update/mark-approved. It computes the
workspace/date/path and rejects unknown keys, wrong identity, source errors,
Sunday, date rollover and existing canonical. Source preparation stays read-only.
Validate package completeness and size before persistence. Use no-follow dirfds,
private files, a cooperating writer lock, fsync and atomic create-if-absent.
Never overwrite an existing automatic draft, including an owner-edited one.

Owner replies update this same artifact without another save-confirmation round
when covered by the standing consent. First read the current file/hash; patch
only answered fields, keep unrelated manual edits verbatim and record the actual
owner reply reference. A stale hash, altered field markers or lifecycle conflict
requires reread/reconciliation. Locks coordinate cooperating writers; filesystem
editors do not supply an atomic external compare-and-swap guarantee.

## Dispatcher rendezvous and delivery

The model retains read-only sandbox/network restrictions. The existing dispatcher
reads a complete successful native `commandExecution` output from its own verified
queued turn. It accepts only one well-formed emit envelope containing the current
run nonce and proposal identity. Source excerpts, user messages, other turns,
agent commentary, failed/running commands and truncated output cannot trigger a
write. Never evaluate commands or paths from the payload. Unknown RPC/tool approval
requests remain refused. The nonce binds transport to the run, not owner consent.

After validated persistence and full readback the dispatcher records a metadata-only
draft-saved receipt. The model polls the computed draft via the read-only reader,
then publishes its full body and source link as `DAILY CHECK-IN (SPOR) — szkic do
uzupełnienia` or the matching Weekly. Never claim save success before readback.
The dispatcher verifies the persisted final against the saved body/hash and ID;
only then records chat completion. Missing chat/history or ambiguous submission
fails closed. No private form values, sources or RPC exception text in journals.

Keep preparation/reservation, artifact saved and chat published as separate
events. A failed publication retains the artifact. Explicit same-date delivery
recovery checks history first and republishes that existing artifact without
regeneration or rewriting. Repeated successful runs, Sunday and missed dates
produce no new publication. Date rollover blocks further writes/publication.

## Approval and rollback

Canonical capture requires the owner's current scope-specific approval. Use the
existing V4 validation, real post-write aggregate refresh, native renderer and
approved calendar procedure. TaskNotes require approval covering tasks. Only then
record the native canonical path/hash in the draft; never delete the draft.
The receipt helper does not create canonical artifacts, run sync or export events.

Enable draft mode only after product tests, semantic/privacy review, official
product update and local dispatcher integration tests. Retain one timer/timezone
and dedup history. Disable draft mode to return to the existing read-only proposal
route; retain all drafts and historical receipts. Do not simulate first real-run
delivery verification. No historical migration or canonical schema changes.

## Question queue presentation v1 / form version2

New describe defaults to form_version=2; an existing draft returns its stored version. The transport contract stays spor-check-in-draft-v1. Legacy four-key packages remain supported and retain unchanged v1 templates and field IDs. New packages add exactly `form_version:2` and `questions:{contract:"spor-question-queue-v1",items:[...]}`. The new v2 templates preserve field count/order and use declarative labels. Template hashes and every lifecycle/CAS guard remain enforced per saved form version; no migration or historical rewrite.

Each question is inert data: `id` K1/K2/... for `priority:essential`, O1/O2/... for `priority:optional`; `kind:question|decision`; nonempty unique `field_ids` from describe; `text`; optionally `recommendation` and `reason`. IDs and texts are unique; every UNKNOWN field has a question reference. Default target is at most four essential Daily/five Weekly; additional actual blockers require a concrete `overflow_reason`. Life Alignment is an essential question with its exact full text from describe and the answer field reference. Initial mental/body/alignment UNKNOWN protections remain unchanged.

Fields hold labeled data, context and marked proposals, without owner prompts. The writer appends both queue sections after final Review. `spor_draft_chat.chat_body(saved)` produces the deterministic numbered projection, field references and complete final queue; the installed local dispatcher delegates new forms to it. It hides only technical markers/empty example tables, preserves stored values/manual notes, and performs no I/O. Sources stay linked after the form.

Owner updates may retain the legacy field patch or use `{"fields":{...},"answered_question_ids":[...]}` for version2. The caller normalizes actual owner replies; the product does not infer semantics or approval from K/O IDs. Retire only questions covered by the actual owner field patch, with fully known referenced fields and an actual changed referenced field. Explicit answered IDs additionally attest the mapping and are rejected while any referenced answer remains unknown or an AI proposal. Partial answers retain the question, optional omissions retain UNKNOWN, stale hashes or edited queue structure stop before writing. Unrelated owner notes remain verbatim. Scoped canonical finalization resolves fully answered question references from its approved field patch, preserving optional unknowns; it restores the native V4 Review question without changing canonical schemas, subjective answers or counters.

Consumer first, then the guarded local scheduler. Never import a development module into the live dispatcher. Legacy installations continue old behavior until an official approved product update supplies the new consumer. Publication/update/full release QA retain their existing independent authority and evidence gates.
