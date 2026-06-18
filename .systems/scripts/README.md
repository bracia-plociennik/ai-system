# Scripts

Validation scripts for AI System live here.

`init-ai-system` generates the ignored root `AGENTS.md` from `.systems/ai/templates/root/AGENTS.template.md`.

`init-workspace` creates or completes a selected private workspace from workspace templates.

`update-workspace` backfills missing neutral schema files in existing workspaces without overwriting runtime data.

`lib-workspaces` contains shared workspace registry helpers for scripts that need to prune or protect private local runtime paths.

`check-contract-compliance` validates the AI System Contract Compliance and Knowledge Capture Gate policy, docs, templates, and validator wiring.

`check-update-workspace` validates the workspace backfill script, update contract, docs, templates, and smoke coverage.

`check-project-state` validates repo-safe project-state contracts, templates, routing, script wiring, and optional workspace pollution scans.

`check-external-source-registry` validates provider-agnostic external source registry contracts, links templates, routing, docs, and optional workspace source records.

`check-system-insights` validates System Insights templates, entry structure, privacy checks, and External Memory scope separation.

`check-personal-ops` validates the daily check-in schema mapping contract, manual intake profile, templates, mapper script, routing, docs, and smoke coverage.

`check-system-skills` validates active system skill contracts, context intake plans, legacy boundaries, offline resources, and generated Python runtime artifact exclusions.

`map-notion-check-ins` maps an owner-approved Notion daily check-in CSV export into canonical Markdown files and derived CSV/JSONL/metrics indexes.

`check-naming` validates strict Markdown filenames while allowing canonical `SKILL.md` contracts and legacy/context source material.
