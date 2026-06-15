#!/usr/bin/env python3
"""Suggest a trigger-focused SKILL.md description from the skill body and trigger evals."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

try:
    from utils import find_skill_md, parse_skill_frontmatter, read_text
except ImportError:  # pragma: no cover
    from .utils import find_skill_md, parse_skill_frontmatter, read_text


def sentence_from_heading(text: str, heading: str) -> str | None:
    pattern = re.compile(rf"^## {re.escape(heading)}\n+(.*?)(?:\n## |\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(text)
    if not match:
        return None
    block = " ".join(line.strip("- ").strip() for line in match.group(1).splitlines() if line.strip())
    block = re.sub(r"\s+", " ", block).strip()
    if not block:
        return None
    return block.split(".")[0].strip()


def suggest_description(skill_dir: Path) -> str:
    skill_md = find_skill_md(skill_dir)
    frontmatter = parse_skill_frontmatter(skill_md)
    text = read_text(skill_md)
    name = frontmatter.get("name", skill_dir.name)
    purpose = sentence_from_heading(text, "Purpose")
    workflow = sentence_from_heading(text, "Workflow")
    pieces = [f"Use this skill when creating, updating, reviewing, or validating {name} work."]
    if purpose:
        pieces.append(purpose)
    if workflow:
        pieces.append(f"Apply it when the task needs this workflow: {workflow}")
    description = " ".join(pieces)
    return description[:1024]


def load_trigger_evals(path: Path | None) -> dict:
    if path is None:
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Trigger evals must be a JSON object")
    queries = data.get("queries", [])
    if not isinstance(queries, list):
        raise ValueError("Trigger evals queries must be a list")
    return data


def trigger_terms(trigger_evals: dict, should_trigger: bool) -> list[str]:
    terms: list[str] = []
    for item in trigger_evals.get("queries", []):
        if not isinstance(item, dict) or item.get("should_trigger") is not should_trigger:
            continue
        query = str(item.get("query", ""))
        words = re.findall(r"[A-Za-z][A-Za-z0-9-]{3,}", query.lower())
        for word in words:
            if word not in terms:
                terms.append(word)
    return terms[:8]


def suggest_from_triggers(skill_dir: Path, trigger_evals: dict) -> dict:
    candidate = suggest_description(skill_dir)
    positive_terms = trigger_terms(trigger_evals, True)
    negative_terms = trigger_terms(trigger_evals, False)
    if positive_terms:
        candidate += " Trigger on work involving " + ", ".join(positive_terms[:5]) + "."
    if negative_terms:
        candidate += " Do not use for adjacent tasks that primarily involve " + ", ".join(negative_terms[:5]) + "."
    return {
        "skill_name": skill_dir.name,
        "candidate_description": candidate[:1024],
        "positive_terms": positive_terms,
        "negative_terms": negative_terms,
        "accepted": False,
        "reason": "Candidate requires owner or reviewer acceptance after trigger eval review.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", type=Path)
    parser.add_argument("--trigger-evals", type=Path)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    try:
        trigger_evals = load_trigger_evals(args.trigger_evals)
        if trigger_evals:
            result = suggest_from_triggers(args.skill_dir, trigger_evals)
            if args.output_json:
                args.output_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            print(result["candidate_description"])
        else:
            print(suggest_description(args.skill_dir))
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
