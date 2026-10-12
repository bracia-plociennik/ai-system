# WEP-QA-009-regression-suite: Cross-flow regression and release safeguards
Date: 2026-10-02. Mode: solo task. Risk: high. Status: conditional specification, not implementation authorization.
## Inputs And Traceability
context.md; decisions/2026-10-02-owner-scope.md; architecture/phase-1-architecture.md; planning/phase-2-project-plan.md section WEP-QA-009-regression-suite; tasks.md; current Plan QA.
Predecessor001-008 modules and Quality reviewed. Current Ledger/coverage/XLSX,
assemble, report, TaxRegister/calculate and editorial bundle interfaces are the
explicit test inputs. Runner uses approved isolated Python with exact pinned
dependencies; no network or real client records. Init request binds version,
existing workspace identity, source roots and registry/config; preview lists
only config/entities writes. Apply rejects existing roots and requires manifest
hash and explicit owner approval. Backup request selects exact relative paths
under work-log or operational work-evidence, excluding private-tax/dump/secrets,
backups and journals. Existing-workspace lock and fresh inventory hashes bind
preview/write. Backup stores immutable copies plus per-file hashes and full
operational inventory fingerprint. Restore preview binds current inventory and
selected target hashes; apply stops on any subsequent edit, backs up replaced
bytes and uses a journal. Retry accepts only that journal's original or restored
hashes, never third-party edits. No deletion or broad workspace copy. Config and
registry corruption remains operator-led; generic CLI cannot bypass validation.
## Goal, Scope And DoD
Goal: Prove end-to-end integrity and privacy before using real runtime data.
Scope: Synthetic cross-flow harness, failpoint testing, product validator routing, documentation and explicit rollout/rollback tooling.
Out-of-scope: No production activation, history migration, broad runtime scan or automatic updater invocation.
Testable DoD: Full synthetic scenario preserves totals/ownership/privacy through ledger, Excel, report, docs, tax and content; backup/rebuild and negative-path tests pass.
## Dependencies And Start Conditions
Blocking dependencies: WEP-DATA-001-contracts, WEP-LEDGER-002-transactions, WEP-XLSX-003-local-tracker, WEP-DOCS-004-replay-kit, WEP-REPORT-005-client-drafts, WEP-TAX-006-evidence-register, WEP-TAX-007-rule-calculator, WEP-CONTENT-008-editorial-drafts.
Start: 001-008 phase5 Quality and upstream implementation approval; explicit controlled fixture roots.
Sequential only; no packages and no dependency on a future task. After predecessor output changes, refresh concrete file/function paths and rerun Spec QA before phase4. Do not substitute absent dependency evidence with this specification.
## Proposed Write Surface
.systems/scripts/check-work-evidence; product validation routing; synthetic fixtures; sanitized runbooks.
Paths are proposed implementation surfaces; inspect current repository at start and preserve other work. Product templates/tests use synthetic names and no real personal/client data. Actual runtime writes need exact owner-scoped approval, not merely product-code approval.
## Implementation Steps
1. Add check-work-evidence targeted runner using anonymized two-workspace, agency/end-client, shared-IP and multi-period fixtures. Register it in the appropriate AI System validation route without altering AI Workflow.
2. Run happy-path trace including manual row, revision, session split, regenerated XLSX, weekly/monthly report, doc package, advisor-gated synthetic result and both brand bundles. Compare committed entry IDs/hashes and total counts.
3. Inject concurrency/crashes, stale source/draft approvals, DST/midnight and duplicate sources. Snapshot files before dry-runs; fail any unexpected writes, network request or privacy-canary appearance.
4. Provide dry-run runtime init and backup/restore manifest tooling, explicitly scoped per selected workspace and file hashes; no broad recursive copy or overwrite. Restore requires approval and detects subsequent changes.
5. Document commands, dependency setup and source freshness. Run product syntax/targeted/integration checks, required full AI System validation for upgrade release, then project Workflow gate; inspect remaining failures rather than relabel unrelated failures as green.
## Tests And Acceptance
Tests below are required future execution, not runs performed by planning.
1. End-to-end: same evidence counted once across all consumers; known-zero/unknown/estimate preserved; no cross-client leakage.
2. Failure injection: partial transaction, corrupted workbook, simultaneous writers, interrupted restore and stale artifact handled deterministically.
3. Read-only: dry-run content hashes unchanged; network access fails test; protected history/raw inputs untouched.
4. Recovery: clean restore and rebuild produce identical canonical hash set and totals.
5. Regression: existing Personal Ops and Task Management behavior unchanged; tax defaults cannot enable real computation.
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
Exact implementation command entrypoints refreshed after upstream tasks; plan fixes test invariants, not fabricated test results.
Recommendation: authorize only this task after its stated prerequisites are met; protect activation gates.
Alternative: retain specification for review without implementing, preserving the current tools.
Design uncertainty blocking specification: none within the explicitly bounded contract.
Implementation blockers: missing scoped implementation approval, predecessor Quality and interface refresh.
## Implementation Gate
All start conditions satisfied: yes for synthetic release verification.
Can proceed to implementation now: yes after refreshed Spec QA.
Reason:001-008 scoped Quality and explicit implementation authorization; real
runtime/cutover decisions remain outside this synthetic task.
## Plan Quality Contract
Plan classification: implementation-capable.
DoD source: canonical plan WEP-QA-009-regression-suite and D01-D10.
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
