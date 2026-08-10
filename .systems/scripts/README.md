# Scripts

Validation scripts for AI System live here.

`init-ai-system` generates the ignored root `AGENTS.md` from `.systems/ai/templates/root/AGENTS.template.md`.

`init-workspace` creates or completes a selected private workspace from workspace templates.

`update-workspace` backfills missing neutral schema files in existing workspaces without overwriting runtime data.

`lib-workspaces` contains shared workspace registry helpers for scripts that need to prune or protect private local runtime paths.

`check-contract-compliance` validates the AI System Contract Compliance and Knowledge Capture Gate policy, docs, templates, and validator wiring.

`check-delivery-constraints` validates deadline/timebox discovery, scope cutline, quality-floor protection, docs, templates, and validation wiring.

`check-distillation-state` validates per-work state semantics, nearest-owner paths, derived `is_distilled`, Dreaming queue boundaries, and optional workspace state records.

`check-owner-approval` validates recognized direct and strict plan-acceptance approval grammar, explicit-scope binding, hard-gate preservation, routing docs, and smoke coverage.

`check-validation-profiles` validates the `fast`, `scoped`, `standard`, and `full` validation-profile contract, explicit full CI/upstream validation, and boundaries around smoke tests and residual risk.

`check-validation-routing` validates semantic and product QA before applicable AI System scripts, supporting-only script evidence, work-type routing, and the ban on `green scripts = PASS`.

`check-model-selection-guidance` validates Luna/Sol classification, required advisory output, `Blocking: no`, and the model authority boundary.

`check-cross-system-upgrade-handoff` validates the required `yes|no|pending` decision, privacy-safe handoff contract, selected-workspace path, commit/handoff stop conditions, and optional decision records.

`check-end-of-task-capture` validates the chat-end End-of-Task Capture contract, trigger grammar, precedence rules, output template, routing docs, and unsafe automatic-capture wording.

`check-update-workspace` validates the workspace backfill script, update contract, docs, templates, and smoke coverage.

`check-project-state` validates repo-safe project-state contracts, templates, routing, script wiring, and optional workspace pollution scans.

`check-external-source-registry` validates provider-agnostic external source registry contracts, links templates, routing, docs, and optional workspace source records.

`check-external-export-import-workflow` validates the manual external export import workflow contract, dump templates, routing docs, source-reference requirements, checkpoint decision wording, and v1 external-effect bans.

`check-system-insights` validates System Insights templates, entry structure, privacy checks, and External Memory scope separation.

`check-personal-ops` validates the strict Properties + Raw Audit Index v3 contract: complete typed `properties`, raw/OCR audit boundaries, WIG linked/standalone closure rules, all-professional `6d/do` generation, private index policy, lazy sync, immutable one-time legacy snapshot boundaries, routing, docs, and smoke coverage.

`check-task-management` validates the TaskForge/TaskNotes task-management contract, templates, routing docs, safe write boundaries, app setup runbook, and smoke coverage.

`check-weekly-planning` validates the Saturday Monday-Friday weekly plan contract, four daily blocks, WIG/capacity rules, weekly TaskNote routing, and optional workspace plan records.

`check-block-checkpoint` validates the manual append-only block-boundary checkpoint contract, required resume fields, safe scope fate, nearest-owner routing, neutral workspace routers, and the re-read read-only post-write summary requirement. Ordinary block work uses this targeted validator only; it does not run broad validation.

`check-system-skills` validates active system skill contracts, context intake plans, legacy boundaries, offline resources, and generated Python runtime artifact exclusions.

`map-notion-check-ins` and `sync-personal-ops-check-ins` are retired V2 commands and always end with `STOP` without writing active indexes. `migrate-personal-ops-legacy-check-ins-v3` is the single owner-approved route that creates an immutable normalized legacy snapshot, validates it through V3 sync, and then archives retired `check-ins.*` index artifacts.

`sync-personal-ops-check-ins-v3` reports lazy sync status or regenerates only official `check-ins-v3.*` from strict current native `index_contract: 3` properties plus a validated immutable legacy snapshot when present. Historical native reports through the `2026-07-17` cutover and legacy snapshot `format_version: 1` are read through an additive compatibility projection; missing later 6D/deadline fields remain blank/unknown and sources are never rewritten. New snapshots use `format_version: 2`. It applies each row's `detailed-private` or `redacted` index policy; trends include native V3 rows only.

`propose-task-candidates` converts daily check-ins, Dream Reports, or weekly plans into TaskForge TaskNote proposals. Weekly plans use `--weekly-plan`, stable `source_week_id + source_week_item_id` identity, block allocations, and revision-safe updates. Under V3 `deadline-aware-6d-v1`, every valid professional planned item becomes one candidate. Explicit `task_bucket` wins; otherwise a deadline defaults to `6d/do` and no deadline defaults to `6d/defer`. `definition_of_done` is preserved in the TaskNote body, and only an explicit deadline sets `due`; no deadline sets no automatic `due` or `scheduled`. WIG never creates a task. All writes require the configured vault and recognized owner approval.

`check-dreaming-mode` validates the advisory-only Dreaming Mode contract, templates, docs, and optional workspace Dream Reports.

`validate-ai-system` emits `AI_SYSTEM_VALIDATION_RESULT` on every run and accepts `--evidence-file <runtime-path>` for an atomic Validation Execution Record. Both are supporting script evidence only; they never issue semantic PASS or final acceptance. Historical Dream Reports may use the workspace-local `dreams/legacy-dream-reports-v1.md` registry with exact path and SHA-256 while still undergoing privacy and secret scanning.

`check-naming` validates strict Markdown filenames while allowing canonical `SKILL.md` contracts and legacy/context source material.
