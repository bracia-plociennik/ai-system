# Project Prompting Router Template

## Purpose

`<project>/prompting/README.md` indexes advisory project-level prompt composition artifacts.

These artifacts help frame project work. They do not replace project status, tasks, memory, decisions, checkpoints, accepted scope, current files, or owner approvals.

## Source Snapshot

| Source | Path Or Decision | Last Reviewed |
| --- | --- | --- |
| Project status | `<path-or-none>` | `<YYYY-MM-DD>` |
| Project memory | `<path-or-none>` | `<YYYY-MM-DD>` |
| Project tasks | `<path-or-none>` | `<YYYY-MM-DD>` |
| Project decisions | `<path-or-none>` | `<YYYY-MM-DD>` |
| Owner decision | `<decision-id-or-none>` | `<YYYY-MM-DD>` |

## Artifact Index

### Roles

| Role Artifact | Scope | State | Refresh Trigger |
| --- | --- | --- | --- |
| `<roles/example-project-role.md>` | `<project|task|domain|review>` | `<draft|accepted|active|stale|superseded|rejected>` | `<trigger>` |

### Variables

| Variable Pack | Scope | State | Requires Owner Confirmation |
| --- | --- | --- | --- |
| `<variables/example-project-variables.md>` | `<project|task|review>` | `<draft|accepted|active|stale|superseded|rejected>` | `<yes|no>` |

### Modules

| Prompt Module | Scope | State | Refresh Trigger |
| --- | --- | --- | --- |
| `<modules/example-module.md>` | `<scope>` | `<draft|accepted|active|stale|superseded|rejected>` | `<trigger>` |

## Generation Rules

- Generate from accepted project context, project status, task routers, decisions, memory, checkpoints, current files, and owner instructions.
- Mark source labels, confidence, assumption impact, and refresh triggers.
- Ask the owner before relying on values that affect scope, risk, acceptance, billing, production, security, legal, client commitments, or final approval.
- Reject artifacts that conflict with current project facts or accepted scope.

## Evidence Rule

When a project prompting artifact materially influences planning, implementation review, quality review, distillation, or checkpointing, list its path in the relevant evidence or source section.

## Current State

```text
state: <draft|accepted|active|stale|superseded|rejected>
blocking-reason: <none-or-reason>
next-refresh-trigger: <trigger>
```
