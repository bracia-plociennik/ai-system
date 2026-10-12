# WEP-DEP-003 Dependency Approval

Owner decision: approved in the current conversation on 2026-10-02.
Exact versions: openpyxl 3.1.5 (MIT), defusedxml 0.7.1 (PSF), et-xmlfile 2.0.0 (MIT).
Scope: isolated environment only, XLSX adapter and safe tests within the accepted implementation range.
Dependency evaluation: decisions/2026-10-02-xlsx-dependency-assessment.md.
No global Python changes, production activation, push or final-owner-yes.

## Implementation Slice Plan
Source and DoD source: owner approval above and accepted WEP-XLSX-003 specification.
Scope: pinned hash-verified dependencies in an isolated /private/tmp environment.
| slice id | goal | expected files/areas | acceptance check | evidence required | status |
| --- | --- | --- | --- | --- | --- |
| dep-003 | Install approved packages only | isolated venv and pinned product requirement file | versions match, defusedxml active, no extra runtime dependencies | pip output and runtime probe | completed |
Stop on package hash/version mismatch or unsupported runtime; never substitute a dependency.
Delivery Constraints: owner-opt-out, no deadline/timebox; all privacy/QA gates remain.
Artifact QA: refreshed task003 Spec QA before adapter implementation. Post-implementation quality: phase-5-quality.
Residual risk: dependency approval is not a security guarantee; archive/XML/resource bounds and adversarial tests remain required.
Model recommendation: workhorse high reasoning; Blocking: no.

Execution: isolated /private/tmp/wep-xlsx-venv; hash-verified binary-only pip
install exited0 after the initial sandbox DNS failure and approved network retry.
Runtime probe confirmed all three exact versions and openpyxl DEFUSEDXML=True.
No global Python changes. Adapter regression: 70 executions successful.
