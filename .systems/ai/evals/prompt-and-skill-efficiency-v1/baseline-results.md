# Baseline Agent Runs

Frozen product revision: `ab6ad83`. Five independent runs used `gpt-6-astra`, `workspace-write`, the same CLI options, and isolated copies containing only the product checkout plus synthetic task fixtures. The owner explicitly approved this network-backed evaluation for synthetic copies only. Raw traces remain under the local `/tmp/ai-system-efficiency-v1.*` directory and are not product artifacts.

| Case | Core docs read (estimate) | Commands | Observed result |
| --- | ---: | ---: | --- |
| `small-typo` | 6 | 4 | One typo corrected; no broad validator, but disproportionate policy reading. |
| `local-code-loop` | 6 | 5 | Slug implementation and tests changed; seven focused tests passed. |
| `task-write-gate` | 6 | 3 | No TaskNote written; missing target and approval identified. |
| `skill-create-trigger` | 4 | 5 | Skill guidance used; read-only design includes trigger and non-trigger examples. |
| `skill-near-miss` | 4 | 3 | No skill-creator guidance loaded and no file changed. |

The tool counts and core-doc estimates come from `summarize_runs.py`; the behavior judgments come from inspecting agent messages, command traces, and synthetic fixture state. This is a small exploratory benchmark, not a statistical claim about production reliability. CLI input-token totals include context and cached tokens and are not a clean measure of document-read cost.
