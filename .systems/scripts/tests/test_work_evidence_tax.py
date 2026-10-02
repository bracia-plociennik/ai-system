"""Synthetic nonlegal calculator cases. No real taxpayer/rate."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

import test_work_evidence_tax_evidence as tax_fixture
import test_work_evidence_docs as docs_fixture
from work_evidence import EvidenceError, digest, canonical_bytes
from work_evidence_docs import assemble, persist
from work_evidence_tax import Calculator, Evaluator, number, rule_shape

def ref(name):
    return {"op": "ref", "name": name}

def const(value, unit="ratio"):
    return {"op": "const", "value": value, "unit": unit}

def op(name, *args):
    return {"op": name, "args": list(args)}


class CalculatorTests(unittest.TestCase):
    def setUp(self):
        self.f = tax_fixture.TaxEvidenceTests()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        docs = docs_fixture.DocsTests()
        docs.setUp()
        self.addCleanup(docs.doCleanups)
        p = copy.deepcopy(docs.procedure)
        p["source_refs"] = copy.deepcopy(self.f.f.entry["source_refs"])
        p["work_ids"] = [self.f.f.entry["work_id"]]
        for group in ("inputs", "derivatives"):
            p[group][0]["source_sha256"] = p["source_refs"][0]["sha256"]
        kit = assemble(self.f.f.ledger, p)
        persist(self.f.f.ledger, p, kit["kit_hash"], owner_approved=True)
        self.f.bundle["work_refs"][0].update(kit_hash=kit["kit_hash"],
                                             procedure_id=p["procedure_id"], procedure_version=1)
        cost = copy.deepcopy(self.f.bundle["finance"][0])
        cost.update(finance_id="sample-cost", category="cost", amount="20.00")
        self.f.bundle["finance"].append(cost)
        self.rule = {"schema_version": 1, "rule_set_id": "synthetic-arithmetic", "version": 1,
                     "taxpayer_id": "sample-taxpayer", "tax_year": 2026,
                     "effective_start": "2026-01-01", "end_exclusive": "2027-01-01",
                     "currency": "PLN", "precision": 40, "rounding": "half-up", "places": 2,
                     "scope": "Nonlegal arithmetic test only",
                     "qualification_method": "Synthetic; no legal eligibility",
                     "allocation_method": "Fixture operands", "exclusions": ["Real tax use"],
                     "inputs": {"revenue": {"finance_id": "sample-invoice", "field": "amount", "unit": "money"},
                                "cost": {"finance_id": "sample-cost", "field": "amount", "unit": "money"}},
                     "expressions": {"difference": op("sub", ref("revenue"), ref("cost")),
                                     "result": op("mul", ref("difference"), const("0.25"))},
                     "outputs": ["result"],
                     "reference_cases": [{"inputs": {"revenue": "100.00", "cost": "20.00"},
                                          "expected": {"result": "20.00"}}]}
        self.envelope = {"schema_version": 1, "rule": self.rule, "revoked": False,
                         "synthetic": True, "activation": None,
                         "approval": {"rule_hash": digest(self.rule), "advisor_id": "fixture-advisor",
                                      "approved_at": "2026-10-02T10:00:00+02:00",
                                      "source_ref": copy.deepcopy(self.f.ref), "owner_verified": True}}
        self.rules_path = self.f.home / "rules.json"
        self.save()
        self.calculator = Calculator(self.f.register, "rules.json")

    def save(self):
        self.rules_path.write_bytes(canonical_bytes(self.envelope))

    def preview(self):
        return self.calculator.calculate(self.f.bundle)

    def resign(self):
        self.envelope["approval"]["rule_hash"] = digest(self.rule)
        self.save()

    def test_golden_exact_trace_readonly(self):
        before = self.f.f.hashes()
        value = self.preview()
        self.assertEqual(before, self.f.f.hashes())
        self.assertEqual(value["outputs"]["result"],
                         {"value": "20.00", "unit": "money", "currency": "PLN"})
        self.assertTrue(value["synthetic_nonlegal"])
        self.assertEqual(value["state"], "draft")
        self.assertTrue(any(isinstance(row["origin"], dict) and
                            row["origin"]["finance_id"] == "sample-invoice" for row in value["trace"]))
        self.assertNotIn("TAX_PRIVATE_CANARY", json.dumps(value))

    def test_decimal_no_float_nonfinite_or_exponent(self):
        for value in (True, 0.25, "NaN", "Infinity", "1e2", "01", "1x2"):
            with self.subTest(value=value), self.assertRaises(EvidenceError):
                number(value)

    def test_unit_and_denominator_rejections(self):
        for expr in (op("mul", ref("revenue"), ref("cost")),
                     op("add", ref("revenue"), const("1")),
                     op("div", ref("revenue"), const("0")),
                     op("ratio", ref("revenue"), const("1")),
                     op("div", const("1"), const("-1"))):
            self.rule["expressions"]["result"] = expr
            with self.subTest(expr=expr), self.assertRaises(EvidenceError):
                rule_shape(self.rule)

    def test_unsupported_code_cycle_and_limits(self):
        for expr in ({"op": "eval", "args": ["__import__('os')"]}, "print('unsafe')",
                     ref("result"), ref("unknown")):
            self.rule["expressions"]["result"] = expr
            with self.subTest(expr=expr), self.assertRaises(EvidenceError):
                rule_shape(self.rule)
        nested = const("1")
        for _ in range(34):
            nested = op("sum", nested)
        self.rule["expressions"]["result"] = nested
        with self.assertRaises(EvidenceError):
            rule_shape(self.rule)

    def test_inactive_bad_golden_and_unknown_precision(self):
        self.rule["expressions"]["unused"] = {"op": "eval", "args": []}
        with self.assertRaises(EvidenceError):
            rule_shape(self.rule)
        del self.rule["expressions"]["unused"]
        self.rule["reference_cases"][0]["expected"]["result"] = "20.01"
        with self.assertRaises(EvidenceError):
            rule_shape(self.rule)
        self.rule["precision"] = 20
        with self.assertRaises(EvidenceError):
            rule_shape(self.rule)

    def test_rounding_and_sum_min_max_ratio(self):
        values = {name: {"value": number(value), "unit": "money", "currency": "PLN", "origin": "fixture"}
                  for name, value in {"revenue": "100.00", "cost": "20.00"}.items()}
        for expr, expected in ((op("sum", ref("revenue"), ref("cost")), "120.00"),
                               (op("min", ref("revenue"), ref("cost")), "20.00"),
                               (op("max", ref("revenue"), ref("cost")), "100.00"),
                               (op("ratio", ref("cost"), ref("revenue")), "0.20"),
                               (const("1.005", "money"), "1.01")):
            self.rule["expressions"]["result"] = expr
            self.assertEqual(Evaluator(self.rule, values).run()["outputs"]["result"]["value"], expected)

    def test_taxpayer_year_period_currency_and_approval(self):
        for field, value in (("taxpayer_id", "other"), ("tax_year", 2025),
                             ("effective_start", "2026-10-03"), ("currency", "USD")):
            original = self.rule[field]
            self.rule[field] = value
            self.resign()
            with self.subTest(field=field), self.assertRaises(EvidenceError):
                self.preview()
            self.rule[field] = original
        self.resign()
        self.envelope["approval"]["rule_hash"] = "0"*64
        self.save()
        with self.assertRaises(EvidenceError):
            self.preview()

    def test_real_activation_missing_and_revoked(self):
        self.envelope["synthetic"] = False
        self.save()
        with self.assertRaises(EvidenceError):
            self.preview()
        self.envelope["synthetic"] = True
        self.envelope["revoked"] = True
        self.save()
        with self.assertRaises(EvidenceError):
            self.preview()

    def test_missing_amount_vs_zero_and_incomplete_coverage(self):
        self.f.bundle["finance"][1]["amount"] = None
        with self.assertRaises(EvidenceError):
            self.preview()
        self.f.bundle["finance"][1]["amount"] = "0.00"
        self.assertEqual(self.preview()["outputs"]["result"]["value"], "25.00")
        self.f.bundle["rights"] = []
        with self.assertRaises(EvidenceError):
            self.preview()

    def test_activation_hash_scope_and_source_correction(self):
        self.envelope.update(synthetic=False, activation={"rule_hash": digest(self.rule),
                             "taxpayer_id": "sample-taxpayer", "approved_by": "owner",
                             "approved_at": "2026-10-02T11:00:00+02:00", "advisor_reviewed": True})
        self.save()
        self.assertFalse(self.preview()["synthetic_nonlegal"])
        for field, value in (("approved_by", "agent"), ("advisor_reviewed", False),
                             ("taxpayer_id", "other"), ("rule_hash", "0"*64),
                             ("approved_at", "2026-10-02T09:00:00+02:00")):
            old = self.envelope["activation"][field]
            self.envelope["activation"][field] = value
            self.save()
            with self.subTest(field=field), self.assertRaises(EvidenceError):
                self.preview()
            self.envelope["activation"][field] = old
        self.save()
        result = self.calculator.write(self.f.bundle, digest(self.preview()), owner_approved=True)
        self.f.source.write_text("Changed source", encoding="utf-8")
        self.assertEqual(self.calculator.read_current(self.f.bundle, result["relative_path"])["state"], "stale")

    def test_write_read_current_idempotent_and_source_rule_stale(self):
        value = self.preview()
        result = self.calculator.write(self.f.bundle, digest(value), owner_approved=True)
        before = self.f.f.hashes()
        self.calculator.write(self.f.bundle, digest(value), owner_approved=True)
        self.assertEqual(before, self.f.f.hashes())
        self.assertTrue(self.calculator.read_current(self.f.bundle, result["relative_path"])["usable_as_current"])
        self.envelope["revoked"] = True
        self.save()
        self.assertEqual(self.calculator.read_current(self.f.bundle, result["relative_path"])["state"], "stale")
        with self.assertRaises(EvidenceError):
            self.calculator.write(self.f.bundle, digest(value), owner_approved=True)

    def test_changed_rule_and_cli_no_unapproved_access(self):
        value = self.preview()
        self.rule["scope"] = "changed scope"
        self.resign()
        with self.assertRaises(EvidenceError):
            self.calculator.write(self.f.bundle, digest(value), owner_approved=True)
        scripts = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable, "-B", str(scripts / "work-evidence-tax-calculate"),
                                 "write", "--workspace", "/missing", "--taxpayer", "sample",
                                 "--rules", "rules.json", "--bundle", "bundle.json"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)["category"], "owner-approval-required")
