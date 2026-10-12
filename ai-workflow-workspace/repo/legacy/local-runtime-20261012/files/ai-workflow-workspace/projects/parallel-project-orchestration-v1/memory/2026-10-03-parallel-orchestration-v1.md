# 2026-10-03 - Parallel Orchestration V1

- Date: 2026-10-03
- Topic: flat dynamic delegation and evidence
- Type: project-constraint
- Status: active
- Scope: project
- Source: distillations/phase-6-ppo-core-005-quality-distillation.md
- Evidence: five Phase 5 quality records; quality/product-inputs.json; current full run e8058c84353f4c3e8e99dfa3e092edc6
- Summary: one coordinator owns one global pool and shared routers; worker count is chosen dynamically with no fixed cap. Reservations remain occupied until native termination is confirmed.
- Applies to: run model, native assignment/reception, preflight, future Workflow integration
- Rule: preserve actual baseline/input/output hashes, retired identities and local gates; use serial/read-only fallback until final Workflow support is negotiated.
- Review trigger: counterpart final handoff or any schema/authority/resource-boundary change.

No general performance, production isolation or cross-system interoperability claim is supported. Product changes remain uncommitted in the isolated worktree; Phase 8 and publication were not authorized.
