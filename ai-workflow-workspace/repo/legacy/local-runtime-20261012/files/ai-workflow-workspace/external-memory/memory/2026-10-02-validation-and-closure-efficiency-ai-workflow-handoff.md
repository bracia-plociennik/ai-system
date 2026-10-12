# Cross-System Upgrade Handoff

## Metadata

- Date: `2026-10-02`
- Source system: `ai-system`
- Counterpart: `ai-workflow`
- Status: `accepted-for-handoff`
- Privacy/scope check: `pass`
- Raw client data included: `no`
- Delivery constraints: owner opted out of deadline and timebox.
- Implementation state: accepted design; AI System implementation in progress. This is not release evidence.

## Concept And Intended Outcome

Implement `validation-and-closure-efficiency-v1`: eliminate unnecessary repeated execution and formatting rework without reducing coverage, semantic review, approvals, or evidence integrity. AI Workflow can adapt its own producers and consumers in parallel. The seven requirements below are the complete integration scope, not an instruction to import another system's runtime.

## Owner Decisions

- Complete all seven priorities; technical Phase 8 may run, but no final-owner-yes is inferred.
- Cross-system impact: yes. This handoff is requested before implementation to enable parallel work.
- Commit, push, installation updates, production, and migration are not authorized by this handoff.

## Cross-system Impact

- Owner decision: yes
- Counterpart: ai-workflow
- Handoff artifact: external-memory/memory/2026-10-02-validation-and-closure-efficiency-ai-workflow-handoff.md
- Reason: shared validation, evidence, refresh, and closure efficiency requirements.

## Safety And Authority Boundaries

- Each agent writes only its own upstream product and execution artifacts. Neither modifies the other's nested installation, runtime routers, or source files.
- AI System continues to obey the installed AI Workflow gates. New behavior is used only after explicit capability discovery, not inferred from a directory or version number.
- Delegation and this advisory document do not create approval. The owner must authorize the counterpart's execution scope in its own conversation.
- Fresh semantic review, DoD assessment, failure-path review, and residual-risk assessment are never replaced by cached scripts.
- CI and updater validation remain freshly executed in V1. No automatic reuse for publication/install gates.
- No private projects, raw prompts, client data, credentials, or historical report rewrites are included.

## Seven Adaptation Requirements

1. **Source-bound check reuse.** Bind each successful completed check to its implementation/dependencies, declared inputs, parameters, tool versions, environment, and coverage. Recheck all identities before reuse. Unknown dependencies, timeout, interruption, failures, missing inputs, and changed coverage invalidate reuse. Report executed/reused/invalidated/not-applicable separately and retain the source run. A different commit alone is not an input change.
2. **Separate product and execution-artifact validation.** Declare product/runtime-artifact/integration/environment categories and applicability before execution. Router or checkpoint changes run their consumers; unknown impact escalates. Add project-artifact checks that do not repeat unchanged framework smoke tests, but preserve fresh full validation where the installed contract requires it.
3. **Bounded defect route.** A reversible defect with known consumers, observable DoD, accepted scope, and regression evidence may use one compact work record. Medium risk is eligible only when the local risk contract explicitly supports it. Security, permissions, billing, production, migrations, irreversible effects, and architecture changes retain broader gates. Capture reusable knowledge, not boilerplate per phase.
4. **Historical QA lifecycle.** Distinguish current/historical/superseded assessment and assessed baseline. History remains immutable and cannot supply current PASS. A new product change must not require moving or rewriting unrelated historical reports solely to stop treating them as current evidence. Integrity/privacy checks still apply.
5. **Schema-driven quality producer.** Generate deterministic metadata, safe names, input fingerprints, and evidence tables from the same schema consumed by validation. Semantic findings, DoD, verdict, and owner approval remain supplied evidence, never invented. Validate before publication. AI Workflow owns its Phase 8/owner-approval producer; AI System must not emulate an unsupported format.
6. **Selective refresh and preflight.** Store opened-contract fingerprints, authorized scope, and resume stage. Resume rereads changed or relevant sources, not every document; do not repeat resolved approval questions. Check needed tools, cwd, environment, and capabilities before expensive work. Permission failure stops early; it does not authorize escalation.
7. **Whole-process timing.** Record discovery/refresh, implementation, review, product tests, artifact work/rework, owner waiting, and publication. Include rerun reason and affected inputs. Keep wall time distinct from child time and do not sum overlapping intervals. Model/reading estimates must be labeled estimates; absent telemetry is unknown, not zero.

## Integration Interface

- Interface contract: `execution-efficiency-v1`. Capabilities are explicit booleans, not assumed from a release version.
- Suggested capability names: `source-bound-check-reuse`, `project-artifact-validation`, `bounded-defect`, `historical-qa-lifecycle`, `quality-record-producer`, `selective-refresh`, `process-timing`.
- Interoperability requires a documented machine-readable capability record before AI System selects a local extension. Missing/unknown capability means the existing installed route.
- Reuse records must expose check ID, source run ID, state, input/implementation/environment/coverage fingerprints, and exit status. A reused result is supporting evidence, not newly executed evidence.
- A work record must expose work ID, approval reference/scope, DoD, route, source baseline, inputs, changed artifacts, semantic assessment, check references, capture disposition, and timings. Do not duplicate project specifications or task lifecycle state.
- Each system retains its own schema/validator ownership. These interface requirements do not dictate a copied implementation or shared runtime registry.

## Source-System References

- `.systems/ai/core/validation-routing.md`
- `.systems/ai/core/validation-profiles.md`
- `.systems/ai/core/project-orchestration.md`
- `.systems/ai/core/distillation-state.md`
- `.systems/scripts/validation_runner.py`
- `.systems/scripts/validation_support.py`
- `.systems/scripts/validation-dependencies.json`
- AI System starting baseline: `b21295774b62fb25359d8b8a11f7a48f20e57f46`.
- Installed Workflow starting baseline: `0c767da0385723560d1b0d4794a9091316c23140`. Verify counterpart HEAD independently; do not treat this as an update request.

## Validation Expectations

- Identical successful check inputs allow reuse; changed consumer, check implementation, parameters, tools, environment, or coverage invalidate it.
- Failed, interrupted, timed-out, incomplete, forged, or undeclared-input evidence never reuses.
- Runtime-only closure does not rerun unchanged product tests unless an existing full-required gate demands it.
- Historical integrity is checked without converting historical verdicts into current approval.
- Producer output validates before durable publication; malformed semantic assessment and fabricated approval are rejected.
- Older Workflow capabilities fall back safely, including the currently installed full-required gates.
- Run synthetic baseline and candidate cases: bounded multi-consumer defect, runtime-only closure, and shared-contract change. Preserve equivalent coverage; collect three comparable timing samples per variant. No speedup claim without measured comparable evidence.
- Review negative paths, privacy, rerun reasons, actual opened sources, and Phase 8 owner separation.

## Counterpart Adaptation Checklist

- [ ] Define capability discovery and source-bound reuse with negative-path tests.
- [ ] Separate project artifact checks from unchanged product smoke execution.
- [ ] Add locally authorized bounded-defect eligibility without weakening risk gates.
- [ ] Model current/historical/superseded QA without modifying original reports.
- [ ] Provide schema-driven Phase 8/owner-approval generation and prepublication validation.
- [ ] Implement selective resume and environment preflight without approval expansion.
- [ ] Measure whole-process timings and equivalent benchmark coverage.
- [ ] Produce an outcome handoff with limitations; do not claim the other system has adopted it.

## Privacy Check

- Client or private runtime copied: `no`
- Secrets or credentials copied: `no`
- Production identifiers copied: `no`

## Residual Risk

Declared dependencies may be incomplete; unknown impact must fail closed to execution. Capability differences may keep repeated full validation mandatory until the counterpart is updated. Timing from synthetic fixtures does not establish production speedup. Technical Phase 8 remains separate from final owner acceptance.

## AI System Outcome Addendum

The initial design above remains historical handoff context. AI System now implements the
seven-priority V1 contract in `execution-efficiency.md`, `execution_efficiency.py`, the validation
runner, dependency registry, orchestration preflight and `prepare-quality-record`.

- Reuse is explicitly selected and authenticated with a caller-supplied owner-only local key.
  The key is not published or automatically created. Full, CI and updater runs stay fresh.
- Complete product declarations bind files, directory inventory, helpers, parameters, tools,
  environment and coverage. Unknown declarations and runtime reference closures run fresh.
- Optional capabilities use `.systems/ai/capabilities/execution-efficiency-v1.json`, contract 1,
  explicit booleans. Missing falls back; linked, broken-linked or malformed records block.
- The quality producer accepts reviewer semantics and path inventories, computes metadata and
  fingerprints, validates its shared schema and publishes atomically without overwriting.
  It does not produce the installed Workflow Phase 8 format or owner-approval evidence.
- Historical classification preserves original reports. Existing Workflow historical QA
  consumers still need counterpart adaptation; AI System does not change them in a nested clone.
- Current supporting run: `7d0e53abb22e401fb51282bcf74dbf42`, full, exit 0, 34 checks,
  seven smoke groups and 220 negative cases. Fifteen new behavioral tests cover the V1 boundary.
- Source digest: `1d2f8cee4695436a106d2f0052c9ea2abba908122b4c86f578e0ba2f7d305188`.
  This is an unpublished worktree assessment, not a counterpart release or installation claim.
- Final benchmark evidence and formal phase evidence live in the isolated technical project
  `projects/validation-and-closure-efficiency-v1/quality/`; whole-agent latency is not measured.

Known limits: whole-product declarations over-invalidate; runtime consumers cannot reuse without
complete reference closure; MAC trust assumes local key integrity; installed Workflow gates
continue to apply. No final-owner-yes, commit, push or management rollout is authorized.
