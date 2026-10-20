# Workspace Directory Layout

## Repository collection

The selected AI System workspace `projects/` contains only the owner's canonical
project repositories. A canonical checkout may itself use Git's linked-worktree
representation; the distinction is its owner-selected project role, not whether
`.git` is a file. Auxiliary implementation, review, publication and verification
worktrees are never additional projects in that collection.

Use this layout relative to the verified repository-collection root:

```text
projects/<repository-id>/
.worktrees/<repository-id>/<work-id>/
.tmp/<work-id>/
```

For AI System coordination, the collection root is the selected workspace resolved
under the existing workspace-selection and local-path rules. Standalone AI
Workflow uses an explicitly selected, approved collection/storage root outside
the target repository; resolve it from the current execution context before
creating a worktree. Do not substitute the default owner workspace for an
explicitly selected company workspace. Never hardcode a home directory, user
name, machine or operating system. Work IDs and repository IDs remain scoped
metadata, not shell commands or approval.

## Worktrees and temporary files

Before creating a worktree, inspect the parent's registered worktrees and reuse
a suitable owned one. Create new auxiliary trees under `.worktrees/`, with the
existing explicit branch/base, isolation, source-review and permission rules.
This applies to implementation and source-only release preparation alike. Pass
the resolved absolute destination to tools that require one; a tool accepting an
arbitrary path does not change this agent placement rule. Do not create a second
project entry or an alias under `projects/` for an auxiliary tree.

Disposable task scripts, scratch clones, temporary validation workspaces and
intermediate output belong under `.tmp/<work-id>/`. Set `TMPDIR` to that approved
task directory when invoking a tool or test harness that supports that root
under its existing output-safety guards, so temporary-file APIs inherit the
same placement. Do not widen or bypass a guard to relocate internal tool output. Platform-managed internal
temporary files and isolated CI runners remain platform-owned; this contract
does not require changing operating-system settings. When temporary Gitless
fixtures live under a Git-managed workspace, set `GIT_CEILING_DIRECTORIES` to
the task scratch root for the test process, so Git does not discover the
workspace ancestor as a foreign fixture repository. Explicit fixture repositories
with their own `.git` remain discoverable. Durable QA, Capture and checkpoints belong from the beginning in the owning
persistent runtime outside auxiliary worktrees and scratch. Accepted code must
have a preserved canonical Git ref before an environment becomes disposable;
unfinished work is retained. Apply task-resource-cleanup.md for new registered
task resources; no automatic adoption/migration of old environments.

Creation and reuse still require the existing scoped write authority. Do not
follow linked storage roots, overwrite another work unit, edit ignore rules,
move existing files, delete worktrees, reset changes, commit or push just because
this layout exists. Existing misplaced repositories, materials and history are
preserved until an exact owner-approved relocation scope is supplied. Preserve
historical QA bytes and record relocations separately; a path change never
supplies fresh QA or changes the assessed HEAD.

## Runtime namespace distinction

`AI_WORKFLOW_WORKSPACE_HOME/projects/<project>/` is the logical namespace for
plans, tasks, specs, Quality and Capture. It is not the AI System repository
collection `projects/`: keep its existing layout and lifecycle. Do not put Git
clones, auxiliary worktrees or scratch runs there. AI System project runtime
continues under the nearest-owner `project-state/`. Raw imports use the existing
dump/intake routes; project materials use their accepted context/document roots.

The hidden storage directories are optional operational storage, not new
required workspace schema roots. No automatic backfill, data migration or
cleanup follows from this contract.
