# Cross-System Upgrade Handoff

## Metadata
- Date: 2026-10-01
- Source system: ai-system
- Counterpart: ai-workflow
- Status: accepted-for-handoff
- Privacy/scope check: pass
- Raw client data included: no

## Concept And Intended Outcome
Preserve all assertion populations and independent fixture transactions while reducing full-validation overhead. Preparation uses one tracked-product copier per domain; all-domain execution uses at most two independently owned subprocesses. This is an advisory adaptation candidate, not an instruction to change counterpart code.

## Owner Decisions
- Approved isolated-suite optimization without coverage reduction, no deadline/timebox.
- Local reviewable commits and technical capture; no push, rollout or counterpart product write.
- Final owner acceptance must refer to the completed current assessment.

## Safety And Authority Boundaries
- Preflight complete sources and safe extras before copy; preserve metadata and containment.
- No hard links, shared writable fixture/cache, scheduler or detached worker service.
- Drain started peers, propagate failure, stop future pairs and emit completion only for all successful domains.
- Validation runner retains owned process-group interruption cleanup.
- Green scripts and measured timing do not supply semantic or owner acceptance.

## Source-System References
- .systems/scripts/smoke_fixture.py
- .systems/scripts/check-validator-smoke-tests
- .systems/scripts/smoke_coverage.py
- .systems/scripts/smoke/negative-expectations.json
- .systems/scripts/tests/test_validation_integrity.py
- .systems/scripts/report-validation-comparison

## Validation Expectations
The current synthetic matrix retains seven exact transaction bodies, 220 exact negative contracts and all 20 integrity cases. Three repetitions per variant show current mean wall 169.9906 seconds versus old isolated 225.5908 and monolithic 201.4699. An earlier copy-only matrix did not clear overhead and remains retained. Small local samples/noise limit portability; never infer equal coverage from a count alone or use failed/partial runs as timing acceptance.

## Counterpart Adaptation Checklist
- [ ] Compare current counterpart fixture ownership before considering a change.
- [ ] Audit domain writes and global state before allowing overlapping domains.
- [ ] Preserve exact bodies, mutation/restore logic, negatives and required gates.
- [ ] Test independent roots, copy metadata, invalid paths, bounded workers and drained failure.
- [ ] Repeat frozen complete comparisons and keep unsuccessful hypotheses.
- [ ] Perform semantic review before supporting scripts; preserve formal owner gates.

## Privacy Check
- Client data, secrets, credentials and production identifiers: not included.
- Private runtime and home paths: not included.
- References are product-relative; no counterpart historical approval is imported.

## Residual Risk
Parallel independence depends on an explicit write audit. Shared-state suites cannot be treated as independent without redesign and separate scope. Local timing does not guarantee other machines or truthful future agent behavior.
