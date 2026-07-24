# Model Selection Guidance

## Purpose

Give the owner an advisory model recommendation for every new planning, implementation, and QA scope.

## Required Output

```text
Model recommendation:
- Recommended: <GPT-5.6 Luna High|GPT-5.6 Sol High>
- Reason:
- Criticality:
- Current model known: <yes|no>
- Blocking: no
```

Use `Current model known: no` when the runtime does not expose the active model. Do not guess.

## Recommendation Rules

Recommend `GPT-5.6 Luna High` for clear, bounded, reversible work with a testable Definition of Done and low or medium risk. Examples include routine implementation, narrow documentation, targeted review, and local deterministic fixes.

Recommend `GPT-5.6 Sol High` for difficult architecture, substantial ambiguity, security, billing, migrations, production changes, broad integrations, recovery, adversarial review, high-risk work, or high-impact AI System policy changes.

Deadline pressure, model availability, or cost preference does not justify recommending a weaker model for critical work. If the owner continues with another model, keep all workflow requirements unchanged.

## Authority Boundary

Model selection is advisory-only:

- `Blocking: no` is mandatory;
- model choice does not change source-of-truth order, scope, risk, privacy, permissions, Definition of Done, evidence, QA, approvals, or stop conditions;
- a model recommendation cannot guarantee correctness or `PASS`.
