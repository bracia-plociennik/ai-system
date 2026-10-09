"""Prepare a committed product projection without merging development runtime."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile

PRODUCT_DIRS = (".systems/", ".github/")
PRODUCT_FILES = {"README.md", "HUMANS.md", ".gitignore"}
RUNTIME = "ai-workflow-workspace/"


def git_environment():
    env = dict(os.environ)
    # -C does not override inherited repository/index selectors.
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
                "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"):
        env.pop(key, None)
    return env


def git(root, *args, env=None):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                            env=git_environment() if env is None else env, check=False)
    if result.returncode:
        raise ValueError("Git command failed: " + " ".join(args[:2]) + ": " +
                         result.stderr.decode(errors="replace").strip())
    return result.stdout


def commit(root, ref):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_./-]*", ref) or ".." in ref:
        raise ValueError("Invalid source/target reference")
    return git(root, "rev-parse", "--verify", ref + "^{commit}").decode().strip()


def path_kind(name):
    parts = PurePosixPath(name).parts
    if (not name or name.startswith("/") or "\\" in name or
            any(c in name for c in "\n\r\t") or
            any(p in {"", ".", ".."} for p in name.split("/"))):
        raise ValueError("Unsafe tracked path")
    if name.startswith(RUNTIME):
        return "runtime"
    if name not in PRODUCT_FILES and not name.startswith(PRODUCT_DIRS):
        raise ValueError("Unknown tracked publication path: " + name)
    if any(p in {".git", "node_modules", "__pycache__", ".assets"} or
           p == ".env" or p.startswith(".env.") or
           p.endswith((".pem", ".key", ".p12", ".pfx", ".pyc")) for p in parts):
        raise ValueError("Forbidden product publication path: " + name)
    return "product"


def tree(root, revision):
    result = {}
    for entry in git(root, "ls-tree", "-rz", revision).split(b"\0"):
        if not entry:
            continue
        metadata, raw_name = entry.split(b"\t", 1)
        mode, kind, oid = metadata.decode().split()
        name = raw_name.decode("utf-8")
        classification = path_kind(name)
        if classification == "product" and (kind != "blob" or mode not in {"100644", "100755"}):
            raise ValueError("Linked or non-regular product input: " + name)
        result[name] = (mode, oid, classification)
    return result


def product(entries):
    return {name: (mode, oid) for name, (mode, oid, kind) in entries.items() if kind == "product"}


def digest(entries):
    return hashlib.sha256(json.dumps(entries, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def plan(root, source="dev", target="origin/main"):
    root = Path(root).resolve(strict=True)
    source_sha, target_sha = commit(root, source), commit(root, target)
    git(root, "merge-base", "--is-ancestor", target_sha, source_sha)
    source_entries, target_entries = tree(root, source_sha), tree(root, target_sha)
    if any(value[2] == "runtime" for value in target_entries.values()):
        raise ValueError("Target already tracks runtime; reconcile explicitly before publication")
    source_product, target_product = product(source_entries), product(target_entries)
    if not PRODUCT_FILES.issubset(source_product):
        raise ValueError("Source is missing a required root product file")
    changes = [{"path": name, "change": "A" if name not in target_product else
                "D" if name not in source_product else "M"}
               for name in sorted(source_product.keys() | target_product.keys())
               if source_product.get(name) != target_product.get(name)]
    return {"source_commit": source_sha, "target_commit": target_sha,
            "product_file_count": len(source_product),
            "excluded_runtime_file_count": len(source_entries) - len(source_product),
            "product_manifest_sha256": digest(source_product), "changes": changes,
            "evidence_role": "supporting-only; not approval, QA or publication"}, source_product


def projection_tree(root, entries):
    with tempfile.TemporaryDirectory(prefix="product-projection-") as directory:
        env = git_environment()
        env["GIT_INDEX_FILE"] = str(Path(directory) / "index")
        git(root, "read-tree", "--empty", env=env)
        payload = b"".join((mode + " " + oid + "\t" + name).encode() + b"\0"
                           for name, (mode, oid) in sorted(entries.items()))
        subprocess.run(["git", "-C", str(root), "update-index", "-z", "--index-info"],
                       input=payload, env=env, check=True, capture_output=True)
        return git(root, "write-tree", env=env).decode().strip()


def destination(root, path):
    path = Path(path)
    if not path.is_absolute() or ".." in path.parts:
        raise ValueError("Release worktree requires an absolute normalized path")
    if any(p.is_symlink() for p in [path, *path.parents]):
        raise ValueError("Linked release worktree path")
    if path.exists() or not path.parent.is_dir():
        raise ValueError("Release worktree must not exist and its parent must exist")
    if path.is_relative_to(Path(root).resolve()):
        raise ValueError("Release worktree cannot be inside the source repository")
    return path


def verify_candidate(root, candidate, report, expected):
    candidate = Path(candidate)
    if any(p.is_symlink() for p in [candidate, *candidate.parents]):
        raise ValueError("Linked candidate path")
    candidate = candidate.resolve(strict=True)
    common_root = git(root, "rev-parse", "--path-format=absolute", "--git-common-dir").strip()
    common_candidate = git(candidate, "rev-parse", "--path-format=absolute", "--git-common-dir").strip()
    if common_candidate != common_root:
        raise ValueError("Candidate belongs to another repository")
    head = commit(candidate, "HEAD")
    if head != report["target_commit"]:
        parents = git(candidate, "show", "-s", "--format=%P", "HEAD").decode().split()
        head_entries = tree(candidate, head)
        if (parents != [report["target_commit"]] or
                any(value[2] != "product" for value in head_entries.values()) or
                product(head_entries) != expected):
            raise ValueError("Publication requires one product-only commit directly on the target")
    actual = {}
    for entry in git(candidate, "ls-files", "--stage", "-z").split(b"\0"):
        if not entry:
            continue
        metadata, name = entry.split(b"\t", 1)
        mode, oid, stage = metadata.decode().split()
        name = name.decode()
        if stage != "0" or path_kind(name) != "product":
            raise ValueError("Unexpected candidate index entry")
        actual[name] = (mode, oid)
    if actual != expected:
        raise ValueError("Candidate index differs from the complete committed product projection")
    object_format = git(root, "rev-parse", "--show-object-format").decode().strip()
    for name, (mode, oid) in expected.items():
        path = candidate / name
        if any(p.is_symlink() for p in [path, *path.parents] if p.is_relative_to(candidate)) or not path.is_file():
            raise ValueError("Missing or linked candidate product file: " + name)
        data = path.read_bytes()
        actual_oid = hashlib.new(object_format, b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if actual_oid != oid or bool(path.stat().st_mode & 0o111) != (mode == "100755"):
            raise ValueError("Candidate live product differs: " + name)
    git(candidate, "diff", "--quiet")
    if git(candidate, "ls-files", "--others", "--exclude-standard").strip():
        raise ValueError("Candidate contains untracked files")
    return candidate


def prepare(root, path, branch, report, expected):
    path = destination(root, path)
    if not branch or not branch.startswith("codex/publish/"):
        raise ValueError("Release branch must use codex/publish/")
    git(root, "check-ref-format", "--branch", branch)
    exists = subprocess.run(["git", "-C", str(root), "show-ref", "--verify", "--quiet",
                             "refs/heads/" + branch], env=git_environment(), check=False).returncode
    if exists != 1:
        raise ValueError("Release branch already exists or cannot be checked")
    if not report["changes"]:
        raise ValueError("No product changes; no release worktree or empty commit needed")
    projected = projection_tree(root, expected)
    git(root, "worktree", "add", "-b", branch, str(path), report["target_commit"])
    # Only the newly created isolated index is updated; source/runtime are untouched.
    git(path, "read-tree", "-m", "-u", report["target_commit"], projected)
    verify_candidate(root, path, report, expected)
    return {**report, "prepared_worktree": str(path), "branch": branch,
            "product_tree": projected, "commit_created": False, "push_performed": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--source", default="dev")
    parser.add_argument("--target", default="origin/main")
    operation = parser.add_mutually_exclusive_group()
    operation.add_argument("--prepare", type=Path)
    operation.add_argument("--verify-candidate", type=Path)
    parser.add_argument("--branch")
    parser.add_argument("--owner-approved", action="store_true")
    args = parser.parse_args()
    try:
        if args.prepare and not args.owner_approved:
            raise ValueError("Preparing a worktree requires scoped owner approval")
        if args.branch and not args.prepare:
            raise ValueError("--branch requires --prepare")
        root = args.repo.resolve(strict=True)
        report, entries = plan(root, args.source, args.target)
        if args.prepare:
            report = prepare(root, args.prepare, args.branch, report, entries)
        elif args.verify_candidate:
            verify_candidate(root, args.verify_candidate, report, entries)
            report["candidate_verified"] = True
        print(json.dumps(report, indent=2))
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print("Product publication blocked: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
