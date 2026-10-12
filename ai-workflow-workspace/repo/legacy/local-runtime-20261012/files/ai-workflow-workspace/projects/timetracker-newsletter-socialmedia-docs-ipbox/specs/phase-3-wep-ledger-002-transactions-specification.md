# WEP-LEDGER-002-transactions: Canonical ledger and transactional synchronization
Date: 2026-10-02. Mode: solo task. Risk: high. Status: conditional specification, not implementation authorization.
## Inputs And Traceability
context.md; decisions/2026-10-02-owner-scope.md; architecture/phase-1-architecture.md; planning/phase-2-project-plan.md section WEP-LEDGER-002-transactions; tasks.md; current Plan QA.
Interface refresh 2026-10-02: task001 Quality passed. work_evidence.py supplies
validate_entry, validate_session, validate_config, validate_source, safe_path,
actual_seconds, canonical_bytes and digest. Ledger logic belongs in the scoped
work_evidence_ledger.py consumer so the shared contract remains independently
reviewable. Actual writable roots remain config-bound and owner-approved.
## Goal, Scope And DoD
Goal: Record real work once and rebuild derived views without duplication or loss.
Scope: Revision store, session allocation, preview/prepare/apply/recover protocol, index rebuild and selective checkpoint/TaskNote adapters.
Out-of-scope: No task lifecycle writes, automatic extraction-as-fact, broad history scans or automatic stale-lock deletion.
Testable DoD: Failure injection at every commit stage and repeated apply preserve exactly one counted entry; rebuild reproduces totals and source coverage.
## Dependencies And Start Conditions
Blocking dependencies: WEP-DATA-001-contracts.
Start: Task 001 Quality evidence and exact approved writable roots; implementation approval.
Sequential only; no packages and no dependency on a future task. After predecessor output changes, refresh concrete file/function paths and rerun Spec QA before phase4. Do not substitute absent dependency evidence with this specification.
## Proposed Write Surface
.systems/scripts/work_evidence.py; work-evidence-* wrappers; synthetic storage/transaction fixtures.
Paths are proposed implementation surfaces; inspect current repository at start and preserve other work. Product templates/tests use synthetic names and no real personal/client data. Actual runtime writes need exact owner-scoped approval, not merely product-code approval.
## Implementation Steps
1. Expose proposed commands work-evidence-preview, work-evidence-prepare, work-evidence-apply and work-evidence-rebuild. Preview stdout only; prepare is a separately approved write, records source snapshot, row/work IDs and proposed changes. Apply requires prepared manifest hash and expected source versions.
2. Store revisions append-only under resolved nearest owner root. Under an exclusive workspace writer lock stage/fsync records and commit manifest; readers select only committed manifests. Write index as replaceable projection after canonical commit; stale index is labeled and can be rebuilt.
3. Implement journal states prepared -> canonical-committed -> projections-written -> completed; recovery verifies hashes and resumes only the same transaction. Rollback uses approved compensating revisions, never deletes audit history. If workbook projection fails, ledger remains committed and receipt is explicitly pending.
4. Validate human session overlap and sum of allocations; exact measured/confirmed actual totals exclude estimates, automation, waiting and unknowns. UTC elapsed time, Warsaw period boundaries, partial aggregates and DST ambiguity follow schema.
5. Adapters prepare candidates referencing selected TaskNotes/checkpoints with source hashes and dates. Never derive minutes from a work block, commit time or task completion. Duplicated sources corroborate existing work_id; uncertain identity is queued for resolution.
## Tests And Acceptance
Tests below are required future execution, not runs performed by planning.
1. Integration: inject failure before manifest, after manifest and before projection; retry yields respectively zero or one committed record, never two.
2. Integration: simultaneous writers serialize; changed source hash or stale approval refuses mutation; stale lock requires explicit recovery.
3. Unit: allocation exceeds session rejected; mixed human/AI sessions do not inflate human totals; DST/overnight durations correct on UTC instants.
4. Integration: rebuild from committed revisions equals prior normalized index; void/correction adjusts totals once; source snapshots remain unchanged.
5. Read-only: preview file hashes before/after identical, including missing-index and ambiguous-candidate paths.
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
No dependency output yet; spec dependency-gated and refreshed after 001. Source-to-entry semantic matching stays owner-reviewed.
Recommendation: authorize only this task after its stated prerequisites are met; protect activation gates.
Alternative: retain specification for review without implementing, preserving the current tools.
Design uncertainty blocking specification: none within the explicitly bounded contract.
Implementation blockers: none for isolated product fixtures; real runtime activation remains gated.
## Implementation Gate
All start conditions satisfied: yes for synthetic local implementation.
Can proceed to implementation now: yes after refreshed Spec QA.
Reason: current owner implementation approval and task001 Quality; no real runtime activation.
## Plan Quality Contract
Plan classification: implementation-capable.
DoD source: canonical plan WEP-LEDGER-002-transactions and D01-D10.
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
