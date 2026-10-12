# ASYS-CR-011-local-paths

- Project: ai-system
- Timing: post-final-approval
- Type: follow-up-enhancement
- Status: in-progress
- Risk: high
- Owner request: portable HOME/AI_SYSTEM_HOME paths for tasks, Work Evidence and projects; analyze history compatibility; plan through Spec QA then implementation range; Auto; local commits approved
- Approval: decisions/2026-10-09-cr-011-owner-scope.md
- Triage result: scoped path resolver and transaction safety form one dependent task; old Capture repair excluded
- Routing decision: new-project-iteration
- Task: ASYS-CORE-019-local-paths
- Evidence required: architecture/plan/spec QA; exact source diff; synthetic and existing regression tests; full product validation; current Phase 5; distillation and final Phase 7
- Final check impact: new iteration stops before separately requested Phase 8; old final-owner approvals remain immutable
- Post-final impact: no reopening or reinterpretation of historical CRs; no product publication or management update
- Target worktree: /home/ubuntu/ai-system/onlinen-workspace/projects/ai-system-paths-dev, codex/asys-cr-011-local-paths from verified dev 1c9efd74a569be68c96b3cc347c8210deaf3cfa9

## Task Intake

Co zostaje: Markdown tasks independent of TaskForge, literal configs, raw hashes, owner scopes, historical evidence.
Co jest słabe / do poprawy lub usunięcia: divergent path resolution and missing variable-context transaction binding.
Czego brakuje: shared resolver and synthetic cross-host/versioning proof; outputs of this iteration.
Blokery / decyzje: none for the approved local range; real Mac run/publication excluded.
Rekomendowany routing: full architecture/plan/spec gates -> implementation -> Quality -> distillation/checkpoint.

## Batch Triage

| item | group | theme | risk | routing | target project/workspace | dependencies | owner decision | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| paths and transaction context | paths | portable roots | high | change-request-candidate | Onlinen / ai-system | resolver then consumers then QA | covered by owner scope | aliases and write context must remain coherent |
| existing Capture defects | capture | historical evidence | unknown | change-request-candidate | Onlinen / Kuba | separate intake | separate approval | explicitly excluded |

Triage supplies no additional authority; actual owner instruction and local phase gates govern writes.
