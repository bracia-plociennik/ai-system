# WEP-TAX-006-evidence-register: Private IP and financial evidence register
Date: 2026-10-02. Mode: solo task. Risk: high. Status: conditional specification, not implementation authorization.
## Inputs And Traceability
context.md; decisions/2026-10-02-owner-scope.md; architecture/phase-1-architecture.md; planning/phase-2-project-plan.md section WEP-TAX-006-evidence-register; tasks.md; current Plan QA.
Current001/002/004 Quality and actual ledger/procedure APIs reviewed.
Private register uses existing <workspace>/private-tax/<taxpayer-id>/config.json;
never initialized automatically. Config binds taxpayer_id, owner_workspace,
currencies and explicit allowed_workspaces ID->local path map, each verified
against its operational Ledger config. Tax-only source aliases are relative
directories under this private taxpayer root; normal operational allowlist still
refuses private-tax. Private references are never passed to non-tax consumers.
Bundle fields: schema_version, taxpayer_id, tax_year, ip_items, rights, finance,
allocations, work_refs. IP items have ip_id, taxpayer_id, rights_holder_id and
description. Rights have right_id/ip_id/taxpayer_id/kind/effective_start/end_exclusive,
source_refs/evidence_state. Finance has finance_id/taxpayer_id/category/amount
(Decimal string or null)/currency/date/source_refs/evidence_state. Allocations
have allocation_id/finance_id/ip_id/amount/currency/work_refs. Work references
bind owner_workspace/entry_id/entry_hash and documented procedure kit hash when
provided; no duplicated minutes. Optional kit_hash=null means documentation gap.
All sources hash-bound; unknown rights/amounts, taxpayer conflicts, unsupported
currency or over-allocation mark evidence packet blocked with specific gaps;
structurally invalid inputs reject safely. Eligibility always unknown.
Private packet persistence hash-bound, immutable content-addressed bundle+packet;
no taxpayer inference, live classification or automatic history import.
## Goal, Scope And DoD
Goal: Prepare traceable advisor evidence without asserting qualification.
Scope: Taxpayer/IP/rights/finance identities, allocation links, missingness reports and private advisor packet.
Out-of-scope: No automatic IP qualification, reading bank accounts, tax filing, public distribution or importing example percentages as policy.
Testable DoD: Every proposed financial/IP allocation traces to evidence; conflicting taxpayer, missing rights or unsupported amounts remain blocked/unknown, not eligible by default.
## Dependencies And Start Conditions
Blocking dependencies: WEP-DATA-001-contracts, WEP-LEDGER-002-transactions, WEP-DOCS-004-replay-kit.
Start: 001/002/004 Quality; implementation approval; taxpayer/root mapping before real data entry.
Sequential only; no packages and no dependency on a future task. After predecessor output changes, refresh concrete file/function paths and rerun Spec QA before phase4. Do not substitute absent dependency evidence with this specification.
## Proposed Write Surface
.systems/ai/templates/work-evidence/tax/; .systems/scripts/work-evidence-tax-evidence; sanitized fixtures.
Paths are proposed implementation surfaces; inspect current repository at start and preserve other work. Product templates/tests use synthetic names and no real personal/client data. Actual runtime writes need exact owner-scoped approval, not merely product-code approval.
## Implementation Steps
1. Define separate private schemas for taxpayer, IP item, agreement/right transfer, invoice/payment/cost facts and allocation record. Store Decimal strings, currency and source locators/hash; distinguish asserted, verified and advisor-assessed states.
2. Use IP identity independent of website/task. Allow references to work from both workspace ledgers without copying entries or duration. Validate ownership and confidentiality per approved root.
3. Enforce allocation totals per source amount/category, effective dates, currency consistency and evidence linkage; negative corrections require documented credit/correction policy, otherwise block rather than coerce.
4. Build evidence-only completeness packet grouped by IP and period, with missing source/rights/amount/qualification fields and explicit review questions. No implicit treatment of absent values as zero.
5. Exclude tax store and advisor packet from tracker summary, client reports and editorial source selectors. No taxpayer choice inferred from document filename or third-party interpretation.
## Tests And Acceptance
Tests below are required future execution, not runs performed by planning.
1. Unit: two workspace references to one work record count once; one client can have multiple IPs without auto-splitting.
2. Integration: allocation > source, conflicting taxpayer or unsupported currency blocks packet's completeness, preserves raw facts.
3. Privacy: tax canary absent from all non-tax projections and content bundles; allowlist refuses tax paths.
4. Fixture: third-party interpretation and working spreadsheet remain illustrative evidence; unexplained percentage cannot qualify a record.
5. Manual: advisor packet trace invoice -> allocation -> IP -> rights evidence -> work revision, with gaps clearly visible.
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
Actual taxpayer and advisor classification unavailable; activation gate, not an engine default.
Recommendation: authorize only this task after its stated prerequisites are met; protect activation gates.
Alternative: retain specification for review without implementing, preserving the current tools.
Design uncertainty blocking specification: none within the explicitly bounded contract.
Implementation blockers: missing scoped implementation approval, predecessor Quality and interface refresh.
## Implementation Gate
All start conditions satisfied: yes for synthetic private-register implementation.
Can proceed to implementation now: yes after refreshed current Spec QA.
Reason: explicit implementation authorization and001/002/004 Quality.
Actual taxpayer/source policy and advisor assessment remain separate activation gates.
## Plan Quality Contract
Plan classification: implementation-capable.
DoD source: canonical plan WEP-TAX-006-evidence-register and D01-D10.
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
