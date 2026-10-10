"""Explicit local init, selected backups and hash-bound journaled restoration."""
from __future__ import annotations

from pathlib import Path
import hashlib
from work_evidence import (require, shape, version, digest, canonical_bytes, read_json,
                           safe_path, file_hash, validate_config, validate_registry)
from work_evidence_ledger import Ledger, atomic_write
from local_paths import LocalPathError, resolve_path


def init_preview(workspace, request):
    try:
        workspace = resolve_path(workspace, base=Path.cwd(), allow_relative=True)
    except LocalPathError:
        require(False, "invalid-workspace", "init")
    require(workspace.is_dir() and not workspace.is_symlink(), "invalid-workspace", "init")
    shape(request, {"schema_version", "config", "entities"})
    version(request)
    validate_config(request["config"], workspace.resolve())
    validate_registry(request["entities"])
    require(request["config"]["workspace_id"] == workspace.name, "workspace-identity-conflict", "init")
    home = safe_path(workspace, "work-evidence", must_exist=False)
    require(not home.exists(), "already-initialized", "init")
    files = {"work-evidence/config.json": canonical_bytes(request["config"]).decode("utf-8"),
             "work-evidence/entities.json": canonical_bytes(request["entities"]).decode("utf-8")}
    return {"schema_version": 1, "workspace": str(workspace.resolve()), "files": files,
            "request_hash": digest(request), "state": "init-preview"}


def initialize(workspace, request, expected_hash, *, owner_approved=False):
    require(owner_approved, "owner-approval-required", "init")
    value = init_preview(workspace, request)
    require(digest(value) == expected_hash, "stale-approval", "init")
    home = safe_path(workspace, "work-evidence", must_exist=False)
    # Exclusive mkdir reserves the empty namespace; no existing state is overwritten.
    require(not home.exists(), "already-initialized", "init")
    home.mkdir()
    ledger_lock = home / "init.lock"
    with ledger_lock.open("xb"):
        for name, content in value["files"].items():
            atomic_write(safe_path(workspace, name, must_exist=False), content.encode(), immutable=True)
    ledger_lock.unlink()
    return {"state": "initialized", "workspace_id": request["config"]["workspace_id"]}


EXCLUDED = {"backups", "restore-journals", "writer.lock", "init.lock", "lock-recovery"}


def operational_path(ledger, relative):
    require(isinstance(relative, str), "invalid-path", "backup")
    parts = Path(relative).parts
    require(len(parts) >= 2 and parts[0] in {"work-evidence", "work-log"}
            and not any(p in EXCLUDED for p in parts), "unapproved-backup-path", "backup")
    path = safe_path(ledger.workspace, relative, must_exist=False)
    require(not path.exists() or path.is_file(), "invalid-backup-file", "backup")
    require(not path.exists() or path.stat().st_size <= 16 * 1024 * 1024,
            "backup-file-too-large", "backup")
    return path


def inventory(ledger):
    ledger.check_loaded()
    result = {}
    for name in ("work-log", "work-evidence"):
        root = safe_path(ledger.workspace, name, must_exist=False)
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            relative = str(path.relative_to(ledger.workspace))
            parts = Path(relative).parts
            if any(p in EXCLUDED for p in parts):
                continue
            require(not path.is_symlink(), "unsafe-runtime-path", "inventory")
            if path.is_file():
                operational_path(ledger, relative)
                result[relative] = file_hash(path)
                require(len(result) <= 10000, "inventory-too-large", "inventory")
    return result


def backup_preview(ledger, paths):
    require(isinstance(paths, list) and paths and len(paths) <= 1000
            and len(set(paths)) == len(paths), "invalid-backup-paths", "backup")
    snapshot = inventory(ledger)
    if any(path.endswith(".xlsx") for path in paths):
        from work_evidence_xlsx import Tracker
        Tracker(ledger).closed()
    files = {}
    total_bytes = 0
    for relative in sorted(paths):
        path = operational_path(ledger, relative)
        require(path.is_file(), "missing-backup-file", "backup")
        total_bytes += path.stat().st_size
        require(total_bytes <= 64 * 1024 * 1024, "backup-too-large", "backup")
        files[relative] = file_hash(path)
    return {"schema_version": 1, "workspace_id": ledger.config["workspace_id"],
            "files": files, "inventory": snapshot, "state": "backup-preview"}


def write_backup(ledger, paths, expected_hash, *, owner_approved=False):
    require(owner_approved, "owner-approval-required", "backup")
    with ledger.lock():
        value = backup_preview(ledger, paths)
        require(digest(value) == expected_hash, "stale-approval", "backup")
        folder = "backups/" + expected_hash + "/"
        for relative, checksum in value["files"].items():
            path = operational_path(ledger, relative)
            data = path.read_bytes()
            require(file_hash(path) == checksum and hashlib.sha256(data).hexdigest() == checksum,
                    "source-changed", "backup")
            atomic_write(ledger.runtime(folder + "files/" + relative), data, immutable=True)
        require(inventory(ledger) == value["inventory"], "source-changed", "backup")
        atomic_write(ledger.runtime(folder + "manifest.json"), canonical_bytes(value), immutable=True)
        return {"state": "backed-up", "backup_id": expected_hash}


def load_backup(ledger, backup_id):
    from work_evidence import sha
    sha(backup_id, "backup_id")
    folder = "backups/" + backup_id + "/"
    value = read_json(ledger.runtime(folder + "manifest.json", exists=True))
    shape(value, {"schema_version", "workspace_id", "files", "inventory", "state"})
    require(digest(value) == backup_id and value["workspace_id"] == ledger.config["workspace_id"],
            "backup-binding-conflict", "backup")
    data = {}
    for relative, checksum in value["files"].items():
        operational_path(ledger, relative)
        path = ledger.runtime(folder + "files/" + relative)
        require(path.is_file() and path.stat().st_size <= 16 * 1024 * 1024,
                "corrupt-backup", "backup")
        require(file_hash(path) == checksum, "corrupt-backup", "backup")
        data[relative] = path.read_bytes()
    return value, data


def restore_preview(ledger, backup_id):
    value, _ = load_backup(ledger, backup_id)
    current = inventory(ledger)
    # Config/registry cannot be replaced under a different identity/policy.
    for relative in ("work-evidence/config.json", "work-evidence/entities.json"):
        require(current.get(relative) == value["inventory"].get(relative),
                "configuration-changed", "restore")
    canonical = lambda path: path.startswith(("work-log/", "work-evidence/commits/",
                                              "work-evidence/transactions/", "work-evidence/sessions/"))
    require(not any(canonical(path) and path not in value["inventory"] for path in current),
            "newer-canonical-records", "restore")
    return {"schema_version": 1, "workspace_id": value["workspace_id"], "backup_id": backup_id,
            "inventory": current, "targets": {p: current.get(p) for p in value["files"]},
            "state": "restore-preview"}


def restore(ledger, preview, expected_hash, *, owner_approved=False, failpoint=None):
    require(owner_approved, "owner-approval-required", "restore")
    require(digest(preview) == expected_hash, "stale-approval", "restore")
    shape(preview, {"schema_version", "workspace_id", "backup_id", "inventory", "targets", "state"})
    version(preview)
    require(preview["workspace_id"] == ledger.config["workspace_id"], "wrong-workspace", "restore")
    with ledger.lock():
        value, files = load_backup(ledger, preview["backup_id"])
        require(set(preview["targets"]) == set(files), "restore-target-conflict", "restore")
        folder = "restore-journals/" + expected_hash + "/"
        journal = ledger.runtime(folder + "journal.json")
        existing = journal.exists()
        if existing:
            saved = read_json(journal)
            require(saved["preview"] == preview, "restore-journal-conflict", "restore")
        else:
            require(restore_preview(ledger, preview["backup_id"]) == preview, "newer-user-edits", "restore")
            saved = {"preview": preview, "restored": [], "pending": None, "state": "prepared"}
        current = inventory(ledger)
        expected = dict(preview["inventory"])
        for relative in saved["restored"]:
            expected[relative] = value["files"][relative]
        pending = saved.get("pending")
        if pending is not None:
            require(pending in files, "restore-journal-conflict", "restore")
            if current.get(pending) == value["files"][pending]:
                expected[pending] = value["files"][pending]
        require(current == expected, "newer-user-edits", "restore")
        if not existing:
            for relative, old_hash in preview["targets"].items():
                if old_hash is not None:
                    atomic_write(ledger.runtime(folder + "previous/" + relative),
                                 operational_path(ledger, relative).read_bytes(), immutable=True)
            atomic_write(journal, canonical_bytes(saved), immutable=True)
        for index, (relative, data) in enumerate(files.items()):
            if relative in saved["restored"]:
                continue
            path = operational_path(ledger, relative)
            if relative.endswith(".xlsx"):
                from work_evidence_xlsx import Tracker
                Tracker(ledger).closed()
            current_hash = file_hash(path) if path.is_file() else None
            allowed = {preview["targets"][relative]}
            if saved.get("pending") == relative:
                allowed.add(value["files"][relative])
            require(current_hash in allowed, "newer-user-edits", "restore")
            saved["pending"] = relative
            atomic_write(journal, canonical_bytes(saved))
            atomic_write(path, data)
            if failpoint == "before-receipt-" + str(index):
                require(False, "injected-failure", "restore")
            saved["restored"].append(relative)
            saved["pending"] = None
            atomic_write(journal, canonical_bytes(saved))
            if failpoint == "after-file-" + str(index):
                require(False, "injected-failure", "restore")
        saved["state"] = "restored"
        expected = dict(preview["inventory"])
        expected.update(value["files"])
        require(inventory(ledger) == expected, "newer-user-edits", "restore")
        atomic_write(journal, canonical_bytes(saved))
        return {"state": "restored", "restore_id": expected_hash, "file_count": len(files),
                "previous_bytes_retained": True}
