# Adversarial Review 01

- Reviewer: native agent 01a1032c-b64e-7082-b056-1369d4d725be, read-only attempt ppo-audit-01
- Reviewed source HEAD: bcd1e0dcb9b9b2def6afec9636a72ea058a79ca7
- Reviewed diff fingerprint reported by reviewer: 9b5ef1008a8fd212d7994f59eb4f303bbcb92b50bf719789de5bc44492373fdb
- Disposition: rejected as quality-ready; findings preserved; worker closed before refreshed review

## Findings And Fixes

1. P2: case-insensitive worktree aliases bypassed resolved-string comparison. Fix: filesystem samefile identity for existing paths; identity errors fail closed. Added actual case-alias and portable samefile regressions.
2. P2: imported simultaneous live Workflow/System snapshot bypassed dispatch-only linear fallback. Fix: validate the live-state invariant too; unsupported Workflow live units require a single live delegated unit. Added snapshot regression.
3. P2: CLI logical rebase could not inspect a changed on-disk baseline. Fix: explicit new_source_manifest plus new_baseline recovery event; validate old metadata and no live/accepted work, then verify the new real HEAD/manifest/digest. Old unaccepted identities retire. Added source-drift success and missing/stale/live/accepted rejection cases.

Parent also fixed malformed enum types, null/nonobject event handling, verified-check types and replay/alias regressions. Post-fix full review is separately recorded; this report is not current PASS evidence.

## Boundaries

No writes or recursive agents by the reviewer. Native trials were parent evidence, not independently verified by this reviewer. The previous run manifest became stale after contract corrections; it is preserved as rejected historical inspection, never accepted as a current receipt.
