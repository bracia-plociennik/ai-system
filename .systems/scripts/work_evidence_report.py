"""Recipient-isolated local reports; approved projections never send mail."""
from __future__ import annotations

import html

from work_evidence import (digest, canonical_bytes, require, shape, version, identifier,
                           text, instant, validate_registry, validate_source)
from work_evidence_docs import md, approved_text
from work_evidence_ledger import atomic_write, period_entries


def descendant(entities, child, parent):
    while child is not None:
        if child == parent:
            return True
        child = entities[child].get("parent_id")
    return False


def report(ledger, policy):
    shape(policy, {"schema_version", "report_id", "recipient_id", "client_ids", "project_ids",
                   "start", "end_exclusive", "coverage_attested", "texts", "recurring_care"})
    version(policy)
    identifier(policy["report_id"], "report_id")
    entities = validate_registry(ledger.registry)
    recipient = policy["recipient_id"]
    require(isinstance(recipient, str) and recipient in entities
            and entities[recipient]["kind"] in {"client", "agency"}, "unknown-recipient", "recipient")
    for field, kind in (("client_ids", "client"), ("project_ids", "project")):
        values = policy[field]
        require(isinstance(values, list) and len(values) <= 100
                and all(isinstance(value, str) for value in values)
                and len(set(values)) == len(values), "invalid-scope", field)
        for value in values:
            require(value in entities and entities[value]["kind"] == kind, "unknown-entity", field)
    require(policy["client_ids"], "missing-scope", "client_ids")
    for value in policy["client_ids"]:
        require(descendant(entities, value, recipient), "recipient-scope-conflict", "client_ids")
    for value in policy["project_ids"]:
        require(entities[value].get("parent_id") in policy["client_ids"],
                "project-scope-conflict", "project_ids")
    require(type(policy["coverage_attested"]) is bool, "invalid-coverage", "coverage_attested")
    current = ledger.committed()[0]
    selected = [entry for entry in current.values()
                if entry["client_id"] in policy["client_ids"]
                and (not policy["project_ids"] or entry["project_id"] in policy["project_ids"])]
    period = period_entries(selected, policy["start"], policy["end_exclusive"])
    for row in period["exact"] + period["partly_overlapping_aggregates"]:
        for ref in row["entry"]["source_refs"]:
            validate_source(ref, ledger.config)
    require(isinstance(policy["texts"], list) and len(policy["texts"]) <= 10000,
            "invalid-list", "texts")
    approved = {}
    for row in policy["texts"]:
        shape(row, {"entry_id", "entry_hash", "recipient_id", "text", "text_hash",
                    "purpose", "approved_by", "approved_at"})
        key = row["entry_id"]
        require(isinstance(key, str) and key not in approved and key in current,
                "invalid-projection-entry", "entry_id")
        entry = current[key]
        require(entry in selected and not entry.get("voided", False)
                and row["entry_hash"] == digest(entry), "stale-projection", "entry_hash")
        require(row["recipient_id"] == recipient and row["purpose"] == "client-report"
                and row["approved_by"] == "owner" and row["text_hash"] == digest(row["text"]),
                "projection-approval-required", "projection")
        text(row["text"], "safe_text")
        instant(row["approved_at"], "approved_at")
        approved[key] = row["text"]
    care = []
    require(isinstance(policy["recurring_care"], list) and len(policy["recurring_care"]) <= 100,
            "invalid-list", "recurring_care")
    for item in policy["recurring_care"]:
        shape(item, {"recipient_id", "source_ref", "derivative"})
        require(item["recipient_id"] == recipient, "recipient-scope-conflict", "care")
        validate_source(item["source_ref"], ledger.config)
        care.append(approved_text(item["derivative"], [item["source_ref"]], "client-care"))
    groups = {"done": [], "in-progress": [], "unknown": []}
    missing = 0
    for row in period["exact"] + period["partly_overlapping_aggregates"]:
        entry = row["entry"]
        if entry["entry_id"] not in approved:
            missing += 1
            continue
        group = "done" if entry["status"] == "done" else (
            "unknown" if entry["status"] == "unknown" else "in-progress")
        groups[group].append({"text": approved[entry["entry_id"]], "status": entry["status"]})
    actual = [row["actual_seconds"] for row in period["exact"] if row["actual_seconds"] is not None]
    unknown = sum(row["entry"]["duration"]["basis"] == "unknown" for row in period["exact"])
    estimates = [{"seconds": row["entry"]["duration"]["seconds"]} for row in period["exact"]
                 if row["entry"]["duration"]["basis"] == "estimated"]
    coverage = {"known_actual_human_seconds": sum(actual), "confirmed_rows": len(actual),
                "unknown_duration_rows": unknown, "estimated_rows": len(estimates),
                "estimated_seconds": sum(row["seconds"] for row in estimates),
                "partial_aggregate_rows": len(period["partly_overlapping_aggregates"]),
                "withheld_outcome_rows": missing, "recorded_rows": len(period["exact"]),
                "period_coverage": "owner-attested" if policy["coverage_attested"] else "unknown",
                "no_recorded_work": not period["exact"] and not period["partly_overlapping_aggregates"]}
    index_state = ledger.index_status()["status"]
    heading = "Client Work Report: " + policy["start"] + " to " + policy["end_exclusive"] + " (exclusive)"
    lines = ["# " + md(heading), "", "Local draft, not sent. Period timezone: Europe/Warsaw."]
    blocks = []
    for label, key in (("Completed outcomes", "done"), ("Partial / blocked / waiting", "in-progress"),
                       ("Status unknown", "unknown")):
        lines += ["", "## " + label]
        rows = groups[key]
        lines += ["- " + md(row["text"]) + " (" + row["status"] + ")" for row in rows] or ["No approved outcomes recorded."]
        blocks += ["<h2>" + label + "</h2><ul>" + "".join(
            "<li>" + html.escape(row["text"]) + " (" + row["status"] + ")</li>" for row in rows) + "</ul>"]
    lines += ["", "## Contractual recurring care", "Agreed scope only; not proof of unlogged execution or hours."]
    lines += ["- " + md(value) for value in care] or ["No approved service catalogue supplied."]
    blocks += ["<h2>Contractual recurring care</h2><p>Agreed scope only; no performed hours inferred.</p><ul>"
               + "".join("<li>" + html.escape(value) + "</li>" for value in care) + "</ul>"]
    details = ("Known actual human time: " + str(coverage["known_actual_human_seconds"]) + " seconds; "
               "confirmed rows: " + str(coverage["confirmed_rows"]) + "; unknown rows: " + str(unknown)
               + "; estimates: " + str(coverage["estimated_seconds"]) + " seconds (not actual). "
               "Partial aggregate rows excluded from exact sum: " + str(coverage["partial_aggregate_rows"])
               + "; withheld outcomes: " + str(missing) + ". Period coverage: " + coverage["period_coverage"]
               + ". No recorded rows does not prove no work. Index: " + index_state + "; canonical ledger used.")
    lines += ["", "## Coverage", md(details)]
    document = "<!doctype html><html lang=\"en\"><meta charset=\"utf-8\"><title>Local report draft</title><body><h1>" + html.escape(heading) + "</h1><p>Local draft, not sent.</p>" + "".join(blocks) + "<h2>Coverage</h2><p>" + html.escape(details) + "</p></body></html>\n"
    files = {"report.md": "\n".join(lines) + "\n", "report.html": document}
    manifest = {"schema_version": 1, "policy_hash": digest(policy), "recipient_id": recipient,
                "start": policy["start"], "end_exclusive": policy["end_exclusive"],
                "timezone": "Europe/Warsaw", "coverage": coverage, "index_state": index_state,
                "source_snapshot": ledger.snapshot(),
                "entry_hashes": {row["entry"]["entry_id"]: digest(row["entry"])
                                 for row in period["exact"] + period["partly_overlapping_aggregates"]},
                "files_hash": digest(files)}
    return {"state": "local-draft", "draft_hash": digest(manifest), "files": files, "manifest": manifest}


def write_report(ledger, policy, expected_hash, *, owner_approved=False):
    require(owner_approved, "owner-approval-required", "report")
    with ledger.lock():
        result = report(ledger, policy)
        require(result["draft_hash"] == expected_hash, "stale-approval", "draft_hash")
        folder = "reports/" + policy["start"] + "/" + policy["report_id"] + "/" + expected_hash + "/"
        atomic_write(ledger.runtime(folder + "private-manifest.json"), canonical_bytes(result["manifest"]), immutable=True)
        for name, body in result["files"].items():
            atomic_write(ledger.runtime(folder + "client-draft/" + name), body.encode("utf-8"), immutable=True)
        return {"state": "local-draft", "draft_hash": expected_hash, "folder": folder + "client-draft/"}
