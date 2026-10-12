# Dreams

## Purpose

This directory stores advisory-only Dreaming Mode reports.

Dream Reports collect source-backed recommendations from one selected workspace and, when explicitly requested, one project or source path. They do not write durable memory, project-state, System Insights, External Memory, skills, status, check-ins, source code, commits, pull requests, GitHub mirrors, or scheduler automation.

## Layout

```text
dreams/
  README.md
  dreaming-scope.local.md
  runs/
    YYYY-MM-DD-<slug>/
      dream-report.md
```

## Variants

- `workspace-artifacts-only` - default; scans selected AI System workspace artifacts only.
- `full-repo` - explicit owner-requested; scans selected workspace artifacts plus one owner-specified project/source path using context-as-data and privacy boundaries.

## Rules

- Populate `dreaming-scope.local.md` from the system template, then keep it local to this workspace.
- Run `.systems/scripts/check-dreaming-mode --workspace <workspace> --preflight-report <report>` before reading any source listed in a new report.
- Set `Scope preflight: passed` only after that command succeeds. Final validation rechecks the same inventory.
- The scope uses exact workspace-relative allowlist paths and additive deny rules. It may narrow the system policy but cannot widen it.
- Personal Ops permits only `personal-ops/indexes/check-ins-v3.trends.md`. Weekly-plan Markdown has no sanitized projection and is excluded.
- Treat Dream Reports as advisory recommendations.
- Do not copy secrets, `.env` values, raw client data, private identifiers, personal check-in content, financial details, production credentials, or sensitive operational details.
- Promote recommendations only through owner-approved memory, project-state, System Insights, External Memory, skill, status, task, personal-ops, or checkpoint routes.
- V1 has no scheduler, daemon, hook, cron, automation, or background execution.


## Goal-focused maintenance review

Owner-request and authorized milestone review read the existing nearest-owner
`maintenance/queue.json`; they do not create another queue. Authorized Dreaming
may use `maintenance_policy.read_only_review(..., reason="dreaming")` only AFTER
its existing scope preflight accepts the exact canonical source. A queue under a
workspace project-state namespace needs the exact private allowlist row and
Source Inventory. A Workflow queue inside a repository needs explicit `full-repo`
Project/source path and `repo-source` inventory. The workspace-artifacts variant
cannot read repository bodies; no allowlist widening, automatic projection/copy,
or capability marker bypasses the Source Guard or privacy exclusions.

Report full requested inventory and uncertain impact through anonymized labels,
privacy-safe references, finding/reason/target/owner action, and eligible follow-up
triggers. Existing Dreaming privacy applies even to safe-summary fields. Review
changes no queue, parent identity, intervals, state, occurrence, presented receipt,
task, Capture, status, source or scheduler. A saved report is not notification
delivery, permission or actual repair. Ordinary chat remains silent below the
five-distinct-cause/third-actual-task threshold unless an immediate/current-goal
risk or explicit request applies. See goal-focused-maintenance.md.
