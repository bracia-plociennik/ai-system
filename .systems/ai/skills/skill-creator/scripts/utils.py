"""Shared stdlib-only helpers for skill creator scripts."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def normalize_skill_name(value: str) -> str:
    name = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    name = re.sub(r"-+", "-", name)
    if not name:
        raise ValueError("Skill name cannot be empty after normalization")
    if len(name) > 63:
        raise ValueError("Skill name must be 63 characters or fewer")
    if not NAME_RE.fullmatch(name):
        raise ValueError(f"Invalid skill name: {name}")
    return name


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str, overwrite: bool = False) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(read_text(path))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def dump_json(path: Path, data: dict[str, Any], overwrite: bool = True) -> None:
    write_text(path, json.dumps(data, indent=2, sort_keys=True) + "\n", overwrite=overwrite)


def parse_skill_frontmatter(skill_md: Path) -> dict[str, str]:
    text = read_text(skill_md)
    if not text.startswith("---\n"):
        raise ValueError(f"Missing frontmatter: {skill_md}")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError(f"Unclosed frontmatter: {skill_md}")
    result: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"Invalid frontmatter line in {skill_md}: {line}")
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip("'\"")
    return result


def find_skill_md(skill_dir: Path) -> Path:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        raise FileNotFoundError(f"Missing SKILL.md: {skill_md}")
    return skill_md
