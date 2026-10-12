# WEP-DATA-001-contracts: Canonical contracts and identity registry
Date: 2026-10-02. Mode: solo task. Risk: high. Status: conditional specification, not implementation authorization.
## Inputs And Traceability
context.md; decisions/2026-10-02-owner-scope.md; architecture/phase-1-architecture.md; planning/phase-2-project-plan.md section WEP-DATA-001-contracts; tasks.md; current Plan QA.
No predecessor implementation output required for this foundation task.
## Goal, Scope And DoD
Goal: Make workspace ownership, provenance and time semantics unambiguous before any writes.
Scope: Versioned entry/session/config/entity/binding schemas, source allowlists, privacy projection contracts and synthetic fixtures.
Out-of-scope: No runtime activation, import, TaskNote edits or fiscal qualification.
Testable DoD: Synthetic fixtures reject ambiguous ownership, unsafe references and invented duration; entry-to-report field matrix has explicit mapping or exclusion.
## Dependencies And Start Conditions
Blocking dependencies: none.
Start: Explicit implementation approval; current safe branch and synthetic fixture roots.
Sequential only; no packages and no dependency on a future task. After predecessor output changes, refresh concrete file/function paths and rerun Spec QA before phase4. Do not substitute absent dependency evidence with this specification.
## Proposed Write Surface
.systems/ai/core/work-evidence.md; .systems/ai/templates/work-evidence/; .systems/scripts/work_evidence.py; synthetic tests.
Paths are proposed implementation surfaces; inspect current repository at start and preserve other work. Product templates/tests use synthetic names and no real personal/client data. Actual runtime writes need exact owner-scoped approval, not merely product-code approval.
## Implementation Steps
1. Add .systems/ai/core/work-evidence.md and sanitized schema/template resources. Define entry UUID, work_id, immutable owner, revision/hash chain, nullable bindings and provenance envelope. Use one shared validator module under .systems/scripts for all consumers.
2. Define timing as a tagged union: date + declared seconds; measured start/end with timezone/offset; aggregate start/end-exclusive + declared seconds. Forbid contradictory fields, negative/fractional seconds and inferred timing. Model unknown as null, zero only explicit; estimated values excluded from actual totals.
3. Define normalized registry IDs with explicit aliases, end-client vs agency mapping, legal taxpayer mapping separate. A reference names a configured root alias plus safe relative path/hash; reject symlink escapes before read and revalidate before use.
4. Specify state/revision transitions, mandatory reason for corrections/voids, independent actor_kind human/automation/waiting and allowed visibility states. Default internal. Distinguish conflicts from missing fields.
5. Publish producer-consumer matrix for ledger, XLSX, reports, documentation, tax and editorial. Use allowlists, not blacklist-only output sanitization. Add schema-version rejection with no auto-migration.
## Tests And Acceptance
Tests below are required future execution, not runs performed by planning.
1. Unit: valid zero, null and estimated durations produce three distinct states; reject -1, bool-as-number, unknown-with-positive-seconds.
2. Unit: one TaskNote binding cannot assign the same task to two workspace owners; cross-workspace source reference alone creates no entry.
3. Unit: traversal, absolute path, escaped symlink and credential-like roots fail closed before file content is returned.
4. Contract: every required field maps to consumer behavior; unknown schema rejects without any source/file changes.
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
No unresolved design choice. Actual runtime roots and entity aliases need owner-approved activation later.
Recommendation: authorize only this task after its stated prerequisites are met; protect activation gates.
Alternative: retain specification for review without implementing, preserving the current tools.
Design uncertainty blocking specification: none within the explicitly bounded contract.
Implementation blockers: missing scoped implementation approval.
## Implementation Gate
All start conditions satisfied: no.
Can proceed to implementation now: no.
Reason: planning-range stops before phase4 and explicit prerequisites above are unfulfilled. Spec QA may accept this dependency-gated design; it cannot waive the implementation gate or real-data activation restrictions.
## Plan Quality Contract
Plan classification: implementation-capable.
DoD source: canonical plan WEP-DATA-001-contracts and D01-D10.
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
