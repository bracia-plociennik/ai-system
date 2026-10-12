# Ownership And Publication Boundary

## Owned Product Inventory

- .systems/ai/core/command-routing.md
- .systems/ai/core/execution-efficiency.md
- .systems/ai/core/operating-model.md
- .systems/ai/core/project-orchestration.md
- .systems/ai/core/task-intake.md
- .systems/ai/core/validation-profiles.md
- .systems/ai/core/validation-routing.md
- .systems/ai/templates/quality/execution-quality-record.template.json
- .systems/ai/templates/root/AGENTS.template.md
- .systems/scripts/README.md
- .systems/scripts/check-execution-efficiency
- .systems/scripts/check-required-artifacts
- .systems/scripts/execution_efficiency.py
- .systems/scripts/prepare-quality-record
- .systems/scripts/project-orchestration-preflight
- .systems/scripts/tests/benchmark_execution_efficiency.py
- .systems/scripts/tests/test_execution_efficiency.py
- .systems/scripts/tests/test_validation_integrity.py
- .systems/scripts/validate-ai-system
- .systems/scripts/validation-dependencies.json
- .systems/scripts/validation_runner.py
- HUMANS.md
- README.md

## Owned Execution Evidence

Only this project's new records, the delivered counterpart handoff/index entry and the canonical
nearest-owner capture-state record are part of this execution. Product source digest is
1d2f8cee4695436a106d2f0052c9ea2abba908122b4c86f578e0ba2f7d305188.

## Pre-Existing Changes

The following four prior CR-010 files were dirty at intake and were not edited here:
- ai-workflow-workspace/projects/ai-system/status.md
- ai-workflow-workspace/projects/ai-system/tasks.md
- ai-workflow-workspace/projects/ai-system/change-requests.md
- ai-workflow-workspace/projects/ai-system/change-requests/2026-10-02-ai-system-cr-010-overnight-schedules.md

Their presence is not a blocker for this isolated technical project, but they must never be
staged as this scope. Root AGENTS and nested Workflow remain unchanged. Management rollout
and client/private runtime writes are excluded.

## Recovery Evidence

- Product full-run failure is preserved in quality/product-first-failed.md.
- Intermediate successful runs are retained as historical source assessments.
- Final product evidence is quality/product-release-full.md.
- Workflow timing preflight rejected the first runtime output location before testing;
  the permitted retry uses a new tmp location. No assertion, guard or suite was removed.
- Sandbox ps inspection was denied. Approved full Workflow QA runs with the needed process
  inspection capability, not with skipped tests.
- Capture-state CLI initially rejected an over-specific root; the documented nearest-owner
  project-state/ai-system root was used on retry, not a recursive scan of foreign runtimes.

## Publication

No commit, push, update-from-upstream or final-owner-yes is authorized. Product untracked files
are admitted explicitly in isolated smoke fixtures, not staged solely to make tests see them.
This inventory is preparation evidence, not commit permission.

