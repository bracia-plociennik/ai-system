> Compatible new implementation tasks use `default-sprint.md` V2: bounded targeted QA after acceptance and incremental phases5–7; explicit full verification/Phase8 remains separate. This scoped rule takes precedence over ordinary implementation/checkpoint chaining below. V1 and unsupported tasks retain installed rules. `Phase X` / `-all` follows `phase-x-maintenance.md`; manual only, never autopilot/Dreaming.

# Validation Profiles

## Purpose

Validation Profiles define what AI System script bundles run after `.systems/ai/core/validation-routing.md` establishes that scripts are applicable.

Default `.systems/scripts/validate-ai-system` with no arguments is the `standard` profile. It is not a default implementation command and never substitutes for semantic or product QA.

Profiles may reduce script execution time, but they must not change source-of-truth order, privacy, owner-approved writes, evidence requirements, semantic QA, product checks, contract compliance, Knowledge Capture Gate, End-of-Task Capture, final acceptance, CI behavior, or commit readiness.

## Profiles

| Profile | Intended use | Final validation evidence |
| --- | --- | --- |
| `full` | Applicable checkpoint validation, major distillation, final system verification, CI, release confidence, and high-impact AI System contract changes | supporting evidence, unless smoke tests are skipped |
| `standard` | Applicable ordinary AI System artifact quality or system-maintenance closure | supporting evidence only |
| `scoped` | Explicit targeted artifact validators after semantic review | supporting evidence only |
| `fast` | Optional quick contract sanity check outside active implementation writes | supporting evidence only |

## Script Interface

`.systems/scripts/validate-ai-system` supports:

- no arguments: same as `--profile standard`;
- `--profile full`;
- `--profile standard`;
- `--profile scoped --checks <check-a,check-b>`;
- `--profile fast`;
- `--explain` with any profile.

`--checks` is valid only with `--profile scoped`. Scoped checks must be explicit existing script basenames such as `check-personal-ops`; automatic changed-file inference is intentionally out of scope for v1.

`--explain` reports the selected profile, smoke-test behavior, final-evidence eligibility, and explicit scoped checks.

Every completed invocation emits a final machine-readable marker:
`AI_SYSTEM_VALIDATION_RESULT profile=<profile> status=<completed|failed> exit_code=<n> supporting_only=true ...`.
This marker is completion evidence for the script run, not a semantic PASS or final acceptance. For checkpoint,
final-system, or upstream-update evidence, pass `--evidence-file <existing-runtime-directory>/<record>.md`.
The evidence record includes the profile, scope, baseline, checks run or skipped, smoke status, exit code, and residual
risk; it explicitly records that script evidence is `supporting-only` and that the final verdict is not issued by the
script. The evidence path must remain outside `.systems/**` and is never created by a routine implementation write.

## Source-Bound Integrity And Observability

The runner emits one start, per-check progress and exactly one completion marker with a unique
run ID. Evidence records actual `not-started`, `started`, `completed`, `failed`, `timeout` or
`interrupted` states, source fingerprints, coverage, parent/child monotonic timing and an
environment fingerprint. `--timeout-seconds <n>` bounds only this run; cleanup targets its
own child process groups. A pending or interrupted run never inherits completed smoke status.

`--evidence-file` requires an existing local runtime or non-repository output directory.
Foreign repositories, product paths, tracked/deleted-tracked files, symlink parents and
existing destinations are rejected. Publication is atomic and no-clobber, with parent identity
rechecked. Use a new evidence filename for every retry; do not replace prior failure evidence.

`--profile scoped --checks ... --scope-manifest <json>` uses `validation-dependencies.json`.
The manifest contains `scope_contract: 1`, `workspace`, `owned_root`, all `inputs` with hashes,
`required_checks`, `semantic_evidence` and `privacy_evidence` path/hash objects, and
`product_source_digest`. Canonical capture-state or block-checkpoint namespaces are supported;
unmapped consumers require full validation. Inputs and evidence are rechecked after execution.
No manifest means iteration-only, not a checkpoint coverage claim. Checkers receive explicit
`--owned-root` and never infer the owner from a directory name or crawl nested repositories.

Smoke suites are isolated transactions with owned setup, mutation, assertions and cleanup.
Negative tests require declared exit codes and cause-specific diagnostics; 126/127, signals,
missing modules and permissions failures do not count. Each suite checks complete negative
coverage before its completion marker. Test bodies retain their direct positive assertions.

`report-validation-comparison` requires at least three complete frozen runs per variant, equal
test coverage and environment, and no within-variant source drift. Wall duration and child
attribution are reported separately, never added. Population changes invalidate speedup claims.

## Standard And Full

### Explicit Iteration Reuse

`execution-efficiency.md` defines `--reuse-evidence <run> --reuse-key-file <owner-only-key>`.
Only authenticated successful completed records with revalidated complete inputs may reuse.
Unknown dependencies and runtime reference closures execute fresh. Per-check execution is
`executed`, `reused` or `invalidated`, with reason and source run. A reused duration is zero
new child execution, not the original test cost. Historical evidence is not current acceptance.
Full/CI/updater runs remain fresh; the runner rejects reuse with the full profile or in CI.
`--extra-product-file <path>` explicitly includes newly approved untracked product files in
isolated full-smoke fixtures; it does not admit private runtime or change test membership.

`standard` runs the complete AI System validator chain except embedded `check-validator-smoke-tests`. Use it only when validation routing marks the broad chain applicable.

`full` runs the complete standard chain and `check-validator-smoke-tests`. Use it after semantic current-diff review for checkpoint validation, major distillation, final system verification, CI, release confidence, upstream updates, and high-impact system changes. Classify impact by changed behavior, risk, and cross-contract reach, not by a file path alone. A local typo in a core document is not automatically high-impact; a small-looking approval, privacy, schema, security, or routing change can be.

CI and `.systems/scripts/update-from-upstream` must call `.systems/scripts/validate-ai-system --profile full` explicitly.

If `AI_SYSTEM_SKIP_SMOKE_TESTS=1` is used with `--profile full`, the result is not eligible for final validation evidence unless the owner explicitly accepts the residual risk.

## Scoped And Fast

`scoped` runs shared diff/privacy checks plus explicitly named validators once each. It does not automatically run the entire `fast` bundle. Use it after semantic artifact review for targeted validation. It must not be described as a quality verdict or as sufficient before commit or push.

`fast` runs diff, privacy-boundary, and required-artifact sanity checks. Do not run it automatically during ordinary implementation. It is not a quality verdict. The privacy-boundary check is path-oriented; it is not a full content or secret scan.

## Personal Ops Targeted Default

Routine native V3 daily check-in writes use targeted validation by default:

- `AI_SYSTEM_WORKSPACE_HOME=<workspace-path> .systems/scripts/check-personal-ops` for check-in-only writes;
- add `AI_SYSTEM_WORKSPACE_HOME=<workspace-path> .systems/scripts/check-task-management` when the same approved write creates or updates TaskNotes;
- use `.systems/scripts/sync-personal-ops-check-ins-v3 --workspace <workspace-path> --status-only` to inspect freshness without regenerating indexes.

This targeted route follows semantic and data review. It is not a quality verdict for repository changes. Use `standard` or `full` only when validation routing marks the broad profile applicable. Targeted validation cannot skip required schema, privacy, owner-approval, TaskForge, or explicit route checks.

## Safety Boundaries

Validation profiles must not:

- run broad AI System validation solely because AI System governs an ordinary implementation;
- run before semantic QA, findings-first review, and applicable product checks;
- derive `PASS` from green scripts alone;
- make `fast` or `scoped` sufficient before commit or push by default;
- make `standard` replace `full` for a full-required gate;
- let skipped smoke tests count as PASS or final validation evidence;
- weaken CI, privacy, evidence, contract compliance, Knowledge Capture Gate, owner approval, or final acceptance.

When scripts are used, record the semantic QA result, findings/blockers, product checks, script applicability, targeted commands, `Script evidence role: supporting-only`, final verdict, skipped checks, and residual risk.


## Intent brief supporting verification

check-intent-to-execution-brief runs standalone synthetic profile/corpus regressions in standard/full. With --workflow-root and explicit --expected-head it purely inspects accepted installed source capability; no writes, install, native proof or owner consent. Full source gates include smoke. Native25-case paired original-input review is separate required implementation evidence; green scripts are supporting-only. Existing execution-mode fixed14 contract1/readiness2/QA2/Capture2 unchanged.


## Concurrent validation inputs

Follow `validation-concurrency.md`: automatic product-v1 stability guards run even without timing. Select actual runtime inputs with the owning project/scope manifest or repeatable `--validation-input-root`. Unrelated runtime writes are not product drift; changed assessed inputs never grant successful evidence. No automatic retry or historical QA rewrite.
