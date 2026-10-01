"""Shared local validation identity and no-clobber evidence primitives."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import uuid
from pathlib import Path


class InvalidEvidence(ValueError):
    pass


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def fingerprint(value):
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def relative_path(value):
    if not isinstance(value, str) or not value or "\\" in value:
        raise InvalidEvidence("Invalid relative evidence path")
    path = Path(value)
    if path.is_absolute() or any(p in {"", ".", ".."} for p in value.split("/")):
        raise InvalidEvidence("Evidence path must be normalized and relative")
    return path


def contained_file(root, value):
    root = Path(root).resolve(strict=True)
    path = root / relative_path(value)
    if any(p.is_symlink() for p in [path, *path.parents] if p != root and root in p.parents):
        raise InvalidEvidence("Symlink evidence path is forbidden")
    resolved = path.resolve(strict=True)
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise InvalidEvidence("Evidence path escapes its owned root")
    return resolved


def git_output(root, *args):
    proc = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    return proc.stdout.strip() if proc.returncode == 0 else ""


def product_identity(root):
    root = Path(root).resolve()
    paths = git_output(root, "ls-files", "--", ".systems", ".github", "README.md", "HUMANS.md", ".gitignore").splitlines()
    # Approved new product paths are included in current source identity, but never private runtime.
    for directory in (root / ".systems", root / ".github"):
        if directory.is_dir():
            paths += [str(p.relative_to(root)) for p in directory.rglob("*") if p.is_file()]
    paths += [p for p in ("README.md", "HUMANS.md", ".gitignore") if (root / p).is_file()]
    hashes = {}
    for name in sorted(set(paths)):
        if any(part in {"__pycache__", ".git"} for part in Path(name).parts):
            continue
        path = contained_file(root, name)
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {"head": git_output(root, "rev-parse", "HEAD"), "source_digest": fingerprint(hashes), "files": hashes}


def safe_destination(value, product_root):
    path = Path(value).expanduser().absolute()
    product_root = Path(product_root).resolve()
    if path.exists() or path.is_symlink():
        raise InvalidEvidence("Evidence destination already exists; use a new run path")
    parent = path.parent.resolve(strict=True)
    if not parent.is_dir():
        raise InvalidEvidence("Evidence parent must exist")
    for candidate in (path.parent, *path.parent.parents):
        if candidate.is_symlink() and str(candidate) not in {"/tmp", "/var"}:
            raise InvalidEvidence("Evidence parent may not be a symlink")
    resolved = parent / path.name
    containing_repo = git_output(parent, "rev-parse", "--show-toplevel")
    if containing_repo:
        containing_repo = Path(containing_repo).resolve()
        if containing_repo != product_root:
            raise InvalidEvidence("Evidence destination belongs to a foreign repository")
        rel = resolved.relative_to(product_root)
        if not rel.parts or rel.parts[0] not in {"ai-workflow-workspace", "ai-system-workspace"}:
            raise InvalidEvidence("Evidence destination is a protected product path")
        if git_output(product_root, "ls-files", "--", str(rel)):
            raise InvalidEvidence("Tracked or deleted-tracked evidence destination is protected")
    elif resolved.is_relative_to(product_root):
        raise InvalidEvidence("Evidence destination is inside product source")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", path.name):
        raise InvalidEvidence("Unsafe evidence filename")
    return resolved


def atomic_create(path, text, expected_parent=None):
    """Create, never replace; pin the directory while publishing the complete file."""
    path = Path(path)
    directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    actual = os.fstat(directory)
    if expected_parent is not None and (actual.st_dev, actual.st_ino) != expected_parent:
        os.close(directory)
        raise InvalidEvidence("Evidence directory changed after preflight")
    temporary = None
    try:
        temporary = ".validation-" + uuid.uuid4().hex
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=directory)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path.name, src_dir_fd=directory, dst_dir_fd=directory, follow_symlinks=False)
        os.fsync(directory)
    finally:
        if temporary:
            os.unlink(temporary, dir_fd=directory)
        os.close(directory)
