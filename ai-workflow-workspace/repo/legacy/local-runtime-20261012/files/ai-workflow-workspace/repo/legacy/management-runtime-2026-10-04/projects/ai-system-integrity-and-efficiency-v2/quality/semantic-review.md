# Semantic And Adversarial Review

## Scope And Authority
Reviewed the current staged product diff against the eleven accepted task DoDs and program specification. This is an agent review, not an independent external-model evaluation. No client material, real workspace migration, Workflow source change, push or management rollout is included. Phase 8 must await owner final acceptance.

## Producer-Consumer Audit

| Task | Reviewed production and consumption | Observed behavior and boundary |
| --- | --- | --- |
| IEV2-VAL-001-typed-negative-assertions | smoke harness -> exact negative manifest -> assertion helper -> completeness marker | All 220 negative identities require a declared code and specific diagnostic. Wrong cause, duplicate execution, shell infrastructure errors and missing cases are rejected. Positive/direct assertions remain in the owned case bodies. |
| IEV2-SKL-002-eval-freshness | eval plan/source -> run manifest -> per-eval metadata -> grade/result fingerprints -> standalone aggregator | Complete plan/source changes invalidate aggregation; recomputing a tampered metadata hash does not bypass canonical-plan comparison. Orphan grades and changed output cannot be adopted. Existing symlink descendants in an ungraded output are now rejected before run.json is written. |
| IEV2-VAL-003-evidence-destinations | evidence CLI -> ownership preflight -> pinned directory -> no-clobber publication | Existing, tracked, deleted-tracked, foreign-repo and linked paths are refused. Directory identity is checked at publication; concurrent destination creation cannot be overwritten. This does not grant owner approval for an otherwise unauthorized target. |
| IEV2-UPD-004-canonical-updater | fetch -> explicit ancestry classification -> fast-forward -> full validation | Equal/behind are allowed; ahead/diverged stop without reset, stash or merge. Local synthetic remotes tested all four states. Network publication and management rollout remain out of scope. |
| IEV2-VAL-005-validation-lifecycle | command selection -> actual child states -> owned process groups -> completion/evidence | Failed or interrupted children never acquire completed smoke state. Timeout/SIGTERM fixtures verify child cleanup. Start/progress/result contain a common run identity; scripts never issue semantic acceptance. |
| IEV2-VAL-006-comparable-timing | frozen source/environment/population -> complete records -> comparison | At least three unique complete runs per variant; within-variant drift, missing child coverage and unequal population are rejected. Wall time and summed child attribution are not additive. Timing is not a quality verdict. |
| IEV2-VAL-007-scoped-coverage | dependency registry + complete owned inventory -> scoped consumer args -> after-run freshness | Capture-state and block checkpoint only; unknown consumers or changed shared product source require full validation. Exact inventory and semantic/privacy fingerprints prevent a partial manifest from claiming checkpoint coverage. |
| IEV2-OPS-008-bounded-recovery | failure artifact -> bounded hypothesis/fix -> fresh retest -> closure evidence | Failed runs remain evidence. No broad retry permission, production effect or guard bypass follows from a test failure. Current product hashes, not an old successful log, govern closure. |
| IEV2-SKL-009-metadata-discovery | workspace/system frontmatter discovery -> matching decision -> selected full SKILL.md | Metadata reader stops at the closing frontmatter delimiter. Workspace name precedence and excluded legacy imports tested. Matching remains an agent decision; discovery is not automatic invocation. |
| IEV2-DRM-010-dream-lifecycle | lifecycle JSON -> reviewed Source Guard inventory -> previous/decision/quality references | Stable IDs and permitted transitions require current fingerprints. Implemented needs previous history and quality evidence. Referenced decisions are evidence, not new approval; history is not rewritten or inferred. |
| IEV2-OPS-011-freshness-topology | explicit Git roots or product contract names -> stdout metadata | No fetch, recursive runtime crawl, client body read or reconciliation. Topology links are structural evidence, not proof of behavior; unavailable upstream remains unknown. |

## Negative Space
- Full-required shared-source/CI/updater/final integration cannot become scoped-ready merely because checks are green.
- Evidence ownership and a source fingerprint do not grant execution or publication permission.
- Grade fingerprints detect freshness, not whether manual grading was truthful.
- Dream recommendation history does not execute accepted actions or promote knowledge.
- Skill descriptions do not override the matched full contract or higher-priority instructions.
- Local Git freshness cannot establish the current remote tip without an authorized fetch.
- Historical records and unrelated CR009 edits are not repaired or staged by this program.

## Review Findings
- Blockers found and resolved: ungraded eval-output symlink escape; normal Python entrypoints now suppress generated bytecode before local imports; source-bound test-population hashing includes the regression-test body, not only method names.
- Existing failed fixture/consumer runs are retained in recovery-ledger.md; no historical result is relabeled.
- No unresolved material implementation finding identified after the current code review.

## Limitations
No independent model session or private runtime pilot was run. Local isolation and tests constrain the implementation, but cannot prove every future agent will follow routing, truthful grading, privacy decisions or owner approval. Performance acceptance requires the separate frozen comparison records, not this narrative.
