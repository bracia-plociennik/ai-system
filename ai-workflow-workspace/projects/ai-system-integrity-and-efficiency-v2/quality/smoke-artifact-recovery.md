# Current Artifact Recovery

Targeted current QA validation rejected the intermediate pending Phase 8 assessment because its temporary source-HEAD placeholder had invalid length. No commit, technical acceptance or owner closure followed that rejection. The assessment remains pending/FAIL while the current supporting chain runs; its source binding was regenerated from the actual Git HEAD and current declared files. The failed diagnostic and intermediate report bytes are retained in evidence/smoke-artifact-recovery.json.

The new fix Quality clone's mechanically duplicated input row was also removed during read-only review before validation. The final table is deduplicated and every hash is recomputed from its declared root. This is runtime evidence formatting recovery, not an assertion change or hidden product success.

The handoff decision validator also rejected the missing exact `Cross-system Impact` section. The required section was added before commit or handoff acceptance, then the same targeted check was repeated. Failure diagnostic: `Missing Cross-system Impact section`. No target-specific write gate was weakened.

The first renewed Workflow full invocation returned 127 because it was started from the product root instead of the nested Workflow root; its runner requires relative `.systems/scripts/run-with-timeout`. The failure completion marker and log remain retained as smoke-optimization-workflow-full.log. The corrected invocation uses the nested Workflow working directory and a new full-02 log. No source change or test weakening was used to repair the invocation.

The corrected full-02 completed with exit 0, all smoke groups and one full completion marker (648 seconds). Rejected/intermediate records remain excluded from acceptance; scripts remain supporting-only.
