# Expanded Small-Task Agent Runs

## Why the first sample went from 26 to 30

The five original runs counted distinct `.systems/ai/core/*.md` files read per
case. The candidate loaded `command-routing.md` in four cases where baseline
did not (+4). In `local-code-loop`, it also loaded `owner-approval.md` (+1).
In `small-typo`, it omitted `delivery-constraints.md` (-1). Net: +4 distinct
core-document reads across those five runs. The candidate root template
explicitly points to `command-routing.md` as the selector for relevant core
contracts. This explains the observed path-set difference; it does not prove
that routing always adds four reads or that the added reads were unnecessary.

## Expansion

Six additional synthetic, bounded tasks were appended without changing the
five frozen prompts: two read-only questions, two one-line documentation
edits, one JSON value edit, and one focused test-only change. Baseline product
source is `ab6ad83`; candidate is the current uncommitted product diff. Both
used `gpt-6-astra`, the same Codex CLI options, isolated copies, and identical
synthetic fixtures. The expansion candidate includes the final root-template
link restoration that was absent from the initial five candidate copies.
No private runtime or real TaskForge vault was sent to the agent runs.

| New case | Core docs: baseline -> candidate | Commands: baseline -> candidate | Behavioral result |
| --- | ---: | ---: | --- |
| `small-read-command` | 0 -> 0 | 2 -> 2 | Correct command, no write. |
| `small-read-code` | 4 -> 0 | 2 -> 2 | Correct return value, no write. |
| `small-doc-heading` | 5 -> 3 | 4 -> 3 | Only the heading changed. |
| `small-doc-note` | 7 -> 7 | 4 -> 3 | Exact sentence appended; original typo retained. |
| `small-config-value` | 6 -> 7 | 4 -> 4 | Only `retries` changed from 2 to 3. |
| `small-test-only` | 6 -> 7 | 4 -> 3 | One test added, focused test passed, production code unchanged. |

The six-case expansion totals are **28 -> 24** distinct core-document paths
and **20 -> 17** commands. Combined with the initial five-case scorecard,
that first comparison was **54 -> 54** core paths and **40 -> 34** commands.
The initial five remain recorded as **26 -> 30** and **20 -> 17**; no score was
silently replaced. All eleven pairs completed the requested behavior without
a broad validator call, out-of-scope write, or observed approval/privacy miss.

## Final-tree rerun

The initial candidate copies preceded the last root-template link restoration.
The five original prompts were therefore rerun against fresh copies of the
exact final candidate product tree, with the same model, CLI settings, and
synthetic fixtures. All five completed their expected behavior: the typo fix
changed one word; the local code loop passed seven focused tests; the TaskNote
gate refused the underspecified write; the skill design triggered guidance;
and the near-miss remained read-only without skill-creator guidance.

| Original case | Baseline core paths -> final candidate | Baseline commands -> final candidate |
| --- | ---: | ---: |
| `small-typo` | 6 -> 7 | 4 -> 3 |
| `local-code-loop` | 6 -> 9 | 5 -> 5 |
| `task-write-gate` | 6 -> 3 | 3 -> 3 |
| `skill-create-trigger` | 4 -> 5 | 5 -> 4 |
| `skill-near-miss` | 4 -> 4 | 3 -> 2 |

This final-tree five-case run is **26 -> 28** core paths and **20 -> 17**
commands. Combining it with the six-case expansion gives **54 -> 52** core
paths and **40 -> 34** commands across eleven unique tasks. These are more
relevant to the final tree than the initial combined figure, but still only
one final-tree run per original task.

## Repeat and limits

`small-typo` was rerun from fresh copies: baseline read 7 rather than 6 core
docs, and candidate read 6 rather than 5 in that repeat and 7 in the final-tree
run. All changed only the typo.
`small-read-command` was also rerun: both configurations again read zero core
docs and answered correctly. This small repeat shows that document selection
can vary by run even with the same prompt and configuration. The repeated
cases are not included in the eleven-case aggregate.

The metric is a path-count estimate from shell commands containing reads, not
proof that every file opened, tokens actually consumed, elapsed time, or the
semantic necessity of each read. Compound commands are counted even when a
later operation returns nonzero.
Model token totals include context/caching effects and do not establish cost
or latency savings. Each unique case still has only one run per configuration,
so the aggregate is exploratory rather than a statistical reliability claim.
The follow-up should target unnecessary repeated reads of common contracts
without weakening task intake, approvals, quality checks, or route-specific
policy.
