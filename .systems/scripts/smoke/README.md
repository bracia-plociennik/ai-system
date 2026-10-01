# Smoke Transactions

`negative-expectations.json` declares exact suite ownership, rejection exit and diagnostic
for every negative case. Test bodies retain their original setup, mutation, direct assertions
and cleanup in `check-validator-smoke-tests`; all mode runs isolated per-domain transactions.
Changes require completeness checks and baseline/candidate equivalence review.

`smoke_fixture.py` prepares a complete independent physical copy per domain in one
Python process, avoiding per-file shell process overhead. It preflights the tracked
product inventory and explicit safe extras, preserves bytes/modes/timestamps, and
never uses hard links, shared writable caches or private runtime sources. The suite
case bodies and restore logic remain unchanged.
Full execution schedules at most two independent domains at a time. Both started
transactions are drained before the next pair; any failure stops later domains,
propagates a nonzero result and omits the all-suite completion marker. Domain
output is buffered and printed in deterministic domain order, not interleaved.
No transaction shares a fixture root or writable cache.
