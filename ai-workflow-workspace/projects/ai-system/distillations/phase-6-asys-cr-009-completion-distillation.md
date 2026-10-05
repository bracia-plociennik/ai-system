# CR-009 Completion Distillation

- Task: ASYS-POPS-017-unified-aggregates
- Quality: history/asys-cr-009/25ee186/evidence/recovery-phase-5-asys-pops-017-unified-aggregates-quality.md
- memory-in-repo-memory: true

## What Was Done

The current aggregate implementation was re-reviewed against its accepted mapping/cutover scope and installed state. Runtime completion now distinguishes a done implementation task from the separately approved final CR gate. Fresh full product and project checks include smoke; protected source hashes remain unchanged during this correction.

## Problems

An in-progress implementation status cannot be retained solely because owner final acceptance is outstanding: it contradicts Phase 8 entry. Historical repo intake wording about whole-project closure also cannot act as a current post-final project status.

A failed broad historical private naming audit does not prove a product defect. It remains failed evidence; do not turn the audit into PASS or rename protected history merely to make a product gate green. The accepted aggregate-only boundary defines the applicable product/domain checks, and an actual warning within that boundary still blocks final acceptance.

## Decisions

Mark verified installed implementation done, keep the CR open until current technical final checks pass, then apply only the explicit scoped final-owner-yes. Other open CRs and historical approvals remain independent.

Preserve prior negative QA reports byte-for-byte. A new current report binds reviewed source/spec/decision evidence by hashes. Current status routers point to that report without rewriting the previous attempt.

## Future Rules

- Read a completion claim against its timestamp and scope. Earlier snapshot equality is not a claim that files can never change later.
- Preserve owner/other-process edits; use a fresh protected snapshot for a new read-only acceptance run and describe differences from older snapshots separately.
- After runtime reconciliation, re-review the full current implementation and capture/status boundary before final acceptance. Green structural checks alone cannot settle a semantic gate contradiction.
- Environment-blocked smoke requires an identical safe retry, not a skip or weakened test.

## Capture And Residual Risk

Project-local acceptance constraints belong in technical project memory, not private owner memory, External Memory or System Insights. No new product-wide architecture decision is needed. Historical semantic comparability and future source reconciliation remain limitations; live rollback is not re-executed by acceptance QA.

## Owner Decision Checkpoint

- Decision state: clear
- Source: decisions/2026-10-01-cr-009-completion-scope.md
- Next route: phase-7-checkpoint, then explicitly owner-requested phase-8-final-check

## Optional Knowledge Capture

- Capture recommended: yes
- Target: project-memory
- Owner decision: defer-to-checkpoint
- Privacy/scope check: pass, technical constraints only
