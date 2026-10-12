# Upgrade With Master Prompt Code Review Router

## Purpose

`code-review.md` is the project-local review checklist and router.

Detailed review artifacts live in `reviews/`.

Review artifacts do not replace QA evidence in `quality/`.

## Review Checklist

- Scope matches the approved task or package.
- No unresolved blocking decisions were silently implemented.
- Behavior matches repo state, architecture, plan, and specification.
- Edge cases are covered or explicitly rejected with justification.
- Changed paths and direct dependencies were reviewed for regressions.
- Validation evidence is explicit, reproducible, and tied to the change.
- PASS is claimed only when all DoD conditions are met.
- Security, data, infrastructure, or contract risks are called out when relevant.
- Required docs and operational artifacts are updated when the change affects them.

## Review Index

| Date | Task | Result | Route |
| --- | --- | --- |
| 2026-06-12 | Prompt Composition final review after findings | `PASS` | `ai-workflow-workspace/projects/upgrade-with-master-prompt/reviews/final-prompt-composition-review-2026-06-12.md` |
