# Skill Evaluation

Read this only when designing, running, or reviewing a skill evaluation.

1. Define realistic should-trigger, should-not-trigger, and near-miss prompts with expected and forbidden behavior. Include edge cases and a holdout when there are enough examples.
2. Use `schemas.md` for eval and grading formats. Save local runs under an approved workspace or `/tmp`, never as runtime output in the product skill directory.
3. Compare the same prompts and comparable inputs with the old skill or no skill (`baseline`) and the candidate (`with_skill`). Capture transcripts, produced files, tool calls, timing, and available token metrics.
4. Use `agents/grader.md` for expectation-level reasons, `agents/comparator.md` for A/B differences, and `agents/analyzer.md` for repeated failure patterns. A single run is exploratory, not proof of general trigger reliability.
5. Use `scripts/run_eval.py`, `scripts/aggregate_benchmark.py`, and `scripts/generate_report.py` only when their inputs exist. `scripts/improve_description.py` proposes wording; it does not validate a trigger by itself.
6. Record quality, safety, privacy, cost, and residual risk before deciding whether to keep the candidate.

Allowed modes are `manual-review`, `local-script`, and `approved-subagent`. External model CLIs, network services, browser automation, production systems, and subagents require explicit owner approval for that execution path and the relevant AI System gates. Synthetic fixtures must not contain private client or runtime data.
