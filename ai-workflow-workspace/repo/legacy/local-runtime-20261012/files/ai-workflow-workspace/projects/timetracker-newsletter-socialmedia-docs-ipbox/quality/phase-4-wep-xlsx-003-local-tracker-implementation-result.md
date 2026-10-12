# WEP-XLSX-003 Implementation
Source and DoD source: specs/phase-3-wep-xlsx-003-local-tracker-specification.md and refreshed Spec QA run002.
Scope: pinned isolated adapter, seven-sheet projection, manual intake, conflicts, resumable projection and synthetic verification.
## Implementation Slice Plan
| slice id | goal | expected files/areas | acceptance check | evidence required | status |
| --- | --- | --- | --- | --- | --- |
| xlsx-1 | Safe workbook codec and projection | work_evidence_xlsx.py | bounded XML/ZIP and seven typed sheets | unit/security traces | completed |
| xlsx-2 | Stable manual transaction protocol | adapter and CLI | roundtrip/new/correct/void/recovery count once | integration failpoints | completed |
| xlsx-3 | Artifact and quality verification | synthetic tests, private QA | visual review every sheet and current-state review | saved workbook renders and tests | completed |
Stop on changed scope, unsafe source/approval or missing evidence; no real activation.
## Instruction Refresh
Performed-full after compaction: root/nested AGENTS, operating-model/workflow, risk/permissions, slicing/delivery/dependencies, phase4/SpecQA/full-QA/quality review, current architecture/plan/index/spec/decisions and source reviewed.
Baseline bcd1e0d with explicit untracked001/002 files; no unrelated edits. Dependency-pending state superseded by explicit approval.
## Delivery Constraints
Owner-opt-out, no deadline/timebox. Quality floor: complete DoD/privacy/failure evidence.
## Distillation State
Work ID: WEP-XLSX-003-local-tracker. State: pending-quality.
State record path: distillations/wep-xlsx-003-state.md.
## Model Recommendation
Workhorse high reasoning; high data-integrity/privacy impact; Blocking: no.
## Owner Decision Checkpoint
State clear for synthetic implementation; actual runtime remains gated.
## Optional Knowledge Capture
Required; phase6 after Quality, then checkpoint cadence. No Codex memory updates.

## Slice Execution Evidence
xlsx-1: exact dependency versions installed with pip --require-hashes --only-binary=:all:
in /private/tmp/wep-xlsx-venv. Initial sandbox DNS failure retained as unavailable
network evidence; approved isolated retry exited0. Probe exact versions and
DEFUSEDXML=True. No global Python or production dependency change.
Seven sheets contain typed, literal values, explicit time basis/coverage and stable IDs.
Domain scope is Not recorded because entry v1 has no explicit domain attribution;
no ambiguous domain is inferred from a project or title.
xlsx-2: prepare snapshots input; apply validates input backup and pending sidecar
against the approved manifest; corrections/voids retain immutable revisions.
Recovery after canonical and after workbook replacement uses original IDs.
Export preserves manual history/receipts and blocks obsolete pre-import restoration.
Office owner-file lock is checked; other editors must be closed by the operator.
xlsx-3: isolated unittest discovery exited0, 70 executions (includes inherited
base contract tests), 16 XLSX cases. Manual trace: 600 seconds -> revision1 ->
10 actual minutes -> no-new-rows; acknowledged-row edit -> explicit category,
filesystem unchanged. All seven saved-sheet PNGs inspected; Work Entries
full A:L range includes Revision; headers/IDs/units wrap without clipping.
Artifact-tool import inspected seven sheets and found no formula errors.
Files: requirements-xlsx.txt, work_evidence_xlsx.py, work-evidence-xlsx,
test_work_evidence_xlsx.py. Private render scripts/outputs are QA only.
git diff --check exited0; untracked files reviewed directly, not assumed covered
by git diff. Broad release QA remains task009, not claimed here.

## Pre-Quality Failures And Corrections
Initial XLSX tests failed on macOS /var versus /private/var source alias:
resolve configured root before relative-path binding; retest passed.
New regression initially called dict fixture as function (TypeError); corrected
fixture use, no protected assertion weakened. Backup regression initially used
an unexported test helper (AttributeError); imported the actual ledger helper.
Review found stale export, acknowledged-row reuse, missing prepare snapshot,
obsolete backup receipts, snapshot read/hash race and unbound projection sidecar.
All corrected inside xlsx-2 before the first Phase5 verdict; explicit negative
tests added. Latest full scoped regression is 70/70 executions successful.
Residual risk: Office lock heuristic cannot detect every third-party editor;
same-volume atomic replacement assumed. Owner usability/replay remains task010.
Next route: phase-5-quality, not task completion from tests alone.
