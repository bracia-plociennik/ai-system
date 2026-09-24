#!/usr/bin/env python3
"""Summarize isolated agent-run traces; quality still needs human review."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def summarize(log: Path) -> dict:
    events = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line]
    commands = [
        event["item"]["command"]
        for event in events
        if event.get("type") == "item.completed"
        and event.get("item", {}).get("type") == "command_execution"
    ]
    usage = next((event["usage"] for event in events if event.get("type") == "turn.completed"), {})
    # A compound command may read a file successfully and then fail a later
    # operation (for example, `cat ...; git status` outside a git checkout).
    read_commands = [command for command in commands if re.search(r"\b(cat|sed|head|tail|nl)\b", command)]
    core_docs = sorted(set(re.findall(r"\.systems/ai/core/[\w-]+\.md", "\n".join(read_commands))))
    return {
        "case": log.stem,
        "completed": any(event.get("type") == "turn.completed" for event in events),
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "commands": len(commands),
        "core_docs_read_estimate": len(core_docs),
        "core_docs": core_docs,
        "file_change_events": sum(
            event.get("type") == "item.completed" and event.get("item", {}).get("type") == "file_change"
            for event in events
        ),
        "broad_validator_invoked": any("validate-ai-system" in command and not re.search(r"\b(cat|rg|sed)\b", command) for command in commands),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", type=Path)
    args = parser.parse_args()
    cases = [summarize(path) for path in sorted(args.logs.glob("*.jsonl")) if path.stem != "probe"]
    print(json.dumps(cases, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
