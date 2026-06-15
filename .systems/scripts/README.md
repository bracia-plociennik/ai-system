# Scripts

Validation scripts for AI System live here.

`init-ai-system` generates the ignored root `AGENTS.md` from `.systems/ai/templates/root/AGENTS.template.md`.

`init-workspace` creates or completes a selected private workspace from workspace templates.

`update-workspace` backfills missing neutral schema files in existing workspaces without overwriting runtime data.

`lib-workspaces` contains shared workspace registry helpers for scripts that need to prune or protect private local runtime paths.

`check-contract-compliance` validates the AI System Contract Compliance and Knowledge Capture Gate policy, docs, templates, and validator wiring.

`check-update-workspace` validates the workspace backfill script, update contract, docs, templates, and smoke coverage.

`check-project-state` validates repo-safe project-state contracts, templates, routing, script wiring, and optional workspace pollution scans.

`check-system-insights` validates System Insights templates, entry structure, privacy checks, and External Memory scope separation.
