"""Data-only editorial bundles and local drafts; never a publication client."""
from __future__ import annotations

import re
from datetime import timedelta

from work_evidence import (require, shape, version, identifier, text, choice, iso_date,
                           instant, digest, validate_source, read_json, canonical_bytes, safe_path)
from work_evidence_ledger import atomic_write
from work_evidence_docs import md, assemble

PRIVACY = {"public-ready", "needs-anonymization", "anonymized-needs-review", "internal-only"}
SECRET = re.compile(r"(?:password|api[_ -]?key|access[_ -]?token|secret)\s*[:=]\s*\S+"
                    r"|Bearer\s+[A-Za-z0-9._-]{12,}|-----BEGIN .{0,30}PRIVATE KEY", re.I)
CLAIM_TOKEN = re.compile(r"\{\{claim:([a-z0-9-]+)\}\}")


def safe_text(value, field):
    text(value, field)
    require(not SECRET.search(value), "secret-like-content", field)
    return value


def editorial_queue(brands, start, weeks):
    start = iso_date(start, "queue_start")
    require(start.weekday() == 0 and type(weeks) is int and 1 <= weeks <= 8,
            "invalid-queue-window", "queue")
    require(isinstance(brands, list) and len(brands) == 2, "invalid-brands", "brands")
    by_id, kinds = {}, set()
    for brand in brands:
        shape(brand, {"brand_id", "kind", "name", "primary_language", "optional_languages",
                      "newsletter_title", "newsletter_anchor"})
        identifier(brand["brand_id"], "brand_id")
        require(brand["brand_id"] not in by_id and brand["kind"] not in kinds,
                "duplicate-brand", "brand")
        choice(brand["kind"], {"personal", "company"}, "kind")
        primary = "pl" if brand["kind"] == "personal" else "en"
        require(brand["primary_language"] == primary, "brand-language-conflict", "brand")
        require(isinstance(brand["optional_languages"], list)
                and len(brand["optional_languages"]) <= 1
                and all(lang in {"pl", "en"} - {primary} for lang in brand["optional_languages"]),
                "invalid-languages", "brand")
        safe_text(brand["name"], "brand_name")
        safe_text(brand["newsletter_title"], "newsletter_title")
        iso_date(brand["newsletter_anchor"], "anchor")
        by_id[brand["brand_id"]] = brand
        kinds.add(brand["kind"])
    anchors = [iso_date(b["newsletter_anchor"], "anchor") for b in brands]
    require(abs((anchors[0] - anchors[1]).days) % 14 == 7,
            "newsletter-not-staggered", "brands")
    slots = []
    for brand in brands:
        languages = [brand["primary_language"]] + brand["optional_languages"]
        for week in range(weeks):
            monday = start + timedelta(days=week * 7)
            for index, offset in enumerate((1, 3, 5)):
                day = monday + timedelta(days=offset)
                slots.append({"slot_id": brand["brand_id"] + ":social:" + day.isoformat(),
                              "brand_id": brand["brand_id"], "channel": "social",
                              "date": day.isoformat(), "optional": index == 2,
                              "languages": languages})
        anchor = iso_date(brand["newsletter_anchor"], "anchor")
        day = start + timedelta(days=(anchor - start).days % 14)
        while day < start + timedelta(days=weeks * 7):
            slots.append({"slot_id": brand["brand_id"] + ":newsletter:" + day.isoformat(),
                          "brand_id": brand["brand_id"], "channel": "newsletter",
                          "date": day.isoformat(), "optional": False, "languages": languages})
            day += timedelta(days=14)
    pilots = {b["brand_id"]: [{"issue": i + 1,
                              "date": (iso_date(b["newsletter_anchor"], "anchor")
                                       + timedelta(days=i * 14)).isoformat(),
                              "languages": [b["primary_language"]] + b["optional_languages"],
                              "visits": None, "signups": None, "qualified_replies": None,
                              "effort_minutes": None, "translation_review": "required"}
                             for i in range(4)] for b in brands}
    return by_id, slots, pilots


def selected_claim(ledger, claim):
    shape(claim, {"claim_id", "entry_id", "entry_hash", "source_ref", "text", "privacy_state",
                  "sensitive_terms", "replacements", "review", "supported", "approval"},
          {"procedure_ref"})
    identifier(claim["claim_id"], "claim_id")
    entry = ledger.committed()[0].get(claim["entry_id"])
    require(entry is not None and not entry.get("voided", False)
            and digest(entry) == claim["entry_hash"], "stale-claim", "claim")
    validate_source(claim["source_ref"], ledger.config)
    require(claim["source_ref"] in entry["source_refs"], "unlinked-claim-source", "claim")
    for ref in entry["source_refs"]:
        validate_source(ref, ledger.config)
    if "procedure_ref" in claim:
        doc = claim["procedure_ref"]
        shape(doc, {"procedure_id", "version", "kit_hash"})
        identifier(doc["procedure_id"], "procedure_id")
        require(type(doc["version"]) is int and doc["version"] > 0, "invalid-version", "procedure")
        folder = "documentation/" + doc["procedure_id"] + "/v" + str(doc["version"]) + "/"
        saved = read_json(ledger.runtime(folder + "provenance.json", exists=True))
        kit = assemble(ledger, saved["procedure"])
        require(doc["kit_hash"] == kit["kit_hash"] == saved["kit_hash"]
                and entry["work_id"] in saved["procedure"]["work_ids"],
                "stale-documentation", "claim")
        for name, value in kit["files"].items():
            require(ledger.runtime(folder + "kit/" + name, exists=True).read_bytes() ==
                    value.encode("utf-8"), "stale-documentation", "claim")
    safe_text(claim["text"], "claim")
    choice(claim["privacy_state"], PRIVACY, "privacy_state")
    require(type(claim["supported"]) is bool, "invalid-support-state", "claim")
    require(isinstance(claim["sensitive_terms"], list) and len(claim["sensitive_terms"]) <= 100
            and all(isinstance(term, str) and term.strip() for term in claim["sensitive_terms"]),
            "invalid-sensitive-terms", "claim")
    shape(claim["review"], {"identifiers", "quasi_identifiers", "contracts", "copyright"})
    require(all(type(value) is bool for value in claim["review"].values()),
            "invalid-review", "claim")
    require(isinstance(claim["replacements"], list) and len(claim["replacements"]) <= 100,
            "invalid-replacements", "claim")
    replacements = {}
    for row in claim["replacements"]:
        shape(row, {"from", "to"})
        safe_text(row["from"], "replacement")
        safe_text(row["to"], "replacement")
        require(row["from"].casefold() not in replacements, "duplicate-replacement", "claim")
        replacements[row["from"].casefold()] = row["to"]
    if not claim["supported"] or claim["privacy_state"] == "internal-only":
        return {"claim_id": claim["claim_id"], "state": "held",
                "reason": "unsupported-benefit" if not claim["supported"] else "internal-only"}
    if claim["privacy_state"] == "public-ready":
        approval = claim["approval"]
        shape(approval, {"claim_hash", "purpose", "approved_by", "approved_at"})
        instant(approval["approved_at"], "approved_at")
        unsigned = {key: value for key, value in claim.items() if key != "approval"}
        require(approval["claim_hash"] == digest(unsigned) and approval["purpose"] == "editorial-source"
                and approval["approved_by"] == "owner" and all(claim["review"].values()),
                "claim-approval-required", "claim")
    derivative = claim["text"]
    for term in sorted(replacements, key=len, reverse=True):
        derivative = re.sub(re.escape(term), lambda m: replacements[term], derivative, flags=re.I)
    if any(term.casefold() in derivative.casefold() for term in claim["sensitive_terms"]):
        return {"claim_id": claim["claim_id"], "state": "held", "reason": "needs-anonymization"}
    if claim["privacy_state"] == "needs-anonymization" and not replacements:
        return {"claim_id": claim["claim_id"], "state": "held", "reason": "needs-anonymization"}
    return {"claim_id": claim["claim_id"], "text": derivative,
            "state": ("public-ready" if claim["privacy_state"] == "public-ready"
                      else "anonymized-needs-review"),
            "source_claim_hash": digest(claim)}


def bundle(ledger, request):
    ledger.check_loaded()
    shape(request, {"schema_version", "topic_id", "claims", "brands", "queue_start", "weeks", "drafts"})
    version(request)
    identifier(request["topic_id"], "topic_id")
    require(isinstance(request["claims"], list) and len(request["claims"]) <= 100,
            "invalid-claims", "request")
    claims = [selected_claim(ledger, claim) for claim in request["claims"]]
    require(len({c["claim_id"] for c in claims}) == len(claims), "duplicate-claim", "request")
    available = {c["claim_id"]: c for c in claims if c["state"] != "held"}
    brands, slots, pilots = editorial_queue(request["brands"], request["queue_start"], request["weeks"])
    slot_map = {s["slot_id"]: s for s in slots}
    require(isinstance(request["drafts"], list) and len(request["drafts"]) <= 200,
            "invalid-drafts", "request")
    files, drafts, identities = {}, [], set()
    source_hash = digest({"claims": claims, "snapshot": ledger.snapshot()})
    for draft in request["drafts"]:
        shape(draft, {"draft_id", "brand_id", "language", "channel", "slot_id",
                      "claim_ids", "title", "body", "approval"})
        identifier(draft["draft_id"], "draft_id")
        require(draft["brand_id"] in brands and draft["slot_id"] in slot_map,
                "unknown-editorial-slot", "draft")
        slot = slot_map[draft["slot_id"]]
        require(slot["brand_id"] == draft["brand_id"] and slot["channel"] == draft["channel"]
                and draft["language"] in slot["languages"], "draft-slot-conflict", "draft")
        identity = (draft["slot_id"], draft["language"])
        require(identity not in identities and draft["draft_id"] not in files,
                "duplicate-variant", "draft")
        identities.add(identity)
        require(isinstance(draft["claim_ids"], list) and draft["claim_ids"]
                and len(set(draft["claim_ids"])) == len(draft["claim_ids"])
                and all(cid in available for cid in draft["claim_ids"]), "held-or-missing-claim", "draft")
        safe_text(draft["title"], "title")
        safe_text(draft["body"], "body")
        require(set(CLAIM_TOKEN.findall(draft["body"])) == set(draft["claim_ids"]),
                "unmapped-draft-claim", "draft")
        rendered = CLAIM_TOKEN.sub(lambda match: available[match[1]]["text"], draft["body"])
        require("{{claim:" not in rendered, "unmapped-draft-claim", "draft")
        terms = [t for c in request["claims"] for t in c["sensitive_terms"]]
        require(not any(term.casefold() in rendered.casefold() or
                        term.casefold() in draft["title"].casefold() for term in terms),
                "draft-needs-anonymization", "draft")
        safe_text(rendered, "rendered")
        basis = {"source_hash": source_hash, "brand_id": draft["brand_id"],
                 "language": draft["language"], "channel": draft["channel"],
                 "slot_id": draft["slot_id"], "title": draft["title"], "body": rendered}
        approval = draft["approval"]
        review_state = "needs-review"
        if approval is not None:
            shape(approval, {"content_hash", "source_hash", "brand_id", "language", "channel",
                             "purpose", "approved_by", "approved_at"})
            instant(approval["approved_at"], "approved_at")
            require(approval["content_hash"] == digest(basis) and approval["source_hash"] == source_hash
                    and approval["brand_id"] == draft["brand_id"]
                    and approval["language"] == draft["language"] and approval["channel"] == draft["channel"]
                    and approval["purpose"] == "editorial-draft" and approval["approved_by"] == "owner"
                    and all(available[cid]["state"] == "public-ready" for cid in draft["claim_ids"]),
                    "draft-approval-required", "draft")
            review_state = "owner-reviewed-draft"
        content = ("# " + md(draft["title"]) + "\n\n"
                   + "Local draft; publication not authorized. Review: " + review_state + "\n\n"
                   + md(rendered) + "\n")
        filename = draft["draft_id"] + ".md"
        require(filename not in files, "duplicate-draft", "draft")
        files[filename] = content
        drafts.append({**basis, "content_hash": digest(basis), "review_state": review_state,
                       "claim_ids": draft["claim_ids"], "draft_id": draft["draft_id"]})
    return {"schema_version": 1, "state": "draft-only", "topic_id": request["topic_id"],
            "source_hash": source_hash, "request_hash": digest(request), "claims": claims,
            "queue": slots, "language_pilot": pilots, "drafts": drafts, "files": files,
            "files_hash": digest(files), "model_calls": 0, "publication_authorized": False}


def persist_bundle(ledger, request, expected_hash, *, owner_approved=False):
    require(owner_approved, "owner-approval-required", "editorial")
    policy = ledger.config.get("editorial_policy")
    shape(policy, {"destination_root"})
    root = safe_path(ledger.workspace, policy["destination_root"], must_exist=False)
    require(root.is_dir(), "unconfigured-editorial-destination", "editorial")
    with ledger.lock():
        result = bundle(ledger, request)
        require(digest(result) == expected_hash, "stale-approval", "editorial")
        relative = request["topic_id"] + "/" + expected_hash + "/"
        private = {"request": request, "result_hash": expected_hash,
                   "source_hash": result["source_hash"], "files_hash": result["files_hash"]}
        atomic_write(ledger.runtime("editorial/" + relative + "private-manifest.json"),
                     canonical_bytes(private), immutable=True)
        for name, body in result["files"].items():
            atomic_write(safe_path(root, relative + name, must_exist=False),
                         body.encode("utf-8"), immutable=True)
        atomic_write(ledger.runtime("editorial/" + relative + "review-queue.json"),
                     canonical_bytes({k: v for k, v in result.items() if k != "files"}), immutable=True)
        return {"state": "draft-only", "bundle_hash": expected_hash,
                "relative_folder": policy["destination_root"] + "/" + relative,
                "publication_authorized": False}
