# Managed storage and task continuity

## Capacity before allocation

Before a new worktree, dependency installation, build, data expansion or heavy validation, use manage-storage-capacity plan with the actual destination, explicit --bytes and --inodes estimates, and the host's one owner-selected --state-dir. Estimates come from observed comparable work or an explicit declaration. A missing estimate requires a bounded measurement or decision. Registry configuration belongs to the host owner and is shared by its managed projects.

Use manage-storage-capacity run with --approved, --work-id and a directly supplied argv after -- to reserve, execute and release under the shared registry lock. Keep at least max(10 GiB, 10% filesystem capacity) and 1024 inodes, plus full outstanding reservations. The conservative calculation includes the entire reservation while the command runs. The caller verifies actual authority for the command. Child exit status propagates. A remaining process group retains its reservation for inspection. Interrupted reservations require actual activity reconciliation and explicit release by the same owning work. There is no time-based expiry.

The inspect and plan actions are read-only. reserve and release support explicit multi-step operations. Reservations coordinate participating tools. Current filesystem measurements remain necessary before a resumed heavy operation.

## Source checkout and lifecycle

create-source-worktree takes an existing owning --record, --canonical repository, durable --workspace, --collection, new --target, codex --branch, --resource-id, shared capacity --state-dir and growth estimates. With verified --approved scope it reserves capacity, creates from dev without checkout, binds durable runtime and registers the worktree before materializing source. Only tracked ai-workflow-workspace is excluded by the sparse pattern. Existing source/runtime dependencies require review before choosing this route.

Normal cleanup continues through manage-task-resources list and plan at task start, claim/resume before reuse, and reviewed release at actual safe closure. Existing seven-day retention and current QA/Capture requirements remain binding. An interrupted creation leaves its exact registered resource for inspection. Old unregistered data receives a read-only inventory and individual disposition. Compare avoided allocation, recovered allocation and evidence-pinned resources separately.

## Proportional work and evidence

Inside the existing intake state why the selected route fits the change. Link each accepted requirement to one observable scenario and its current evidence, including missing evidence. Use the existing work record and QA report for these links. A tiny task can use a short inline mapping.

At an actual stage boundary or scope switch keep a compact resume packet in existing OSNR/status containing the goal, current stage, accepted decisions, evidence references and next action. Preserve human edits and the stable task identity. Read this packet on resume, then verify its current source binding.

## On-demand retrospective

analyze-task-retrospective reads one explicitly selected JSON input with task_id and observed events. Each event names action, source_fingerprint, environment_fingerprint, mandatory, reason, evidence and category. Use category executor-error, missing-contract or environment-constraint only for an evidenced observation. A repeat with identical declared inputs is a candidate finding only when mandatory is false and reason is no-new-input. The agent verifies input claims against original artifacts and distinguishes a hypothesis from a conclusion.

In an active task, briefly surface an observed anomaly and its evidence at the next useful boundary. A report with no significant inefficiency is valid. Time savings require actual measurements.
