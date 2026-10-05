# Phase Commit Policy

## Future Scoped Decisions

For future approved work only, planning-range and Phase 6/7 may end in a scoped local commit when the accepted plan explicitly authorizes that Git scope, Quality/capture are current, one coordinator owns the index and counterpart impact is resolved. Phase 8 additionally requires actual scoped final-owner-yes. Existing no-commit always wins; ignored-only/no-op creates no commit. Push requires a separate explicit scope, never inferred from a phase boundary or worker result.

`qa_source_binding.phase_commit` returns a supporting-only eligibility decision, never stages or invokes a commit. Missing Git approval/index ownership, pending impact or unresolved QA blocks the boundary. A cross-system yes decision still needs its privacy-safe handoff; no requires a reason. Normal privacy, scope, DoD and risk checks remain mandatory. Do not force-add ignored runtime, unrelated files, empty commits, reset, stash, cherry-pick or merge automatically.

## Opt-In QA Source Binding

Use opt-in `full-qa-verification-v3` only for implementation-quality with a schema-1 immutable target snapshot and formal owning QA. Bind project/task identity, the exact snapshot SHA-256 and accepted semantic verdict. Snapshot JSON is data, not approval; declare and review all dependencies before freezing it outside the target source population. The default remains current V2 QA and capture schema 2; historical evidence is not restamped or downgraded.

`qa_source_binding.snapshot` inventories the entire physical repo population, including untracked/ignored files, modes, directories and the full index. Only root Git metadata is excluded; nested Git, symlinks, special/sensitive entries or oversized population require fresh QA and an explicit supported scope rather than hidden exclusions. It records repository/common-Git identity, actual HEAD/tree/index and separate dependency inventories.

The consumer recomputes current live population and dependencies. Same-HEAD reuse also requires unchanged baseline tree/index. After commit, only the first single-parent source-only child of the exact baseline can qualify; actual committed blobs/modes and the complete index must equal the snapshot. Ancestry, saved eligible=true or a cached script receipt cannot substitute. Partial staging, hook mutation, changed identity/modes/dependencies or added files reject equivalence.

Tracked runtime commit chains, later commits, unsupported populations and missing target-product proof require fresh QA. Capture schema 3 invokes this same consumer, not another lenient implementation. Current status/QA/checkpoint artifact validation remains a separate fresh obligation. An equivalent source snapshot is supporting evidence, not final acceptance or authorization.

## Current Scope

Compatibility adaptation explicitly forbids commit/push. This policy does not retroactively change that instruction. Native backend interoperability is also unverified; Git eligibility has no relationship to native dispatch permission.
