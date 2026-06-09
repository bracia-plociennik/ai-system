# Memory Model

## Purpose

Memory turns local work into durable context without replacing current filesystem review.

Memory helps the owner resume work, preserve decisions, detect stale assumptions, and distill reusable lessons.

## Levels

| Level | Location | Use |
| --- | --- | --- |
| Workspace memory | `ai-system-workspace/memory/` | Broad operating preferences, recurring patterns, and workspace-level decisions. |
| Client memory | `ai-system-workspace/clients/<client>/memory/` | Raw client-specific facts, history, constraints, and relationship context. |
| Project memory | `ai-system-workspace/projects/<project>/memory/` or client project memory | Project-specific facts, decisions, implementation notes, risks, and lessons. |
| Distillations | project/client distillation files | Compressed summaries of raw memory and materials. |
| Checkpoints | project/client checkpoint files | Periodic state snapshots for safe resume. |
| System insights | `ai-system-workspace/system-insights/` | Anonymized lessons for owner competence, offer, process, and work quality. |
| External memory | `ai-system-workspace/external-memory/` | Suggestions for improving AI System itself. |

## Router Pattern

Each memory area should have a short router/index and dated entries.

The router tracks date, topic, type, status, and route. It should not contain long raw context.

Detailed entries should include source, evidence, summary, applies-to, and review trigger.

## Distillation Reminders

AI should remind the owner to distill memory when:

- a client or project accumulates many new notes or files;
- a project phase ends;
- a recurring pattern appears;
- a checkpoint is stale;
- raw memory is too large to scan efficiently;
- memory conflicts with current files or status.

## Checkpoints

Use checkpoints before long pauses, after major decisions, after substantial file triage, and before final closure.

A checkpoint should record:

- current status;
- active client/project;
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
- Do not store secrets, credentials, private documents, or identifiable client facts in `.systems/`.
- Do not use memory to bypass owner approval, privacy checks, validation, or stop conditions.
