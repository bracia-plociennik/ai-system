# Client Prompting Router Template

## Purpose

`<workspace>/clients/<client>/prompting/README.md` indexes advisory client-level prompt composition artifacts.

These artifacts help frame collaboration with the client. They do not replace `context/client-brief.md`, client status, memory, decisions, tasks, contracts, current files, or owner approvals.

## Source Snapshot

| Source | Path Or Decision | Last Reviewed |
| --- | --- | --- |
| Client brief | `<path-or-none>` | `<YYYY-MM-DD>` |
| Client status | `<path-or-none>` | `<YYYY-MM-DD>` |
| Client memory | `<path-or-none>` | `<YYYY-MM-DD>` |
| Client decisions | `<path-or-none>` | `<YYYY-MM-DD>` |
| Owner decision | `<decision-id-or-none>` | `<YYYY-MM-DD>` |

## Artifact Index

### Roles

| Role Artifact | Scope | State | Refresh Trigger |
| --- | --- | --- | --- |
| `<roles/example-client-role.md>` | `<client|relationship|communication|review>` | `<draft|accepted|active|stale|superseded|rejected>` | `<trigger>` |

### Variables

| Variable Pack | Scope | State | Requires Owner Confirmation |
| --- | --- | --- | --- |
| `<variables/example-client-variables.md>` | `<client|relationship|communication>` | `<draft|accepted|active|stale|superseded|rejected>` | `<yes|no>` |

### Modules

| Prompt Module | Scope | State | Refresh Trigger |
| --- | --- | --- | --- |
| `<modules/example-module.md>` | `<scope>` | `<draft|accepted|active|stale|superseded|rejected>` | `<trigger>` |

## Generation Rules

- Generate from approved client brief, current client files, memory, decisions, contacts, links, and owner instructions.
- Mark source labels, confidence, assumption impact, and refresh triggers.
- Ask the owner before relying on values that affect scope, risk, acceptance, billing, production, security, legal, client commitments, or final approval.
- Treat stale artifacts as advisory only after refresh.

## Evidence Rule

When a client prompting artifact materially influences intake, planning, review, distillation, or checkpointing, list its path in the relevant evidence or source section.

## Current State

```text
state: <draft|accepted|active|stale|superseded|rejected>
blocking-reason: <none-or-reason>
next-refresh-trigger: <trigger>
```
