> Compatible new implementation tasks use `default-sprint.md` V2: bounded targeted QA after acceptance and incremental phases5–7; explicit full verification/Phase8 remains separate. This scoped rule takes precedence over ordinary implementation/checkpoint chaining below. V1 and unsupported tasks retain installed rules. `Phase X` / `-all` follows `phase-x-maintenance.md`; manual only, never autopilot/Dreaming.

# Execution Modes V1

## Intent brief and private style context

Use intent-to-execution-brief.md during existing intake: minimal inline/embedded fields with provenance and disposition; preserve original request/accepted decisions as independent QA anchors. Batch triage and current action/phase ceilings remain first. This adds no phase or approval. Use style-profile.md for optional explicitly enabled local style; recording needs actual exact-target consent and minimal provenance/privacy, observations stay tentative and current instruction overrides profile. Invalid/disabled profile supplies no preferences. Auto chooses only covered reversible options and queues protected owner decisions; Human groups material questions, settled answers not repeated and noninteractive routes stay so.


## Purpose And Selection

New work defaults to `auto`. Exact task-local `human mode` or `human coop` selects
`human`; `auto mode` selects `auto`. An explicit owner choice wins over a stored
choice for the same work unit. A switch changes interaction only, never approval,
scope, risk, quality, accepted evidence or permission. Do not migrate or resume
historical stopped runs automatically. On resume, retain the recorded mode;
missing historical mode needs a disposition before adopting a new default.

Record mode, scope (`task|session|project`), scope ID and choice source. Resolve
current explicit task choice, resumed recorded choice, explicit matching-session
choice, project choice, then Auto. Session scope never leaks into another session;
task scope expires with that task. In Workflow projects preserve the source run's
selection. A new explicit mode choice requires refreshed source readiness rather
than overwriting its stored selection inside a read-only preflight.

This is an execution/interaction contract, not a work mode, formal phase, scheduler
or agent backend. Analysis remains analysis; planning remains planning. A plan-only
request never authorizes implementation. Use `owner-approval.md`: an ordinary
implementation request or mode label does not grant write authority. Explicit
owner-approved or valid complete-plan acceptance remains necessary and scoped.

## Auto Mode

After scoped approval, work autonomously toward the accepted DoD. Resolve
verifiable technical choices inside that outcome, including architecture and
libraries, and record material rationale, alternatives and verification in the
existing work record. Permission for a production dependency or sensitive effect
is separate from permission to choose a local implementation approach.

Auto asks no live questions during an approved run. Use discoverable facts first.
Missing deadline/timebox means `Mode: auto-unconstrained`; do not invent limits or
ask a compulsory delivery question. Preserve supplied constraints, must-have,
quality floor and scoped outcomes; do not add unrequested optional improvements.

Classify each decision as:

- agent-resolved: technical choice inside authorized scope, with rationale/evidence;
- owner-proposal: optional, non-blocking refinement with recommendation and impact;
- dependent-blocker: missing approval/fact or owner outcome/sensitive-effect choice.

A dependent-blocker stops only its affected units and transitive dependents.
Continue work whose independence is demonstrated. Unknown dependencies are not
independence. If ownership, workspace, safe verification or a shared interface
cannot be resolved, block every affected unit; do not guess a destination or gate.
Do not execute affected actions while their blocking decisions remain pending.

When no safe independent work remains, return one owner queue with decision ID,
recommendation, alternative, impact and the work unlocked by an answer. Return
completed, blocked, deferred and skipped checks separately. An incomplete DoD
never receives full PASS; an optional proposal is not an unfinished requirement.

## Human Mode

Ask at most 1-3 grouped material questions before dependent work. Resolve routine
technical details without questions. Use `delivery-constraints.md` for missing
material constraints in Human Mode. Continue independent approved work where safe.
Already-resolved decisions and permissions are not asked again.

## Approval And Effects

Mode is not owner approval. A recorded approval reference is an audit pointer,
not authentication of a conversation message. Changes to outcomes, real data,
production, credentials, permissions, security, billing, migrations, destructive
operations and external actions retain explicit scope and stricter target gates.
Git history is not rollback proof for such effects or untracked/ignored files.
Preserve every risk/QA/privacy gate. Critical work remains human-led unless the
local contract explicitly permits controlled delegation with real approval.

## Recovery And Resume

After three attempts on the same cause without new evidence or improvement, stop
the affected loop and preserve its diagnosis/failures. Measurable progress resets
the stalled count; changing a label or asserting progress does not. Honor a
stricter installed limit even after counterpart support is verified. Workflow's two
Spec/Quality fix-loop limits are not increased to three. After interruption,
inspect current Git, scope/approval, dependencies, decisions and evidence hashes.
Do not replay completed effects or accept stale completion evidence.

## Existing Record And Inspector

Extend the current work/orchestration record with execution mode, owner approval
reference, DoD, allowed writes/actions, phase ceiling, Git policy and decision queue.
`execution_modes.py` inspects its optional execution portion; it neither writes
state nor executes work. Its dependency dispositions and declared-action checks
are supporting-only, never tool receipts, owner authorization or formal PASS.
The JSON inspector format is demonstrated in its behavioral tests. It does not
replace an existing formal project/task status machine or create another run.

Use `check-execution-modes --record <json>` for read-only inspection. CLI input is
data and cannot authenticate approval, safe environment or technical QA. A work
record can reference existing units; do not duplicate Workflow execution state.

## Workflow Integration And Git

Local AI Workflow owns risk, phases, technical state, QA and capture. AI System
references its source run. One coordinator owns shared routers and index; preserve
the existing flat dynamic worker pool and native capability/isolated resource gates.

For a formal project with approved phase scope and verified local support, Auto
continues to technical Phase 8. It never supplies `final-owner-yes`, formal owner
closure or Phase 8 commit permission. Ordinary tasks do not gain artificial phases.
Scoped local commits require explicit approved Git scope and current QA. Explicit
no-commit wins; merge to main and push need owner approval, never mode inference.

`workflow_support` uses the AI System-owned profile
`.systems/ai/capabilities/workflow-execution-modes-v1.json`. It records the tested
Workflow commit, required source SHA-256 and file modes, and explicit mappings
`auto -> auto`, `human -> human-coop`, `auto-unconstrained -> auto-unbounded`.
Recognition checks current committed blobs, index and live files against the
reviewed profile. Unrelated changes may retain support only when every required
source remains identical. A branch name, ancestry, version label or saved eligible
flag is not evidence. Workflow need not supply a separate capability document.

`check-execution-modes --workflow-root <root> --workflow-state <json>` inspects
the original Workflow readiness projection using its verified pure `--state`
inspector on a frozen synthetic copy. It preserves source selection, exact action
names, approval references and readiness outcomes. It never translates an AI
System `implementation` permission into blanket Workflow actions or synthesizes
gates, quality, capture or isolation flags. AI System and Workflow JSON records
remain separate; summary decision IDs require the referenced full source decisions.
Sources and input are rechecked after inspection. This is a point-in-time check,
not an execution lock. The Workflow projection remains data, not authenticated
approval or real isolation evidence.

Unknown support returns `unsupported`; malformed, linked or uncommitted inputs
return `invalid`. Both retain installed-local-gates and the affected compatibility
dependency. Perform only permitted independent work; never install or override a
target Workflow automatically. The actual local committed version is sufficient
for synthetic integration; publication is not a prerequisite. Native behavior and
agent obedience remain unverified by deterministic fixtures.

## Quality And Closure

Semantic findings-first review, failure paths, product tests and current DoD evidence
precede supporting validators. Report observed agent decisions separately from pure
protocol tests and real counterpart integration. Required skipped tests remain
blockers, not implicit acceptance. Capture/distillation/checkpoints keep their
existing approval and nearest-owner scope; technical Phase 8 does not close work.


## Goal-Focused Maintenance Integration

Use goal-focused-maintenance.md only after explicit scoped activation and verified local support. One nearest-owner private maintenance/queue.json records proven independent incidental debt; project coordination references the Workflow-owned queue rather than duplicating it. E01–E05 and actual current-goal blockers are immediate. Five distinct active project causes or the third actual affected parent task schedule one consolidated milestone summary; scans/resumes do not count or repeat receipts. One stable approved parent shares TOTAL 600 seconds incidental diagnosis/edit/review/test/record work across both adapters. No background executor, scheduler or automatic TaskNotes. Required current QA and full release/updater failures remain binding. Missing counterpart support keeps existing gates; labels are not activation or authority.

Auto resolves only approved local choices. Live eligibility never grants permission: require local/reversible/low-risk known cause/test, collision-free exact approved target. Security/auth/billing/permissions/production/migration/secrets/architecture/external effects/dependency install/cross-owner writes are excluded from this allowance.

## Sprint iteration

For actual task-local Sprint selection use `sprint-iteration.md` and the compatible installed Workflow. Keep preview/feedback implementation open until genuine final current-effect acceptance or explicit verification request. Deferred quality is not completed/PASS or resource release. Preserve normal behavior without explicit activation.
