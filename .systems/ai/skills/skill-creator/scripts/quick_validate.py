#!/usr/bin/env python3
"""Validate an AI System skill folder using stdlib-only checks."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FRONTMATTER_KEY_RE = re.compile(r"^[A-Za-z0-9_-]+:")
AUTHORITY_PATTERNS = (
    re.compile(r"AGENTS\.md", re.IGNORECASE),
    re.compile(r"privacy|workspace", re.IGNORECASE),
    re.compile(r"permissions|owner-approved|owner approval", re.IGNORECASE),
    re.compile(r"validation", re.IGNORECASE),
    re.compile(r"evidence", re.IGNORECASE),
    re.compile(r"stop conditions|final acceptance", re.IGNORECASE),
)
UNSAFE_PATTERNS = (
    re.compile("clau" + "de -p", re.IGNORECASE),
    re.compile(r"\." + "clau" + "de/"),
    re.compile("CLAUDE" + "CODE"),
    re.compile(r"fonts\.googleapis", re.IGNORECASE),
    re.compile(r"fonts\.gstatic", re.IGNORECASE),
    re.compile(r"cdn\.", re.IGNORECASE),
    re.compile(r"unpkg\.com", re.IGNORECASE),
    re.compile(r"jsdelivr\.net", re.IGNORECASE),
)
UNDOCUMENTED_DEP_RE = re.compile(
    r"^[ \t]*(import[ \t]+yaml\b|from[ \t]+yaml[ \t]+import\b)",
    re.MULTILINE,
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"File is not UTF-8 text: {path}") from exc


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = read_text(path)
    if not text.startswith("---\n"):
        raise ValueError(f"Missing YAML frontmatter: {path}")

    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError(f"Unclosed YAML frontmatter: {path}")

    values: dict[str, str] = {}
    current_key: str | None = None
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if FRONTMATTER_KEY_RE.match(line):
            key, value = line.split(":", 1)
            current_key = key.strip()
            values[current_key] = value.strip().strip("'\"")
        elif current_key and line.startswith((" ", "\t")):
            values[current_key] += " " + line.strip().strip("'\"")
        else:
            raise ValueError(f"Invalid frontmatter line in {path}: {line}")

    for key in ("name", "description"):
        if not values.get(key):
            raise ValueError(f"Missing required frontmatter key '{key}': {path}")

    extra = sorted(set(values) - {"name", "description"})
    if extra:
        raise ValueError(f"Unexpected frontmatter keys in {path}: {', '.join(extra)}")

    return values


def iter_text_files(root: Path) -> list[Path]:
    paths: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix in {".md", ".py", ".txt", ".json", ".html", ".css", ".js"}:
            paths.append(path)
    return sorted(paths)


def validate(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    if not skill_dir.exists() or not skill_dir.is_dir():
        return [f"Skill directory does not exist: {skill_dir}"]

    name = skill_dir.name
    if not NAME_RE.fullmatch(name):
        errors.append(f"Skill directory name must be lowercase kebab-case: {name}")

    skill_md = skill_dir / "SKILL.md"
    readme = skill_dir / "README.md"

    if not skill_md.is_file():
        errors.append(f"Missing SKILL.md: {skill_md}")
    else:
        try:
            frontmatter = parse_frontmatter(skill_md)
        except ValueError as exc:
            errors.append(str(exc))
        else:
            if frontmatter["name"] != name:
                errors.append(
                    f"Frontmatter name must match directory name: {frontmatter['name']} != {name}"
                )
            description = frontmatter["description"]
            if len(description) > 1024:
                errors.append("Frontmatter description must be 1024 characters or fewer")
            if "<" in description or ">" in description:
                errors.append("Frontmatter description must not contain angle brackets")

        body = read_text(skill_md)
        for pattern in AUTHORITY_PATTERNS:
            if not pattern.search(body):
                errors.append(f"SKILL.md missing authority boundary pattern: {pattern.pattern}")

    if not readme.is_file():
        errors.append(f"Missing README.md: {readme}")
    else:
        readme_text = read_text(readme)
        if "SKILL.md" not in readme_text:
            errors.append("README.md must point to SKILL.md")
        if len(readme_text.splitlines()) > 80:
            errors.append("README.md must stay under 80 lines")

    for path in iter_text_files(skill_dir):
        text = read_text(path)
        for pattern in UNSAFE_PATTERNS:
            if pattern.search(text):
                errors.append(f"Unsafe external/runtime marker in {path}: {pattern.pattern}")
        if path.suffix == ".py" and UNDOCUMENTED_DEP_RE.search(text):
            errors.append(f"Undeclared Python dependency import in {path}: yaml")

    for resource_name in ("assets", "eval-viewer"):
        resource_dir = skill_dir / resource_name
        if not resource_dir.exists():
            continue
        for path in iter_text_files(resource_dir):
            text = read_text(path)
            if re.search(r"https?://", text):
                errors.append(f"External resource URL in offline {resource_name}: {path}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", type=Path)
    args = parser.parse_args()

    errors = validate(args.skill_dir)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(f"Skill validation passed: {args.skill_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
