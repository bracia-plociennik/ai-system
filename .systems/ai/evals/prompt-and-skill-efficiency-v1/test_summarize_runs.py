#!/usr/bin/env python3
"""Focused regression tests for the exploratory run summarizer."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location("summarize_runs", Path(__file__).with_name("summarize_runs.py"))
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SummarizeRunsTests(unittest.TestCase):
    def test_compound_command_counts_read_before_later_failure(self) -> None:
        events = [
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": "cat .systems/ai/core/task-intake.md; git status",
                    "exit_code": 128,
                },
            },
            {"type": "turn.completed", "usage": {"input_tokens": 10, "output_tokens": 5}},
        ]
        with tempfile.TemporaryDirectory() as temporary:
            log = Path(temporary) / "compound.jsonl"
            log.write_text("\n".join(json.dumps(event) for event in events) + "\n", encoding="utf-8")
            result = MODULE.summarize(log)

        self.assertEqual(result["core_docs"], [".systems/ai/core/task-intake.md"])
        self.assertEqual(result["core_docs_read_estimate"], 1)
        self.assertTrue(result["completed"])


if __name__ == "__main__":
    unittest.main()
