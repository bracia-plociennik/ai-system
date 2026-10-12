"""Opt-in source equivalence. Verification is supporting evidence, never PASS."""

import json
from pathlib import Path
import re
import subprocess

from orchestration_compatibility import Blocked, require, inventory, identity, digest, fingerprint, contained


def current_qa(text):
    visible, fence = [], None
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            token = marker[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None:
            visible.append(line)
    text = "\n".join(visible) + "\n"
    require(text.splitlines().count("## Current QA Run") == 1, "missing/duplicate current QA run")
    return text.split("## Current QA Run\n", 1)[1].split("\n## ", 1)[0]


def quality_gate(text):
    text = current_qa(text)
    for heading in ("### Definition Of Done Validation", "### Intent / Plan / Spec Compliance", "### Review Completeness Gate", "### Quality Gate"):
        require(text.splitlines().count(heading) == 1, "formal implementation QA completeness missing/duplicate")
    gate = text.split("### Quality Gate\n", 1)[1].split("\n##", 1)[0]
    for field in ("100% DoD satisfied: yes", "No known bug in scope: yes", "Quality result: PASS"):
        require(gate.splitlines().count("- " + field) == 1, "formal implementation quality gate incomplete")
    review = text.split("### Review Completeness Gate\n", 1)[1].split("\n###", 1)[0]
    for field in ("Status: complete", "Closure freshness: current", "Required-field mapping: complete"):
        require(review.splitlines().count("- " + field) == 1, "review evidence incomplete")


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def index(repo):
    entries = {}
    for line in git(repo, "ls-files", "--stage", "-z").split("\0"):
        if not line:
            continue
        fields, name = line.split("\t", 1)
        mode, oid, stage = fields.split()
        require(stage == "0" and mode in {"100644", "100755"}, "unmerged or unsupported index entry")
        entries[name] = {"mode": mode, "oid": oid}
    return entries


def snapshot(repo, project, task, dependencies=()):
    repo = Path(repo).absolute()
    require(all(isinstance(v, str) and v for v in (project, task)), "missing snapshot scope")
    data = {"schema": 1, "role": "implementation-quality", "project": project, "task": task,
            "repository": str(repo), "repository_identity": identity(repo),
            "common_identity": identity(Path(git(repo, "rev-parse", "--git-common-dir")) if Path(git(repo, "rev-parse", "--git-common-dir")).is_absolute()
                                        else repo / git(repo, "rev-parse", "--git-common-dir")),
            "head": git(repo, "rev-parse", "HEAD"), "tree": git(repo, "rev-parse", "HEAD^{tree}"),
            "index": index(repo), "population": inventory(repo, git_root=True), "dependencies": []}
    for dep in dependencies:
        root = Path(dep).absolute()
        data["dependencies"].append({"root": str(root), "population": inventory(root)})
    return {"body": data, "sha256": digest(data)}


def verify_snapshot(value, repo):
    if isinstance(value, dict) and isinstance(value.get("body"), dict) and value["body"].get("binding") == "runtime-scope-v1":
        from runtime_source_binding import verify_runtime_snapshot
        return verify_runtime_snapshot(value, repo)
    require(isinstance(value, dict) and value.get("sha256") == digest(value.get("body")), "snapshot fingerprint mismatch")
    body = value["body"]
    require(body.get("schema") == 1 and body.get("role") == "implementation-quality", "unsupported QA snapshot role")
    repo = Path(repo).absolute()
    require(body["repository"] == str(repo) and body["repository_identity"] == identity(repo), "repository identity changed")
    common = Path(git(repo, "rev-parse", "--git-common-dir"))
    if not common.is_absolute():
        common = repo / common
    require(identity(common) == body["common_identity"], "common Git identity changed")
    require(inventory(repo, git_root=True) == body["population"], "complete live population drift")
    for dep in body["dependencies"]:
        require(inventory(dep["root"]) == dep["population"], "dependency drift")
    head = git(repo, "rev-parse", "HEAD")
    current_index = index(repo)
    if head == body["head"]:
        require(git(repo, "rev-parse", "HEAD^{tree}") == body["tree"] and current_index == body["index"], "baseline tree/index drift")
        return {"equivalent": True, "binding": "same-head", "supporting_only": True}
    raw = git(repo, "cat-file", "-p", head)
    parents = re.findall(r"^parent ([0-9a-f]{40})$", raw, re.M)
    require(parents == [body["head"]], "not the first source-only child commit")
    entries = body["population"]["entries"]
    files = {p: v for p, v in entries.items() if v["kind"] == "file"}
    require(not any(p.startswith(("ai-workflow-workspace/", "capture-state/", "project-state/")) for p in files), "tracked runtime commit chains unsupported")
    tree = {}
    for row in git(repo, "ls-tree", "-r", "-z", head).split("\0"):
        if not row:
            continue
        fields, name = row.split("\t", 1)
        mode, kind, oid = fields.split()
        require(kind == "blob" and mode in {"100644", "100755"}, "unsupported committed entry")
        tree[name] = {"mode": mode, "oid": oid}
    require(set(tree) == set(files) and tree == current_index, "partial staging or population/index mismatch")
    for name, entry in files.items():
        expected_mode = "100755" if entry["mode"] & 0o111 else "100644"
        blob = subprocess.check_output(["git", "-C", str(repo), "cat-file", "blob", tree[name]["oid"]])
        import hashlib
        require(tree[name]["mode"] == expected_mode and hashlib.sha256(blob).hexdigest() == entry["sha256"], "committed mode/content mismatch")
    return {"equivalent": True, "binding": "first-source-only-commit", "supporting_only": True}


def verify_qa_binding(value, repo, qa_path, project, task):
    body = value["body"]
    require(body["project"] == project and body["task"] == task, "QA scope mismatch")
    text = Path(qa_path).read_text()
    quality_gate(text)
    require(text.splitlines().count("- QA verification contract: full-qa-verification-v3") == 1, "unsupported QA binding contract")
    text = current_qa(text)
    required = ["Artifact kind: implementation-quality",
                "Project/task identity: " + project + ":" + task, "Source snapshot SHA-256: " + value["sha256"],
                "Verdict: PASS", "Gate Decision: PASS"]
    require(all(text.splitlines().count("- " + item) == 1 for item in required), "missing or duplicate immutable QA binding")
    return verify_snapshot(value, repo)


def phase_commit(phase, approved_git_scope, no_commit, tracked_changes, final_owner_yes=False, impact="pending", index_owned=False):
    require(phase in {"planning-range", "phase-6", "phase-7", "phase-8"}, "unknown phase boundary")
    require(all(type(v) is bool for v in (approved_git_scope, no_commit, tracked_changes, final_owner_yes, index_owned)), "invalid Git decision type")
    if no_commit:
        return "forbidden-by-owner"
    if not tracked_changes:
        return "not-required"
    require(impact in {"yes", "no", "pending"}, "invalid impact disposition")
    if not approved_git_scope or not index_owned or impact == "pending":
        return "blocked"
    if phase == "phase-8" and not final_owner_yes:
        return "awaiting-owner-final-yes"
    return "eligible-for-scoped-commit-not-executed"
