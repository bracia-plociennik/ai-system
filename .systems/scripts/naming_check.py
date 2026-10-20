"""Naming consumer: current managed artifacts, with immutable source boundaries."""
import argparse
from datetime import date
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

NAME = re.compile(r"[a-z0-9]+([.-][a-z0-9]+)*\.md\Z")
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
SOURCE_DIRS = {"projects", "context", "documents", "contracts", "assets", "archive"}
PRESERVATION = "core/naming-source-preservation.json"
V4_FILES = {"check-ins-v4.jsonl", "check-ins-v4.csv", "check-ins-v4.metrics.csv",
            "check-ins-v4.md", "check-ins-v4.trends.md", "check-ins-v4-fields.md"}


def aggregate_alias(file, relative, owner):
    """The existing V4 pointer contract is the only managed link exception."""
    prefix = "personal-ops/indexes/"
    if relative != prefix + "check-ins-v4-active" and relative not in {prefix + name for name in V4_FILES}:
        return False
    index = owner / prefix
    pointer = index / "check-ins-v4-active"
    if not pointer.is_symlink():
        raise ValueError("Missing canonical aggregate pointer")
    target = os.readlink(pointer)
    if not re.fullmatch(r"generations-v4/[0-9a-f]{24}", target):
        raise ValueError("Invalid aggregate pointer target")
    generation = index / target
    if (index / "generations-v4").is_symlink() or generation.is_symlink() or not generation.is_dir():
        raise ValueError("Linked or missing aggregate generation")
    if file != pointer and os.readlink(file) != "check-ins-v4-active/" + file.name:
        raise ValueError("Invalid aggregate compatibility link")
    return True


def source_exception(relative):
    parts = PurePosixPath(relative).parts
    if parts[:4] == (".systems", "ai", "skills", "legacy"):
        return True
    return len(parts) >= 6 and parts[:3] == (".systems", "ai", "skills") and parts[4] == "context"


def valid_name(relative, workspace=False):
    """Exceptions bind to governing roots, never to arbitrary basenames."""
    parts = PurePosixPath(relative).parts
    base = parts[-1]
    if base == "README.md":
        return True
    if not workspace:
        if relative in {"AGENTS.md", "HUMANS.md", ".systems/ai/templates/root/AGENTS.template.md"}:
            return True
        if source_exception(relative):
            return True
        skill = parts[:3] == (".systems", "ai", "skills") and len(parts) == 5
    else:
        if relative == "tasks/TaskForge.md":
            return True
        if len(parts) == 4 and parts[:3] == ("tasks", "TaskNotes", "Tasks"):
            return True  # task-management.md: Use Title as Filename, on.
        if len(parts) == 6 and parts[:3] == ("tasks", "silverbullet", "tasks"):
            return True  # Default SilverBullet Space: client/project/native title.md.
        if len(parts) == 4 and parts[:2] in {("tasks", "weekly-plans"), ("personal-ops", "weekly-check-ins-v4")}:
            match = re.fullmatch(r"([0-9]{4})-W([0-9]{2})\.md", base)
            if match and parts[2] == match[1]:
                try:
                    date.fromisocalendar(int(match[1]), int(match[2]), 1)
                    return True
                except ValueError:
                    pass
        skill = len(parts) == 3 and parts[0] == "skills"
    if skill and base == "SKILL.md" and SLUG.fullmatch(parts[-2]):
        return True
    return NAME.fullmatch(base) is not None


def preserved_directory(parts):
    """Only declared source/history slots; never whole owner or project-state roots."""
    # Owner execution slots contain source/check fixtures, not managed evidence.
    # The walker still rejects a linked slot itself before this boundary applies.
    if parts in {('.tmp',), ('.worktrees',)}:
        return True
    if parts[0] in SOURCE_DIRS:
        return True
    if len(parts) >= 2 and parts[:2] == ("dump", "incoming"):
        return True
    if len(parts) >= 3 and parts[0] == "skills" and parts[2] == "context":
        return True
    if parts == ("capture-state", "history"):
        return True
    if parts in {("tasks", "archive"), ("tasks", "TaskNotes", "Archive"), ("personal-ops", "archive")}:
        return True
    if len(parts) == 4 and parts[:2] == ("tasks", "migration-reports") and parts[3] in {"backups", "removed-tasknotes", "active-folder-originals"}:
        return True
    if parts[0] == "project-state":
        if len(parts) == 4 and parts[2] == "capture-state" and parts[3] == "history":
            return True
        if len(parts) == 4 and parts[3] in {"backups", "router-backups", "tests"}:
            return True
    return False


def duplicate_free(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("Duplicate preservation field")
        out[key] = value
    return out


def preservation_entries(workspace):
    if (workspace / "core").is_symlink():
        raise ValueError("Linked naming registry ancestor")
    manifest = workspace / PRESERVATION
    if not manifest.exists() and not manifest.is_symlink():
        return {}
    if manifest.is_symlink() or not manifest.is_file():
        raise ValueError("Linked or invalid naming preservation registry")
    data = json.loads(manifest.read_text(), object_pairs_hook=duplicate_free)
    if not isinstance(data, dict) or set(data) != {"schema_version", "inputs"} or type(data["schema_version"]) is not int or data["schema_version"] != 1 or not isinstance(data["inputs"], list):
        raise ValueError("Invalid naming preservation registry schema")
    entries = {}
    for entry in data["inputs"]:
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256", "source_commit", "disposition"}:
            raise ValueError("Invalid preservation entry fields")
        path = entry["path"]
        if not isinstance(path, str) or not path or "\\" in path or PurePosixPath(path).is_absolute() or path != str(PurePosixPath(path)) or any(p in {".", ".."} for p in PurePosixPath(path).parts):
            raise ValueError("Invalid preservation path")
        # Only historical loose root inputs; managed files cannot be exempted.
        if len(PurePosixPath(path).parts) != 1 or not path.endswith(".md") or path in {"status.md", "memory.md", "README.md", "AGENTS.md", "HUMANS.md"} or NAME.fullmatch(path):
            raise ValueError("Preservation entry is not a noncanonical loose root input")
        if path in entries or entry["disposition"] != "preserved-unclassified" or not isinstance(entry["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]) or not isinstance(entry["source_commit"], str) or not re.fullmatch(r"[0-9a-f]{40}", entry["source_commit"]):
            raise ValueError("Invalid or duplicate historical preservation identity")
        file = workspace / path
        if file.is_symlink() or not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError("Missing, linked or changed preserved root input")
        result = subprocess.run(["git", "-C", str(workspace), "cat-file", "blob", entry["source_commit"] + ":" + path], capture_output=True)
        if result.returncode or hashlib.sha256(result.stdout).hexdigest() != entry["sha256"]:
            raise ValueError("Preserved root input has no matching historical Git provenance")
        entries[path] = entry
    return entries


def files_under(root, prunes=(), workspace=False):
    """Yield owner-relative paths without following directory/file links."""
    prunes = {Path(os.path.abspath(p)) for p in prunes}

    def walk(directory, owner):
        for file in sorted(directory.iterdir()):
            if file.name == ".git" or file in prunes:
                continue
            relative = file.relative_to(owner).as_posix()
            if file.is_symlink():
                if workspace and aggregate_alias(file, relative, owner):
                    continue
                raise ValueError("Linked naming input: " + str(file))
            if file.is_dir():
                parts = PurePosixPath(relative).parts
                if workspace and len(parts) == 2 and parts[0] in {"clients", "owned-assets"}:
                    yield from walk(file, file)
                elif not (workspace and preserved_directory(parts)):
                    yield from walk(file, owner)
            elif file.is_file() and file.suffix == ".md":
                yield file, relative
    yield from walk(root, root)


def check(repo, workspace=None, prunes=()):
    failures = []

    def inspect(path, relative, source, private=False):
        if not valid_name(relative, private):
            failures.append(f"Invalid Markdown filename ({source}): {path}")
            if "_" in Path(relative).name:
                failures.append(f"Markdown filename contains underscore ({source}): {path}")

    for file, relative in files_under(repo, prunes):
        inspect(relative, relative, "filesystem")
    if workspace is not None:
        if workspace.is_symlink() or not workspace.is_dir():
            raise ValueError("Selected naming workspace is missing or linked")
        for parent in workspace.parents:
            if parent.is_symlink():
                raise ValueError("Linked workspace ancestor")
        preserved = preservation_entries(workspace)
        for file, relative in files_under(workspace, workspace=True):
            if file.parent == workspace and file.name in preserved:
                print("Preserved historical unclassified naming input: " + str(file))
                continue
            inspect(file, relative, "workspace-filesystem", True)
    git = subprocess.run(["git", "-C", str(repo), "rev-parse", "--is-inside-work-tree"], capture_output=True)
    if git.returncode == 0:
        paths = subprocess.check_output(["git", "-C", str(repo), "ls-files", "-z", "--", "*.md"]).decode().split("\0")
        for relative in filter(None, paths):
            inspect(relative, relative, "git-index")
    return failures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--workspace", type=Path)
    parser.add_argument("--prune", type=Path, action="append", default=[])
    args = parser.parse_args()
    try:
        failures = check(args.repo, args.workspace, args.prune)
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print("Naming input boundary failed: " + str(error), file=sys.stderr)
        return 1
    for failure in failures:
        print(failure)
    if failures:
        print("Naming check failed. Use lowercase kebab-case for new non-root Markdown files unless the path is an explicit AI System exception.")
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
