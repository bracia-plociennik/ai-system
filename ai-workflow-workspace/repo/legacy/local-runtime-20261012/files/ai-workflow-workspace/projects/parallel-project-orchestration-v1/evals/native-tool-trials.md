# Native Tool Trials

- Date: 2026-10-03
- Baseline: bcd1e0dcb9b9b2def6afec9636a72ea058a79ca7
- Approved scope: synthetic read-only verification; no external CLI model sessions, private repositories or recursive delegation
- Shared DoD: unique IDs, nonnegative integer minutes, exact expected sums; coordinator verifies returned evidence against the same two JSON inputs

## Results And Tool Identities

| Mode | Unit | Attempt | Native agent | Sum | Findings | Termination |
| --- | --- | --- | --- | --- | --- | --- |
| linear | sum-a | linear-clean-a-02 | 01a1032b-61f3-79d1-af89-3a89fa773ecb | 70 | none | closed after completion |
| linear | sum-b | linear-clean-b-02 | 01a1032b-ba0b-77f3-bee4-20c5fa890751 | 80 | none | closed after completion |
| parallel | sum-a | parallel-a-01 | 01a1032a-eab2-7b61-8f82-d3b85320d480 | 70 | none | closed after completion |
| parallel | sum-b | parallel-b-01 | 01a1032a-eb6f-7920-a15e-cd96318bf018 | 80 | none | closed after completion |

Evidence inputs: `evals/input-a.json`, `evals/input-b.json`. Native messages returned both expected sums; coordinator independently read the input files and checked identical definitions. Both modes reached the same correct bounded result with no writes. The parallel wave chose two agents because it had two independent read-only units; this is not a product cap.

## Timing Limits

- Linear measured spawn/wait/close cycle: 46.669 seconds.
- Parallel observed spawn/result-collection cycle: 30.514 seconds; includes coordinator collection delay between the first result and the final wait.
- These are one-sample native-tool observations, not whole-project time-to-integrated-quality measurements or a general speedup claim. Background implementation activity, model/service variation, warm context, different result lengths and collection delay confound comparison. No resource-cost conclusion is supported.
- The initial exploratory linear pair (`linear-a-01`, `linear-b-01`) also returned 70/80 but included unrelated coordinator work; it is excluded from timing comparison.

## Behavioral And Failure Evidence

The focused reducer/CLI suite separately tests more than three slots, cyclic dependencies, overlap despite different files, rejected unsafe paths/symlinks, stale manifest/output/attempts, cancellation retaining capacity until confirmed termination, replay prevention and linear Workflow fallback. Native trials establish the current spawn/wait/close adapter path and coordinator reception on synthetic data, not real client write isolation, production safety, injected tool failures or interoperability with the future Workflow contract.

No formal project PASS is issued by a worker message or this timing record. Whole-scope Phase 5 review evaluates the integrated code, contracts, failures and evidence.
