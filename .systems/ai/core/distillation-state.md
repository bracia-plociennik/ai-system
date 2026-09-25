# Distillation State

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

## Privacy And Scope

State records contain paths and workflow metadata only. Do not copy raw client data, secrets, credentials, private keys, production data, check-in content, or project-specific domain content into cross-project reports.
