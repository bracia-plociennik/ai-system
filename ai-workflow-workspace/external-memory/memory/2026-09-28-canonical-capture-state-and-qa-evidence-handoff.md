# Canonical Capture State And QA Evidence Handoff

## Metadata

- Date: 2026-09-28
- Owner decision: yes; the owner approved publication of both fixes and checkout updates.
- Counterparts: AI System and AI Workflow.
- Scope: validator evidence integrity only; no historical record migration.

## Outcome And Decisions

- AI System Distillation State validation selects only documented canonical owner namespaces. Nested repositories, foreign runtimes, and product templates are not capture-state evidence for the selected workspace.
- Historical record formatting is accepted without rewriting records. A completed state still requires exactly one in-scope, existing distillation artifact; missing or ambiguous references fail.
- AI Workflow QA evidence reads the declared overall result, not component rows, command results, or prose containing `PASS`. Conflicting overall results fail. A negative final check may contain successful component checks.
- Neither validator result is a standalone semantic PASS or an owner final approval.

## Source References

- AI System: `.systems/ai/core/distillation-state.md`, `.systems/scripts/check-distillation-state`, `.systems/scripts/check-validator-smoke-tests`.
- AI Workflow: `.systems/ai/core/full-qa-verification.md`, `.systems/scripts/check-qa-evidence`, `.systems/scripts/check-validator-smoke-tests`.
- Project final-check evidence remains in its owner namespace; this handoff does not copy it.

## Validation Expectations

- Canonical capture-state fixtures cover owner namespaces, old presentation syntax, missing/ambiguous references, and symlink/path escape. A real workspace scan must report explicit total, invalid, and unresolved counts.
- QA fixtures cover a negative final check with a passing component, positive decisions lacking evidence, conflicting decisions, and a punctuated positive result.
- Re-run product validation and project-scoped Workflow validation after publication and checkout updates. Inspect the result and skipped checks before making a final-check decision.

## Counterpart Adaptation Checklist

- [ ] Publish the scoped AI Workflow parser fix and update the nested clone through its official updater.
- [ ] Publish the scoped AI System scanner fix and update the management checkout.
- [ ] Confirm installed baselines and rerun the selected project's final-check evidence.
- [ ] Preserve previous negative final-check artifacts as immutable history.

## Privacy And Residual Risk

- Privacy/scope check: passed; no client data, private paths, secrets, credentials, or production identifiers are included.
- Residual risk: selection by canonical namespace does not prove actual model read-set or the semantic accuracy of source records. Final acceptance remains a separate owner gate.
