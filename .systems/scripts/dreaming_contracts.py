"""Consumer v1: pure validation; readiness and metadata never authorize effects."""
import uuid
from dreaming_provider_v1 import (ProtocolError, require, shape, slug, sha, source_ref,
                                 capability, envelope, digest, oneof, CONSUMERS)

READINESS = {"ready-for-review", "needs-evidence", "needs-owner-decision", "not-applicable"}


def consume(value, actual_capability, accepted_fingerprints):
    envelope(value); capability(actual_capability)
    require(value["capability"] == actual_capability, "producer-drift")
    require(actual_capability["source_fingerprints"] == accepted_fingerprints, "unreviewed-producer")
    return value


def candidate(value):
    shape(value, {"schema_version", "candidate_id", "revision", "predecessor_hash", "owner_workspace_id",
                  "project_id", "intent", "case_ref", "work_id", "evidence_refs", "facts", "inferences",
                  "unknowns", "consumer_readiness", "privacy_state", "prior_decision_ref"})
    require(type(value["schema_version"]) is int and value["schema_version"] == 1, "unsupported-candidate")
    try: uuid.UUID(value["candidate_id"])
    except (ValueError, TypeError, AttributeError): raise ProtocolError("invalid-candidate-id") from None
    require(type(value["revision"]) is int and value["revision"] > 0, "invalid-revision")
    require((value["revision"] == 1) == (value["predecessor_hash"] is None), "missing-predecessor")
    if value["predecessor_hash"] is not None: sha(value["predecessor_hash"])
    slug(value["owner_workspace_id"]); slug(value["project_id"])
    require(oneof(value["intent"], {"new-case", "enrich-case"}), "invalid-intent")
    for field in ("case_ref", "work_id", "prior_decision_ref"):
        require(value[field] is None or isinstance(value[field], str), "invalid-case-identity")
    require(isinstance(value["evidence_refs"], list), "invalid-evidence-list")
    for ref in value["evidence_refs"]:
        source_ref(ref)
        require(ref["owner_workspace_id"] == value["owner_workspace_id"] and ref["project_id"] == value["project_id"], "candidate-owner-mismatch")
    for label, level in [("facts", "observed"), ("inferences", "inference"), ("unknowns", "unknown")]:
        require(isinstance(value[label], list), "invalid-claims")
        for claim in value[label]:
            shape(claim, {"text", "source_hashes", "evidence_level"})
            require(isinstance(claim["text"], str) and isinstance(claim["source_hashes"], list), "invalid-claim")
            require(oneof(claim["evidence_level"], {"observed", "owner-attested"} if label == "facts" else {level}), "claim-level-mismatch")
            allowed = {r["sha256"] for r in value["evidence_refs"]}
            require(all(isinstance(h, str) and h in allowed for h in claim["source_hashes"]), "unbound-claim")
            require(label == "unknowns" or claim["source_hashes"], "uncited-claim")
    readiness = value["consumer_readiness"]
    require(isinstance(readiness, dict) and set(readiness) == CONSUMERS, "missing-consumer")
    for item in readiness.values():
        shape(item, {"state", "missing_fields", "evidence_hashes"})
        require(oneof(item["state"], READINESS) and isinstance(item["missing_fields"], list)
                and all(isinstance(x, str) for x in item["missing_fields"]), "invalid-readiness")
        require(isinstance(item["evidence_hashes"], list) and all(h in {r["sha256"] for r in value["evidence_refs"]} for h in item["evidence_hashes"]), "unbound-readiness")
        require(item["state"] != "ready-for-review" or not item["missing_fields"], "false-ready")
    require(oneof(value["privacy_state"], {"private", "review-required", "reviewed-projection"}), "invalid-privacy-state")
    return value
