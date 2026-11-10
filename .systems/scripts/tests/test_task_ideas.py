import json
import re
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from task_ideas import merge_idea


class IdeaTests(unittest.TestCase):
    def setUp(self):
        self.text = '---\nauthor: human\n---\n## TODO\n- [x] Ręczny etap\n\n## Evidence\nKeep\n## Working dump\n## TODO\nRaw\n'
        self.idea = dict(id='csv-export', text='Dodać CSV', source='owner message 2',
                         parent_task_id='00000000-0000-4000-8000-000000000001',
                         parent_stage_id='filters', kind='stage-extension')

    def test_capture_retry_preserves_manual_edits_and_raw(self):
        saved = merge_idea(self.text, self.idea)
        self.assertEqual(saved.split('## Evidence')[1], self.text.split('## Evidence')[1])
        edited = saved.replace('Ocenić pomysł — Dodać CSV', 'Mój opis pomysłu')
        self.assertEqual(merge_idea(edited, self.idea), edited)

    def test_resolution_has_own_checkbox_and_is_idempotent(self):
        saved = merge_idea(self.text, self.idea)
        request = dict(self.idea, disposition='accepted', evidence='spec.md scenario csv')
        resolved = merge_idea(saved, request)
        self.assertIn('- [x] Ocenić', resolved)
        self.assertEqual(merge_idea(resolved, request), resolved)
        self.assertIn('- [x] Ręczny etap', resolved)

    def test_conflict_and_injection_rejected(self):
        saved = merge_idea(self.text, self.idea)
        for value in (dict(self.idea, text='Different'), dict(self.idea, source='x\n## TODO'),
                      dict(self.idea, text='<!-- spoof -->')):
            with self.assertRaises(ValueError):
                merge_idea(saved, value)

    def test_ambiguous_todo_rejected(self):
        with self.assertRaises(ValueError):
            merge_idea('## TODO\n## TODO\n', self.idea)

    def test_guarded_store_writer_preview_apply_and_conflict(self):
        import hashlib
        import tempfile
        from task_store import TaskStore, frontmatter
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'tasks').mkdir()
            store = TaskStore(root, 'silverbullet-v1')
            files, *_ = store.write_candidates([dict(title='Fixture', client='Example', project='Example',
                                                     execution_bucket='do', source_system='ai-system')])
            path = files[0]
            identity = frontmatter(path.read_text())['task_id']
            before = path.read_bytes()
            digest = hashlib.sha256(before).hexdigest()
            idea = dict(self.idea, parent_task_id=identity)
            self.assertFalse(store.write_idea(identity, idea, digest)['writes'])
            self.assertEqual(path.read_bytes(), before)
            self.assertTrue(store.write_idea(identity, idea, digest, apply=True)['writes'])
            with self.assertRaises(ValueError):
                store.write_idea(identity, idea, digest, apply=True)


    def test_addition_contract_is_reachable_and_keeps_authority(self):
        core = Path(__file__).resolve().parents[2] / 'ai/core'
        policy = (core / 'task-efficiency.md').read_text()
        section = policy.split('## Addition signals and preserving the main plan', 1)[1]
        for alias in ('btw', 'btw.', 'by the way', 'dodatkowo', 'w dodatku', 'dodatk.', 'dodat.'):
            self.assertIn('`' + alias + '`', section)
        for term in ('complete token or phrase boundaries', 'btw = by the way',
                     'quoted examples', 'next safe action', 'Read-only',
                     'pending durable capture', 'No extra agent', 'before its finish stage'):
            self.assertIn(term, section)
        for name in ('command-routing.md', 'task-management.md'):
            self.assertIn('preserving the main plan', ' '.join((core / name).read_text().split()))

    def test_all_aliases_preserve_goal_resume_plan_and_original_wording(self):
        main = ('## Checkpoint OSNR\nGoal: finish main build\nStage: build\n'
                'Next: verify build\n' + self.text)
        old_plan = '<!-- plan -->\n- [x] Start\n- [ ] Build\n- [ ] Finish\n'
        main = main.replace('- [x] Ręczny etap\n', old_plan)
        for i, alias in enumerate(('btw', 'btw.', 'BTw.', 'by the way', 'dodatkowo', 'w dodatku', 'dodatk.', 'dodat.')):
            with self.subTest(alias=alias):
                idea = dict(self.idea, id='addition-' + str(i), text=alias + ' dodać eksport')
                saved = merge_idea(main, idea)
                self.assertEqual(saved.split('## TODO', 1)[0], main.split('## TODO', 1)[0])
                self.assertIn(old_plan, saved)
                self.assertEqual(saved.split('## Working dump')[1], main.split('## Working dump')[1])
                self.assertIn('- [ ] Ocenić pomysł — ' + idea['text'], saved)
                data = json.loads(re.search(r'<!-- idea-data (.+) -->', saved)[1])
                self.assertEqual(data, idea)
                self.assertEqual(merge_idea(saved, idea), saved)

    def test_multiple_additions_do_not_replace_main_or_each_other(self):
        one = dict(self.idea, id='first-addition', text='btw. dodać eksport')
        two = dict(self.idea, id='second-addition', text='dodat. zbadać inne zadanie', kind='unrelated')
        saved = merge_idea(merge_idea(self.text, one), two)
        self.assertEqual(saved.count('- [ ] Ocenić pomysł'), 2)
        self.assertIn('- [x] Ręczny etap', saved)
        self.assertEqual(merge_idea(merge_idea(saved, one), two), saved)
        for kind in ('correction', 'unrelated'):
            idea = dict(self.idea, id='explicit-' + kind, text='btw. popraw wymaganie', kind=kind)
            self.assertIn('"kind": "' + kind + '"', merge_idea(self.text, idea))

    def test_accepted_addition_extends_actual_plan_before_finish(self):
        import hashlib
        import tempfile
        from task_store import TaskStore, frontmatter
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / 'tasks').mkdir()
            store = TaskStore(root, 'silverbullet-v1')
            files, *_ = store.write_candidates([dict(title='Fixture', client='Example', project='Example',
                                                     execution_bucket='do', source_system='ai-system')])
            path = files[0]; identity = frontmatter(path.read_text())['task_id']
            digest = lambda: hashlib.sha256(path.read_bytes()).hexdigest()
            plan = dict(id='main-plan', stages=[dict(id='start', text='Start main'),
                        dict(id='build', text='Build main'), dict(id='finish', text='Finish main')])
            store.write_plan(identity, plan, digest(), apply=True)
            before = path.read_bytes()
            idea = dict(self.idea, parent_task_id=identity, parent_stage_id='build', text='btw. add export')
            self.assertFalse(store.write_idea(identity, idea, digest())['writes'])
            self.assertEqual(path.read_bytes(), before)
            store.write_idea(identity, idea, digest(), apply=True)
            self.assertNotIn('main-plan:export', path.read_text())
            store.write_idea(identity, dict(idea, disposition='accepted', evidence='synthetic spec'), digest(), apply=True)
            plan['stages'].insert(-1, dict(id='export', text='Implement accepted export'))
            store.write_plan(identity, plan, digest(), apply=True)
            saved = path.read_text()
            self.assertLess(saved.index('main-plan:export'), saved.index('main-plan:finish'))
            self.assertIn('- [x] Ocenić pomysł', saved)
            self.assertIn('- [ ] Implement accepted export', saved)


if __name__ == '__main__':
    unittest.main()
