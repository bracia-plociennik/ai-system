"""Independent editorial v2: data preparation, route review and local concepts."""
from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlsplit

from work_evidence import (require, shape, identifier, sha, instant, digest, read_json,
                           canonical_bytes, safe_path, validate_source)
from work_evidence_editorial import selected_claim, editorial_queue, safe_text, CLAIM_TOKEN
from work_evidence_ledger import atomic_write
from work_evidence_docs import md

FORMATS = ("blog-article", "newsletter", "social-post", "short-video-concept", "youtube-concept")
PREPARE_FIELDS = {"editorial_schema_version", "topic", "claims", "brands",
                  "queue_start", "weeks", "capacity"}
REQUEST_FIELDS = PREPARE_FIELDS | {"recommendation", "decision", "artifacts", "previous_bundle_hash"}
TOPIC_FIELDS = {"topic_id", "revision", "title", "audience_problem", "transferable_lesson",
                "selected_brand_ids", "claim_ids", "brand_angles"}
ASSESSMENT_FIELDS = {"brand_id", "format", "fit", "readiness", "rationale",
                     "evidence_gaps", "confidence", "effort_minutes"}
NODE_FIELDS = {"node_id", "brand_id", "language", "format", "output_kind", "objective",
               "claim_ids", "allocation_group", "slot_id", "effort_minutes"}
DECISION_FIELDS = {"decision_id", "recommendation_hash", "source_hash", "selected_route_id",
                   "route_hash", "previous_bundle_hash", "mode", "reason", "approved_by",
                   "approved_at", "authority_ref"}
APPROVAL_FIELDS = {"content_hash", "source_hash", "decision_hash", "brand_id", "language",
                   "format", "purpose", "approved_by", "approved_at", "authority_ref"}
FORMAT_FIELDS = {
    "blog-article": {"proposed_slug", "meta_description", "tldr", "key_takeaways", "outline", "cta"},
    "newsletter": {"subject", "preheader", "standalone_value", "additional_value", "cta"},
    "social-post": {"hook", "key_takeaways", "cta"},
    "short-video-concept": {"hook", "teaching_point", "scenes", "assets_needed", "cta"},
    "youtube-concept": {"working_title", "promise", "outline", "demo_plan", "assets_needed", "cta"},
}
BLOCKED_READINESS = {"internal-only", "needs-evidence", "needs-anonymization"}
LOCAL_TEXT = re.compile(r"(?:file://|/Users/|/private/|/tmp/|[A-Za-z]:\\|"
                        r"(?i:private-tax|working[- ]dump|raw[- ]check[- ]in)/)")
SECRET_ASSIGNMENT = re.compile(r"(?i)\b(?:token|api[_-]?key|secret|password|credential)\s*[:=]\s*\S+")


def public_url(url):
    parsed = urlsplit(url)
    require(parsed.scheme in {"http", "https"} and parsed.hostname and parsed.username is None
            and parsed.password is None and not re.search(r"[\s\\]", url),
            "unsafe-editorial-url", "url")
    host = parsed.hostname.lower().rstrip(".")
    require(host not in {"localhost", "localhost.localdomain"}
            and not host.endswith((".local", ".localhost", ".internal")), "unsafe-editorial-url", "url")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        require("." in host and re.fullmatch(r"[a-z0-9.-]+", host.encode("idna").decode("ascii"))
                and not host.rsplit(".", 1)[-1].isdigit(), "unsafe-editorial-url", "url")
    else:
        require(address.is_global, "unsafe-editorial-url", "url")


def editorial_version(request):
    require(isinstance(request, dict), "invalid-shape", "request")
    if "editorial_schema_version" in request:
        require("schema_version" not in request
                and type(request["editorial_schema_version"]) is int
                and request["editorial_schema_version"] == 2,
                "unsupported-editorial-version", "request")
        return 2
    require(type(request.get("schema_version")) is int and request["schema_version"] == 1,
            "unsupported-editorial-version", "request")
    return 1


def items(values, field, *, limit=200, empty=True):
    require(isinstance(values, list) and len(values) <= limit and (empty or bool(values)),
            "invalid-list", field)
    return values


def ids(values, field, *, limit=100, empty=True):
    items(values, field, limit=limit, empty=empty)
    for value in values:
        identifier(value, field)
    require(len(set(values)) == len(values), "duplicate-identity", field)
    return values


def effort(value):
    require(value is None or (type(value) is int and value >= 0),
            "invalid-effort", "effort")


def positive(value):
    require(type(value) is int and value > 0, "invalid-revision", "revision")


def texts(values, field):
    for value in items(values, field):
        safe_text(value, field)


def clean(value, terms=()):
    """Scan all agent prose/metadata; known identifiers never hide in a title."""
    if isinstance(value, str):
        safe_text(value, "editorial-text")
        require(not SECRET_ASSIGNMENT.search(value), "secret-editorial-content", "text")
        require(not LOCAL_TEXT.search(value), "private-editorial-path", "text")
        for url in re.findall(r"https?://[^\s<>]+", value):
            public_url(url.rstrip(".,;!?)"))
        require(not any(term.casefold() in value.casefold() for term in terms),
                "editorial-needs-anonymization", "text")
    elif isinstance(value, dict):
        for key, item in value.items():
            clean(key, terms)
            clean(item, terms)
    elif isinstance(value, list):
        for item in value:
            clean(item, terms)


def owner_record(record):
    require(record["approved_by"] == "owner", "owner-approval-required", "record")
    instant(record["approved_at"], "approved_at")
    # The calling agent checks the real scoped instruction; metadata is not consent.
    require(isinstance(record["authority_ref"], str)
            and re.fullmatch(r"(?:chat|decision):[a-z0-9][a-z0-9-]{0,199}", record["authority_ref"]),
            "invalid-authority-reference", "approval")


def original_claim_hash(claim):
    """Bind owner review to the original lesson, independently of its derivative."""
    fields = {"claim_id", "entry_id", "entry_hash", "source_ref", "text",
              "supported", "sensitive_terms", "procedure_ref"}
    return digest({k: v for k, v in claim.items() if k in fields})


def original_lesson(ledger, claim):
    base = {k: v for k, v in claim.items() if k != "private_review"}
    require(base.get("privacy_state") in {"public-ready", "needs-anonymization",
                                        "anonymized-needs-review", "internal-only"},
            "invalid-privacy-state", "claim")
    probe = {**base, "privacy_state": "internal-only", "approval": None}
    # Validate live evidence without applying any transformation to the original.
    selected_claim(ledger, probe)
    safe_text(base["text"], "original-lesson")
    require(not SECRET_ASSIGNMENT.search(base["text"]), "secret-editorial-content", "lesson")
    entry = ledger.committed()[0][base["entry_id"]]
    return {"claim_id": base["claim_id"], "text": base["text"],
            "original_hash": original_claim_hash(base), "source_ref": base["source_ref"],
            "entry_id": base["entry_id"], "supported": base["supported"],
            "privacy_state": base["privacy_state"],
            "context": {k: entry[k] for k in ("work_id", "client_id", "project_id") if k in entry}}


def review_source(ledger, request):
    require(editorial_version(request) == 2, "unsupported-editorial-version", "review-source")
    shape(request, PREPARE_FIELDS)
    ledger.check_loaded()
    shape(request["topic"], TOPIC_FIELDS)
    selected = ids(request["topic"]["claim_ids"], "claim_ids")
    claims = items(request["claims"], "claims", limit=100)
    lessons = [original_lesson(ledger, c) for c in claims]
    require(len({c["claim_id"] for c in lessons}) == len(lessons),
            "duplicate-claim", "claims")
    require(set(selected) <= {c["claim_id"] for c in lessons}, "unlinked-topic-claim", "topic")
    lessons = [c for c in lessons if c["claim_id"] in selected]
    lines = ["# Private Original Lessons", "", "Owner-only. Disclosure not authorized.", ""]
    for lesson in lessons:
        lines += ["## " + md(lesson["claim_id"]), "", md(lesson["text"]), "",
                  "Evidence supported: " + str(lesson["supported"]),
                  "Original hash: " + lesson["original_hash"],
                  "Context: " + md(str(lesson["context"])),
                  "Source: " + md(str(lesson["source_ref"])), ""]
    return {"state": "private-owner-review", "audience": "owner-only", "lessons": lessons,
            "markdown": "\n".join(lines) + "\n", "publication_authorized": False, "model_calls": 0}


def reviewed_claim(ledger, claim):
    original_lesson(ledger, claim)
    base = {k: v for k, v in claim.items() if k != "private_review"}
    review = claim.get("private_review")
    if "private_review" in claim:
        shape(review, {"original_hash", "purpose", "approved_by", "approved_at", "authority_ref"})
        owner_record(review)
        require(review["purpose"] == "private-lesson-anonymization"
                and review["original_hash"] == original_claim_hash(base),
                "private-lesson-review-required", "claim")
    if base["replacements"] and review is None:
        return {"claim_id": base["claim_id"], "state": "held", "reason": "needs-private-review"}
    return selected_claim(ledger, base)


def prepare(ledger, request):
    require(editorial_version(request) == 2, "unsupported-editorial-version", "prepare")
    shape(request, PREPARE_FIELDS)
    ledger.check_loaded()
    topic = request["topic"]
    shape(topic, TOPIC_FIELDS)
    identifier(topic["topic_id"], "topic_id")
    positive(topic["revision"])
    for field in ("title", "audience_problem", "transferable_lesson"):
        safe_text(topic[field], field)
    selected = ids(topic["selected_brand_ids"], "selected_brand_ids", limit=2, empty=False)
    ids(topic["claim_ids"], "claim_ids")
    brands, queue, _ = editorial_queue(request["brands"], request["queue_start"], request["weeks"])
    require(set(selected) <= set(brands), "unknown-brand", "topic")
    angles = items(topic["brand_angles"], "brand_angles", limit=2, empty=False)
    for angle in angles:
        shape(angle, {"brand_id", "audience", "promise", "angle"})
        for field in ("audience", "promise", "angle"):
            safe_text(angle[field], field)
    require(len(angles) == len(selected) and {a["brand_id"] for a in angles} == set(selected),
            "brand-angle-conflict", "topic")
    shape(request["capacity"], {"effort_budget_minutes"})
    effort(request["capacity"]["effort_budget_minutes"])
    items(request["claims"], "claims", limit=100)
    for claim in request["claims"]:
        require(isinstance(claim, dict) and isinstance(claim.get("text"), str), "invalid-shape", "claim")
        require(not SECRET_ASSIGNMENT.search(claim["text"]), "secret-editorial-content", "claim")
    claims = [reviewed_claim(ledger, claim) for claim in request["claims"]]
    require(len({c["claim_id"] for c in claims}) == len(claims), "duplicate-claim", "claims")
    require(set(topic["claim_ids"]) <= {c["claim_id"] for c in claims},
            "unlinked-topic-claim", "topic")
    terms = [t for claim in request["claims"] for t in claim["sensitive_terms"]]
    clean(topic, terms)
    clean(request["brands"], terms)
    available = [c for c in claims if c["state"] != "held"]
    clean(available, terms)
    held = [{"claim_id": c["claim_id"], "reason": c["reason"]} for c in claims if c["state"] == "held"]
    # Entry digests include all linked source hashes; unrelated work never invalidates a topic.
    basis = {k: request[k] for k in PREPARE_FIELDS if k not in {"editorial_schema_version", "claims"}}
    source_hash = digest({**basis, "claims": request["claims"],
                          "config": ledger.loaded_config_hash, "registry": ledger.loaded_registry_hash})
    ready = bool(topic["claim_ids"]) and set(topic["claim_ids"]) <= {c["claim_id"] for c in available}
    result = {"editorial_schema_version": 2, "state": "prepared" if ready else "needs-evidence",
              "topic": topic, "claims": available, "held_claims": held,
              "brands": [brands[bid] for bid in selected],
              "queue": [s for s in queue if s["brand_id"] in selected], "capacity": request["capacity"],
              "source_hash": source_hash, "model_calls": 0, "publication_authorized": False}
    result["package_hash"] = digest(result)
    return result


def validate_route(route, package):
    shape(route, {"route_id", "title", "why", "tradeoffs", "nodes", "edges"})
    identifier(route["route_id"], "route_id")
    safe_text(route["title"], "title")
    safe_text(route["why"], "why")
    texts(route["tradeoffs"], "tradeoffs")
    nodes = items(route["nodes"], "nodes", limit=40)
    node_map, groups, slots, variants = {}, {}, {}, set()
    brands = {b["brand_id"]: b for b in package["brands"]}
    slot_map = {s["slot_id"]: s for s in package["queue"]}
    claim_ids = set(package["topic"]["claim_ids"])
    for node in nodes:
        shape(node, NODE_FIELDS)
        for field in ("node_id", "allocation_group"):
            identifier(node[field], field)
        require(node["node_id"] not in node_map, "duplicate-node", "node")
        require(node["brand_id"] in brands and node["format"] in FORMATS, "invalid-route-node", "node")
        brand = brands[node["brand_id"]]
        require(node["language"] in [brand["primary_language"]] + brand["optional_languages"],
                "brand-language-conflict", "node")
        kinds = {"concept"} if node["format"].endswith("-concept") else {"brief", "draft"}
        require(node["output_kind"] in kinds, "invalid-output-kind", "node")
        ids(node["claim_ids"], "claim_ids", empty=False)
        require(set(node["claim_ids"]) <= claim_ids, "unlinked-route-claim", "node")
        effort(node["effort_minutes"])
        safe_text(node["objective"], "objective")
        slot = node["slot_id"]
        if slot is not None:
            require(node["format"] not in {"blog-article", "youtube-concept"}
                    and slot in slot_map, "unknown-editorial-slot", "node")
            channel = "newsletter" if node["format"] == "newsletter" else "social"
            require(slot_map[slot]["brand_id"] == node["brand_id"]
                    and slot_map[slot]["channel"] == channel, "draft-slot-conflict", "node")
            require(slot not in slots or slots[slot] == node["allocation_group"],
                    "capacity-conflict", "slot")
            slots[slot] = node["allocation_group"]
        group = node["allocation_group"]
        signature = (node["brand_id"], node["format"], slot, node["output_kind"], node["objective"],
                     tuple(node["claim_ids"]))
        require(group not in groups or groups[group] == signature, "allocation-group-conflict", "node")
        groups[group] = signature
        require((group, node["language"]) not in variants, "duplicate-variant", "node")
        variants.add((group, node["language"]))
        node_map[node["node_id"]] = node
    edges = items(route["edges"], "edges", limit=100)
    seen, dependencies = set(), {nid: [] for nid in node_map}
    for edge in edges:
        shape(edge, {"from_node_id", "to_node_id", "relation"})
        a, b = edge["from_node_id"], edge["to_node_id"]
        require(a in node_map and b in node_map and a != b
                and edge["relation"] in {"related-to", "requires-artifact"},
                "invalid-editorial-graph", "edge")
        key = (a, b, edge["relation"])
        require(key not in seen, "invalid-editorial-graph", "edge")
        seen.add(key)
        if edge["relation"] == "requires-artifact":
            dependencies[b].append(a)
    active, visited = set(), set()
    def visit(nid):
        require(nid not in active, "invalid-editorial-graph", "cycle")
        if nid in visited:
            return
        active.add(nid)
        for parent in dependencies[nid]:
            visit(parent)
        active.remove(nid)
        visited.add(nid)
    for nid in node_map:
        visit(nid)
    return node_map, dependencies


def recommendation(value, package, terms):
    shape(value, {"package_hash", "recommendation_id", "revision", "assessments",
                  "primary", "alternative", "questions"})
    require(value["package_hash"] == package["package_hash"], "stale-recommendation", "package")
    identifier(value["recommendation_id"], "recommendation_id")
    positive(value["revision"])
    texts(value["questions"], "questions")
    rows = items(value["assessments"], "assessments", limit=10)
    expected = {(b["brand_id"], f) for b in package["brands"] for f in FORMATS}
    found = {}
    for row in rows:
        shape(row, ASSESSMENT_FIELDS)
        key = (row["brand_id"], row["format"])
        require(key in expected and key not in found, "invalid-format-assessments", "assessment")
        require(row["fit"] in {"recommended", "optional", "defer", "unsuitable"}
                and row["readiness"] in BLOCKED_READINESS | {"needs-review", "ready-for-local-draft"}
                and row["confidence"] in {"low", "medium", "high"},
                "invalid-format-assessments", "assessment")
        texts(row["evidence_gaps"], "evidence_gaps")
        safe_text(row["rationale"], "rationale")
        effort(row["effort_minutes"])
        found[key] = row
    require(set(found) == expected, "incomplete-format-assessments", "assessment")
    routes = {}
    for field in ("primary", "alternative"):
        routes[field] = validate_route(value[field], package)
    main, alternative = value["primary"], value["alternative"]
    def semantics(route):
        nodes = route["nodes"]
        positions = {n["node_id"]: i for i, n in enumerate(nodes)}
        return {"nodes": [{k: v for k, v in n.items() if k not in {"node_id", "allocation_group"}}
                          for n in nodes],
                "edges": sorted((positions[e["from_node_id"]], positions[e["to_node_id"]], e["relation"])
                                for e in route["edges"])}
    require(main["route_id"] != alternative["route_id"]
            and (digest(semantics(main)) != digest(semantics(alternative))
                 or (not main["nodes"] and not alternative["nodes"] and main["why"] != alternative["why"]
                     and bool(value["questions"]))), "identical-editorial-alternative", "route")
    clean(value, terms)
    return found, routes


def existing_bundles(ledger):
    """Read committed v2 receipts and legacy reservations without initializing storage."""
    folder = ledger.runtime("editorial", exists=False)
    records, reservations = {}, []
    if not folder.exists():
        return records, reservations
    for path in sorted(folder.glob("v2/*/*/complete.json")):
        path = safe_path(ledger.workspace, str(path.relative_to(ledger.workspace)))
        receipt = read_json(path)
        shape(receipt, {"topic_id", "bundle_hash", "source_hash", "files_hash", "previous_bundle_hash",
                        "artifact_ids", "pending_node_ids", "manifest_hash", "queue_hash"},
              {"private_lessons_hash"})
        sha(receipt["bundle_hash"], "bundle_hash")
        identifier(receipt["topic_id"], "topic_id")
        require(path.parent.name == receipt["bundle_hash"] and path.parent.parent.name == receipt["topic_id"],
                "invalid-editorial-receipt", "receipt")
        manifest = read_json(ledger.runtime(str(path.parent.relative_to(ledger.home)) + "/private-manifest.json",
                                           exists=True))
        queue = read_json(ledger.runtime(str(path.parent.relative_to(ledger.home)) + "/review-queue.json",
                                        exists=True))
        policy = ledger.config.get("editorial_policy")
        shape(policy, {"destination_root"})
        expected_destination = (policy["destination_root"] + "/v2/" + receipt["topic_id"]
                                + "/" + receipt["bundle_hash"])
        require(manifest.get("destination") == expected_destination,
                "invalid-editorial-receipt", "destination")
        if "private_lessons_hash" in receipt:
            sha(receipt["private_lessons_hash"], "private_lessons_hash")
            original = ledger.runtime(str(path.parent.relative_to(ledger.home)) + "/private-lessons.md",
                                      exists=True).read_bytes().decode("utf-8")
            require(digest(original) == receipt["private_lessons_hash"],
                    "tampered-private-lesson", "receipt")
        require(digest(manifest) == receipt["manifest_hash"] and digest(queue) == receipt["queue_hash"]
                and digest(queue) == receipt["bundle_hash"]
                and manifest["result_hash"] == receipt["bundle_hash"]
                and manifest["request_hash"] == digest(manifest["request"])
                and queue["request_hash"] == manifest["request_hash"]
                and queue["editorial_schema_version"] == 2 and queue["state"] == "draft-only"
                and queue["publication_authorized"] is False and queue["model_calls"] == 0
                and queue["package"]["source_hash"] == receipt["source_hash"]
                and queue["package"]["package_hash"] == digest({k: v for k, v in queue["package"].items()
                                                               if k != "package_hash"})
                and queue["topic_revision"] == manifest["request"]["topic"]["revision"]
                and queue["decision_hash"] == digest(manifest["request"]["decision"])
                and queue["source_hash"] == receipt["source_hash"]
                and queue["files_hash"] == receipt["files_hash"]
                and digest(queue["files"]) == receipt["files_hash"]
                and queue["topic_id"] == receipt["topic_id"]
                and queue["previous_bundle_hash"] == receipt["previous_bundle_hash"]
                and [d["artifact_id"] for d in queue["artifacts"]] == receipt["artifact_ids"]
                and queue["pending_node_ids"] == receipt["pending_node_ids"],
                "invalid-editorial-receipt", "receipt")
        for name, content in queue["files"].items():
            require(name.endswith(".md") and name == name.split("/")[-1],
                    "invalid-editorial-receipt", "file")
            target = safe_path(ledger.workspace, manifest["destination"] + "/" + name)
            require(target.read_bytes() == content.encode("utf-8"), "tampered-editorial-artifact", "file")
        records[receipt["bundle_hash"]] = {"receipt": receipt, "queue": queue, "manifest": manifest}
    by_topic = {}
    for key, row in records.items():
        topic = row["receipt"]["topic_id"]
        by_topic.setdefault(topic, []).append(key)
    heads = {}
    for topic, keys in by_topic.items():
        parents = [records[key]["receipt"]["previous_bundle_hash"] for key in keys]
        require(parents.count(None) == 1 and len([p for p in parents if p is not None])
                == len(set(p for p in parents if p is not None)), "invalid-editorial-chain", "topic")
        for parent in parents:
            require(parent is None or parent in keys, "invalid-editorial-chain", "predecessor")
        candidates = set(keys) - set(parents)
        require(len(candidates) == 1, "invalid-editorial-chain", "head")
        head = candidates.pop()
        seen, current = set(), head
        while current is not None:
            require(current not in seen, "invalid-editorial-chain", "cycle")
            seen.add(current)
            current = records[current]["receipt"]["previous_bundle_hash"]
        require(seen == set(keys), "invalid-editorial-chain", "topic")
        heads[topic] = head
        reservations.extend({"topic_id": topic, "bundle_hash": head, **node}
                            for node in records[head]["queue"]["route"]["nodes"] if node["slot_id"] is not None)
    # Legacy output folder is editorial/<topic>/<hash>/; v2 has an extra namespace.
    for path in sorted(folder.glob("*/*/review-queue.json")):
        path = safe_path(ledger.workspace, str(path.relative_to(ledger.workspace)))
        saved = read_json(path)
        require(saved.get("schema_version") == 1, "invalid-legacy-editorial-queue", "queue")
        for draft in saved["drafts"]:
            reservations.append({"topic_id": saved["topic_id"], "bundle_hash": path.parent.name,
                                 "slot_id": draft["slot_id"], "language": draft["language"],
                                 "allocation_group": "legacy", "brand_id": draft["brand_id"]})
    return {"records": records, "heads": heads}, reservations


def cta(value, ledger, request):
    if value is None:
        return
    shape(value, {"text", "target_kind", "target_url", "verification_ref", "verified_at"})
    safe_text(value["text"], "cta-text")
    if value["target_kind"] == "none":
        require(all(value[k] is None for k in ("target_url", "verification_ref", "verified_at")),
                "invalid-editorial-cta", "cta")
        return
    require(value["target_kind"] == "existing-url", "invalid-editorial-cta", "cta")
    url = value["target_url"]
    safe_text(url, "url")
    require("{{" not in url and "}}" not in url, "unsafe-editorial-url", "cta")
    public_url(url)
    ref = value["verification_ref"]
    validate_source(ref, ledger.config)
    require(ref in [c["source_ref"] for c in request["claims"]], "unlinked-cta-proof", "cta")
    instant(value["verified_at"], "verified_at")


def render_artifact(artifact, node, package, ledger, request, decision_hash, related_blog):
    shape(artifact, {"artifact_id", "node_id", "claim_ids", "title", "body", "format_fields", "approval"})
    identifier(artifact["artifact_id"], "artifact_id")
    safe_text(artifact["title"], "title")
    safe_text(artifact["body"], "body")
    ids(artifact["claim_ids"], "claim_ids", empty=False)
    available = {c["claim_id"]: c for c in package["claims"]}
    require(set(artifact["claim_ids"]) == set(node["claim_ids"])
            and set(artifact["claim_ids"]) <= set(available), "held-or-missing-claim", "artifact")
    fields = artifact["format_fields"]
    shape(fields, FORMAT_FIELDS[node["format"]])
    for key, val in fields.items():
        if key in {"key_takeaways", "outline", "scenes"}:
            texts(items(val, key, empty=False), key)
        elif key == "assets_needed":
            for asset in items(val, key):
                shape(asset, {"kind", "description", "permission_state", "evidence_claim_ids"})
                safe_text(asset["description"], "description")
                require(asset["kind"] in {"screen-demo", "illustration", "diagram", "recording", "other"}
                        and asset["permission_state"] in {"unknown", "review-required", "approved"},
                        "invalid-asset-need", "asset")
                ids(asset["evidence_claim_ids"], "evidence_claim_ids")
                require(set(asset["evidence_claim_ids"]) <= set(artifact["claim_ids"]),
                        "unlinked-asset-claim", "asset")
                require(asset["permission_state"] == "approved" or node["slot_id"] is None,
                        "concept-not-ready-for-slot", "asset")
        elif key == "cta":
            cta(val, ledger, request)
        elif key == "additional_value" and val is None:
            require(not related_blog, "newsletter-additional-value-required", "newsletter")
        else:
            safe_text(val, key)
    if node["format"] == "blog-article":
        identifier(fields["proposed_slug"], "proposed_slug")
    terms = [t for claim in request["claims"] for t in claim["sensitive_terms"]]
    clean({"title": artifact["title"], "body": artifact["body"], "format_fields": fields}, terms)
    used = set()
    def render(value):
        if isinstance(value, str):
            tokens = CLAIM_TOKEN.findall(value)
            used.update(tokens)
            require(set(tokens) <= set(artifact["claim_ids"]), "unmapped-draft-claim", "artifact")
            output = CLAIM_TOKEN.sub(lambda m: available[m[1]]["text"], value)
            require("{{claim:" not in output, "unmapped-draft-claim", "artifact")
            clean(output, terms)
            return output
        if isinstance(value, list):
            return [render(x) for x in value]
        if isinstance(value, dict):
            return {k: render(v) for k, v in value.items()}
        return value
    # Never render evidence refs/claim IDs into the shareable artifact.
    public_fields = {}
    for key, val in fields.items():
        if key == "cta" and val is not None:
            public_fields[key] = {k: val[k] for k in ("text", "target_kind", "target_url")}
        elif key == "assets_needed":
            public_fields[key] = [{k: a[k] for k in ("kind", "description", "permission_state")} for a in val]
        else:
            public_fields[key] = val
    title, body, rendered_fields = render(artifact["title"]), render(artifact["body"]), render(public_fields)
    require(used == set(artifact["claim_ids"]), "unmapped-draft-claim", "artifact")
    basis = {"source_hash": package["source_hash"], "decision_hash": decision_hash,
             "node": node, "title": title, "body": body, "format_fields": rendered_fields,
             "metadata_hash": digest(fields), "claim_hashes": {cid: available[cid]["source_claim_hash"]
                                                             for cid in artifact["claim_ids"]}}
    content_hash, review = digest(basis), "needs-review"
    approval = artifact["approval"]
    if approval is not None:
        shape(approval, APPROVAL_FIELDS)
        owner_record(approval)
        require(approval["content_hash"] == content_hash and approval["source_hash"] == package["source_hash"]
                and approval["decision_hash"] == decision_hash
                and all(approval[k] == node[k] for k in ("brand_id", "language", "format"))
                and approval["purpose"] == "editorial-draft-v2"
                and all(available[cid]["state"] == "public-ready" for cid in artifact["claim_ids"]),
                "draft-approval-required", "artifact")
        review = "owner-reviewed-draft"
    lines = ["# " + md(title), "", "Local draft; publication not authorized. Review: " + review,
             "", md(body), ""]
    for key, val in rendered_fields.items():
        if val is None:
            continue
        lines.extend(["## " + key.replace("_", " ").title(), ""])
        if isinstance(val, str):
            lines.append(md(val))
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, dict):
                    lines.append("- " + md(item["description"]) + " (" + item["permission_state"] + ")")
                else:
                    lines.append("- " + md(item))
        else:
            lines.append(md(val["text"]))
            if val["target_url"]:
                lines.append(md(val["target_url"]))
        lines.append("")
    return {**basis, "artifact_id": artifact["artifact_id"], "node_id": node["node_id"],
            "content_hash": content_hash, "review_state": review}, "\n".join(lines) + "\n"


def bundle(ledger, request):
    require(editorial_version(request) == 2, "unsupported-editorial-version", "request")
    shape(request, REQUEST_FIELDS)
    package = prepare(ledger, {k: request[k] for k in PREPARE_FIELDS})
    terms = [t for claim in request["claims"] for t in claim["sensitive_terms"]]
    assessment, maps = recommendation(request["recommendation"], package, terms)
    items(request["artifacts"], "artifacts", limit=200)
    previous = request["previous_bundle_hash"]
    if previous is not None:
        sha(previous, "previous_bundle_hash")
    existing, reservations = existing_bundles(ledger)
    heads = existing.get("heads", {})
    require(previous == heads.get(package["topic"]["topic_id"]), "stale-editorial-predecessor", "topic")
    records = existing.get("records", {})
    if previous:
        require(package["topic"]["revision"] > records[previous]["queue"]["topic_revision"],
                "stale-topic-revision", "topic")
    decision = request["decision"]
    base = {"editorial_schema_version": 2, "topic_id": package["topic"]["topic_id"],
            "topic_revision": package["topic"]["revision"], "package": package,
            "source_hash": package["source_hash"], "request_hash": digest(request),
            "previous_bundle_hash": previous, "model_calls": 0, "publication_authorized": False}
    if decision is None:
        require(not request["artifacts"], "route-decision-required", "artifacts")
        return {**base, "state": "recommendation-needs-decision",
                "recommendation": request["recommendation"]}
    shape(decision, DECISION_FIELDS)
    identifier(decision["decision_id"], "decision_id")
    owner_record(decision)
    safe_text(decision["reason"], "reason")
    clean(decision, terms)
    require(decision["mode"] in {"accept-primary", "accept-alternative"}, "invalid-route-decision", "mode")
    field = "primary" if decision["mode"] == "accept-primary" else "alternative"
    route = request["recommendation"][field]
    require(decision["recommendation_hash"] == digest(request["recommendation"])
            and decision["source_hash"] == package["source_hash"]
            and decision["selected_route_id"] == route["route_id"] and decision["route_hash"] == digest(route)
            and decision["previous_bundle_hash"] == previous, "stale-route-decision", "decision")
    nodes, dependencies = maps[field]
    available = {c["claim_id"] for c in package["claims"]}
    for node in nodes.values():
        row = assessment[node["brand_id"], node["format"]]
        require(row["fit"] not in {"defer", "unsuitable"} and row["readiness"] not in BLOCKED_READINESS
                and set(node["claim_ids"]) <= available, "held-editorial-node", "node")
        if node["format"].endswith("-concept") and row["evidence_gaps"]:
            require(node["slot_id"] is None and row["readiness"] == "needs-review",
                    "concept-not-ready-for-slot", "node")
    reserved = [r for r in reservations if not (previous and r["bundle_hash"] == previous)]
    for node in nodes.values():
        if node["slot_id"]:
            require(not any(r["slot_id"] == node["slot_id"] for r in reserved),
                    "capacity-conflict", "slot")
    values = [n["effort_minutes"] for n in nodes.values()]
    budget = package["capacity"]["effort_budget_minutes"]
    known = sum(v for v in values if v is not None)
    unknown = budget is None or any(v is None for v in values)
    scheduled = any(n["slot_id"] for n in nodes.values())
    if scheduled:
        require(not unknown, "capacity-unknown", "schedule")
        require(known <= budget, "capacity-conflict", "schedule")
    capacity = {"estimated_minutes_known": known, "budget_minutes": budget,
                "state": "capacity-unknown" if unknown else "capacity-conflict" if known > budget else "fits",
                "question": "Confirm effort and budget before scheduling." if unknown else None}
    artifacts_by_node, artifact_ids = {}, set()
    for artifact in request["artifacts"]:
        shape(artifact, {"artifact_id", "node_id", "claim_ids", "title", "body", "format_fields", "approval"})
        require(artifact["node_id"] in nodes and artifact["node_id"] not in artifacts_by_node
                and artifact["artifact_id"] not in artifact_ids, "duplicate-or-unknown-artifact", "artifact")
        artifacts_by_node[artifact["node_id"]] = artifact
        artifact_ids.add(artifact["artifact_id"])
    output, files, completed, visiting = [], {}, set(), set()
    decision_hash = digest(decision)
    rendered = {}
    for nid, artifact in artifacts_by_node.items():
        related_blog = any((nodes[e["from_node_id"]]["format"] == "blog-article" and e["to_node_id"] == nid)
                           or (nodes[e["to_node_id"]]["format"] == "blog-article" and e["from_node_id"] == nid)
                           for e in route["edges"])
        # Validate even blocked children: dependencies must not hide unsafe input.
        rendered[nid] = render_artifact(artifact, nodes[nid], package, ledger, request,
                                        decision_hash, related_blog)
    def produce(nid):
        if nid in completed:
            return True
        if nid not in artifacts_by_node:
            return False
        if nid in visiting:
            return False
        visiting.add(nid)
        if not all(produce(parent) for parent in dependencies[nid]):
            visiting.remove(nid)
            return False
        value, content = rendered[nid]
        output.append(value)
        files[value["artifact_id"] + ".md"] = content
        completed.add(nid)
        visiting.remove(nid)
        return True
    for nid in nodes:
        produce(nid)
    pending = sorted(set(nodes) - completed)
    return {**base, "state": "draft-only", "recommendation": request["recommendation"],
            "decision_hash": decision_hash, "route": route, "capacity": capacity,
            "reservation_snapshot": reserved, "artifacts": output, "files": files,
            "files_hash": digest(files), "pending_node_ids": pending,
            "review_state": "owner-reviewed-draft" if not pending and output
            and all(a["review_state"] == "owner-reviewed-draft" for a in output) else "needs-review"}


def persist_bundle(ledger, request, expected_hash, *, owner_approved=False, failpoint=None):
    require(owner_approved, "owner-approval-required", "editorial")
    sha(expected_hash, "expected_hash")
    policy = ledger.config.get("editorial_policy")
    shape(policy, {"destination_root"})
    root = safe_path(ledger.workspace, policy["destination_root"], must_exist=False)
    require(root.is_dir(), "unconfigured-editorial-destination", "editorial")
    def stop(point):
        require(failpoint != point, "injected-failure", point)
    with ledger.lock():
        ledger.check_loaded()
        require(editorial_version(request) == 2, "unsupported-editorial-version", "write")
        shape(request, REQUEST_FIELDS)
        topic = identifier(request["topic"]["topic_id"], "topic_id")
        folder = "editorial/v2/" + topic + "/" + expected_hash + "/"
        receipt_path = ledger.runtime(folder + "complete.json")
        if receipt_path.exists():
            records, _ = existing_bundles(ledger)
            saved = records["records"].get(expected_hash)
            require(saved is not None and saved["manifest"]["request_hash"] == digest(request),
                    "stale-approval", "retry")
            # A retry still checks live proof; it does not bless stale committed content.
            package = prepare(ledger, {k: request[k] for k in PREPARE_FIELDS})
            require(package["package_hash"] == saved["queue"]["package"]["package_hash"],
                    "stale-approval", "retry")
            return {"state": "draft-only", "bundle_hash": expected_hash, "publication_authorized": False}
        result = bundle(ledger, request)
        require(result["state"] == "draft-only", "route-decision-required", "write")
        require(digest(result) == expected_hash, "stale-approval", "editorial")
        destination = policy["destination_root"] + "/v2/" + topic + "/" + expected_hash
        manifest = {"request": request, "request_hash": digest(request), "result_hash": expected_hash,
                    "destination": destination}
        originals = review_source(ledger, {k: request[k] for k in PREPARE_FIELDS})["markdown"]
        writes = [(ledger.runtime(folder + "private-manifest.json"), canonical_bytes(manifest)),
                  (ledger.runtime(folder + "private-lessons.md"), originals.encode("utf-8"))]
        writes += [(safe_path(ledger.workspace, destination + "/" + name, must_exist=False),
                    content.encode("utf-8")) for name, content in result["files"].items()]
        writes += [(ledger.runtime(folder + "review-queue.json"), canonical_bytes(result))]
        for index, (path, data) in enumerate(writes):
            atomic_write(path, data, immutable=True)
            stop("after-write-" + str(index))
        stop("before-receipt")
        receipt = {"topic_id": topic, "bundle_hash": expected_hash, "source_hash": result["source_hash"],
                   "files_hash": result["files_hash"], "previous_bundle_hash": request["previous_bundle_hash"],
                   "artifact_ids": [a["artifact_id"] for a in result["artifacts"]],
                   "pending_node_ids": result["pending_node_ids"], "manifest_hash": digest(manifest),
                   "queue_hash": digest(result), "private_lessons_hash": digest(originals)}
        atomic_write(receipt_path, canonical_bytes(receipt), immutable=True)
        stop("after-receipt")
        return {"state": "draft-only", "bundle_hash": expected_hash,
                "relative_folder": destination, "publication_authorized": False}
