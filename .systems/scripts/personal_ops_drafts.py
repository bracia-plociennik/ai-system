"""Private, noncanonical SPOR drafts. No index, task, calendar or network writes.

The caller must verify actual owner authority. Payloads, receipts and flags are
data, never consent. Scheduled callers have create-only authority for one date.
"""
from __future__ import annotations

import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import stat
from datetime import date, datetime
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
ZONE = ZoneInfo("Europe/Warsaw")
CONTRACT = "spor-check-in-draft-v1"
MAX_BYTES = 256_000
LABELS = ("Potwierdzone", "Zaplanowane", "Propozycja AI", "Nieznane — pytanie", "Nieznane - pytanie")
HEADER = re.compile(r'\A---\ntype: spor-check-in-draft-v1\ndraft: (\{[^\n]+\})\n---\n\n')
FIELD = re.compile(r'<!-- spor-field:(f\d{3}) -->\n(.*?)\n<!-- /spor-field -->', re.S)


def stamp():
    return datetime.now(ZONE)


def identity(workspace, target):
    from personal_ops_spor_proposals import periods
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", workspace.name):
        raise ValueError("Invalid workspace identity")
    window = periods(target)
    if window["mode"] == "none":
        raise ValueError("Sunday has no draft")
    return {"proposal_id": f"spor-proposal:{workspace.name}:{target}:{window['mode']}",
            "date": str(target), "mode": window["mode"], "periods": window}


def relative_path(info):
    return f"personal-ops/check-in-drafts/{info['mode']}/{info['date'][:4]}/{info['date']}.md"


def template(mode):
    if mode not in {"daily", "weekly"}:
        raise ValueError("Invalid mode")
    return (ROOT / f".systems/ai/templates/workspace/personal-ops/{mode}-spor-proposal.template.md").read_text()


def form(mode):
    fields = {}
    section = ""
    for line in template(mode).splitlines():
        if line.startswith("## "):
            section = line[3:]
        if line.startswith("- ") and not line.startswith("- Propozycja jest read-only"):
            key = f"f{len(fields) + 1:03}"
            fields[key] = {"section": section, "label": line[2:]}
    return fields


def validate_fields(mode, fields, *, initial):
    from personal_ops_spor_proposals import SECRET
    expected = form(mode)
    if not isinstance(fields, dict) or (initial and set(fields) != set(expected)) or not set(fields) <= set(expected) or not fields:
        raise ValueError("Missing, unknown or empty form fields")
    for key, value in fields.items():
        if not isinstance(value, str) or not value.strip() or len(value.encode()) > 32_000:
            raise ValueError("Invalid field value")
        if not any(value.startswith(label + ":") for label in LABELS):
            raise ValueError("Every field requires a source/confidence label")
        if "<!--" in value or re.search(r"(?m)^(?:#{1,6} |---\s*$)", value):
            raise ValueError("Field cannot replace form structure")
        if SECRET.search(value):
            raise ValueError("Secret-like field requires private review")
        owner_field = expected[key]["label"].startswith("Odpowiedź:") or (
            expected[key]["section"] in {"STATE (dziś)", "STATE (przyszły tydzień)"}
            and expected[key]["label"].startswith(("Mental", "Ciało")))
        if initial and owner_field and (not value.startswith(("Nieznane — pytanie:", "Nieznane - pytanie:")) or "UNKNOWN" not in value):
            raise ValueError("Current owner assessment must remain UNKNOWN in an automatic draft")


def render(info, fields):
    lines = template(info["mode"]).splitlines()
    out, index = [], 0
    for line in lines:
        if line.startswith("# "):
            out.append(f"# {info['mode'].upper()} CHECK-IN (SPOR) — szkic do uzupełnienia")
        elif line.startswith("Proposal ID:"):
            out.append(f"Proposal ID: {info['proposal_id']}. Szkic niezatwierdzony; nie jest źródłem faktów ani zatwierdzonym planem.")
            out.append(f"Czas przygotowania Europe/Warsaw: {info['prepared_at']}")
        elif line.startswith("- Propozycja jest read-only"):
            out.append("- Szkic nie zasila indeksów, TaskNotes ani kalendarza. Zapis canonical wymaga aktualnego zatwierdzenia właściciela.")
        elif line.startswith("- "):
            index += 1
            key = f"f{index:03}"
            out.extend([line, f"<!-- spor-field:{key} -->", fields[key], "<!-- /spor-field -->"])
        else:
            out.append(line)
    return "\n".join(out) + "\n"


def encode(meta, body):
    data = ("---\ntype: " + CONTRACT + "\ndraft: " + json.dumps(meta, ensure_ascii=False, separators=(",", ":")) + "\n---\n\n" + body).encode()
    if len(data) > MAX_BYTES:
        raise ValueError("Draft too large")
    return data


def decode(data):
    text = data.decode("utf-8")
    match = HEADER.match(text)
    if not match:
        raise ValueError("Invalid draft header")
    meta = json.loads(match[1])
    if meta.get("schema_version") != 1 or meta.get("status") not in {"draft", "approved"}:
        raise ValueError("Invalid draft lifecycle")
    return meta, text[match.end():]


def digest(data):
    return hashlib.sha256(data).hexdigest()


@contextlib.contextmanager
def directory(workspace, info, *, create=False):
    """Use no-follow dirfds throughout; never follow a model-selected path."""
    workspace = Path(workspace).absolute()
    if workspace.is_symlink():
        raise ValueError("Linked workspace rejected")
    fd = os.open(workspace, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in relative_path(info).split("/")[:-1]:
            if create:
                try:
                    os.mkdir(part, 0o700, dir_fd=fd)
                except FileExistsError:
                    pass
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        yield fd, info["date"] + ".md"
    finally:
        os.close(fd)


def read_at(fd, name):
    handle = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
    try:
        info = os.fstat(handle)
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_BYTES:
            raise ValueError("Unsafe draft file")
        if info.st_nlink != 1:
            # A crash after atomic link publication can retain the writer's
            # temporary link. Read it without cleanup; every link must be a
            # private temp peer in this same directory. Foreign hard links fail.
            peers = 1
            for entry in os.listdir(fd):
                if re.fullmatch(r"\.draft-[0-9a-f]{32}", entry):
                    peer = os.stat(entry, dir_fd=fd, follow_symlinks=False)
                    if (peer.st_dev, peer.st_ino) == (info.st_dev, info.st_ino):
                        peers += 1
            if peers != info.st_nlink:
                raise ValueError("Foreign draft hard link rejected")
        with os.fdopen(handle, "rb", closefd=False) as stream:
            data = stream.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError("Draft too large")
        return data
    finally:
        os.close(handle)


def read(workspace, target):
    info = identity(Path(workspace), target)
    with directory(workspace, info) as (fd, name):
        data = read_at(fd, name)
    meta, body = decode(data)
    for key in ("proposal_id", "date", "mode", "periods"):
        if meta.get(key) != info[key]:
            raise ValueError("Draft identity mismatch")
    return {"path": relative_path(info), "sha256": digest(data), "metadata": meta, "body": body}


@contextlib.contextmanager
def locked(fd):
    handle = os.open(".writer.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600, dir_fd=fd)
    try:
        if not stat.S_ISREG(os.fstat(handle).st_mode) or os.fstat(handle).st_nlink != 1:
            raise ValueError("Unsafe writer lock")
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    finally:
        os.close(handle)


def atomic(fd, name, data, *, expected=None):
    tmp = ".draft-" + secrets.token_hex(16)
    handle = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
    try:
        with os.fdopen(handle, "wb", closefd=False) as stream:
            stream.write(data)
            stream.flush()
            os.fsync(handle)
        if expected is None:
            # Hard-link publication is an atomic create-if-absent, never replace.
            os.link(tmp, name, src_dir_fd=fd, dst_dir_fd=fd, follow_symlinks=False)
        else:
            if digest(read_at(fd, name)) != expected:
                raise ValueError("Draft changed; reread and reconcile owner edits")
            os.replace(tmp, name, src_dir_fd=fd, dst_dir_fd=fd)
        os.fsync(fd)
    finally:
        os.close(handle)
        try:
            os.unlink(tmp, dir_fd=fd)
            os.fsync(fd)
        except FileNotFoundError:
            pass


def canonical_sources(workspace, target):
    """Canonical existence guard; no raw/body reads or generation refresh."""
    from personal_ops_spor_proposals import read_frontmatter, safe_path
    info = identity(Path(workspace), target)
    base = Path(workspace)
    if info["mode"] == "daily":
        candidates = [base / f"personal-ops/check-ins-v4/{target.year}/{target}.md"]
    else:
        years = {target.year, date.fromisoformat(info["periods"]["review_start"]).year}
        candidates = [path for year in sorted(years) for path in
                      (base / f"personal-ops/weekly-check-ins-v4/{year}").glob("*.md")]
    found = []
    for path in candidates:
        if not path.exists() and not path.is_symlink():
            continue
        path = safe_path(base, path)
        top, props = read_frontmatter(path)
        if info["mode"] == "daily":
            if top.get("type") != "daily-check-in-v4" or str(props.get("session_date")) != str(target):
                raise ValueError("Conflicting canonical identity")
            found.append(str(path.relative_to(base)))
        elif (str(props.get("recording_date")) == str(target)
              or (str(props.get("review_week_start")) == info["periods"]["review_start"]
                  and str(props.get("plan_week_start")) == info["periods"]["plan_start"]
                  and str(props.get("plan_week_end")) == info["periods"]["plan_end"])):
            if top.get("type") != "weekly-check-in-v4":
                raise ValueError("Conflicting weekly canonical identity")
            found.append(str(path.relative_to(base)))
    return found


def create(workspace, target, payload, *, clock=stamp):
    """Scheduled create only. Actual standing approval is checked by caller."""
    workspace = Path(workspace).absolute()
    current = clock()
    if current.date() != target:
        raise ValueError("No catch-up or date rollover writes")
    info = identity(workspace, target)
    if set(payload) != {"contract", "proposal_id", "fields", "sources"} or payload["contract"] != CONTRACT or payload["proposal_id"] != info["proposal_id"]:
        raise ValueError("Invalid draft package identity")
    validate_fields(info["mode"], payload["fields"], initial=True)
    if not isinstance(payload["sources"], list) or not payload["sources"] or len(payload["sources"]) > 150:
        raise ValueError("Draft requires source references")
    for source in payload["sources"]:
        if not isinstance(source, str) or not source.strip() or len(source) > 1500 or "\n" in source:
            raise ValueError("Invalid source reference")
    # Reuse the real read-only collector to reject source-error/already-recorded.
    from personal_ops_spor_proposals import prepare
    package = prepare(workspace, target, scheduled=True)
    if package["status"] != "ready":
        raise ValueError("Draft sources not ready: " + package["status"])
    meta = {"schema_version": 1, **info, "status": "draft", "created_at": current.isoformat(),
            "updated_at": current.isoformat(), "revision": 1, "sources": payload["sources"],
            "template_sha256": digest(template(info["mode"]).encode()),
            "authority": "unapproved-draft", "canonical_source": None}
    data = encode(meta, render({**info, "prepared_at": current.isoformat()}, payload["fields"]))
    with directory(workspace, info, create=True) as (fd, name), locked(fd):
        if clock().date() != target or canonical_sources(workspace, target):
            raise ValueError("Date changed or canonical already exists")
        atomic(fd, name, data)
    result = read(workspace, target)
    if result["sha256"] != digest(data):
        raise ValueError("Draft readback mismatch")
    return result


def update(workspace, target, updates, expected, owner_reference, *, clock=stamp):
    """Patch only selected fields; caller verifies current chat-owner provenance."""
    if not owner_reference or not re.fullmatch(r"[a-f0-9]{64}", expected):
        raise ValueError("Owner reply reference and read hash required")
    info = identity(Path(workspace), target)
    validate_fields(info["mode"], updates, initial=False)
    with directory(workspace, info) as (fd, name), locked(fd):
        data = read_at(fd, name)
        if digest(data) != expected:
            raise ValueError("Draft changed; reread owner edits")
        meta, body = decode(data)
        if meta.get("proposal_id") != info["proposal_id"] or meta["status"] != "draft" or canonical_sources(workspace, target):
            raise ValueError("Draft identity/lifecycle conflict")
        if meta.get("template_sha256") != digest(template(info["mode"]).encode()):
            raise ValueError("Template changed; explicit reconciliation required")
        matches = list(FIELD.finditer(body))
        if len({m[1] for m in matches}) != len(matches) or not set(updates) <= {m[1] for m in matches}:
            raise ValueError("Edited field structure requires manual reconciliation")
        body = FIELD.sub(lambda m: f"<!-- spor-field:{m[1]} -->\n{updates.get(m[1], m[2])}\n<!-- /spor-field -->", body)
        meta.update(updated_at=clock().isoformat(), revision=meta["revision"] + 1, owner_reply_reference=owner_reference)
        atomic(fd, name, encode(meta, body), expected=expected)
    return read(workspace, target)


def mark_approved(workspace, target, expected, canonical, source_hash, owner_reference):
    """Receipt only AFTER approved native canonical capture/QA; never creates it."""
    from personal_ops_v4 import load_daily, load_weekly, weekly_path
    from personal_ops_spor_proposals import safe_path, read_frontmatter
    info = identity(Path(workspace), target)
    if not owner_reference or canonical not in canonical_sources(workspace, target):
        raise ValueError("Current approval and matching saved canonical required")
    path = safe_path(Path(workspace), Path(workspace) / canonical)
    top, props = read_frontmatter(path)
    if digest(path.read_bytes()) != source_hash:
        raise ValueError("Canonical changed")
    if info["mode"] == "daily":
        load_daily(Path(workspace), target)
    else:
        if (str(props.get("report_id")) != path.stem
                or weekly_path(Path(workspace), date.fromisoformat(props["review_week_start"])).resolve() != path):
            raise ValueError("Weekly canonical path/identity mismatch")
        load_weekly(Path(workspace), str(props["report_id"]))
    with directory(workspace, info) as (fd, name), locked(fd):
        data = read_at(fd, name)
        if digest(data) != expected:
            raise ValueError("Draft changed")
        meta, body = decode(data)
        if meta.get("proposal_id") != info["proposal_id"] or meta["status"] != "draft":
            raise ValueError("Draft lifecycle conflict")
        if digest(path.read_bytes()) != source_hash:
            raise ValueError("Canonical changed during validation")
        meta.update(status="approved", canonical_source=canonical, canonical_sha256=source_hash,
                    owner_approval_reference=owner_reference, updated_at=stamp().isoformat(), revision=meta["revision"] + 1)
        atomic(fd, name, encode(meta, body), expected=expected)
    return read(workspace, target)
