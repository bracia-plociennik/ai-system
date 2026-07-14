# Scripts

Validation scripts for AI System live here.

`init-ai-system` generates the ignored root `AGENTS.md` from `.systems/ai/templates/root/AGENTS.template.md`.

`init-workspace` creates or completes a selected private workspace from workspace templates.

`update-workspace` backfills missing neutral schema files in existing workspaces without overwriting runtime data.

`lib-workspaces` contains shared workspace registry helpers for scripts that need to prune or protect private local runtime paths.

`check-contract-compliance` validates the AI System Contract Compliance and Knowledge Capture Gate policy, docs, templates, and validator wiring.

`check-validation-profiles` validates the `fast`, `scoped`, `standard`, and `full` validation-profile contract, explicit full CI/upstream validation, and boundaries around smoke tests and residual risk.

`check-end-of-task-capture` validates the chat-end End-of-Task Capture contract, trigger grammar, precedence rules, output template, routing docs, and unsafe automatic-capture wording.

`check-update-workspace` validates the workspace backfill script, update contract, docs, templates, and smoke coverage.

`check-project-state` validates repo-safe project-state contracts, templates, routing, script wiring, and optional workspace pollution scans.

`check-external-source-registry` validates provider-agnostic external source registry contracts, links templates, routing, docs, and optional workspace source records.

`check-external-export-import-workflow` validates the manual external export import workflow contract, dump templates, routing docs, source-reference requirements, checkpoint decision wording, and v1 external-effect bans.

`check-system-insights` validates System Insights templates, entry structure, privacy checks, and External Memory scope separation.

`check-personal-ops` validates the strict Properties + Raw Audit Index v3 contract: complete typed `properties`, raw/OCR audit boundaries, WIG linked/standalone closure rules, all-professional `6d/do` generation, private index policy, lazy sync, immutable one-time legacy snapshot boundaries, routing, docs, and smoke coverage.

`check-task-management` validates the TaskForge/TaskNotes task-management contract, templates, routing docs, safe write boundaries, app setup runbook, and smoke coverage.

`check-system-skills` validates active system skill contracts, context intake plans, legacy boundaries, offline resources, and generated Python runtime artifact exclusions.

`map-notion-check-ins` and `sync-personal-ops-check-ins` are retired V2 commands and always end with `STOP` without writing active indexes. `migrate-personal-ops-legacy-check-ins-v3` is the single owner-approved route that creates an immutable normalized legacy snapshot, validates it through V3 sync, and then archives retired `check-ins.*` index artifacts.

`sync-personal-ops-check-ins-v3` reports lazy sync status or regenerates only official `check-ins-v3.*` from complete native `index_contract: 3` properties plus a validated immutable legacy snapshot when present. It applies each row's `detailed-private` or `redacted` index policy; trends include native V3 rows only.

`propose-task-candidates` converts daily check-ins or Dream Reports into TaskForge TaskNote proposals. Under V3 `all-professional-do-v1`, every valid professional planned item becomes a `6d/do` candidate regardless of WIG or overload; WIG never creates a task. Eligible V3 items may create or extend one strongly matched TaskNote with the same owner approval that writes the V3 check-in; all other task writes require exact owner approval, `--write`, and a configured vault.

`check-dreaming-mode` validates the advisory-only Dreaming Mode contract, templates, docs, and optional workspace Dream Reports.

`check-naming` validates strict Markdown filenames while allowing canonical `SKILL.md` contracts and legacy/context source material.
