# Local Root Paths

Selected task, Work Evidence and project consumers share `.systems/scripts/local_paths.py`.
Resolution supplies paths, never approval, ownership, directory creation, cloning or migration.

## Expressions And Bases

Supported roots: literal absolute paths, `~/...`, `${HOME}`, `${AI_SYSTEM_HOME}` and
`${AI_SYSTEM_WORKSPACE_HOME}` (the corresponding `$NAME` forms are also accepted).
HOME is the current user's home; AI_SYSTEM_HOME defaults to the actual installation
containing the resolver, not the current directory. An explicit selected workspace
overrides the ambient workspace variable. Base variable values must be concrete
absolute paths; unknown, missing, recursive or malformed expressions fail closed.
There is no shell evaluation or glob expansion. Existing symlink components are
rejected before lexical normalization, including aliases hidden by `..`.

Work Evidence root fields require absolute results. Project links and task config
relative paths use the explicitly selected workspace (standalone task config reads
use the config directory). Relative CLI repository/workspace arguments retain an
explicit caller-CWD base. Missing directories stay missing; project execution is
blocked and source availability remains pending. There is no recursive discovery.

Only root fields expand. Relative source references, record locators, entity labels,
tax source references and historical Capture Verification fields keep their semantics.

## Work Evidence Transaction Context

Configuration schema, entries, sessions and commit records remain version 1.
New prepared transaction manifests use schema 2 with a hash-covered `path_context`:
context schema 1, selected absolute `workspace`, resolved `source_roots` by alias and
ordered `ledger_roots`. Existing raw config and registry file hashes still bind approval.
Resolving config creates a copy; it never changes on-disk bytes or historical hashes.

Prepare deduplication, apply and transaction recovery require the same live resolved
context. In-process environment drift also invalidates the loaded Ledger. Unknown
versions, missing/extra context fields and malformed roots fail closed. Schema-1
prepared transactions may replay only with literal absolute root configuration;
there is no proof permitting variable roots to be retroactively attached to them.

Committed schema-1/schema-2 history validates original manifest/record hashes and
chain order. Integrity reads do not require historical host paths to equal today's
host paths. That is not permission to replay a transaction at a different root.
Changing a variable config's raw bytes also invalidates pending transaction approval.
No automatic cancel, reapproval, relocation or history rewrite is performed.

## Adoption And Rollback

Illustrative shared task root: `${AI_SYSTEM_HOME}/kuba-plociennik-workspace/tasks`.
TaskNotes source root adds `/TaskNotes/Tasks`. Each ledger root is its own
`${AI_SYSTEM_WORKSPACE_HOME}`; the tracker remains in that workspace's work-evidence
directory. Shared task visibility does not transfer ledger ownership.

Before adopting expressions, resolve pending transactions under their original
approval and inspect the exact owner-selected roots. New local configurations,
publication, management updates and migrations keep their separate approvals.
Keep canonical source/revision/receipt hashes unchanged. Old readers cannot apply
schema-2 transactions; after new transactions, use a compatible reader or forward
fix rather than downgrading/recasting history. Backup formats remain unchanged;
restoring config requires explicitly reloading its Ledger.

The target consumer list is bounded: task candidate configuration/arguments,
Work Evidence Ledger/init and private-tax workspace-map roots, project orchestration
preflight and explicit repository freshness. This does not add substitution to every
AI System script or to installed AI Workflow's own path resolver.

## Agent installation and context

resolve-agent-context uses the user-owned ${HOME}/.config/ai-system/installation.json, schema1: system_id, system_home, enabled, adapter_ids, owner_workspace_id, owner_asset_id. system_home is absolute or HOME-derived, never self-referential AI_SYSTEM_HOME/recursive expansion. Validate explicit management role, source consistency and registered project/common Git identity; do not infer authority from repository text. Existing local role/Work Evidence schemas remain unchanged.

CLI: resolve-agent-context --cwd ABS --tool codex|claude-code|generic [--workspace ABS] [--system-home ABS] [--format json|human]. Registration conflicts reject, including explicit installation selection; rebind only under a separately approved registration transaction. Exit0 resolved descriptive context,2 malformed/unsupported input,3 unavailable/incompatible,4 conflicting owner/root. requested_write_roots is empty without actual task approval; authorization_assessed=false always. Official Workflow has workflow_mode=official, nested clone target, management has no self-clone. Output contract version is independent of product revision. Unknown/malformed inputs never enroll, initialize or mutate anything.
