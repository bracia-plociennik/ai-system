# Memory Model

## Purpose

Memory turns local work into durable context without replacing current filesystem review.

Memory helps the owner resume work, preserve decisions, detect stale assumptions, and distill reusable lessons.

## Levels

| Level | Location | Use |
| --- | --- | --- |
| Workspace memory | `<workspace>/memory/` | Broad operating preferences, recurring patterns, and workspace-level decisions. |
| Primary-entity memory | `<workspace>/memory.md` and `<workspace>/memory/` | Raw primary company, brand, or owner-controlled entity facts, decisions, constraints, and reusable context when the entity lives at the workspace root. |
| Client memory | `<workspace>/clients/<client>/memory/` | Raw client-specific facts, history, constraints, and relationship context. |
| Owned-asset memory | `<workspace>/owned-assets/<asset>/memory/` | Raw owner-controlled asset facts, decisions, constraints, and business or brand context in a generic workspace or explicit sub-asset namespace. |
| Project memory | `<workspace>/project-state/<project>/memory/` or nearest client/owned-asset `project-state/<project>/memory/` | Project-specific facts, decisions, implementation notes, risks, and lessons. |
| Distillations | primary-entity, project, or client distillation files | Compressed summaries of raw memory and materials. |
| Checkpoints | primary-entity, project, or client checkpoint files | Periodic state snapshots for safe resume. |
| System insights | `<workspace>/system-insights/system-insights.md` and `<workspace>/system-insights/insights/` | Anonymized operating lessons and skill candidates for owner competence, offer, process, and work quality. |
| Prompting artifacts | workspace, client, owned-asset, or project `prompting/` directories | Advisory role, variable, module, and collaboration framing. Not durable fact storage. |
| External memory | `<workspace>/external-memory/` | Suggestions for improving AI System itself. |
| Dream Reports | `<workspace>/dreams/runs/**/dream-report.md` | Advisory recommendation queues. Not durable fact storage. |

## Router Pattern

Each memory area should have a short router/index and dated entries.

The router tracks date, topic, type, status, and route. It should not contain long raw context.

Detailed entries should include source, evidence, summary, applies-to, and review trigger.

## Knowledge Capture Gate

Before `AI_SYSTEM_WORK_CLOSURE`, use `.systems/ai/core/contract-compliance.md` to decide whether `Knowledge capture` is required.

The gate must explicitly choose one of:

- `status/evidence`;
- `workspace-memory`;
- `primary-entity-memory`;
- `client-memory`;
- `owned-asset-memory`;
- `project-memory`;
- `distillation`;
- `checkpoint`;
- `external-memory`;
- `system-insights`;
- `not-applicable`.

This is a routing decision, not write permission. Durable writes still require the correct selected workspace target, privacy-safe content, and exact `owner-approved` scope unless an existing checkpoint or final-check route authorizes that exact capture.

Use `not-applicable` when no status, decision, evidence, reusable lesson, or durable context changed, or when the current artifact already captured the same fact.

For project memory, status, distillations, decisions, and checkpoints, use `.systems/ai/core/project-state.md`. Do not write AI System runtime files into a project git worktree unless the owner explicitly chooses colocated local-only state.

## Distillation Reminders

AI should remind the owner to distill memory when:

- a primary entity, client, owned asset, or project accumulates many new notes or files;
- a project phase ends;
- a recurring pattern appears;
- a checkpoint is stale;
- raw memory is too large to scan efficiently;
- memory conflicts with current files or status.

## Checkpoints

Use checkpoints before long pauses, after major decisions, after substantial file triage, and before final closure.

A checkpoint should record:

- current status;
- active primary entity, client, owned asset, or project;
- recent decisions;
- open blockers;
- next safe action;
- evidence or files reviewed.

## System Insights Promotion

Raw client and project memory may contain identifying details.

Before promoting anything to `system-insights/`, use `.systems/ai/core/system-insights.md` and anonymize:

- client names;
- people names;
- domains;
- amounts;
- contract details;
- secrets;
- unique project identifiers;
- facts that could identify the client.

If anonymization is uncertain, stop and ask the owner.

Durable System Insights writes require exact `owner-approved` capture or checkpoint routing. Store long insight content as dated entries under `<workspace>/system-insights/insights/` and keep `<workspace>/system-insights/system-insights.md` as a short router/index.

## Dream Reports

Dream Reports are not memory entries, checkpoints, distillations, status updates, System Insights, External Memory, skills, personal-ops records, or task artifacts.

Use `.systems/ai/core/dreaming-mode.md` for Dreaming Mode. Findings from a Dream Report can become memory only through a later exact owner-approved capture or checkpoint/final-check route.

## Rules

- Memory is supporting context, not source of truth.
- Always check current files before acting on memory.
- Select the target workspace before reading or writing memory.
- Do not store secrets, credentials, private documents, or identifiable client facts in `.systems/`.
- Do not use memory to bypass owner approval, privacy checks, validation, or stop conditions.
- Do not treat prompting artifacts as memory. If a prompt artifact contains durable facts, move those facts into the correct memory or decision artifact only after owner-approved write scope.
