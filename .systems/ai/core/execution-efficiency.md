# Execution Efficiency

## Purpose

Reduce repeated execution and artifact rework, never evidence or quality. This is the central
`execution-efficiency-v1` contract for validation reuse, bounded defects and closure records.
Semantic review, DoD, privacy, approvals and local project gates remain authoritative.

## Check Plan And Reuse

`validation-dependencies.json` declares product/runtime-artifact/integration/environment categories.
Unknown category/dependency coverage is not eligible for reuse. A complete declaration binds input
files and inventory, implementation and helpers, parameters, coverage, tools and environment.
Per-check evidence records `execution: executed|reused|invalidated`, reason, identity and source run.
An inapplicable check is reported separately with its reason; it is never counted as executed.

Use `validate-ai-system --profile scoped --checks ... --reuse-evidence <run> --reuse-key-file <local-key>`
only with an explicitly selected, authenticated successful local record. The key is an existing,
owner-only unlinked file of at least 32 bytes, outside published evidence. Run with the same key
and `--evidence-file` to authenticate the initial fresh record. No key or evidence is created
implicitly. Never publish the key. MAC authentication assumes local key integrity; it does not
protect against an authorized local process that already has access to the key.

Completed zero-exit evidence is required. Failures, interruption, timeout, duplicate/incomplete
checks, tampering and wrong keys reject reuse. Changed identities execute again with a recorded
invalidation reason. Unknown checks and runtime consumers with undeclared reference closure
execute fresh. `git diff --check` always executes. HEAD is provenance, not an input by itself.
Full, CI and updater validation execute fresh in V1; no cache can weaken publication/install gates.
Fresh current-diff semantic review remains mandatory even when every eligible script is reused.

## Product Versus Runtime Artifacts

Before scripts, identify changed producers and their consumers. Status/checkpoint changes should
run applicable artifact consumers rather than unrelated product tests. Use existing scoped runtime
manifests when their complete namespace, privacy and semantic evidence requirements are met.
Unknown impact escalates. Full-required installed Workflow gates cannot be replaced by a proposal
or counterpart handoff; their explicit capability must exist and their local contract must permit it.

## Bounded Defect

One compact work record may contain approved scope, known consumers, observable DoD, reversible
fix, focused regression evidence, semantic review, outcome and capture decision. Low or medium risk
is eligible only when every criterion is explicit and the local contract permits the route.
Security, credentials, permissions, billing, migration, production, irreversible effects and
architecture changes require the broader local route. No new approval is inferred from the record.
The helper returns eligibility, not write authority. Capture is required when knowledge is reusable,
not merely because phase-shaped boilerplate could be generated.

## Quality Record And History

Start from `.systems/ai/templates/quality/execution-quality-record.template.json`. Empty required
fields deliberately fail validation; fill actual evidence, never synthetic acceptance defaults.
`prepare-quality-record --review <json>` accepts reviewer semantic fields and `input_paths`,
`evidence_paths`, `opened_contract_paths` instead of hash maps; it computes current HEAD/source
identity and fingerprints, validates against the same canonical schema, then publishes only to
the explicit new output path. `--input` validates an already complete canonical record.

`prepare-quality-record` consumes the shared typed schema in `execution_efficiency.py` and validates
before atomic no-clobber publication. The reviewer supplies semantic result, findings, DoD,
approval reference/scope and capture disposition. The producer cannot generate formal PASS,
final-owner-yes, owner-approval artifacts or unsupported Workflow formats.

Assessments are `current|historical|superseded`, bound to HEAD and source digest. Changed source
makes the assessment historical; an unchanged source digest can remain current after a commit.
Historical input fingerprints are provenance, not claims about live files; original report bytes
remain immutable and privacy/integrity checks still apply. Historical/superseded assessments cannot
satisfy current acceptance. Do not move or rewrite unrelated past QA on every source change.
Existing reports are not migrated automatically. AI Workflow owns its Phase 8 evidence schema.

## Selective Resume And Preflight

Record actual opened contracts and hashes, work ID, accepted scope/approval reference and stage.
Recheck source truth on resume; reread changed/relevant contracts and escalate unresolved conflicts.
Same-scope continuation does not repeat resolved questions or broaden approval. Installed local
refresh rules, including compaction refresh, remain controlling.
Before expensive execution verify cwd, required tools/versions, input and output containment,
timeout policy and required capabilities. Missing process-inspection permission is an environment
failure, not permission to escalate or skip tests. Environment fingerprints never expose inherited
values; local records remain private-sensitive if their paths or commands identify private work.
`validate-ai-system --plan-only` performs preflight and prints categories without executing checks;
its planned record cannot serve as success evidence. `--require-process-inspection` explicitly
probes the capability when the accepted task needs it; routine checks do not require it implicitly.

## Capability Discovery

Optional `.systems/ai/capabilities/execution-efficiency-v1.json` in the installed Workflow contains
`{"contract":1,"capabilities":{...}}`, with explicit boolean values for the names listed in the
handoff. Missing capability means `installed-local-gates`. Malformed/linked declarations stop
preflight. A capability advertises support, not an approval or waiver of the local gate.

## Process Timing

The same work record stores intervals for discovery-refresh, implementation, review, product-tests,
artifact-work, artifact-rework, owner-waiting and publication. Each includes observed/estimate,
ordered finite start/end, reason and inputs. Union overlapping intervals; do not sum child time
into wall time. Unmeasured phases are unknown, not zero. Reruns identify their changed input or gate.
No raw prompts or client data enter portable comparisons. Benchmark equivalent coverage with
three samples per variant; synthetic script savings do not prove whole-agent latency savings.


## Goal-Focused Maintenance Integration

Use goal-focused-maintenance.md only after explicit scoped activation and verified local support. One nearest-owner private maintenance/queue.json records proven independent incidental debt; project coordination references the Workflow-owned queue rather than duplicating it. E01–E05 and actual current-goal blockers are immediate. Five distinct active project causes or the third actual affected parent task schedule one consolidated milestone summary; scans/resumes do not count or repeat receipts. One stable approved parent shares TOTAL 600 seconds incidental diagnosis/edit/review/test/record work across both adapters. No background executor, scheduler or automatic TaskNotes. Required current QA and full release/updater failures remain binding. Missing counterpart support keeps existing gates; labels are not activation or authority.

A live current-goal Capture selection first inspects every sibling identity/dependency/distillation/alias claim, including invalid records. It retains full inventory and isolates only proven disjoint history; unknown/shared/duplicate/foreign claims stay blocking. Default whole-history/full validators remain exhaustive, with their actual exit codes.
