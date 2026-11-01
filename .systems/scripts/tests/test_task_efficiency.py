import copy
import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import task_efficiency as t


def facts(kind='answer'):
    return dict(kind=kind, risk='low', operation=None, **{k: True for k in t.FLAGS})


def operation():
    f = facts('data-operation'); f['risk'] = 'critical'
    f['operation'] = {k: k not in {'uncertain_result', 'excluded_impact'} for k in t.OPERATION}
    return f


class TaskPaths(unittest.TestCase):
    def test_general_paths_and_unchanged_authority(self):
        for kind in t.KINDS:
            f = operation() if kind == 'data-operation' else facts(kind)
            out = t.assess(f)
            self.assertFalse(out['execution_authorized'])
            self.assertEqual(out['risk'], f['risk'])
            self.assertNotIn(out['route'], {'spawn', 'change-model'})
        self.assertEqual(t.assess(facts())['route'], 'answer-directly')

    def test_necessary_unknown_and_access_hold(self):
        f = facts('diagnosis'); f['evidence_sufficient'] = False
        self.assertEqual(t.assess(f)['route'], 'resolve-specific-unknown')
        for key in t.FLAGS - {'evidence_sufficient'}:
            f = facts(); f[key] = False
            self.assertEqual(t.assess(f)['route'], 'blocked')

    def test_operation_guards_and_uncertain_result(self):
        self.assertEqual(t.assess(operation())['route'], 'bounded-operation-candidate')
        for k in t.OPERATION - {'uncertain_result', 'excluded_impact'}:
            f = operation(); f['operation'][k] = False
            self.assertEqual(t.assess(f)['route'], 'normal-local-route')
        f = operation(); f['operation']['excluded_impact'] = True
        self.assertEqual(t.assess(f)['route'], 'normal-local-route')
        f['operation']['uncertain_result'] = True
        self.assertEqual(t.assess(f)['route'], 'inspect-outcome')

    def test_invalid_and_duplicate_facts(self):
        variants = [dict(facts(), command='write'), dict(facts(), risk='unknown'),
                    dict(facts(), scope_known=1), dict(operation(), operation={}),
                    dict(facts(), operation={})]
        for value in variants:
            with self.assertRaises(ValueError): t.assess(value)
        for raw in ('{"kind":"answer","kind":"research"}', 'x' * 65537, '{}'):
            p = subprocess.run([sys.executable, '-B', str(ROOT/'task_efficiency.py')], input=raw, text=True, capture_output=True)
            self.assertEqual(p.returncode, 2)
            self.assertNotIn('execution_authorized": true', p.stdout)

    def test_synthetic_transaction_cases(self):
        # An isolated acceptance fixture, not a production SQL executor.
        for case in ('one-invalid','all-valid','case-difference','ambiguous','record-drift','rule-drift','wrong-count','transaction-error'):
            with self.subTest(case=case):
                db = sqlite3.connect(':memory:'); db.execute('create table records(id integer primary key, value text, version integer)')
                db.executemany('insert into records values(?,?,?)', [(1,'bad',0),(2,'good',0)]); db.commit()
                old = db.execute('select value,version from records where id=1').fetchone()
                eligible = case not in {'all-valid','case-difference','ambiguous','rule-drift'}
                if case == 'record-drift': db.execute("update records set value='later',version=1 where id=1"); db.commit()
                before = list(db.execute('select * from records order by id'))
                db.execute('begin')
                if eligible:
                    count = db.execute('update records set value=NULL,version=version+1 where id=? and value=? and version=?',(1,*old)).rowcount
                    if count != 1 or case in {'wrong-count','transaction-error'}: db.rollback()
                    else: db.commit()
                else: db.rollback()
                after = list(db.execute('select * from records order by id'))
                self.assertEqual(after[1], before[1])
                if case == 'one-invalid': self.assertIsNone(after[0][1])
                else: self.assertEqual(after,before)
                db.close()

    def test_cms_filter_and_protected_fields_premises(self):
        before = dict(active=True, empty=None, relation=7)
        observed = dict(active=False, empty=[], relation=7)
        self.assertNotEqual(observed['empty'], before['empty'])
        self.assertEqual([observed] if observed['active'] else [], [])
        # A missing active-only result cannot establish the all-records state.
        self.assertFalse(observed['active']); self.assertEqual(observed['relation'],before['relation'])
        f = operation(); f['operation']['known_side_effects'] = False
        self.assertEqual(t.assess(f)['route'],'normal-local-route')


if __name__ == '__main__': unittest.main()
