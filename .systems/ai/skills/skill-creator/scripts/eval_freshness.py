"""One producer/consumer freshness contract for local skill evaluations."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def read(path):
    no_links(path)
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def no_links(path):
    path = Path(path).absolute()
    if any(p.is_symlink() for p in [path, *path.parents] if str(p) not in {"/tmp", "/var"}):
        raise ValueError("Linked eval input or run path is forbidden")
    return path


def identity(plan_path, plan, configs):
    files = {}
    names = list(plan.get("source_files", []))
    names += [name for item in plan["evals"] for name in item.get("files", [])]
    target = plan.get("target_path")
    if target:
        target = Path(target)
        if not target.is_absolute():
            target = plan_path.parent / target
        no_links(target)
        if not target.exists():
            raise ValueError("Missing eval target source")
        names += [str(p) for p in target.rglob("*") if p.is_file() and "__pycache__" not in p.parts] if target.is_dir() else [str(target)]
    for name in names:
        path = Path(name)
        if not path.is_absolute():
            path = plan_path.parent / path
        no_links(path)
        if not path.is_file():
            raise ValueError(f"Missing or linked eval input: {name}")
        files[str(path.resolve())] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {"plan_fingerprint": digest(plan), "input_fingerprints": files,
            "configurations": configs, "eval_ids": [str(item["id"]) for item in plan["evals"]]}


def validate_run(root):
    root = no_links(root)
    manifest = read(root / "run.json")
    if manifest.get("freshness_contract") != 1:
        raise ValueError("Legacy eval run has no freshness contract; create a fresh run")
    plan_path = Path(manifest["source_plan"])
    expected = identity(plan_path, read(plan_path), manifest["configurations"])
    if any(manifest.get(k) != v for k, v in expected.items()):
        raise ValueError("Stale eval plan or source fingerprint")
    if manifest.get("run_fingerprint") != digest(expected):
        raise ValueError("Invalid eval run fingerprint")
    for eval_id in manifest["eval_ids"]:
        metadata = read(root / eval_id / "eval_metadata.json")
        if metadata.get("run_fingerprint") != manifest["run_fingerprint"]:
            raise ValueError("Stale eval metadata fingerprint")
        if digest({k: v for k, v in metadata.items() if k != "metadata_fingerprint"}) != metadata.get("metadata_fingerprint"):
            raise ValueError("Tampered eval metadata")
        item = next(i for i in read(plan_path)["evals"] if str(i["id"]) == eval_id)
        assertions = item.get("assertions") or [{"text": text, "type": "required", "method": "manual-review"} for text in item["expected_behavior"]]
        expected_metadata = {"run_fingerprint": manifest["run_fingerprint"], "eval_id": eval_id,
            "eval_name": item.get("name", eval_id), "prompt": item["prompt"], "files": item.get("files", []),
            "expected_output": item.get("expected_output", ""), "assertions": assertions,
            "forbidden_behavior": item.get("forbidden_behavior", []), "configurations": manifest["configurations"]}
        if {k: v for k, v in metadata.items() if k != "metadata_fingerprint"} != expected_metadata:
            raise ValueError("Eval metadata does not match the current plan")
    result = []
    for path in sorted(root.rglob("grading.json")):
        no_links(path)
        rel = path.relative_to(root)
        if path.is_symlink() or len(rel.parts) != 3 or rel.parts[0] not in manifest["eval_ids"] or rel.parts[1] not in manifest["configurations"]:
            raise ValueError("Orphan or unknown grading path")
        data = read(path)
        metadata = read(root / rel.parts[0] / "eval_metadata.json")
        if data.get("eval_id") != rel.parts[0] or data.get("configuration") != rel.parts[1]:
            raise ValueError("Grade identity does not match run membership")
        if data.get("run_fingerprint") != manifest["run_fingerprint"] or data.get("metadata_fingerprint") != metadata["metadata_fingerprint"]:
            raise ValueError("Stale grade fingerprint")
        results = {}
        config_root = path.parent
        for result_path in sorted(config_root.rglob("*")):
            if not result_path.is_file() or result_path.name in {"grading.json", "grading.todo.md", "transcript.todo.md", "README.md"}:
                continue
            no_links(result_path)
            results[str(result_path.relative_to(config_root))] = hashlib.sha256(result_path.read_bytes()).hexdigest()
        if not results or data.get("result_fingerprints") != results:
            raise ValueError("Stale or missing evaluated result fingerprints")
        result.append((path, data))
    return manifest, result
