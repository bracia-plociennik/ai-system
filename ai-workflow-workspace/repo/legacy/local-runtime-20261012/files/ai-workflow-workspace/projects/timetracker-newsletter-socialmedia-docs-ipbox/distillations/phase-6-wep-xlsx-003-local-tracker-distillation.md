# WEP-XLSX-003 Distillation
## Result
Seven-sheet local workbook and hash-bound manual intake with immutable revisions,
input/output snapshots and exact-once recovery. CLI writes require explicit approval.
## Problems And Decisions
A stale derived view may be refreshed only if protected content and prior receipts
are intact. Pre-import backup restoration cannot drop a committed import receipt.
Acknowledged manual rows are immutable history; corrections use new rows and base revision.
Pending sidecar is compared against the immutable approved input workbook before apply.
## Reusable Rules
Reserve IDs once, bind canonical and projection recovery to the same manifest.
Store both input and generated output snapshots; check hashes before restoration.
Check snapshot bytes against the current file hash, not a later read alone.
Use exact pinned dependency hashes; active XML/cells/relationships are rejected.
Domain scope remains unknown until an explicit canonical attribution exists.
## Evidence
quality/phase-5-wep-xlsx-003-local-tracker-quality.md current run001.
70 successful scoped test executions; 16 XLSX cases; seven-sheet visual review.
## Memory
memory-in-repo-memory: true
Project-only technical capture; no Codex memory or public insight writes.
## Owner Decision Checkpoint
Clear for synthetic adapter; real usability and independent human replay remain gated.
## Optional Knowledge Capture
Required project capture completed. Checkpoint cadence now reached for001-003.
