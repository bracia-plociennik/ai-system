# Parallel Project Orchestration V1: Current Handoff

## Metadata

- Date: `2026-10-03`
- Source system: `ai-system`
- Counterpart: `ai-workflow`
- Status: `accepted-for-handoff`
- Implementation status: AI System own scope implemented, quality verified and captured through Phase 7; uncommitted isolated worktree
- Privacy/scope check: `pass`
- Raw client data included: `no`
- Authority: advisory coordination context

## Concept And Intended Outcome

AI System is developing parallel-project-orchestration-v1 alongside the proposed AI Workflow
parallel-task-orchestration-v1. The outcome is a shorter time to a correct integrated result,
including review and QA, when independent work justifies delegation. Speedup is a hypothesis.

One execution coordinator controls a flat set of workers. Entering an AI Workflow project does
not automatically spawn a second coordinator or another worker pool. AI System selects the
workspace and target; the installed local Workflow controls phases, technical QA and capture.

## Owner Decisions

- Cross-system impact: yes; counterpart ai-workflow.
- No deadline and no timebox.
- The orchestrator dynamically selects worker count; no fixed two/three-agent product limit.
- One run-level resource budget includes workers and reviewers across both systems.
- No recursive worker delegation in V1.
- Approved AI System work ends after QA, distillation and Phase 7 checkpoint.
- Commit, push, nested updates and Phase 8 are outside the current approval.

## Cross-system Impact

- Owner decision: yes
- Counterpart: ai-workflow
- Handoff artifact: external-memory/memory/2026-10-03-parallel-project-orchestration-ai-workflow-handoff.md
- Reason: align flat delegation, run-wide capacity and local Workflow execution boundaries.

## Safety And Authority Boundaries

- Delegation inherits the exact approved scope and local gates; it never creates new approval.
- One coordinator writes shared status, memory and formal evidence.
- Separate worktrees or equivalent write isolation are required for concurrent implementation;
  worktrees are not a security sandbox. Test databases, ports and generated files also need ownership.
- A submitted worker result is ready for review, not formal PASS or final owner acceptance.
- Unknown writers, unresolved shared decisions and unsafe resource overlaps block affected writes.
- Timeout/cancel-request does not free a slot until worker termination is confirmed.
- Runtime limitations constrain actual capacity; the plan contains no fixed product worker cap.
- Unavailable/incompatible Workflow support falls back to its installed local gates.

## Source-System References

- `.systems/ai/core/project-orchestration.md`
- `.systems/ai/core/execution-efficiency.md`
- `.systems/scripts/project-orchestration-preflight`
- `.systems/ai/templates/workspace/project-state/orchestration-record.template.md`
- Counterpart existing `.systems/ai/core/parallel-work-policy.md`
- Counterpart planned `.systems/ai/core/parallel-task-orchestration.md` (not yet verified as implemented)

## Validation Expectations

- Dependency cycles, duplicate IDs, resource/file overlaps and unready dependency results are rejected.
- Agent budget, cancellation, late results and resume behavior are tested with synthetic projects.
- Same-scope sequential and parallel trials compare wall time through integration/QA, rework and findings.
- Integration review covers intent/plan/spec/DoD, the complete diff, failure paths and current evidence.
- Local Workflow checkpoint cadence and owner-triggered Phase 8 remain in force.

## Counterpart Adaptation Checklist

- [ ] Agree one execution coordinator and flat delegation across system boundaries.
- [ ] Align assignment/result identifiers, state transitions and resource-budget ownership.
- [ ] Agree a versioned capability handshake; a capability is support metadata, not authority.
- [ ] Align cancellation, confirmed termination, stale result and recovery semantics.
- [ ] Clarify subagents under one execution run versus independent implementation-range autopilots.
- [ ] Provide final implemented contracts, fixtures and runtime QA before claiming interoperability.

## Privacy Check

- Client or private runtime copied: `no`
- Secrets or credentials copied: `no`
- Production identifiers copied: `no`
- Content: product integration decisions only; source references are repository-relative.

## Residual Risk

The counterpart final contract is pending. AI System can implement its own behavior and test the
adapter against synthetic capability fixtures, but cannot claim installed Workflow interoperability
until the counterpart implemented contract and evidence are reviewed. This handoff does not authorize
counterpart writes or import historical approvals/status.

## Implemented AI System Interface

- Core: `.systems/ai/core/project-orchestration.md`, flat coordination, dynamic wave selection and confirmed native termination.
- Run schema: `.systems/ai/templates/workspace/project-state/parallel-run.template.json` (contract 1).
- Assignment envelope: `.systems/ai/templates/workspace/project-state/orchestration-record.template.md`.
- Pure reducer: `.systems/scripts/parallel_orchestration.py`; validates graph, exclusive resource claims, conservative path aliases, capacity and identity/receipt transitions.
- Inspection CLI: `.systems/scripts/check-parallel-orchestration --plan <run.json> --repo <selected-root> [--event <event.json>]`; no launches or saved transitions.
- Preflight: `.systems/scripts/project-orchestration-preflight --parallel-plan <run.json>`; actual repo/input/output hashes checked, unsupported Workflow capability rejected.
- Source digest: SHA-256 of sorted `path=sha256\n` manifest entries. This is the declared stable input set, not an implicit whole-repo snapshot or repository lock.
- Recovery preserves retired attempt/native agent IDs. Logical `rebase` requires no live workers or accepted results, an explicit new manifest and actual new baseline verification; it does not perform Git rebase.

## Actual Quality And Capture

- Planning: architecture, project plan and five specifications plus formal artifact QA.
- Product quality: 85 focused behavior tests; all seven smoke groups, 222 expected negative cases and full profile completed with exit 0.
- Current supporting run: e8058c84353f4c3e8e99dfa3e092edc6. Scripts are supporting-only; independent adversarial findings were corrected and the integrated diff re-reviewed before semantic quality closure.
- Native trial: same two read-only synthetic inputs yielded correct sums in linear and parallel modes; all agents closed. One-sample timing 46.669/30.514 seconds is not general project-speedup evidence.
- Execution evidence: `projects/parallel-project-orchestration-v1/` in the source development runtime, including quality, reviews, native trials and the separate dependency record.
- Phase 6 technical capture and Phase 7 checkpoint completed; Distillation State completed. No Phase 8, final-owner-yes, commit, push, nested upgrade or management rollout.

## Separate Pending Dependency And Limits

Final AI Workflow parallel capability/schema negotiation remains `pending-counterpart`. The preflight deliberately rejects asserted Workflow parallel support until a final installed contract is reviewed and a handshake implemented. That dependency does not invalidate AI System's own completed synthetic scope; it prevents an interoperability claim.

The adapter is coordinator-operated native tooling, not an autonomous scheduler. Worktrees are not a security sandbox. Real client writes, injected native service failures and whole-project performance were not tested. Implementation workers used the installed baseline Workflow's explicit disjoint-write policy in one isolated product worktree; this is not proof of the new separate-worker-worktree rule. Future modeled parallel-write runs require separate verified worktrees and resource ownership.

Counterpart action: compare final schemas, global capacity ownership, evidence receipt, termination/retry/rebase semantics and local phase gates. Request a separate compatibility adaptation if they differ; do not copy historical status or approvals from these evidence files.
