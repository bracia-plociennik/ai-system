# WEP-CONTENT-011-editorial-routing Specification
Date: 2026-10-03. Mode: solo project task. Risk: high.
Original design status (2026-10-03): ready for artifact QA, then no implementation
authority. Current bounded implementation/review authority is recorded in
decisions/2026-10-05-wep-011-owner-review.md and section 14 below.

## 1. Inputs, Goal And Authority
Inputs: WEP-CR-001 D11-D21, current architecture Editorial v2, current Phase 2 plan/task index and its QA. Baseline code: HEAD 4f26727c9e1e8565db155905a16e114fcfcaf3dc.
Reviewed concrete producers/consumers: .systems/scripts/work-evidence-editorial, work_evidence_editorial.py (editorial_queue, selected_claim, bundle, persist_bundle), existing ledger lock/atomic helpers and .systems/ai/core/work-evidence-editorial.md.
Goal: help the owner choose a justified, source-backed editorial flow, including blog or video concepts where useful, without forcing any format, inventing evidence or publishing anything.
Source of truth: evidence for facts; explicit owner for approval; agent for labeled recommendations only. Formats are consumers of a shared topic, not a mandatory linear funnel.
Historical WEP-008 specification/Quality describes v1 and does not authorize 011.

## 2. Scope And Testable DoD
In scope: independent v2 schema; deterministic prepare; recommendation and owner decision validation; five format assessments per selected brand; safe brief/draft/concept rendering; optional DAG; capacity checks; immutable local persistence; legacy regression and seven semantic examples.
DoD:
1. One topic can select one or both registered brands, with complete format fit/readiness, primary route and one alternative, reasons, gaps, qualitative confidence and estimated effort.
2. Blog/newsletter/social briefs and drafts preserve factual claim lineage; short/long video remain concepts only.
3. Newsletter can be standalone or add distinct value to a useful complete blog; social can be standalone or point to a real verified reference.
4. Owner choice, source privacy, draft review and write permission stay separate. Changed content/sources/choice invalidate the corresponding review.
5. No additional cadence is implied by formats or translations; unscheduled backlog and missing capacity are explicit.
6. Unchanged v1 golden cases, all v2 acceptance cases, persistence failure cases and seven human-reviewed synthetic routes satisfy the QA matrix.
7. No forbidden data, production/media output, external I/O or new ledger/schema/history mutation.
Out of scope: actual publication, CMS/social/email APIs, real video creation or full production scripts, image generation, audience lists, campaign results, tax calculation changes, TaskNotes, cloud sync, scheduler, new dependencies, autonomous source discovery and actual runtime activation.

## 3. Versioning And Compatibility
- Keep shared work_evidence.VERSION=1, ledger entries/config and legacy request schema_version=1 unchanged.
- New requests use editorial_schema_version: 2; they MUST NOT contain schema_version.
- Dispatch by the unique marker before legacy version()/shape(). Both markers, no marker, bool instead of integer, unknown version or extra fields are errors.
- Existing preview/write v1 semantics, shape errors, approval digests, output files and queue stay unchanged.
- v2 helper code may live in work_evidence_editorial_v2.py to avoid destabilizing v1; no generic framework necessary.
- Do not convert previous records or reinterpret old approval hashes. Config's existing editorial_policy.destination_root remains sufficient; v2 data is namespaced under v2/.
- The complete two-brand registry still validates staggered anchors and language policy. selected_brand_ids can contain one or both registry IDs; unselected brands create no topic artifacts.
- A future format/schema change requires explicit versioned contract review; unknown formats fail, not generic fallback.

## 4. Wire Records And Required Fields
All JSON objects are strict: listed fields required unless marked optional; no extra fields. IDs use existing lowercase identifier validator, revisions positive integers, hashes SHA-256 hex, timestamps offset-aware. Text uses existing nonempty safe-text checks unless a field explicitly permits null. Lists unique where IDs are used. No NaN/Infinity, negative effort or empty approval reason.
Inherited Claim and Brand shapes and provenance rules are those of v1. Topic limit: 100 selected claims, 2 selected brands, 40 route nodes, 200 artifacts and 100 dependency edges per route. Five format rows per selected brand; no omitted row to silently mean unsuitable.

| Record | Fields and producer | Validation / consumer |
| --- | --- | --- |
| PrepareRequest | editorial_schema_version, topic, claims, brands, queue_start, weeks, capacity | CLI read-only prepare |
| Preview/WriteRequest | all PrepareRequest fields plus recommendation, decision, artifacts, previous_bundle_hash | CLI preview or gated write; decision nullable, artifacts list; previous_bundle_hash null for first v2 commit, otherwise exact current v2 topic head |
| Topic | topic_id, revision, title, audience_problem, transferable_lesson, selected_brand_ids, claim_ids, brand_angles | agent-authored proposals, not new facts |
| BrandAngle | brand_id, audience, promise, angle | exactly one for each selected brand; no unsupported benefit promise |
| Capacity | effort_budget_minutes (integer or null) | null means unknown, not unlimited; existing slots constrain scheduled items |
| Package | editorial_schema_version, state, topic, claims, held_claims, brands, queue, capacity, source_hash, package_hash, model_calls, publication_authorized | deterministic prepare output; safe derivatives only |
| HeldClaim | claim_id, reason | no original sensitive text/path |
| Recommendation | package_hash, recommendation_id, revision, assessments, primary, alternative, questions | agent-authored; source freshness checked |
| Assessment | brand_id, format, fit, readiness, rationale, evidence_gaps, confidence, effort_minutes | rows for all five formats per selected brand |
| Route | route_id, title, why, tradeoffs, nodes, edges | main and alternative have different route IDs; at least one materially different format/order/hold option |
| RouteNode | node_id, brand_id, language, format, output_kind, objective, claim_ids, allocation_group, slot_id, effort_minutes | existing selected brand/language; slot_id nullable; estimated effort integer or null |
| Edge | from_node_id, to_node_id, relation | same route; no dangling/self links or duplicate edges |
| Decision | decision_id, recommendation_hash, source_hash, selected_route_id, route_hash, previous_bundle_hash, mode, reason, approved_by, approved_at, authority_ref | owner; mode accept-primary/accept-alternative; predecessor binds changed reservation scope as well as selected route |
| Artifact | artifact_id, node_id, claim_ids, title, body, format_fields, approval | agent input; one artifact per chosen node, unless explicit partial subset documented |
| Approval | content_hash, source_hash, decision_hash, brand_id, language, format, purpose, approved_by, approved_at, authority_ref | nullable on draft; nonnull must match all current values |
| AssetNeed | kind, description, permission_state, evidence_claim_ids | concept only; no binary/path loading |
| CTA | text, target_kind, target_url, verification_ref, verified_at | nullable CTA; safe rendering and existing target proof rules below |

Enums:
- format: blog-article | newsletter | social-post | short-video-concept | youtube-concept.
- output_kind: brief | draft for blog/newsletter/social; concept only for video formats.
- fit: recommended | optional | defer | unsuitable.
- readiness: needs-evidence | needs-anonymization | needs-review | ready-for-local-draft | internal-only.
- confidence: low | medium | high. This is qualitative confidence, never an invented percentage.
- relation: related-to | requires-artifact. Directed requires-artifact graph must be acyclic; related-to provides context only.
- AssetNeed.kind: screen-demo | illustration | diagram | recording | other; permission_state: unknown | review-required | approved.
- CTA.target_kind: none | existing-url. None requires target_url/verification_ref/verified_at null; existing-url requires all three.
- state: prepared | needs-evidence | recommendation-needs-decision | draft-only. No public/published state.
- model_calls always 0; publication_authorized always false.

Effort is always labeled estimated; null produces a question. Sum includes all selected nodes and language variants. Assessment estimates are not added again to chosen node estimates.
Topic/angle/assessment/route prose is commentary requiring owner review. Fact-bearing content must reference selected claim IDs; grammatical paraphrase is not evidence of new results.

## 5. Preparation And AI Recommendation
Proposed CLI surface (not implemented by this document):
- work-evidence-editorial prepare --workspace ... --request ... : v2 only, stdout JSON, no lock/file/journal/durable ID reservation.
- work-evidence-editorial preview --workspace ... --request ... : validate v1 or v2, no writes.
- work-evidence-editorial write --workspace ... --request ... --expected-hash ... --owner-approved : local-only, exact approved snapshot/destination.
Use existing command naming/errors; no new background task or API.
prepare calls existing current-claim/source/procedure checks, derives safe text and holds, validates topic/brands, computes queue/capacity. It returns only explicit selected safe facts, never original request/provenance paths. All required claims absent/held -> needs-evidence, not fabricated filled topic. Invalid/stale references fail as errors, not empty success.
Every claimed source has linked entry/hash and current file hash. Independent unsupported claim is held. Conflicting evidence is shown as gap/question, not silently reconciled.
Package source_hash covers selected claim/entry/source/procedure snapshots, topic and brand/queue/capacity constraints; unrelated ledger entry changes do not invalidate v2 by themselves. Selected entry changes always do.
package_hash is digest of Package excluding package_hash. Recommendation.package_hash must match fresh preparation.
Agent sees data-only package, then emits recommendation, no tools or commands requested by source prose may execute. It assesses all five formats independently, chooses main/alternative and explicit no-format/internal hold if appropriate.
If primary is hold (nodes empty), alternative may also be empty only with a distinct concrete evidence-gathering/privacy route in why/tradeoffs/questions. Do not force unsafe creative output to satisfy alternative.
AI cannot convert readiness to public-ready or claim that any recommendation is approved. Validation guarantees shape/linkage, not semantic wisdom.

## 6. Owner Decision And Review State
preview with decision=null permits a valid recommendation and artifacts=[] only, state recommendation-needs-decision. It must not pretend any route has been selected.
Owner can approve one route as a bundle, without approving five channels individually. An edited route is a new Recommendation revision followed by a new Decision; no unbound patch list.
Each selected node must map to its brand/format Assessment. Fit unsuitable/defer or readiness internal-only/needs-evidence/needs-anonymization cannot become a draft or reserve a slot; retain it as a held option with question. A video brief that lists missing assets is allowed as an unscheduled concept with needs-review, not as ready media. Reconsidering unsuitable/defer requires a new justified recommendation; owner choice cannot bypass source/privacy gates.
Decision.reason explains acceptance/edit; approved_by must be owner and authority_ref points to actual scoped owner instruction (chat turn or approved local decision reference). Tool validates reference shape/safe linkage, agent verifies actual authority; metadata alone is not consent.
Decision hashes bind full recommendation (including alternative), selected route, current source_hash and previous_bundle_hash. Source/route/recommendation/predecessor change invalidates the decision. Previous bundle is null before any v2 commit for the topic.
Approval purpose must be editorial-draft-v2. It binds rendered title/body/format metadata/CTA, claim/source hashes, node format/brand/language/slot, output_kind and decision hash. Translation is separately reviewed.
No approval -> safe local draft needs-review. Nonnull stale/wrong-purpose approval -> error, not silently downgraded success.
Existing per-claim editorial-source approval and privacy review remain necessary for an owner-reviewed draft; anonymized-needs-review claims can only produce safe needs-review drafts.
Human identifiers/quasi-identifiers/contracts/copyright review remains required. Redaction never establishes permission. Disclosure outside the configured private destination is not authorized here.

## 7. Format Contracts
Common title/body use {{claim:claim-id}} tokens. Validate exact declared claim coverage across title/body and every nested textual format field before rendering; all claim IDs must be available safe derivatives. Scan rendered strings, metadata and filenames for secret canaries/sensitive terms; escape HTML and Markdown links. Other prose remains explicitly unverified commentary for semantic review.
Do not emit private provenance, local paths, authority references or raw source IDs in shareable draft body. Private manifest retains lineage.
Draft files stay labeled local / publication not authorized, with needs-review or owner-reviewed-draft.

| Format | Required format_fields | Expected value |
| --- | --- | --- |
| blog-article | proposed_slug, meta_description, tldr, key_takeaways, outline, cta | useful complete promised answer; brief may have body as synopsis, draft must have developed sections |
| newsletter | subject, preheader, standalone_value, additional_value, cta | can stand alone; if related to blog, concrete extra example/tool/decision/checklist, not just duplicated article |
| social-post | hook, key_takeaways, cta | useful short message; blog link optional |
| short-video-concept | hook, teaching_point, scenes, assets_needed, cta | scenes are nonempty ordered scene descriptions; AssetNeed list; no finished media |
| youtube-concept | working_title, promise, outline, demo_plan, assets_needed, cta | explicit visual/story justification and source/permission gaps; no full production or upload |
tldr/meta/subject/etc are strings; key_takeaways/outline/scenes are nonempty lists of strings; assets_needed is a list of AssetNeed; cta nullable. proposed_slug is lowercase kebab-case proposal, not reserved/live URL.
newsletter additional_value is nullable for standalone newsletter. It is nonempty when a same-topic blog is related or required; human review checks value is genuinely distinct, not a repeated label.
youtube demo_plan may be a statement that a demonstration is missing and what is needed, but readiness must then defer/needs-evidence, not production-ready.
Concept assets with unknown permission remain needed, not included. No screenshot/attachment ingestion.
An accepted route can choose brief first; actual drafting is explicitly staged, not mandatory expansion to all outputs. Partial artifacts are permitted as a subset of selected nodes; result lists unproduced node IDs as pending, never complete.
Existing-url CTA only for owner-provided http(s) URL whose evidence ref/date is reviewed; no fetching or invented verification. Reject file://, javascript:, embedded credentials/private source links. If no verified target, use null CTA or target_kind=none and a private editorial note; never fake URL. A route edge alone does not prove publication.

## 8. Scheduling And Dependencies
Preserve fortnightly staggered newsletter queue and social slots from brand registry. v2 blog/youtube slot_id always null (unscheduled); newsletter/social/short concept slot may be null or an existing compatible queue slot.
allocation_group identifies variants of one chosen output, scoped to one brand, compatible format and slot. Distinct outputs cannot evade limits by sharing a group. Same-language duplicate in one group is rejected; additional language adds estimated effort, not an additional cadence allowance.
short-video-concept scheduled on social replaces a social-post allocation, never coexists with an unrelated post in the same slot. Producing a concept is not fulfillment of a published video commitment.
Across selected nodes and current committed v2 review queues, the same slot/group/language cannot be double-booked. Existing legacy v1 saved draft slots also reserve capacity; do not ignore them because schema differs. v2 reservation reader uses only the unique current committed successor chain per topic: a new approved request explicitly names previous_bundle_hash, replaces that topic's reservation set, and preserves the prior files. Reject a fork, stale predecessor or cross-topic predecessor. Removing a v2 allocation requires the same new owner-approved route/write decision. Legacy reservations are not modified or implicitly superseded by v2; choose another slot or leave unscheduled until separately approved legacy queue resolution.
Known sum exceeding known budget -> capacity-conflict for scheduling. Unknown any effort/budget -> capacity-unknown and question; allow unscheduled idea/draft, do not claim capacity fits. Estimated effort excludes unavailable production effort only with explicit scope note: video concept estimate is not recording/editing estimate.
requires-artifact edge blocks dependent output until referenced local artifact exists and current hashes validate. related-to never blocks. A blog's existence does not imply URL validity.
No graph cycle or future/nonexistent parent inference. If a prerequisite is delayed, produce independent safe nodes only and list blocked/pending nodes.

## 9. Storage, Hashes And Failure Semantics
Proposed runtime paths: ledger editorial/v2/<topic_id>/<bundle_hash>/private-manifest.json and review-queue.json; configured destination/v2/<topic_id>/<bundle_hash>/<artifact_id>.md. Use safe_path root checks; no auto-init/migration, no absolute user-controlled destination.
bundle_hash binds validated request (including previous_bundle_hash), deterministic prepared package, selected route, rendered outputs and capacity reservation snapshot. Snapshot excludes the topic's named predecessor reservations only when replacement is valid; all other topics and legacy reservations stay included. Use existing canonical digest() routine; approval objects excluded from their own signed payload only. No recursive hashes.
write reacquires ledger lock, re-prepares and rechecks every source, configured destination, decision, slot reservation and expected preview hash. New conflicting queue changes -> stale-approval; fail before writing.
Persist files immutably, then final complete.json receipt in private bundle folder last (topic ID, bundle/source/files hashes, previous_bundle_hash, artifact IDs, pending node IDs). Readers/reservation accounting only consider bundles with valid receipt and matching files and a unique acyclic predecessor chain. The head is derived from receipts under the existing workspace lock, not an unprotected mutable pointer. Exact duplicate apply returns the existing receipt before evaluating a second new reservation.
Crash before receipt leaves incomplete private staging, not committed output. Same approved request/hash can retry and complete identical bytes; changed existing bytes/conflicting snapshot stops for recovery. Do not silently delete files, refund capacity, or overwrite records.
This is atomic-file plus commit-receipt protocol, not multi-file atomic rename. Local incomplete bytes may be visible to the filesystem owner; never claim physical invisibility.
Error output: blocked + stable category + safe object ID only, no source text, tokens or raw paths. Categories reuse existing validation where possible; add unsupported-editorial-version, stale-recommendation, route-decision-required, invalid-editorial-graph, capacity-conflict, capacity-unknown, artifact-dependency-pending as applicable. Unknown capacity is a warning for unscheduled draft, not fatal for preservation.
No bundle should be reported as fully approved when any requested output is held/pending. Separate completed artifact IDs from outstanding nodes and approval state.

## 10. Producer-Consumer Field Audit
| Producer | Required output | Consumer / assertion |
| --- | --- | --- |
| prepare CLI | Package fields, safe Claim or HeldClaim, package/source hashes | recommendation template; no missing constraints silently defaulted |
| agent recommendation template | all Assessment rows, main+alternative Route, questions | preview strict validation and owner review |
| owner decision capture | full Decision, reference to actual instruction | preview/write; recommendation edits require new hash |
| blog/newsletter/social templates | Common Artifact plus exact format_fields | rendering and approval digest include every textual field |
| video concept templates | concept-only Artifact and AssetNeed | renderer never loads/downloads assets or calls media tools |
| renderer | escaped private local files, lineage kept separate | owner review; source/metadata/translation changes break approval |
| persistence | immutable manifests and final receipt | queue/capacity reader excludes incomplete/stale/conflicting writes |
| old v1 CLI | unchanged request/response | original v1 consumers; v2 not passed through version(v1) |

## 11. Acceptance And Failure Matrix (Future Executable Tests)
T01: v1 accepted/rejected golden cases unchanged; all ledger/report/tax/Excel interfaces stay v1; no global schema bump.
T02: prepare/preview leave fixture tree bytes unchanged including missing destination, empty claims, all-held, unsupported claim, source conflicts and injected instructions. No network/model calls.
T03: malformed/ambiguous version, duplicate/unknown brand, missing assessment, enum typo, extra field, path traversal/symlink escape reject.
T04: main/alternative validate with one brand or two, empty hold routes, different language variants; no forced media or newsletter.
T05: wrong or absent decision, forged purpose/identity, stale topic/source/procedure/recommendation/route, changed translation or CTA cannot retain review.
T06: plaintext secret, quasi-identifier combination, private URL, hidden metadata, placeholder claim and mixed permission-bypass wording cannot become approved/exported. Safe 'never publish automatically' is not falsely blocked as an instruction.
T07: brand cadence, existing v1 reservations, null budget, variant summed effort, oversubscription and reel replacement tested; no double-counting allocation. Test v2 release/replace by predecessor, stale/fork/cross-topic predecessor, exact duplicate apply and absence of implicit legacy release.
T08: missing/late dependency, cycle, unrelated edge and unpublished blog link tested. Independent drafts survive; exact pending IDs returned. Unsuitable/deferred/internal-only nodes cannot bypass holds through owner route selection.
T09: every format has all fields, safe escaping and complete token coverage; generated metadata cannot claim measured success without claim evidence.
T10: crash before/after each immutable write/receipt, retry, concurrent writer, changed source between preview/write and tampered receipt stop/resume correctly. No partial current bundle.
T11: new output metadata/approval/queue paths never leak private provenance; no runtime source changes or TaskNote mutations; shared ledger totals unchanged.
T12: semantic review cases below run through real agent recommendations from synthetic packages; record exact input/output hashes, actual reviewer verdict and limitations. Fixture shape tests alone are insufficient.

## 12. Seven Semantic Cases
| Case | Expected admissible recommendation | Review rejection |
| --- | --- | --- |
| Evergreen repeatable procedure | complete A-Z blog, newsletter summary plus reusable acceptance template/checklist, selected social | essential blog steps withheld, repetitive newsletter, all channels forced |
| Short timely observation | standalone newsletter or social | unnecessary long article or invented SEO demand |
| Deep technical niche | technical blog plus optional developer recovery-test checklist newsletter; social unsuitable | essential blog steps withheld or forced social hook distorting nuance |
| Strong visual demonstration | short/YouTube concept with asset gaps | claimed finished video or unlicensed screenshots |
| Valuable confidential incident | keep original lesson privately, owner reviews before anonymizing separate derivative; otherwise hold | original overwritten, anonymization before review, identity hidden only by name while domain/timing exposes client |
| Different brand audiences | recommend both when useful, distinct angles and PL vs EN policy; one brand may be excluded when unsuitable | identical translated voice or forced both brands |
| Weak/conflicting source or missing capacity | needs-evidence / unscheduled hold with question and honest alternative | invented impact, guessed budget or accepted route without owner |
Scorecard per case: evidence fidelity, audience promise, format justification, main/alternative difference, incremental value, privacy, capacity, uncertainty. Mandatory safety dimensions must all pass; editorial preference disagreements are documented, not silently coerced into one model answer. No claimed conversion/SEO outcome without real measurements.

## 13. Verification, Quality And Recovery
Implementation order follows six slices in current plan. Use synthetic anonymized fixtures only.
Future commands: relevant unittest/test runners discovered from current check-work-evidence suite, check-work-evidence, py_compile for changed modules/wrappers, git diff --check; scoped Workflow QA evidence/status checks. Full AI System validation with smoke tests at release/upgrade. No fake command results in planning.
Findings-first Phase 5 must inspect full diff, data/adversarial/producer-consumer matrix, failures and seven semantic scorecards. No P0/P1/material P2 open. Tests support, not replace, review.
Then technical distillation/checkpoint. Phase 8 requires its own owner trigger; final-owner-yes remains separate.
Rollback: keep v1 available; disabling v2 leaves immutable records untouched. No deletion, downgrade conversion or retroactive approval. Real rollout requires approved backup/restore/pilot and destinations; absent pilot leaves synthetic functionality only.

## 14. Current Gate And Capture
Current addendum: decisions/2026-10-05-wep-011-owner-review.md is actual human review
of the seven cases and authority for its bounded corrections. Review acceptance
does not accept unfinished corrections or grant activation/publication.
Before anonymization, review-source presents original selected lessons privately.
An optional v2 claim private_review binds original_hash, purpose
private-lesson-anonymization, approved_by, approved_at and authority_ref.
Original hash binds claim/entry/source/text/support/sensitive terms/procedure,
excluding derivative replacements, disclosure review and public approval.
Missing private review holds replacements; stale/invalid supplied review rejects.
The shared v1 claim contract remains unchanged. review-source is read-only and
never applies replacements; output is private-owner-only, not a safe editorial
package. Secrets remain rejected even in original lessons.
Approved local writes also preserve readable private-lessons.md beside the
private manifest, never in the shareable draft destination; its bytes are bound
by an optional receipt private_lessons_hash for compatible older v2 receipts.
Blog stays complete; newsletter may summarize plus add a reusable checklist or
template. Case 3 main route becomes blog plus recovery-test checklist newsletter.
Cases fitting both brands recommend distinct audience promises, not forced duplication.

Current implementation gate: authorized by decisions/2026-10-03-wep-011-implementation-authorization.md through the exact accepted annotated prompt. Original documentation-only approval remains historical. Scope excludes activation, commit, push and Phase 8.
Predecessor evidence: archived historical v1 reports at history/2026-10-03-wep-v1-baseline/evidence plus current HEAD interfaces. Re-read at implementation start; re-review spec if drift occurs.
No new material owner choice needed for bounded specification. Blog cadence/video production expansion stays out of scope, not a hidden design blocker.
Plan Quality Contract: implementation-capable design; DoD sections 2/11/12; artifact route Phase 3 Spec QA; future Phase 5/capture/checkpoint; current writes project artifacts only; residual semantic privacy/recommendation risk remains explicit.
Delivery Constraints: owner-opt-out, no deadline/timebox; no QA/privacy cutline.
Owner Decision Checkpoint: clear for bounded WEP-011 implementation/QA and required technical capture; WEP-010 still gates real activation.
Optional Knowledge Capture: current spec/status/evidence only, later technical distillation after implementation. No Codex memory or public insight.
Model recommendation: workhorse/frontier, high reasoning; current model unknown; non-blocking.
