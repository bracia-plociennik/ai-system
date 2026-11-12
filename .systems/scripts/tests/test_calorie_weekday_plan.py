"""Synthetic weekday budget/renderer tests; no owner data, sync or API writes."""
import importlib.machinery
import importlib.util
from datetime import date
from pathlib import Path
import json
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))


def module(name):
    loader = importlib.machinery.SourceFileLoader(name.replace('-', '_'), str(SCRIPTS / name))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    result = importlib.util.module_from_spec(spec)
    loader.exec_module(result)
    return result


calc = module('calculate-personal-ops-budgets')


class WeekdayPlanTests(unittest.TestCase):
    def config(self):
        return {'weekly_calorie_budget': '16900', 'training_day_standard': '2500',
                'rest_day_standard': '2300', 'calorie_weekday_targets_json': '[2300,2300,2300,2300,2300,2700,2700]',
                'monthly_base_budget': '1000', 'monthly_buffer': '100',
                'daily_spending_pace': '50', 'monthly_budget_currency': 'PLN'}

    def row(self, day, value, session='2026-11-11'):
        return {'session_date': session, 'aggregate_observations': [{'metric': 'calories',
                'period_start': day, 'period_end': day, 'value': value, 'approximate': False}]}

    def report(self, rows=None, target=date(2026, 11, 11)):
        if rows is None:
            rows = [self.row('2026-11-09', 2500), self.row('2026-11-10', 2600)]
        return calc.calorie_report(rows, target, self.config())

    def test_owner_example_no_automatic_compensation(self):
        report = self.report()
        self.assertEqual([report[k] for k in ['actual_consumed','remaining_before_today',
                         'remaining_planned','projected_week_total','projected_overrun']], [5100,11800,12300,17400,500])
        self.assertEqual(report['planned_today'], 2300)
        self.assertIsNone(report['mechanical_limit_after_today'])
        self.assertEqual(calc.calorie_summary_lines(report), [
            'Plan: 16 900 kcal.', 'Podjedzono: 5100 kcal.', 'Pozostało: 11 800 kcal.',
            'Prognoza: 17 400 kcal.', 'Przekroczenie: +500 kcal.'])

    def test_missing_day_is_unknown_not_zero(self):
        report = self.report([self.row('2026-11-09',2500)])
        self.assertEqual(report['actual_consumed'], 2500)
        self.assertEqual(report['coverage']['missing_dates'], ['2026-11-10'])
        for key in ['remaining_before_today','projected_week_total','projected_overrun']:
            self.assertIsNone(report[key])
        self.assertIn('Prognoza: nieznane kcal.', calc.calorie_summary_lines(report))

    def test_duplicate_does_not_double_count_conflict_blocks(self):
        row = self.row('2026-11-09', 2500)
        self.assertEqual(self.report([row,row,self.row('2026-11-10',2600)])['actual_consumed'],5100)
        with self.assertRaisesRegex(ValueError,'conflicting'):
            self.report([row,self.row('2026-11-09',2600)])

    def test_correction_replaces_selected_value(self):
        report = self.report([self.row('2026-11-09',2300),self.row('2026-11-10',2300)])
        self.assertEqual(report['actual_consumed'],4600)
        self.assertEqual(report['projected_overrun'],0)

    def test_lower_intake_preserves_plan(self):
        report = self.report([self.row('2026-11-09',2200),self.row('2026-11-10',2100)])
        self.assertEqual(report['plan_deviation_to_date'],-300)
        self.assertEqual(report['projected_overrun'],0)
        self.assertEqual(report['planned_today'],2300)

    def test_partial_current_day_is_not_added(self):
        report = self.report([self.row('2026-11-09',2500),self.row('2026-11-10',2600),self.row('2026-11-11',700)])
        self.assertEqual(report['actual_consumed'],5100)

    def test_future_record_is_not_imported_into_past(self):
        report = self.report([self.row('2026-11-09',2500,session='2026-11-12')])
        self.assertIsNone(report['actual_consumed'])

    def test_week_boundary_resets_and_sunday_is_weekend(self):
        self.assertEqual(self.report([],date(2026,11,9))['projected_week_total'],16900)
        self.assertEqual(self.report([],date(2026,11,15))['planned_today'],2700)
        rows = [self.row('2026-11-09',9999,session='2026-11-09')]
        self.assertEqual(self.report(rows,date(2026,11,16))['actual_consumed'],0)

    def test_workout_independent_defaults_and_legacy_fallback(self):
        c = self.config()
        for profile in ['rest','training',None]:
            self.assertEqual(calc.default_calorie_target(c,date(2026,11,9),profile),2300)
            self.assertEqual(calc.default_calorie_target(c,date(2026,11,15),profile),2700)
        del c['calorie_weekday_targets_json']
        self.assertEqual(calc.default_calorie_target(c,date(2026,11,9),'training'),2500)

    def test_explicit_daily_target_wins_without_losing_closure(self):
        rows = [self.row('2026-11-09',2500), self.row('2026-11-10',2600)]
        report = calc.calculate_from_records(rows,date(2026,11,11),self.config(),{'planned_calories_representative':2400})['weekly_calories']
        self.assertEqual(report['actual_consumed'],5100)
        self.assertEqual(report['planned_today'],2400)
        self.assertEqual(report['projected_week_total'],17500)

    def test_invalid_config_rejected(self):
        for value in ['[]','[2300]','[2300,2300,2300,2300,2300,2700,true]',
                      '[2300,2300,2300,2300,2300,2700,NaN]', '[2300,2300,2300,2300,2300,2700,-1]']:
            with self.assertRaises(ValueError):
                calc.configured_weekday_targets({**self.config(),'calorie_weekday_targets_json':value})
        with self.assertRaisesRegex(ValueError,'sum'):
            calc.configured_weekday_targets({**self.config(),'weekly_calorie_budget':'16800'})

    def test_weekly_schedule_uses_same_defaults(self):
        import personal_ops_spor_proposals as p
        weekly = p.schedule_plan(self.config(),None,date(2026,11,7),'weekly')
        self.assertEqual([row['proposed_calorie_target'] for row in weekly['days']],[2300]*5)


if __name__ == '__main__':
    unittest.main()
