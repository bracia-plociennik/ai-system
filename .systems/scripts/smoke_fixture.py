"""Copy the complete product inventory into one independent smoke transaction."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
SUITES = ("core", "skills", "workspace", "personal-ops", "tasks", "dreaming", "quality")


def run_transactions(commands):
    """Run at most two isolated transactions, drain both, then stop on failure."""
    results = []
    with ThreadPoolExecutor(max_workers=2) as workers:
        for start in range(0, len(commands), 2):
            futures = [workers.submit(subprocess.run, command, stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT, text=True)
                       for command in commands[start:start + 2]]
            batch = [future.result() for future in futures]
            results.extend(batch)
            if any(result.returncode for result in batch):
                break
    return results


def copy_fixture(root, destination, extras=()):
    root = Path(root).resolve(strict=True)
    destination = Path(destination)
    if destination.is_symlink() or not destination.is_dir() or any(destination.iterdir()):
        raise ValueError("Smoke destination must be an empty unlinked directory")
    destination = destination.resolve(strict=True)
    if destination.is_relative_to(root):
        raise ValueError("Smoke destination must be outside the product root")
    inventory = subprocess.check_output([
        "git", "-C", str(root), "ls-files", "-z", "--",
        ".systems", ".github", "README.md", "HUMANS.md", ".gitignore",
    ]).decode().rstrip("\0").split("\0")
    for name in extras:
        if (not name.startswith((".systems/", ".github/")) or re.search(r"\s", name)
                or any(marker in name for marker in ("..", ".env", "private", "secret"))
                or name.endswith((".pem", ".key", ".p12", ".pfx"))):
            raise ValueError("Unsafe extra product path: " + name)
    names = sorted(set(inventory + list(extras)))
    sources = []
    for name in names:
        path = Path(name)
        if not name or path.is_absolute() or any(p in {"", ".", ".."} for p in name.split("/")):
            raise ValueError("Unsafe smoke source path: " + name)
        if path.parts[0] not in {".systems", ".github"} and name not in {"README.md", "HUMANS.md", ".gitignore"}:
            raise ValueError("Smoke source is outside the product inventory: " + name)
        source = root / path
        if not source.is_file() or source.is_symlink():
            raise ValueError("Unsafe or missing smoke source: " + name)
        parent = source.parent.resolve(strict=True)
        if not any(parent == allowed or parent.is_relative_to(allowed)
                   for allowed in (root / ".systems", root / ".github")) and parent != root:
            raise ValueError("Smoke source escapes product root: " + name)
        sources.append((source, destination / path))
    # Preflight the entire inventory before writes; every domain owns physical copies.
    created = {destination}
    for source, target in sources:
        if target.parent not in created:
            target.parent.mkdir(parents=True, exist_ok=True)
            created.add(target.parent)
        shutil.copy2(source, target, follow_symlinks=False)
    return names


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--destination")
    parser.add_argument("--run-all", action="store_true")
    parser.add_argument("--extra-product-file", action="append", default=[])
    args = parser.parse_args()
    try:
        if args.run_all:
            if args.destination:
                raise ValueError("All-suite orchestration does not accept a shared destination")
            script = Path(args.repo_root).resolve(strict=True) / ".systems/scripts/check-validator-smoke-tests"
            commands = []
            for suite in SUITES:
                command = [str(script), "--suite", suite]
                for extra in args.extra_product_file:
                    command.extend(["--extra-product-file", extra])
                commands.append(command)
            results = run_transactions(commands)
            for result in results:
                print(result.stdout, end="", flush=True)
            failed = next((result.returncode for result in results if result.returncode), 0)
            if failed:
                return failed if failed > 0 else 1
            print("SMOKE_COMPLETION suites=7 isolation=per-domain workers=2 supporting_only=true")
            return 0
        if not args.destination:
            raise ValueError("Fixture copy requires a destination")
        copy_fixture(args.repo_root, args.destination, args.extra_product_file)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
