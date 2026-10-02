"""Append-only revisions with committed-batch visibility and recoverable projections."""
from __future__ import annotations

import os
import uuid
from contextlib import contextmanager
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from work_evidence import (
    ACTUAL_BASES, EvidenceError, actual_seconds, canonical_bytes, digest,
    file_hash, identifier, instant, iso_date, read_json, require, safe_path,
    sha, shape, uuid_id, validate_config, validate_entry, validate_registry,
    validate_session,
)


def atomic_write(path, data, *, immutable=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    require(not path.is_symlink(), "unsafe-runtime-path", "output")
    if immutable and path.exists():
        require(path.read_bytes() == data, "immutable-conflict", "output")
        return
    temporary = path.with_name("." + path.name + "." + str(uuid.uuid4()) + ".tmp")
    try:
        with temporary.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        # Writers are serialized by the workspace lock. Never claim multi-file atomicity.
        os.replace(temporary, path)
        fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    finally:
        if temporary.exists():
            temporary.unlink()


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class Ledger:
    def __init__(self, workspace):
        candidate = Path(workspace)
        require(candidate.is_dir() and not candidate.is_symlink(), "invalid-workspace", "workspace")
        self.workspace = candidate.resolve()
        self.home = self.workspace / "work-evidence"
        self.config_path = safe_path(self.workspace, "work-evidence/config.json")
        self.registry_path = safe_path(self.workspace, "work-evidence/entities.json")
        self.loaded_config_hash = file_hash(self.config_path)
        self.loaded_registry_hash = file_hash(self.registry_path)
        self.config = validate_config(read_json(self.config_path), self.workspace)
        self.registry = read_json(self.registry_path)
        validate_registry(self.registry)
        self.check_loaded()
        require(self.config["workspace_id"] == self.workspace.name,
                "workspace-identity-conflict", "workspace")

    def check_loaded(self):
        require(file_hash(self.config_path) == self.loaded_config_hash
                and file_hash(self.registry_path) == self.loaded_registry_hash,
                "configuration-changed-after-load", "configuration")

    def runtime(self, relative, *, exists=False):
        return safe_path(self.workspace, "work-evidence/" + relative, must_exist=exists)

    @contextmanager
    def lock(self):
        path = self.runtime("writer.lock")
        try:
            handle = path.open("xb")
        except FileExistsError:
            raise EvidenceError("writer-locked", "workspace") from None
        token = canonical_bytes({"pid": os.getpid(), "created_at": now(), "token": str(uuid.uuid4())})
        try:
            with handle:
                handle.write(token)
                handle.flush()
                os.fsync(handle.fileno())
            yield
        finally:
            # An operator must not remove/replace a lock while its writer is active.
            require(path.exists() and path.read_bytes() == token, "lock-changed", "writer")
            path.unlink()

    def recover_lock(self, expected_hash):
        path = self.runtime("writer.lock", exists=True)
        require(file_hash(path) == expected_hash, "stale-lock-approval", "lock")
        value = read_json(path)
        require(type(value.get("pid")) is int and value["pid"] > 0, "invalid-lock", "pid")
        try:
            os.kill(value["pid"], 0)
        except ProcessLookupError:
            path.unlink()
            return {"status": "lock-recovered"}
        except PermissionError:
            raise EvidenceError("lock-owner-active-or-unknown", "pid") from None
        raise EvidenceError("lock-owner-active-or-unknown", "pid")

    def committed(self):
        entries, sessions, manifests = {}, {}, []
        directory = self.runtime("commits")
        if not directory.exists():
            return entries, sessions, manifests
        require(directory.is_dir(), "invalid-commit-root", "commits")
        for path in sorted(directory.glob("*.json")):
            manifest = read_json(self.runtime("commits/" + path.name, exists=True))
            shape(manifest, {"schema_version", "transaction_id", "manifest_hash",
                             "sequence", "records", "sessions"})
            require(manifest["schema_version"] == 1, "unsupported-version", "commit")
            uuid_id(manifest["transaction_id"], "transaction_id")
            sha(manifest["manifest_hash"], "manifest_hash")
            require(type(manifest["sequence"]) is int and manifest["sequence"] >= 1,
                    "invalid-sequence", "commit")
            manifests.append(manifest)
        manifests.sort(key=lambda x: x["sequence"])
        for sequence, manifest in enumerate(manifests, 1):
            require(manifest["sequence"] == sequence, "commit-sequence-conflict", "commit")
            prepared = read_json(self.runtime("transactions/" + manifest["transaction_id"] + "/manifest.json", exists=True))
            require(digest(prepared) == manifest["manifest_hash"],
                    "commit-approval-conflict", "manifest")
            require(prepared["snapshot"]["ledger_hash"] == digest(manifests[:sequence - 1]),
                    "commit-chain-conflict", "manifest")
            expected_records = []
            for row in prepared["rows"]:
                entry = row["entry"]
                expected_records.append({
                    "ledger_root": row["ledger_root"],
                    "relative_path": f"work-log/{entry['performed_on'][:4]}/{entry['entry_id']}/r{entry['revision']:04d}.json",
                    "sha256": digest(entry)})
            expected_sessions = [{"relative_path": "sessions/" + s["session_id"] + ".json",
                                  "sha256": digest(s)} for s in prepared["sessions"]]
            require(manifest["records"] == expected_records and manifest["sessions"] == expected_sessions,
                    "commit-record-conflict", "manifest")
            for locator in manifest["records"]:
                shape(locator, {"ledger_root", "relative_path", "sha256"})
                index = locator["ledger_root"]
                require(type(index) is int and 0 <= index < len(self.config["ledger_roots"]),
                        "invalid-root", "ledger_root")
                path = safe_path(self.config["ledger_roots"][index], locator["relative_path"])
                require(file_hash(path) == locator["sha256"], "corrupt-revision", "record")
                entry = validate_entry(read_json(path), self.config, self.registry,
                                       verify_sources=False)
                expected = f"work-log/{entry['performed_on'][:4]}/{entry['entry_id']}/r{entry['revision']:04d}.json"
                require(locator["relative_path"] == expected, "revision-locator-conflict", "record")
                previous = entries.get(entry["entry_id"])
                self.check_chain(entry, previous)
                entries[entry["entry_id"]] = entry
            for locator in manifest["sessions"]:
                shape(locator, {"relative_path", "sha256"})
                path = self.runtime(locator["relative_path"], exists=True)
                require(file_hash(path) == locator["sha256"], "corrupt-session", "session")
                session = validate_session(read_json(path), self.config, verify_sources=False)
                require(session["session_id"] not in sessions, "duplicate-session", "session")
                sessions[session["session_id"]] = session
        self.check_links(entries, sessions)
        return entries, sessions, manifests

    @staticmethod
    def check_chain(entry, previous):
        if previous is None:
            require(entry["revision"] == 1, "missing-revision", "entry")
        else:
            require(entry["revision"] == previous["revision"] + 1
                    and entry["previous_revision_hash"] == digest(previous),
                    "revision-conflict", "entry")
            for field in ("owner_workspace", "work_id", "entry_id", "performed_on"):
                require(entry[field] == previous[field], "immutable-identity-conflict", field)

    @staticmethod
    def check_links(entries, sessions):
        work_ids = set()
        for entry in entries.values():
            require(entry["work_id"] not in work_ids, "duplicate-work", "work_id")
            work_ids.add(entry["work_id"])
            sid = entry["duration"]["session_id"]
            if sid is not None:
                require(sid in sessions and entry["actor_kind"] == "human"
                        and entry["duration"]["basis"] in ACTUAL_BASES,
                        "session-link-conflict", "entry")
                allocation = {a["entry_id"]: a["seconds"] for a in sessions[sid]["allocations"]}
                require(entry["entry_id"] in allocation and
                        (entry["revision"] > 1 or allocation[entry["entry_id"]] == entry["duration"]["seconds"]),
                        "session-allocation-conflict", "entry")
        for session in sessions.values():
            for allocation in session["allocations"]:
                entry = entries.get(allocation["entry_id"])
                require(entry is not None,
                        "session-allocation-conflict", "session")
            allocated = sum(entry["duration"]["seconds"] for entry in entries.values()
                            if not entry.get("voided", False)
                            and entry["duration"]["session_id"] == session["session_id"])
            require(allocated <= session["duration"]["seconds"],
                    "session-overallocated", "session")

    def snapshot(self):
        self.check_loaded()
        _, _, manifests = self.committed()
        return {"config_hash": file_hash(self.config_path),
                "registry_hash": file_hash(self.registry_path),
                "ledger_hash": digest(manifests)}

    def materialize(self, candidate, *, persistent=False):
        shape(candidate, {"schema_version", "changes"}, {"sessions", "projection_source"})
        require(candidate["schema_version"] == 1, "unsupported-version", "candidate")
        require(isinstance(candidate["changes"], list) and bool(candidate["changes"]),
                "empty-batch", "changes")
        rows, seen_ids, anonymous = [], set(), set()
        for index, change in enumerate(candidate["changes"]):
            shape(change, {"entry"}, {"row_id", "ledger_root"})
            row_id = change.get("row_id")
            if row_id:
                identifier(row_id, "row_id")
                require(row_id not in seen_ids, "duplicate-row-id", "row_id")
            else:
                fingerprint = digest(change)
                require(fingerprint not in anonymous, "ambiguous-identical-rows", "row_id")
                anonymous.add(fingerprint)
                row_id = str(uuid.uuid4()) if persistent else f"preview-row-{index}"
            seen_ids.add(row_id)
            entry = dict(change["entry"])
            for field in ("entry_id", "work_id"):
                if not entry.get(field):
                    entry[field] = str(uuid.uuid4()) if persistent else str(uuid.uuid5(uuid.NAMESPACE_URL, row_id + field))
            validate_entry(entry, self.config, self.registry)
            root_index = change.get("ledger_root", 0)
            require(type(root_index) is int and 0 <= root_index < len(self.config["ledger_roots"]),
                    "invalid-root", "ledger_root")
            rows.append({"row_id": row_id, "ledger_root": root_index, "entry": entry})
        sessions = candidate.get("sessions", [])
        require(isinstance(sessions, list), "invalid-shape", "sessions")
        for session in sessions:
            validate_session(session, self.config)
        current, current_sessions, _ = self.committed()
        proposed, proposed_sessions = dict(current), dict(current_sessions)
        entry_ids = set()
        for row in rows:
            entry = row["entry"]
            require(entry["entry_id"] not in entry_ids, "duplicate-entry-change", "entry_id")
            entry_ids.add(entry["entry_id"])
            self.check_chain(entry, current.get(entry["entry_id"]))
            proposed[entry["entry_id"]] = entry
        for session in sessions:
            require(session["session_id"] not in proposed_sessions, "duplicate-session", "session_id")
            proposed_sessions[session["session_id"]] = session
        self.check_links(proposed, proposed_sessions)
        projection = candidate.get("projection_source")
        if projection:
            shape(projection, {"relative_path", "sha256"})
            path = safe_path(self.workspace, projection["relative_path"])
            require(file_hash(path) == projection["sha256"], "stale-workbook", "projection")
        return rows, sessions

    def preview(self, candidate):
        rows, sessions = self.materialize(candidate)
        return {"status": "preview", "persistent_ids_reserved": False,
                "rows": rows, "sessions": sessions, "snapshot": self.snapshot(),
                "warnings": overlap_warnings(list(self.committed()[1].values()) + sessions)}

    def prepare(self, candidate, *, candidate_source=None):
        with self.lock():
            self.check_loaded()
            transactions = self.runtime("transactions")
            if transactions.exists():
                for path in sorted(transactions.glob("*/manifest.json")):
                    existing = read_json(self.runtime(str(path.relative_to(self.home)), exists=True))
                    if existing.get("candidate_digest") == digest(candidate):
                        for source in existing["candidate_sources"]:
                            require(file_hash(source["path"]) == source["sha256"],
                                    "stale-candidate", "candidate")
                        return {"status": "prepared", "transaction_id": existing["transaction_id"],
                                "manifest_hash": digest(existing), "manifest": existing}
            rows, sessions = self.materialize(candidate, persistent=True)
            sources = []
            if candidate_source:
                path, expected = candidate_source
                require(file_hash(path) == expected, "stale-candidate", "candidate")
                sources.append({"path": str(Path(path).resolve()), "sha256": expected})
            manifest = {"schema_version": 1, "transaction_id": str(uuid.uuid4()),
                        "prepared_at": now(), "snapshot": self.snapshot(),
                        "rows": rows, "sessions": sessions, "candidate_sources": sources,
                        "projection_source": candidate.get("projection_source"),
                        "candidate_digest": digest(candidate)}
            directory = "transactions/" + manifest["transaction_id"] + "/"
            atomic_write(self.runtime(directory + "manifest.json"), canonical_bytes(manifest), immutable=True)
            self.progress(manifest["transaction_id"], "prepared")
            return {"status": "prepared", "transaction_id": manifest["transaction_id"],
                    "manifest_hash": digest(manifest), "manifest": manifest}

    def progress(self, transaction_id, state):
        atomic_write(self.runtime("transactions/" + transaction_id + "/state.json"),
                     canonical_bytes({"state": state, "updated_at": now()}))

    def apply(self, transaction_id, expected_hash, *, failpoint=None):
        uuid_id(transaction_id, "transaction_id")
        sha(expected_hash, "manifest_hash")
        with self.lock():
            manifest = read_json(self.runtime("transactions/" + transaction_id + "/manifest.json", exists=True))
            shape(manifest, {"schema_version", "transaction_id", "prepared_at", "snapshot",
                             "rows", "sessions", "candidate_sources", "projection_source", "candidate_digest"})
            require(manifest["schema_version"] == 1 and manifest["transaction_id"] == transaction_id,
                    "transaction-conflict", "transaction_id")
            require(digest(manifest) == expected_hash, "stale-approval", "manifest_hash")
            entries, sessions, commits = self.committed()
            committed = next((c for c in commits if c["transaction_id"] == transaction_id), None)
            require(not committed or committed["manifest_hash"] == expected_hash,
                    "transaction-conflict", "manifest_hash")
            # Config/registry changes cannot silently retarget an approved transaction.
            require(file_hash(self.config_path) == manifest["snapshot"]["config_hash"]
                    and file_hash(self.registry_path) == manifest["snapshot"]["registry_hash"],
                    "stale-configuration", "snapshot")
            if not committed:
                require(digest(commits) == manifest["snapshot"]["ledger_hash"],
                        "stale-ledger", "snapshot")
                for source in manifest["candidate_sources"]:
                    require(file_hash(source["path"]) == source["sha256"],
                            "stale-candidate", "candidate")
                # Validate the whole proposed state again, not only individual rows.
                candidate = {"schema_version": 1, "changes": manifest["rows"],
                             "sessions": manifest["sessions"]}
                if manifest["projection_source"]:
                    candidate["projection_source"] = manifest["projection_source"]
                self.materialize(candidate)
                projection = manifest["projection_source"]
                if projection:
                    path = safe_path(self.workspace, projection["relative_path"])
                    require(file_hash(path) == projection["sha256"], "stale-workbook", "projection")
                records, session_records = [], []
                for index, row in enumerate(manifest["rows"]):
                    entry = row["entry"]
                    relative = f"work-log/{entry['performed_on'][:4]}/{entry['entry_id']}/r{entry['revision']:04d}.json"
                    path = safe_path(self.config["ledger_roots"][row["ledger_root"]], relative, must_exist=False)
                    atomic_write(path, canonical_bytes(entry), immutable=True)
                    records.append({"ledger_root": row["ledger_root"], "relative_path": relative,
                                    "sha256": digest(entry)})
                    if failpoint == f"after-record-{index}":
                        raise EvidenceError("injected-failure", "record")
                for session in manifest["sessions"]:
                    relative = "sessions/" + session["session_id"] + ".json"
                    atomic_write(self.runtime(relative), canonical_bytes(session), immutable=True)
                    session_records.append({"relative_path": relative, "sha256": digest(session)})
                if failpoint == "before-manifest":
                    raise EvidenceError("injected-failure", "commit")
                committed = {"schema_version": 1, "transaction_id": transaction_id,
                             "manifest_hash": expected_hash, "sequence": len(commits) + 1,
                             "records": records, "sessions": session_records}
                atomic_write(self.runtime("commits/" + transaction_id + ".json"),
                             canonical_bytes(committed), immutable=True)
            if failpoint == "after-manifest":
                raise EvidenceError("injected-failure", "commit")
            self.progress(transaction_id, "canonical-committed")
            if failpoint == "before-projection":
                raise EvidenceError("injected-failure", "projection")
            result = self.rebuild_locked()
            self.progress(transaction_id, "projections-written")
            if failpoint == "after-projection":
                raise EvidenceError("injected-failure", "receipt")
            atomic_write(self.runtime("receipts/" + transaction_id + ".json"),
                         canonical_bytes({"transaction_id": transaction_id,
                                          "manifest_hash": expected_hash, "status": "completed"}),
                         immutable=True)
            self.progress(transaction_id, "completed")
            return {"status": "completed", "transaction_id": transaction_id, **result}

    def rebuild_locked(self):
        self.check_loaded()
        entries, sessions, commits = self.committed()
        selected = sorted(entries.values(), key=lambda e: (e["performed_on"], e["entry_id"]))
        output = b"".join(canonical_bytes(entry) for entry in selected)
        metadata = {"schema_version": 1, "ledger_hash": digest(commits),
                    "projection_hash": __import__("hashlib").sha256(output).hexdigest(),
                    "coverage": coverage(selected), "warnings": overlap_warnings(list(sessions.values()))}
        atomic_write(self.runtime("derived/work-index.jsonl"), output)
        atomic_write(self.runtime("derived/index-meta.json"), canonical_bytes(metadata))
        return metadata

    def rebuild(self):
        with self.lock():
            return self.rebuild_locked()

    def index_status(self):
        entries, _, commits = self.committed()
        meta = self.runtime("derived/index-meta.json")
        index = self.runtime("derived/work-index.jsonl")
        status = "missing"
        if meta.exists() and index.exists():
            metadata = read_json(meta)
            status = ("current" if metadata.get("ledger_hash") == digest(commits)
                      and metadata.get("projection_hash") == file_hash(index) else "stale")
        return {"status": status, "canonical_coverage": coverage(list(entries.values())),
                "scope": "committed local ledger only; no historical import implied"}


def source_candidate(ref, config, *, role, fact_date):
    """Selected TaskNote/checkpoint facts are review hints, never performed work."""
    from work_evidence import validate_source
    import re
    require(role in {"tasknote", "checkpoint"}, "invalid-source-role", "role")
    iso_date(fact_date, "fact_date")
    path = validate_source(ref, config)
    require(path.suffix.lower() == ".md", "unsupported-source-type", "source")
    body = path.read_text(encoding="utf-8")
    # Never export private trailing sections even from an explicitly selected file.
    body = re.split(r"(?im)^##\s+(?:Raw Check-In|Working Dump)\b", body, maxsplit=1)[0]
    osnr = {}
    for label in ("O", "S", "N", "R"):
        matches = re.findall(r"(?m)^-?[ \t]*" + label +
                             r"[ \t]*[-:\u2013\u2014][ \t]*(.{0,1000})$", body)
        if len(matches) == 1:
            value = matches[0]
            require(not re.search(r"(?i)(?:password|api[_ -]?key|bearer|secret)\s*[:=]", value),
                    "sensitive-source-field", "osnr")
            osnr[label] = value
    return {"source_ref": ref, "source_role": role, "fact_date": fact_date,
            "osnr_hints": osnr, "duration_seconds": None, "identity": "unresolved",
            "requires_owner_confirmation": True, "canonical_entry_created": False}


def overlap_warnings(sessions):
    intervals = sorted(
        [(instant(s["timing"]["start"], "start").astimezone(timezone.utc),
          instant(s["timing"]["end"], "end").astimezone(timezone.utc), s["session_id"])
         for s in sessions if s["timing"]["kind"] == "interval"])
    return [{"category": "human-session-overlap", "sessions": [a[2], b[2]]}
            for index, a in enumerate(intervals) for b in intervals[index + 1:]
            if b[0] < a[1] and a[0] < b[1]]


def coverage(entries):
    active = [e for e in entries if not e.get("voided", False)]
    confirmed = [actual_seconds(e) for e in active if actual_seconds(e) is not None]
    return {"active_entries": len(active), "actual_human_seconds": sum(confirmed),
            "confirmed_human_entries": len(confirmed),
            "unknown_entries": sum(e["duration"]["basis"] == "unknown" for e in active),
            "estimated_entries": sum(e["duration"]["basis"] == "estimated" for e in active),
            "estimated_seconds": sum(e["duration"]["seconds"] for e in active
                                     if e["duration"]["basis"] == "estimated"),
            "nonhuman_entries": sum(e["actor_kind"] != "human" for e in active),
            "coverage_complete": all(actual_seconds(e) is not None for e in active
                                     if e["actor_kind"] == "human")}


def period_entries(entries, start_date, end_date_exclusive, *, zone="Europe/Warsaw"):
    start_day = iso_date(start_date, "period_start")
    end_day = iso_date(end_date_exclusive, "period_end")
    require(start_day < end_day, "invalid-period", "period")
    tz = ZoneInfo(zone)
    start = datetime.combine(start_day, time(), tz).astimezone(timezone.utc)
    end = datetime.combine(end_day, time(), tz).astimezone(timezone.utc)
    exact, partial = [], []
    for entry in entries:
        if entry.get("voided", False):
            continue
        timing = entry["timing"]
        amount = actual_seconds(entry)
        if timing["kind"] == "date":
            if start_day <= date.fromisoformat(timing["date"]) < end_day:
                exact.append({"entry": entry, "actual_seconds": amount})
        elif timing["kind"] == "aggregate":
            a = date.fromisoformat(timing["start_date"])
            b = date.fromisoformat(timing["end_date_exclusive"])
            if a < end_day and start_day < b:
                destination = exact if start_day <= a and b <= end_day else partial
                destination.append({"entry": entry, "actual_seconds": amount if destination is exact else None})
        else:
            a = instant(timing["start"], "start").astimezone(timezone.utc)
            b = instant(timing["end"], "end").astimezone(timezone.utc)
            overlap = max(0, int((min(b, end) - max(a, start)).total_seconds()))
            if overlap or (a == b and start <= a < end):
                exact.append({"entry": entry, "actual_seconds": overlap if amount is not None else None})
    return {"exact": exact, "partly_overlapping_aggregates": partial}
