# Autopilot State - autopilot-001

```yaml
autopilot:
  run-id: autopilot-001
  mode: supervised
  range: planning-range
  status: completed
  active-project: upgrade-with-master-prompt
  readiness-artifact: ai-workflow-workspace/projects/upgrade-with-master-prompt/autopilot/runs/autopilot-001/readiness.md
  readiness-result: ready
  owner-actions-status: resolved
  start-phase: phase-1-architecture
  stop-phase: phase-3-spec-qa
  stop-condition: all-planned-specs-pass
  started-at: 2026-06-11
  updated-at: 2026-06-11

current:
  task-id: UWMP-SYSTEM-001-prompt-composition-contract
  task-name: Milestone 1 Prompt Composition product contract
  phase: phase-3-spec-qa
  phase-artifact: ai-workflow-workspace/projects/upgrade-with-master-prompt/quality/phase-3-uwmp-system-001-prompt-composition-contract-spec-qa.md
  last-stable-pass: phase-3-spec-qa
  next-transition: phase-4-implementation

retry-counts:
  spec-qa-for-current-task: 0
  quality-for-current-task: 0
  total-for-run: 0

progress:
  completed-tasks: []
  completed-distillations-since-checkpoint: 0
  checkpoint-required-now: false
  last-checkpoint: null
  final-checkpoint-required: true
  final-check-owner-only: true

blockers: []
```
