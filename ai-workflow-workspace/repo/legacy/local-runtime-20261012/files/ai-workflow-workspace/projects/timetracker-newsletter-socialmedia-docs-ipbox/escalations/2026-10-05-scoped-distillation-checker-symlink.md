# WEP-CR-001 Scoped Distillation Checker Escalation

```yaml
escalation:
  at: 2026-10-05
  task-id: WEP-CONTENT-011-editorial-routing
  phase: phase-7-checkpoint-and-phase-8-final-check
  escalation-reason: The supported project-scoped distillation-state checker rejects an existing symlinked runtime directory before inspecting the project's state record.
  classification: blocking-drift
  workflow-effect: STOP

failed-checks:
  - check-distillation-state --project timetracker-newsletter-socialmedia-docs-ipbox
  - check-distillation-state --runtime-only --scope-root projects/timetracker-newsletter-socialmedia-docs-ipbox

evidence:
  commands:
    - ai-workflow/.systems/scripts/check-distillation-state --project timetracker-newsletter-socialmedia-docs-ipbox
    - ai-workflow/.systems/scripts/check-distillation-state --runtime-only --scope-root projects/timetracker-newsletter-socialmedia-docs-ipbox
  artifacts:
    - checkpoints/phase-7-checkpoint-2026-10-05-wep-content-011-editorial-routing.md
    - capture-state/wep-content-011-editorial-routing.md
  observations:
    - Both supported project scopes reject the pre-existing quality/artifacts/node_modules symlink before evaluating the distillation-state record.
    - The link target is a bundled local runtime dependency directory; no link target contents were inspected for this escalation.
    - Full workflow validation's generic distillation-state check and direct review of the project record are supporting evidence only, not a substitute for this scoped check.
    - The existing symlink remains unchanged.

suspected-cause: The upstream validation-scope inventory rejects every symlinked directory beneath a project-owned artifact directory, including this existing quality/artifacts runtime link, with no project-scoped exclusion mechanism.
recommended-path: Route a separate narrowly scoped change to the upstream AI Workflow product owner to make validation scope safely classify or explicitly exclude approved ignored runtime symlinks without following or mutating them; then rerun the project-scoped checker and Phase 7/8.
recommended-path-impact: Preserves the symlink and checker integrity while enabling complete scoped evidence; requires a separate upstream product-change approval and QA.
alternative-path: Keep the symlink and current checker unchanged, retain this escalation, and leave Phase 8 failed until a supported checker/runtime-layout resolution is approved.
alternative-path-impact: No system boundary is crossed, but CR-001 cannot reach a technically eligible owner-final-approval gate.
risk-if-ignored: Treating generic validation or manual inspection as equivalent could conceal an incomplete runtime inventory and produce unsupported Phase 7/8 confidence.
required-owner-action: Approve a separate upstream AI Workflow change request and exact checkout/implementation scope, or explicitly defer the remediation and accept that this project's Phase 8 remains blocked.
```
