# Prompt and Skill Efficiency V1 Eval

This eval compares AI System routing before and after a product contract change.
Use only the synthetic fixtures in this directory. Do not use private workspace data.
The original five cases are frozen; six small-task cases extend the benchmark
without changing the original prompts or expected behavior.

## Protocol

1. Freeze the source revision and the eval prompts before editing behavior contracts.
2. For each case, copy the same source revision and fixtures into an isolated directory.
   Use the generated AI System `AGENTS.md` from that revision, not the local
   AI Workflow root shim. Give each run the same model, effort, tools, sandbox,
   and prompt. Record the exact run configuration.
3. Capture the agent event log and final answer. A scaffold created by
   `skill-creator/scripts/run_eval.py` is not an executed agent run.
4. Score the observable behavior against `evals.json`. Record read count,
   broad-validator calls, clarification requests, elapsed time, final-answer
   length, completion, and safety-gate misses. Mark metrics unavailable when
   the event log does not expose them; never estimate them from memory.
5. Re-run the frozen cases after the product change. Keep the pre-change
   baseline immutable and compare the same model/configuration pair.

## Acceptance

- No new privacy, approval, source-of-truth, evidence, or PASS-integrity miss.
- No loss of task completion or relevant QA in the implementation case.
- Skill creation triggers the AI System skill-creator; adjacent work does not.
- At least one simple-case efficiency measure improves without a quality loss.
- A script result alone never supplies semantic PASS.

Case-specific results and exact source revisions belong in scorecards in this
directory. `core_docs_read_estimate` counts distinct core Markdown paths in
commands containing a read operation, not the number of verified file reads
or total context size. A compound command may read the file and fail later.
Compare the path sets, not just the aggregate: a selected route may add a
different contract while removing a broader read. Repeated runs are needed to
separate agent sampling variance from a routing change. Raw JSONL events and
disposable workdirs stay outside `.systems/`.

Run `python3 -B -m unittest discover -s .systems/ai/evals/prompt-and-skill-efficiency-v1 -p 'test_*.py'`
to check the scorecard parser. It uses synthetic events only.
