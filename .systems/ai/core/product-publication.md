# Product Publication

## Branch And Worktree Policy

Apply `workspace-directory-layout.md`: canonical repos stay in `projects/`;
implementation and release trees use `.worktrees/<repository-id>/<work-id>/`
under the selected collection root. Disposable task output uses `.tmp/<work-id>/`.
The explicit `--prepare` destination below must follow that placement rule.

The product-development checkout uses `dev`. Start implementation worktrees on
`codex/<work-id>` from the verified current `dev`, not `main`. Keep local role
`development` and the local project contract; branch names never grant authority.
One coordinator owns the Git index, integration and approved publication.

`dev` may track approved technical evidence under `ai-workflow-workspace/`.
It is not permission to publish private runtime, secrets, client data or local
configuration. Review each new evidence path before staging; never blanket-add
ignored workspaces. Existing runtime remains byte-preserved unless separately
approved. Management checkouts consume `main` through the official updater.

## Filtered Publication

Publish a complete committed product snapshot, not a merge or PR from `dev` to
`main`. The exact allowlist is `.systems/**`, `.github/**`, `README.md`, `HUMANS.md`
and `.gitignore`. Only `ai-workflow-workspace/**` is excluded as tracked runtime.
Unknown tracked paths, linked product files, secret-like paths and missing root
product files block preparation; extending the allowlist is a reviewed change.
The allowlist is not a secret scanner: semantic/privacy review is still required.

Development QA, local commits and remote push remain scoped owner-approved actions.
No approval follows from a branch, a manifest, a successful check or this policy.
An explicit no-commit/no-push wins. Product publication does not authorize a
management update, workspace migration, branch deletion or final-owner-yes.

Before preparation, verify repository identity, origin URL, actual remote tips,
Git state, source QA and the complete product diff. Fetch is an explicitly scoped
network operation. Current target `main` must be an ancestor of source `dev`:
if main advanced, first reconcile main into dev without overwriting runtime or
unreviewed work, then refresh affected QA. Never force-push or silently discard.

## Preparation And Verification

`.systems/scripts/prepare-product-release` is read-only by default. It resolves
committed source/target identities and reports product additions, modifications,
deletions, modes, manifest fingerprint and excluded runtime count as JSON.
Uncommitted source changes are not included and remain untouched.

```sh
.systems/scripts/prepare-product-release --source dev --target origin/main
.systems/scripts/prepare-product-release --source dev --target origin/main \
  --prepare /absolute/new/release-worktree --branch codex/publish/work-id \
  --owner-approved
.systems/scripts/prepare-product-release --source dev --target origin/main \
  --verify-candidate /absolute/new/release-worktree
```

Preparation requires scoped approval and creates a new isolated worktree from
the captured target main commit. It stages the entire product projection using
a separate index; source runtime and source index are not modified. It performs
no fetch, commit, push, merge, installation or cleanup. No product delta means
no worktree and no empty commit. Interrupted preparation can leave its new
worktree for inspection; do not automatically remove or reset it.

Before and after a publication commit, verify index, live blob bytes, executable
modes and repository identity against the complete source manifest. A committed
candidate must have exactly one parent: the captured main target. Its tree must
contain only the exact product projection. Worker success is supporting-only;
the coordinator reviews DoD, failure paths, skipped checks and privacy before
acceptance. Reusing source QA requires proven identical product inputs and an
applicable QA contract, not merely a successful tool output.

The approved publication commit is pushed explicitly and non-forced to `main`.
Check the remote target again immediately before pushing; a moved target blocks
the release and requires reconciliation/review. Never import dev's runtime
commit ancestry into main. Historical runtime already in main history cannot
be erased by projection and requires separate owner approval if removal is needed.

After publication, synchronize the published main commit back into dev while
preserving approved runtime, check product parity and push dev only when approved.
Product contents converge; commit histories intentionally differ. Future worktrees
start from this synchronized dev. Filtered publication is not a cherry-pick recipe
and does not imply that every runtime-only commit must be released.

## Quality And Boundaries

`check-product-publication` runs offline synthetic repository regressions and
checks the policy consumers. Cover dry-run, no-op, complete projection, runtime
exclusion, additions/deletions, modes, unknown paths, symlinks, stale target,
dirty live bytes, partial index, commit ancestry and explicit approval boundaries.
Scripts remain supporting-only; no script creates semantic PASS or owner approval.
This is an AI System product policy, not an update to AI Workflow or its phases.
