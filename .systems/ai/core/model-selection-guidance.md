# Model Selection Guidance

## Purpose

Give the owner an advisory model recommendation for every new planning, implementation, and QA scope.

## Required Output

```text
Model recommendation:
- Recommended: <available model and effort, or capability class when availability is unknown>
- Reason:
- Criticality:
- Current model known: <yes|no>
- Blocking: no
```

Use `Current model known: no` when the runtime does not expose the active model. Recommend an exact model only when its availability is known; otherwise name a capability class. Do not guess the current model or promise a model switch.

## Recommendation Rules

Recommend a fast capable model for clear, bounded, reversible work with a testable Definition of Done and low or medium risk. Examples include routine implementation, narrow documentation, targeted review, and local deterministic fixes.

Recommend a workhorse or frontier model for difficult architecture, substantial ambiguity, security, billing, migrations, production changes, broad integrations, recovery, adversarial review, high-risk work, or high-impact AI System policy changes. Use the frontier class when the task needs deeper multi-step reasoning or adversarial evaluation. Select effort from task complexity, not from a fixed legacy model pair.

Earlier Luna/Sol labels were examples of fast/workhorse recommendations, not permanent required model names. Assess any newly available frontier model against the current task and supported effort options before recommending it. Availability and capabilities may change; never imply that an unverified model is selectable.

Deadline pressure, model availability, or cost preference does not justify recommending a weaker model for critical work. If the owner continues with another model, keep all workflow requirements unchanged.

## Authority Boundary

Model selection is advisory-only:

- `Blocking: no` is mandatory;
- model choice does not change source-of-truth order, scope, risk, privacy, permissions, Definition of Done, evidence, QA, approvals, or stop conditions;
- a model recommendation cannot guarantee correctness or `PASS`.

## Explicit Luna-first profile

Only an actually owner-activated source-verified luna-first-v1 component adds automatic native task selection and one-way takeover under core/luna-first.md. Outside that activation, guidance stays advisory. Preserve current owner choice, native support, risk, source, permissions and Sprint/QA/Phase8 gates. No claim that this switches a desktop root-chat model.
