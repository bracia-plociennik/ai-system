# Shared Workflow Routing

Shared System consumer: shared-workflow-v1.

An owner-enabled shared default lives in the registered System at
`ai-workflow-workspace/shared-installation.json`. It selects the System's single
`ai-workflow/` tool/policy clone for real project repositories inside that System.
The schema is exactly `schema_version: 1`, boolean `enabled`, and
`workflow_home: ai-workflow`. The existing user installation registration and
management role remain authoritative; repository markers are not registration.

`configure-shared-workflow` previews by default. Its `--approved` write requires
actual owner scope and verified installed producer/consumer source profiles.
It changes routing only. Project bootstrap, custom instruction merges, artifact
changes, clone retirement, Git publication and execution need their own covered
scope and applicable gates. `--disable` supports an explicit rollback; it does
not delete projects or artifacts.

`resolve-agent-context` and `project-orchestration-preflight` use the same neutral
`durable_runtime.py` path consumer as Workflow. A configured shared home takes
precedence over old nested discovery. Runtime defaults to each target's own
`ai-workflow-workspace/`, retaining verified persistent durable-worktree bindings.
Missing/invalid shared support fails closed instead of selecting an older clone.

The management root remains management when it exposes shared Workflow.
Registered projects keep their actual owner, canonical/worktree identity and
private state boundaries. Unknown repositories can observe shared availability
without enrollment or loading a personal default; availability is not approval.
Outside-System repositories retain their existing standalone routing.

Read shared `AGENTS.md` and the target's preserved local instructions before
project execution. Pass `AI_WORKFLOW_TARGET_ROOT` when shared tools are invoked
outside the target directory. Do not substitute the shared clone's parent as a
project target. Workflow product development retains explicit official source
mode for testing that source; a development source repo is not another required
project-local installation.

One shared clone is updated through the established source-only installation
procedure and actual required full/smoke gates. Changing a binding never migrates
or repairs old QA, reopens an accepted plan, grants final-owner-yes or removes a
workspace. Retire obsolete clones only under exact scope after per-target
readback and verified preservation of their local state and all artifact roots.

For large source contracts, an explicitly reviewed local shared entrypoint may
keep the native automatic chain short while requiring the unchanged original
contract as a manual read. See agent-adapters.md. Exact original/override hashes
are routing evidence, not owner consent; changed files, unreviewed local shadows,
global overrides and selected guidance over 16 KiB remain blocking.

Capture QA-input verification and current-goal dependency claims resolve
`workflow-source` against the configured shared policy home, preserving the
assessed product source and owning evidence root. Standalone nested and official
Workflow source proofs retain their established locations; explicit
AI_WORKFLOW_MODE=official preserves product-source verification inside the System. Input hashes and
current source identity remain mandatory; switching tools never repairs old QA.
