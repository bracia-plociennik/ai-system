# WEP-DOCS-004-replay-kit: Reproducible documentation packages
Date: 2026-10-02. Mode: solo task. Risk: high. Status: conditional specification, not implementation authorization.
## Inputs And Traceability
context.md; decisions/2026-10-02-owner-scope.md; architecture/phase-1-architecture.md; planning/phase-2-project-plan.md section WEP-DOCS-004-replay-kit; tasks.md; current Plan QA.
Current execution:001/002 scoped Quality exists. Interfaces are
work_evidence.validate_source/safe_path/canonical_bytes/digest and
work_evidence_ledger.Ledger.snapshot/runtime/lock/committed/atomic_write.
Assembler accepts explicit source references plus separately owner-approved
sanitized derivatives, never auto-copies source bodies or executes steps.
Procedure fields: schema_version, procedure_id, version, work_ids, target_outcome,
skills, environment, prerequisites, inputs, steps, tests, stop_conditions,
rollback, limits, source_refs, derivatives. Steps have id/action/expected;
tests have id/assertion. Sanitized input/derivative approval binds source hash,
text hash, purpose=documentation and approved_by=owner with timestamp.
Kit manifest binds procedure/config/registry and source hashes; read-only preview
returns kit hash, approved write uses expected hash and immutable versioned files.
Human replay envelope binds tester identity/consent/role, kit hash, environment,
offset start/end, all assertions, failed/ambiguous steps and help_requested;
signed tester evidence and explicit owner verification approval are mandatory.
These are attestations with artifact hashes, not invented cryptographic signatures.
Automated/owner-assisted evidence cannot transition to replay-passed.
## Goal, Scope And DoD
Goal: Turn evidence into a procedure another programmer can execute without the owner.
Scope: Procedure schema/template, explicit selected-source assembler, replay checklist and redacted mock package.
Out-of-scope: No actual contractor access, production credentials, inferred completion or code modifications in DealerCRM.
Testable DoD: Package states prerequisites, inputs, exact steps, expected outputs, tests, failure/rollback and evidence; only signed human replay evidence can mark replay-passed.
## Dependencies And Start Conditions
Blocking dependencies: WEP-DATA-001-contracts, WEP-LEDGER-002-transactions.
Start: 001/002 Quality and explicit source allowlist; implementation approval.
Sequential only; no packages and no dependency on a future task. After predecessor output changes, refresh concrete file/function paths and rerun Spec QA before phase4. Do not substitute absent dependency evidence with this specification.
## Proposed Write Surface
.systems/ai/templates/work-evidence/procedure/; .systems/scripts/work-evidence-documentation; synthetic kit fixtures.
Paths are proposed implementation surfaces; inspect current repository at start and preserve other work. Product templates/tests use synthetic names and no real personal/client data. Actual runtime writes need exact owner-scoped approval, not merely product-code approval.
## Implementation Steps
1. Implement document kit metadata with procedure_id/version, target outcome, assumed programmer skills, software versions, sanitized mock inputs and exact source manifest. Link entry/task IDs without duplicating work.
2. Provide ordered setup/run/test/cleanup steps with expected observable outcomes and recovery for missing tools, failed API responses, interrupted setup and version mismatch. Mark unverified assumptions.
3. Assembler resolves explicit paths within allowlist, excludes secrets/databases/tax/raw dumps and refuses unresolved links. Export selected sanitized derivatives, never whole repository by default.
4. Replay record captures tester identity/consent, kit hash, environment, start/end, successful assertions, failed/ambiguous steps and help requested. Any owner assistance fails the independence criterion for that version.
5. Only separately approved human evidence transitions documented -> replay-passed; changed kit invalidates prior replay association and requires retest. Retain prior evidence history.
## Tests And Acceptance
Tests below are required future execution, not runs performed by planning.
1. Contract: missing prerequisites/test/rollback sections prevent documented completeness.
2. Integration: package source change marks kit stale; symlink/private sentinel blocked; no implicit network access.
3. State: local automated tests alone cannot set replay-passed; help requested or failed expected result cannot pass.
4. Manual synthetic trace: qualified programmer checklist exposes missing input instead of silently fetching production data.
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
Actual tester/access requires owner action at pilot; template and assembler are independently testable now.
Recommendation: authorize only this task after its stated prerequisites are met; protect activation gates.
Alternative: retain specification for review without implementing, preserving the current tools.
Design uncertainty blocking specification: none within the explicitly bounded contract.
Implementation blockers: missing scoped implementation approval, predecessor Quality and interface refresh.
## Implementation Gate
All start conditions satisfied: yes for synthetic product implementation after refreshed Spec QA.
Can proceed to implementation now: yes after current Spec QA PASS.
Reason: explicit implementation authorization and verified001/002 interfaces;
actual selected pilot source/human replay and real activation remain separate.
## Plan Quality Contract
Plan classification: implementation-capable.
DoD source: canonical plan WEP-DOCS-004-replay-kit and D01-D10.
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
