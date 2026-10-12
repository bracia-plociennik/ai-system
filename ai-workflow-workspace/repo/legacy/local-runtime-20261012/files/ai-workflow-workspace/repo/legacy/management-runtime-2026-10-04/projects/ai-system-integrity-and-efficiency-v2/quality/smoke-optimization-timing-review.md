# Smoke Optimization Timing Review

## Method
Two retained nine-run matrices, all full-profile repetitions sequential between variants. The first copy-only hypothesis did not clear the monolithic warning and is excluded from current acceptance. The second matrix uses three complete repetitions each for old sequential isolation, corrected monolithic reference and optimized two-worker isolation. Every current variant contains the same 20-test integrity body, seven domain-body hashes and 220 exact negative contracts. Sources are frozen within each variant; environment and coverage digests match.

## Current Measurement
| Variant | Mean wall seconds | Sample standard deviation | Mean child attribution seconds |
| --- | --- | --- | --- |
| Old sequential isolated | 225.5908 | 2.7687 | 225.3369 |
| Monolithic reference | 201.4699 | 6.7067 | 201.2186 |
| Optimized isolated, two workers | 169.9906 | 19.0906 | 169.7330 |

The optimized mean is 24.65 percent lower than old isolation and 15.62 percent lower than monolithic in this local sample. Wall and child attribution are not added. All nine records completed with exit 0 and complete full smoke state; no failed, partial or skipped run establishes this comparison.

## Disposition
P2-PERF-001 is resolved for this measured, approved setup: independent transaction roots and unchanged coverage are retained, and the current mean meets the no-worse-than-monolithic DoD. This is not a universal speed guarantee. Correctness and authority acceptance also require semantic review, fixture/failure tests, producer-consumer audit and current artifact gates, not these green timing records alone.

## Freshness And Limits
- Candidate source digest: dee21660d7935759ac79da9a9577947e8b66c5140e7e5badd9134c560527a3ed.
- Coverage digest: d0ebb4dd4b8512ed042fb9aca062d039d07e749e99e800a3c953ffa50bc45607.
- Current worktree product file hashes/source digest match all optimized frozen records and the actual current-worktree full execution. Synthetic fixture Git HEADs and the assessed real HEAD are recorded separately; they are not claimed to be identical.
- Existing 15 integrity cases remain, plus five copy/scheduling cases. No old assertion/mutation/restore body changed.
- Two-worker scheduling is the approved experimental treatment, not an environmental equality claim about identical execution scheduling.
- Three repetitions are a small local sample. Machine load/cache are not laboratory-controlled; standard deviations and prior unsuccessful hypothesis are disclosed.
- No private runtime pilot, external model eval, publication or management rollout.
