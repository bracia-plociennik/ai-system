from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyze_task_usage import analyze


class UsageTests(unittest.TestCase):
    def event(self, identity, amount, kind='cumulative'):
        return dict(session_id='s', event_id=identity, kind=kind,
                    usage=dict(input_tokens=amount, cached_input_tokens=0, output_tokens=1))

    def test_cumulative_and_duplicate(self):
        a, b = self.event('1', 10), self.event('2', 20)
        result = analyze([a, a, b])
        self.assertEqual(result['groups'][0]['input_tokens'], 20)
        self.assertEqual(result['duplicates_skipped'], 1)

    def test_reset_is_explicit(self):
        result = analyze([self.event('1', 20), self.event('2', 10)])
        self.assertEqual(len(result['warnings']), 1)
        self.assertEqual(result['groups'][0]['input_tokens'], 20)

    def test_conflicting_duplicate_rejects(self):
        with self.assertRaises(ValueError):
            analyze([self.event('1', 10), self.event('1', 20)])

    def test_missing_counters_reject(self):
        item = self.event('1', 20)
        del item['usage']['input_tokens']
        with self.assertRaises(ValueError):
            analyze([item])

    def test_mixed_delta_cumulative_rejected(self):
        with self.assertRaises(ValueError):
            analyze([self.event('1', 10, 'delta'), self.event('2', 20)])

    def test_fork_response_identity_counted_once(self):
        first = dict(self.event('1', 10, 'delta'), response_id='shared-response')
        fork = dict(first, session_id='fork', event_id='copied-event')
        result = analyze([first, fork])
        self.assertEqual(result['groups'][0]['input_tokens'], 10)
        self.assertEqual(result['duplicates_skipped'], 1)

    def test_explicit_epoch_after_confirmed_reset(self):
        first = dict(self.event('1', 20), epoch='before-reset')
        second = dict(self.event('2', 10), epoch='after-reset')
        result = analyze([first, second])
        self.assertEqual(result['groups'][0]['input_tokens'], 30)
        self.assertEqual(result['warnings'], [])


if __name__ == '__main__':
    unittest.main()
