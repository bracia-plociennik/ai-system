# Phased Work Evidence Pipeline Plan
Revision: 2026-10-03. Classification: implementation-capable design. WEP-001-010 sections describe the v1 baseline; WEP-CONTENT-011 below is the current extension. Current authority: decisions/2026-10-03-wep-011-implementation-authorization.md, implementing/QA only; no activation, commit or push.
## Current Execution State
Tasks001-009 are implemented with scoped Quality and phase6 evidence on synthetic
inputs; task003 pinned XLSX dependency approval WEP-DEP-003 is granted/installed.
Current owner decision decisions/2026-10-02-technical-closure-scope.md explicitly
defers010 and authorizes technical001-009 closure and commit, without push or
final-owner-yes. This prior implementation/commit authorization is historical and does not cover WEP-011. No runtime activation or history import. Original planning
authorization statements below are historical, not current approval evidence.
Independent human pilot and usability/privacy acceptance remain future gates.
## Governing Inputs
context.md; decisions/2026-10-02-owner-scope.md; change-requests/2026-10-03-wep-cr-001-editorial-routing.md; architecture/phase-1-architecture.md; quality/phase-1-architecture-qa.md (current run wep-editorial-v2-architecture-001).
## Current Completion Overlay
001/002/003/004/005/006/007/008/009: completed scoped implementation Quality and phase6.
010: owner-deferred, not completed; all human/runtime gates remain in force.
011: in-progress; authorized bounded implementation and QA, with current architecture/plan/spec QA. Technical capture follows Quality; no Phase 8.
V1 assessed sources and QA are preserved at history/2026-10-03-wep-v1-baseline.
Old QA paths are historical routers; they do not certify the new editorial v2.
This overlay and tasks.md govern current execution. The ten-task design and
acceptance criteria below remain unchanged; no real pilot success is inferred.
No separate numbered execution-list section exists; the exact WEP IDs below
are updated instead of guessing a mapping to another list.
## Intake
Co zostaje: existing work documents, OSNR and TaskNotes as evidence; local trackers and private workflows.
Co jest slabe / do poprawy: duplicate client sheets, unlinked time/proof, unclear fact versus contractual care, unsafe reuse.
Czego brakuje: canonical identity/transactions, reviewed projections, replay evidence and advisor-gated rules.
Blokery / decyzje: no planning blocker; implementation approval, dependency selection, taxpayer/rules and human pilot are explicit later gates.
Rekomendowany routing: solo tasks below, individual specification and Spec QA; stop before phase4.
## Sequence And Milestones
1. Foundation: 001 contracts -> 002 ledger. No dependent real records until both have phase5 evidence.
2. Operational projections: 003 local Excel -> 004 documentation -> 005 client reports.
3. Private accounting evidence: 006 register -> 007 generic calculator. Real calculation remains disabled.
4. Editorial: 008 two-brand local drafts, no publishing mechanism.
5. Integrated verification: 009 full synthetic trace -> 010 human DealerCRM pilot and explicitly approved runtime rollout.

Execution is solo in listed order even where dependency graph permits parallelism. No packages; no shared-router parallel writes. Later tasks are dependency-gated; refresh their specs against actual predecessor output and rerun Spec QA before implementation.
Planning artifacts can pass their own completeness gate without asserting conditional implementation tasks ready.
## Data And Source-Of-Truth Matrix
| Data | Authority | Input method | Derived consumers | Prohibited inference |
| --- | --- | --- | --- | --- |
| Task intent/status | existing TaskNote plus explicit lifecycle decisions | read-only binding | planned context | done means measured time |
| Actual performed work | committed work revision + evidence level | owner/measurement, approved candidate | Excel, reports, proof | duplicate sources add work |
| Human time | confirmed session/declared actual; unknown separate | after block/manual row | actual totals | calendar duration = actual |
| Process reproducibility | versioned procedure + independent human replay | scoped kit, signed replay log | documentation, safe lessons | agent test = human replay |
| Contractual recurring care | approved service catalogue | owner mapping | separate report section | recurring scope = performed hours |
| Financial/IP facts | private source-backed records | reviewed manual/import input | advisor packet | client/domain = qualified IP |
| Fiscal computation | applicable advisor-approved rule version | exact approval + golden cases | private trace | third-party example = owner rule |
| Public/client text | separately approved derivative | explicit field/recipient policy | local draft | internal facts safe by default |
| Editorial rhythm | brand config | accepted cadence | queue only | schedule = permission to publish |
## Shared Implementation Contract
All task statuses are conditional until separate owner implementation approval. This is not a project blocker for producing specifications. Each task requires phase4 implementation, findings-first phase5 Quality, then appropriate distillation/checkpoint before completion/handoff. Phase8 is never part of this planning run.
Writes planned now: private project artifacts only; implementation writes proposed per task, not executed. No TaskNotes.
Dependencies listed below are hard blocking quality dependencies; context sources are informational. No dependency on a future task. Unknown real activation parameters are explicit gates, not invented defaults.
Plan quality DoD: all ten tasks have complete contracts, testable results, valid dependency order, safe boundaries and individual spec/QA paths. No historical source rewrite.

## WEP-DATA-001-contracts: Canonical contracts and identity registry
- Goal: Make workspace ownership, provenance and time semantics unambiguous before any writes.
- Scope: Versioned entry/session/config/entity/binding schemas, source allowlists, privacy projection contracts and synthetic fixtures.
- Out-of-scope: No runtime activation, import, TaskNote edits or fiscal qualification.
- DoD: Synthetic fixtures reject ambiguous ownership, unsafe references and invented duration; entry-to-report field matrix has explicit mapping or exclusion.
- Dependencies (blocking): none
- Informational dependencies: accepted context and versioned architecture; historical artifacts do not grant approval.
- Risk: high; primary risk: data integrity, ownership and evidence correctness.
- Start condition: Explicit implementation approval; current safe branch and synthetic fixture roots.
- End condition: DoD tested with phase5 Quality evidence and required capture; not just a green script.
- Readiness/status: completed (current scoped implementation; no runtime activation).
- User decision required before implementation: yes; scoped implementation approval.
- Spec: specs/phase-3-wep-data-001-contracts-specification.md
- Spec QA: quality/phase-3-wep-data-001-contracts-spec-qa.md
- Quality: quality/phase-5-wep-data-001-contracts-quality.md (current implementation evidence).
- Proposed write surface: .systems/ai/core/work-evidence.md; .systems/ai/templates/work-evidence/; .systems/scripts/work_evidence.py; synthetic tests
- Uncertainty / activation gate: No unresolved design choice. Actual runtime roots and entity aliases need owner-approved activation later.

## WEP-LEDGER-002-transactions: Canonical ledger and transactional synchronization
- Goal: Record real work once and rebuild derived views without duplication or loss.
- Scope: Revision store, session allocation, preview/prepare/apply/recover protocol, index rebuild and selective checkpoint/TaskNote adapters.
- Out-of-scope: No task lifecycle writes, automatic extraction-as-fact, broad history scans or automatic stale-lock deletion.
- DoD: Failure injection at every commit stage and repeated apply preserve exactly one counted entry; rebuild reproduces totals and source coverage.
- Dependencies (blocking): WEP-DATA-001-contracts
- Informational dependencies: accepted context and versioned architecture; historical artifacts do not grant approval.
- Risk: high; primary risk: data integrity, ownership and evidence correctness.
- Start condition: Task 001 Quality evidence and exact approved writable roots; implementation approval.
- End condition: DoD tested with phase5 Quality evidence and required capture; not just a green script.
- Readiness/status: completed (current scoped implementation; no runtime activation).
- User decision required before implementation: yes; scoped implementation approval.
- Spec: specs/phase-3-wep-ledger-002-transactions-specification.md
- Spec QA: quality/phase-3-wep-ledger-002-transactions-spec-qa.md
- Quality: quality/phase-5-wep-ledger-002-transactions-quality.md (current implementation evidence).
- Proposed write surface: .systems/scripts/work_evidence.py; work-evidence-* wrappers; synthetic storage/transaction fixtures
- Uncertainty / activation gate: No dependency output yet; spec dependency-gated and refreshed after 001. Source-to-entry semantic matching stays owner-reviewed.

## WEP-XLSX-003-local-tracker: Local Excel projection and manual intake
- Goal: Provide one clear local tracker per workspace while retaining safe manual custom entries.
- Scope: XLSX adapter, generated sheets, manual row identity, conflict preview, receipts, workbook integrity and import safety.
- Out-of-scope: No Google Sheets, macros, executing formulas, Make modifications or unattended bidirectional merge.
- DoD: Manual new/corrected entries round-trip idempotently; generated edits conflict rather than disappear; workbook opens and renders clearly with actual/estimated/unknown separated.
- Dependencies (blocking): WEP-DATA-001-contracts, WEP-LEDGER-002-transactions
- Informational dependencies: accepted context and versioned architecture; historical artifacts do not grant approval.
- Risk: high; primary risk: data integrity, ownership and evidence correctness.
- Start condition: 001/002 Quality; reviewed and approved pinned XLSX dependency/version/license/security; implementation approval.
- End condition: DoD tested with phase5 Quality evidence and required capture; not just a green script.
- Readiness/status: completed (current scoped implementation; no runtime activation).
- User decision required before implementation: yes; scoped implementation approval plus dependency approval.
- Spec: specs/phase-3-wep-xlsx-003-local-tracker-specification.md
- Spec QA: quality/phase-3-wep-xlsx-003-local-tracker-spec-qa.md
- Quality: quality/phase-5-wep-xlsx-003-local-tracker-quality.md (current implementation evidence).
- Proposed write surface: .systems/scripts/work_evidence_xlsx.py; workbook templates; dependency declaration; XLSX synthetic tests
- Uncertainty / activation gate: Dependency assessment pending blocks implementation/install of adapter; owner decision recommendation reviewed pinned openpyxl, alternative approved XLSX library behind same interface.

## WEP-DOCS-004-replay-kit: Reproducible documentation packages
- Goal: Turn evidence into a procedure another programmer can execute without the owner.
- Scope: Procedure schema/template, explicit selected-source assembler, replay checklist and redacted mock package.
- Out-of-scope: No actual contractor access, production credentials, inferred completion or code modifications in DealerCRM.
- DoD: Package states prerequisites, inputs, exact steps, expected outputs, tests, failure/rollback and evidence; only signed human replay evidence can mark replay-passed.
- Dependencies (blocking): WEP-DATA-001-contracts, WEP-LEDGER-002-transactions
- Informational dependencies: accepted context and versioned architecture; historical artifacts do not grant approval.
- Risk: high; primary risk: data integrity, ownership and evidence correctness.
- Start condition: 001/002 Quality and explicit source allowlist; implementation approval.
- End condition: DoD tested with phase5 Quality evidence and required capture; not just a green script.
- Readiness/status: completed (current scoped implementation; no runtime activation).
- User decision required before implementation: yes; scoped implementation approval.
- Spec: specs/phase-3-wep-docs-004-replay-kit-specification.md
- Spec QA: quality/phase-3-wep-docs-004-replay-kit-spec-qa.md
- Quality: quality/phase-5-wep-docs-004-replay-kit-quality.md (current implementation evidence).
- Proposed write surface: .systems/ai/templates/work-evidence/procedure/; .systems/scripts/work-evidence-documentation; synthetic kit fixtures
- Uncertainty / activation gate: Actual tester/access requires owner action at pilot; template and assembler are independently testable now.

## WEP-REPORT-005-client-drafts: Weekly and monthly client report drafts
- Goal: Report actual outcomes clearly without inventing recurring work or exposing other clients.
- Scope: Period queries, client-safe field projection, contracted-care catalogue and local Markdown/HTML draft rendering.
- Out-of-scope: No email sends/draft API, audience import, contractual changes or manufactured time for ongoing care.
- DoD: Week/month reports reconcile to committed ledger, show coverage and distinguish delivered work from contracted recurring scope; recipient isolation tests pass.
- Dependencies (blocking): WEP-DATA-001-contracts, WEP-LEDGER-002-transactions
- Informational dependencies: accepted context and versioned architecture; historical artifacts do not grant approval.
- Risk: high; primary risk: data integrity, ownership and evidence correctness.
- Start condition: 001/002 Quality; owner-approved recipient aliases, scope catalogue and field policy before real reports.
- End condition: DoD tested with phase5 Quality evidence and required capture; not just a green script.
- Readiness/status: completed (current scoped implementation; no runtime activation).
- User decision required before implementation: yes; scoped implementation approval.
- Spec: specs/phase-3-wep-report-005-client-drafts-specification.md
- Spec QA: quality/phase-3-wep-report-005-client-drafts-spec-qa.md
- Quality: quality/phase-5-wep-report-005-client-drafts-quality.md (current implementation evidence).
- Proposed write surface: .systems/scripts/work-evidence-report; report templates; synthetic recipient/period fixtures
- Uncertainty / activation gate: Real safe-field and recurring-care policies to be approved on pilot; default internal-only is safe, not auto-client-visible.

## WEP-TAX-006-evidence-register: Private IP and financial evidence register
- Goal: Prepare traceable advisor evidence without asserting qualification.
- Scope: Taxpayer/IP/rights/finance identities, allocation links, missingness reports and private advisor packet.
- Out-of-scope: No automatic IP qualification, reading bank accounts, tax filing, public distribution or importing example percentages as policy.
- DoD: Every proposed financial/IP allocation traces to evidence; conflicting taxpayer, missing rights or unsupported amounts remain blocked/unknown, not eligible by default.
- Dependencies (blocking): WEP-DATA-001-contracts, WEP-LEDGER-002-transactions, WEP-DOCS-004-replay-kit
- Informational dependencies: accepted context and versioned architecture; historical artifacts do not grant approval.
- Risk: high; primary risk: financial attribution and false qualification.
- Start condition: 001/002/004 Quality; implementation approval; taxpayer/root mapping before real data entry.
- End condition: DoD tested with phase5 Quality evidence and required capture; not just a green script.
- Readiness/status: completed (current scoped implementation; no runtime activation).
- User decision required before implementation: yes; scoped implementation approval.
- Spec: specs/phase-3-wep-tax-006-evidence-register-specification.md
- Spec QA: quality/phase-3-wep-tax-006-evidence-register-spec-qa.md
- Quality: quality/phase-5-wep-tax-006-evidence-register-quality.md (current implementation evidence).
- Proposed write surface: .systems/ai/templates/work-evidence/tax/; .systems/scripts/work-evidence-tax-evidence; sanitized fixtures
- Uncertainty / activation gate: Actual taxpayer and advisor classification unavailable; activation gate, not an engine default.

## WEP-TAX-007-rule-calculator: Advisor-gated deterministic calculation engine
- Goal: Compute only from applicable approved rules with reproducible intermediate results.
- Scope: Rule envelope validation, restricted Decimal evaluator, approval/staleness checks and synthetic reference tests.
- Out-of-scope: No authoring legal rules on behalf of advisor, generic inherited92-98%, filing, external tax services or real calculation without gate.
- DoD: Approved synthetic golden cases reconcile exactly to declared rounding; missing/revoked/wrong-period rules block output; every operand has provenance.
- Dependencies (blocking): WEP-TAX-006-evidence-register
- Informational dependencies: accepted context and versioned architecture; historical artifacts do not grant approval.
- Risk: high; primary risk: financial attribution and false qualification.
- Start condition: 006 Quality and implementation approval; real activation additionally requires advisor-signed complete rules and reviewed reference cases.
- End condition: DoD tested with phase5 Quality evidence and required capture; not just a green script.
- Readiness/status: completed (current scoped implementation; no runtime activation).
- User decision required before implementation: yes; scoped implementation approval.
- Spec: specs/phase-3-wep-tax-007-rule-calculator-specification.md
- Spec QA: quality/phase-3-wep-tax-007-rule-calculator-spec-qa.md
- Quality: quality/phase-5-wep-tax-007-rule-calculator-quality.md (current implementation evidence).
- Proposed write surface: .systems/scripts/work_evidence_tax.py; work-evidence-tax-calculate; synthetic rule/golden fixtures
- Uncertainty / activation gate: Fiscal rules not yet provided. Generic evaluator can be implemented; activation stays blocked. Recommendation advisor supplies declarative rules+golden cases; alternative evidence-only operation.

## WEP-CONTENT-008-editorial-drafts: Two-brand editorial and anonymization pipeline
- Goal: Reuse valuable work evidence in distinct source-backed newsletter and social drafts.
- Scope: Source selection, claim registry, anonymized derivatives, brand/language briefs, local drafts and per-version review queue.
- Out-of-scope: No social/email publication APIs, audience lists, tax/raw-dump ingestion or consent inferred from anonymization.
- DoD: One case produces two appropriate newsletter drafts and linked social derivatives with traceable claims, privacy labels and independent approvals; source secrets never enter output.
- Dependencies (blocking): WEP-DATA-001-contracts, WEP-LEDGER-002-transactions, WEP-DOCS-004-replay-kit
- Informational dependencies: accepted context and versioned architecture; historical artifacts do not grant approval.
- Risk: high; primary risk: privacy and unsupported claims.
- Start condition: 001/002/004 Quality; exact approved source roots and destination; implementation approval.
- End condition: DoD tested with phase5 Quality evidence and required capture; not just a green script.
- Readiness/status: completed (current scoped implementation; no runtime activation).
- User decision required before implementation: yes; scoped implementation approval.
- Spec: specs/phase-3-wep-content-008-editorial-drafts-specification.md
- Spec QA: quality/phase-3-wep-content-008-editorial-drafts-spec-qa.md
- Quality: quality/phase-5-wep-content-008-editorial-drafts-quality.md (current implementation evidence).
- Proposed write surface: .systems/ai/core/work-evidence-editorial.md; bundle CLI; private draft templates; synthetic privacy/claim tests
- Uncertainty / activation gate: Audience outcomes unknown until measured; no promise of newsletter conversion. Real content remains draft and owner-reviewed.

## WEP-QA-009-regression-suite: Cross-flow regression and release safeguards
- Goal: Prove end-to-end integrity and privacy before using real runtime data.
- Scope: Synthetic cross-flow harness, failpoint testing, product validator routing, documentation and explicit rollout/rollback tooling.
- Out-of-scope: No production activation, history migration, broad runtime scan or automatic updater invocation.
- DoD: Full synthetic scenario preserves totals/ownership/privacy through ledger, Excel, report, docs, tax and content; backup/rebuild and negative-path tests pass.
- Dependencies (blocking): WEP-DATA-001-contracts, WEP-LEDGER-002-transactions, WEP-XLSX-003-local-tracker, WEP-DOCS-004-replay-kit, WEP-REPORT-005-client-drafts, WEP-TAX-006-evidence-register, WEP-TAX-007-rule-calculator, WEP-CONTENT-008-editorial-drafts
- Informational dependencies: accepted context and versioned architecture; historical artifacts do not grant approval.
- Risk: high; primary risk: data integrity, ownership and evidence correctness.
- Start condition: 001-008 phase5 Quality and upstream implementation approval; explicit controlled fixture roots.
- End condition: DoD tested with phase5 Quality evidence and required capture; not just a green script.
- Readiness/status: completed (current scoped implementation; no runtime activation).
- User decision required before implementation: yes; scoped implementation approval.
- Spec: specs/phase-3-wep-qa-009-regression-suite-specification.md
- Spec QA: quality/phase-3-wep-qa-009-regression-suite-spec-qa.md
- Quality: quality/phase-5-wep-qa-009-regression-suite-quality.md (current implementation evidence).
- Proposed write surface: .systems/scripts/check-work-evidence; product validation routing; synthetic fixtures; sanitized runbooks
- Uncertainty / activation gate: Exact implementation command entrypoints refreshed after upstream tasks; plan fixes test invariants, not fabricated test results.

## WEP-PILOT-010-dealercrm-rollout: DealerCRM human pilot and gated two-workspace rollout
- Goal: Validate useful outputs and owner-independent replay on one controlled real case before routine use.
- Scope: Approved local DealerCRM evidence selection, mock-only kit, real human replay, local tracker/report/draft pilot, later scoped runtime activation.
- Out-of-scope: No production/API access, actual newsletter sends, tax filing, history import, automatic Make retirement or unrestricted contractor disclosure.
- DoD: Independent programmer reproduces accepted mock result without owner help; actual time reconciles and every draft/projection passes privacy review; owner explicitly accepts pilot before cutover.
- Dependencies (blocking): WEP-QA-009-regression-suite
- Informational dependencies: accepted context and versioned architecture; historical artifacts do not grant approval.
- Risk: high; primary risk: unsafe disclosure and false reproducibility.
- Start condition: 009 Quality; owner approves tester, redacted access bundle, expected result, writable roots, cutover and backup/rollback. Tax calculation additionally gated by D04.
- End condition: DoD tested with phase5 Quality evidence and required capture; not just a green script.
- Readiness/status: deferred by current owner decision; not completed.
- User decision required before implementation: yes; scoped implementation approval plus pilot activation decisions.
- Spec: specs/phase-3-wep-pilot-010-dealercrm-rollout-specification.md
- Spec QA: quality/phase-3-wep-pilot-010-dealercrm-rollout-spec-qa.md
- Quality: none currently; future target quality/phase-5-wep-pilot-010-dealercrm-rollout-quality.md, not produced by planning.
- Proposed write surface: private approved pilot namespace; runtime work-evidence roots only after activation approval
- Uncertainty / activation gate: Conditional real execution: tester, safe bundle, expected result and cutover require owner decision. Recommendation one mock-only human pilot; alternative remain on synthetic validation with no replay-success claim.

## Pilot Acceptance Matrix
| Gate | Evidence | Failure response |
| --- | --- | --- |
| Selected DealerCRM stage | approved exact local source/version and expected mock outcome | no pilot start |
| Human independence | qualified programmer log, no owner help, assertions met | revise kit and replay; no success claim |
| Time integrity | session/entry/revision reconcile; rerun no duplicates | fix ledger before cutover |
| Projection privacy | recipient and brand-specific review, no private canaries | hold affected outputs |
| Tax | advisor evidence packet complete or gaps explicit | evidence-only; real calculation blocked |
| Owner usability | measured time/documentation overhead, owner accept/rework | remain pilot |
| Cutover | exact two-workspace paths, backups and restore rehearsal, owner approval | existing process stays active |

## Required Verification
Per-task unit/integration/adversarial tests specified in phase3. At 009: check-work-evidence, applicable Personal Ops/Task Management regressions, Python compile, git diff --check and full AI System upgrade validation without skipped smoke tests. Project Workflow validation follows current validation-routing; ordinary artifact QA uses targeted evidence/status checks, not broad system tests.
Every actual command/outcome must be recorded; planned commands are not test evidence. No real private fixtures in product or upstream tracked docs.
## Recovery And Change Control
Preview before any runtime import; no history migration/backfill in this plan. Keep source snapshots and immutable revisions. Rollback requires approval and hash-bound manifest, stops on newer user edits. Existing Make/Sheets remain until separate retirement decision. Material scope/technology changes return to architecture/plan QA, not silent substitutions.
## Delivery Constraints
Mode owner-opt-out: no deadline or time budget; must-have complete foundation/projections/evidence/drafts/pilot with privacy and QA. No stretch scope. No cutline inside must-have. Stop on failed gates or missing material decisions, not lower quality.
## Plan Quality Contract
Plan classification: implementation-capable.
DoD source: context.md, owner D01-D10 and approved architecture.
Testable DoD / acceptance conditions: ten complete task contracts, acyclic hard dependencies, source matrix and gated pilot; implementation judged per task.
Artifact QA route: phase-2-plan-qa; trigger: plan plus task index completed.
Implementation Quality Closure route: phase-5-quality per task.
Required verification: semantic scope/field/dependency review, index comparison, failure scenarios and targeted artifact validators.
Quality-ready criteria: no P0/P1/material P2 open; conditional activation cannot be mistaken for readiness.
Owner opt-out: none for quality. Not-applicable reason: none. Blocking decision: none for planning.
Next route: phase-2-plan-qa.
## Owner Decision Checkpoint
Interaction mode queued; clear for planning. D04/D05/D08 govern later authorization. Recommend staged foundation implementation; alternative owner reviews plan first. Neither grants activation.
## Optional Knowledge Capture
Capture recommended yes; target plan/status/evidence; capture-now within planning scope. Technical distillation follows future implementation, no extra memory writes.
## Model Recommendation
Frontier/workhorse high reasoning; high-impact data and privacy policy; current model unknown; Blocking: no.

## WEP-CONTENT-011-editorial-routing: Topic Routing, Blogs And Video Concepts
Owner refinement 2026-10-05 is recorded in decisions/2026-10-05-wep-011-owner-review.md.
The seven human verdicts replace the missing-review blocker after applying their
corrections and fresh QA. Bounded follow-up adds private original review and
review-before-anonymization, readable receipt-bound private preservation, blog
summary plus newsletter bonus and the corrected case 3 route. No new cadence,
activation, commit, push or Phase 8. Existing task scope/quality floor is retained.
This new task extends completed WEP-008; it does not rewrite its v1 DoD or completion.
- Goal: make evidence reusable through the most appropriate brand/format route without a mandatory blog, newsletter or social chain.
- Scope: independent editorial v2 contract; deterministic prepare; topic/recommendation/owner-decision records; blog, newsletter and social briefs/drafts; short-video and YouTube concepts; immutable local bundles and source-bound review; compatibility and semantic QA.
- Out-of-scope: product AI Workflow, ledger schema changes, real runtime activation, historical migration, real publication, media production, CMS/API/scheduler, new dependencies, automatic editorial judgment or IP Box changes.
- DoD: seven synthetic cases cover varied routes, each with source-traceable claims, one main route and one alternative, independent fit/readiness, one/both brand selection, consistent capacity, honest uncertainty and owner decision. Legacy v1 fixtures remain unchanged. No private canary or unsupported claim crosses export; no route acceptance grants publication.
- Dependencies (blocking): historical delivered WEP-DATA-001-contracts, WEP-LEDGER-002-transactions, WEP-DOCS-004-replay-kit, WEP-CONTENT-008-editorial-drafts, WEP-QA-009-regression-suite, plus current interface/source refresh before implementation.
- Informational dependency: WEP-PILOT-010 remains deferred; no pilot required for synthetic v2 development, but real activation remains blocked until its gates.
- Risk: high; privacy, false source claims, stale approval and legacy regression.
- Start condition: current Architecture/Plan/Spec QA, current interface review and explicit owner-approved implementation for WEP-011. Authorization recorded in decisions/2026-10-03-wep-011-implementation-authorization.md.
- End condition: scoped Phase 5 Quality, preserved v1 regression evidence, all seven manual routing cases, required distillation and checkpoint. Phase 8 separately owner-triggered.
- Readiness/status: in-progress; code and technical tests complete, but DoD6 human review is missing. Quality closure blocked; real activation remains deferred.
- User decision required before implementation: resolved by exact owner-approved annotated prompt; no new dependency or material scope decision.
- Spec: specs/phase-3-wep-content-011-editorial-routing-specification.md
- Spec QA: quality/phase-3-wep-content-011-editorial-routing-spec-qa.md
- Quality: quality/phase-5-wep-content-011-editorial-routing-quality.md; owner supplied DoD6 review on 2026-10-05; bounded corrections require fresh source-bound reassessment, not runtime or final owner acceptance.
- Approved write surface: existing editorial CLI/module/core; new editorial-v2 schema/templates; synthetic tests and existing check-work-evidence integration; required private implementation/QA/capture artifacts.
- Delivery constraints: owner-opt-out, no deadline/timebox; full QA/privacy protected; no cutline in required compatibility/security; extras require new decision.

### Future Implementation Slices
| Order | Result | Verification / stop gate |
| --- | --- | --- |
| 1 | Independent v2 parser, schemas and v1 compatibility boundary | strict version/shape tests and unchanged v1 golden cases; stop on shared ledger/version regression |
| 2 | Explicit-source read-only prepare and topic/recommendation validation | source freshness, canary, path and no-write tests; no LLM calls |
| 3 | Owner route decision and optional artifact graph | wrong-scope/stale approval, DAG, one-brand and unavailable-format tests |
| 4 | Local briefs/drafts/concepts and bounded scheduling | per-format required fields, additive newsletter, missing URL, shared-language budget and slot collision cases |
| 5 | Immutable persistence, completion receipts and recovery | retry/crash/stale-input tests, no uncommitted bundle visible to consumers |
| 6 | End-to-end and manual semantic review | seven agent-authored synthetic cases and explicit reviewer limitations, v1 regressions, full diff/privacy review; real human privacy/publication review remains required later; then Phase 5/capture/checkpoint |
Slices are sequential parts of WEP-011, not separately authorized tasks or a hidden activation plan.

### Evidence And Data Matrix For Extension
| Producer -> consumer | Required linkage | Failure behavior |
| --- | --- | --- |
| ledger/approved proof -> prepare | entry/procedure/source IDs and current hashes | safe hold on unsupported topic; reject invalid/stale references |
| prepare -> agent recommendation | package digest, source claim IDs, selected brands and constraints | arbitrary text is data; no inferred execution authority |
| recommendation -> owner choice | primary/alternative, suitability, effort/gaps, recommendation digest | unaccepted recommendation cannot become selected route |
| owner choice -> drafts | choice digest, chosen node IDs, graph, brand/language/format | changed recommendation or decision requires fresh acceptance |
| drafts -> local review | rendered content plus claim/source/decision hashes | altered translation, metadata, CTA or source invalidates review |
| local review -> publication | no connection in this task | publication_authorized remains false |
Existing source-of-truth table above remains valid; new records never create counted time or fiscal eligibility.

### Artifact And Implementation QA
Current artifact route: Architecture QA -> Plan QA -> Specification QA with source hashes, producer-consumer audit and negative-path review. Private history preservation is verified byte-for-byte; no prior implementation/final verdict is refreshed.
Future required checks: editorial v1/v2 unit/contract/integration and seven manually assessed anonymized examples; check-work-evidence, Python compilation, git diff --check, applicable product regressions, full AI System validation without skipped smoke tests at release/upgrade. Workflow checks follow current validation routing; scoped ordinary work is not a full release.
Quality-ready: no P0/P1/material P2; human semantic scorecards distinguish unsupported assertions from editorial preference; all actual commands recorded. Unknown human pilot/tax rules are still separate gates.
Rollback: preserve v1, no auto migration; new v2 bundles remain private and immutable. Disabling v2 routing does not erase history or roll back user records. Any destructive restoration requires fresh approval.
Residual risk: a valid recommendation may still be unhelpful or re-identifying; schema/keyword tests cannot prove semantic safety.

### Current Plan Quality Contract
Classification: implementation-capable design, not implementation permission.
DoD source: WEP-CR-001 D11-D21 and architecture Editorial v2.
Implementation writes planned now: yes, bounded WEP-011 product and private Quality/capture scope under current authorization; no real runtime activation.
Artifact QA: phase-2-plan-qa and phase-3-spec-qa. Future quality: phase-5-quality -> distillation/checkpoint; final check separate.
Required verification: full artifact review, source-hash and status integrity, seven-case acceptance mapping and privacy/compatibility adversarial matrix.
Owner Decision Checkpoint: clear for approved implementation/QA; later activation and formal final closure remain separate decisions.
Optional Knowledge Capture: required technical distillation/checkpoint after Quality, project-scoped only; no Codex memory.
Model recommendation: workhorse/frontier high reasoning; non-blocking.
