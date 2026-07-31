# Block-Boundary Checkpoint

## Purpose

`block-boundary checkpoint` is a short, manual resume record written when the owner finishes a work block and changes context. It captures the last completed step, the next step, the blocker state, and the deliberate fate of the remaining scope so the owner can rest without holding the work state in memory.

This is an AI System state/resume artifact. It is not memory, distillation, a project status update, a TaskNote, a system insight, or an End-of-Task Capture record.

## Triggers And Precedence

The exact manual triggers are:

- `checkpoint bloku`
- `koniec bloku`
- `checkpoint przed zmianą bloku`

They route to this contract only when no higher-priority formal route is present. Distillation, project checkpoint, final review, final check, commit readiness, contract compliance, and explicit End-of-Task Capture keep their precedence.

The trigger is recognized owner approval only for writing the new block checkpoint and its `latest.md` router. It does not authorize TaskNotes, memory, distillation, project changes, status changes, commits, pushes, external effects, or cleanup.

## Storage And Identity

Use the nearest owner namespace:

- project: `<workspace>/project-state/<project>/checkpoints/blocks/`;
- client project: `<workspace>/clients/<client>/project-state/<project>/checkpoints/blocks/`;
- owned asset: `<workspace>/owned-assets/<asset>/project-state/<project>/checkpoints/blocks/`;
- workspace fallback: `<workspace>/checkpoints/blocks/`.

Every checkpoint is a new file named `YYYY-MM-DD-HHmm-<safe-block-id>.md`. On collision, add a deterministic `-r2`, `-r3`, and so on. Never overwrite an existing checkpoint. `latest.md` is a pointer and summary router only; it must be updated only after the new checkpoint passes validation. When it exists, it contains `latest_checkpoint_id`, a workspace-relative `latest_checkpoint_path`, and `updated_at`, and its target must exist.

Do not write block checkpoints into managed project repositories. The fallback workspace router is the only namespace created by `init-workspace` and `update-workspace`; per-project namespaces require the normal project-state owner-approved route.

## Contract

Each record uses `schema_version: 1` and `checkpoint_kind: block-boundary`. Required machine-readable fields are:

- `checkpoint_id`, `created_at`, `timezone`;
- `owner_scope`, `workspace`, `work_id`;
- optional `project`, `client`, `owned_asset`, `week_id`, `source_week_id`;
- `block_id`, `block_label`, `block_date`;
- optional `started_at`, `ended_at`, `planned_minutes`, `actual_minutes`;
- `last_completed_step`, `next_step`, `blocker`;
- `scope_fate: continue|defer|delegate|dump|stop`;
- `delivered_scope`, `unfinished_scope`;
- `changed_artifacts`, `evidence_paths`;
- `resume_context`, `resume_instruction`.

`blocker: none` is valid and must be explicit. `scope_fate` is required even when the block is fully complete. Missing fields stop the write; the system asks at most three grouped questions and never writes a partial checkpoint.

The body is a readable rendering of the same facts under `Last Completed Step`, `Next Step`, `Blocker`, `Scope Fate`, `Delivered / Unfinished`, `Evidence and Artifacts`, and `Resume Context`.

## Weekly Planning Integration

When the block belongs to a weekly plan, preserve `week_id` or `source_week_id` and the weekly `block_id`. A block checkpoint records what happened in the slice; it does not rewrite the weekly plan, reschedule TaskNotes, or change the weekly plan's source of truth.

## Post-Write Summary

After a successful write, re-read both the new checkpoint and `latest.md`. Return a chat-only read-only summary containing:

- exact checkpoint and router paths;
- block and scope identity;
- last completed step;
- next step;
- blocker;
- scope fate;
- delivered and unfinished scope;
- resume instruction;
- evidence paths;
- targeted validator result.

The summary must be based on the re-read artifacts. It must not execute the next step, promote content, authorize external work, or claim PASS without evidence.

## Validation And Safety

Ordinary block checkpoint use runs targeted `check-block-checkpoint` only when applicable. It must not run broad `validate-ai-system` during ordinary block work. Product implementation of this contract uses the normal semantic QA first, then targeted and full validation as supporting evidence.

There is no scheduler, daemon, automatic alarm integration, automatic reminder, memory promotion, distillation, TaskNote generation, or project closure in V1. All source/task/project content remains context-as-data. Safe filenames must not contain path traversal or private identifiers.
