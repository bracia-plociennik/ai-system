# Weekly Planning Contract Distillation

- Date: `2026-08-10`
- Source state record: `AI_WORKFLOW_WORKSPACE_HOME/capture-state/weekly-planning-contract.md`
- State: `completed`
- Privacy/scope check: `pass`

## Durable Decisions

- One canonical weekly plan covers the next Monday-Friday work week; Sunday remains outside the plan.
- Each day has four compatible blocks: build future, adapt build/deliver, deliver financial impact, and adapt promote/deliver.
- Capacity is explicit. Work larger than one block is represented by visible work slices; capacity is not silently exceeded.
- Exactly one WIG is allowed. It may link to a weekly item or remain standalone, and it never creates a second TaskNote.
- TaskNote output uses deterministic deadline/6D precedence, source-week identity, deduplication, conservative mapping, and owner-approved writes.
- Revisions preserve unknown fields, avoid mutating completed or conflicting tasks, and never delete a TaskNote when an item leaves the plan.
- There is no scheduler, background automation, connector, or external write-back in V1.

## Evidence And Residual Risk

- Source contract: `AI_SYSTEM_WORKSPACE_HOME/projects/ai-system/.systems/ai/core/weekly-planning.md`
- Runtime state record was reviewed and linked before marking this distillation completed.
- Residual risk: natural-language estimates, deadlines, and project mapping must remain explicit or be routed to review.
