# Runtime Capture Binding

Use only for an explicitly selected isolated workspace runtime scope, after
source/dependency closure and exclusion review. It never replaces product-wide,
CI, updater, release, semantic QA or owner gates. It is not a permission profile.

`runtime_source_binding.runtime_snapshot(repo, project, task, runtime_root,
exclusions, dependencies)` prepares immutable snapshot schema 2 /
implementation-quality / runtime-scope-v1. Capture schema 3 and fresh
full-qa-verification-v3 QA bind its SHA-256; canonical validate_formal and every
collection consumer verify the same binding. Existing snapshot schema 1 and
Capture schema 2 retain their original semantics. Do not relabel old QA.

The entire declared runtime namespace is inventoried, including untracked files,
additions, deletions and permissions. Explicit relative exclusions have a file
or directory kind and a mandatory reviewed reason. Only derived evidence or
mutable administrative outputs may be excluded; code, prompts, configuration
and dependencies must remain bound. Paths cannot overlap. Changing the
definition/exclusions requires new QA; the bound snapshot must never be edited.
Absolute external regular files bind SHA-256 and mode. No linked input roots,
linked dependencies, special files or nested Git repositories. Unknown imports
or dependencies block source-closure acceptance; a manifest is supporting
evidence, not proof that semantic dependency analysis occurred.

QA has its standard complete V3 current run and Source snapshot SHA-256. The
Capture qa_ref binds QA plus snapshot path/hash. Capture source_head must equal
the snapshot assessed head. Git HEAD/index movement outside the source namespace
is irrelevant; repository/common Git identity and actual live runtime bytes must
match. The original commit remains available as provenance. Source or dependency
drift blocks current quality even when Git HEAD is unchanged.

For scheduler transport, review dispatcher.py, test_dispatcher.py, prompt.md
and both systemd unit dependencies. Generated quality/evidence/distillations
may be excluded to prevent circular binding, along with dispatch-events.jsonl
and dispatch.lock (administrative mutable state). Declare additional output
paths explicitly. Changes to scheduling unit bytes or prompt invalidate the
source binding. Reading a ledger or old receipt does not establish new delivery.
Domain SPOR content and live new-run evidence require their own QA.

Rollout: publish reviewed System source through the product release route, update
management with its official updater, then take a fresh scheduler scoped snapshot
and fresh V3 QA. Preserve all older QA and accepted distillation; only the current
Capture proof references the new QA/snapshot. Test current collection consumers
and retain a before-copy. No service/timer edit, manual generation or automatic
backfill. Until every consumer is updated, retain current schema-2 proof.
Rollback: restore the before-copy and use fresh schema-2 QA at current HEAD; never
rewrite historical QA. This feature does not automatically repair other records.
