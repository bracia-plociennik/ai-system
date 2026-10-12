# WEP-REPORT-005-client-drafts: Weekly and monthly client report drafts
Date: 2026-10-02. Mode: solo task. Risk: high. Status: conditional specification, not implementation authorization.
## Inputs And Traceability
context.md; decisions/2026-10-02-owner-scope.md; architecture/phase-1-architecture.md; planning/phase-2-project-plan.md section WEP-REPORT-005-client-drafts; tasks.md; current Plan QA.
Current001/002 Quality reviewed; use Ledger.committed/snapshot/index_status/lock,
period_entries and canonical_bytes/digest, approved_text for purpose-bound text.
Policy fields: schema_version, report_id, recipient_id, client_ids, project_ids,
start, end_exclusive, coverage_attested, texts, recurring_care. Recipient is a
registered client or agency; allowed clients must be itself or registry descendants.
Project scopes are explicit registry identities, not title/domain matching.
Text approval binds entry ID/hash, recipient, text/hash, purpose=client-report,
approved_by=owner and offset approved_at. Care approval binds current source
hash and recipient, but describes contracted scope, not performed work or time.
No missing-safe-text fallback. Totals/coverage cover only current eligible entries;
unapproved outcomes are withheld and reported as missing projection coverage.
Approval for local persistence binds draft hash, policy, period, recipient and
current source revisions. Full period coverage is owner-attested, never inferred
from an empty ledger; stale index warning uses canonical data without sync.
## Goal, Scope And DoD
Goal: Report actual outcomes clearly without inventing recurring work or exposing other clients.
Scope: Period queries, client-safe field projection, contracted-care catalogue and local Markdown/HTML draft rendering.
Out-of-scope: No email sends/draft API, audience import, contractual changes or manufactured time for ongoing care.
Testable DoD: Week/month reports reconcile to committed ledger, show coverage and distinguish delivered work from contracted recurring scope; recipient isolation tests pass.
## Dependencies And Start Conditions
Blocking dependencies: WEP-DATA-001-contracts, WEP-LEDGER-002-transactions.
Start: 001/002 Quality; owner-approved recipient aliases, scope catalogue and field policy before real reports.
Sequential only; no packages and no dependency on a future task. After predecessor output changes, refresh concrete file/function paths and rerun Spec QA before phase4. Do not substitute absent dependency evidence with this specification.
## Proposed Write Surface
.systems/scripts/work-evidence-report; report templates; synthetic recipient/period fixtures.
Paths are proposed implementation surfaces; inspect current repository at start and preserve other work. Product templates/tests use synthetic names and no real personal/client data. Actual runtime writes need exact owner-scoped approval, not merely product-code approval.
## Implementation Steps
1. Report builder takes owning workspace, recipient/client ID, explicit [start,end) Warsaw period and safe field policy. Join end-client/domain using registry, not titles. Stop ambiguous agency/end-client mapping.
2. Produce completed outcomes, partial/waiting actions and separate contracted recurring care. Catalogue items describe agreed service scope, never assert unlogged execution or minutes.
3. Aggregate only actual human durations from eligible current records; show estimates/unknowns/multi-day overlaps separately with coverage. Each internal row retains entry/revision provenance; client-facing copy omits source paths and internal notes.
4. Generate deterministic Markdown plus escaped HTML without tracking/external assets. Approval binds draft hash, period, recipient and source versions; changed input invalidates approval.
5. Keep local draft and internal manifest separate. Review any sensitive operational detail even for the same client; no broad fallback to internal title when safe text missing.
## Tests And Acceptance
Tests below are required future execution, not runs performed by planning.
1. Integration: one event corroborated in Daily/Weekly/checkpoint appears once; recurring scope appears without invented duration.
2. Boundary: empty period versus missing data differs; crossing-month aggregate shown separately; exactly-midnight entries assigned once.
3. Privacy: mixed agency/end-client fixtures never leak unrelated client/project, raw notes or local paths.
4. Security: injected HTML/script escaped; source instruction ignored; change after approval invalidates draft.
5. Manual: trace one week and month from entry through report with explicit partial and contractual-scope rows.
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
Real safe-field and recurring-care policies to be approved on pilot; default internal-only is safe, not auto-client-visible.
Recommendation: authorize only this task after its stated prerequisites are met; protect activation gates.
Alternative: retain specification for review without implementing, preserving the current tools.
Design uncertainty blocking specification: none within the explicitly bounded contract.
Implementation blockers: missing scoped implementation approval, predecessor Quality and interface refresh.
## Implementation Gate
All start conditions satisfied: yes for synthetic local implementation.
Can proceed to implementation now: yes after refreshed Spec QA.
Reason: current001/002 Quality and explicit implementation authorization.
Real recipient/text/care policy and local destination remain owner-gated.
## Plan Quality Contract
Plan classification: implementation-capable.
DoD source: canonical plan WEP-REPORT-005-client-drafts and D01-D10.
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
