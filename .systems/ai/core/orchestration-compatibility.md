# Orchestration Compatibility

## Authority And Version

AI System owns intent and its nearest-owner coordination state; installed local AI Workflow owns project execution, phases, risk and technical capture. One coordinator owns all shared routers/index. No recursive delegation or duplicate agent pools.

The AI System original contract-1 reducer remains inspection-only. Strict compatibility uses explicit contract 2 unit access sets. Workflow schema 1 is mapped field-by-field, not accepted as an AI System contract-1 run. Missing task identities/read sets are not silently inferred from legacy metadata.

Use `check-orchestration-compatibility --workflow-root <installed-local-root>` to check the complete six-source capability population. Source-verified protocol metadata is not a verified native backend. This release has no verified native enforcement adapter: `parallel_write: false`, `execution_authorized: false`, serial fallback even if a capability claims verified isolation/capacity. A local draft is advisory evidence, not installation or approval. Malformed/stale capability fails closed.

## Access And Parent Gates

Each new unit has task/package/slice identity, observable DoD, dependencies, normalized `read_set`/`write_set`, and typed shared/exclusive resource claims. Check read/write as well as write/write overlaps and physical aliases; resource names refer to the same actual resource across both systems. Unknown ownership blocks execution.

`allocate` produces proposals only. Verified free capacity determines worker count dynamically with no fixed product cap. Local parent-task checkpoint slots are a different constraint, not a worker limit. The inspection CLI accepts no declared ready dependency IDs as execution evidence. For same-task dependencies, the coordinator calls `verify_delivery` on an actual immutable separate copy, full relevant files/modes/directory/deletion coverage, after rechecking the producer receipt. Different-task dependencies require current local owning Quality/capture/checkpoint gates. Neither an ID nor accepted metadata alone passes these gates.

## Inventory And Integration

`inventory` covers all regular files, modes, empty directories and deletions through exact before/after comparison. Symlinks, nested Git roots, special files, sensitive filenames and inventories over 64MB fail closed, without hidden exclusions. Frozen inventories and required check-file hashes belong to the private coordinator preflight; receipt hashes are consistency seals, not hostile-host authenticity.

`seal_result` requires observed termination and exact approved writes; `verify_result` recomputes actual output/check hashes. The ledger binds results to the physically observed reserved worker root and its preflight. Worker messages and supplied booleans are not native tool evidence; the coordinator must actually observe termination through the applicable backend before calling these helpers.

Submitted, accepted, integrated and formal task PASS are different. Acceptance requires real intent/diff/tests/privacy review; review fields record that review, not perform it. `integration_prepare` freezes current destination and intended state and stops on baseline conflicts. It does not copy, merge or roll back files. Separately approved integration is followed by `integration_confirm`, which recomputes the complete destination identity/inventory and output receipt. Integrated metadata is supporting-only, not formal PASS. The coordinator still performs whole-task QA.

## Durable Recovery

`Ledger` is a cooperative local CAS helper, not a launcher or distributed/security lock. Store one private ledger under the nearest-owner `orchestration/runs/<run-id>/ledger.json`, never in a managed project repo. Its parent must already exist in the approved namespace. The coordinator alone calls metadata writes inside an approved scope; the public inspection CLI has no write command.

Expected revision, coordinator/root identity, event-chain hashes, reservation-state hash, exclusive lock, fsync and atomic replacement preserve concurrent-update/crash evidence. Never automatically remove an existing lock. A failed persistence acknowledgement retains its lock and must be reconciled by a separately reviewed recovery action. Do not auto-replay.

Reservations retain attempts and resource claims through running/submitted/accepted/integrating states. Unknown effects block new reservations. Fresh known-original-or-intended inventories and observed termination are needed to abandon an interrupted integration; unresolved/unrecognized effects or pre-integration unknown outcomes require manual recovery. No rollback, forced termination, discarded history or stale-result promotion occurs automatically.

## Capture And Git

Use `capture_parity.py` through `check-distillation-state` and the compatibility inventory CLI. Entire canonical owning collections participate in duplicate detection, including invalid siblings. Schema 1 is historical/advisory and never provides current QA PASS. New formal schema 2 binds work/project/task coverage, source HEAD, actual formal implementation QA and all input hashes, and one uniquely claimed accepted owning distillation. It does not widen namespaces or rewrite history.

For opt-in schema 3, QA binding must be recomputed through `qa_source_binding.py`; otherwise use fresh schema-2 QA. Aggregated AI System work IDs explicitly list all owning task QA; they are not guessed to be Workflow task IDs.

`parent_completion` consumes a current fingerprinted approved unit plan, the durable ledger and the same whole owning capture collection. Exact unit/task coverage, every actual integrated destination and accepted capture must remain current. Invalid siblings and physical aliases of distillation files participate in duplicate detection. Its result is readiness for the local parent gate, never formal PASS; local Workflow still owns that gate.

Future phase commits follow `phase-commit-policy.md`. Explicit no-commit wins. Complete immutable target snapshots and actual Git/tree/index/live/dependency evidence are required for source-equivalence; unsupported proofs require fresh QA. Current artifact closure remains separate.

## Quality And Limits

Semantic review, producer-consumer audit, adversarial recovery and actual local fixtures precede supporting-only validators. No script alone creates PASS. Native enforcement/capacity verification remains unavailable and no real parallel-write or speedup claim follows. Worktree alone is not a sandbox. Test benchmarks must include integration/rework/quality, at least three paired samples and resource observations before broader claims.

Do not mutate counterpart sources, nested installations, history, status, approvals, memory, TaskNotes, commit or push from inspection. Scope expansion follows local change-request and owner gates.
