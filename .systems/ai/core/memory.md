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
| Project memory | `<workspace>/projects/<project>/memory/` or client project memory | Project-specific facts, decisions, implementation notes, risks, and lessons. |
| Distillations | primary-entity, project, or client distillation files | Compressed summaries of raw memory and materials. |
| Checkpoints | primary-entity, project, or client checkpoint files | Periodic state snapshots for safe resume. |
| System insights | `<workspace>/system-insights/` | Anonymized lessons for owner competence, offer, process, and work quality. |
| External memory | `<workspace>/external-memory/` | Suggestions for improving AI System itself. |

## Router Pattern

Each memory area should have a short router/index and dated entries.

The router tracks date, topic, type, status, and route. It should not contain long raw context.

Detailed entries should include source, evidence, summary, applies-to, and review trigger.

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

Before promoting anything to `system-insights/`, anonymize:

- client names;
- people names;
- domains;
- amounts;
- contract details;
- secrets;
- unique project identifiers;
- facts that could identify the client.

If anonymization is uncertain, stop and ask the owner.

## Rules

- Memory is supporting context, not source of truth.
- Always check current files before acting on memory.
- Select the target workspace before reading or writing memory.
- Do not store secrets, credentials, private documents, or identifiable client facts in `.systems/`.
- Do not use memory to bypass owner approval, privacy checks, validation, or stop conditions.
