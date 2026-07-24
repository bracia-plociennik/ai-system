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

## Validation Execution Record

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

`.systems/ai/core/validation-profiles.md` defines what each profile runs and what evidence it supplies.

This contract decides whether scripts are applicable and when they run. Profile selection never moves scripts before semantic QA.

## Authority Boundary

Validation routing does not weaken privacy, risk, permissions, owner approvals, acceptance criteria, evidence, Delivery Constraints, Distillation State, contract compliance, or final acceptance.

A skipped inapplicable AI System script is not a skipped product check.
