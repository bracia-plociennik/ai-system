# 2026-06-23 - End-of-Task Capture For AI System

## Type

AI System improvement note

## Source

Owner-approved capture after implementing and pushing AI System End-of-Task Capture.

## Observation

AI System now has a dedicated End-of-Task Capture contract for chat-end prompts such as `to koniec zadania`, `koniec taska`, `dziękuję, utrwal wiedzę`, and `end task and capture knowledge`.

## Reusable Rule

End-of-Task Capture should default to capture review/proposal, not durable writes.

Durable capture requires:

- explicit owner-approved target;
- selected workspace;
- clear scope;
- privacy/scope check;
- evidence;
- write permission;
- no conflict with checkpoint, distillation, final review, final check, commit readiness, contract compliance, or other higher-precedence routes.

## Safety Boundary

End-of-Task Capture must not automatically mark PASS, run final check, close projects, update status from chat-only claims, or write memory, checkpoints, system-insights, external-memory, task files, commits, or pushes.

## Future Use

Use this as a reference pattern for future chat-end capture workflows: create proposal-first routing, required output fields, precedence rules, validator coverage, and unsafe wording smoke tests before allowing durable writes.
