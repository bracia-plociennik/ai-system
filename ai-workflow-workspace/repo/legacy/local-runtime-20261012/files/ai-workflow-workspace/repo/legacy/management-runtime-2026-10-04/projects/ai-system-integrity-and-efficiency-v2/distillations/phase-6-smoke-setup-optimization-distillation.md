# Smoke Setup Optimization Distillation

## Metadata
- Project: ai-system-integrity-and-efficiency-v2
- Date: 2026-10-01
- Workflow phase: 6. FAZA DESTYLACJI
- Scope: IEV2-CR-001-smoke-setup-optimization
- Quality artifact: quality/phase-5-iev2-cr-001-smoke-setup-optimization-quality.md
- Approval: accepted technical implementation/capture scope; not final owner acceptance
- memory-in-repo-memory: false
- memory-in-project-memory: true

## Durable Decisions
1. Optimize fixture preparation and bounded execution, not assertion populations. Full copies remain independent; no hard links or writable shared cache.
2. Preflight every tracked source and explicit extra before writes. Preserve file content, executable modes and timestamps.
3. At most two independent domains run together. Drain both started peers on failure, stop future pairs and emit full completion only after all seven succeed.
4. Output order and source/coverage identity remain deterministic even when execution overlaps. Wall time and child attribution are distinct, not additive.
5. A faster setup micro-hypothesis does not prove the full system is faster. Retain failed acceptance hypotheses and rerun comparable full populations after changes.
6. Earlier immutable evidence can remain historically true while a later measured setup supersedes its performance disposition. Refresh current QA fingerprints only after actual semantic and behavior re-review.

## Measurement And Recovery
Copy-only optimization improved the old isolated setup but did not clear monolithic overhead; all nine records remain in evidence/smoke-copy-only. The bounded follow-up has nine equivalent complete records with 20 integrity tests, seven unchanged bodies and 220 negative contracts. Mean wall: old isolated 225.5908 seconds; monolithic 201.4699; optimized isolated 169.9906. Current local improvement: 24.65 percent versus old isolation and 15.62 percent versus monolithic. Source/environment/coverage identity was checked, including actual current-worktree full execution. The earlier six-run warning and prior failed Phase 8 are preserved.

## Capture And Boundaries
- Project memory: memory/2026-10-01-smoke-setup-optimization.md.
- Advisory handoff: external-memory/memory/2026-10-01-isolated-smoke-optimization-ai-workflow-handoff.md.
- No counterpart source, managed checkout, client runtime, scheduler, publication or global memory change.
- No final owner acceptance inferred from implementation approval or successful scripts.

## Distillation Gate
- Captures reusable knowledge: yes
- Avoids local noise: yes
- Ready for checkpoint processing: yes
- Privacy/scope check: pass
- Residual risk: three local repetitions, machine/cache noise, no private-runtime pilot; timing is not a universal guarantee
