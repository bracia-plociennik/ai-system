# WEP-TAX-007-rule-calculator: Advisor-gated deterministic calculation engine
Date: 2026-10-02. Mode: solo task. Risk: high. Status: conditional specification, not implementation authorization.
## Inputs And Traceability
context.md; decisions/2026-10-02-owner-scope.md; architecture/phase-1-architecture.md; planning/phase-2-project-plan.md section WEP-TAX-007-rule-calculator; tasks.md; current Plan QA.
Predecessor006 Quality and TaxRegister.packet/write interfaces reviewed.
Calculator loads a relative private rules JSON on every invocation and recomputes
the current source-backed packet; no hidden operational index or stale cache.
Rule envelope: schema_version, rule, approval, revoked, synthetic, activation.
Rule fields: schema_version, rule_set_id, version, taxpayer_id, tax_year,
effective_start, end_exclusive, currency, precision, rounding, places, scope,
qualification_method, allocation_method, exclusions, inputs, expressions,
outputs, reference_cases. Inputs map names to finance_id/field(amount|allocated)/
unit(money). Expression nodes use op with const value/unit, ref name, or args.
Derived units are money in the configured currency or dimensionless ratio.
Approval binds rule_hash, advisor_id, approved_at, source_ref and owner_verified.
Actual activation additionally binds rule hash, taxpayer, approved_at/by owner
and advisor_reviewed=true. Missing activation blocks real calculations.
Synthetic envelopes are explicitly nonlegal, activation=null, still approval-
hash bound with fixture proof. Golden cases map every input name to Decimal
strings and every declared output to its expected rounded Decimal string.
Only an evidence-complete packet and passed reference cases can emit a result.
Preview/read are read-only. Write recomputes under owner ledger lock and compares
expected result hash; immutable private result. Read rechecks current rules,
revocation, approval and all source/ledger bindings; old output is stale on change.
## Goal, Scope And DoD
Goal: Compute only from applicable approved rules with reproducible intermediate results.
Scope: Rule envelope validation, restricted Decimal evaluator, approval/staleness checks and synthetic reference tests.
Out-of-scope: No authoring legal rules on behalf of advisor, generic inherited92-98%, filing, external tax services or real calculation without gate.
Testable DoD: Approved synthetic golden cases reconcile exactly to declared rounding; missing/revoked/wrong-period rules block output; every operand has provenance.
## Dependencies And Start Conditions
Blocking dependencies: WEP-TAX-006-evidence-register.
Start: 006 Quality and implementation approval; real activation additionally requires advisor-signed complete rules and reviewed reference cases.
Sequential only; no packages and no dependency on a future task. After predecessor output changes, refresh concrete file/function paths and rerun Spec QA before phase4. Do not substitute absent dependency evidence with this specification.
## Proposed Write Surface
.systems/scripts/work_evidence_tax.py; work-evidence-tax-calculate; synthetic rule/golden fixtures.
Paths are proposed implementation surfaces; inspect current repository at start and preserve other work. Product templates/tests use synthetic names and no real personal/client data. Actual runtime writes need exact owner-scoped approval, not merely product-code approval.
## Implementation Steps
1. Implement rule_set version/taxpayer/year/effective dates/approval locator+hash/advisor/revocation fields and allowlisted expression nodes constant/ref/add/subtract/multiply/divide/sum/ratio/min/max with declared Decimal precision and rounding. Define operand/result types; multiplication of money by a dimensionless ratio returns money, money divided by money returns ratio. Reject unsupported dimensions and nonfinite values.
2. Validate bounded expression depth/size, acyclic references, typed monetary/ratio inputs, positive nonzero denominators as required by declared policy, currency mapping and allocation basis. No eval, imports or arbitrary code.
3. Evaluate into a trace containing operands, rule ID/version and intermediate/result decimals; output blocked with gap codes when required input absent. Do not emit a partial result labeled full tax.
4. Persist local result only with scoped approval; bind all input/rule/approval hashes. Recheck on read; source correction, rule revocation or approval mismatch makes status stale and ineligible as current.
5. Use anonymized synthetic rules clearly marked nonlegal for development. Activation workflow validates actual advisor packet and golden examples without inferring legal eligibility from tests.
## Tests And Acceptance
Tests below are required future execution, not runs performed by planning.
1. Unit: exact Decimal outcomes/rounding against synthetic golden table; float input and unknown precision rejected. Nonlegal arithmetic example: (100.00 - 20.00) * 0.25 = 20.00 with explicitly declared two-decimal half-up rounding. Reject NaN/infinity, money multiplied by money and every zero denominator. This is only an evaluator example, not an IP Box formula or rate.
2. Security: unsupported operation, recursion/cycle, oversized expression, zero denominator and code string rejected without execution.
3. Integration: wrong taxpayer/year, missing approval hash, revoked rule or modified source blocks current output.
4. Integration: missing amount differs from explicit zero; partial coverage cannot yield full eligible-income/tax result.
5. Human gate: real calculations require approved applicable rules and independent advisor reference comparison; absent gate is visible blocked.
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
Fiscal rules not yet provided. Generic evaluator can be implemented; activation stays blocked. Recommendation advisor supplies declarative rules+golden cases; alternative evidence-only operation.
Recommendation: authorize only this task after its stated prerequisites are met; protect activation gates.
Alternative: retain specification for review without implementing, preserving the current tools.
Design uncertainty blocking specification: none within the explicitly bounded contract.
Implementation blockers: missing scoped implementation approval, predecessor Quality and interface refresh.
## Implementation Gate
All start conditions satisfied: yes for synthetic engine after current Spec QA.
Can proceed to implementation now: yes after refreshed Spec QA.
Reason: explicit implementation authorization,006 Quality and concrete API refresh.
Real taxpayer/advisor reference approval remains a distinct activation gate.
## Plan Quality Contract
Plan classification: implementation-capable.
DoD source: canonical plan WEP-TAX-007-rule-calculator and D01-D10.
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
