# Cross-System Upgrade Handoff

## Metadata
- Date: 2026-10-01
- Source system: ai-system
- Counterpart: ai-workflow
- Status: accepted-for-handoff
- Privacy/scope check: pass
- Raw client data included: no

## Concept And Intended Outcome
Validation must be fast enough for ordinary work without weakening evidence integrity. The product now separates execution success, complete coverage and formal eligibility; it binds evals and timing to actual source and result fingerprints. Scoped evidence is restricted to complete, owned runtime namespaces. Shared-source changes and final integration remain full-required.

## Owner Decisions
- Implement the eleven-task program with no deadline/timebox.
- Deliver one complete result through Phase 8, without final-owner-yes.
- Local reviewable commits only; no push or management rollout.
- Cross-system impact yes; adaptation in the counterpart requires a separate review and approval.

## Safety And Authority Boundaries
- Exact expected rejection code and cause; infrastructure failure is not a negative-test success.
- New evidence files are atomic and no-clobber; foreign repositories and symlink parents are not output targets.
- Timeout and signal cleanup affects only owned process groups.
- Eval freshness binds plan, sources, metadata, grade membership and evaluated output.
- Grade freshness does not prove truthful grading or confer approval.
- Metadata skill discovery precedes reading the full matched contract; legacy imports remain inactive.
- Dream recommendation lifecycle is advisory evidence, never an action executor.
- Historical records remain unchanged; private runtime is not copied or crawled.

## Source-System References
- .systems/scripts/validation_runner.py
- .systems/scripts/validation_support.py
- .systems/scripts/validation-dependencies.json
- .systems/scripts/smoke_assertion.py
- .systems/scripts/smoke_coverage.py
- .systems/ai/skills/skill-creator/scripts/eval_freshness.py
- .systems/scripts/discover-skills
- .systems/scripts/dream_recommendations.py
- .systems/scripts/report-workspace-freshness
- .systems/scripts/report-contract-topology
- .systems/ai/core/validation-routing.md
- .systems/ai/core/validation-profiles.md

## Validation Expectations
- Run check-validation-integrity and exact negative completeness tests.
- Reuse neither stale grades nor partial/failed timing runs.
- Require at least three frozen complete runs per variant and equal coverage/environment.
- Compare transaction bodies, setup, helper/direct assertions and restoration, not just case counts.
- Preserve all failed attempts and test symlink/no-clobber/interrupt/missing-consumer paths.
- Scripts remain supporting-only; final owner acceptance is separate.

## Counterpart Adaptation Checklist
- [ ] Compare with current local contracts before importing any implementation.
- [ ] Preserve Workflow formal phases and owner gates.
- [ ] Review typed assertions and transaction-ownership manifests.
- [ ] Review source/result-bound eval freshness and standalone aggregation.
- [ ] Review source-bound timing and timeout cleanup.
- [ ] Adopt only missing runtime-scope or discovery/lifecycle behavior.
- [ ] Keep shared source, CI, updater and final integration full-required.
- [ ] Run semantic and adversarial QA before supporting scripts.

## Privacy Check
- Client or private runtime copied: no
- Secrets or credentials copied: no
- Production identifiers copied: no
- References are product-relative and contain no private home paths.

## Residual Risk
Static contracts cannot guarantee every future agent's routing, truthful grading or approved read set. Local remote freshness is unknown without fetch. Performance benefits must not be inferred from unequal test populations or from successful scripts alone.
