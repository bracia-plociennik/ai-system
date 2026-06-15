#!/usr/bin/env python3
"""Generate a Markdown skill eval report from benchmark.json."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True

try:
    from utils import load_json, write_text
except ImportError:  # pragma: no cover
    from .utils import load_json, write_text


def render_report(benchmark: dict) -> str:
    metadata = benchmark.get("metadata", {})
    run_summary = benchmark.get("run_summary", {})
    verdict = "pass" if not benchmark.get("blocking_findings") else "needs-review"
    lines = [
        "# Skill Eval Report",
        "",
        f"- Verdict: `{verdict}`",
        f"- Skill: `{metadata.get('skill_name', benchmark.get('skill_name', 'unknown'))}`",
        f"- Eval count: `{metadata.get('eval_count', benchmark.get('eval_count', 0))}`",
        "",
        "## Configuration Summary",
        "",
        "| Configuration | Runs | Pass Rate | Score | Time | Tokens | Errors |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for config, item in run_summary.items():
        lines.append(
            f"| `{config}` | `{item.get('runs', 0)}` | `{item.get('pass_rate_mean', 'n/a')}` | "
            f"`{item.get('score_mean', 'n/a')}` | `{item.get('time_seconds_mean', 'n/a')}` | "
            f"`{item.get('tokens_mean', 'n/a')}` | `{item.get('errors_mean', 'n/a')}` |"
        )
    if not run_summary:
        lines.append("| `default` | `0` | `n/a` | `n/a` | `n/a` | `n/a` | `n/a` |")

    lines.extend([
        "",
        "## Deltas",
        "",
    ])
    deltas = benchmark.get("deltas") or {}
    if deltas:
        for name, values in deltas.items():
            lines.append(f"- `{name}`: `{values}`")
    else:
        lines.append("- none")

    lines.extend([
        "",
        "## Blocking Findings",
        "",
    ])
    findings = benchmark.get("blocking_findings") or []
    if findings:
        for item in findings:
            lines.append(
                f"- `{item.get('severity', 'P3')}` `{item.get('eval_id', 'unknown')}`: {item.get('finding', '')}"
            )
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("benchmark_json", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        benchmark = load_json(args.benchmark_json)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    output = args.output or (args.benchmark_json.parent / "review-notes.md")
    write_text(output, render_report(benchmark), overwrite=True)
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
