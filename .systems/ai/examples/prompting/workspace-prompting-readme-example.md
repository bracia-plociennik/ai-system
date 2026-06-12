# Example Workspace Prompting Router

## Purpose

This fictional router shows how a workspace-level prompting index may look.

It is advisory only and does not replace workspace status, memory, decisions, client artifacts, project artifacts, current files, or owner approvals.

## Artifact Index

### Roles

| Role Artifact | Scope | State | Refresh Trigger |
| --- | --- | --- | --- |
| `roles/example-workspace-reviewer.md` | `workspace` | `draft` | workspace status changes |

### Variables

| Variable Pack | Scope | State | Requires Owner Confirmation |
| --- | --- | --- | --- |
| `variables/example-workspace-variables.md` | `workspace` | `draft` | yes |

### Modules

| Prompt Module | Scope | State | Refresh Trigger |
| --- | --- | --- | --- |
| `modules/example-source-labeling.md` | `review` | `draft` | source policy changes |
