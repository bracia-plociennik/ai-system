"""Execute the seven authored synthetic cases and emit reproducible QA hashes."""
import copy
import json
import sys
import unittest

import test_work_evidence_editorial_v2 as fixtures
from editorial_v2_semantic_cases import CASES
from work_evidence import digest, file_hash
from work_evidence_editorial_v2 import prepare, bundle, PREPARE_FIELDS


def trace(case):
    f = fixtures.EditorialV2Tests()
    f.setUp()
    try:
        q = f.request
        f.f.source.write_text(case["source"], encoding="utf-8")
        entry = copy.deepcopy(f.ledger.committed()[0][fixtures.ENTRY_ID])
        entry.update(revision=entry["revision"] + 1, previous_revision_hash=digest(entry),
                     reason="Synthetic editorial semantic proof")
        entry["source_refs"][0]["sha256"] = file_hash(f.f.source)
        f.f.commit({"schema_version": 1, "changes": [{"row_id": "semantic-proof", "entry": entry}]})
        claim = q["claims"][0]
        claim.update(entry_hash=digest(entry), source_ref=copy.deepcopy(entry["source_refs"][0]),
                     text=case["source"], privacy_state=case.get("privacy", "public-ready"),
                     supported=case.get("supported", True), sensitive_terms=case.get("sensitive_terms", []),
                     replacements=[{"from": v["from_"], "to": v["to"]} for v in case.get("replacements", [])],
                     approval=None)
        if claim["privacy_state"] == "public-ready" and claim["supported"]:
            f.v1.approve_claim(claim)
        if claim["replacements"]:
            original = fixtures.review_source(f.ledger, {k: q[k] for k in PREPARE_FIELDS})
            assert case["source"] == original["lessons"][0]["text"], "Original must remain intact privately"
            f.review_original(claim)
        q["topic"].update(topic_id=case["case_id"], title=case["title"], audience_problem=case["audience_problem"],
                          transferable_lesson=case["lesson"], brand_angles=copy.deepcopy(case["angles"]),
                          selected_brand_ids=[a["brand_id"] for a in case["angles"]])
        q["capacity"]["effort_budget_minutes"] = case["budget"]
        package = prepare(f.ledger, {k: q[k] for k in PREPARE_FIELDS})
        assert package == prepare(f.ledger, {k: q[k] for k in PREPARE_FIELDS}), "Same proof must prepare identically"
        recommendation = dict(package_hash=package["package_hash"], recommendation_id=case["case_id"], revision=1,
            assessments=copy.deepcopy(case["assessments"]), primary=copy.deepcopy(case["primary"]),
            alternative=copy.deepcopy(case["alternative"]), questions=case["questions"])
        recommendation["primary"]["why"] = case["primary_why"]
        recommendation["alternative"]["why"] = case["alternative_why"]
        q.update(recommendation=recommendation, decision=None, artifacts=[])
        before = f.f.hashes()
        output = bundle(f.ledger, q)
        assert before == f.f.hashes(), "Preview must not write"
        assert output["state"] == "recommendation-needs-decision"
        assert not output["publication_authorized"] and output["model_calls"] == 0
        for term in case.get("sensitive_terms", []):
            assert term not in json.dumps(output), "Identifier leaked from safe candidate"
        return {"case_id": case["case_id"], "input_hash": digest(package),
                "output_hash": digest(recommendation), "package_state": package["state"],
                "main_formats": [n["format"] for n in recommendation["primary"]["nodes"]],
                "alternative_formats": [n["format"] for n in recommendation["alternative"]["nodes"]],
                "assessments": len(recommendation["assessments"]), "read_only": True,
                "publication_authorized": False, "model_calls": 0}
    finally:
        f.doCleanups()


class SemanticCases(unittest.TestCase):
    def test_seven_real_agent_authored_recommendations(self):
        self.assertEqual(len(CASES), 7)
        for case in CASES:
            with self.subTest(case=case["case_id"]):
                result = trace(case)
                self.assertEqual(result["assessments"], 5 * len(case["angles"]))
                self.assertEqual(result["package_state"], "needs-evidence" if not case.get("supported", True) else "prepared")

    def test_owner_reviewed_blog_bonuses_and_distinct_brands(self):
        cases = {case["case_id"]: case for case in CASES}
        for key in ("evergreen-procedure", "technical-niche"):
            result = trace(cases[key])
            self.assertIn("blog-article", result["main_formats"])
            self.assertIn("newsletter", result["main_formats"])
            self.assertNotIn("requires-artifact", [e["relation"] for e in cases[key]["primary"]["edges"]])
        both = cases["two-brand-audiences"]
        self.assertEqual({n["brand_id"] for n in both["primary"]["nodes"]}, {"creator", "company"})


if __name__ == "__main__" and "--evidence" in sys.argv:
    print(json.dumps([trace(c) for c in CASES], indent=2))
elif __name__ == "__main__":
    unittest.main()
