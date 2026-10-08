# Execution Modes V1

## Purpose And Selection

New work defaults to `auto`. Exact task-local `human mode` or `human coop` selects
`human`; `auto mode` selects `auto`. An explicit owner choice wins over a stored
choice for the same work unit. A switch changes interaction only, never approval,
scope, risk, quality, accepted evidence or permission. Do not migrate or resume
historical stopped runs automatically. On resume, retain the recorded mode;
missing historical mode needs a disposition before adopting a new default.

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
stricter installed limit until counterpart support is verified. After interruption,
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

`workflow_support` inspects an installed source-bound execution-modes-v1 capability.
The proposed JSON interface declares `contract: 1`, `capability: execution-modes-v1`,
`behaviors`, `sources` (relative source paths to SHA-256), and explicit `mode_mapping`
of `auto` to `auto` and `human` to `human-coop`. The adapter does not infer this
mapping from prose or a branch. This interface must be reconciled with the actual
counterpart release before declaring shared integration complete.
A proposed handoff, branch name, version label or saved eligible flag is not proof.
Missing/invalid support returns installed-local-gates fallback and an explicit
compatibility dependency. Perform only permitted independent work; never update,
install or override a target Workflow automatically. Native behavior and agent
obedience remain unverified by capability metadata and deterministic fixtures.

## Quality And Closure

Semantic findings-first review, failure paths, product tests and current DoD evidence
precede supporting validators. Report observed agent decisions separately from pure
protocol tests and real counterpart integration. Required skipped tests remain
blockers, not implicit acceptance. Capture/distillation/checkpoints keep their
existing approval and nearest-owner scope; technical Phase 8 does not close work.
