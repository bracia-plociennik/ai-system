# Final Semantic Review

## Scope And Findings

Fresh review of the accepted seven priorities, current source diff, input declarations,
runner authentication, capability preflight, quality record producer and behavioral tests.
Three earlier findings remain resolved as documented in semantic-review.md.
A fourth finding was reproduced during closure review: a broken capability symlink was
treated as absent. The producer now rejects linked declarations and linked namespace parents
before absence fallback. Positive and broken-file/broken-directory cases are covered.
No unresolved material finding remains after this fix. Current-source full evidence is
required separately; the preceding completed run is historical input evidence after the fix.

## Manual Decision Traces

1. Runtime-only change with identical declared product input, command, tools, environment
   and coverage may reuse authenticated completed checks. Diff remains fresh. Unknown
   runtime reference closures execute rather than inheriting a stale success.
2. A changed shared contract or consumer implementation invalidates reuse. A commit alone
   is provenance, not a forced invalidation of unchanged explicit inputs.
3. Failed, planned, interrupted, tampered, duplicate or incomplete records do not reuse.
   A checksum without the selected private authentication key does not confer authority.
4. Missing Workflow capabilities preserve installed local gates. Linked or malformed
   capabilities block preflight; capability availability never grants approval.
5. The quality producer fingerprints actual sources and validates the shared schema.
   Reviewer conclusions and the approval reference must be provided, not generated.
   Historical assessments remain evidence of their source, not current acceptance.
6. Bounded-defect eligibility excludes high/critical risk and external/security effects.
   This high-risk policy change follows the full local phase route, not its own shortcut.
7. Observed intervals union overlaps; unmeasured agent/owner time is unknown. Comparative
   script timing is limited to synthetic equivalent check populations, not whole-process speed.

## Coverage And Limits

Reviewed producer-consumer mappings are retained in semantic-review.md. New capability-link
cases extend the adversarial matrix; no assertion or full-required gate was removed.
Conservative whole-product declarations may rerun unnecessarily after unrelated product edits.
Local MAC trust depends on private-key integrity and does not defend against an already
authorized process. Runtime-only benchmark gains do not establish production agent latency.
Detailed counterpart quality production and historical registries still require adoption in
AI Workflow; V1 does not emulate or overwrite its installed evidence schema.

## Boundary Review

No root AGENTS, nested Workflow product, management checkout, prior CR-010 routers,
client/private runtime, commits or pushes are part of these writes. Source fixtures contain
product and synthetic data only. Final-owner-yes remains absent by owner instruction.

## Owner Decision Checkpoint

- Decision state: clear for technical execution through Phase 8
- Final owner approval: not provided

## Optional Knowledge Capture

- Capture recommended: yes
- Target: technical distillation and checkpoint, plus the already delivered handoff
- Privacy/scope check: pass
