"""Typed negative assertions and complete per-suite rejection accounting."""
import argparse
import json
import re
from pathlib import Path


def verify(case, code, output):
    if code in {126, 127} or code < 0 or code >= 128:
        raise ValueError("Infrastructure or interrupted process cannot satisfy rejection")
    if code != case["exit_code"] or not case["diagnostic"] or case["diagnostic"] not in output:
        raise ValueError(f"Wrong rejection: expected exit {case['exit_code']} and {case['diagnostic']!r}; got {code}")
    if re.search(r"(?:SyntaxError|ModuleNotFoundError|command not found|Permission denied)", output):
        raise ValueError("Infrastructure diagnostic cannot satisfy rejection")


def complete(cases, suite, executed):
    expected = {name for name, case in cases.items() if suite == "all" or case["suite"] == suite}
    if len(executed) != len(set(executed)) or set(executed) != expected:
        raise ValueError(f"Incomplete negative coverage: missing={sorted(expected - set(executed))}, extra={sorted(set(executed) - expected)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expectations", required=True)
    parser.add_argument("--executed", required=True)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--case")
    parser.add_argument("--code", type=int)
    parser.add_argument("--output")
    args = parser.parse_args()
    cases = json.loads(Path(args.expectations).read_text())["cases"]
    try:
        if args.case:
            case = cases.get(args.case)
            if not case or (args.suite != "all" and case["suite"] != args.suite):
                raise ValueError("Undeclared negative assertion or wrong suite ownership")
            verify(case, args.code, Path(args.output).read_text())
            with Path(args.executed).open("a") as stream:
                stream.write(args.case + "\n")
        else:
            executed = Path(args.executed).read_text().splitlines() if Path(args.executed).exists() else []
            complete(cases, args.suite, executed)
            print(f"SMOKE_NEGATIVE_COVERAGE suite={args.suite} count={len(executed)} complete=true")
    except (ValueError, OSError) as exc:
        parser.exit(1, str(exc) + "\n")
