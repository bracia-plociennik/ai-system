# Checkout Role Bootstrap Distillation

- Work ID: checkout-role-bootstrap
- Owning project: checkout-role-bootstrap
- Date: 2026-10-08
- Acceptance: accepted
- Acceptance basis: current owner-approved final review, distillation and scoped publication; technical capture only, not final-owner-yes
- Product baseline reviewed: 7b999c0d88886295986dbb81a77876bbd9901cfc plus the 20 explicitly fingerprinted product inputs
- Quality evidence: ../quality/local-role-quality.md; ../quality/product-validation.md
- Privacy/scope check: pass; reusable technical decisions only

## Outcome And Decisions

Checkout role is explicit local identity, not a branch convention. The ignored
`ai-system.local.json` has exactly `schema_version: 1` and a `management` or
`development` role. A fresh clone is unconfigured until explicit bootstrap;
existing installations are not guessed, migrated or backfilled.

Management bootstrap may generate a missing local AGENTS from the committed
template. Recognized generated contracts remain unchanged unless explicit
refresh is requested. A Workflow shim or unknown contract is never silently
replaced, even with refresh. Development records its role and preserves the
project contract byte-for-byte; it does not create a management contract,
install Workflow or create a runtime workspace. Missing development AGENTS
is reported as not ready, rather than silently repaired.

Local status is read-only. Role and contract readiness are not owner approval,
proof of Workflow installation, workspace readiness, isolation or QA. Management
does not require Workflow in its root; managed-project preflight remains local
to the selected project's actual repository.

## Verification And Reusable Lessons

The 29 synthetic behavior tests cover explicit first role, idempotence, saved
role reuse, byte/mtime preservation, strict JSON, conflicts, CLI exit semantics,
missing templates and linked paths. Semantic producer-consumer/adversarial review
found no remaining blocker. Required-artifact and whitespace checks succeeded.
The complete supporting product run completed 37 checks and seven smoke groups;
the negative population remains 222. All 373 product inputs and modes were
reverified against its isolated fixture after the runtime-only upstream change.

Preflight rejects ordinary input problems before either output is written.
Filesystem publication uses atomic individual files and no-clobber creation,
but is not a multi-file transaction or concurrency lock. Unexpected filesystem
failure requires explicit inspection; concurrent bootstrap writers are unsupported.

Keep identity configuration local, ignore populated files and validate that
they are not staged. Never infer role from a basename, remote, branch or the
presence of a nested installation. Preserve technical evidence separately from
product publication and do not fabricate freshness by restamping old reports.

## Boundaries And Residual Risk

No management rollout, local role activation, AGENTS refresh, runtime migration,
counterpart change or formal Phase 8 was performed. Cross-system impact is no;
counterpart none and handoff not-required. Auto/Human work is separate.
Metadata cannot technically enforce an agent's behavior or filesystem isolation.
Historical runtime files untracked by upstream were retained locally with exact
bytes, not republished in this scope.
