# Ledger OSNR Regression Fix
Task: WEP-LEDGER-002-transactions. Finding: WEP-LEDGER-002-P2-001.
DoD source: accepted selective TaskNote/checkpoint adapter and read-only source contract.
Input: quality/phase-5-wep-ledger-002-transactions-quality.md run002 FAIL.
Retry count: 1. Maximum retry count: 2. Limit reached: no.

## Diagnosis And Scoped Fix
Standard TaskNotes use a Unicode dash between O/S/N/R and descriptive labels.
The prior ASCII-only regex silently dropped all four fields. New regression
failed before repair: 41 executions, one failure; osnr_hints was empty.
Change: support colon, hyphen, en dash and em dash without allowing whitespace
to consume subsequent lines. Duplicate labels remain unresolved, not guessed.
No status/time inference, source writes, Raw/Dump inclusion or new scope.
Files: work_evidence_ledger.py and test_work_evidence_ledger.py only.

## Verification
Full ledger test file after fix: 41 executions OK, includes inherited contract tests.
Contract test file separately: 13 executions OK. git diff --check exit0.
Current-state re-review covers the entire ledger, CLI wrappers, approval boundary,
manifest/revision integrity, source exclusions, safe paths, session allocations,
period arithmetic, crash recovery and read-only preview; not only changed lines.
Ready to return to phase-5-quality; this fix loop grants no task PASS.

## Owner Decision Checkpoint
Clear within existing owner-approved implementation scope; dependency approval
for the following XLSX task remains pending and is not waived by this fix.
## Optional Knowledge Capture
Required task002 technical distillation; retain failing and successful evidence.
