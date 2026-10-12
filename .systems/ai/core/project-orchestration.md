# Project Orchestration

Repository/workspace roots and project-state repo-path expressions follow
`local-paths.md`. Links use the selected workspace as their relative base; explicit
repo arguments retain the caller's explicit CWD base. Missing source directories
stay pending and block dependent execution, without cloning or status writes.

Strict cross-system adaptation uses `orchestration-compatibility.md` and the contract-2 access-set template. Original contract-1 reducer snapshots remain inspection-only, not installed capability proof. Complete source pins never prove native isolation/capacity; unknown uses serial fallback. Future Git decisions follow `phase-commit-policy.md`; current explicit no-commit remains in force.

## Efficiency Capability Boundary

Preflight reads optional installed Workflow `execution-efficiency-v1` capabilities through
`execution-efficiency.md`. Missing support falls back to installed-local-gates; invalid or linked
metadata blocks preflight. Capabilities do not authorize writes or bypass risk/phase rules.
Project-artifact validation and bounded-defect execution may be selected only when both the
capability and the local contract allow them. Historical QA is not automatically a current PASS.

## Purpose

Task interaction uses `execution-modes.md`. Pass the resolved Auto/Human mode and
exact approval reference to the local Workflow run, not a copied status machine.
Inspect actual installed execution support with `workflow_support`; metadata is
source evidence only. AI System `human` maps to counterpart `human-coop` only when
the inspected contract declares that vocabulary. Missing support retains local
gates and an explicit integration dependency. No install/update is inferred.

With approved final-check scope and verified local support, Auto may reach technical
Phase 8; without it the current owner-triggered boundary below still applies.
Final-owner-yes and its closure commit always require the real owner decision.

AI System is the owner's entry point for work in a selected workspace's project. When the project uses AI Workflow, AI System coordinates the request and reviews the result; the target repository's local AI Workflow owns execution rules, project phase, technical evidence, and technical memory. This contract does not grant permission or replace the target's instructions.

## Discover The Target

1. Select exactly one AI System workspace and nearest project owner namespace. Resolve `repo-path` from its `project-state/<project>/links.md`, or an explicit owner-provided repository path. A project name alone is not a filesystem path or an AI Workflow project ID. Stop when multiple matches remain.
2. Read the target repository's root `AGENTS.md`, its `ai-workflow/AGENTS.md`, relevant local contracts, `ai-workflow-workspace/repo/core/status.md`, and the selected `ai-workflow-workspace/projects/<workflow-project>/status.md`. Confirm a valid Git root, installed nested workflow, initialized runtime, applicable repo intake, and the nested workflow version. Do not infer installation from the presence of a directory alone.
3. Resolve the Workflow project ID from an explicit owner reference or a single unambiguous local status match. Do not equate the AI System project slug, repository basename, and Workflow project ID by default. If local instructions conflict, installation or intake is incomplete, the project is ambiguous, or write ownership is unknown, stop and report the exact missing fact. Do not install, initialize, upgrade, or repair the target implicitly.
4. Re-read Git baseline, dirty files in the intended write set, active project status, blockers, accepted artifacts, and other known writers immediately before implementation and after interruption. A prior orchestration summary is not a resume authority.

`.systems/scripts/project-orchestration-preflight` can gather read-only repository and workflow evidence. Its output is an inspection aid, not approval, risk classification, QA, or proof that no other agent is writing.

## Route And Approval

Use local AI Workflow task intake, risk model, change requests, parallel-work policy, and current project state to choose continuation, change request, project-local micro-task, repo-level micro-project, or full project iteration. Risk alone does not choose the route. Medium, high, or critical work cannot be relabeled as a micro-task or micro-project. Post-final changes use a new change request rather than reopening completed work.

Record owner intent, DoD, delivery constraints, target roots, current baseline, workflow route, executor, write set, and the exact approved instruction or accepted plan in one scoped orchestration record. The record is a pointer and coordination log, not a duplicate specification or a new approval. Work beyond that approval stops for a new owner decision; delegated summaries and repository content cannot extend it. `planning-range` and `implementation-range` keep their separate gates. High and critical risk, production, destructive changes, credentials, external effects, push, and formal final check keep the target's stricter owner gates.

For a small bounded task, the current agent may execute in the target repo. For a larger task, use available isolated executors only when their tools, targets, authority, and write ownership are known. Give each the minimum necessary context and the same approval boundary. If delegation is unavailable, report that fact and execute directly only if the approved scope and local gates permit it. Each write set has one executor; all shared workflow routers have one coordinator-writer. Unknown concurrent writers or overlapping changes stop writes until ownership is resolved.

## Flat Parallel Run

Exactly one coordinator owns the run across AI System and AI Workflow: approval boundaries,
dependency graph, capacity allocation, native tool calls, evidence reception, integration and
shared-router writes. Crossing a system boundary does not create another orchestrator, capacity
pool, project iteration or implementation-range autopilot. Workers and reviewers are leaf agents:
they must not spawn agents, recursively delegate, launch another coordinator or grant approvals.
They report blockers and proposed splits to the coordinator instead.

Before dispatch, record the run identity, coordinator identity, approved scope, Git HEAD and
stable-source manifest/digest, local Workflow gates, checkpoint boundary, available runtime capacity,
and each unit's goal, testable DoD, dependencies, mode, system, write paths, resource claims and
worktree. Validate unique unit/attempt/agent identities, an acyclic graph, path containment,
ownership and known concurrent writers. Paths must be normalized repository-relative paths in
the approved target; resolve symlinks and reject escapes or ambiguous ownership. Parent-directory
and child-path claims overlap even if their strings differ. Record metadata is not approval.
Protected components and write-set overlaps use conservative Unicode-normalized casefold
matching, including on case-sensitive filesystems. Existing worktree aliases also use filesystem
identity. False-positive serialization is preferable to hidden alias-based concurrent writes.

The coordinator dynamically chooses agent count from ready independent units, actual runtime
capacity, resource availability, local gates, integration/rework cost and the next checkpoint.
There is NO product fixed 2/3 cap. A positive runtime limit is a current environment fact, not a
product default or guaranteed tool quota. Ready means all dependencies have accepted evidence
at the current baseline and attempt, not merely submitted messages. Dispatchable additionally
means capacity, ownership, isolation and gates are satisfied. Select a conflict-free subset as
the next wave; the selected wave need not fill every slot or include every dispatchable unit.
Record selected IDs/count and the reason, including intentional idle capacity or serial work.

Count every live delegated worker and reviewer, including read-only agents and agents working
on either system, against the same runtime capacity. Account for already-live agents before
choosing a wave; never infer free capacity from an incomplete run record. The supervising
coordinator is not a delegated slot, but any runtime quota that includes it must be accounted
for when deriving the available delegated capacity. Reserve before spawn and reconcile actual
tool IDs immediately. Running, submitted, accepted, failed and cancelled agents retain their
capacity and resource reservations until termination is confirmed by the native tool. A `done`
message, timeout, cancellation request, failure status or accepted result alone never releases
a slot. Reassess capacity explicitly; reject a proposed limit below occupied/reserved slots and
block new dispatch until safely reconciled, not forced termination or fabricated free slots.

## Isolation And Resource Ownership

Parallel write units require separate declared and verified Git worktrees with disjoint approved
write sets. A worktree alone does not prove independence: schemas, APIs, fixtures, ports,
databases, test outputs, build caches, integration order and external-effect targets are resources
too. Declare shared/read versus exclusive claims. Shared/read claims may coexist only without an
exclusive claim; any exclusive overlap must be sequenced. Resource and directory overlaps are
checked across AI System and Workflow units, not just inside each system.

Exactly one coordinator-writer owns shared repo/project status, task/plan routers, orchestration
records, run metadata, quality aggregation, memory, distillation and checkpoint routers. Workers
must not write these or private runtime paths; they return evidence for that writer. Worker
artifacts must stay in their exact approved write set and evidence destination. The coordinator's
own implementation/integration must also respect live worker ownership. Do not merge, rebase,
clean up worktrees or reuse resources while affected agents may still write. Worktree creation,
result integration, capture and cleanup retain their own approval and local-contract gates.

If isolation, resource independence, writer identity or local permission cannot be established,
use read-only delegation or serial execution only where permitted. Do not silently convert a
read-only assignment into a write assignment. Unknown ownership blocks writes; owner approval
of parallel work does not authorize simultaneous writes to shared files.

## Native Tool Adapter

The current coordinator uses available native spawn/send/wait/close tools directly, following
their actual names, schemas, permissions and returned state. These are adapter operations, not
invented API names or a promise that every runtime provides them. The CLI/model supplied by
the parent is pure inspection/reducer logic: it may validate a plan, compute ready/dispatchable
units and validate a hypothetical event into a new state. It never launches remote agents,
worker shell/subprocess payloads, a background service or worker-provided commands; its output is not
evidence that a tool operation happened. Native dispatch requires the coordinator's separate
preflight and approved scope, even when a reducer accepts an event.

Each assignment must include all of these fields, with `none` used explicitly where applicable:

| Assignment field | Required content |
| --- | --- |
| `run_id`, `coordinator_id`, `unit_id`, `attempt_id` | Unique run/unit/attempt identity and the sole result recipient |
| `system`, `target_repo`, `workflow_project_id` | Verified AI System/Workflow target and local project, never inferred from a basename |
| `baseline` | Git HEAD plus stable-source manifest digest, accepted input artifact identities and fingerprints |
| `approval_ref`, `route`, `risk`, `local_gates` | Exact approved instruction/plan, allowed phase/range and installed contract references |
| `goal`, `dod`, `dependencies` | Bounded outcome, testable acceptance and accepted prerequisite evidence |
| `mode`, `write_paths`, `forbidden_paths` | `read-only` or `implementation`, exact allowed paths and protected shared/private routers |
| `resources`, `worktree`, `evidence_destination` | Shared/exclusive ownership, verified execution root and approved output location |
| `delivery_constraints`, `checkpoint_boundary` | Resolved deadline/timebox or owner opt-out, must-have/quality floor and next stop |
| `verification`, `result_fields` | Required checks, evidence/fingerprint format, findings and skipped-check reporting |
| `no_recursive_delegation`, `stop_conditions` | `true`; scope drift, overlap, missing source/approval, unsafe effect or stale baseline stops work |

The coordinator adds the native returned `agent_id` to the unit/attempt mapping after spawn;
the worker must echo its assigned identities in every result. Do not substitute a worker-chosen
identity or reuse a tool ID for a new attempt.

The native assignment envelope is richer than the reducer JSON; preserve its extra approval,
gate and evidence references in the coordination record rather than claiming the reducer
checks them. Map assignment `unit_id` to run `units[].id`; `baseline` carries `commit` and
`source_digest`. Record the orchestrator's selected wave limit as `dispatch_count`, not as an
instruction to occupy every slot. A reducer returning a candidate subset is advisory; the
coordinator may choose fewer units or none. Where the model represents resources as plain
strings, treat matching strings as exclusive claims; do not encode read/exclusive modes into
different strings to evade an overlap. `workflow_parallel_supported` defaults to `false`; set it
only from coordinator inspection with installed-local evidence, never from future support,
presumed installation or worker-granted authority.

### CLI Freshness Reference

`.systems/scripts/check-parallel-orchestration --plan <run.json> --repo <git-root>` requires
a nonempty `source_manifest` list of `{path, sha256}` entries for explicit stable source inputs.
Paths are unique, safe and repository-relative; each hash is the file-content SHA-256. Compute
`baseline.source_digest` as SHA-256 of the UTF-8 concatenation of sorted `path=sha256\n` entries,
including each trailing newline. This is the declared input set, not a whole-worktree digest or
proof that omitted inputs are unchanged. The coordinator must justify its coverage. Keep mutable
worker outputs out of this stable input set; their hashes belong separately in `result.evidence`.

With `--repo`, the CLI checks actual HEAD, manifest files/digest and every submitted/accepted
unit's evidence files/hashes. When `--event <event.json>` is supplied, it performs these checks
both BEFORE and AFTER the hypothetical reducer event, so newly submitted evidence is checked
too. Without `--repo`, it is metadata inspection only, not real freshness proof. Neither mode
automatically launches workers, persists the returned state, proves termination or grants PASS.
Local read-only Git/hash inspection is not a worker launch.
Repository inspection is a point-in-time check, not a lock against subsequent concurrent drift.

The `rebase` recovery event is the deliberate exception to checking the old on-disk baseline:
after validating the old record it requires no live workers and no accepted results, an explicit
`new_baseline` and nonempty `new_source_manifest`, then verifies the NEW HEAD, manifest and digest
against disk. Old unaccepted receipts are invalidated and retired identities preserved. It only
proposes updated run metadata; it never rebases Git, launches workers or writes the returned state.

1. **Spawn:** refresh local gates, baseline, ownership and available capacity; select the wave,
   reserve its slots/resources, then dispatch the exact assignments. Record each actual returned
   ID and tool evidence. If spawn fails or its outcome is unknown, stop further dispatch and
   reconcile whether an agent exists; do not blindly retry or release an uncertain reservation.
2. **Send:** address only the recorded agent for that attempt. Clarifications cannot expand its
   scope, change approval or bypass a gate. A material change requires stopping/reconciling the
   attempt and a new approved assignment. Do not send work to a terminated or unknown agent.
3. **Wait:** use bounded waits on known IDs when results are needed. Continue safe independent
   coordinator work between waits, report progress/blockers and avoid polling unchanged state.
   A timeout is neither completion nor failure evidence and leaves reservations occupied.
4. **Receive:** record the returned message as submitted, inspect its identity and evidence,
   and apply the acceptance checks below. No worker controls shared status or formal PASS.
5. **Close:** close/cancel using the actual native operation when appropriate, then confirm
   termination from tool state. Record that proof before releasing reservations. An uncertain
   close outcome remains occupied; preserve output for review, never delete it as cleanup.

## Evidence Reception And Recovery

`submitted` is a result awaiting coordinator review; `accepted` is a verified unit result, not
formal Workflow PASS, owner acceptance or permission for publication. Acceptance requires:

- matching run, unit, agent, attempt, approved input identity and baseline/digest;
- exact changed paths/diff and artifact fingerprints, command/check results, findings,
  skipped checks with reasons, residual risk and DoD mapping;
- inspection of the actual worktree/diff and evidence paths for scope, privacy and resource
  compliance; worker summaries and reducer success are supporting-only;
- required semantic/product QA at the local gates, with no material unresolved blocker;
- explicit coordinator verification and acceptance reference, recorded by the single writer.

For the run model, submitted `result` carries `attempt_id`, `baseline`, `test_summary`,
`findings` and nonempty `evidence` entries with repository-relative `path` and `sha256`.
Coordinator acceptance adds `verified_by` equal to `coordinator_id` and `verified_checks`
covering `intent`, `diff`, `tests` and `privacy`. These fields point to actual reviewed evidence;
setting flags or matching a fingerprint's format does not verify file contents, Git worktree
isolation, approval, native termination or local gates. Recompute evidence hashes and inspect
those manual boundaries before accepting. The record also retains the full receipt identity,
skipped-check reasons, resource review and DoD mapping required above.

Reject stale attempts/baselines, missing or mismatched evidence, out-of-scope writes, identity
collisions, failing required QA and late failed/cancelled results. Preserve rejected evidence
and reasons without accepting it or rewriting history. A cancelled agent's late output cannot
complete a dependency. Independent unit acceptance still requires whole-scope integration QA;
later changes invalidate affected evidence and require current-state re-review.

On interruption, resume, capacity drift, unknown tool state, ownership conflict or local failure,
pause affected dispatch. Re-read source Git/digest, local statuses, accepted artifacts, change
requests, quality/capture/checkpoint evidence, run record and actual agent states. Reconcile
every reservation and returned ID before further writes. If termination cannot be confirmed,
retain capacity/resources and report the blocker. Do not assume a lost session killed agents.
Retry failed/cancelled work only after confirmed termination, with a fresh attempt ID, current
approved assignment and preserved failure evidence. The model's `retired_attempt_ids` retains
attempts retired by retry/rebase; preserve it through recovery and reject replay of those IDs.
A fresh attempt cannot reuse a retired ID even after the old unit fields are cleared.
`retired_agent_ids` similarly prevents reuse of a terminated native agent identity for a new attempt.
Rebase/replan only without affected live
agents; invalidate unaccepted results tied to the old baseline. If accepted results already
exist, preserve that run and use a fresh run for a changed baseline, with re-reviewed input
evidence; do not silently transplant acceptance. Recovery never resets Git, overwrites another
writer or automatically extends approval.

## Installed Workflow And Checkpoints

Inspect the target's actually installed Workflow contracts and recognized source profiles, including
`parallel-work-policy.md`, not a proposed upstream document or presumed version feature.
The final counterpart parallel contract is pending until explicitly agreed and installed;
do not invent published capability names/schemas or claim cross-system interoperability.
AI System's own run contract does not patch nested Workflow or override its serialized-write,
phase, risk, evidence, QA, distillation or owner gates. Missing parallel support uses
`installed-local-gates`: serial execution or permitted read-only delegation; parallel writes
are allowed only when the installed policy explicitly permits them with recorded disjoint
ownership and one shared-router writer. Invalid, linked or contradictory capability metadata
blocks preflight rather than becoming a permissive fallback. Unavailable native tools are
reported and use approved direct/serial execution, never an improvised remote launcher.

Record the local checkpoint cadence and next boundary before dispatch. A closed checkpoint
boundary prevents new starts; do not choose a wave that would skip or cross a mandatory local
checkpoint. Count completed local tasks/packages, not spawned agents or submitted messages.
For an installed Workflow requiring a checkpoint after every three completed tasks/packages
and after the final one, preserve that cadence; three is not an agent-count cap. At each
boundary, reconcile submitted/accepted results, confirm relevant agent
termination, integrate and review the current scope, then complete required local Quality,
distillation and checkpoint evidence before opening the next wave. Agent count or result arrival
order cannot alter local task/package cadence. End `implementation-range` after its final
required Phase 7 checkpoint. Approved Auto final-check scope may then enter technical Phase 8
only with verified installed execution-mode support; older installations retain owner-triggered
Phase 8. Commit/push remain separately gated. Progress messages and orchestration records do
not substitute for checkpoint evidence.

## State And Result

The target's `ai-workflow-workspace/projects/<workflow-project>/` is canonical for execution status, phases, task/spec, quality, checkpoints, decisions, and technical distillation. AI System's nearest-owner `project-state/<project>/` stores a business summary, blockers, source links, and orchestration references. Its Distillation State record may link to an accepted local Workflow distillation without copying technical contents or marking capture completed without evidence. Do not create a second technical status or distillation in AI System.

After execution, compare the owner intent and DoD with the actual diff, product tests, findings, skipped checks, QA evidence, distillation/checkpoint, and Git state. A worker's `done` message is not evidence. Return the actual result, residual risk, blockers, and next owner decision. After interruption, check source status and Git again; do not replay completed writes or trust a stale record.

A scoped local commit may follow applicable QA and an approved implementation, distillation, or execution checkpoint when its write set is known. Do not stage unrelated changes, create an empty commit, or commit merely because a block-boundary checkpoint was saved. Push, production, and owner-only final acceptance require their own explicit authority; approval to publish an AI System product upgrade does not carry to target projects.

Use semantic and product QA first. AI Workflow validation applies to its own artifacts when needed; broad AI System validation does not run merely because AI System coordinates ordinary project work. Both script results are supporting evidence only. Dreaming Mode remains advisory and does not execute orchestration.

## Record And Rollout

For an approved non-exempt work unit, use `.systems/ai/templates/workspace/project-state/orchestration-record.template.md` at the nearest owner's `project-state/<project>/orchestration/<work-id>.md`. Keep the record limited to coordination metadata and privacy-safe paths. It does not replace local Workflow status, AI System Distillation State, or a required workflow change request. Do not put it inside a managed repository or copy private client content into a cross-project artifact.

V1 has no scheduler, background agent launcher, or lock service. Inspect the target's installed Workflow version; do not assume all nested clones have the same features. Changes needed in upstream AI Workflow follow a separate approved change and a privacy-safe cross-system handoff.


## Intent brief boundary

Use intent-to-execution-brief.md: original owner intent and accepted decisions remain independent verification inputs; an inferred brief or style profile cannot supply permission, scope or final acceptance. Style-profile.md permits only explicitly scoped, provenance-bearing private advisory feedback. Consumer handoff preserves original scope/DoD/exclusions, mode/source, supplied limits, actual action ceiling, corrections and sanitized optional style projection; consumer verifies local gates itself.


## Goal-Focused Maintenance Integration

Use goal-focused-maintenance.md only after explicit scoped activation and verified local support. One nearest-owner private maintenance/queue.json records proven independent incidental debt; project coordination references the Workflow-owned queue rather than duplicating it. E01–E05 and actual current-goal blockers are immediate. Five distinct active project causes or the third actual affected parent task schedule one consolidated milestone summary; scans/resumes do not count or repeat receipts. One stable approved parent shares TOTAL 600 seconds incidental diagnosis/edit/review/test/record work across both adapters. No background executor, scheduler or automatic TaskNotes. Required current QA and full release/updater failures remain binding. Missing counterpart support keeps existing gates; labels are not activation or authority.

Before shared activation, verify the reviewed committed Workflow profile/source HEAD with maintenance_policy.workflow_projection. The standalone System evaluator is identical portable core plus the owner adapter. The installed nested Workflow retains its existing local gates until separately updated; coordination does not overwrite it. One parent identity and owner queue are shared, not 600+600 seconds.
