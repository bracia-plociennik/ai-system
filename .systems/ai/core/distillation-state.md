# Distillation State

## Canonical Capture Parity

`capture_parity.py` is the shared formal record/collection consumer used by `check-distillation-state` and compatibility inventory. Existing schema-1 records remain immutable historical/advisory data and do not provide current QA PASS. New formal records use `Capture schema: 2` and a `Capture Verification` JSON block with work/project/task identities, exact evidence root, source root/HEAD, current implementation QA references and fingerprints. Ready/completed require current source/input hashes and full owning task coverage. Completed additionally binds the uniquely claimed accepted owning distillation and its SHA-256. Entire owning collections, including invalid sibling claims, participate in duplicate detection; no foreign runtime is scanned.

Schema 3 is explicit opt-in only: the same consumer invokes immutable QA source-equivalence under `phase-commit-policy.md`. Unsupported target proof requires fresh QA, not saved eligibility. Historical fields are not upgraded/backfilled. Aggregated work units list their actual owning task IDs rather than pretending to be one Workflow task. Record source roots are local runtime metadata, never reusable product paths or permission.

## Purpose

Distillation State is a per-work-unit disposition that makes reusable knowledge and unresolved capture visible. It is workspace runtime evidence, not permission to write memory or a reason to modify source artifacts.

Use one state record for a coherent implementation unit. List the resulting artifacts in that record instead of adding `is_distilled` fields to client files, project repositories, source code, or every generated document.

## State Record

Every implementation-class write except an eligible micro-change must create or update a scoped state record before quality closure. The recognized approval for that implementation includes its state metadata record in the canonical nearest-owner namespace; no second approval is required for the metadata record itself.

The micro-change exception uses the exact eligibility limits in `delivery-constraints.md`: one bounded, reversible local change in at most three files including tests, with no API, schema, protocol, policy, routing, approval, privacy, permissions, security, migration, client or production state, external effect, dependency, or cross-module change. It requires focused QA and an explicit `Distillation State: micro-exempt` disposition with reason in the work response, but no per-work state file. Do not emit a synthetic `is_distilled` value for an absent record. If scope expands, create a `pending-quality` record for the entire work unit before further writes. Reusable knowledge discovered during a micro-change still follows the normal Knowledge Capture Gate.

```text
Distillation State
- Work ID:
- Work mode: <project|micro-task|micro-project|side-task|system-maintenance|client-work>
- Owner scope: <workspace|primary-entity|client|owned-asset|project>
- Scope path:
- Source artifacts:
- Quality evidence:
- State: <pending-quality|ready|completed|deferred|owner-skipped|blocked|not-applicable>
- Distillation artifact: <path|none>
- Last reminder: <timestamp|none>
- Owner disposition: <capture-now|defer|skip|blocked|not-requested>
- Privacy/scope check: <pass|fail|unknown>
- Residual risk:
```

Canonical namespaces are:

- workspace or system work: `AI_SYSTEM_WORKSPACE_HOME/capture-state/<work-id>.md`;
- standalone project: `AI_SYSTEM_WORKSPACE_HOME/project-state/<project>/capture-state/<work-id>.md`;
- client work: `AI_SYSTEM_WORKSPACE_HOME/clients/<client>/capture-state/<work-id>.md` or its nearest project-state namespace;
- owned-asset work: `AI_SYSTEM_WORKSPACE_HOME/owned-assets/<asset>/capture-state/<work-id>.md` or its nearest project-state namespace.

Do not write capture-state records into managed project repositories.

## State Semantics And Transitions

- `pending-quality`: a meaningful implementation write happened and required quality closure is incomplete.
- `ready`: quality closure passed and durable distillation is recommended or required.
- `completed`: an accepted distillation exists and is linked.
- `deferred`: the owner or workflow deferred capture with a reason and next trigger.
- `owner-skipped`: the owner explicitly rejected capture and residual risk is recorded.
- `blocked`: privacy, scope, permission, evidence, or another hard gate prevents capture.
- `not-applicable`: no reusable knowledge was produced and the rationale is recorded.

Normal transitions are `pending-quality -> ready`, `pending-quality -> not-applicable`, `ready -> completed`, `ready -> deferred`, `ready -> owner-skipped`, `ready -> blocked`, and `ready -> not-applicable`. Later implementation or changed quality evidence may return a record to `pending-quality`. Invalid transitions must be reported instead of silently rewritten.

`is_distilled` is compatibility output only. It is `true` exactly when `State: completed` and `false` for every other state. The enum is the source of truth; the derived boolean grants no permission to write, promote, commit, push, or close work.

## Producers And Consumers

- The first non-exempt implementation-class write creates or updates `pending-quality`.
- Quality closure moves the record to `ready` or justified `not-applicable`.
- An accepted distillation moves it to `completed` and records the artifact path.
- For `.systems/ai/core/project-orchestration.md`, an accepted distillation in the target AI Workflow project may be the referenced artifact. Verify its existence, target scope, and acceptance evidence before recording `completed`; do not make a duplicate technical distillation in AI System.
- Task intake reports unresolved records for the selected scope before unrelated new implementation.
- End-of-Task Capture, contract compliance, and checkpoints report unresolved state and owner action.
- Dreaming reads state records and reports an Undistilled Work Queue only.

Unresolved state is advisory and does not automatically block a new work unit, but it must not be hidden.

## Dreaming Boundary

Dreaming reports counts by state, privacy-safe workspace-relative state/source paths, quality evidence, proposed distillation target, blocker, owner action, and residual risk. It does not change state, create distillation, write memory, write External Memory or System Insights, create TaskNotes, update status, commit, push, or run scheduler automation.

For sensitive scopes, report the safe state-record path and omit or anonymize private source path components.

## Bootstrap And History

`init-workspace` and `update-workspace` create only the neutral top-level `capture-state/README.md` and `capture-state/capture-state.md`. Per-work and nearest-owner records are created only with approved implementation work.

Do not backfill historical work automatically. Work completed before this contract is invisible to the queue until the owner approves a separate audit or backfill.

`check-distillation-state --workspace` inventories only the canonical AI System namespaces listed above. It does not recursively scan managed project repositories, nested AI Workflow runtimes, or product templates. A `capture-state/` directory directly inside a managed repository remains a placement error. The checker reports invalid records separately from unresolved valid states; an invalid state must not disappear into a zero-unresolved summary.

For existing canonical records, a single pair of Markdown backticks around a field value and a semicolon-delimited note after `Privacy/scope check` are presentation syntax, not a different state. `is_distilled` is derived from `State`; if the compatibility field is present it must agree, but an older record may omit it. A relative distillation artifact path resolves against the AI System workspace root or the record's nearest-owner root; missing, ambiguous, or out-of-workspace targets fail. This compatibility rule does not rewrite historical files, infer a missing `State`, or admit records from foreign runtimes.

## Privacy And Scope

State records contain paths and workflow metadata only. Do not copy raw client data, secrets, credentials, private keys, production data, check-in content, or project-specific domain content into cross-project reports.
