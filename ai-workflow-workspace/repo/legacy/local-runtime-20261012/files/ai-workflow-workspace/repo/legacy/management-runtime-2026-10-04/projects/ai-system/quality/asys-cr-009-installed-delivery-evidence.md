# Unified Aggregate Installed Delivery Evidence

Recorded 2026-10-01 after publication and the approved target-only cutover. This supplements frozen Phase 5/7 evidence; it is not a Phase 8 final check or final owner approval.

## Publication And Installed Verification

- Product commit: `5fb67dabeff605b5508a0e908a5170880038cd14`, published on `origin/main` and installed in management.
- Official `update-from-upstream`: completed, exit 0; full product validation and all smoke tests ran.
- Generated root contract refreshed with `init-ai-system --refresh-agents`; target workspace `update-workspace --dry-run` performed without backfill.
- Installed Personal Ops/V4, Weekly Planning/V4 and Task Management checks: exit 0 before and after cutover.
- Installed aggregate runner: 24 regressions, exit 0. Installed SPOR V4 runner: exit 0.

## Actual Cutover Evidence

- Read-only mapping audit: 102 effective sessions, 76 historical and 26 native V4; 164 registered fields, 108 source hashes, no unmapped fields or conflicts.
- Owner-approved migration: `active-and-archived`; immutable generation `9f06461a487e788a7bd61148`.
- All 12 previous index outputs archived and compared to pre-migration SHA-256 values: no changes.
- All six stable V4 links select the same verified generation; no active legacy index files remain.
- Two post-write syncs preserve the same generation and all 102 records; status-only reports unsynced 0. Repeated migration dry-run reports already-active.
- All 462 protected canonical, weekly-plan, TaskNote and foreign-workspace input/index hashes remain unchanged after migration and consumer probes.
- Monday/weekend, regular Daily and Saturday Weekly proposal packages: exit 0, read-only, each uses the latest 30 Daily records.
- Budget probes for historical, vacation, month-end and current periods: exit 0. Incomplete periods expose missing-date coverage and unknown full balances; no historical data invented.
- Current canonical renderer: exit 0, no source rewrite. An existing ambiguous/missing macro profile remains explicitly unknown rather than being manufactured by migration.
- Sanitized trends reviewed: report counts and allowed categorical counts only. Selected local Dreaming reference changed from V3 to V4; historical Dream Reports unchanged.
- Private delivery details remain solely in the selected aggregate input namespace. No private financial, health, calorie, lesson or client payload is stored here.

## Warnings And Limits

The first management updater invocation explicitly selected the private target for broad validation and failed pre-existing historical naming checks (TaskNote names, dependency files and weekly filenames). Those files were not renamed. The official updater was rerun in product scope with all smoke tests, then target-only Personal Ops/Weekly/Task Management checks were separately completed. No claim is made that every unrelated private-workspace naming rule passes.

Rollback was verified with synthetic new-source fixtures, not exercised destructively on the owner's live history. The local Dreaming scope retains its pre-existing document format; only its aggregate dependency and detailed-index exclusion were changed. No Dreaming run, historical report repair, other workspace migration, TaskNote write, canonical rewrite or AI Workflow product edit occurred.

## Scope And Capture

Delivery Constraints: owner-opt-out, no deadline or time budget; quality floor preserved. Knowledge capture: required technical delivery evidence, distillation and checkpoint; no Codex memory writes. Cross-system impact: no, owner decision; AI Workflow product unchanged. Legacy semantic ambiguity and future historical source edits remain reconciliation risks.

Formal Phase 8 and final-owner-yes remain unrequested. Implementation delivery is complete; project final acceptance is a separate gate.

## Optional Knowledge Capture

This technical record supplements the existing distillation; no private lessons are promoted.

## Owner Decision Checkpoint

Delivery uses the existing explicit owner approval. No new final acceptance is inferred.
