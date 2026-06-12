# System Insights Router

## Purpose

`AI_SYSTEM_WORKSPACE_HOME/system-insights/system-insights.md` is the router and index for anonymized System Insights.

Detailed entries live in `AI_SYSTEM_WORKSPACE_HOME/system-insights/insights/`.

Use this router only for date, topic, category, status, skill candidate, and route to the detailed insight entry. Do not store long insight content in this file.

System Insights are advisory. They do not override `AGENTS.md`, `.systems/ai/core/`, workspace status, memory, decisions, checkpoints, privacy rules, validation, stop conditions, owner approvals, or skills.

## Insight Index

| Date | Topic | Category | Status | Skill Candidate | Route |
| --- | --- | --- | --- | --- | --- |

## Rules

- Keep this file short. It is an index, not the insight body.
- Store detailed entries in `AI_SYSTEM_WORKSPACE_HOME/system-insights/insights/`.
- Use categories from `.systems/ai/core/system-insights.md`.
- Do not store raw client data, client names, repo-specific facts, project-specific details, secrets, credentials, or production identifiers.
- Do not store AI System product improvement proposals here; use External Memory for those.
- Promote accepted skill candidates through the normal skill creation/update process before treating them as skills.
