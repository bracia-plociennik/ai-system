"""Advisor-gated deterministic arithmetic; synthetic examples are not tax law."""
from __future__ import annotations

from decimal import (Decimal, localcontext, DecimalException, ROUND_HALF_UP,
                     ROUND_HALF_EVEN, ROUND_DOWN)
import re

from work_evidence import (EvidenceError, require, shape, version, identifier, text,
                           iso_date, instant, sha, digest, read_json, safe_path, canonical_bytes)
from work_evidence_ledger import atomic_write
from work_evidence_tax_evidence import TaxRegister, amount, decimal_string

ROUNDING = {"half-up": ROUND_HALF_UP, "half-even": ROUND_HALF_EVEN, "down": ROUND_DOWN}
NUMBER = re.compile(r"-?(?:0|[1-9][0-9]{0,23})(?:\.[0-9]{1,12})?\Z")


def number(value):
    require(isinstance(value, str) and NUMBER.fullmatch(value),
            "invalid-decimal", "operand")
    result = Decimal(value)
    require(result.is_finite(), "invalid-decimal", "operand")
    return result


class Evaluator:
    def __init__(self, rule, values):
        self.rule, self.values = rule, values
        self.trace, self.cache, self.active = [], {}, set()
        self.count = 0

    def quantity(self, value, unit, origin):
        require(unit in {"money", "ratio"}, "invalid-unit", "operand")
        return {"value": value, "unit": unit,
                "currency": self.rule["currency"] if unit == "money" else None,
                "origin": origin}

    def node(self, node, depth=0):
        self.count += 1
        require(depth <= 32 and self.count <= 512, "expression-limit", "expression")
        require(isinstance(node, dict), "invalid-expression", "expression")
        op = node.get("op")
        if op == "const":
            shape(node, {"op", "value", "unit"})
            result = self.quantity(number(node["value"]), node["unit"], "rule-constant")
        elif op == "ref":
            shape(node, {"op", "name"})
            name = node["name"]
            identifier(name, "ref")
            if name in self.values:
                result = self.values[name]
            else:
                require(name in self.rule["expressions"], "missing-operand", "ref")
                require(name not in self.active, "expression-cycle", "ref")
                if name in self.cache:
                    result = self.cache[name]
                else:
                    self.active.add(name)
                    result = self.node(self.rule["expressions"][name], depth + 1)
                    self.active.remove(name)
                    self.cache[name] = result
        else:
            shape(node, {"op", "args"})
            require(op in {"add", "sub", "mul", "div", "sum", "ratio", "min", "max"},
                    "unsupported-operation", "expression")
            args = node["args"]
            require(isinstance(args, list) and 1 <= len(args) <= 32,
                    "invalid-arguments", "expression")
            require(op in {"sum", "min", "max"} or len(args) == 2,
                    "invalid-arguments", "expression")
            values = [self.node(item, depth + 1) for item in args]
            a, b = values[0], values[-1]
            if op in {"add", "sub", "sum", "min", "max"}:
                require(all(v["unit"] == a["unit"] and v["currency"] == a["currency"]
                            for v in values), "unit-mismatch", "expression")
                operands = [v["value"] for v in values]
                value = {"add": lambda: operands[0] + operands[1],
                         "sub": lambda: operands[0] - operands[1],
                         "sum": lambda: sum(operands, Decimal(0)),
                         "min": lambda: min(operands),
                         "max": lambda: max(operands)}[op]()
                unit = a["unit"]
            elif op == "mul":
                require(not (a["unit"] == b["unit"] == "money"),
                        "unit-mismatch", "expression")
                value = a["value"] * b["value"]
                unit = "money" if "money" in (a["unit"], b["unit"]) else "ratio"
            else:
                require(b["value"] > 0, "invalid-denominator", "expression")
                require(a["unit"] == b["unit"] or
                        (op == "div" and a["unit"] == "money" and b["unit"] == "ratio"),
                        "unit-mismatch", "expression")
                value = a["value"] / b["value"]
                unit = "ratio" if a["unit"] == b["unit"] else "money"
            result = self.quantity(value, unit, "expression")
        value = result["value"]
        require(value.is_finite() and (value == 0 or abs(value.adjusted()) <= 100),
                "numeric-limit", "expression")
        self.trace.append({"op": op, "node_hash": digest(node),
                           "value": decimal_string(value), "unit": result["unit"],
                           "currency": result["currency"], "origin": result["origin"]})
        return result

    def run(self):
        outputs = {}
        try:
            with localcontext() as ctx:
                ctx.prec = self.rule["precision"]
                ctx.rounding = ROUNDING[self.rule["rounding"]]
                for name in self.rule["outputs"]:
                    value = self.node({"op": "ref", "name": name})
                    rounded = value["value"].quantize(Decimal(1).scaleb(-self.rule["places"]))
                    outputs[name] = {"value": decimal_string(rounded),
                                     "unit": value["unit"], "currency": value["currency"]}
        except DecimalException:
            require(False, "numeric-limit", "expression")
        return {"outputs": outputs, "trace": self.trace}


def rule_shape(rule):
    shape(rule, {"schema_version", "rule_set_id", "version", "taxpayer_id", "tax_year",
                 "effective_start", "end_exclusive", "currency", "precision", "rounding",
                 "places", "scope", "qualification_method", "allocation_method",
                 "exclusions", "inputs", "expressions", "outputs", "reference_cases"})
    version(rule)
    for key in ("rule_set_id", "taxpayer_id"):
        identifier(rule[key], key)
    require(type(rule["version"]) is int and rule["version"] > 0, "invalid-version", "rule")
    require(type(rule["tax_year"]) is int, "invalid-year", "rule")
    start, end = iso_date(rule["effective_start"], "start"), iso_date(rule["end_exclusive"], "end")
    require(start < end, "invalid-period", "rule")
    require(type(rule["precision"]) is int and 28 <= rule["precision"] <= 50,
            "invalid-precision", "rule")
    require(rule["rounding"] in ROUNDING and type(rule["places"]) is int
            and 0 <= rule["places"] <= 8, "invalid-rounding", "rule")
    text(rule["currency"], "currency", limit=3)
    for key in ("scope", "qualification_method", "allocation_method"):
        text(rule[key], key)
    require(isinstance(rule["exclusions"], list) and len(rule["exclusions"]) <= 100,
            "invalid-exclusions", "rule")
    for excluded in rule["exclusions"]:
        text(excluded, "exclusion")
    for group in ("inputs", "expressions"):
        require(isinstance(rule[group], dict) and 0 < len(rule[group]) <= 128,
                "invalid-expressions", group)
        for name in rule[group]:
            identifier(name, group)
    require(not (set(rule["inputs"]) & set(rule["expressions"])),
            "ambiguous-reference", "rule")
    for spec in rule["inputs"].values():
        shape(spec, {"finance_id", "field", "unit"})
        identifier(spec["finance_id"], "finance_id")
        require(spec["field"] in {"amount", "allocated"} and spec["unit"] == "money",
                "unsupported-input", "rule")
    require(isinstance(rule["outputs"], list) and 0 < len(rule["outputs"]) <= 32
            and len(set(rule["outputs"])) == len(rule["outputs"])
            and all(name in rule["expressions"] for name in rule["outputs"]),
            "invalid-output", "rule")
    require(isinstance(rule["reference_cases"], list) and
            0 < len(rule["reference_cases"]) <= 100, "missing-reference-cases", "rule")
    # Validate unreachable nodes as well; unused unsafe formulas cannot hide in a ruleset.
    for case in rule["reference_cases"]:
        shape(case, {"inputs", "expected"})
        require(isinstance(case["inputs"], dict) and set(case["inputs"]) == set(rule["inputs"])
                and isinstance(case["expected"], dict)
                and set(case["expected"]) == set(rule["outputs"]),
                "invalid-reference-case", "rule")
        values = {name: {"value": number(value), "unit": "money",
                         "currency": rule["currency"], "origin": "synthetic-reference"}
                  for name, value in case["inputs"].items()}
        check = Evaluator(rule, values)
        checked = check.run()
        for name in rule["expressions"]:
            with localcontext() as ctx:
                ctx.prec = rule["precision"]
                ctx.rounding = ROUNDING[rule["rounding"]]
                check.node({"op": "ref", "name": name})
        require(all(number(case["expected"][name]) == Decimal(out["value"])
                    for name, out in checked["outputs"].items()),
                "reference-case-mismatch", "rule")


class Calculator:
    def __init__(self, register, rules_path):
        self.register, self.rules_path = register, rules_path

    def calculate(self, bundle):
        register = self.register
        envelope = read_json(safe_path(register.home, self.rules_path))
        shape(envelope, {"schema_version", "rule", "approval", "revoked", "synthetic", "activation"})
        version(envelope)
        require(type(envelope["revoked"]) is bool and not envelope["revoked"],
                "revoked-rule", "rule")
        require(type(envelope["synthetic"]) is bool, "invalid-synthetic-state", "rule")
        rule = envelope["rule"]
        rule_shape(rule)
        require(rule["taxpayer_id"] == register.config["taxpayer_id"]
                and rule["tax_year"] == bundle["tax_year"],
                "rule-taxpayer-period-conflict", "rule")
        require(rule["currency"] in register.config["currencies"], "unsupported-currency", "rule")
        approval = envelope["approval"]
        shape(approval, {"rule_hash", "advisor_id", "approved_at", "source_ref", "owner_verified"})
        sha(approval["rule_hash"], "rule_hash")
        identifier(approval["advisor_id"], "advisor_id")
        instant(approval["approved_at"], "approved_at")
        register.source(approval["source_ref"])
        require(approval["rule_hash"] == digest(rule) and approval["owner_verified"] is True,
                "advisor-approval-required", "rule")
        if envelope["synthetic"]:
            require(envelope["activation"] is None, "invalid-synthetic-activation", "rule")
        else:
            activation = envelope["activation"]
            require(isinstance(activation, dict), "real-activation-required", "rule")
            shape(activation, {"rule_hash", "taxpayer_id", "approved_at", "approved_by", "advisor_reviewed"})
            require(instant(activation["approved_at"], "approved_at") >=
                    instant(approval["approved_at"], "approved_at"),
                    "invalid-approval-order", "rule")
            require(activation["rule_hash"] == digest(rule)
                    and activation["taxpayer_id"] == rule["taxpayer_id"]
                    and activation["approved_by"] == "owner"
                    and activation["advisor_reviewed"] is True,
                    "real-activation-required", "rule")
        packet = register.packet(bundle)
        require(packet["state"] == "evidence-only", "incomplete-evidence", "packet")
        records = {row["finance_id"]: row for row in bundle["finance"]}
        values = {}
        for name, spec in rule["inputs"].items():
            require(spec["finance_id"] in records, "missing-operand", "rule")
            row = records[spec["finance_id"]]
            day = iso_date(row["date"], "date")
            require(iso_date(rule["effective_start"], "start") <= day <
                    iso_date(rule["end_exclusive"], "end"), "rule-period-conflict", "rule")
            require(row["currency"] == rule["currency"], "currency-mismatch", "operand")
            value = (row["amount"] if spec["field"] == "amount" else
                     packet["allocated_amounts"].get(spec["finance_id"]))
            require(value is not None, "missing-operand", "rule")
            values[name] = {"value": amount(value), "unit": "money", "currency": row["currency"],
                            "origin": {"finance_id": row["finance_id"], "field": spec["field"],
                                       "record_hash": digest(row)}}
        evaluated = Evaluator(rule, values).run()
        return {"schema_version": 1, "state": "draft",
                "synthetic_nonlegal": envelope["synthetic"], "taxpayer_id": rule["taxpayer_id"],
                "rule_set_id": rule["rule_set_id"], "rule_version": rule["version"],
                "rule_hash": digest(rule), "envelope_hash": digest(envelope),
                "bundle_hash": digest(bundle), "packet_hash": digest(packet),
                "rounding": rule["rounding"], "places": rule["places"],
                "precision": rule["precision"], **evaluated}

    def write(self, bundle, expected_hash, *, owner_approved=False):
        require(owner_approved, "owner-approval-required", "calculation")
        with self.register.ledgers[self.register.config["owner_workspace"]].lock():
            value = self.calculate(bundle)
            require(digest(value) == expected_hash, "stale-approval", "calculation")
            relative = ("calculations/" + value["rule_set_id"] + "/v" +
                        str(value["rule_version"]) + "/" + expected_hash + ".json")
            atomic_write(safe_path(self.register.home, relative, must_exist=False),
                         canonical_bytes(value), immutable=True)
            return {"state": "draft", "result_hash": expected_hash, "relative_path": relative}

    def read_current(self, bundle, result_path):
        saved = read_json(safe_path(self.register.home, result_path))
        try:
            current = self.calculate(bundle)
            require(digest(saved) == digest(current), "stale-calculation", "result")
        except EvidenceError:
            return {"state": "stale", "usable_as_current": False}
        return {"state": "draft", "usable_as_current": True, "result": current}
