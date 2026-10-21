# Validation Routing

## Purpose

Separate semantic and product QA from AI System script validation.

AI System scripts are applicable supporting evidence. They are never the source of a quality verdict and must not replace intent review, Definition of Done, findings-first review, product checks, or manual verification.

## Required Order

For every QA, quality closure, checkpoint, or final system verification:

1. compare the work with owner intent, scope, Definition of Done, and the accepted plan or specification;
2. perform findings-first code, diff, or artifact review;
3. inspect edge cases, regressions, failure paths, skipped checks, and residual risk;
4. run safe and applicable target-product tests, builds, and manual checks;
5. run only applicable `.systems/scripts/**` checks as supporting evidence;
6. issue the artifact-appropriate final verdict from the complete evidence.

Green scripts do not equal `PASS`. A semantic mismatch, unresolved blocker, material finding, incomplete Definition of Done, or missing product evidence cannot be overridden by script output.

## Routing Matrix

| Work | Semantic or product QA | AI System scripts |
| --- | --- | --- |
| Active implementation, micro-task, client implementation, PDF, document, or design work | required for the current artifact or product | no broad `validate-ai-system`; use product checks instead |
| Architecture, project plan, specification, package, or artifact QA | semantic artifact review first | targeted artifact validators only when applicable |
| Ordinary implementation quality review | findings-first diff/code review and product tests | only targeted checks for changed AI System contracts or runtime artifacts |
| Distillation or capture quality | source, privacy, evidence, and state review | only applicable capture, privacy, or state checks |
| Checkpoint | checkpoint completeness and resume-safety review first | explicit profile selected through `validation-profiles.md` when applicable |
| CI, final system verification, upstream update, or high-impact system maintenance | full current-diff semantic review first | explicit `full` profile |

Running an implementation tool or generating an artifact must not automatically trigger broad AI System validation. Broad validation belongs to an applicable quality or checkpoint route after semantic and product review.

When `.systems/ai/core/project-orchestration.md` routes work into another repository, run its applicable product checks and local AI Workflow artifact validation. AI System's broad validators apply to changes in AI System contracts, not merely to an implementation coordinated by AI System. Review the executor's diff and evidence before reporting a verdict; do not treat a worker's `done` message as QA.

## Safe Local Iteration

Within an already approved, bounded local implementation, run the relevant focused test, fix an observed failure in the approved files, and retest without asking for approval at every iteration. This loop does not expand the file set, change the target, or authorize an external effect. Stop and seek a new decision if a fix requires broader scope, production access, secrets, destructive actions, a new dependency with material risk, or a changed acceptance criterion. A passing local test is product evidence, not the final quality verdict; still perform semantic review and route-specific QA before closure.

## Validation Execution Record

### Bounded Recovery Evidence

Preserve every failed run and its source identity. Each retry records the observed failure,
one new falsifiable hypothesis, the approved files changed, the focused retest and its result.
Do not repeat an unchanged failed command without new evidence, weaken an assertion, suppress
an unexpected exit or expand permissions to get a green result. Infrastructure failures are
not expected negative-test success. A source change invalidates prior current-diff closure;
perform a fresh semantic review and applicable product checks after the fix before final evidence.

### Runtime-Only Checkpoint Coverage

A scoped runtime checkpoint can be considered only with a complete owned-namespace inventory,
current fingerprints, declared dependency closure and separate semantic/privacy evidence.
Execution coverage, scope coverage and final-evidence eligibility are different fields.
The candidate flag is supporting evidence, not automatic acceptance. Unmapped inputs, stale
evidence or incomplete dependencies stop eligibility. Shared product integration, CI, updater
and final system verification remain full-required. See `validation-profiles.md`.

Use `.systems/ai/templates/quality/validation-execution-record.template.md`.

QA artifacts and substantive quality closures record:

```text
Validation Execution Record
- Semantic QA result:
- Findings/blockers:
- Product checks:
- AI System script applicability:
- Targeted AI System commands:
- Script evidence role: supporting-only
- Final verdict:
```

`AI System script applicability` is `applicable` or `not-applicable` with a reason. The final verdict comes from all semantic and product evidence, not from script exit status alone.

## Relationship To Validation Profiles

Use `execution-efficiency.md` to plan product/runtime-artifact/integration/environment checks,
reuse explicitly selected authenticated evidence, and retain immutable historical assessments.
The runner records applicability and invalidation reasons; unknown impact executes. Reuse never
replaces fresh semantic review or an installed full-required gate. Whole-process intervals in
the compact quality record explain refresh, tests, artifact rework and owner waiting separately.

`.systems/ai/core/validation-profiles.md` defines what each profile runs and what evidence it supplies.

This contract decides whether scripts are applicable and when they run. Profile selection never moves scripts before semantic QA.

## Authority Boundary

Validation routing does not weaken privacy, risk, permissions, owner approvals, acceptance criteria, evidence, Delivery Constraints, Distillation State, contract compliance, or final acceptance.

A skipped inapplicable AI System script is not a skipped product check.


## Intent brief supporting verification

check-intent-to-execution-brief runs standalone synthetic profile/corpus regressions in standard/full. With --workflow-root and explicit --expected-head it purely inspects accepted installed source capability; no writes, install, native proof or owner consent. Full source gates include smoke. Native25-case paired original-input review is separate required implementation evidence; green scripts are supporting-only. Existing execution-mode fixed14 contract1/readiness2/QA2/Capture2 unchanged.


## Goal-Focused Maintenance Integration

Use goal-focused-maintenance.md only after explicit scoped activation and verified local support. One nearest-owner private maintenance/queue.json records proven independent incidental debt; project coordination references the Workflow-owned queue rather than duplicating it. E01–E05 and actual current-goal blockers are immediate. Five distinct active project causes or the third actual affected parent task schedule one consolidated milestone summary; scans/resumes do not count or repeat receipts. One stable approved parent shares TOTAL 600 seconds incidental diagnosis/edit/review/test/record work across both adapters. No background executor, scheduler or automatic TaskNotes. Required current QA and full release/updater failures remain binding. Missing counterpart support keeps existing gates; labels are not activation or authority.

Explicit current-goal selection is not full validation. It derives actual current dependency closure from canonical proof and preserves exhaustive errors internally. Default full/source/release/updater gates execute fresh and keep FAIL; independent historical errors never create current PASS. Semantic QA remains first.

## Sprint iteration

For actual task-local Sprint selection use `sprint-iteration.md` and the compatible installed Workflow. Keep preview/feedback implementation open until genuine final current-effect acceptance or explicit verification request. Deferred quality is not completed/PASS or resource release. Preserve normal behavior without explicit activation.


## Concurrent validation inputs

Follow `validation-concurrency.md`: automatic product-v1 stability guards run even without timing. Select actual runtime inputs with the owning project/scope manifest or repeatable `--validation-input-root`. Unrelated runtime writes are not product drift; changed assessed inputs never grant successful evidence. No automatic retry or historical QA rewrite.
