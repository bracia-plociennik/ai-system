# WEP-XLSX-003-local-tracker: Local Excel projection and manual intake
Date: 2026-10-02. Mode: solo task. Risk: high. Status: conditional specification, not implementation authorization.
## Inputs And Traceability
context.md; decisions/2026-10-02-owner-scope.md; architecture/phase-1-architecture.md; planning/phase-2-project-plan.md section WEP-XLSX-003-local-tracker; tasks.md; current Plan QA.
Current execution supplement: predecessor outputs001/002 have scoped Quality.
Concrete interfaces: work_evidence_ledger.Ledger.preview/prepare/apply/committed,
snapshot/runtime/lock and atomic_write; work_evidence.validate_entry/digest/safe_path.
Workbook SHA-256 is projection_source in the prepared manifest; rows keep stable
row_id and immutable revision chains. Manual confirmations use the approved
workbook snapshot as owner-attested provenance, never inferred task durations.
Dependency approval: decisions/2026-10-02-xlsx-dependency-approval.md.
Runtime probe: isolated Python3.14, exact versions and openpyxl DEFUSEDXML=True.
## Goal, Scope And DoD
Goal: Provide one clear local tracker per workspace while retaining safe manual custom entries.
Scope: XLSX adapter, generated sheets, manual row identity, conflict preview, receipts, workbook integrity and import safety.
Out-of-scope: No Google Sheets, macros, executing formulas, Make modifications or unattended bidirectional merge.
Testable DoD: Manual new/corrected entries round-trip idempotently; generated edits conflict rather than disappear; workbook opens and renders clearly with actual/estimated/unknown separated.
## Dependencies And Start Conditions
Blocking dependencies: WEP-DATA-001-contracts, WEP-LEDGER-002-transactions.
Start: 001/002 Quality; reviewed and approved pinned XLSX dependency/version/license/security; implementation approval.
Sequential only; no packages and no dependency on a future task. After predecessor output changes, refresh concrete file/function paths and rerun Spec QA before phase4. Do not substitute absent dependency evidence with this specification.
## Proposed Write Surface
.systems/scripts/work_evidence_xlsx.py; workbook templates; dependency declaration; XLSX synthetic tests.
Paths are proposed implementation surfaces; inspect current repository at start and preserve other work. Product templates/tests use synthetic names and no real personal/client data. Actual runtime writes need exact owner-scoped approval, not merely product-code approval.
## Implementation Steps
1. Evaluate openpyxl against local supported Python, XLSX formula/link behavior and licensing/advisories; pin approved version in existing dependency mechanism. Do not install until approval. If unsuitable, stop for adapter decision, not silent custom XML parser.
2. Generate sheets Summary, Work Entries, Sessions, Manual Inputs, Conflicts, Import Receipts and metadata. Read-only styled generated columns include owner/client/project/domain/status/actual minutes/estimated minutes/coverage/source IDs. No private source paths or tax data in broad summary.
3. Manual Inputs columns: row_id, action new|correct|void, entry_id/base_revision, performed date or interval, duration/basis, client/project IDs, outcome, reason. Preserve entered text. Validate types, formula cells, duplicate IDs and ownership before preparing a batch.
4. Preview without saving. Approved prepare snapshots workbook and reserves IDs in journal. Identical blank rows are ambiguous and need explicit disambiguation; moving existing rows keeps identity. Never infer delete from a missing row.
5. Before apply recheck workbook/source digest and OS/open-file lock. Commit canonical via 002, then regenerate to sibling temporary XLSX, validate it and atomically replace with backup. Workbook save conflict stops projection and preserves the pending journal, not a second ledger import.
6. Quote untrusted text as literal strings, reject active/formula content in manual fields and macros/external links. Re-export only known supported schema. Visually inspect desktop-sized sheets and filters; avoid cropped headings and ambiguous units.
## Tests And Acceptance
Tests below are required future execution, not runs performed by planning.
1. Integration: blank-ID import, rerun and row reorder count once; two indistinguishable blank rows stop; IDs survive export.
2. Integration: edited generated cell, stale base revision, changed workbook after approval and open Excel cause explicit conflict with no data loss.
3. Security: leading =,+,-,@ text remains literal; formula cells, external links and macros rejected; private paths/tax sentinels absent.
4. Failure: canonical committed/projection crash resumes same IDs; broken XLSX backup restore tested on synthetic workbook.
5. Artifact: open in Excel or approved viewer; inspect sheets, filters, freeze panes, units and row wrapping; semantic totals match ledger.
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
Pinned dependencies approved and installed in isolated /private/tmp/wep-xlsx-venv.
Macro/link/formula/ZIP bounds remain adapter checks, not delegated to dependency approval.
Recommendation: authorize only this task after its stated prerequisites are met; protect activation gates.
Alternative: retain specification for review without implementing, preserving the current tools.
Design uncertainty blocking specification: none within the explicitly bounded contract.
Implementation blockers: missing scoped implementation approval, predecessor Quality and interface refresh, approved dependency assessment.
## Implementation Gate
All start conditions satisfied: yes after current Spec QA refresh.
Can proceed to implementation now: yes after refreshed Spec QA PASS.
Reason: current owner implementation authorization and pinned dependency approval
supersede the initial planning-only gate. Actual runtime activation remains separate.
## Plan Quality Contract
Plan classification: implementation-capable.
DoD source: canonical plan WEP-XLSX-003-local-tracker and D01-D10.
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
