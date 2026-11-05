import json
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


if __name__ == '__main__':
    unittest.main()
