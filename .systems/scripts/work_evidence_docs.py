"""Version-bound documentation kits; no step execution or inferred replay success."""
from __future__ import annotations

import html
import re
from datetime import timezone

from work_evidence import (digest, canonical_bytes, require, shape, version, identifier,
                           uuid_id, text, instant, validate_source, file_hash)
from work_evidence_ledger import atomic_write


def texts(values, field, *, empty=False):
    require(isinstance(values, list) and len(values) <= 100 and (empty or values),
            "invalid-list", field)
    for value in values:
        text(value, field)
    return values


def approved_text(item, refs, purpose):
    shape(item, {"source_index", "text", "source_sha256", "text_sha256",
                 "purpose", "approved_by", "approved_at"})
    index = item["source_index"]
    require(type(index) is int and 0 <= index < len(refs), "invalid-reference", "source_index")
    text(item["text"], "derivative")
    require(item["source_sha256"] == refs[index]["sha256"]
            and item["text_sha256"] == digest(item["text"])
            and item["purpose"] == purpose and item["approved_by"] == "owner",
            "derivative-approval-required", "approval")
    instant(item["approved_at"], "approved_at")
    return item["text"]


def validate_procedure(procedure, ledger):
    fields = {"schema_version", "procedure_id", "version", "work_ids", "target_outcome",
              "skills", "environment", "prerequisites", "inputs", "steps", "tests",
              "stop_conditions", "rollback", "limits", "source_refs", "derivatives"}
    shape(procedure, fields)
    version(procedure)
    identifier(procedure["procedure_id"], "procedure_id")
    require(type(procedure["version"]) is int and 1 <= procedure["version"] <= 1000000,
            "invalid-version", "version")
    text(procedure["target_outcome"], "target_outcome")
    texts(procedure["skills"], "skills")
    texts(procedure["prerequisites"], "prerequisites")
    texts(procedure["stop_conditions"], "stop_conditions")
    texts(procedure["rollback"], "rollback")
    texts(procedure["limits"], "limits", empty=True)
    require(isinstance(procedure["environment"], dict) and procedure["environment"]
            and len(procedure["environment"]) <= 30, "invalid-environment", "environment")
    for key, value in procedure["environment"].items():
        identifier(key, "software")
        text(value, "software_version", 256)
    require(isinstance(procedure["source_refs"], list) and 1 <= len(procedure["source_refs"]) <= 50,
            "missing-source", "source_refs")
    for ref in procedure["source_refs"]:
        validate_source(ref, ledger.config)
    refs = procedure["source_refs"]
    require(len({digest(ref) for ref in refs}) == len(refs), "duplicate-source", "source_refs")
    require(isinstance(procedure["work_ids"], list) and len(procedure["work_ids"]) <= 100,
            "invalid-list", "work_ids")
    for value in procedure["work_ids"]:
        uuid_id(value, "work_id")
    require(len(set(procedure["work_ids"])) == len(procedure["work_ids"]),
            "duplicate-work-id", "work_ids")
    entries = ledger.committed()[0]
    selected = {key: digest(entry) for key, entry in entries.items()
                if entry["work_id"] in procedure["work_ids"] and not entry.get("voided", False)}
    require(set(procedure["work_ids"]) <= {entries[key]["work_id"] for key in selected},
            "unknown-work-id", "work_ids")
    for collection, fields in (("steps", {"id", "action", "expected"}),
                               ("tests", {"id", "assertion"})):
        rows = procedure[collection]
        require(isinstance(rows, list) and 1 <= len(rows) <= 100, "invalid-list", collection)
        ids = set()
        for row in rows:
            shape(row, fields)
            identifier(row["id"], "step_id")
            require(row["id"] not in ids, "duplicate-step-id", collection)
            ids.add(row["id"])
            for key in fields - {"id"}:
                text(row[key], key)
    for collection in ("inputs", "derivatives"):
        require(isinstance(procedure[collection], list) and 1 <= len(procedure[collection]) <= 50,
                "invalid-list", collection)
        for item in procedure[collection]:
            approved_text(item, refs, "documentation")
    return selected


def md(value):
    escaped = html.escape(str(value), quote=False)
    return re.sub(r"([\\`*_{}\[\]()#+.!|>-])", r"\\\1", escaped)


def assemble(ledger, procedure):
    """Read-only preview. Original source text is not copied into the kit."""
    selected = validate_procedure(procedure, ledger)
    source_state = {"config_hash": file_hash(ledger.config_path),
                    "registry_hash": file_hash(ledger.registry_path),
                    "entries": selected,
                    "sources": [ref["sha256"] for ref in procedure["source_refs"]]}
    lines = ["# Reproducible Procedure", "", "## Outcome", md(procedure["target_outcome"])]
    for title, key in (("Required Skills", "skills"), ("Prerequisites", "prerequisites"),
                       ("Stop Conditions", "stop_conditions"), ("Rollback", "rollback"),
                       ("Known Limits", "limits")):
        lines += ["", "## " + title] + ["- " + md(value) for value in procedure[key]]
        if not procedure[key]:
            lines += ["None declared; this is not proof of an exhaustive assessment."]
    lines += ["", "## Environment"] + ["- " + md(k) + ": " + md(v)
                                    for k, v in procedure["environment"].items()]
    lines += ["", "## Inputs"] + [md(item["text"]) for item in procedure["inputs"]]
    lines += ["", "## Ordered Steps"]
    for index, step in enumerate(procedure["steps"], 1):
        lines += [str(index) + ". " + md(step["id"]) + ": " + md(step["action"]),
                  "Expected: " + md(step["expected"])]
    lines += ["", "## Tests"] + ["- " + md(test["id"]) + ": " + md(test["assertion"])
                               for test in procedure["tests"]]
    lines += ["", "## Reviewed Operational Notes"] + [md(item["text"]) for item in procedure["derivatives"]]
    checklist = ["# Independent Programmer Replay", "",
                 "Record tester identity, consent, skills and exact kit hash.",
                 "Record environment and offset start/end timestamps.",
                 "No owner help. Do not fetch production data or credentials.",
                 "Log every failed or ambiguous step and all assistance requests.", ""]
    checklist += ["- [ ] " + md(test["id"]) + ": " + md(test["assertion"]) for test in procedure["tests"]]
    checklist += ["", "Provide signed tester evidence to owner for separate verification.",
                  "Automated tests and kit generation do not prove independent replay."]
    public_manifest = {"schema_version": 1, "procedure_id": procedure["procedure_id"],
                       "version": procedure["version"], "state": "documented",
                       "environment": procedure["environment"],
                       "assertion_ids": [test["id"] for test in procedure["tests"]],
                       "sources": [{"source_id": "source-" + str(i + 1), "sha256": ref["sha256"]}
                                   for i, ref in enumerate(procedure["source_refs"])]}
    files = {"procedure.md": "\n".join(lines) + "\n",
             "replay-checklist.md": "\n".join(checklist) + "\n",
             "manifest.json": canonical_bytes(public_manifest).decode("utf-8")}
    # Source paths and canonical work links stay outside the shareable kit.
    binding = {"procedure_hash": digest(procedure), "source_state": source_state,
               "files_hash": digest(files)}
    kit_hash = digest(binding)
    files["identity.json"] = canonical_bytes({"kit_hash": kit_hash,
                                             "files_hash": binding["files_hash"]}).decode("utf-8")
    return {"state": "documented", "kit_hash": kit_hash, "files": files,
            "binding": binding, "procedure": procedure}


def persist(ledger, procedure, expected_hash, *, owner_approved=False):
    require(owner_approved, "owner-approval-required", "documentation")
    with ledger.lock():
        kit = assemble(ledger, procedure)
        require(kit["kit_hash"] == expected_hash, "stale-approval", "kit_hash")
        folder = "documentation/" + procedure["procedure_id"] + "/v" + str(procedure["version"]) + "/"
        provenance = {"kit_hash": kit["kit_hash"], "binding": kit["binding"], "procedure": procedure}
        # Immutable provenance prevents same-version replacement with new source content.
        atomic_write(ledger.runtime(folder + "provenance.json"), canonical_bytes(provenance), immutable=True)
        for name, body in kit["files"].items():
            atomic_write(ledger.runtime(folder + "kit/" + name), body.encode("utf-8"), immutable=True)
        return {"state": "documented", "kit_hash": kit["kit_hash"], "folder": folder + "kit/"}


def verify_replay(ledger, procedure, kit_hash, replay, approval):
    kit = assemble(ledger, procedure)
    require(kit["kit_hash"] == kit_hash, "stale-kit", "kit_hash")
    shape(replay, {"schema_version", "tester_id", "tester_role", "consent", "kit_hash",
                   "environment", "start", "end", "successful_assertions", "failed_steps",
                   "ambiguous_steps", "help_requested", "kind", "signed_evidence_ref", "signed_at"})
    version(replay)
    identifier(replay["tester_id"], "tester_id")
    require(replay["tester_id"] != "owner" and replay["tester_role"] in {"programmer", "subcontractor"}
            and replay["consent"] is True and replay["kind"] == "human"
            and replay["help_requested"] is False,
            "independent-human-required", "replay")
    require(replay["kit_hash"] == kit_hash and replay["environment"] == procedure["environment"],
            "replay-version-conflict", "replay")
    start, end = instant(replay["start"], "start"), instant(replay["end"], "end")
    require(end.astimezone(timezone.utc) >= start.astimezone(timezone.utc),
            "reversed-interval", "replay")
    require(replay["failed_steps"] == [] and replay["ambiguous_steps"] == [],
            "replay-incomplete", "replay")
    ids = [test["id"] for test in procedure["tests"]]
    require(isinstance(replay["successful_assertions"], list)
            and len(replay["successful_assertions"]) == len(ids)
            and all(isinstance(value, str) for value in replay["successful_assertions"])
            and set(replay["successful_assertions"]) == set(ids),
            "missing-assertions", "replay")
    validate_source(replay["signed_evidence_ref"], ledger.config)
    signed = instant(replay["signed_at"], "signed_at")
    require(signed.astimezone(timezone.utc) >= end.astimezone(timezone.utc),
            "reversed-approval-order", "signed_at")
    shape(approval, {"kit_hash", "replay_hash", "signed_evidence_sha256", "approved_by",
                     "approved_at", "purpose", "human_evidence_verified"})
    require(approval["kit_hash"] == kit_hash and approval["replay_hash"] == digest(replay)
            and approval["signed_evidence_sha256"] == replay["signed_evidence_ref"]["sha256"]
            and approval["approved_by"] == "owner" and approval["purpose"] == "human-replay"
            and approval["human_evidence_verified"] is True,
            "replay-approval-required", "approval")
    approved = instant(approval["approved_at"], "approved_at")
    require(approved.astimezone(timezone.utc) >= signed.astimezone(timezone.utc),
            "reversed-approval-order", "approved_at")
    return {"state": "replay-passed", "kit_hash": kit_hash, "replay_hash": digest(replay),
            "evidence": "owner-verified human attestation, not automatic signature verification"}


def record_replay(ledger, procedure, kit_hash, replay, approval, *, owner_approved=False):
    require(owner_approved, "owner-approval-required", "replay")
    with ledger.lock():
        result = verify_replay(ledger, procedure, kit_hash, replay, approval)
        folder = "documentation/" + procedure["procedure_id"] + "/v" + str(procedure["version"]) + "/"
        provenance = ledger.runtime(folder + "provenance.json", exists=True)
        from work_evidence import read_json
        kit = assemble(ledger, procedure)
        require(read_json(provenance) == {"kit_hash": kit_hash, "binding": kit["binding"],
                                         "procedure": procedure}, "stale-kit", "provenance")
        directory = ledger.runtime(folder + "kit")
        require(directory.is_dir(), "incomplete-or-modified-kit", "kit")
        require({path.name for path in directory.iterdir()} == set(kit["files"]),
                "incomplete-or-modified-kit", "kit")
        for name, body in kit["files"].items():
            path = ledger.runtime(folder + "kit/" + name, exists=True)
            require(path.read_bytes() == body.encode("utf-8"), "modified-kit", "kit")
        result["replay"] = replay
        result["approval"] = approval
        atomic_write(ledger.runtime(folder + "replays/" + digest(replay) + ".json"),
                     canonical_bytes(result), immutable=True)
        return result
