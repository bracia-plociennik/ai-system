# Workspace Prompting Router Template

## Purpose

`<workspace>/prompting/README.md` indexes advisory workspace-level prompt composition artifacts.

These artifacts help frame broad workspace or primary-entity work. They do not replace workspace registry, workspace status, primary-entity status, memory, client artifacts, project artifacts, current files, or owner approvals.

## Source Snapshot

| Source | Path Or Decision | Last Reviewed |
| --- | --- | --- |
| Workspace registry | `<path-or-none>` | `<YYYY-MM-DD>` |
| Workspace status | `<path-or-none>` | `<YYYY-MM-DD>` |
| Primary-entity status | `<path-or-none>` | `<YYYY-MM-DD>` |
| Workspace memory | `<path-or-none>` | `<YYYY-MM-DD>` |
| Owner decision | `<decision-id-or-none>` | `<YYYY-MM-DD>` |

## Artifact Index

### Roles

| Role Artifact | Scope | State | Refresh Trigger |
| --- | --- | --- | --- |
| `<roles/example-workspace-role.md>` | `<workspace|primary-entity|operation>` | `<draft|accepted|active|stale|superseded|rejected>` | `<trigger>` |

### Variables

| Variable Pack | Scope | State | Requires Owner Confirmation |
| --- | --- | --- | --- |
| `<variables/example-workspace-variables.md>` | `<workspace|primary-entity|operation>` | `<draft|accepted|active|stale|superseded|rejected>` | `<yes|no>` |

### Modules

| Prompt Module | Scope | State | Refresh Trigger |
| --- | --- | --- | --- |
| `<modules/example-module.md>` | `<scope>` | `<draft|accepted|active|stale|superseded|rejected>` | `<trigger>` |

## Rules

- Keep client facts in client-local artifacts.
- Keep project facts in project-local artifacts.
- Use workspace prompting only for broad operating style, primary-entity framing, or AI System operation support.
- List material use of prompting artifacts in evidence or source sections.

## Current State

```text
state: <draft|accepted|active|stale|superseded|rejected>
blocking-reason: <none-or-reason>
next-refresh-trigger: <trigger>
```
