# WEP-LEDGER-002 Implementation
Source: refreshed specs/phase-3-wep-ledger-002-transactions-specification.md.
DoD source: accepted plan task002; authorization in implementation decision.
## Implementation Slice Plan
| slice id | goal | expected files/areas | acceptance check | evidence required | status |
| --- | --- | --- | --- | --- | --- |
| 002a | committed-manifest revision store | work_evidence_ledger.py | crash/retry/revision invariants | tests and manual trace | completed |
| 002b | preview/prepare/apply/recover/rebuild CLI | work-evidence-* | read-only preview, stale approval, lock | CLI and failure tests | completed |
| 002c | bounded source candidates and time coverage | ledger helpers/tests | no inferred time, period/DST coverage | integration tests | completed |
Scope: only local approved input records and isolated fixtures. Stop on missing
facts, unsafe actions or changed input versions. No source or TaskNote mutations.
Delivery: owner-opt-out; no time limits; full DoD/privacy/Quality protected.
Instruction baseline current: full refresh plus task001 implementation/Quality
and distilled decisions. Baseline HEAD bcd1e0dcb9b9b2def6afec9636a72ea058a79ca7.
Distillation State: pending-quality; distillations/wep-ledger-002-state.md.
## Slice Execution Evidence
40 test executions passed (including inherited contract tests), git diff --check
exit0. Crash before manifest leaves zero visible new records; crash after
manifest leaves one record; recovery never adds time twice. Correction/void
retain three immutable versions and change totals exactly once. Normal/failure
traces are in the synthetic suite and current Quality.
Pre-Quality corrections: apply revalidates complete state, commit chain binds
approved manifest and record hashes, session corrections use current allocation
budget, loaded config hash changes fail closed. Full source/tests re-reviewed.
No private sources, TaskNotes, production or history imported.
## Owner Decision Checkpoint
Clear for isolated fixtures; no real roots activated.
## Optional Knowledge Capture
Required technical evidence; defer-to-distillation.
