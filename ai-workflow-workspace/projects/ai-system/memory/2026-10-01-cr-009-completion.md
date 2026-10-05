# 2026-10-01 - CR-009 Completion Boundaries

- Date: 2026-10-01
- Topic: implementation completion and scoped final acceptance
- Type: project-constraint
- Status: active
- Scope: ASYS-CR-009-unified-aggregates
- Source: distillations/phase-6-asys-cr-009-completion-distillation.md
- Evidence: decisions/2026-10-01-cr-009-completion-scope.md; history/asys-cr-009/25ee186/evidence/recovery-phase-5-asys-pops-017-unified-aggregates-quality.md; checkpoints/phase-7-checkpoint-2026-10-01-cr-009-completion.md
- Summary: Installed implementation is done independently of the final owner gate. Current acceptance must use current reviewed evidence; historical negative evidence and independent CRs remain separate.
- Applies to: aggregate implementation delivery, target-only acceptance and future reconciliation
- Rule: Preserve failed broad historical audits without claiming they pass. Evaluate the approved aggregate-only product/domain boundary, and stop on every actual in-scope warning. Historical private filename repair requires a separate scope.
- Review trigger: new aggregate CR, source reconciliation, warning-scope change or acceptance/status drift
