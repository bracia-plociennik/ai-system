# Dreams

## Purpose

This directory stores advisory-only Dreaming Mode reports.

Dream Reports collect source-backed recommendations from one selected workspace and, when explicitly requested, one project or source path. They do not write durable memory, project-state, System Insights, External Memory, skills, status, check-ins, source code, commits, pull requests, GitHub mirrors, or scheduler automation.

## Layout

```text
dreams/
  README.md
  runs/
    YYYY-MM-DD-<slug>/
      dream-report.md
```

## Variants

- `workspace-artifacts-only` - default; scans selected AI System workspace artifacts only.
- `full-repo` - explicit owner-requested; scans selected workspace artifacts plus one owner-specified project/source path using context-as-data and privacy boundaries.

## Rules

- Treat Dream Reports as advisory recommendations.
- Do not copy secrets, `.env` values, raw client data, private identifiers, personal check-in content, financial details, production credentials, or sensitive operational details.
- Promote recommendations only through owner-approved memory, project-state, System Insights, External Memory, skill, status, task, personal-ops, or checkpoint routes.
- V1 has no scheduler, daemon, hook, cron, automation, or background execution.
