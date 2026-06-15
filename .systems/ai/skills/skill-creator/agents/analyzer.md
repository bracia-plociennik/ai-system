# Skill Eval Analyzer

Use this analyzer after one or more skill evals have been graded or compared.

## Inputs

- `evals.json` or equivalent eval plan.
- One or more `grading.json` files.
- `benchmark.json` when available.
- `comparison.json` when available.
- Candidate skill diff or current skill files.
- Any known skipped checks.

## Method

1. Group failures by root cause: trigger, scope, missing procedure, missing reference, weak script, authority boundary, validation gap, stale documentation, or bad eval design.
2. Identify whether each failure is isolated, repeated, or systematic.
3. Compare configurations: where did `with_skill` help, hurt, or make no difference?
4. Look for non-discriminating assertions that pass in every configuration.
5. Look for assertions that fail in every configuration and may be out of scope or badly specified.
6. Look for high-variance evals, timing/token regressions, repeated workaround patterns, and missed bundled-resource opportunities.
7. Separate skill defects from invalid eval expectations.
8. Prefer the smallest skill edit that removes the repeated failure.
9. Do not convert every eval observation into permanent guidance. Keep only reusable procedure.

## Output

```text
verdict: <pass|needs-iteration|blocked>
main_failure_mode: <short label or none>
configuration_result:
- with_skill_helped: <evidence>
- with_skill_hurt: <evidence>
- no_difference: <evidence>
recommended_changes:
- file: <path>
  change: <specific edit>
  reason: <why this fixes observed evidence>
eval_design_changes:
- <assertion or eval improvement>
discarded_noise:
- <observation skipped because it is non-reusable, duplicate, or unsupported>
residual_risk:
- <remaining risk or none>
```
