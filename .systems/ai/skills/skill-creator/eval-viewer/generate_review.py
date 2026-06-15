#!/usr/bin/env python3
"""Generate a standalone offline HTML benchmark review."""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path


def render(data: dict) -> str:
    rows = data.get("rows") or []
    if not rows:
        rows = data.get("runs") or []
    body_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(str(row.get('eval_id', '')))}</td>"
        f"<td>{html.escape(str(row.get('configuration', '')))}</td>"
        f"<td>{html.escape(str(row.get('score', '')))}</td>"
        f"<td>{html.escape(str(row.get('pass_rate', '')))}</td>"
        f"<td>{html.escape(str(row.get('passed', '')))}</td>"
        f"<td><textarea data-run=\"{html.escape(str(row.get('eval_id', '')))}-{html.escape(str(row.get('configuration', '')))}\"></textarea></td>"
        "</tr>"
        for row in rows
    )
    metadata = data.get("metadata", {})
    skill_name = data.get("skill_name", metadata.get("skill_name", "unknown"))
    eval_count = data.get("eval_count", metadata.get("eval_count", 0))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Skill Benchmark Review</title>
  <style>
    body {{ font-family: ui-sans-serif, system-ui, sans-serif; margin: 2rem; color: #171717; }}
    main {{ max-width: 1040px; margin: 0 auto; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
    th, td {{ border: 1px solid #d0d0d0; padding: 0.5rem; text-align: left; }}
    th {{ background: #f3f3f3; }}
    textarea {{ width: 100%; min-height: 5rem; }}
    button {{ margin-top: 1rem; padding: 0.5rem 0.75rem; }}
  </style>
</head>
<body>
  <main>
    <h1>Skill Benchmark Review</h1>
    <p>Skill: <strong>{html.escape(str(skill_name))}</strong></p>
    <p>Eval count: <strong>{html.escape(str(eval_count))}</strong></p>
    <table>
      <thead><tr><th>Eval</th><th>Configuration</th><th>Score</th><th>Pass Rate</th><th>Passed</th><th>Feedback</th></tr></thead>
      <tbody>
        {body_rows}
      </tbody>
    </table>
    <button id="download-feedback">Download feedback.json</button>
  </main>
  <script>
    document.getElementById("download-feedback").addEventListener("click", () => {{
      const reviews = Array.from(document.querySelectorAll("textarea")).map((field) => ({{
        run_id: field.dataset.run,
        feedback: field.value,
        timestamp: new Date().toISOString()
      }}));
      const blob = new Blob([JSON.stringify({{status: "complete", reviews}}, null, 2)], {{type: "application/json"}});
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "feedback.json";
      link.click();
      URL.revokeObjectURL(link.href);
    }});
  </script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("benchmark_json", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        data = json.loads(args.benchmark_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if not isinstance(data, dict):
        print("Benchmark must be a JSON object", file=sys.stderr)
        return 1

    output = args.output or (args.benchmark_json.parent / "benchmark.html")
    output.write_text(render(data), encoding="utf-8")
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
