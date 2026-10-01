# Smoke Transactions

`negative-expectations.json` declares exact suite ownership, rejection exit and diagnostic
for every negative case. Test bodies retain their original setup, mutation, direct assertions
and cleanup in `check-validator-smoke-tests`; all mode runs isolated per-domain transactions.
Changes require completeness checks and baseline/candidate equivalence review.
