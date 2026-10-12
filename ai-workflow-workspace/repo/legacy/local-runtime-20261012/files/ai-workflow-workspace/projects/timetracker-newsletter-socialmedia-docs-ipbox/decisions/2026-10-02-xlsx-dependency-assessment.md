# XLSX Dependency Assessment
Decision ID: WEP-DEP-003. State: awaiting-owner. No installation performed.
Scope: isolated local adapter runtime; not global Python or production hosting.

## Evaluated Candidates
| Package | Version | License | Purpose | Runtime observation |
| --- | --- | --- | --- | --- |
| openpyxl | 3.1.5 | MIT | XLSX reader/writer | installed in bundled Python; absent in system Python |
| et-xmlfile | 2.0.0 | MIT | openpyxl transitive XML writer | installed in bundled Python; no declared dependencies |
| defusedxml | 0.7.1 | PSF | XML entity-expansion protection | not installed in inspected bundled runtime |

Package versions/licenses verified from installed distribution metadata and
primary PyPI metadata on 2026-10-02. The official openpyxl security page recommends
defusedxml; default openpyxl alone does not protect against XML expansion attacks.
Maintenance risk: defusedxml 0.7.1 was released in 2021; compatibility/security
must be exercised on the actual selected Python, not inferred from classifiers.
PyPI vulnerability arrays were empty for inspected versions; this is not a
complete advisory audit or a guarantee of safety.
Wheels: approximately 251 KB + 18 KB + 26 KB, excluding installed footprint.
Benchmarks and supported-Python malicious XLSX tests remain unexecuted.

## Alternatives And Controls
Alternative: separate owner-reviewed XLSX library behind the same ledger API.
No silent hand-written XML parser, hosted Sheets or artifacttool runtime switch.
Recommendation: approved pinned versions and hashes in isolated environment;
fail closed if XML protection unavailable; ZIP entry/size bounds, external-link,
macro and formula rejection are still required. defusedxml is not sufficient alone.
Rollback: stop using isolated environment; canonical JSON ledger is independent.
Do not uninstall global libraries or rewrite user workbooks.

## Approval Boundary
Pending question asks approval of openpyxl 3.1.5 and defusedxml 0.7.1; et-xmlfile
2.0.0 is the assessed transitive dependency, not a new service or vendor.
Actual pinned declaration, installation, adapter writes and XLSX tests wait for
the owner's answer. Dependency approval does not authorize private data import,
runtime cutover, production changes or publication.
Human replay is a later independent evidence gate: owner will supply its result
at the end before final-owner-yes, not substitute an agent test.

## Sources
- https://openpyxl.readthedocs.io/en/stable/ (Security)
- https://pypi.org/pypi/openpyxl/3.1.5/json
- https://pypi.org/pypi/et-xmlfile/2.0.0/json
- https://pypi.org/pypi/defusedxml/0.7.1/json
- Installed metadata inspected with the bundled Python, read-only.

## Owner Decision Checkpoint
Interaction mode: interactive; decision state: awaiting-owner at task003.
Optional Knowledge Capture: decision-artifact; private project only.
