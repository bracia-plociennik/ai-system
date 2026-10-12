# WEP-DOCS-004 Implementation
Source and DoD source: specs/phase-3-wep-docs-004-replay-kit-specification.md.
Scope: explicit-source, owner-approved derivative kits and human replay gate.
## Implementation Slice Plan
| slice id | goal | expected files/areas | acceptance check | evidence required | status |
| --- | --- | --- | --- | --- | --- |
| docs-1 | Complete procedure and safe assembler | work_evidence_docs.py, procedure template | required fields and version/hash binding | contract/private-source tests | completed |
| docs-2 | Independent human replay gate | module and documentation CLI | no automated/assisted/stale success | state and no-write traces | completed |
| docs-3 | Scoped regression and artifact review | tests and private QA | normal/failing kit trace, clear checklist | tests and full review | completed |
Stop on unresolved source, privacy, approval, scope or human-evidence conflict.
## Instruction Refresh
Targeted current scope after full continuity refresh: AGENTS/operating-model,
risk/permissions, phase4/slicing, full-QA/quality review, current architecture,
plan, spec, index and implementation authority reviewed. Baseline bcd1e0d,
only approved untracked product modules001-003, private evidence writes.
## Delivery Constraints
Owner-opt-out: no deadline/timebox, full DoD/privacy/QA protected.
## Distillation State
Work ID: WEP-DOCS-004-replay-kit. State: pending-quality.
State record path: distillations/wep-docs-004-state.md.
## Model Recommendation
Workhorse high reasoning; privacy and false-reproducibility risk; Blocking: no.
## Owner Decision Checkpoint
Clear for synthetic implementation; human pilot evidence remains owner-supplied.
## Optional Knowledge Capture
Required phase6 after Quality; no Codex memory or public knowledge writes.

## Slice Execution Evidence
docs-1: complete procedure schema, explicit approved derivatives, escaped Markdown,
source/config/registry/work revision hashes; identity.json exposes exact kit hash.
docs-2: consent/role/independence, all assertions, signed evidence hash and separate
owner verification; timestamps ordered; persisted kit bytes and file set checked.
Partial/tampered kit cannot produce success. Synthetic success is only a fixture.
docs-3: ten unique docs cases; full work-evidence suite80 executions exit0.
Initial full test exit1: directory passed file-only safe_path exists guard;
diagnosed unsupported-source, corrected to validated directory path plus is_dir.
Retest80 exit0. No protected test weakened or scope expanded.
Manual normal trace: documented kit9e2df2fd..., all required sections inspected.
Failure trace: owner-help -> independent-human-required and all files unchanged.
Full current module/CLI/template/test review: approved text only, no source-body
copy, no hidden execution/network, immutable same-version writes, changed source
or signed proof blocked, owner verification is attestation not signature crypto.
Real human replay is not performed; it remains required by the pilot scope.
No changes to completed001-003 product sources. Ready for phase5 task Quality.
Full continuity refresh after compaction: current root/nested AGENTS, operating,
risk/permissions, workflow, phase4/5, DoD/slicing/delivery, quality/full-QA,
response/compliance/injection, current architecture/plan/spec/approval/status.
Baseline bcd1e0d; no drift except acknowledged future stale planning QA.
