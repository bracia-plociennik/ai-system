#!/usr/bin/env python3
"""Package a skill directory into a zip archive for transfer or review."""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True

try:
    from utils import find_skill_md
except ImportError:  # pragma: no cover
    from .utils import find_skill_md


EXCLUDED_PARTS = {".git", "__pycache__"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def should_include(path: Path) -> bool:
    if any(part in EXCLUDED_PARTS for part in path.parts):
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    return path.is_file()


def package(skill_dir: Path, output: Path) -> int:
    find_skill_md(skill_dir)
    skill_root = skill_dir.resolve()
    output_path = output.resolve(strict=False)
    if output_path == skill_root or skill_root in output_path.parents:
        raise ValueError(f"Output archive must be outside the skill directory: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(skill_dir.rglob("*")):
            if not should_include(path):
                continue
            archive.write(path, path.relative_to(skill_dir.parent))
            count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    output = args.output or (args.skill_dir.parent / f"{args.skill_dir.name}.zip")
    try:
        count = package(args.skill_dir, output)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Wrote {output} with {count} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
