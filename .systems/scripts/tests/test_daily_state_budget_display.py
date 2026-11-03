"""Synthetic state/budget rendering regressions; no private records or API calls."""
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
loader = importlib.machinery.SourceFileLoader("daily_display_under_test", str(SCRIPTS / "render-personal-ops-daily-summary-v4"))
spec = importlib.util.spec_from_loader(loader.name, loader)
renderer = importlib.util.module_from_spec(spec)
loader.exec_module(renderer)


class StateDisplayTests(unittest.TestCase):
    def state(self, current, **properties):
        return "\n".join(renderer.render_state({"current_state_json": json.dumps(current), **properties}, []))

    def test_context_preserved_without_note(self):
        text = self.state({"mental": {"score": 4, "context": "Focused on the approved product."}})
        self.assertIn("**Mental:** `4/5` — Focused on the approved product.", text)
        self.assertNotIn("`4/5` — nie podano", text)

    def test_note_takes_precedence_without_merging_conflicting_text(self):
        self.assertEqual(renderer.state_note({"note": "Current note", "context": "Older context"}), "Current note")
        self.assertEqual(renderer.state_note({"note": "  ", "context": "  Context  "}), "Context")

    def test_score_without_description_has_no_false_missing_suffix(self):
        text = self.state({"body": {"score": 4}})
        self.assertIn("**Ciało:** `4/5`. Wskazówka", text)
        self.assertNotIn("`4/5` —", text)

    def test_actual_missing_score_remains_unknown(self):
        for current in ({}, {"mental": {"score": None}}, {"mental": {"score": ""}}):
            text = self.state(current, mental_clarity_score=None)
            self.assertIn("**Mental:** `nie podano`", text)
            self.assertNotIn("None/5", text)

    def test_scalar_fallback_and_note_without_score_are_preserved(self):
        text = self.state({"mental": {"context": "Description without a score"}}, body_readiness_score=3)
        self.assertIn("`nie podano` — Description without a score", text)
        self.assertIn("**Ciało:** `3/5`.", text)

    def test_description_punctuation_is_not_duplicated(self):
        text = self.state({"body": {"score": 4, "note": "No reported restrictions."}})
        self.assertIn("No reported restrictions. Wskazówka", text)
        self.assertNotIn("restrictions..", text)


class BudgetDisplayTests(unittest.TestCase):
    def monthly(self):
        return {"currency": "PLN", "base_budget": 1000, "buffer": 80, "current_spending": 0,
                "remaining_base_budget": 1000, "remaining_days_inclusive": 20,
                "average_available_per_remaining_day": 50, "approximate": False}

    def test_total_adds_buffer_exactly_once_and_labels_base_average(self):
        original = self.monthly()
        text = "\n".join(renderer.render_monthly_budget({}, original))
        self.assertIn("Pozostało z bazy: `1 000 PLN`", text)
        self.assertIn("Pozostało łącznie z buforem: `1 080 PLN`", text)
        self.assertIn("Średnia z pozostałej bazy na dzień: `50 PLN`", text)
        self.assertEqual(original, self.monthly())

    def test_incomplete_history_never_uses_buffer_as_a_balance(self):
        monthly = self.monthly()
        monthly.update(remaining_base_budget=None, average_available_per_remaining_day=None)
        text = "\n".join(renderer.render_monthly_budget({}, monthly))
        self.assertIn("Pozostało łącznie z buforem: `nie podano PLN`", text)
        self.assertNotIn("Pozostało łącznie z buforem: `80 PLN`", text)

    def test_negative_base_counts_spent_buffer_and_retains_cents(self):
        monthly = self.monthly()
        monthly.update(remaining_base_budget=-25.25)
        text = "\n".join(renderer.render_monthly_budget({}, monthly))
        self.assertIn("Pozostało łącznie z buforem: `54,75 PLN`", text)

    def test_zero_and_missing_buffer_are_distinct(self):
        monthly = self.monthly()
        monthly.update(remaining_base_budget=0, buffer=0)
        self.assertIn("Pozostało łącznie z buforem: `0 PLN`", "\n".join(renderer.render_monthly_budget({}, monthly)))
        monthly["buffer"] = None
        self.assertIn("Pozostało łącznie z buforem: `nie podano PLN`", "\n".join(renderer.render_monthly_budget({}, monthly)))

    def test_approximation_warning_preserved(self):
        monthly = self.monthly()
        monthly["approximate"] = True
        self.assertIn("wartości przybliżone", "\n".join(renderer.render_monthly_budget({}, monthly)))


if __name__ == "__main__":
    unittest.main()
