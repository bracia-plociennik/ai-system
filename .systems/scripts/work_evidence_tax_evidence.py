"""Private evidence register, not IP eligibility or tax advice."""
from __future__ import annotations

import re
import os
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path

from work_evidence import (require, shape, version, identifier, text, choice, iso_date,
                           sha, digest, canonical_bytes, read_json, safe_path, file_hash,
                           instant, validate_source)
from work_evidence_ledger import Ledger, atomic_write
from work_evidence_docs import assemble

STATES = {"asserted", "verified", "advisor-assessed"}
DECIMAL = re.compile(r"(?:0|[1-9][0-9]{0,23})(?:\.[0-9]{1,12})?\Z")


def amount(value, *, nullable=False):
    if nullable and value is None:
        return None
    require(isinstance(value, str) and DECIMAL.fullmatch(value),
            "invalid-decimal", "amount")
    try:
        value = Decimal(value)
        require(value.is_finite() and value >= 0, "invalid-decimal", "amount")
        return value
    except InvalidOperation:
        require(False, "invalid-decimal", "amount")


def decimal_string(value):
    return format(value, "f")


class TaxRegister:
    def __init__(self, workspace, taxpayer_id):
        identifier(taxpayer_id, "taxpayer_id")
        from local_paths import LocalPathError, resolve_path
        try:
            path = resolve_path(workspace, base=Path.cwd(), allow_relative=True)
        except LocalPathError:
            require(False, "invalid-workspace", "tax")
        require(path.is_dir() and not path.is_symlink(), "invalid-workspace", "workspace")
        self.workspace = path.resolve()
        self.home = self.workspace / "private-tax" / taxpayer_id
        for folder in (self.workspace / "private-tax", self.home):
            require(folder.is_dir() and not folder.is_symlink(), "unconfigured-private-store", "tax")
        require(self.home.stat().st_uid == os.getuid() and self.home.stat().st_mode & 0o077 == 0,
                "private-store-permissions-required", "tax")
        self.config_path = safe_path(self.home, "config.json")
        self.config = read_json(self.config_path)
        shape(self.config, {"schema_version", "taxpayer_id", "owner_workspace", "currencies",
                            "source_roots", "allowed_workspaces"})
        version(self.config)
        require(self.config["taxpayer_id"] == taxpayer_id, "taxpayer-conflict", "config")
        identifier(self.config["owner_workspace"], "owner_workspace")
        require(isinstance(self.config["currencies"], list) and self.config["currencies"]
                and all(value in {"PLN", "EUR", "USD"} for value in self.config["currencies"])
                and len(set(self.config["currencies"])) == len(self.config["currencies"]),
                "unsupported-currency-policy", "currencies")
        require(isinstance(self.config["allowed_workspaces"], dict)
                and self.config["allowed_workspaces"], "missing-owner-map", "allowed_workspaces")
        self.ledgers = {}
        for owner, root in self.config["allowed_workspaces"].items():
            identifier(owner, "owner_workspace")
            try:
                root = str(resolve_path(root, workspace=self.workspace))
            except LocalPathError:
                require(False, "invalid-root", "allowed_workspaces")
            require(isinstance(root, str) and Path(root).is_absolute(),
                    "invalid-root", "allowed_workspaces")
            ledger = Ledger(root)
            require(ledger.config["workspace_id"] == owner, "owner-conflict", "allowed_workspaces")
            self.ledgers[owner] = ledger
        require(self.config["owner_workspace"] in self.ledgers
                and self.ledgers[self.config["owner_workspace"]].workspace == self.workspace,
                "owner-conflict", "workspace")
        require(isinstance(self.config["source_roots"], dict) and self.config["source_roots"],
                "missing-root", "source_roots")
        for alias, relative in self.config["source_roots"].items():
            identifier(alias, "root_alias")
            require(safe_path(self.home, relative, must_exist=False).is_dir(),
                    "invalid-root", "tax_sources")
        self.loaded_hash = file_hash(self.config_path)

    def source(self, ref):
        shape(ref, {"root_alias", "relative_path", "sha256", "observed_at", "evidence_state"})
        require(ref["root_alias"] in self.config["source_roots"], "unknown-root", "tax_source")
        sha(ref["sha256"], "source_hash")
        instant(ref["observed_at"], "observed_at")
        choice(ref["evidence_state"], STATES, "evidence_state")
        root = safe_path(self.home, self.config["source_roots"][ref["root_alias"]], must_exist=False)
        path = safe_path(root, ref["relative_path"])
        require(file_hash(path) == ref["sha256"], "stale-source", "tax_source")
        return ref

    def sources(self, refs):
        require(isinstance(refs, list) and len(refs) <= 100, "invalid-list", "source_refs")
        for ref in refs:
            self.source(ref)

    def packet(self, bundle):
        require(file_hash(self.config_path) == self.loaded_hash, "stale-config", "tax")
        shape(bundle, {"schema_version", "taxpayer_id", "tax_year", "ip_items", "rights",
                       "finance", "allocations", "work_refs"})
        version(bundle)
        require(type(bundle["tax_year"]) is int and 1900 <= bundle["tax_year"] <= 2200,
                "invalid-year", "tax_year")
        gaps, ips, rights, finance, work = [], {}, {}, {}, {}
        if bundle["taxpayer_id"] != self.config["taxpayer_id"]:
            gaps.append({"category": "taxpayer-conflict", "id": "bundle"})
        for collection in ("ip_items", "rights", "finance", "allocations", "work_refs"):
            require(isinstance(bundle[collection], list) and len(bundle[collection]) <= 10000,
                    "invalid-list", collection)
        def owned(row, key):
            identifier(row[key], key)
            if row["taxpayer_id"] != self.config["taxpayer_id"]:
                gaps.append({"category": "taxpayer-conflict", "id": row[key]})
        for row in bundle["ip_items"]:
            shape(row, {"ip_id", "taxpayer_id", "rights_holder_id", "description"})
            owned(row, "ip_id")
            require(row["ip_id"] not in ips, "duplicate-identity", "ip_id")
            identifier(row["rights_holder_id"], "rights_holder_id")
            text(row["description"], "description")
            ips[row["ip_id"]] = row
            if row["rights_holder_id"] != self.config["taxpayer_id"]:
                gaps.append({"category": "rights-holder-review-required", "id": row["ip_id"]})
        for row in bundle["rights"]:
            shape(row, {"right_id", "ip_id", "taxpayer_id", "kind", "effective_start",
                        "end_exclusive", "source_refs", "evidence_state"})
            owned(row, "right_id")
            require(row["right_id"] not in rights and row["ip_id"] in ips,
                    "invalid-right-reference", "right_id")
            choice(row["kind"], {"ownership", "license", "transfer"}, "kind")
            choice(row["evidence_state"], STATES, "evidence_state")
            start = iso_date(row["effective_start"], "effective_start")
            end = (iso_date(row["end_exclusive"], "end_exclusive")
                   if row["end_exclusive"] is not None else None)
            require(end is None or start < end, "invalid-period", "rights")
            self.sources(row["source_refs"])
            if not row["source_refs"]:
                gaps.append({"category": "missing-rights-evidence", "id": row["right_id"]})
            rights[row["right_id"]] = row
        for row in bundle["finance"]:
            shape(row, {"finance_id", "taxpayer_id", "category", "amount", "currency",
                        "date", "source_refs", "evidence_state"})
            owned(row, "finance_id")
            require(row["finance_id"] not in finance, "duplicate-identity", "finance_id")
            choice(row["category"], {"invoice", "payment", "cost"}, "category")
            choice(row["evidence_state"], STATES, "evidence_state")
            day = iso_date(row["date"], "date")
            text(row["currency"], "currency", limit=3)
            self.sources(row["source_refs"])
            numeric = amount(row["amount"], nullable=True)
            if day.year != bundle["tax_year"]:
                gaps.append({"category": "finance-period-conflict", "id": row["finance_id"]})
            if numeric is None:
                gaps.append({"category": "missing-amount", "id": row["finance_id"]})
            if row["currency"] not in self.config["currencies"]:
                gaps.append({"category": "unsupported-currency", "id": row["finance_id"]})
            if not row["source_refs"]:
                gaps.append({"category": "missing-finance-evidence", "id": row["finance_id"]})
            finance[row["finance_id"]] = row
        work_identity = {}
        for row in bundle["work_refs"]:
            shape(row, {"owner_workspace", "entry_id", "entry_hash", "kit_hash"},
                  {"procedure_id", "procedure_version"})
            owner = row["owner_workspace"]
            require(owner in self.ledgers, "unapproved-workspace", "work_ref")
            ledger = self.ledgers[owner]
            ledger.check_loaded()
            current = ledger.committed()[0]
            entry = current.get(row["entry_id"])
            require(entry is not None and not entry.get("voided", False)
                    and digest(entry) == row["entry_hash"], "stale-work-reference", "work_ref")
            for ref in entry["source_refs"]:
                validate_source(ref, ledger.config)
            key = owner + ":" + entry["entry_id"]
            require(key not in work or work[key] == row, "conflicting-work-reference", "work_ref")
            # Cross-workspace copying of a logical work identity is not extra evidence/time.
            require(entry["work_id"] not in work_identity or work_identity[entry["work_id"]] == key,
                    "duplicated-work-owner", "work_ref")
            work_identity[entry["work_id"]] = key
            if row["kit_hash"] is None:
                gaps.append({"category": "missing-documentation", "id": key})
            else:
                sha(row["kit_hash"], "kit_hash")
                identifier(row.get("procedure_id"), "procedure_id")
                v = row.get("procedure_version")
                require(type(v) is int and v > 0, "invalid-version", "procedure_version")
                saved = read_json(ledger.runtime("documentation/" + row["procedure_id"]
                                  + "/v" + str(v) + "/provenance.json", exists=True))
                kit = assemble(ledger, saved["procedure"])
                require(saved["kit_hash"] == kit["kit_hash"] == row["kit_hash"]
                        and entry["work_id"] in saved["procedure"]["work_ids"],
                        "stale-documentation", "kit_hash")
                for name, body in kit["files"].items():
                    path = ledger.runtime("documentation/" + row["procedure_id"]
                                          + "/v" + str(v) + "/kit/" + name, exists=True)
                    require(path.read_bytes() == body.encode("utf-8"),
                            "stale-documentation", "kit_file")
            work[key] = row
        allocated, ids, ip_allocations = {}, set(), {key: [] for key in ips}
        with localcontext() as ctx:
            ctx.prec = 50
            for row in bundle["allocations"]:
                shape(row, {"allocation_id", "finance_id", "ip_id", "amount", "currency", "work_refs"})
                identifier(row["allocation_id"], "allocation_id")
                require(row["allocation_id"] not in ids and row["finance_id"] in finance
                        and row["ip_id"] in ips, "invalid-allocation-reference", "allocation")
                ids.add(row["allocation_id"])
                numeric = amount(row["amount"])
                text(row["currency"], "currency", limit=3)
                source = finance[row["finance_id"]]
                if row["currency"] != source["currency"]:
                    gaps.append({"category": "allocation-currency-conflict", "id": row["allocation_id"]})
                require(isinstance(row["work_refs"], list) and row["work_refs"]
                        and all(isinstance(ref, str) and ref in work for ref in row["work_refs"]),
                        "missing-work-reference", "allocation")
                allocated[row["finance_id"]] = allocated.get(row["finance_id"], Decimal(0)) + numeric
                day = iso_date(source["date"], "date")
                effective = [r for r in rights.values() if r["ip_id"] == row["ip_id"]
                             and iso_date(r["effective_start"], "start") <= day
                             and (r["end_exclusive"] is None or day < iso_date(r["end_exclusive"], "end"))
                             and r["source_refs"] and r["taxpayer_id"] == self.config["taxpayer_id"]]
                if not effective:
                    gaps.append({"category": "missing-effective-rights", "id": row["allocation_id"]})
                ip_allocations[row["ip_id"]].append(row["allocation_id"])
            for key, value in allocated.items():
                source = amount(finance[key]["amount"], nullable=True)
                if source is not None and value > source:
                    gaps.append({"category": "over-allocation", "id": key})
        for key in ips:
            if not ip_allocations[key]:
                gaps.append({"category": "missing-allocation", "id": key})
        if not ips or not finance or not bundle["allocations"]:
            gaps.append({"category": "empty-evidence", "id": "bundle"})
        gaps = sorted({(g["category"], g["id"]) for g in gaps})
        return {"schema_version": 1, "state": "blocked" if gaps else "evidence-only",
                "eligibility": "unknown", "taxpayer_id": self.config["taxpayer_id"],
                "tax_year": bundle["tax_year"], "bundle_hash": digest(bundle),
                "config_hash": self.loaded_hash, "unique_work_references": len(work),
                "ledger_snapshots": {owner: self.ledgers[owner].snapshot()
                                     for owner in sorted({row["owner_workspace"] for row in work.values()})},
                "allocated_amounts": {key: decimal_string(value) for key, value in allocated.items()},
                "ip_allocations": ip_allocations,
                "gaps": [{"category": category, "id": key} for category, key in gaps],
                "review_questions": ["Advisor: assess eligibility, rights and allocation method.",
                                     "Owner: supply missing evidence; no inferred zero or qualification."]}

    def write(self, bundle, expected_hash, *, owner_approved=False):
        require(owner_approved, "owner-approval-required", "tax-evidence")
        with self.ledgers[self.config["owner_workspace"]].lock():
            value = self.packet(bundle)
            require(digest(value) == expected_hash, "stale-approval", "tax_packet")
            folder = "packets/" + str(bundle["tax_year"]) + "/" + expected_hash + "/"
            atomic_write(safe_path(self.home, folder + "bundle.json", must_exist=False),
                         canonical_bytes(bundle), immutable=True)
            atomic_write(safe_path(self.home, folder + "packet.json", must_exist=False),
                         canonical_bytes(value), immutable=True)
            return {"state": value["state"], "packet_hash": expected_hash,
                    "relative_folder": folder, "eligibility": "unknown"}
