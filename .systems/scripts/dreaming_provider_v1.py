"""Versioned, pure Dreaming evidence protocol. Metadata never grants authority."""
import hashlib
import json
import re
from datetime import datetime
from pathlib import PurePosixPath

VERSION = 1
LEVELS = {"observed", "owner-attested", "plan", "inference", "unknown"}
CLASSES = {"work", "source", "personal-trends", "secret", "raw-personal", "raw-export", "attachment", "unknown"}
STATES = {"reviewed", "reused-unchanged", "pending", "unsupported", "excluded", "blocked", "missing"}
CONSUMERS = {"ledger", "documentation", "report", "tax-evidence", "editorial"}


class ProtocolError(ValueError):
    """Only this safe category, never an input value, belongs in diagnostics."""
    def __init__(self, category):
        self.category = category
        super().__init__(category)


def require(condition, category):
    if not condition:
        raise ProtocolError(category)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def oneof(value, choices):
    return isinstance(value, str) and value in choices


def sha(value):
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value), "invalid-fingerprint")
    return value


def slug(value):
    require(isinstance(value, str) and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value), "invalid-identity")
    return value


def relative(value):
    require(isinstance(value, str) and value and "\\" not in value and "\x00" not in value,
            "unsafe-relative-path")
    path = PurePosixPath(value)
    require(not path.is_absolute() and not any(p in {"", ".", ".."} for p in value.split("/"))
            and not re.match(r"[A-Za-z]:", value), "unsafe-relative-path")
    return value


def timestamp(value):
    try:
        require(isinstance(value, str), "invalid-timestamp")
        date = datetime.fromisoformat(value.replace("Z", "+00:00"))
        require(date.tzinfo is not None and date.utcoffset() is not None, "invalid-timestamp")
    except (ValueError, TypeError):
        raise ProtocolError("invalid-timestamp") from None
    return value


def shape(value, required, optional=()):
    require(isinstance(value, dict) and set(required) <= set(value)
            and set(value) <= set(required) | set(optional), "invalid-object-fields")


def integer(value, minimum=0):
    require(type(value) is int and value >= minimum, "invalid-integer")


def unique_json(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate-json-key")
        result[key] = value
    return result


def parse_json(text):
    try:
        return json.loads(text, object_pairs_hook=unique_json,
                          parse_constant=lambda _: (_ for _ in ()).throw(ProtocolError("nonfinite-json")))
    except (ValueError, TypeError, RecursionError):
        raise ProtocolError("invalid-json") from None


def source_ref(value):
    shape(value, {"source_root_id", "relative_path", "project_id", "owner_workspace_id", "sha256",
                  "byte_count", "observed_at", "fact_date", "evidence_level", "source_class"})
    slug(value["source_root_id"])
    slug(value["owner_workspace_id"])
    slug(value["project_id"])
    relative(value["relative_path"])
    sha(value["sha256"])
    integer(value["byte_count"])
    timestamp(value["observed_at"])
    require(oneof(value["evidence_level"], LEVELS) and oneof(value["source_class"], CLASSES), "invalid-evidence-kind")
    if value["fact_date"] != "unknown":
        require(isinstance(value["fact_date"], str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value["fact_date"]),
                "invalid-fact-date")
        try:
            datetime.strptime(value["fact_date"], "%Y-%m-%d")
        except ValueError:
            raise ProtocolError("invalid-fact-date") from None
    return value


def capability(value):
    shape(value, {"interface_version", "producer_version", "supported_source_kinds", "supported_classes",
                  "source_fingerprints"})
    require(type(value["interface_version"]) is int and value["interface_version"] == VERSION,
            "unsupported-interface")
    require(value["producer_version"] == "dreaming-evidence-v1", "unsupported-producer")
    require(isinstance(value["supported_source_kinds"], list) and all(isinstance(x,str) for x in value["supported_source_kinds"]) and set(value["supported_source_kinds"]) == {"workflow", "repository", "workspace"},
            "unsupported-source-kinds")
    require(isinstance(value["supported_classes"], list) and all(isinstance(x,str) for x in value["supported_classes"]) and set(value["supported_classes"]) == {"work", "source", "personal-trends"},
            "unsupported-source-classes")
    require(isinstance(value["source_fingerprints"], dict) and value["source_fingerprints"], "missing-capability-binding")
    for path, fingerprint in value["source_fingerprints"].items():
        relative(path)
        sha(fingerprint)
    return value


def read_receipt(value, ref, policy, cap):
    shape(value, {"source_hash", "byte_count", "policy_digest", "coverage", "receipt_id", "capability_digest", "chunk_map"})
    require(value["source_hash"] == ref["sha256"] and value["byte_count"] == ref["byte_count"]
            and type(value["byte_count"]) is int and value["policy_digest"] == policy
            and value["capability_digest"] == digest(cap) and value["coverage"] == "complete", "read-binding-mismatch")
    require(value["receipt_id"] == digest([ref, policy, digest(cap)]), "read-receipt-mismatch")
    require(isinstance(value["chunk_map"], list) and value["chunk_map"], "missing-chunks")
    offset = 0
    for chunk in value["chunk_map"]:
        shape(chunk, {"chunk_id", "start", "end", "sha256"})
        integer(chunk["start"]); integer(chunk["end"]); sha(chunk["sha256"])
        require(chunk["start"] == offset and chunk["end"] >= offset and chunk["end"] <= ref["byte_count"], "chunk-coverage-mismatch")
        require(chunk["chunk_id"] == digest([ref["source_root_id"], ref["relative_path"], ref["sha256"], chunk["start"], chunk["end"]]), "chunk-identity-mismatch")
        require(ref["byte_count"] == 0 or chunk["end"] > offset, "empty-chunk")
        offset = chunk["end"]
    require(offset == ref["byte_count"], "incomplete-read")


def analysis_receipt(value, receipt, policy, known_hashes):
    shape(value, {"analyzer", "policy_digest", "read_receipt_ids", "covered_chunks", "findings", "coverage", "unresolved_conflicts", "receipt_id"})
    shape(value["analyzer"], {"id", "version", "policy_digest"})
    slug(value["analyzer"]["id"]); slug(value["analyzer"]["version"]); sha(value["analyzer"]["policy_digest"])
    require(value["receipt_id"] == digest({k:v for k,v in value.items() if k != "receipt_id"}) and value["policy_digest"] == policy, "analysis-receipt-mismatch")
    require(isinstance(value["read_receipt_ids"], list) and receipt["receipt_id"] in value["read_receipt_ids"], "uncited-read")
    require(isinstance(value["covered_chunks"], list) and all(isinstance(x,str) for x in value["covered_chunks"])
            and {c["chunk_id"] for c in receipt["chunk_map"]} <= set(value["covered_chunks"]), "incomplete-analysis-chunks")
    require(value["coverage"] == "complete" and value["unresolved_conflicts"] == [] and isinstance(value["findings"],list), "incomplete-analysis")
    for finding in value["findings"]:
        shape(finding, {"finding_id", "source_hashes", "facts", "inferences", "unknowns", "native_state", "native_quality"})
        slug(finding["finding_id"])
        require(isinstance(finding["source_hashes"],list) and finding["source_hashes"]
                and all(isinstance(h,str) and h in known_hashes for h in finding["source_hashes"]), "uncited-finding")
        for label in ["facts", "inferences", "unknowns"]:
            require(isinstance(finding[label],list) and all(isinstance(x,str) for x in finding[label]), "invalid-finding-text")
        require(oneof(finding["native_state"], {"new","repeated","promoted","rejected","obsolete","unknown"})
                and oneof(finding["native_quality"], {"verified-current","stale","unknown"}), "invalid-native-state")


def _envelope(value):
    shape(value, {"interface_version", "owner_workspace_id", "capability", "policy_digest", "inventory",
                  "evidence", "result", "coverage"})
    require(type(value["interface_version"]) is int and value["interface_version"] == VERSION, "unsupported-interface")
    slug(value["owner_workspace_id"])
    capability(value["capability"])
    sha(value["policy_digest"])
    require(oneof(value["result"], {"complete", "partial", "blocked"}), "invalid-result")
    require(isinstance(value["inventory"], list) and isinstance(value["evidence"], list), "invalid-evidence-list")
    seen = set()
    known_hashes = {row["source_ref"]["sha256"] for row in value["inventory"] if isinstance(row,dict) and isinstance(row.get("source_ref"),dict) and isinstance(row["source_ref"].get("sha256"),str)}
    for item in value["inventory"]:
        shape(item, {"source_root_id", "relative_path", "project_id", "disposition", "reason_code",
                     "source_ref", "read_receipt", "analysis_receipt"})
        slug(item["source_root_id"]); relative(item["relative_path"]); slug(item["project_id"])
        identity = (item["source_root_id"], item["relative_path"])
        require(identity not in seen, "duplicate-inventory-source")
        seen.add(identity)
        require(oneof(item["disposition"], STATES) and isinstance(item["reason_code"], str), "invalid-disposition")
        if item["source_ref"] is not None:
            ref = source_ref(item["source_ref"])
            require(ref["owner_workspace_id"] == value["owner_workspace_id"] and
                    (ref["source_root_id"], ref["relative_path"], ref["project_id"]) ==
                    (item["source_root_id"], item["relative_path"], item["project_id"]), "source-owner-mismatch")
        if item["read_receipt"] is not None:
            require(item["source_ref"] is not None, "unbound-read-receipt")
            read_receipt(item["read_receipt"], item["source_ref"], value["policy_digest"], value["capability"])
        if item["disposition"] in {"reviewed", "reused-unchanged"}:
            require(item["source_ref"] is not None and isinstance(item["read_receipt"], dict)
                    and isinstance(item["analysis_receipt"], dict), "missing-analysis-evidence")
            analysis_receipt(item["analysis_receipt"], item["read_receipt"], value["policy_digest"], known_hashes)
        if item["disposition"] in {"excluded", "blocked", "missing", "unsupported"}:
            require(item["source_ref"] is None and item["read_receipt"] is None
                    and item["analysis_receipt"] is None, "forbidden-read-receipt")
    readable = {(x["source_root_id"], x["relative_path"]): x for x in value["inventory"] if x["disposition"] in {"reviewed", "reused-unchanged"}}
    ids = set()
    for item in value["evidence"]:
        shape(item, {"evidence_id", "source_ref", "native_kind", "native_state", "native_quality",
                     "semantic_summary", "limitations"})
        slug(item["evidence_id"])
        require(item["evidence_id"] not in ids, "duplicate-evidence-id"); ids.add(item["evidence_id"])
        ref = source_ref(item["source_ref"])
        require(ref["owner_workspace_id"] == value["owner_workspace_id"] and
                (ref["source_root_id"], ref["relative_path"]) in readable and readable[(ref["source_root_id"], ref["relative_path"])]["source_ref"] == ref, "unbound-evidence")
        require(oneof(item["native_state"], {"new", "repeated", "promoted", "rejected", "obsolete", "unknown"})
                and oneof(item["native_quality"], {"verified-current", "stale", "unknown"}), "invalid-native-state")
        require(isinstance(item["semantic_summary"], str) and isinstance(item["limitations"], list), "invalid-evidence-summary")
        require(isinstance(item["native_kind"],str) and all(isinstance(x,str) for x in item["limitations"]), "invalid-evidence-kind")
    shape(value["coverage"], {"enumeration_complete", "counts"})
    require(type(value["coverage"]["enumeration_complete"]) is bool, "invalid-coverage")
    require(isinstance(value["coverage"]["counts"], dict) and set(value["coverage"]["counts"]) == STATES,
            "invalid-coverage-counts")
    expected = {key: sum(row["disposition"] == key for row in value["inventory"]) for key in STATES}
    require(value["coverage"]["counts"] == expected and all(type(n) is int for n in value["coverage"]["counts"].values()), "coverage-mismatch")
    if value["result"] == "complete":
        require(value["coverage"]["enumeration_complete"] and not any(expected[k] for k in
                {"pending", "unsupported", "blocked", "missing"}), "false-complete")
    return value


def local_capabilities(root):
    """Caller compares these actual bytes with its accepted implementation binding."""
    from pathlib import Path
    root = Path(root)
    paths = [".systems/scripts/dreaming_evidence.py", ".systems/scripts/resolve-workflow-env"]
    for rel in [".systems/scripts/dreaming_evidence_reader.py", ".systems/scripts/dreaming_guard.py"]:
        if (root / rel).is_file(): paths.append(rel)
    for rel in [".systems/scripts/dreaming_native.py", ".systems/scripts/lib/qa-evidence.py", ".systems/scripts/lib/capture-record.py"]:
        if (root / rel).is_file(): paths.append(rel)
    return capability({"interface_version":1,"producer_version":"dreaming-evidence-v1",
        "supported_source_kinds":["workflow","repository","workspace"],"supported_classes":["work","source","personal-trends"],
        "source_fingerprints":{rel:hashlib.sha256((root/rel).read_bytes()).hexdigest() for rel in paths}})


def envelope(value):
    try:return _envelope(value)
    except (KeyError,TypeError,IndexError,AttributeError):raise ProtocolError("invalid-evidence-shape") from None
