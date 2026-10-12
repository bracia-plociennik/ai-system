"""Opt-in namespace-complete runtime equality; HEAD is immutable provenance."""
from pathlib import Path
import stat
from orchestration_compatibility import require, contained, identity, digest, fingerprint, relative


def namespace(root, exclusions):
    require(isinstance(exclusions, list), "invalid runtime exclusions")
    excluded = {}
    for item in exclusions:
        require(isinstance(item, dict) and set(item) == {"path", "kind", "reason"}, "invalid exclusion fields")
        name = relative(item["path"])
        require(item["kind"] in {"file", "directory"} and isinstance(item["reason"], str) and item["reason"].strip(), "unreviewed exclusion")
        require(name not in excluded and not any(name.startswith(x + "/") or x.startswith(name + "/") for x in excluded), "overlapping exclusions")
        excluded[name] = item
    root = Path(root).absolute()
    require(root.is_dir() and root.resolve() == root, "unsafe runtime root")
    entries, size = {}, 0

    def walk(directory):
        nonlocal size
        for child in sorted(directory.iterdir()):
            name = relative(child.relative_to(root).as_posix())
            require(not child.is_symlink(), "linked runtime input")
            require(child.name != ".git", "nested Git runtime unsupported")
            if name in excluded:
                require((child.is_dir() if excluded[name]["kind"] == "directory" else child.is_file()), "exclusion kind changed")
                continue
            require(child.name not in {".env", "credentials", "id_rsa", "id_ed25519"} and not child.name.startswith(".env."), "sensitive runtime input")
            require(len(entries) < 100000, "runtime inventory too large")
            mode = stat.S_IMODE(child.stat().st_mode)
            if child.is_dir():
                entries[name] = {"kind": "directory", "mode": mode}
                walk(child)
            else:
                require(child.is_file(), "special runtime input")
                size += child.stat().st_size
                require(size <= 64 * 1024 * 1024, "runtime inventory exceeds 64MB")
                entries[name] = {"kind": "file", "mode": mode, "sha256": fingerprint(child)}
    walk(root)
    require(any(v["kind"] == "file" for v in entries.values()), "empty runtime source population")
    return {"root_identity": identity(root), "root_mode": stat.S_IMODE(root.stat().st_mode), "entries": entries}


def external_file(name):
    path = Path(name)
    require(path.is_absolute() and path == path.absolute() and path.resolve() == path, "unsafe external dependency")
    require(not any(x.is_symlink() for x in (path, *path.parents)), "linked external dependency")
    return {"path": str(path), "mode": stat.S_IMODE(path.stat().st_mode), "sha256": fingerprint(path)}


def runtime_snapshot(repo, project, task, runtime_root, exclusions=(), dependencies=()):
    from qa_source_binding import git
    repo = Path(repo).absolute()
    require(all(isinstance(v, str) and v for v in (project, task)), "missing runtime scope")
    root = contained(repo, runtime_root)
    require(git(repo, "rev-parse", "--show-toplevel") == str(repo), "runtime source must be Git root")
    common = Path(git(repo, "rev-parse", "--git-common-dir"))
    if not common.is_absolute():
        common = repo / common
    deps = [external_file(name) for name in dependencies]
    require(len({d["path"] for d in deps}) == len(deps), "duplicate runtime dependency")
    require(all(not Path(d["path"]).is_relative_to(root) for d in deps), "dependency aliases runtime namespace")
    body = {"schema": 2, "role": "implementation-quality", "binding": "runtime-scope-v1",
            "project": project, "task": task, "repository": str(repo),
            "repository_identity": identity(repo), "common_identity": identity(common),
            "head": git(repo, "rev-parse", "HEAD"), "runtime_root": runtime_root,
            "exclusions": list(exclusions), "population": namespace(root, list(exclusions)),
            "dependencies": deps}
    return {"body": body, "sha256": digest(body)}


def verify_runtime_snapshot(value, repo):
    from qa_source_binding import git
    require(isinstance(value, dict) and value.get("sha256") == digest(value.get("body")), "runtime snapshot fingerprint mismatch")
    body = value["body"]
    require(set(body) == {"schema", "role", "binding", "project", "task", "repository", "repository_identity", "common_identity", "head", "runtime_root", "exclusions", "population", "dependencies"}, "invalid runtime snapshot fields")
    require(body["schema"] == 2 and body["role"] == "implementation-quality" and body["binding"] == "runtime-scope-v1", "unsupported runtime snapshot")
    require(isinstance(body["dependencies"], list) and all(isinstance(d, dict) and set(d) == {"path", "mode", "sha256"} for d in body["dependencies"]), "invalid runtime dependencies")
    require(len({d["path"] for d in body["dependencies"]}) == len(body["dependencies"]), "duplicate runtime dependency")
    repo = Path(repo).absolute()
    require(body["repository"] == str(repo) and body["repository_identity"] == identity(repo), "runtime repository identity changed")
    require(git(repo, "rev-parse", "--show-toplevel") == str(repo), "runtime source must be Git root")
    common = Path(git(repo, "rev-parse", "--git-common-dir"))
    if not common.is_absolute():
        common = repo / common
    require(identity(common) == body["common_identity"], "runtime common Git identity changed")
    require(isinstance(body["head"], str) and __import__("re").fullmatch(r"[0-9a-f]{40,64}", body["head"]), "invalid runtime assessed HEAD")
    require(git(repo, "cat-file", "-t", body["head"]) == "commit", "runtime provenance commit missing")
    root = contained(repo, body["runtime_root"])
    require(namespace(root, body["exclusions"]) == body["population"], "runtime source population drift")
    for dep in body["dependencies"]:
        require(not Path(dep["path"]).is_relative_to(root), "dependency aliases runtime namespace")
        require(external_file(dep["path"]) == dep, "runtime dependency drift")
    return {"equivalent": True, "binding": "runtime-scope-v1", "assessed_head": body["head"],
            "current_head": git(repo, "rev-parse", "HEAD"), "supporting_only": True}
