# Unified Aggregate Consumer Contract Follow-Up

Recorded 2026-10-01 during final delivery review. This is a scoped correction record, not a new Phase 8 or owner final acceptance.

## Finding And Correction

The aggregate runtime correctly retired V3 writes after activation, but legacy wording in Personal Ops, budget and response contracts still prescribed an unconditional V3 post-write sync and described a V3-only budget source. That instruction could prevent a future approved canonical write from refreshing a unified workspace.

The contracts now require V4 post-write sync for unified workspaces and native V4; only unmigrated V3 retains its existing route. Budget documentation identifies the verified active generation and explains dated-fact deduplication, undivided aggregates, missing-date coverage and unknown balances. The response contract selects the native V4 renderer without retiring legacy V3 rendering.

## Review And Verification

- No application/migration logic or canonical/private data changed in this follow-up.
- Entire follow-up diff reviewed against the activated aggregate contract, shared budget reader and retired V3 writer.
- New contract regression covers version-aware post-write routing and the coverage section.
- Upstream aggregate runner: 25 tests, exit 0; Personal Ops/V4 and diff checks: exit 0.
- Full product validation and final official management update must be observed before reporting completion of this correction; earlier full results do not stand in for the new baseline.
- Current follow-up full product validation completed with exit 0 and all smoke tests. Reviewed product diff SHA-256: `17dcf2421b753eedf9361c04f0901a4d8dceab9359a251272608bdc50b354819`. Final installed update remains the publication gate, reported only after its actual completion.
- Read-only reconstruction from original sources equals every active aggregate row and the complete source inventory; the consumer-contract correction does not change the selected generation.
- Earlier Phase 5, checkpoint and installed-cutover observations remain historical evidence; this record does not overwrite their results.

## Scope And Capture

Existing owner-approved delivery scope, no timebox/deadline, no AI Workflow product change. Technical capture is this correction record and the existing aggregate distillation. Residual risk remains historical semantic ambiguity; no unresolved behavioral conflict remains in the reviewed follow-up diff.

## Optional Knowledge Capture

Technical consumer-contract consistency only; no private owner lessons or Codex memory writes.

## Owner Decision Checkpoint

This correction is required inside the accepted aggregate cutover scope. Formal final acceptance is still separate.
