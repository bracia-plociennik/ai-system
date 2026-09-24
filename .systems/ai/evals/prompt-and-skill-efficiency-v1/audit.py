#!/usr/bin/env python3
"""Measure the AI System instruction footprint without running an agent."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


FILES = {
    "root_template": ".systems/ai/templates/root/AGENTS.template.md",
    "skill": ".systems/ai/skills/skill-creator/SKILL.md",
    "response": ".systems/ai/core/response-contract.md",
    "model": ".systems/ai/core/model-selection-guidance.md",
    "validation": ".systems/ai/core/validation-routing.md",
    "prompt_module": ".systems/ai/templates/prompting/prompt-module.template.md",
}


def section(body: str, title: str) -> str:
    match = re.search(rf"(?m)^## {re.escape(title)}\s*$", body)
    if not match:
        return ""
    rest = body[match.end() :]
    end = re.search(r"(?m)^## ", rest)
    return rest[: end.start()] if end else rest


def measure(root: Path) -> dict:
    texts = {name: (root / path).read_text(encoding="utf-8") for name, path in FILES.items()}
    skill_frontmatter = texts["skill"].split("---", 2)[1]
    description = re.search(r"(?m)^description:\s*(.*)$", skill_frontmatter)
    if not description:
        raise ValueError("skill-creator description is missing")

    source_order = section(texts["root_template"], "Source Of Truth")
    always_read = section(texts["root_template"], "Always Read First")
    footer = section(texts["response"], "Required Footer") or section(
        texts["response"], "Decision And Handoff Footer"
    )

    return {
        "files": {
            name: {"lines": len(body.splitlines()), "characters": len(body)}
            for name, body in texts.items()
        },
        "root_source_order_items": len(re.findall(r"(?m)^\d+\. ", source_order)),
        "root_always_read_items": len(re.findall(r"(?m)^\d+\. ", always_read)),
        "skill_description_characters": len(description.group(1)),
        "skill_requires_full_validator": bool(
            re.search(r"(?m)^\.systems/scripts/validate-ai-system\s*$", texts["skill"])
        ),
        "model_names_hardcoded": sorted(set(re.findall(r"GPT-\d+(?:\.\d+)? [A-Za-z]+ High", texts["model"]))),
        "response_requires_footer_for_all_substantive": "Every substantive response must end" in texts["response"],
        "response_footer_template_lines": len(footer.splitlines()),
        "validation_has_semantic_first_order": "findings-first" in texts["validation"]
        and "supporting evidence" in texts["validation"],
        "prompt_module_forbidden_override_bullets": len(
            re.findall(r"(?m)^- ", section(texts["prompt_module"], "Forbidden Overrides"))
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(measure(args.root), ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
