# IEV2-VAL-006-comparable-timing Quality

## Metadata
- Project: ai-system-integrity-and-efficiency-v2
- Task/package ID: IEV2-VAL-006-comparable-timing
- Date: 2026-10-01
- Result: PASS
- QA verification contract: `full-qa-verification-v2`

## Current QA Run
- Run ID: qa-iev2-val-006-comparable-timing-2026-10-01-format-recovery-smoke-optimization
- Artifact kind: implementation-quality
- Project/task identity: ai-system-integrity-and-efficiency-v2:IEV2-VAL-006-comparable-timing
- Assessed source HEAD: 3e8b795821bc46d7d91f6a620d6a3272e8a5cafb
- Assessed worktree digest: 8b0dd6b82a3f928985f9da96b848e05581f7e7f1545d253fa1ad7b51399c1c2c
- Input artifacts: see table
- Verdict: PASS
- Gate Decision: PASS

### Input Artifacts
| Root kind | Relative path | SHA-256 |
| --- | --- | --- |
| approved-target-source | .systems/scripts/check-required-artifacts | 5c5fad09b9cbc82e77f4b35acc6c825b18ad9e98f6cca49d9df0f85f5e8d0fd2 |
| approved-target-source | .systems/scripts/check-validation-profiles | 3deea2250e20a1bb03aeddceb428e5c91077f09f9f6124c6d074e6b3b016d2e7 |
| approved-target-source | .systems/scripts/check-validator-smoke-tests | 9398d7250d0153e5e3c4644351ab109ae857ce48e4bfb6bbb2b64c3fc9a9c28a |
| approved-target-source | .systems/scripts/report-validation-comparison | da46d0196fda417a14b8b8143789564052e889936a583131823bcb115e2d4f50 |
| approved-target-source | .systems/scripts/smoke/README.md | 20030f16a63a04e99b75e51e8313db5785ddeb881fb5f07d7b5118a2a7e2f98c |
| approved-target-source | .systems/scripts/smoke_coverage.py | 0c552c7920a5dfb91b5028996bb540a655dfa4fa6afdb5dffdd8b3864fbe22ae |
| approved-target-source | .systems/scripts/smoke_fixture.py | e50e628ec964d279cdff9af73a73cdd651236c1e8a5b911b81a97eb51f87fea3 |
| approved-target-source | .systems/scripts/tests/README.md | aeaa0708dc3c3bf832947d24c820fc98905f02c16ba687b0beffb6b014077668 |
| approved-target-source | .systems/scripts/tests/test_validation_integrity.py | 8870f4c72c9335d30a5b583c0a97cda8a292c2665e611c5083176c44afb0a2d7 |
| owning-project-evidence | change-requests/2026-10-01-iev2-cr-001-smoke-setup-optimization.md | c7db66f359a3de10ba32cbacafd7afb5690171048df6484781c2e33a383f6a02 |
| owning-project-evidence | implementation/phase-4-iev2-cr-001-smoke-setup-optimization-implementation.md | 6479c9e81cd3bb625764d1badd0ee2eedcd19774e5ed3ce9bf7e39595798102c |
| owning-project-evidence | implementation/phase-4-iev2-val-006-comparable-timing-implementation.md | 09aed9b37d05d0514d5904bf4724e17a00f69a2341a4a058de5ccc095fb5d420 |
| owning-project-evidence | quality/evidence/integrity-full-03.md | 75cbc61a6603b082c0ea192e145349f9a24fd3cec779db7affb103959d170dbb |
| owning-project-evidence | quality/evidence/integrity-tests-07.log | 4f76f32d07378234bac3dfffcdc90a3da9c5138e9e9e6e4c66438cdd5258662e |
| owning-project-evidence | quality/evidence/isolated-1.md | 9947a0440ec513df2db1f1290d9ff730147b0f376f7e89c88deb0a03a4f0a3aa |
| owning-project-evidence | quality/evidence/isolated-2.md | f0d696cbb915867aeaf3ff0fa413568325bd4d636c848466a818bd3a2f1a9fce |
| owning-project-evidence | quality/evidence/isolated-3.md | 291a5d660f905b37672c51136b53c2042d28c6a388278f09beb9c47625822747 |
| owning-project-evidence | quality/evidence/monolithic-1.md | 43d1c532210580e06b5d9870bf320f34767b303ab3795b6ba867a50701d48f02 |
| owning-project-evidence | quality/evidence/monolithic-2.md | c0c9508fa24f5a06c76f3aa49df80672e65c7ae43138933b1b16a37ecd951c29 |
| owning-project-evidence | quality/evidence/monolithic-3.md | d19acfcd191735655be2c039b2a974076ac225b7eb3e7c67cfe09101f51c1527 |
| owning-project-evidence | quality/evidence/smoke-equivalence.json | b22a91df5797405f6b12008fc9c7bdcb83d96597a6242301db35910f22b04371 |
| owning-project-evidence | quality/evidence/smoke-optimization-current-source.json | 439a1f3e1b18dd77f4c1553f5a06473dff0ed196df1b19782e5ef799cfc1aa76 |
| owning-project-evidence | quality/evidence/smoke-optimization-full.md | 08b53c384b0cc353b5fea15e4273c65a34096ea9704b70f2ff4908f920bb8324 |
| owning-project-evidence | quality/evidence/smoke-optimization-tests.log | fd995145caeb65ee3765fb89c518805d7e04c3be3eb0ee9f6e29131de1f61b55 |
| owning-project-evidence | quality/evidence/smoke-optimized/monolithic-to-optimized.json | 8e35b0ec1eca815bb27ae57902defaf614d610ba3d6b78fa175ef8458ed57af1 |
| owning-project-evidence | quality/evidence/smoke-optimized/old-to-optimized.json | 6f0ac9de27fe9d2b5af4cfcaeb09b6e6c6535697e32773ae02fa6bbf562974a1 |
| owning-project-evidence | quality/evidence/smoke-optimized/population.json | fd9b142cfe9a3c7a89e550c49f8ffa642dc8a3573341d0356671ade5b984f32d |
| owning-project-evidence | quality/evidence/timing-comparison.json | 6c84f9eb051677cc0e4bdcd08a05c54070a313fe67235de30a9987d483d6d66f |
| owning-project-evidence | quality/recovery-ledger.md | 853ac42e104acffd3ed80c19379c14ccc7a8298d2ea6f2cd4ef5520def997aac |
| owning-project-evidence | quality/semantic-review.md | b17cdcaad2863f369ab8507527afea1cf221083e7d7002df3b6565a596ce0165 |
| owning-project-evidence | quality/skill-routing-trace.md | c1a9444a3e06cddd25457801fc9b57db3114c2a11fc6dc37cb77b0fe17ad76c7 |
| owning-project-evidence | quality/smoke-optimization-review.md | 2003ab568174aaffc28383665494bf9403ede9d9a390cf01fcc8a6f60302206b |
| owning-project-evidence | quality/smoke-optimization-timing-review.md | dd4d2cb71c41f06ca7bafb09b09fd69928ad633a1e74c95a7b1aeaad761ac43f |
| owning-project-evidence | quality/timing-review.md | 2dfeab097d9e758caea8cf987666aca01d0d916587f8517480c09dcab02b94e0 |
| owning-project-evidence | specs/phase-3-program-specification.md | 824384b8391f7b37b283e4f68c10a7c322d80e0df622aaa89cd8d8cef9c8f399 |

### Evidence
Current diff and producer-consumer review for IEV2-VAL-006-comparable-timing, documented in semantic-review.md. Representative behavior: Three frozen equivalent runs per variant. Failure paths: source/environment/population drift, duplicate and incomplete records. Executable/manual evidence: test_timing_rejects_population_drift_and_partial; all 20 current integrity tests and historical full-03 (superseded by current smoke-optimization-full) validation completed. Formal verdict combines the reviewed DoD, boundaries, current hashes and behavior; scripts are supporting-only. Old failed runs remain excluded from current acceptance.

### Definition Of Done Validation
| DoD Item | Result | Evidence |
| --- | --- | --- |
| At least three complete equivalent runs; parent wall time distinct from child attribution; reject source/coverage drift. | PASS | semantic-review.md task row, implementation record and referenced behavior traces |

### Intent / Plan / Spec Compliance
- Result: PASS
- Owner instruction reviewed: yes
- Accepted plan reviewed: yes
- Accepted spec reviewed: yes
- Scope/out-of-scope reviewed: yes
- Acceptance criteria reviewed: yes
- Compliance status: aligned
- Wrong problem solved: no
- Owner instruction mismatch: no
- Accepted plan mismatch: no
- Accepted spec mismatch: no
- Acceptance criteria gap: no
- Scope creep: no
- Underbuild: no
- Overbuild: no
- Evidence: context.md, program specification, eleven-task accepted scope and current task producer-consumer row

### Review Completeness Gate
- Status: complete
- Cross-contract consistency: aligned
- Risk/work mode compatibility: aligned
- Source-of-truth, permissions, phase gates, artifact state, and acceptance criteria reviewed: yes
- Negative-space / adversarial review: completed
- Automated evidence role: supporting-only
- Post-fix full re-review: completed
- Reviewed baseline: original dabbf34 and current input table/digest; current actual smoke-optimization-full source matches optimized frozen records
- Instruction refresh: performed-targeted
- Instruction baseline: current
- Closure freshness: current
- Policy-boundary adversarial matrix: completed
- Producer-consumer field audit: completed
- Required-field mapping: complete
- Producers/consumers reviewed: .systems/scripts/report-validation-comparison, .systems/scripts/smoke_coverage.py
- Evidence: semantic-review.md, recovery-ledger.md and current source-bound behavior results

### Adaptive Data / Integration Verification Matrix
- Applicability: required
| Source Shape | Expected Canonical State | Expected Derived Output | Forbidden States/Rows | Failure Behavior | Automated Check | Manual Trace |
| --- | --- | --- | --- | --- | --- | --- |
| Three frozen equivalent runs per variant | Source-bound, owned, approved scope | Current result only, supporting-only scripts | source/environment/population drift, duplicate and incomplete records | Reject or report unavailable without broadening writes | test_timing_rejects_population_drift_and_partial | Current task row in semantic-review.md and reviewed fixture positive/failure traces |

### Commands
| Command | Result | Notes |
| --- | --- | --- |
| check-validation-integrity | PASS | 20 offline synthetic behavior tests; no external model session |
| validate-ai-system --profile full | PASS | smoke-optimization-full, all seven domains; supporting-only |

### Findings
- Blockers: none
- Unresolved findings: none
- Previous timing finding: resolved by IEV2-CR-001 current equivalent 20-test matrix, optimized 169.9906 seconds versus old isolated 225.5908 and monolithic 201.4699. Earlier six-run timing and copy-only unsuccessful hypothesis remain historical evidence; see smoke-optimization-timing-review.md.
- Warnings: none in the approved scope; independent model sessions, private runtime pilot, counterpart source and management rollout are explicitly excluded residual limits
- Residual risk: fingerprints do not prove truthful source claims; future agents must still follow semantic review and owner gates

### Quality Gate
- Intent / Plan / Spec Compliance PASS: yes
- Review Completeness Gate PASS: yes
- Cross-contract consistency aligned: yes
- Risk/work mode compatibility aligned: yes
- Negative-space / adversarial review complete or not applicable: yes
- Automated evidence treated as supporting-only: yes
- Post-fix full re-review complete or not required: yes
- Instruction baseline current: yes
- Closure freshness current: yes
- Policy-boundary adversarial matrix complete or not applicable: yes
- Producer-consumer field audit complete or not applicable: yes
- Required-field mapping complete or not applicable: yes
- 100% DoD satisfied: yes
- No known bug in scope: yes
- No regression in changed/direct paths: yes
- Edge cases covered or explicitly rejected: yes
- Explicit evidence attached: yes
- Quality result: PASS
- Required next phase: 6. FAZA DESTYLACJI

## Delivery Constraints QA
- Deadline/timebox status: owner-opt-out
- Quality floor preserved: yes
- Deferred scope: none within this task; publication and runtime migration excluded

## Validation Execution Record
- Semantic QA result: current task review complete
- Findings/blockers: none unresolved in scope
- Product checks: referenced behavior tests and manual/source audit
- Workflow script applicability: applicable for source-bound artifact integrity
- Targeted workflow commands: check-qa-evidence --project ai-system-integrity-and-efficiency-v2
- Script evidence role: supporting-only
- Final verdict: PASS

## Model Recommendation
- Recommended: GPT-5.6 Sol High
- Reason: high-impact shared integrity review with cross-contract failure paths
- Criticality: high
- Current model known: no
- Blocking: no

## Previous Runtime Formatting Recovery (Historical)
Only current runtime EOF formatting and declared input fingerprints were refreshed. Pre-recovery report bytes are retained in quality/evidence/pre-format-recovery-qa.json. Product source and product behavior evidence are unchanged. Required nonzero gates stop subsequent commit execution.

## Smoke Optimization Recovery
Current semantic/failure-path re-review is recorded in smoke-optimization-review.md. All prior 15 integrity cases are retained and all 20 current cases passed. Current actual full execution and nine equivalent frozen runs establish current supporting evidence; the initial copy-only performance hypothesis remains retained and excluded from acceptance. No privacy/approval gate, domain body, assertion or restore was removed. Previous report bytes are retained in evidence/pre-smoke-optimization-qa.json.
