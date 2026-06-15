#!/usr/bin/env python3
"""Aggregate local skill grading results into benchmark JSON and Markdown."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from statistics import mean, stdev
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def maybe_load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return load_json(path)


def collect_gradings(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    return [(path, load_json(path)) for path in sorted(root.rglob("grading.json"))]


def number(value: Any, default: float = 0.0) -> float:
    return float(value) if isinstance(value, (int, float)) else default


def bool_value(value: Any, path: Path) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"Missing boolean passed in {path}")
    return value


def expectation_summary(data: dict[str, Any]) -> tuple[int, int, int, float]:
    expectations = data.get("expectations")
    if isinstance(expectations, list) and expectations:
        total = len(expectations)
        passed = sum(1 for item in expectations if isinstance(item, dict) and item.get("passed") is True)
        failed = total - passed
        return passed, failed, total, passed / total if total else 0.0

    summary = data.get("summary")
    if isinstance(summary, dict) and "pass_rate" in summary:
        passed = int(number(summary.get("passed")))
        failed = int(number(summary.get("failed")))
        total = int(number(summary.get("total"), passed + failed))
        return passed, failed, total, number(summary.get("pass_rate"))

    passed = 1 if data.get("passed") is True else 0
    failed = 0 if data.get("passed") is True else 1
    return passed, failed, 1, float(passed)


def issue_finding(issue: Any) -> str:
    if not isinstance(issue, dict):
        return str(issue)
    return str(issue.get("finding", issue))


def issue_severity(issue: Any) -> str:
    if not isinstance(issue, dict):
        return "P3"
    return str(issue.get("severity", "P3"))


def mean_or_none(values: list[float]) -> float | None:
    return round(mean(values), 2) if values else None


def stdev_or_none(values: list[float]) -> float | None:
    return round(stdev(values), 2) if len(values) > 1 else 0.0 if values else None


def configuration_from_path(root: Path, grading_path: Path, data: dict[str, Any]) -> str:
    if data.get("configuration"):
        return str(data["configuration"])
    rel = grading_path.relative_to(root)
    return rel.parts[1] if len(rel.parts) >= 3 else "default"


def build_run_row(root: Path, path: Path, data: dict[str, Any]) -> dict[str, Any]:
    eval_id = str(data.get("eval_id", path.parent.parent.name if len(path.parts) >= 3 else path.parent.name))
    configuration = configuration_from_path(root, path, data)
    metrics = dict(data.get("execution_metrics") or {})
    timing = dict(data.get("timing") or {})
    metrics.update(maybe_load_json(path.parent / "outputs" / "metrics.json"))
    timing.update(maybe_load_json(path.parent / "timing.json"))
    passed_count, failed_count, total_count, pass_rate = expectation_summary(data)
    issues = data.get("issues", [])
    if not isinstance(issues, list):
        raise ValueError(f"Expected issues list in {path}")

    return {
        "eval_id": eval_id,
        "eval_name": str(data.get("eval_name", eval_id)),
        "configuration": configuration,
        "skill_name": str(data.get("skill_name", "unknown")),
        "score": number(data.get("score")),
        "passed": bool_value(data.get("passed"), path),
        "passed_expectations": passed_count,
        "failed_expectations": failed_count,
        "total_expectations": total_count,
        "pass_rate": round(pass_rate, 4),
        "time_seconds": number(timing.get("total_duration_seconds")),
        "tokens": number(timing.get("total_tokens")),
        "tool_calls": number(metrics.get("total_tool_calls")),
        "errors": number(metrics.get("errors_encountered")),
        "expectations": data.get("expectations", []),
        "issues": issues,
        "source": str(path),
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    configs = sorted({row["configuration"] for row in rows})
    for config in configs:
        config_rows = [row for row in rows if row["configuration"] == config]
        summary[config] = {
            "runs": len(config_rows),
            "passed_runs": sum(1 for row in config_rows if row["passed"]),
            "failed_runs": sum(1 for row in config_rows if not row["passed"]),
            "pass_rate_mean": mean_or_none([row["pass_rate"] for row in config_rows]),
            "pass_rate_stdev": stdev_or_none([row["pass_rate"] for row in config_rows]),
            "score_mean": mean_or_none([row["score"] for row in config_rows]),
            "time_seconds_mean": mean_or_none([row["time_seconds"] for row in config_rows if row["time_seconds"]]),
            "tokens_mean": mean_or_none([row["tokens"] for row in config_rows if row["tokens"]]),
            "tool_calls_mean": mean_or_none([row["tool_calls"] for row in config_rows if row["tool_calls"]]),
            "errors_mean": mean_or_none([row["errors"] for row in config_rows]),
        }
    return summary


def build_deltas(summary: dict[str, dict[str, Any]]) -> dict[str, dict[str, float | None]]:
    if "with_skill" not in summary or "baseline" not in summary:
        return {}
    left = summary["with_skill"]
    right = summary["baseline"]
    fields = ("pass_rate_mean", "score_mean", "time_seconds_mean", "tokens_mean", "tool_calls_mean", "errors_mean")
    delta = {}
    for field in fields:
        if left.get(field) is None or right.get(field) is None:
            delta[field.replace("_mean", "_delta")] = None
        else:
            delta[field.replace("_mean", "_delta")] = round(float(left[field]) - float(right[field]), 2)
    return {"with_skill_vs_baseline": delta}


def build_benchmark(root: Path) -> dict[str, Any]:
    gradings = collect_gradings(root)
    if not gradings:
        raise ValueError(f"No grading.json files found under {root}")

    rows = [build_run_row(root, path, data) for path, data in gradings]
    blocking_findings = []
    for row in rows:
        for issue in row["issues"]:
            severity = issue_severity(issue)
            if severity in {"P1", "P2"}:
                blocking_findings.append(
                    {
                        "eval_id": row["eval_id"],
                        "configuration": row["configuration"],
                        "severity": severity,
                        "finding": issue_finding(issue),
                        "source": row["source"],
                    }
                )

    run_summary = summarize(rows)
    return {
        "metadata": {
            "skill_name": rows[0]["skill_name"],
            "eval_count": len({row["eval_id"] for row in rows}),
            "configurations": sorted(run_summary),
        },
        "run_summary": run_summary,
        "deltas": build_deltas(run_summary),
        "runs": rows,
        "blocking_findings": blocking_findings,
        "analyzer_notes": [],
    }


def render_markdown(benchmark: dict[str, Any]) -> str:
    metadata = benchmark["metadata"]
    lines = [
        "# Skill Benchmark",
        "",
        f"- Skill: `{metadata['skill_name']}`",
        f"- Eval count: `{metadata['eval_count']}`",
        f"- Configurations: `{', '.join(metadata['configurations'])}`",
        "",
        "## Summary",
        "",
        "| Configuration | Runs | Pass Rate | Score | Time | Tokens | Tool Calls | Errors |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for config, item in benchmark["run_summary"].items():
        lines.append(
            f"| `{config}` | `{item['runs']}` | `{item['pass_rate_mean']}` | `{item['score_mean']}` | "
            f"`{item['time_seconds_mean']}` | `{item['tokens_mean']}` | `{item['tool_calls_mean']}` | `{item['errors_mean']}` |"
        )

    lines.extend(["", "## Runs", "", "| Eval | Config | Score | Pass Rate | Passed | Source |", "| --- | --- | ---: | ---: | --- | --- |"])
    for row in benchmark["runs"]:
        lines.append(
            f"| `{row['eval_id']}` | `{row['configuration']}` | `{row['score']}` | `{row['pass_rate']}` | `{row['passed']}` | `{row['source']}` |"
        )

    lines.extend(["", "## Blocking Findings", ""])
    if benchmark["blocking_findings"]:
        for finding in benchmark["blocking_findings"]:
            lines.append(
                f"- `{finding['severity']}` `{finding['eval_id']}` `{finding['configuration']}`: {finding['finding']}"
            )
    else:
        lines.append("- none")

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("eval_run_dir", type=Path)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-md", type=Path)
    args = parser.parse_args()

    root = args.eval_run_dir
    if not root.exists() or not root.is_dir():
        print(f"Eval run directory does not exist: {root}", file=sys.stderr)
        return 1

    try:
        benchmark = build_benchmark(root)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    output_json = args.output_json or root / "benchmark.json"
    output_md = args.output_md or root / "benchmark.md"
    output_json.write_text(json.dumps(benchmark, indent=2) + "\n", encoding="utf-8")
    output_md.write_text(render_markdown(benchmark), encoding="utf-8")

    print(f"Wrote {output_json}")
    print(f"Wrote {output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
