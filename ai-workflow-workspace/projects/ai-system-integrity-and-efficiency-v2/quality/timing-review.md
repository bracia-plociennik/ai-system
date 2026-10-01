# Frozen Timing And Population Review

## Method
Three complete full-profile runs per variant, alternated monolithic/isolated, synthetic tracked product copies only. Both use current strict negative assertions, the same 220 negative identities, identical seven case bodies and the same 15-test regression body. The only benchmark source difference is all-suite orchestration: one temporary root versus one root per domain.

The baseline is not the old weaker validator. It is the corrected current product with monolithic orchestration retained solely as a frozen comparison fixture. The first pre-fix failed benchmark is excluded and retained as benchmark-rejected-01.

## Observed Result
- Monolithic mean wall: 198.2723 seconds; sample standard deviation: 10.6764 seconds.
- Isolated mean wall: 228.4555 seconds; sample standard deviation: 13.1668 seconds.
- Isolated mean is approximately 15.22 percent slower in this sample.
- Summed child attribution: 197.9151 versus 228.1708 seconds; these are not added to wall time.
- All six runs completed with exit 0 and complete smoke state.
- Equal source-bound coverage digest: 0875e3342781e97753a8d1b652bff2a1ffb96200c0ec32a6682a0161e77587dd.
- No within-variant source/environment/coverage drift.

## Interpretation And Disposition
No full-suite speedup claim. Isolation adds setup/copy/process overhead and removes shared-fixture contamination; the approved task requested transaction isolation and trustworthy equivalence, not a lower full-profile timing threshold. Retain isolation as an integrity improvement and surface its measured cost for final owner review.

Ordinary-work efficiency comes from correct selective discovery, bounded recovery and complete runtime-only scoped validation, not from weakening full-required CI/updater/final integration. Future optimization must preserve this population and safety evidence.

## Limitations
Three repetitions are a small local sample. Foreground load, cache and filesystem noise were not controlled as a laboratory benchmark. This is supporting measurement, not independent performance acceptance, a semantic verdict or proof of a universal slowdown/speedup.
