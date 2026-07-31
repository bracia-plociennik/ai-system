# Block-Boundary Checkpoint

```yaml
schema_version: 1
checkpoint_kind: block-boundary
checkpoint_id: <YYYY-MM-DD-HHmm-safe-block-id>
created_at: <YYYY-MM-DD HH:MM>
timezone: <Europe/Warsaw>
owner_scope: <workspace|project|client|owned-asset>
workspace: <workspace-id>
work_id: <work-id>
project:
client:
owned_asset:
week_id:
source_week_id:
block_id: <build-future|adapt-build-deliver|deliver-financial-impact|adapt-promote-deliver|custom>
block_label: <block label>
block_date: <YYYY-MM-DD>
started_at:
ended_at:
planned_minutes:
actual_minutes:
last_completed_step: <required>
next_step: <required>
blocker: <none or required blocker>
scope_fate: <continue|defer|delegate|dump|stop>
delivered_scope: <what was completed>
unfinished_scope: <what remains>
changed_artifacts: []
evidence_paths: []
resume_context: <context needed to resume>
resume_instruction: <first safe action after the break>
```

## Last Completed Step

<same value as `last_completed_step`>

## Next Step

<same value as `next_step`>

## Blocker

<same value as `blocker`>

## Scope Fate

<same value as `scope_fate`>

## Delivered / Unfinished

### Delivered

<same value as `delivered_scope`>

### Unfinished

<same value as `unfinished_scope`>

## Evidence and Artifacts

- Changed artifacts: <paths or none>
- Evidence: <paths or none>

## Resume Context

<same value as `resume_context`>

### Resume Instruction

<same value as `resume_instruction`>
