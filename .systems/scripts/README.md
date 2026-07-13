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

`check-personal-ops` validates V2/V3 daily check-in contracts, manual V3 intake, private-sensitive indexes, lazy sync, templates, mapper compatibility, routing, docs, and smoke coverage.

`check-task-management` validates the TaskForge/TaskNotes task-management contract, templates, routing docs, safe write boundaries, app setup runbook, and smoke coverage.

`check-system-skills` validates active system skill contracts, context intake plans, legacy boundaries, offline resources, and generated Python runtime artifact exclusions.

`map-notion-check-ins` maps an owner-approved Notion daily check-in CSV export into canonical Markdown files and derived CSV/JSONL/metrics indexes.

`sync-personal-ops-check-ins` reports lazy sync status or regenerates V2/V3 Personal Ops derived indexes plus sanitized `check-ins.trends.md` from canonical Markdown after exact owner approval.

`propose-task-candidates` converts daily check-ins or Dream Reports into TaskForge TaskNote proposals. V3 planned items may create or extend one strongly matched TaskNote with the same owner approval that writes the V3 check-in; all other task writes require exact owner approval, `--write`, and a configured vault.

`check-dreaming-mode` validates the advisory-only Dreaming Mode contract, templates, docs, and optional workspace Dream Reports.

`check-naming` validates strict Markdown filenames while allowing canonical `SKILL.md` contracts and legacy/context source material.
