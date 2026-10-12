# WEP-011 Findings-First Implementation Review
Date: 2026-10-03. Scope: all eleven approved product files, six sequential slices and private current project artifacts. No formal final acceptance.

## Reviewed Surfaces
Legacy module work_evidence_editorial.py and shared work_evidence.VERSION remain byte-unchanged. CLI dispatch, new module, companion schema, recommendation/format guidance, full 38-case v2 contract suite and seven-case agent semantic harness inspected in full. Templates do not grant authority; no API/model/media client exists. No imports/eval/subprocess driven by package text.

## Findings And Fixes
| ID | Severity | Observed condition | Correction / evidence | State |
| --- | --- | --- | --- | --- |
| E11-I1 | P1 | Pending-child metadata could bypass generic token assignment detection | Prevalidate every supplied artifact, including blocked children; explicit secret assignment scanner plus regression | resolved |
| E11-I2 | material P2 | Different node IDs alone could masquerade as a distinct alternative | Compare route semantics excluding identity/group labels; reject ID-only alternative | resolved |
| E11-I3 | material P2 | Unknown asset permission could be omitted from stated assessment gaps while retaining a scheduled concept | Explicit unscheduled asset-permission gate; negative regression | resolved |
| E11-I4 | material P2 | Private-host/trailing-dot and templated CTA ambiguity | Shared public host checks and literal reviewed CTA only; private URL, numeric shorthand and substitution cases | resolved |
| E11-I5 | material P2 | Receipt reader lacked request/decision/package cross-bindings | Bind manifest, queue, request, decision, safe destination and prepared package hashes; fork/tamper regressions | resolved |
| E11-E1 | evidence gap | Full smoke fixture omitted approved new untracked product files | Use existing explicit extra-product-file mechanism with eight exact safe paths; no index staging, weakened test or generic copier change | resolved; full run eacce7905e4c419183a9f4c34acdf127 exit0, all seven smoke suites complete |

## T01-T12 Mapping
| Requirement | Automated and manual evidence |
| --- | --- |
| T01 legacy compatibility | All original 135 tests retained; v1 output/ledger unchanged after v2 local write; shared version unchanged |
| T02 safe preparation | Tree fingerprints unchanged, missing destination/no-init, held/empty/conflicting data, selected proof hashes, injected text inert; actual CLI trace |
| T03 strict shape/version/paths | Schema field audit, extra/ambiguous markers, malformed scalars/brands, symlink output rejection; CLI diagnostics omit paths |
| T04 optional routes and brands | One/two brand tests, standalone letter, unscheduled blog, no forced media; all seven authored routing cases |
| T05 approval/freshness | No decision, wrong owner/purpose/ref, stale topic/source/recommendation/route/translation/CTA; unchanged unrelated entry and changed selected entry; procedure reference unavailable stops |
| T06 privacy/adversarial | Secrets in held sources and pending metadata rejected; full literal redaction remains review-required; private body URL and hidden field cases |
| T07 cadence/capacity | Language variants share slot but add effort; distinct group/output rejected; unknown/oversubscribed capacity blocked for scheduling; legacy reservations retained; named replacement preserves prior bytes |
| T08 graph/readiness | DAG cycle rejected, missing parent yields exact pending list with independent output retained, related edge does not block; deferred/privacy-held rows cannot be selected |
| T09 formats/metadata | All five fields rendered/covered, additive newsletter required, title/CTA/translation changes invalidate review, markup escaped; asset permission gaps never become finished media |
| T10 recovery | Failure after manifest/draft/queue and before/after receipt, identical retry, writer lock, changed proof after preview, conflicting queue, changed staging, malformed receipt, fork, stale/cross-topic predecessor |
| T11 privacy and integrity | No private provenance in files/package, no model/sends/publication, ledger unchanged, source/private historical fingerprints preserved, original v1 files remain unchanged |
| T12 semantic output | Seven authored recommendations with exact evaluated package/output hashes; actual manual scorecards and same-agent limitation in semantic-editorial-review |

## Manual Success And Failure Traces
Actual isolated CLI: prepare then preview, both exit0 with identical tree; write plus exact retry exit0 with one completed local artifact and identical immutable bytes. Alter selected proof then retry: exit2 stale-source, no write. No real owner runtime was initialized. Completion is receipt-based, not multi-file atomic rename or physical invisibility.

## Scope And Residual Risk
High privacy/data risk managed by explicit user-approved scope, safe synthetic fixtures, mandatory local human-review gates and no activation/publication. Full post-fix source and requirements re-review completed, not just regression rerun. No unresolved product P0/P1/material P2. Full AI System validation completed exit0; script evidence remains supporting-only, not final owner acceptance.
Human semantic truth, combined identifiers, real audience preference and truly incremental newsletter value cannot be proven mechanically. Current agent authored and reviewed these synthetic recommendations; no independent human replay/acceptance claimed. WEP-010 and tax-rule gates unchanged. No Codex memory, public insights, TaskNotes, commits, push or updater.
