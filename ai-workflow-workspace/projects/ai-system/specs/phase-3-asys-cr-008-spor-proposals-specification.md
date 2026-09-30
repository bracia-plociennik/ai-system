# SPOR Proposals Specification

## Source And Definition Of Done

Source: owner-approved Propozycje SPOR I Scheduler plan and complete owner Daily/Weekly SPOR formats. Proposal is an advisory draft, never a canonical check-in, execution record or TaskNote source. The task card states testable DoD and delivery dependencies.

## Architecture

Separate read-only preparation module and CLI expose deterministic source-labeled JSON. Existing V3/V4 scalar adapters and budget arithmetic are reused, with an in-memory planned-properties interface; canonical calculator CLI remains compatible. Full templates and a core contract govern agent synthesis. Scheduler stays in the desktop automation service, not product cron or tracked runtime files.

## Implementation Slices

| Slice | Files | Acceptance | Evidence | State |
| --- | --- | --- | --- | --- |
| S1 | core contract, templates, routing | complete formats; no canonical writes | artifact review | completed |
| S2 | preparation module/CLI, calculator interface | period, provenance, uncertainty and bounded sources | synthetic and real read-only runs | completed |
| S3 | proposal runner, validation integration | safety/failure/date/capacity regressions | targeted tests and full validation | completed |
| S4 | scoped workflow evidence, upstream delivery, heartbeat | installed checks, verified timezone, no duplicate | updater and scheduler evidence; first-run observation pending until executed | pending |

## Policy And Data Boundaries

Monday reviews Friday-Sunday, Tuesday-Friday yesterday, Saturday Monday-Friday and next Monday-Friday. Sunday is a quiet no-op. No guessed completion, sleep, subjective scores or alignment answer. No raw bodies, OCR, attachments, Daily Working Dump, secrets, code search or unrestricted foreign workspace scans. Weekly dump candidates remain a separate existing limited projection, never plan input. Conflicting evidence stays visible; V4 takes precedence only when it is the newer canonical source. Aggregates remain aggregates. Only exact mapped operational paths may be read across workspaces.

## Artifact QA And Verification

Before implementation: review architecture/plan/spec against the accepted plan, producer-consumer boundaries and missing-data/failure paths. After implementation: full formats and provenance in three proposal modes plus incomplete source scenario; test all listed owner regressions; Phase 5 findings-first whole-diff review. Required commands are listed on the task card. Quality-ready requires no P0/P1/material P2, unchanged historical/private inputs and complete evidence; green scripts alone are insufficient.

## Plan Quality Contract

- Plan classification: implementation-capable.
- Implementation writes planned: yes.
- Delivery Constraints: owner-opt-out, no deadline or time budget; must-have/privacy/QA retained.
- Artifact QA route: architecture/plan/spec QA, with accepted owner plan as primary DoD.
- Implementation Quality Closure: phase-5-quality, then distillation and checkpoint.
- Knowledge capture: technical only, no owner-private facts.
- Cross-system impact: no, explicit owner decision.
- Residual risk: agent interpretation and local scheduling availability; first actual run is not simulated QA.

## Optional Knowledge Capture

Required in the iteration distillation and checkpoint only.

## Owner Decision Checkpoint

All implementation decisions are covered by the accepted plan. Scheduler timezone failure prevents activation; first-run evidence remains pending rather than inferred.
