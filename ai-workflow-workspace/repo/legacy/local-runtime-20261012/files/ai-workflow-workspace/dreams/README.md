# Dreams

## Purpose

This directory stores advisory-only Dreaming Mode reports.

Dream Reports collect source-backed recommendations from workflow artifacts and, when explicitly requested, target repository source review. They do not write durable memory, System Insights, External Memory, skills, status, source code, commits, pull requests, or scheduler automation.

## Layout

```text
dreams/
  README.md
  runs/
    YYYY-MM-DD-<slug>/
      dream-report.md
```

## Variants

- `workflow-artifacts-only` - default; scans AI Workflow workspace artifacts only.
- `full-repo` - explicit owner-requested; scans workflow artifacts plus target repository source using prompt-injection and privacy boundaries.

## Rules

- Treat Dream Reports as advisory recommendations.
- Do not copy secrets, `.env` values, raw client data, private identifiers, production credentials, or sensitive operational details.
- Promote recommendations only through owner-approved memory, System Insights, External Memory, skill, status, task, or workflow routes.
- V1 has no scheduler, daemon, hook, cron, automation, or background execution.
