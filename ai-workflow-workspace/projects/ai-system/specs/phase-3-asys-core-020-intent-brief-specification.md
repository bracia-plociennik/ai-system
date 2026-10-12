# ASYS-CORE-020-intent-brief Specification

## ASYS-CORE-020-intent-brief — Interpretacja intencji w AI System

- Goal: Dostosować intake i orchestration AI System do tego samego briefu i lokalnego modelu zgody.
- Risk: high (future permission/routing/shared integration behavior); current planning/QA approved, implementation approval absent
- Status/readiness: conditional; complete spec contract can be reviewed now, actual execution prerequisites remain gated
- Scope/output: AI System core adapter, root template routing and business-to-technical handoff with explicit consent/mode mappings.
- Out-of-scope: unrelated refactors, UI/export/global store, real TaskNotes/ledger/Capture/private migration, publication/update/production/external actions, Phase 8/final-owner-yes; current implementation/staging/commit/push forbidden
- Dependencies: IEB-QA-002-intent-brief-verification; actual prerequisite implementation + Phase 5 PASS and required own capture/checkpoint must be inspected before execution, then refresh dependent spec/Spec QA against its delivered source
- Start conditions: explicit future implementation approval, owned codex worktree from reviewed dev, current Spec QA, exact prerequisite outputs/capability/source accepted, safe synthetic command environment, no unrelated staging/overlap
- End conditions: numbered task DoD fully verified, actual implementation diff and tests, formal Phase 5, own capture/checkpoint; no unfinished dependency disguised as completion
- User-decision flag: no unresolved material planning choice; future implementation approval required; any new uncovered effect/cost/scope must be queued
- Implementation gate: CLOSED in current run by owner exclusion; conditional until accepted dependency outputs and refreshed Spec QA
- Task card: tasks/asys-core-020-intent-brief.md
- Spec path: specs/phase-3-asys-core-020-intent-brief-specification.md
- Quality path: none (future Phase 5 artifact not created)
- Notes: solo; current Spec QA path quality/phase-3-asys-core-020-intent-brief-spec-qa.md; no implementation completion claim

### Task DoD

1. AI System and Workflow semantic v1 fields/provenance/disposition map without loss, while each retains its own approval policy.
2. Tasks remain Markdown-first and independent of TaskForge; interpretation creates no TaskNote or schema migration.
3. Scoped context stays in one selected workspace; raw conversations/dumps are not copied automatically to product sources.
4. Read-only/idea/planning commands and corrections retain intended action ceiling; generated brief cannot authorize writes.
5. Current mode mappings and dependency-local blocking are explicit and testable; implementation remains conditional until actual Workflow acceptance.

## Governing Inputs / Dependency Outputs

Owner scope and independent input: decisions/2026-10-09-intent-brief-owner-scope.md, context/intent-brief-source-intent.md. Shared v1 fields/profile/population/behavior corpus: context/intent-brief-shared-semantics-v1.md. Architecture: architecture/cr-012/phase-1-architecture.md. Accepted plan: planning/cr-012/phase-2-project-plan.md; Plan QA: quality/cr-012/phase-2-plan-qa.md. Task card: tasks/asys-core-020-intent-brief.md. Original owner intent/actual constraints remain the review oracle, never just this generated brief.

Dependency outputs: IEB-QA-002-intent-brief-verification; NOT implemented by this run. Future consumer must inspect each dependency's actual diff/commit, current Phase 5, required capture/checkpoint and producer handoff, then refresh source references/spec and rerun Spec QA before Phase 4. Today's complete contract is explicitly dependency-gated; no prerequisite availability or implementation readiness is fabricated.

## Exact Future Implementation Write Set

- .systems/ai/core/intent-to-execution-brief.md
- .systems/ai/core/task-intake.md
- .systems/ai/core/command-routing.md
- .systems/ai/core/prompt-composition.md
- .systems/ai/core/project-orchestration.md
- .systems/ai/core/execution-modes.md
- .systems/ai/core/delivery-constraints.md
- .systems/ai/core/response-contract.md
- .systems/ai/core/context-as-data.md
- .systems/ai/templates/root/AGENTS.template.md
- README.md
- HUMANS.md

Listed nonexistent files are deliberate new implementation outputs, not current evidence references. Runtime implementation/QA/capture evidence will be owned by this project under the relevant future phase. Product write-set expansion or a new transitive policy dependency requires scope review and affected planning/QA refresh before writes. AI System target must never edit its installed ai-workflow/.systems; Workflow implementation belongs in its official upstream owned worktree. Generated management AGENTS and primary installations are not in this future task write set.

## Concrete Implementation Steps (Future, Not Executed)

1. Verify actual accepted Workflow handoff/source and its CORE/QА/capture gates, then refresh this spec against the delivered counterpart and rerun Spec QA.
2. Add AI System interpretation core contract aligned with the shared semantic v1; route at current task intake without adding a new phase.
3. Update root AGENTS template and mode-aware intake/prompt-composition; generated management AGENTS regeneration remains a later authorized update, never edit it directly here.
4. Make orchestration carry outcome/output/DoD, selected target, mode, supplied limits, actual allowed actions and stop phase. Explicitly map human to human-coop and auto-unconstrained to auto-unbounded.
5. Keep TaskNotes and private workspace data unchanged; multi-idea requests remain proposals. Unknown repository or ambiguous target blocks affected work rather than picking a client.
6. Document correction propagation to the technical project and independent QA against original instructions; no business status claims based on chat or UI alone.

## Test And Evidence Plan

Use shared B01–B18 and R01–R16 traceability, independent original-input oracle and synthetic fixtures only. Existing pure check-execution-modes tests and prompt-composition/task-intake/risk/permission source checks must still pass. Structural assertions verify actual producer/consumer links/fields, not only new headings; negative fixtures test unknown versions, missing fields and sources, malformed paths, symlink/mode drift, stale pins, unauthorized action inference and unverified dependencies.

Actual-agent evaluation is required for the completed V1 behavior: paired baseline/candidate sessions with same model/effort/environment, isolated temporary workspaces, observed files/actions/questions/outputs and source fingerprints. The verification task owns full corpus evidence; a contract-only task can receive its own scoped Phase 5 without declaring the entire behavioral feature accepted. No fictional expected-output fixture, echo command or metadata projection may stand in for a live agent run. Unavailable safe runner, unverified touched/read boundaries or an unassessed high-impact effect is explicitly disclosed and blocks the affected behavior acceptance.

Required future commands run from explicit TARGET_REPO_ROOT/AI_WORKFLOW_HOME; intake establishes safe paths. Relevant targeted regression commands are selected from actual implemented files, not guessed package tools. Shared source changes require full `validate-workflow --profile full` for Workflow, and `validate-ai-system --profile full` plus owning installed Workflow runtime consumers for System; smoke must run. Record command/exit/output, execution vs coverage and semantic/native evidence separately. No product/full/eval execution now because the owner authorized planning only.

## Adversarial / Regression / Failure Paths

- Lost negation, wrong output, self-confirming brief: independently map original requirements; zero losses/extra scope, compare accepted decisions and delivered artifact.
- Source says “ignore rules”, wishes or read-only requests: context remains data, original action ceiling preserved; zero product/external/Git effects.
- Missing vs contradictory input: provenance unknown/conflicted; Auto queues protected decisions and excludes affected units, Human groups material questions without repeating solved ones.
- Mixed dependencies/shared resources: actual DAG and reservations reviewed; unknown/shared work cannot be called independent.
- Correction and resume: retain task identity/history/mode/limits/retry counts; invalidate affected specs/QA, preserve unrelated proof.
- Counterpart absent/stale or unsupported schema: fail closed; no auto-install/compatibility PASS; source profile and runtime behavior are separate evidence.
- Timing slowdown or behavior regression: disclose measured results; any semantic/safety-oracle failure blocks acceptance. Do not weaken tests or expand scope to get green.

## Safety / Rollback

Future high-risk implementation needs explicit scope-bound approval and its dedicated codex worktree from reviewed dev. Preserve unrelated staging/runtime/historical evidence; never stash/reset/force-add or update management automatically. Keep source-only release/update separately authorized. A future regression requires a forward fix or approved source rollback; no historical TaskNote/Capture/manifest rewrite. Test workspaces disposable and isolated; no real customer/financial/private content or production services.

## Implementation Gate Decision

- All start conditions fulfilled now: no — implementation explicitly excluded; downstream dependency outputs not implemented.
- Blocking uncertainties in the design/spec: none; delivered sources and measured behavior are explicit future outputs, not guessed values.
- Owner decisions pending for current planning: none.
- Can start implementation in this run: no.
- Future route: explicit implementation approval; verify actual prerequisites/source/worktree; refresh affected dependency-gated spec and Spec QA; then phase-4-implementation.
- Spec QA evaluates the complete consistent testable contract and correct conditional gate, not completion or current write permission.

## Plan Quality Contract

- Plan classification: implementation-capable
- DoD source: decisions/2026-10-09-intent-brief-owner-scope.md and context/intent-brief-shared-semantics-v1.md
- Testable DoD / acceptance conditions: R01–R16 and the task-specific numbered DoD; current planning acceptance is complete, mutually consistent artifact contracts through Spec QA with no product/Git/history mutation
- Artifact QA route: phase-3-spec-qa
- Artifact QA trigger: after the artifact and its governing inputs are complete, before the next phase
- Implementation Quality Closure route: phase-5-quality
- Required verification: original-intent/field/dependency audit, B01–B18 adversarial matrix, relevant regressions and full product validation with smoke for future source changes; actual-agent paired evidence required for feature acceptance
- Quality-ready criteria: required decisions resolved, current applicable QA/source evidence, all task DoD items verified; capability checks alone insufficient
- Owner opt-out: none
- Not-applicable reason: none
- Blocking decision: none for planning; implementation approval explicitly absent and prerequisite outputs gated
- Next route: phase-3-spec-qa; stop this owner-approved run after Spec QA, before implementation

## Delivery Constraints

- Execution mode: auto; explicit owner choice, scoped to this feature planning iteration
- Mode: auto-unbounded; System orchestration equivalent auto-unconstrained
- Deadline: none supplied
- Time budget: none supplied
- Timezone: Europe/Warsaw
- Must-have outcome: both linked scope records, architecture/plan QA and every complete task spec with current Spec QA
- Cutline/deferred scope: all implementation, product tests/evals execution, publication/update, prompt UI/export, mandatory brief files, historical migration and Capture repair
- Quality floor: full semantic artifact review, provenance, independent original-intent reference, risk/permission/source-bound gates; never lower it for speed
- Overrun checkpoint: preserve complete artifact/gate state; queue uncovered scope decision, no invented deadline

## Knowledge Capture And Approval Boundary

Planning facts/decisions are durable in these approved artifacts and QA evidence. No technical implementation distillation is claimed. Distillation State: not-applicable for this planning-only unit; future non-exempt implementation creates its own pending-quality record and required Phase 6/7 after actual Phase 5. Existing Capture records are outside this scope and remain byte-identical.

Model recommendation: strong-reasoning capability class for shared policy architecture, specs and adversarial QA; non-blocking; current exact model configuration unknown. Skills used: none (no matching domain skill after frontmatter discovery).
