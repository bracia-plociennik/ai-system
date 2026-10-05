# Overnight Schedules Review Record

## Scope And Evidence

Source baseline: 25ee18623e09ddf94e2ede067a15cc65c7aea11b. Owner-approved CR-010 repair and publication only, AI System without Workflow product changes, no deadline/timebox. Full eight-file diff re-reviewed after the fixture and clipping corrections in the Phase 4 result. No unresolved product finding.

Product full validation: run df518f78d52241a6b1811c30b65894d6, exit 0, all 33 checks and seven smoke suites completed. Standalone SPOR V4 runner completed exit 0; proposal runner 21 tests passed; compile and diff checks exit 0. No reduced smoke scope or assertion removed.

The first project Workflow full attempt exited 1 at smoke process inspection because sandboxed `ps` was denied. Its prior validators completed, but that execution is not passing full evidence. A complete rerun with the required process access is the publication gate.

## Owner-Approved Historical Evidence Relocation

The owner approved archiving both CR-009 reports under the exact directory below and updating explicit technical references. They are immutable historical assessments, not CR-010 current quality and not a repeated Phase 8 or owner approval.

| Archived report relative to project | Original/current SHA-256 |
| --- | --- |
| history/asys-cr-009/25ee186/evidence/recovery-phase-5-asys-pops-017-unified-aggregates-quality.md | 153644d3f24382037f2f934e0262789c11512efef75c8d94d900e6336001ef07 |
| history/asys-cr-009/25ee186/evidence/recovery-phase-8-final-check.md | 876caa6519f3630b472f93829aa0cc5c778985434ac2a4e70c6b89118c7169b9 |

Both original/current hashes match. Routers, technical memory, checkpoints, distillations and CR-009's narrative references point at these approved paths. Frozen QA input tables and earlier archived reports remain byte-preserved; their paths and source fingerprints describe their historical run, not the new source state.

## Negative-Space And Producer-Consumer Review

- Strict clock parsing remains centralized; optional offset defaults to zero. Bool/float/string coercion is not allowed. Positive next-day end is explicit, never guessed from clock ordering.
- Duration is a session-relative wall-clock interval, not DST-adjusted measured sleep. Exact 24 hours is permitted; greater spans and equal same-day clocks fail.
- Both plain rows and matched professional rows preserve offset through rendering. Next-day label and schedule ordering avoid an invented morning position.
- Macro conflict detection preserves existing start-point/clipping policy. A next-day meal cannot fit same-day meal packages, so the projection is unavailable, not fabricated.
- Proposal fallback capacity includes only work rows; sleep remains context. Checkpoint clocks use modulo 1440 with relative day offsets and remain inside the work interval, including short blocks and exact midnight.
- Canonical synchronization and TaskNote preflight run on a synthetic daily with the overnight row. No private records, indexes, tasks or settings were changed by product testing.

## Capture And Remaining Gates

Knowledge capture required: technical Phase 6/7 only. No Codex memory, External Memory or private user data. Product review is complete; formal Quality requires the complete project Workflow execution, followed by current evidence validation and capture/checkpoint. Commit, push and official installed update are subsequent delivery actions. Phase 8 remains outside approval.
