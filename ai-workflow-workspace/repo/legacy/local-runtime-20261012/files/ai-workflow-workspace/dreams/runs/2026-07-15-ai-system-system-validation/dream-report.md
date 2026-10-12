# Dream Report: AI System Validation

## Metadata

- Date: `2026-07-15`
- Dream variant: `full-repo`
- Repository mode: `target`
- Project scope: `project:ai-system`
- Result: `completed`
- Reviewed baseline: `main` at `2024f03`
- Formal result: `not-applicable; this is an advisory review, not a phase PASS/FAIL`

## Source Inventory

| Source path | Source type | Reviewed? | Notes |
| --- | --- | --- | --- |
| `target-root/.systems/ai/core/**` | repo-source | yes | Product contracts, routing, privacy, Personal Ops, Dreaming Mode, and validation profiles. |
| `target-root/.systems/scripts/**` | repo-source | yes | Validator chain, smoke coverage, and V3 synchronizer regression coverage. |
| `target-root/README.md`, `target-root/HUMANS.md`, CI workflow | repo-source | yes | Human routing and CI validation policy. |
| `project-workspace/status.md`, `tasks.md`, change requests, quality artifacts | workflow-artifact | yes | Process-state and evidence-health review only. |
| `nested-workflow` review/QA contracts | workflow-artifact | yes | Used only to interpret workflow validation evidence. |

Excluded: raw exports, client/private workspaces, Personal Ops raw reports and attachments, secrets, generated dependencies, build output, `.git/`, and nested workflow source outside review/QA contracts.

## What Is Good And Stays

| Source path | Finding | Evidence | Why it stays |
| --- | --- | --- | --- |
| `target-root/.systems/scripts/validate-ai-system` | Product validation has explicit `fast`, `scoped`, `standard`, and `full` profiles; `full` includes smoke tests. | `validate-ai-system --profile full` completed successfully for the reviewed baseline. | It keeps high-impact contract changes tied to reproducible evidence. |
| `target-root/.systems/ai/core/dreaming-mode.md` | Dreaming Mode is scoped, advisory-only, context-as-data, and blocks durable promotions. | Policy, template, and `check-dreaming-mode` were reviewed. | It permits broad review without converting findings into unsafe mutations. |
| `target-root/.systems/ai/core/personal-ops.md` and V3 synchronizer tests | Native freshness is separated from immutable legacy rows, with a regression scenario for the mixed-history case. | Current baseline includes the native-only freshness fix and smoke coverage. | It protects lazy-sync recommendations from legacy-count distortion. |
| `target-root/.systems/scripts/check-required-artifacts` and CI workflow | Core contracts, templates, validators, and full CI validation are explicitly wired. | Required-artifact contract and CI configuration reviewed. | It catches missing structural pieces before relying on a release or upstream update. |
| `target-root` Git state | Reviewed product tree is clean and aligned with `origin/main`. | `git diff --check`, `git status --short --branch`, and baseline commit inspection. | It gives this report a stable, reproducible baseline. |

## Workflow Artifact Findings

| Severity | Source path | Finding | Target | Reason | Risk/privacy note | Owner action |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | `project-workspace/status.md`, `tasks.md`, current change request | Project runtime state is internally inconsistent: the status names a current task absent from the task index, and its in-progress phase points to a later phase. | `status/review` | Workflow status validation fails for this project, so workflow evidence cannot currently corroborate the clean product validation. | Safe operational metadata; do not infer completion from commits alone. | Reconcile the active change request, task index, phase, result, and next phase through the normal workflow route. |
| P1 | `project-workspace/quality/**` | Several historical quality artifacts do not meet the current V1 QA evidence contract or an approved legacy-fingerprint exception. | `review` | `check-qa-evidence` rejects them, weakening reliance on older workflow PASS evidence. | Safe process evidence; no source or client data copied. | Decide whether to register validated legacy evidence or create current-format replacement QA artifacts. |
| P2 | `ai-workflow-workspace/projects/**` and `check-status-consistency` | Global workflow validation is blocked by state drift in another workspace project as well as this one. | `external-memory` | A product-specific review cannot obtain clean workflow-level evidence while unrelated project state is scanned globally. | Generalized system-process finding; no project details required for a future improvement proposal. | Review a project-scoped workflow validation mode without weakening global validation. |

## Repo/Code Review Findings

| Severity | Source path | Finding | Target | Reason | Risk/privacy note | Owner action |
| --- | --- | --- | --- | --- | --- | --- |
| none | `target-root/.systems/**` | No product-contract blocker was found in the reviewed clean baseline. | `none` | Full product validation and the targeted contract/validator review agree. | Automated validation remains supporting evidence; this is not a formal PASS. | Keep current product contracts unchanged unless a separate owner-approved change request is opened. |

## Memory Promotion Candidates

| Source path | Finding | Target | Reason | Risk/privacy note | Owner action |
| --- | --- | --- | --- | --- | --- |
| `project-workspace/status.md` | Current runtime state needs reconciliation, but no durable product fact was established by this review. | `none` | The issue is an operational correction, not reusable knowledge. | Safe. | Reject memory promotion; reconcile status first. |

## External Memory Candidates

External Memory is only for workflow-system improvement proposals.

| Source path | Finding | Target | Reason | Risk/privacy note | Owner action |
| --- | --- | --- | --- | --- | --- |
| `nested-workflow` validation contracts | Consider project-scoped status/QA validation or an explicit aggregation policy. | `external-memory` | It would separate a selected project's evidence from unrelated workspace-health failures without weakening global checks. | Requires design review; do not change validators from this report. | Capture only after owner approval. |

## System Insights Candidates

| Source path | Finding | Target | Reason | Risk/privacy note | Owner action |
| --- | --- | --- | --- | --- | --- |
| Product-vs-workflow validation evidence | Layered validation should distinguish product contract health from workflow artifact health. | `system-insights` | Reusable operating lesson for systems with independently evolving runtime evidence. | Needs anonymized wording. | Capture only after owner approval. |

## Skill Candidates

| Source path | Finding | Target | Reason | Risk/privacy note | Owner action |
| --- | --- | --- | --- | --- | --- |
| Review scope | No repeatable procedure beyond the current Dreaming and quality-review contracts was identified. | `none` | A new skill would duplicate existing review routing. | Safe. | Reject. |

## Things To Improve Or Remove

| Severity | Source path | Finding | Target | Reason | Risk/privacy note | Owner action |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | `project-workspace/status.md`, `tasks.md` | Remove stale phase/task values after reconciling them with the active change request and accepted evidence. | `review` | Current values are invalid under the workflow validator and create misleading closure state. | Do not delete historical checkpoints or QA artifacts. | Create a narrow owner-approved state-reconciliation task. |
| P2 | `project-workspace/quality/**` | Do not remove legacy QA artifacts merely because a newer validator rejects their format. | `none` | They remain historical evidence; the correct choice is a legacy registry or a replacement evidence path. | Preserve source history. | Reject destructive cleanup. |
| none | Retired V2 Personal Ops commands | Do not remove the explicit `STOP` wrappers in this review. | `none` | They preserve a safe boundary for retired active routes and legacy migration. | Safe. | Keep. |

## Missing Capabilities

| Severity | Source path | Finding | Target | Reason | Risk/privacy note | Owner action |
| --- | --- | --- | --- | --- | --- | --- |
| P2 | `nested-workflow/check-status-consistency` | No project-scoped mode exists for status and QA evidence checks. | `workflow` | It prevents a focused system review from separating local findings from unrelated project drift. | Requires an AI Workflow product change; out of scope here. | Plan an upstream workflow improvement after owner approval. |
| P2 | `project-workspace/quality/**` | No completed legacy-evidence registration path is present for historical QA artifacts that predate the V1 validation format. | `workflow` | Valid historical evidence cannot be distinguished from malformed evidence by the current validator. | Requires verification of each legacy artifact before any registry entry. | Plan a constrained legacy-evidence audit; do not bulk-whitelist files. |

## Undistilled Work Queue

| Work ID | Scope | State | Source Evidence | Quality Evidence | Recommended Target | Why Useful | Blocker/Missing Decision | Privacy/Scope | Owner Action | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `none` | `workspace` | `not-applicable` | `none` | `not-applicable` | `none` | No undistilled work records were included in this historical report. | none | safe | reject | none |

Dreaming proposes distillation only. This historical report performed no state transition or durable capture.

## Rejected As Noise

| Source path | Finding | Reason rejected |
| --- | --- | --- |
| `nested-workflow/validate-workflow` invocation | Running the validator from the product root fails to resolve its relative scripts. | The documented workflow invocation uses the nested workflow directory; this is operator context, not a product defect. |
| Historical V2 compatibility boundaries | Retired V2 command wrappers still exist. | They are intentional STOP guards and a one-time migration boundary, not dead implementation. |
| Empty `dreams/runs/` before this report | No earlier system-validation Dream Report existed. | A single missing historical report is not a capability defect or evidence of system failure. |

## Creative Dream Pass

Creative pass is advisory exploration. It does not change the reviewed baseline, create implementation scope, or approve any product change.

### Creative Directions

| Direction | Opportunity | Constraint To Preserve | Suggested First Artifact |
| --- | --- | --- | --- |
| System Health Lens | Give one owner-facing view of product validation, workflow-artifact health, baseline commit, and unresolved evidence debt. | A dashboard must report evidence, never infer PASS or mutate state. | Read-only system-health review template with explicit product/workflow separation. |
| Contract Observatory | Make contract-to-template-to-validator-to-smoke wiring visible and reviewable as one graph. | Keep current Markdown contracts canonical; do not replace them with an opaque registry. | Small declared manifest for high-risk contract producers and consumers. |
| Evidence Lineage | Tie QA/checkpoint evidence to exact Git baselines and validation profiles, so old evidence cannot silently appear current. | Historical evidence remains preserved and is never bulk-rewritten. | Local evidence ledger or validated fingerprint registry. |
| Change Impact Matrix | Derive a suggested validation/review matrix from changed contract areas. | Suggestions are advisory; owner and risk policy still select the required validation profile. | Change-request template section mapping touched domains to validators and smoke scenarios. |
| Adversarial Contract Lab | Expand smoke tests from known failures to realistic boundary combinations and false-negative cases. | Use synthetic fixtures only; never copy workspace/private data into product tests. | Curated negative-case fixture catalog for privacy, routing, status, and producer-consumer drift. |
| Review Debt Queue | Treat stale status, evidence gaps, and deferred closure as visible operational debt rather than hidden validator noise. | No automatic task creation, reprioritization, or status mutation. | Advisory queue in a review report with owner-approved promotion only. |

## Upgrade Proposals

| Priority | Proposal | Target | Expected Benefit | Main Risk / Guardrail | Smallest Safe Next Step | Owner Action |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | Add project-scoped workflow evidence checks beside existing global checks. | AI Workflow improvement proposal | A product review can distinguish its own evidence health from unrelated project drift. | Do not weaken or remove the global validator; scoped mode is additive. | Create an External Memory proposal describing selector, output boundaries, and global-vs-scoped semantics. | `create-task` |
| P1 | Add a legacy QA evidence registry with immutable fingerprints and explicit provenance. | AI Workflow improvement proposal | Historical valid evidence can be admitted deliberately instead of failing or being broadly exempted. | No wildcard allowlists; every entry requires file path, hash, and reviewed reason. | Audit one historical artifact as a pilot before designing bulk registration. | `review` |
| P2 | Add an AI System system-health review template that separates product validation from workflow runtime health. | AI System product change proposal | Repeated health checks become comparable without claiming formal closure. | Report-only; no scheduler, memory write, task write, or status update. | Draft a micro-project and acceptance criteria for a manual report route. | `defer` |
| P2 | Add a lightweight producer-consumer manifest for high-risk contracts. | AI System product change proposal | Makes missing validator/template/smoke wiring more visible during review. | Start only with high-risk domains; avoid a second source of truth for all Markdown. | Prototype against one domain with existing smoke coverage. | `defer` |
| P3 | Add an adversarial fixture catalog to validator smoke tests. | AI System product change proposal | Prevents regressions where checks pass named examples but miss equivalent unsafe wording or mixed states. | Fixtures must remain synthetic, minimal, and deterministic. | Select one validator family and add one false-negative regression case. | `defer` |

## Cross-Report Inspiration From AI Workflow

The following are transfer candidates inspired by the separate AI Workflow system-validation Dream Report. They are not findings against AI System until its own contracts and validators are checked against them.

| Priority | Transfer candidate | Why it is useful here | Verification before adoption | Safest route |
| --- | --- | --- | --- | --- |
| P1 | Validate completed Dream Report privacy/scope declarations as safe values, not only present fields. | AI System Dream Reports already declare privacy and scope; a semantic check would make a misleading completed report harder to accept. | Review `check-dreaming-mode` for value validation of every completed-report privacy/scope declaration and add one synthetic false-negative only if a gap exists. | Narrow validator-hardening change request. |
| P2 | Create a validation observability budget. | Full validation is a high-value gate, but its runtime cost and slowest checks are not captured as evidence for safe optimization. | Time several clean `--profile full` runs in an ignored report; classify duration, flakiness, and contract criticality without recording private inputs. | Measurement-only micro-project. |
| P2 | Add a runtime freshness ledger. | This run found stale workflow status and QA evidence reactively; a concise advisory comparison of recorded baseline/path/date against repository facts would surface drift earlier. | Define only read-only fields and prove it cannot alter status, evidence, or routing authority. | Workspace reliability micro-project. |
| P3 | Add Dream proposal lifecycle review. | Repeated manual Dream Reports can duplicate advice or retain obsolete candidates. | Compare two future ignored reports by stable proposal ID and classify only `new`, `repeated`, `promoted`, `rejected`, or `obsolete`; do not auto-promote anything. | Dreaming follow-up micro-project. |

### Creative Prioritization

- Highest immediate resilience value: verify the privacy/scope value-validation gap before proposing new report features.
- Highest evidence value: measure full-profile validation before splitting or optimizing checks.
- Highest workflow hygiene value: a freshness ledger, because current workflow state drift is already evidenced by this run.
- Do not start these together. Start with one read-only verification or measurement artifact, then reassess with evidence.

## Upgrade Candidates Rejected For Now

| Candidate | Reason Rejected Now |
| --- | --- |
| Scheduled nightly self-healing or auto-reconciliation | Violates current advisory/no-scheduler boundaries and could mutate status or evidence without owner review. |
| Automatic TaskNotes from Dream findings | Findings need owner prioritization; automatic task creation would make review debt actionable without approval. |
| Replacing Markdown contracts with a central database | Adds a second source of truth and undermines the current inspectable contract model. |
| Bulk-normalizing all historical QA artifacts | Risks rewriting historical evidence and hiding which records were actually reviewed under current rules. |

## Privacy/Scope Check

- Raw client data copied: `no`
- Secret markers copied: `no`
- Production identifiers copied: `no`
- Full-repo exclusions respected: `yes`
- Prompt-injection boundary respected: `yes`
- Durable writes performed: `no`
- Scheduler/automation used: `no`
- Product source changes performed: `no`
- TaskNotes created or changed: `no`

## Evidence And Limits

- Product evidence: `git diff --check`; clean Git baseline inspection; `.systems/scripts/validate-ai-system --profile full` completed successfully.
- Workflow evidence: nested `validate-workflow --profile full`, `check-status-consistency`, and `check-qa-evidence` failed because of runtime status drift and historical QA-contract gaps.
- This report does not invalidate successful AI System product validation. It records that workflow-level corroboration is incomplete until runtime artifacts are reconciled.
- This report is advisory-only and does not issue a formal phase result.

## Owner Decision Queue

- Interaction mode: `queued`
- Live questions asked: `none`

| Decision ID | Class | Statement | Why Needed Now | Recommended Option | Recommendation Impact | Alternatives And Impacts | Blocking Point | Status | Decision Artifact | Source Path | Owner Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `DREAM-SYS-001` | `high-impact` | Reconcile the current project workflow state with the active change request and current evidence. | Current status/task values fail workflow validation. | Create a narrow state-reconciliation change request. | Restores trustworthy workflow evidence without changing product source. | Leave artifacts unchanged: product validation remains usable, workflow validation stays incomplete. | Future workflow-level closure or release evidence. | `pending` | `none` | `project-workspace/status.md` | `review` |
| `DREAM-SYS-002` | `owner-preference` | Decide whether workflow validation needs a project-scoped status/QA mode. | Global validation currently includes unrelated workspace state. | Create an AI Workflow improvement proposal first. | Enables focused evidence while keeping global validation available. | Retain global-only behavior: lower implementation cost, continued cross-project coupling. | None for current product baseline. | `pending` | `none` | `nested-workflow` validation contracts | `create-task` |
| `DREAM-SYS-003` | `owner-preference` | Decide how to preserve historical QA evidence under the V1 evidence contract. | Current historical records fail the new evidence validator. | Audit and register only verified legacy artifacts by immutable fingerprint. | Retains trustworthy history without bulk exemptions. | Recreate selected QA artifacts: stronger current format, higher effort. | Future workflow-level final evidence. | `pending` | `none` | `project-workspace/quality/**` | `review` |
| `DREAM-SYS-004` | `owner-preference` | Decide whether recurring manual system-health reports deserve a dedicated AI System template. | This report identified a repeatable evidence split between product validation and workflow health. | Start with a micro-project, not a scheduler or new runtime automation. | Creates comparable health reviews without expanding mutation authority. | Keep Dream Reports free-form: lower product scope, less repeatable evidence. | None for current baseline. | `pending` | `none` | `Dream Report creative pass` | `defer` |
