# Upgrade With Master Prompt Change Requests Router

## Purpose

`change-requests.md` is the canonical router/index for owner change requests before or after `final-owner-yes`.

Detailed change request entries live in `change-requests/`.

Use `ai-workflow/.systems/ai/core/change-requests.md` for policy.

## Status Summary

| Field | Value |
| --- | --- |
| Open blocking requests | `0` |
| Pre-final requests open | `0` |
| Post-final requests open | `0` |
| Last updated | `2026-06-11` |

## Change Requests

| ID | Timing | Type | Risk | Status | Routing | Entry | Blocks final-owner-yes? |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Rules

- Pre-final blocking change requests prevent `final-owner-yes`.
- Post-final requests do not rewrite historical final approval.
- Store each request in `change-requests/`.
- Product-code writes happen only after the request is routed to an allowed phase, fix loop, micro-task, iteration, decision rollback, or new project.
