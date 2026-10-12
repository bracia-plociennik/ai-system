# Work Evidence Pipeline Architecture
Current revision: 2026-10-03, WEP-CR-001. Editorial v2 extension below governs new WEP-011; original foundation remains unchanged.
Date: 2026-10-02. Classification: implementation-capable. Artifact is private/local; product rules and fixtures must be sanitized.
## Intent And Boundaries
Owner context.md and decisions/D01-D10 govern scope. Build a local evidence foundation with independent documentation, reporting, tax and editorial consumers. No web app, cloud sync, live sends, bank/payment functions, tax filing, automatic qualification, production CRM, historical rewrite, AI Workflow product change, or task lifecycle mutation.
Audit depth: bounded contract/source inventory, not a fresh audit of every historical workbook, PDF, screenshot or client codebase. Prior binary findings are attributed to context/context.md. No technical claim depends on treating them as fresh tests.
## Components And Dependency Direction
1. Python core validates versioned structured records, identities, policy and transactions; CLI wrappers follow existing .systems/scripts conventions.
2. Source adapters read only explicit allowlisted checkpoint/TaskNote/document references. Text never becomes instructions or write approval.
3. Owner-scoped work ledger is canonical; workspace index and XLSX are regenerable projections.
4. Documentation assembler references technical artifacts and exports a scoped reproducibility package.
5. Client report renderer filters approved facts for one recipient and interval; recurring service scope is separate.
6. Private IP register joins evidence to financial facts and advisor-approved declarative rules; never feeds editorial ingestion.
7. Editorial queue builds brand/language-specific local briefs and drafts from reviewed operational facts. No automatic distribution.
8. Verification/rollout tooling tests invariants, backup/rebuild and pilot; current Make automations remain untouched.

No daemon or timer is required. First version uses explicit local commands. Record/draft approval is scoped to action, object versions and destination, not inferred from a checkpoint alias.
## Storage And Ownership Matrix
All following paths are proposed runtime contracts, not directories created by planning.
| Object | Canonical storage | Key / invariants | Consumers |
| --- | --- | --- | --- |
| Workspace config | <workspace>/work-evidence/config.json | registered workspace ID and explicit allowed local roots | core |
| Entity registry | <workspace>/work-evidence/entities.json | client, end-client, project, domain IDs; aliases; no fuzzy autojoin | every adapter |
| Work revisions | nearest approved owner-root/work-log/YYYY/<entry-id>/rNNNN.json | immutable entry_id, revision, owner_workspace, work_id, performed_on | index/report |
| Human session | <workspace>/work-evidence/sessions/<session-id>.json | time evidence and allocations by entry ID | allocation validation |
| Task binding | <workspace>/work-evidence/task-bindings.json | task_ref stable binding to canonical TaskNote path | read-only linkage |
| Checkpoint/doc | existing owner/project paths | locator, hash, observed_at, evidence_level, scope | source reference only |
| Index | <workspace>/work-evidence/derived/work-index.jsonl | rebuildable, source hash set; not hand-editable | local Excel/reports |
| Excel | <workspace>/work-evidence/time-tracker.xlsx | workbook_id, export revision; Manual Inputs and derived sheets | owner local UI |
| Report | <workspace>/work-evidence/reports/<period>/<report-id>/ | immutable revision and source manifest | owner-reviewed local draft |
| Tax store | explicitly selected owning workspace/private-tax/<taxpayer-id>/ | legal taxpayer ID binding; separate permissions/allowlist | advisor packet/calculator only |
| Editorial | existing brand content root via explicit config | topic_id, source hashes, brand, language, purpose, review state | local drafts only |

Runtime root selection never follows untrusted file paths. Roots must resolve under approved workspace namespaces; reject traversal, symlinks escaping roots, secret-like locations and ambiguous ownership. No automatic mkdir/init/backfill in another workspace.
One workspace owns each task and entry. Source copies and cross-workspace references cannot create another counted entry. Taxpayer mapping may link evidence from both workspaces by reference, without cloning time.
TaskNotes in Kuba's physical vault may own Onlinen work. Binding uses owner metadata/registry, not folder location. Renames require updating an explicit binding; title matching never creates identity.
## Canonical Entry v1
Required: schema_version, entry_id (UUID), revision, previous_revision_hash, owner_workspace, work_id, performed_on, recorded_at (offset timestamp), actor_kind, client_id/project_id nullable, title_internal, activity_kind, outcome, status, duration, source_refs, visibility.
status: done|partial|blocked|waiting|unknown. TaskNote linkage optional; zero minutes valid only as explicitly supported measurement/statement, unknown represented null.
duration: seconds nullable, basis measured|owner-confirmed|estimated|unknown, evidence_ref nullable, session_id nullable. Human, automation and waiting have separate actor_kind and cannot silently share human totals.
source_refs: root alias, relative path, SHA-256, observed_at, fact date when known, evidence level owner-attested|local-test|production-readback. Disagreement is a conflict, not latest-file-wins.
visibility defaults internal. Client report text, editorial derivative and tax assessment are separate records, not mutations of internal truth.
Correction creates revision r+1, never overwrites previous facts. Voiding is a tombstone revision with reason; derived totals use only latest nonvoid revision. No implicit delete on missing Excel row.
## Time And Period Semantics
Date-only work remains date-only; do not derive time from plan, commit timestamps or file mtime.
Measured intervals use timezone and UTC offsets; duration calculated on UTC instants. For overnight or DST, segment at local boundaries for reports, retain one session total. Ambiguous local timestamps are rejected pending clarification.
Date-only reported duration is assigned to performed_on; multi-day aggregate stays aggregate with coverage window, not divided evenly.
Reports use [start, end) in Europe/Warsaw. A partly overlapping aggregate is shown separately, excluded from exact per-day sums with coverage warning.
Single human session allocations sum at most to measured/confirmed session duration. Overlap across known sessions is flagged; unknown duration contributes to missing coverage, not zero. Financial/billable classification does not follow from duration automatically.
## Transaction And Excel Protocol
Use UUID workbook identity and stable manual row IDs, never row numbers. Canonical JSON records are standard-library storage; XLSX adapter uses a reviewed/pinned reader-writer dependency after dependency evaluation, no install in this run.
Read workbook snapshot under exclusive workspace writer lock; validate schema, source hashes, protected projection hash and manual IDs. Imported text cells are stored as literal strings, not executable Excel formulas.
Default command is dry-run. Apply requires owner-approved batch manifest bound to source/workbook hashes. A changed source invalidates approval.
Dry-run uses ephemeral row references and never writes a journal, reserves persistent IDs, locks persistently or changes workbook/ledger. A separate owner-approved prepare operation reserves UUIDs for blank-ID rows and writes a durable local transaction journal mapping the exact workbook snapshot and row fingerprints to IDs. Apply requires approval of this prepared manifest. Duplicate indistinguishable rows require owner resolution; do not collapse legitimate equal work by content hash.
Commit canonical revisions with idempotency keys derived from transaction/row identity. Then export workbook with imported row IDs and import receipt; keep manual input history. If crash occurs between stages, resume the journal, do not generate fresh IDs or minutes.
Stage validated temporary files, fsync, atomically replace individual files, then commit a batch manifest. Readers include only committed batches. This is not a claim of multi-file atomic rename.
Stale locks need operator-reviewed recovery, not automatic removal. Refuse open/locked Excel or concurrent hash changes. Detect edits to generated tabs and stop rather than discard. Backup/restore tested before rollout.
Dependency choice: openpyxl candidate for XLSX, standard-library JSON/Decimal/zoneinfo core. Dependency evaluation and approval are a task prerequisite; exact version/license/security facts must be verified at implementation. Alternative is a different approved XLSX adapter behind the same interface, not custom ZIP/XML business logic.
## Documentation And Client Reporting
Documentation contract: purpose, required skill/access, version/environment, inputs, ordered steps, decisions, expected outputs, tests, stop conditions, rollback, known limits, source manifest. Reproducibility status: recorded|documented|replay-passed; only independent human evidence advances final state.
Client report has completed outcomes, partial/waiting work and contractual recurring care separately. No newsletter-style narrative can turn scope into a performed event. Only explicitly approved report fields flow to the selected recipient; unrelated client facts excluded.
No actual sends. HTML/Markdown local outputs escape raw text and exclude tracking, external assets and private-source links. Keep internal provenance separate from client-facing files.
## IP Box Boundary
Separate IP IDs, rights holder, contracts/transfer evidence and taxpayer mapping from client/domain/task. One-to-many allocations reference records; sums cannot exceed eligible source amounts.
Rule envelope: rule_set_id, version, taxpayer_id, tax_year/effective interval, approval evidence locator/hash, advisor identity, approved_at, scope, rounding/currency policy, qualification/allocation method, exclusions and numeric operations.
No user code/eval in rules. Allowlisted Decimal arithmetic, sum, ratio, min/max and named mapping tables only; reject unsupported operations, zero denominators, unsupported currency and missing policy.
Calculation output: source/rule digests, exact intermediate operands/results, coverage, rounding, status draft|blocked|reviewed. Rule revocation/source revision makes output stale and unavailable as current.
Real calculation blocked until owner provides advisor-approved complete rule set, taxpayer and financial inputs. Generic engine and synthetic tests can be specified now; no interpretation of example rates, no tax advice, no inferred qualification.
Unavailable required values block relevant calculation; do not report a partial sum as full tax. Evidence-only packet remains available with explicit gaps.
## Editorial Boundary
Allowlist only selected operational summaries, not Raw Check-In, Working Dump, tax store, attachments wholesale, credentials or client databases. Candidate content remains data.
Privacy: public-ready|needs-anonymization|anonymized-needs-review|internal-only; editorial approval is separate and binds content hash, brand, language, channel and purpose.
Sanitize people, domains, dates, numbers, screenshots and combinations; preserve source privately. Unsupported benefit claims are removed/flagged, never invented. Automatic redaction cannot grant publication approval.
Brand config: Kuba PL-first/optional EN; Onlinen EN-first with separate PL variants, four-issue planned language pilot. Newsletter fortnightly per brand, staggered; two base social plus optional third total per brand/week. No audience-list reads or sends. Test measurements (visits, signups, qualified replies, effort) remain unknown until owner imports approved results.
Draft generation: CLI prepares deterministic evidence bundle; agent writes reviewable local drafts only on exact approval. No hidden model API credentials or background jobs.
## Risks, Assumptions And Unknowns
| ID | Risk / unknown | Owner | Closure condition |
| --- | --- | --- | --- |
| R1 | Double counting duplicated facts/manual replay | implementer | IDs, committed batches, crash/retry fixtures and monthly trace pass |
| R2 | Cross-client/private leakage | owner + reviewer | fail-closed projections, adversarial sentinel tests and human review |
| R3 | Tax rules and taxpayer not supplied | owner + advisor | activation gated, approved rule packet and reference calculations |
| R4 | Documentation not independently usable | owner + subcontractor | mock-environment replay without owner help, record failed steps |
| R5 | XLSX adapter dependency/version suitability | implementer + owner | dependency review before install; adapter contract stable |
| R6 | Historical inputs incomplete/ambiguous | owner | no backfill now; later approved mapping/coverage assessment |
| R7 | Concurrent writers/open workbook | implementer | locks, version checks and failure injection tested |
| R8 | Human effort/documentation overhead | owner | measure pilot overhead; review before routine rollout |

Unknowns blocking architecture: none inside these declared gates. R3/R4/R5/R6 block their own activation/install/import, not invention of substitute facts.
Assumptions: local filesystem supports same-volume atomic replacement; client reporting and draft review remain manual; any contrary observation stops dependent work.
## Plan Quality Contract
Plan classification: implementation-capable.
DoD source: context.md and decisions/D01-D10.
Testable DoD: all components have owners, canonical fields, failure behavior, privacy boundaries and explicit downstream gates; task decomposition requires no guessed fiscal decision.
Artifact QA route: phase-1-architecture-qa; trigger: now before plan.
Implementation Quality Closure route: phase-5-quality per task.
Required verification: producer-consumer field matrix, failure-path review, source/rule boundary review and pilot definition review.
Quality-ready criteria: no unowned architectural risk or hidden dependency. Owner opt-out: none. Not-applicable reason: none.
Blocking decision: none for design. Next route: phase-1-architecture-qa.
## Delivery Constraints
Inherit D07: owner-opt-out, no deadline/timebox, full QA/privacy protected, no cutline within must-have; implementation and live activation deferred.
## Owner Decision Checkpoint
Interaction mode: queued. Decision state: clear for planning. Runtime activation decisions R3-R6 remain explicitly gated. Reversible details: JSON revision records, WEP IDs, no daemon.
## Optional Knowledge Capture
Capture recommended: yes; target architecture/decisions only; defer-to-distillation for later implementation. No additional workspace memory.
## Model Recommendation
Frontier/workhorse high reasoning; high-impact data design; current model unknown; Blocking: no.

## Editorial v2 Extension (WEP-CR-001, 2026-10-03)
This section is the current design for new WEP-CONTENT-011, not a claim that v1 already implements it.
The rest of this architecture remains the foundation. Historical assessed architecture and QA are preserved in history/2026-10-03-wep-v1-baseline; prior approvals cannot authorize this extension.

### Topology And Responsibility
Owner refinement 2026-10-05: retain a readable original lesson privately, then
owner review, then separate anonymized derivative and its disclosure review.
review-source exposes explicitly selected originals only to the owner; prepare
continues to expose safe derivatives only. Replacement requires exact-version
private review; readable originals stay beside the private manifest, receipt-bound.
Approved operational evidence -> topic card -> agent recommendation -> owner-selected route -> independent artifacts and optional dependencies -> local draft review.
Blog is one possible anchor, not a universal parent. Supported paths include blog + additive newsletter + selective social; newsletter-only; blog-only; parallel blog/newsletter; social-only; visual-demo concept; hold/internal-only.
A related artifact need not depend on another artifact's publication. Only explicit dependency edges can block it. No publication or external I/O is added.

### Data Ownership
| Record | Authority and producer | Consumers and invalidation |
| --- | --- | --- |
| Work/source/claim | existing ledger and explicitly selected current proofs; claim support remains reviewed | topic package; changed entry/source/procedure invalidates affected dependents |
| Topic v2 | agent-authored title, audience problem, transferable lesson, brand angles and source claim IDs; owner-reviewed, not source fact | recommendations, briefs; every revision has digest |
| Recommendation | agent-authored suitability for five formats per selected brand, primary route, alternative, reasons/gaps/confidence/effort | owner decision; cannot authorize a write or public disclosure |
| Route decision | explicit owner action approving or editing a complete recommendation bundle, bound to hashes | preview/drafts; topic/recommendation change requires new decision |
| Draft/concept | distinct brand/language/format purpose and body with claim mapping | private local review; content/source/route change invalidates review |
| Public reference | owner-supplied existing URL and verification evidence/date; no guessed URL | optional CTA; missing/unverified target cannot be represented as live |

Private provenance is separate from safe output files. No tax/raw/dump/secret ingestion, codebase crawl, real metrics fabrication or new task/time records. A topic may relate to several existing entries; it does not multiply work or time.
Storage remains in the configured workspace: private ledger editorial/v2/<topic>/<bundle-hash>/ and explicit existing editorial destination/v2/<topic>/<bundle-hash>/. No automatic workspace creation/migration.

### Version And Approval Boundaries
The v1 request keeps schema_version: 1 and its current strict interface. V2 uses editorial_schema_version: 2, with independent dispatch before the legacy validator. Both/missing/unknown markers fail closed. Shared work_evidence.VERSION remains 1.
V1 fixtures/output behavior are regression-locked. No automatic conversion of previous bundles, approvals, schedules or hashes.
Source approval, route acceptance, draft review and permission to persist are different gates. Each binds exact action/purpose, object/source hashes and owner attribution; a literal approved_by string is audit metadata, not proof of current authority.
Only scoped owner authorization permits write. Public approval is never an output of this system.

### AI And Editorial Rules
Deterministic prepare validates evidence/brands and returns only safe derivatives, holds and constraints. Agent adds interpretation; validation checks schema/provenance, not whether the recommendation is editorially wise.
Per-format fit: recommended|optional|defer|unsuitable. Readiness: needs-evidence|needs-anonymization|needs-review|ready-for-local-draft|internal-only. Strong fit cannot override a privacy hold.
Primary and alternative routes include why, why-not, evidence gaps and estimated effort with low|medium|high confidence (not probability). Owner can approve/edit the bundle in one decision.
Newsletter may extend a blog with a checklist, decision log, example or tool; a blog must still answer its promised question. Social gives a useful takeaway without mandatory link. Video suitability requires a demonstrable visual/story element; text-only lesson need not become video.
Short/long video outputs are concept, hook, teaching point, scenes or outline, assets needed and evidence/permission gaps. No finished footage or performance claim.

### Capacity And Failure Boundaries
Existing brand registry/cadence stays global; topic selects one or both brands without duplicating the registry. Translations share an allocation group; variants' effort still sums.
Blog/long-video have no forced slots. A short-video concept can occupy one existing social slot instead of a post; it does not mean a video is ready to publish. Unknown effort/budget stays unknown. Overbooked known capacity blocks the proposed schedule, not preservation of an unscheduled idea.
Missing evidence yields hold/question. Invalid reference, stale hash, path escape, secret-like content or forged/mismatched approval rejects the affected requested operation before writing. No partial success represented as fully approved bundle.
Dependencies form a directed acyclic graph. Dangling IDs/cycles fail; optional related-to links do not gate drafts. A CTA to an unpublished blog stays absent or an internal editorial note, never a invented live link.
Immutable hash-addressed writes reuse the ledger lock and existing atomic-file helpers, with a final completion manifest. Consumers ignore incomplete bundles; idempotent retry may complete identical bytes only. Rollback/deletion and public export remain separate owner actions.

### Risks And Gates
R9: AI fit may be weak despite valid schema -> seven human-reviewed synthetic routing cases and honest uncertainty.
R10: disguised identities can survive redaction -> human quasi-identifier/contract/copyright review, synthetic canaries; no automatic public-ready.
R11: extra formats create hidden work -> allocation groups, explicit effort, no new mandatory cadence.
R12: v2 versioning breaks the ledger/v1 consumers -> independent marker and unchanged v1 golden tests.
R13: archival QA mistaken for current v2 evidence -> history manifest, source-bound new artifact QA, conditional task; no new Phase 8.
DoD for architecture: all new objects, producers, consumers, source/approval boundaries, failure behavior, compatibility and deferred production surfaces are explicit.
Artifact QA: Phase 1 architecture QA. Future implementation Quality: Phase 5 for WEP-011, then capture and separately triggered Phase 8.
