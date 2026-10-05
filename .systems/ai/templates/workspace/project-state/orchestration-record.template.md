# Project Orchestration: <work-id>

- Work ID: <safe-id>
- Selected workspace: <workspace-id-or-path>
- Owner namespace: <workspace-relative-project-state-path>
- Target repository: <resolved-path>
- AI Workflow project ID: <verified-id>
- AI Workflow version: <commit>
- Git baseline: <commit-and-dirty-write-set-summary>
- Owner request reference: <current-message-or-accepted-plan>
- Goal and Definition of Done: <brief-outcome-and-evidence>
- Route and risk: <local-workflow-route-and-risk>
- Delivery constraints: <resolved-constraints-or-explicit-opt-out>
- Executor and write owner: <identity-or-current-agent>
- Run ID and coordinator ID: <run-id-and-sole-coordinator-id>
- Parallel run plan reference: <approved-runtime-path-and-fingerprint-or-none>
- Run `source_manifest`: <nonempty-list-of-stable-source-input-path-sha256-entries>
- Baseline `source_digest`: <sha256-of-utf8-concatenated-sorted-path=sha256-newline-entries>
- Source manifest coverage: <explicit-stable-input-set-and-omission-limits-not-whole-worktree-proof>
- Run `retired_attempt_ids`: <preserved-unique-retry-rebase-attempt-history-or-empty-list>
- Run `retired_agent_ids`: <preserved-native-identity-history-or-empty-list>
- Shared-router writer: <sole-coordinator-identity-and-owned-router-paths>
- Approved write set and permissions: <exact-scope>
- Workflow source status: <path-and-observed-state>
- Installed local gates: <contract-paths-version-and-evidence>
- Counterpart parallel contract: <pending-or-verified-installed-reference>
- Run `workflow_parallel_supported`: <false-by-default-or-true-with-installed-local-evidence>
- Execution fallback: <none-or-installed-local-gates-serial-or-permitted-read-only-with-reason>
- Native adapter availability: <actual-spawn-send-wait-close-tools-and-limit-evidence-or-unavailable>
- Runtime capacity: <positive-available-delegated-slot-count-and-source>
- Capacity accounting: <all-live-workers-and-reviewers-across-both-systems-including-other-known-runs>
- Coordinator quota adjustment: <runtime-quota-adjustment-or-not-applicable-with-reason>
- Occupied/reserved capacity: <count-including-unconfirmed-submitted-accepted-failed-cancelled-agents>
- Selected wave: <unit-ids-and-count-not-automatic-full-occupancy>
- Run `dispatch_count`: <selected-positive-wave-limit-not-required-occupancy>
- Wave selection reason: <readiness-resources-rework-cost-local-gates-and-intentionally-idle-slots>
- Checkpoint cadence and next boundary: <installed-local-rule-and-next-required-checkpoint>
- Completed local tasks/packages since checkpoint: <count-and-canonical-evidence-not-agent-count>
- Checkpoint boundary open: <yes-or-no-with-evidence>
- Result evidence: <paths-or-pending>
- QA and skipped checks: <evidence-or-pending>
- Distillation State reference: <path-or-pending>
- Local commit: <sha-or-none>
- Blockers and residual risk: <items-or-none>
- Next owner decision: <action-or-none>

## Unit Assignments

Repeat for each worker or reviewer. Use `none` explicitly where applicable. The coordinator
supplies the assignment; native `agent_id` is recorded after spawn. These fields mirror the
assignment contract in `.systems/ai/core/project-orchestration.md`, not a proposed Workflow
capability. Assignment `unit_id` maps to run `units[].id`; the richer native envelope and
manual approval/gate evidence remain here even when not represented in the pure reducer.

- `run_id`, `coordinator_id`, `unit_id`, `attempt_id`: <unique-identities>
- `agent_id`: <actual-native-returned-id-or-not-spawned>
- `system`, `target_repo`, `workflow_project_id`: <verified-target-identity>
- `baseline`: <commit-source_digest-and-accepted-input-artifact-fingerprints>
- `approval_ref`, `route`, `risk`, `local_gates`: <exact-approved-scope-and-installed-gates>
- `goal`, `dod`, `dependencies`: <bounded-outcome-testable-acceptance-and-accepted-prerequisite-evidence>
- `mode`, `write_paths`, `forbidden_paths`: <read-only-or-implementation-and-exact-normalized-relative-paths>
- `resources`: <shared-read-or-exclusive-claims-including-api-schema-and-runtime-resources>
- `worktree`, `evidence_destination`: <verified-isolated-root-and-approved-output-location>
- `delivery_constraints`, `checkpoint_boundary`: <resolved-constraints-or-opt-out-and-next-stop>
- `verification`, `result_fields`: <required-checks-fingerprints-dod-findings-skips-and-risk>
- `no_recursive_delegation`: true
- `stop_conditions`: <scope-drift-overlap-stale-baseline-missing-source-approval-or-unsafe-effect>

## Ownership And Dispatch Evidence

- Dependency graph check: <unique-identities-acyclic-and-accepted-current-prerequisites>
- Known writers and reservations: <identities-write-sets-and-source-or-blocked-unknown>
- Path containment and overlap check: <symlink-directory-overlap-and-approved-owner-evidence>
- Worktree isolation check: <distinct-verified-write-worktrees-or-read-only-serial-fallback>
- Resource conflict check: <shared-exclusive-claims-and-safe-sequence>
- Spawn reservation and result: <unit-attempt-slots-resources-actual-tool-id-and-tool-evidence>
- Send/wait evidence: <recipient-attempt-instruction-reference-bounded-wait-results-and-progress>
- Uncertain tool operations: <spawn-close-timeout-reconciliation-or-none>
- CLI inspection mode: <plan-repo-freshness-check-or-metadata-only-without-repo>
- Pre-event freshness evidence: <actual-head-manifest-digest-and-submitted-accepted-output-hash-checks-or-unverified>
- Post-event freshness evidence: <same-checks-including-new-submitted-output-or-no-event-or-unverified>
- Capacity reassessment: <old-new-limit-source-occupied-count-and-dispatch-decision-or-none>

## Evidence Reception

Repeat per unit/attempt. A submission is not acceptance. An accepted unit is not formal PASS
or owner acceptance and retains its capacity/resources until native termination is confirmed.

- Receipt identity: <run-unit-agent-attempt-baseline-and-approved-input-fingerprints>
- Submitted result: <message-reference-timestamp-and-actual-evidence-paths>
- Run `result`: <attempt_id-baseline-test_summary-findings-and-evidence-path-sha256-entries>
- Changed paths/diff and artifact fingerprints: <scoped-diff-and-fingerprints-or-none>
- Checks and DoD mapping: <commands-results-findings-skipped-reasons-residual-risk-and-acceptance-map>
- Coordinator verification: <actual-diff-path-privacy-resource-local-qa-review-reference-or-pending>
- Run acceptance receipt: <verified_by-coordinator_id-and-verified_checks-intent-diff-tests-privacy-or-pending>
- Unit run state: <pending-ready-running-submitted-accepted-blocked-failed-cancel-requested-cancelled>
- Acceptance/rejection reference: <explicit-coordinator-decision-and-reason-or-pending>
- Late/stale/mismatched output disposition: <preserved-rejected-evidence-and-reason-or-none>
- Native close/cancel request: <tool-result-reference-or-not-requested>
- Termination confirmed: <yes-or-no-and-native-state-evidence>
- Capacity/resource release: <released-with-confirmation-reference-or-retained>

## Recovery And Quality Boundary

- Refresh baseline: <current-git-digest-local-status-artifacts-and-actual-agent-state-evidence>
- Reservation/identity reconciliation: <all-known-agents-and-uncertain-operations-or-blocker>
- Retry history: <preserved-failure-evidence-termination-proof-fresh-attempt-and-retired-ID-replay-check-or-none>
- Rebase/replan: <no-affected-live-agents-invalidated-results-and-new-run-if-already-accepted-or-none>
- Whole-scope integration QA: <current-diff-product-semantic-review-local-gate-evidence-or-pending>
- Local Quality/distillation/checkpoint references: <canonical-workflow-paths-or-pending>
- Next wave authorization: <same-approved-scope-and-open-local-boundary-or-blocked>
- Actual limits and skipped verification: <runtime-isolation-capability-or-evidence-limits-with-impact>

This record is a coordination reference. The target Workflow artifacts own execution state and technical knowledge. Recording an approval reference does not grant new permission.

Only the coordinator writes shared routers and this record. Workers never delegate recursively.
The parent-supplied CLI/model is pure inspection/reducer logic, never a remote launcher or tool
execution receipt. Keep this record to privacy-safe metadata and references; do not duplicate
technical status, private inputs or source evidence. Native tool IDs/results, local permissions,
confirmed termination and required checkpoints must be inspected, not inferred from this template.
The source manifest covers stable inputs only; output hashes stay in `result.evidence`.
CLI inspection without `--repo` is metadata-only, not real freshness proof. With `--repo` and
an event, HEAD, manifest and submitted/accepted output hashes are rechecked before and after
the hypothetical event; that point-in-time check is not a lock or automatic worker launch.
