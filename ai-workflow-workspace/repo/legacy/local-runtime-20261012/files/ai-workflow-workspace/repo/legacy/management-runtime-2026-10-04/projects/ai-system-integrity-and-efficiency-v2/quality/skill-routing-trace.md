# Skill Discovery And Trigger Trace

## Read Set
1. Active skill frontmatter surfaced by .systems/scripts/discover-skills.
2. Full .systems/ai/skills/skill-creator/SKILL.md opened only after matching the reusable-skill/evaluation scope.
3. Evaluation schemas, grader contract and run/aggregate resources selected for the freshness task.
4. No legacy skill bodies or client workspace skills were loaded.

## Observed Routing Decisions
These are this agent's reviewed routing decisions, not fabricated independent agent trials.

| Synthetic request | Decision | Reason |
| --- | --- | --- |
| Create a reusable invoice-review skill | skill-creator | Reusable skill creation explicitly matches. |
| Update the trigger of an existing skill | skill-creator | Existing skill contract/description update. |
| Evaluate whether a skill triggers on near-misses | skill-creator | Local skill evaluation. |
| Correct one typo in an invoice | no skill-creator | One-off artifact edit, explicitly excluded. |
| Execute the invoice review once | no skill-creator | Task execution is not skill creation. |
| Explain a project status | no skill-creator | Read-only operational response. |
| Create a memory note about a lesson | no skill-creator | Capture route, not reusable skill authoring. |
| Improve the application checkout screen | no skill-creator | Product implementation, not skill update. |

## Executable Evidence
test_metadata_discovery_stops_before_body uses an observed stream that raises if the reader enters the body. It also verifies workspace precedence. This provides a stronger read-boundary check than a text-presence assertion.

## Privacy And Authority
Synthetic requests only. Frontmatter informs discovery, not approval. Current-state and matched contract gates remain mandatory. No external model call or automatic skill invocation occurred.
