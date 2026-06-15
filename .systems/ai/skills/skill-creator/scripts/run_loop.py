#!/usr/bin/env python3
"""Run the local skill validation and eval-report loop."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", type=Path)
    parser.add_argument("--evals-json", type=Path)
    parser.add_argument("--run-dir", type=Path)
    args = parser.parse_args()

    try:
        run([sys.executable, str(SCRIPT_DIR / "quick_validate.py"), str(args.skill_dir)])
        if args.evals_json and args.run_dir:
            run(
                [
                    sys.executable,
                    str(SCRIPT_DIR / "run_eval.py"),
                    str(args.evals_json),
                    "--output-dir",
                    str(args.run_dir),
                    "--overwrite",
                ]
            )
        if args.run_dir and list(args.run_dir.rglob("grading.json")):
            run([sys.executable, str(SCRIPT_DIR / "aggregate_benchmark.py"), str(args.run_dir)])
            run([sys.executable, str(SCRIPT_DIR / "generate_report.py"), str(args.run_dir / "benchmark.json")])
    except subprocess.CalledProcessError as exc:
        return exc.returncode

    print("Skill creator loop completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
