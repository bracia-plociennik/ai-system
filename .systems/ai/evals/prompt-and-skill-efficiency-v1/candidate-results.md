# Candidate Agent Runs

Candidate: uncommitted AI System product diff after the frozen `ab6ad83` baseline. Same five prompts, model (`gpt-6-astra`), CLI options, sandbox, and synthetic fixtures as baseline. No private workspace or real TaskForge vault was used. The copied candidate fixtures preceded a model-guidance wording edit and restoration of explicit System Insights, Delivery Constraints, and Distillation State links in the root template. These were checked by the full product validator but not rerun through agent A/B.

| Case | Core docs read: before -> after | Commands: before -> after | Observable result |
| --- | ---: | ---: | --- |
| `small-typo` | 6 -> 5 | 4 -> 4 | Exactly one typo fixed; concise final answer; no broad validation. |
| `local-code-loop` | 6 -> 8 | 5 -> 5 | Requested slug behavior implemented; six focused tests passed; no broad validation. |
| `task-write-gate` | 6 -> 7 | 3 -> 3 | No TaskNote written; missing target and approval identified. |
| `skill-create-trigger` | 4 -> 5 | 5 -> 3 | Skill guidance used; trigger, non-trigger, and resources supplied; no files written. |
| `skill-near-miss` | 4 -> 5 | 3 -> 2 | No skill-creator guidance loaded; only a spelling suggestion, no write. |

Across five exploratory runs, commands changed `20 -> 17` and reported input tokens `558059 -> 466926`. These token totals include model context/caching and cannot establish causal cost savings. Core-document reads increased `26 -> 30`, so selective routing did not reliably reduce that measure. Elapsed time was not exposed consistently by the event logs and is unavailable. No case invoked broad validation or showed an approval/privacy miss; all expected case behaviors were observed. The A/B sample is too small for a general reliability claim.

Structural audit of the final working tree changed the generated root template from 269 to 195 lines, the active skill from 261 to 144 lines, and its trigger description from 342 to 184 characters. The general full-response footer is now conditional, while route-specific summaries and safety gates remain mandatory. The remaining over-reading of core contracts is a follow-up measurement target, not a reason to weaken mandatory intake or task write approval in this iteration.

The exact final candidate tree was subsequently rerun on all five original prompts; see `expanded-results.md` for the final-tree results and the six additional small-task cases. The initial 26 -> 30 figure above remains a historical observation, not the final aggregate.
