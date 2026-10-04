# Distillation State

- Capture schema: 2

- Work ID: `<stable-work-id>`
- Work mode: `<project|micro-task|micro-project|side-task|system-maintenance|client-work>`
- Owner scope: `<workspace|primary-entity|client|owned-asset|project>`
- Scope path: `<workspace-relative-path>`
- Source artifacts: `<workspace-relative paths or none>`
- Quality evidence: `<paths, checks, or none>`
- State: `<pending-quality|ready|completed|deferred|owner-skipped|blocked|not-applicable>`
- Distillation artifact: `<workspace-relative path|none>`
- Last reminder: `<timestamp|none>`
- Owner disposition: `<capture-now|defer|skip|blocked|not-requested>`
- Privacy/scope check: `<pass|fail|unknown>`
- Residual risk: `<risk or none>`
- `is_distilled` derived value: `<true only for completed; false otherwise>`

## Capture Verification

Populate before ready/completed; pending-quality does not claim current QA.
Source/evidence roots are exact local runtime selections, never reusable private product defaults.

```json
{
  "work_id": "replace-with-work-id",
  "project": "replace-with-owning-project",
  "task_ids": [],
  "source_root": "replace-with-selected-source-root",
  "source_head": "replace-with-current-head",
  "evidence_root": "replace-with-workspace-relative-evidence-root",
  "qa_refs": [],
  "distillation_sha256": "replace-after-accepted-distillation"
}
```
