# WEP-011 Semantic Editorial Review
Date: 2026-10-03. Scope: synthetic agent-authored recommendations only.
Author/reviewer: current Codex agent. This is a real content/route review in this execution, not an independent human, blind model evaluation or a conversion experiment. No additional model/API was called. Cases are authored in .systems/scripts/tests/editorial_v2_semantic_cases.py; the harness only binds fresh proof/package hashes.

## Actual Evaluated Input/Output Hashes
Command: PYTHONPATH=.systems/scripts:.systems/scripts/tests python3 -B .systems/scripts/tests/test_work_evidence_editorial_v2_semantic.py --evidence; exit 0, seven outputs.
| Case | Safe package input SHA-256 | Recommendation output SHA-256 | Package state |
| --- | --- | --- | --- |
| evergreen-procedure | 8537484fff9096d57f5ec9665b5743671c99d9070c33a42d4f26eb6ceba56277 | a1effb8af9d55b6e33b7eff62148ff96df95d25a23d489b863da0605a0c2d7d5 | prepared |
| timely-observation | 897d2ff023ee2a10cb93e7768d610a7a07311f3537c4ef64552553441961c2d9 | 9fe5da8598812115af2d58ce5990c648d796f9fa9de0b448336e2d7b52dbae08 | prepared |
| technical-niche | 87b9c82d7195ce9aa2c120a1ff2edcda7a04bb66319b453972d22b601fc53776 | 18c591eda6f9d3ac5beff03dd14afd532e5a1f12d0512ec734dfbc00477a1eb8 | prepared |
| visual-demo | 67c864536f6a443c3bca778745d7668e797c078bfe81c9025a7bf14315a25485 | 1930669e3ff533534690bbef9250e08ec7dd40d37e8d5a2d9d4b17cc634febcc | prepared |
| confidential-incident | c8be2f5c34fefc74541b1689d77b53749d436bec6b3422f3d15b3425d5da3fe4 | a83046a8b37bb626d33e00eb5a4569d6a10bd1ee64bec7f0f719e24fdf97430d | prepared |
| two-brand-audiences | 28e302d982253e0452ef83c748b9bb9f2a95fbc0e601f27a4075d6535fecf23f | ebd33804f3d30d757fe0a20fe8994511ab9a70978ade2eeffea04d07f4360ec3 | prepared |
| weak-proof-unknown-capacity | 9ab9e883116d1253af8c6f148317e15069f98e7d64d2b232aef023c1c3e6ad42 | b5e10a104d60f51d75f8abd3ceeea6bd4942cfa80e1123e6e4ff66d25aaed6d9 | needs-evidence |
Hashes identify the actual evaluated snapshots. Temporary isolated source/config roots differ between executions, so a new fixture execution receives new hashes. Within the same unchanged proof, prepare is deterministic and checked twice. Authored semantic prose remains stable in the source file and is separately bound by Phase 5 inputs.

## Manual Scorecards
Each case reviewed across evidence fidelity, audience promise, format justification, main/alternative difference, incremental value, privacy, capacity and uncertainty. Every mandatory safety dimension satisfied. Editorial choices are not claimed as universally optimal.
| Case | Fidelity | Promise/format | Main versus alternative | Incremental value | Privacy | Capacity | Uncertainty | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Evergreen procedure | Mock rerun only; no measured business gain | Durable method reference justified | Blog plus additive letter/social versus standalone letter | Extra acceptance checklist requested, not article repetition | Synthetic party-free evidence | 120 estimated minutes within 150, no publication slot reserved | Owner confirms effort and extra checklist | PASS |
| Timely observation | One observation, not universal productivity proof | Short standalone post; long article unsuitable | Short post versus contextual personal letter | No forced blog or media | No client identifiers | 10 versus 25 estimated minutes, unscheduled | Timeliness questioned | PASS |
| Technical niche | Receipt semantics do not imply physical invisibility | Blog-only explanation preserves nuance | Reference versus focused developer checklist | Social explicitly unsuitable, no forced funnel | Synthetic crash evidence | 90 versus 40 estimated minutes within 120 | Limits must remain explicit | PASS |
| Visual demonstration | Synthetic input/filter/output, no ROI | Visual concept justified by sequence | Short concept versus standalone text | Demonstration teaching differs from text | Missing asset permission remains a gap | Concept effort only, unscheduled; production excluded | No finished media claim | PASS |
| Confidential incident | Method retained after name/domain/date redaction | Internal hold recommended | Hold versus generalized private letter candidate | Lesson preserved without authorizing disclosure | All three identifiers removed; human combined-context/contract review still required | Zero selected main effort; alternative 25 estimate | No public-ready inference | PASS |
| Two brand audiences | One supported handoff method | PL personal decision versus EN team method | Two distinct promises versus one brand first | Not identical translated voice | No identifiable client result or invented ROI | 105 estimate within 130; no doubled cadence | Owner confirms both audience promises | PASS |
| Weak proof/unknown capacity | Claimed improvement unsupported and held | All five formats deferred | Reconcile old evidence versus collect a new experiment | No fabricated success story | No held source text leaked in package | Budget and effort unknown; no allocation | Explicit measurement and budget questions | PASS |

## Findings-First Review
No open P0/P1/material P2 in these seven recommendation examples. Same-agent review cannot establish real audience preference, conversion, anonymity against outside knowledge or general model reliability. A human must review every real derivative, translation and identifying combination. No human pilot, public activation or production video was performed.

## Negative Traces
Weak/conflicting evidence yields needs-evidence with no selected nodes. Confidential input yields safe derivative but still review-required, not public approval. Video gaps retain unscheduled concepts. The v2 executable tests independently reject selecting privacy-held/deferred formats, private URLs, stale decisions, missing capacity and cyclic dependencies.
