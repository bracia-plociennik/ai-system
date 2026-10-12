# Adversarial Review 02 Findings

- Reviewer: native agent 01a10338-3d9a-7050-a56a-dcfaed4b558c
- Attempt: ppo-audit-02, read-only
- Disposition: initial post-fix assessment still found two P2 alias boundaries; no PASS claimed

## Findings Preserved

1. Protected path components used case-sensitive matching; .GIT, AI-WORKFLOW and .ENV aliases could bypass metadata restrictions on a case-insensitive filesystem. Fix: casefold protected components and environment-file prefixes; explicit regressions.
2. Disjoint write-set strings could name the same path by case/Unicode spelling. Fix: conservative NFC/casefold overlap comparison, including parent-child claims; explicit case and composed/decomposed Unicode regressions. This may serialize distinct case-sensitive paths, intentionally preferring safety.

The reviewer found no additional defect in the fixture-only timeout/readiness changes: production timeout behavior and all lifecycle/marker/PID-death assertions were preserved. Post-fix full review is recorded separately. Earlier rejected evidence remains historical and cannot supply current PASS.
