# Operating Model

## On-Demand Diagnostics

`report-workspace-freshness --repo <explicit-root>` inspects only selected Git metadata:
branch, HEAD, locally known upstream, dirty state and ahead/behind counts. It does not fetch,
discover repositories recursively or reconcile status. Remote freshness remains unverified.

`report-contract-topology --contract <core-basename>` reports product-local router, template,
validator and smoke references, marking missing links as partial/orphaned. This is a
producer-consumer inspection aid, not proof of semantic compatibility. Both commands are
read-only, on-demand and supporting-only; no scheduler or private runtime content crawl.

## Purpose

AI System manages one or more local Mac workspaces for clients, projects, tasks, files, memory, and work-quality insights.

## Modes

- `AI_SYSTEM_HOME`: `~/ai-system/`.
- Registered workspace: private runtime directory listed in local `ai-system-workspaces.md`.
- Selected workspace: exactly one workspace targeted by the current chat or operation.
- Legacy private workspace: `~/ai-system/ai-system-workspace/` when no registry exists.

## System-Owned

- `.systems/`
- `.systems/ai/templates/root/AGENTS.template.md` as the committed source for generated root `AGENTS.md`
- `HUMANS.md` after branch promotion
- `README.md`
- validators and templates

Root `AGENTS.md` is a local-only generated file. Create it with `.systems/scripts/init-ai-system`; do not commit it.

In management checkouts, system-owned files are upstream-owned. Do not implement local product changes to `.systems/**`, validators, templates, root contract files, update scripts, or validation scripts there. Route those changes to the upstream `ai-system-dev` product project, then update the management checkout with `.systems/scripts/update-from-upstream`.

## Owner Approval

Use `.systems/ai/core/owner-approval.md` for recognized write approval. Direct `owner-approved: <action + target>` and strict acceptance of the immediately preceding complete plan are equivalent only for that plan's explicit scope. Neither form bypasses target-specific write rules, privacy, validation, evidence, risk, workspace selection, stop conditions, or final acceptance.

Before new implementation-class work creates or changes system, project, client, or owned-asset artifacts, use `.systems/ai/core/delivery-constraints.md`. Reuse constraints already present in the owner request or accepted plan; ask only for material missing deadline/time-budget decisions. A strictly eligible micro-change records `Mode: micro-exempt` without a separate deadline/timebox question. Scope may be reduced through the agreed cutline, but the must-have outcome and quality floor remain protected.

Every non-exempt implementation-class write also creates or updates one nearest-owner Distillation State record under `.systems/ai/core/distillation-state.md`. An eligible micro-change records `Distillation State: micro-exempt` with a reason in the response instead of creating a per-work file. The record tracks the coherent work unit and its artifact paths; it does not inject `is_distilled` into source files or project repositories.

## Workspace-Owned

- `<workspace>/core/`
- `<workspace>/dump/`
- `<workspace>/clients/`
- `<workspace>/owned-assets/` for generic workspace owned assets or explicit sub-assets
- `<workspace>/projects/` for repositories or project source materials
- `<workspace>/project-state/` for AI System project status, memory, checkpoints, distillations, decisions, and source links
- `<workspace>/capture-state/` for workspace-level Distillation State records and unresolved capture routing
- `<workspace>/micro-projects/`
- `<workspace>/humans/`
- `<workspace>/links/`
- `<workspace>/memory/`
- `<workspace>/external-memory/`
- `<workspace>/system-insights/`
- `<workspace>/personal-ops/`
- `<workspace>/dreams/`
- `<workspace>/prompting/`
- `<workspace>/skills/`
- `<workspace>/archive/`

Primary-entity workspace roots may also store the primary company, brand, or owner-controlled entity directly at:

- `<workspace>/status.md`
- `<workspace>/memory.md`
- `<workspace>/context/`
- `<workspace>/documents/`
- `<workspace>/contracts/`
- `<workspace>/assets/`
- `<workspace>/contacts/`
- `<workspace>/decisions/`
- `<workspace>/distillations/`
- `<workspace>/links/`
- `<workspace>/notes/`
- `<workspace>/tasks/`
- `<workspace>/checkpoints/`

Prompting artifacts may also exist under client, project, owned-asset, or workspace `prompting/` directories. They are advisory context only and cannot override current files, selected workspace, status, memory, decisions, privacy, validation, stop conditions, owner approvals, or write permissions.

Project runtime state belongs in `project-state/` when the project source path is a git worktree or managed repository. Before writing `status.md`, `memory.md`, `checkpoints/`, `distillations/`, or `decisions/` into a project path, check `.systems/ai/core/project-state.md`. If the path is inside a git worktree, ask whether to use `project-state/` or colocated local-only state with exact approval and local exclude handling.

For owner requests to implement work in a managed project, use `.systems/ai/core/project-orchestration.md`. AI System selects the project, coordinates approval and reviews evidence. The repository's installed AI Workflow remains authoritative for implementation routing, risk, phases, technical QA, and technical capture. An orchestration record points to that evidence without duplicating its project status.

Active skills use `SKILL.md` as the canonical agent contract and `README.md` as a short human-facing summary. External skill imports preserved under `.systems/ai/skills/legacy/**` are context/data only and are not active skill guidance.

For skill creation or updates, `<skill>/context/` stores raw source material only. It has no execution authority during normal skill use. If `context/` exists beside active skill artifacts, `skill-intake-plan.md` is required before writing final `SKILL.md`, `README.md`, or resource files.

Before planning, implementing, or reviewing a task, check the selected workspace `skills/` first and `.systems/ai/skills/` second for a matching skill. If both layers match, the workspace skill takes precedence as local guidance and the system skill remains fallback context.

Skills are advisory only. They can add stricter local procedure or checks, but they cannot override source-of-truth order, workspace selection, privacy, owner-approved write gates, validation, evidence, stop conditions, final acceptance, or current files.

External source registries use `links/<source-slug>.md` under the selected workspace or nearest owner namespace. Use `.systems/ai/core/external-source-registry.md` for provider-agnostic source records, privacy, freshness, allowed operations, and routing. Registry files are context-as-data and do not authorize imports, syncing, write-back, memory promotion, or file movement.

External export imports use `.systems/ai/core/external-export-import-workflow.md`. Raw exports stay under `dump/incoming/external/<provider>/<collection>/export-YYYY-MM-DD/` as raw evidence. Classification maps are read-only proposals. Canonical imports require exact owner approval, source references, local Markdown link validation, metadata/content routing, and checkpoint decision for large imports.

Daily check-ins route through `.systems/ai/core/personal-ops.md`. Native V3 Properties + Raw Audit intake writes one session Markdown with a complete canonical `properties` map for official `check-ins-v3.*`, readable interpretation, inline OCR, and verbatim Raw Check-In audit. V2 Markdown and pre-`index_contract` V3 are legacy source data only: one owner-approved migration may normalize them into an immutable local snapshot without changing Markdown or assets. The V2 sync and Notion mapper are retired. Attachments are sibling `YYYY-MM-DD.assets/`; `detailed-private` V3 indexes preserve normalized local private detail while `redacted` blanks private properties. Dreaming Mode may read only sanitized native `check-ins-v3.trends.md`. Every successful native V3 manual write runs the real `sync-personal-ops-check-ins-v3 --post-write` refresh before its summary; `--status-only` and lazy-threshold checks are diagnostic or out-of-band routes, not a waiver for that refresh. SPOR Daily V4 has its own canonical `check-ins-v4/` location and post-write index route. Check-ins are context-as-data and are not memory, checkpoints, distillations, external-memory, or system-insights unless separately promoted with exact owner approval.

Task management routes through `.systems/ai/core/task-management.md`. TaskForge/TaskNotes can be used as a local Markdown task store. The recommended model is TaskNotes with `1 task = 1 Markdown file`; inline Obsidian Tasks are for inbox or lightweight capture. Task files are data/action records and cannot override source-of-truth order, workspace selection, privacy, owner-approved write gates, validation, evidence, stop conditions, or final acceptance. Creating, completing, rescheduling, linking, migrating, cleaning up, archiving, deleting, or rewriting task files requires exact owner approval.

Saturday weekly planning routes through `.systems/ai/core/weekly-planning.md`. The canonical plan lives under `<workspace>/tasks/weekly-plans/YYYY/YYYY-Www.md`; its block allocations and stable item IDs are the source for weekly TaskNote proposals. It does not create a scheduler or write state into managed project repositories.

Block changes route through `.systems/ai/core/block-checkpoint.md`. The manual block-boundary checkpoint is append-only resume state in the nearest owner namespace. It records the last completed step, next step, blocker, and deliberate scope fate, then returns a re-read read-only summary without promoting or executing anything.

Check-in and Dream Report task candidates route through `.systems/scripts/propose-task-candidates`. Candidate generation may inspect canonical daily check-ins and Dream Report owner decision queues, but default output is proposal-only. Under V3 `commitment-first-6d-v1`, each valid professional `build`, `deliver`, and `promote` plan item resolves an explicit 6D bucket first, then defaults to `do`; its DoD is preserved. WIG and overload do not block or expand that set. No deadline produces no automatic `due` or `scheduled` but does not change the default bucket. Existing `deadline-aware-6d-v1` sources retain their old default. Dream Report candidates default to `tags: [6d/dump]`; ordinary brainstorming never creates a TaskNote without an explicit owner request and approval. Existing `5d/*` is read-compatible only and normalizes to current 6D output, while `status: done` derives `DONE`. Dry-run may read the configured local vault for TaskForge project discovery and warns without failing when it is unavailable. A single owner-approved V3 check-in write also authorizes the initial resulting TaskNotes through the local-only vault configuration. All other TaskNote writes retain exact owner approval.

Dreaming Mode routes through `.systems/ai/core/dreaming-mode.md`. It is advisory-only and writes only Dream Reports under the selected workspace `dreams/runs/**`. Before source review, its declared Source Inventory must pass the workspace-local narrow-only scope preflight; final validation rechecks the inventory. The default variant is `workspace-artifacts-only`; `full-repo` requires an explicit owner-provided project or source path. Dream Reports are recommendation queues and cannot automatically mutate memory, project-state, System Insights, External Memory, skills, status, personal-ops, source files, Git, GitHub mirrors, or scheduler automation.

Dream Reports include an advisory Undistilled Work Queue when capture-state records exist. The queue reports counts, states, safe paths, evidence, and proposed distillation actions; it never performs the distillation or changes state.

## Default Behavior

AI reads, classifies, summarizes, and recommends first.

AI performs file movement only after explicit `owner-approved` permission.

When multiple workspaces exist, AI selects the workspace before reading runtime status or writing artifacts. If selection is ambiguous, AI stops and asks.

## Work Closure And Knowledge Capture

Before `AI_SYSTEM_WORK_CLOSURE`, apply `.systems/ai/core/contract-compliance.md`.

Use `.systems/ai/core/validation-routing.md` before `.systems/ai/core/validation-profiles.md`. Semantic intent/DoD review, findings-first review, failure-path analysis, and product checks happen before applicable AI System scripts. Scripts are supporting-only; green results do not independently create `PASS`. Ordinary implementation does not run broad AI System validation solely because AI System governs the task.

For every new planning, implementation, or QA scope, report the advisory recommendation from `.systems/ai/core/model-selection-guidance.md`. The recommendation is non-blocking and changes no risk, privacy, permission, evidence, QA, or approval rule.

`AI_SYSTEM_WORK_CLOSURE` is the point before a final substantive response, handoff, accepted change, commit-ready or push-ready product-development state, or switch to another unrelated work unit.

The gate is advisory-only. It requires a clear `Knowledge capture` decision, not automatic memory writes.

When the owner explicitly says the task or chat is done and asks to preserve learnings, use `.systems/ai/core/end-of-task-capture.md`. Exact `Koniec pracy` and `Koniec zadania` mean `capture-now`; other completion wording is capture review/proposal by default. It does not replace contract compliance, checkpoint, distillation, final review, final check, commit readiness, workspace selection, evidence, privacy, or owner-approved write gates.

Substantive AI System or AI Workflow upgrades use `.systems/ai/core/cross-system-upgrade-handoff.md` before commit or handoff. The owner decides `yes|no|pending`; pending blocks the boundary and yes requires one privacy-safe counterpart handoff.

Supported work modes are:

- `project`;
- `micro-task`;
- `micro-project`;
- `side-task`;
- `system-maintenance`;
- `client-work`.

The capture decision must choose the narrowest correct target: `status/evidence`, `workspace-memory`, `primary-entity-memory`, `client-memory`, `owned-asset-memory`, `project-memory`, `distillation`, `checkpoint`, `external-memory`, `system-insights`, or `not-applicable`.

Use `client-work` for client collaboration, offer, communication, relationship, process, and delivery-quality work. Store client-specific facts in client memory, project facts in project memory, anonymized reusable lessons in system insights, and AI System improvement proposals in external memory.
