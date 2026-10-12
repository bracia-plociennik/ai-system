# WEP-CONTENT-008-editorial-drafts: Two-brand editorial and anonymization pipeline
Date: 2026-10-02. Mode: solo task. Risk: high. Status: conditional specification, not implementation authorization.
## Inputs And Traceability
context.md; decisions/2026-10-02-owner-scope.md; architecture/phase-1-architecture.md; planning/phase-2-project-plan.md section WEP-CONTENT-008-editorial-drafts; tasks.md; current Plan QA.
Predecessor001/002/004 Quality and actual Ledger/assemble interfaces reviewed.
Request fields: schema_version, topic_id, claims, brands, queue_start, weeks,
drafts. Claims bind claim_id, entry_id/hash, source_ref, text, privacy_state,
sensitive_terms, replacements, review checklist, supported and approval; optional
procedure_ref binds procedure ID/version/kit hash. Source is selected explicitly,
not crawled. Claim approval binds digest of all claim fields except approval,
purpose editorial-source, approved_by owner and approved_at. Review checklist
identifiers/quasi_identifiers/contracts/copyright is required for public-ready.
Sensitive candidates never export original text; validated literal replacements
yield anonymized-needs-review, not public-ready. Unreviewed/internal/unsupported
claims are held with IDs/reasons only. Private provenance retains original inputs.
Brands declare ID/kind/name/primary and optional languages/newsletter title/anchor;
personal PL-first, company EN-first, four-issue language pilot metrics unknown.
Queue has one newsletter slot per fortnight and two base plus one optional
social slot per brand/week; variants share slot IDs. Newsletter anchors stagger.
Drafts are agent-authored input data with ID/brand/language/channel/slot/claim IDs/
title/body/approval. Each body references explicit claim tokens {{claim:ID}};
rendered facts come only from the supported selected derivatives. Other prose
remains commentary for owner semantic review. Draft approval binds body/source
hashes, brand/language/channel/purpose; absent approval remains needs-review.
Persist writes local immutable drafts plus separate private manifest using
config editorial_policy.destination_root (safe relative existing brand root);
never initialize another workspace or publish. All sources are rechecked.
## Goal, Scope And DoD
Goal: Reuse valuable work evidence in distinct source-backed newsletter and social drafts.
Scope: Source selection, claim registry, anonymized derivatives, brand/language briefs, local drafts and per-version review queue.
Out-of-scope: No social/email publication APIs, audience lists, tax/raw-dump ingestion or consent inferred from anonymization.
Testable DoD: One case produces two appropriate newsletter drafts and linked social derivatives with traceable claims, privacy labels and independent approvals; source secrets never enter output.
## Dependencies And Start Conditions
Blocking dependencies: WEP-DATA-001-contracts, WEP-LEDGER-002-transactions, WEP-DOCS-004-replay-kit.
Start: 001/002/004 Quality; exact approved source roots and destination; implementation approval.
Sequential only; no packages and no dependency on a future task. After predecessor output changes, refresh concrete file/function paths and rerun Spec QA before phase4. Do not substitute absent dependency evidence with this specification.
## Proposed Write Surface
.systems/ai/core/work-evidence-editorial.md; bundle CLI; private draft templates; synthetic privacy/claim tests.
Paths are proposed implementation surfaces; inspect current repository at start and preserve other work. Product templates/tests use synthetic names and no real personal/client data. Actual runtime writes need exact owner-scoped approval, not merely product-code approval.
## Implementation Steps
1. Create deterministic evidence-bundle CLI selecting approved operational facts and procedure insights by explicit IDs. Internal facts remain internal; unsupported before/after metrics and client endorsements are flagged rather than invented.
2. Create separate anonymization derivative with removed identifiers, domain/date/number coarsening and re-identification checklist. Store private provenance outside export; needs-anonymization and anonymized-needs-review never equal public-ready approval.
3. Apply brand contracts: Kuba PL-first concrete decisions/mistakes/systems/results; Onlinen EN-first human business benefit, optional PL variant with same claim evidence. Not word-for-word identical brand voice.
4. Represent cadence as editorial queue fields only: fortnightly per brand, staggered; 2 base plus optional3rd social per week total across languages/platforms. Create four-issue language-test plan with unknown metrics and separate review of translation accuracy.
5. Agent consumes data-only bundle and writes local drafts after scoped approval; CLI does not embed hidden LLM API calls. Draft/translation approval binds source+content hash, brand, language, channel and purpose. Any change requires rereview.
6. Allow exclusion or hold without discarding source knowledge. Review privacy/copyright/contract permission before pilot export; no unapproved attachments/screenshots copied.
## Tests And Acceptance
Tests below are required future execution, not runs performed by planning.
1. Security: tax/raw/dump/credential canaries and source prompt injection blocked; no private identity from combined quasi-identifiers in reviewed synthetic case.
2. Contract: anonymization alone cannot set approved; changed translation/claim/source invalidates approval.
3. Artifact: one synthetic case renders two newsletter drafts plus social candidates in distinct voices; each factual claim links privately to proof.
4. Cadence: PL+EN variants count toward same per-brand allocation; no accidental 2x posting promise.
5. Manual: weak-source benefit claim rejected/qualified, valuable sensitive lesson retained as anonymization candidate.
## Edge Cases And Error Behavior
Handled: all failure cases in steps/tests; reject conflicting identity, unsafe paths, missing required evidence and changed inputs. Error includes stable category and safe locator/ID, never secret content.
Handled: empty collection and unknown values remain explicit; no auto-fill from plans or guessed real-world outcomes.
Handled: rerun/review after source change uses current version and retains historical evidence; does not treat stale approval as current.
Intentionally excluded: production/network integration, automatic historical migration and unapproved client/tax disclosures, because they are outside this task's authority. Report unsupported scope; do not silently approximate it.
Potential implementation errors: conflating missing and zero, mixing owner and physical path, stale derived data, approval not bound to current source, and test fixtures accidentally containing private data.
## Verification And Quality Route
Use unit/contract/integration/manual checks listed above against isolated fixture roots. Record adaptive source -> canonical -> derived -> forbidden state -> failure -> automated/manual evidence matrix at phase5, including one normal and one failing trace.
Run appropriate targeted product tests and syntax checks, git diff --check; use complete AI System release verification at task009/cutover. Workflow validation is supporting-only and scoped by current validation-routing.
Quality-ready requires reviewed implementation diff and no unresolved P0/P1/material P2; test count alone is insufficient. Preserve evidence of failures and fixes. No opt-out of QA.
## Recovery And Rollback
Before approved mutations capture input hashes and scoped backup. Abort before writes on conflict. Use ledger committed-batch recovery/compensating revisions where relevant; never undo unrelated user edits or erase audit history. Draft outputs can be regenerated from versioned sources after exact approval. Dependency install and real activation have separate rollback plans.
## Uncertainty And Owner Decisions
Audience outcomes unknown until measured; no promise of newsletter conversion. Real content remains draft and owner-reviewed.
Recommendation: authorize only this task after its stated prerequisites are met; protect activation gates.
Alternative: retain specification for review without implementing, preserving the current tools.
Design uncertainty blocking specification: none within the explicitly bounded contract.
Implementation blockers: missing scoped implementation approval, predecessor Quality and interface refresh.
## Implementation Gate
All start conditions satisfied: yes for synthetic local drafts after current QA.
Can proceed to implementation now: yes after refreshed Spec QA.
Reason: explicit implementation authorization and001/002/004 current interfaces.
Real editorial/public disclosure remains draft-only and separately reviewed.
## Plan Quality Contract
Plan classification: implementation-capable.
DoD source: canonical plan WEP-CONTENT-008-editorial-drafts and D01-D10.
Acceptance conditions: task DoD and concrete tests above.
Artifact QA route: phase-3-spec-qa.
Artifact QA trigger: specification completion, and again after predecessor/interface refresh.
Implementation Quality Closure route: phase-5-quality.
Required verification: unit/integration/adversarial and representative manual traces above; source/current-diff review.
Quality-ready criteria: complete scoped steps/tests, no hidden dependency, phase5 evidence before task completion.
Owner opt-out: none. Not-applicable reason: none.
Blocking decision: D08 implementation approval and task-specific activation gates.
Next route: phase-3-spec-qa only in this run.
## Delivery Constraints
D07 owner-opt-out: no deadline/time budget. Must-have is full task DoD; protect privacy/evidence/QA. No stretch scope or quality cutline. Stop on blocking decision or failed safety gate.
## Owner Decision Checkpoint
Interaction mode: queued. Decision state: clear for specification; activation gates pending at their named boundary. No new question needed to complete planning. Decisions: D01-D10.
## Optional Knowledge Capture
Capture recommended: yes. Target: spec/status/evidence in this project; capture-now for planning. Future implementation distillation/checkpoint only after its approved phase.
## Model Recommendation
Frontier/workhorse high reasoning; high-impact data integrity/privacy. Current model unknown. Blocking: no.
