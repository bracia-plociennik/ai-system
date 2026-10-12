# 3. Task Specification

## Metadata

- Project: `ai-system`
- Task/package ID: `ASYS-POPS-011-daily-check-in-v3-integrity`
- Task/package name: Daily Check-In v3 integrity fixes
- Date: `2026-07-14`
- Workflow phase: `3. FAZA SPECYFIKACJI`
- Readiness: `ready`

## Sources

- Owner-approved plan: `Fix Daily Check-In v3 Integrity`.
- Change request: `AI_WORKFLOW_WORKSPACE_HOME/projects/ai-system/change-requests/2026-07-14-ai-system-cr-002-daily-check-in-v3-integrity.md`.
- Prior V3 implementation diff and validator smoke suite.

## Task Contract

- Goal: make V3 report identity, task provenance, and candidate metrics trustworthy before `check-ins-v3.*` replacement or TaskForge audit use.
- Scope: add a canonical JSON reference property; validate basename/report ID/top-level/properties session identity; validate candidate count from planned item data; add V3 write/preflight/dedup/subtask smoke coverage.
- Out of scope: V2/V3.1 migration, runtime report edits, index backfill, TaskForge UI changes, and external services.
- Definition of Done: all four accepted findings are fixed with negative-path evidence; prior V3 behavior remains covered; full validation is green.
- Risk type: persisted local data and local TaskForge write path.
- Main risk: a malformed report might replace derived indexes or claim TaskNote provenance it does not retain.
- Requires user decision before implementation: `no`.

## Implementation Plan

1. Add and populate `task_generation_references_json` in the schema and V3 producer.
2. Enforce V3 report identity and one effective session row before any atomic index write.
3. Derive and validate `task_candidate_eligible_count` from professional `Task: create` plan items, respecting readiness and overload gates.
4. Extend V3 smoke fixtures for write success, subtask, rerun dedupe, unavailable vault, and invalid source preservation.
5. Run full validation and perform post-fix quality review.

## Edge Cases

| Edge Case | Expected Handling | Covered By Test? |
| --- | --- | --- |
| Report filename or ID disagrees with session date | Stop before replacing indexes. | yes |
| Candidate count drifts from planned items | Stop before replacing indexes. | yes |
| Repeat V3 TaskForge write | Preserve references and create no duplicate task/subtask. | yes |
| Vault preflight fails | Keep check-in writable with `skipped` and `[]` references. | yes |

## Tests And Pass Conditions

| Test / Check | Pass Condition |
| --- | --- |
| V3 smoke fixture | Success, skipped, deduplication, subtask, and invalid-property paths are covered. |
| V3 synchronizer | Rejects identity/count violations before writing indexes. |
| Full validation profile | All required product checks pass. |
| Final diff review | No unresolved in-scope findings or unrelated changes. |

## Implementation Gate

- DoD complete and testable: `yes`
- Dependencies satisfied or explicitly gated: `yes`
- Required user decisions resolved: `yes`
- Can enter implementation: `yes`
- Blocking reason: `none`

## Owner Decision Checkpoint

- Interaction mode: `none`
- Decision state: `clear`
- Material decisions: `accepted integrity plan`
- Questions asked: `none`
- Auto-resolved reversible decisions: `none`
- Optional owner refinements: `none`
- Decision artifacts: `owner-approved plan in conversation`
- Next route: `phase-4-implementation`

## Optional Knowledge Capture

- Capture recommended: `yes`
- Target: `status`
- Reason: post-final data-contract repair needs durable project evidence.
- Owner decision required: `no`
- Owner decision: `defer-to-distillation`
- Privacy/scope check: `pass`
- Suggested entry title: `Daily Check-In v3 integrity rules`
- Suggested entry summary: report identity and task provenance are producer-consumer invariants.
