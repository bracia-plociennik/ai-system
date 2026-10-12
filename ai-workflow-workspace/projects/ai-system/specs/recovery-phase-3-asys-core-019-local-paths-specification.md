# ASYS-CORE-019-local-paths Specification

Goal: deliver the approved CR-011 portable root handling with resolved transaction identity. Scope: CR-011 architecture exact write set. Out of scope: Capture repairs and real runtime/data adoption. Risk: high; explicit approval in decisions/2026-10-09-cr-011-owner-scope.md covers local implementation and formal QA. Inputs: current context/analysis, architecture/QA, plan/QA and task index.

## Plan Quality Contract

- Plan classification: implementation-capable
- DoD source: decisions/2026-10-09-cr-011-owner-scope.md; acceptance list below
- Testable DoD / acceptance conditions: all six numbered acceptance conditions; byte preservation and version/drift rejection measured by fixture hashes and call traces
- Artifact QA route: phase-3-spec-qa
- Artifact QA trigger: after this scoped artifact and inputs are complete
- Implementation Quality Closure route: phase-5-quality
- Required verification: synthetic resolver/entrypoint/ledger integration, negative and crash regressions, existing suites and fresh full product validation
- Quality-ready criteria: current formal QA, no blockers, all DoD rows proven
- Owner opt-out: none
- Not-applicable reason: none
- Blocking decision: none
- Next route: paired artifact QA then next valid phase

## Delivery Constraints

- Mode: auto-unbounded
- Deadline: none
- Timezone: Europe/Warsaw
- Time budget: none
- Must-have outcome: six acceptance conditions below
- Should-have scope: readable portability docs and examples
- Stretch scope: none
- Explicitly deferred scope: old Capture repair, real Mac run, live config adoption, push/publication/update and Phase 8
- Quality floor: semantic/full Phase 5 plus owner/alias/history safety
- Cutline rule: defer only external rollout; never weaken acceptance/tests
- Overrun checkpoint: queue changed scope or unsafe action, stop affected work
- Owner override: Auto and local commits explicitly approved

## Acceptance Conditions

1. absolute/tilde/HOME/AI_SYSTEM_HOME/workspace expressions with deterministic bases and fail-closed invalid inputs.
2. tasks and project preflight use shared resolver; tasks work without UI; missing repo stays unavailable/pending without writes.
3. Work Evidence resolves copies only, preserves raw bytes/hashes, owner boundaries and ordered roots.
4. V2 preparation binds resolved path context; apply/recover/dedup reject drift before canonical writes; V1 literal history supported.
5. existing and new synthetic positive/negative/crash/version/relocation checks pass; full product validation with smoke passes.
6. Phase 5 proves implementation correctness, preserved unrelated history and readiness for the scoped local commit/capture; Phase 6–7 must then prove accepted distillation, actual commit and checkpoint before implementation-range closure; no push or real adoption.

## Implementation Steps And Field Contract

local_paths.resolve_path returns absolute lexical paths without following links and accepts only allowlisted expansion. For CLI relative compatibility pass explicit caller CWD/base; for repo links/task config use selected workspace base. For Work Evidence roots relative bare strings remain invalid. Selected workspace argument overrides ambient workspace variable. Base variables cannot contain substitutions. Validate existing symlink components before normalization. Diagnostics never expose unvalidated secret/source values.

validate_config resolves source_roots/ledger_roots on a deep copy, then existing validation, duplicate normalized roots and owner containment. Raw configuration and config/request digests unchanged. Ledger.check_loaded verifies raw hashes plus resolved path context, freezing workspace from construction.

New transaction schema 2 requires exactly old manifest fields plus path_context. That object has schema_version=1, workspace absolute, source_roots dict with valid aliases and absolute values, ledger_roots nonempty ordered list of absolute values. Context is in the manifest hash. V1 has exactly old keys and literal absolute configuration; apply refuses any root expression. prepare's duplicate branch checks manifest shape and context before returning existing approval. Apply checks context before loading committed records/writing canonical records; recovery uses apply. committed() validates supported manifest/context shape and original bytes/hash/chain, but does not compare historical host equality. Unknown context/transaction versions and extra keys reject. No rewrites/backfills or relaxations of existing locks/config/registry/candidate/chain/XLSX checks.

Tax allowed_workspaces and init workspace/roots use the resolver; tax relative source_roots keep existing semantics. Project preflight catches resolver errors, keeps unavailable sources blocked for execution with pending availability, and does not create sources. Documentation explicitly separates optional TaskForge UI from Markdown store configuration; supported fields and rollback/adoption boundaries are listed.

## Tests / Edge Cases

Injected HOME/system/workspace context on synthetic Mac/VPS roots; tilde/spaces/custom installation/CWD; literal compatibility; missing/unknown/recursive/malformed expansions; symlink parent/root; owner escape/duplicate canonical roots; dry-run and synthetic task create/dedup without UI; project explicit/link equality and missing repo; V1 literal and dynamic rejection; V2 apply idempotency/crash/recover; context tamper/environment drift before/during writes including subprocess reload; historical immutable manifest/revision hashes and relocated integrity; raw init request unchanged; existing tax/XLSX/restore regressions. Unit and existing full product checks use only fixtures.

## Implementation Gate

Enter Phase 4 only with this Spec QA PASS, current isolated source baseline, pending-quality capture record, complete slice plan and owner scope. Review all source changes; do not stage unrelated runtime. Re-QA after local commit because target-source V3 equivalence is unsupported. Full validation gates remain fresh.

## Stage Acceptance Clarification

This recovery preserves the earlier artifacts unchanged. Phase 5 cannot require its dependent Phase 6–7 outputs as already complete. Stage six proves commit/capture readiness at Quality; the implementation-range closure separately requires actual commit and accepted capture/checkpoint. No owner scope, implementation or quality-floor reduction. Semantic planning re-review completed against the exact changed stage dependency and all other acceptance conditions.
