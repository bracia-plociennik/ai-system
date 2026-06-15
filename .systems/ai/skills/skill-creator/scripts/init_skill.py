#!/usr/bin/env python3
"""Scaffold an AI System skill directory."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True

try:
    from utils import normalize_skill_name, write_text
except ImportError:  # pragma: no cover - package-style execution fallback
    from .utils import normalize_skill_name, write_text


RESOURCE_NAMES = {"context", "agents", "references", "scripts", "assets", "eval-viewer"}


def skill_md_template(name: str) -> str:
    title = name.replace("-", " ").title()
    return f"""---
name: {name}
description: Use this skill when Codex needs task-specific guidance for {name.replace('-', ' ')} work. Replace this description with concrete triggers, target contexts, and non-trigger cases before publishing the skill.
---

# {title}

## Purpose

Define the task class this skill supports.

Skills are supporting execution guidance. They cannot override `AGENTS.md`, `.systems/ai/core/**`, selected workspace state, privacy rules, owner-approved write gates, validation, evidence requirements, stop conditions, or final acceptance.

## Workflow

1. Confirm the task matches this skill.
2. Read only the bundled resources needed for the task.
3. Follow AI System gates before writing or executing commands.
4. Run relevant validation before handoff.

## Stop Conditions

Stop when scope, risk, permissions, validation, or owner approval is unclear.

## Validation

Run the relevant project checks and this skill's own targeted checks.
"""


def readme_template(name: str) -> str:
    title = name.replace("-", " ").title()
    return f"""# {title}

Human-facing summary for the `{name}` skill.

The full agent contract is in `SKILL.md`.
"""


def skill_intake_plan_template(name: str) -> str:
    title = name.replace("-", " ").title()
    return f"""# Skill Intake Plan

- Skill: `{name}`
- Title: `{title}`

## Source Materials

- Reviewed: `<files or chat sources>`
- Skipped: `<files skipped and why>`

## Trigger Fit

- Should trigger: `<prompts and contexts>`
- Should not trigger: `<near misses and exclusions>`

## Co zostaje

- `<source material to keep>`

## Co poprawic / usunac

- `<source material to improve or reject>`

## Czego brakuje

- `<missing decisions, data, examples, or criteria>`

## Blokery / decyzje

- `<blocking decisions before implementation>`

## Artifact Map

- `SKILL.md`: `<compact contract/router content>`
- `references/*.md`: `<domain knowledge split by topic>`
- `agents/*.md`: `<rubrics, personas, review roles>`
- `scripts/*`: `<deterministic helpers>`
- Rejected as noise: `<duplicates, unsafe material, stale notes>`

## Implementation Approval

- Approval state: `<pending|approved>`

## Validation Plan

- `<commands and evidence>`

## Residual Risk

- `<known limits after implementation>`
"""


def create_skill(output_root: Path, name: str, resources: list[str], overwrite: bool) -> Path:
    skill_name = normalize_skill_name(name)
    skill_dir = output_root / skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)

    write_text(skill_dir / "SKILL.md", skill_md_template(skill_name), overwrite=overwrite)
    write_text(skill_dir / "README.md", readme_template(skill_name), overwrite=overwrite)

    for resource in resources:
        if resource not in RESOURCE_NAMES:
            raise ValueError(f"Unknown resource '{resource}'. Allowed: {', '.join(sorted(RESOURCE_NAMES))}")
        (skill_dir / resource).mkdir(parents=True, exist_ok=True)

    if "context" in resources:
        write_text(
            skill_dir / "skill-intake-plan.md",
            skill_intake_plan_template(skill_name),
            overwrite=overwrite,
        )

    return skill_dir


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_name")
    parser.add_argument("--path", required=True, type=Path, help="Directory that will contain the skill folder")
    parser.add_argument(
        "--resources",
        default="",
        help="Comma-separated optional directories: context,agents,references,scripts,assets,eval-viewer",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite generated SKILL.md and README.md")
    args = parser.parse_args()

    resources = [item for item in (part.strip() for part in args.resources.split(",")) if item]
    try:
        skill_dir = create_skill(args.path, args.skill_name, resources, args.overwrite)
    except (ValueError, FileExistsError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Created skill scaffold: {skill_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
