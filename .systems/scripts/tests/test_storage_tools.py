"""Exercise the source-bound consumer through the public System CLI."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class StorageToolsTests(unittest.TestCase):
    def test_canonical_argument_reaches_worktree_consumer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scripts = root / '.systems/scripts'
            scripts.mkdir(parents=True)
            names = ('manage-storage-capacity', 'storage_capacity.py', 'create-source-worktree',
                     'analyze-task-retrospective', 'task_retrospective.py',
                     'task_resource_cleanup.py', 'durable_runtime.py')
            for name in names:
                (scripts / name).write_text('# synthetic dependency\n')
            consumer = scripts / 'create-source-worktree'
            consumer.write_text('#!/usr/bin/env python3\nimport json,sys\nprint(json.dumps(sys.argv[1:]))\n')
            consumer.chmod(0o755)
            capability = root / '.systems/ai/capabilities/managed-storage-v1.json'
            capability.parent.mkdir(parents=True)
            capability.write_text(json.dumps(dict(schema=1, capability='managed-storage-v1', authority='none',
                files={'.systems/scripts/' + name: hashlib.sha256((scripts / name).read_bytes()).hexdigest()
                       for name in names})))
            args = [str(ROOT / 'storage-tools'), '--canonical', str(root), '--workflow-root', str(root),
                    'create-source-worktree', '--branch', 'codex/example']
            result = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), ['--canonical', str(root), '--branch', 'codex/example'])
            consumer.write_text(consumer.read_text() + '# drift\n')
            stale = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(stale.returncode, 2)
            self.assertIn('source differs', stale.stderr)


if __name__ == '__main__':
    unittest.main()
