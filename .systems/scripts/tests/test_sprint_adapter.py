"""Source-verified System delegation; no second Sprint executor."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(SCRIPTS))
import sprint_adapter


class Adapter(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        for rel in sprint_adapter.FILES:
            p=self.root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('synthetic '+rel)
        self.cap=self.root/'.systems/ai/capabilities/sprint-iteration-v1.json';self.cap.parent.mkdir(parents=True)
        self.value={'schema':1,'capability':'sprint-iteration-v1','contract_version':1,'authority':'none','files':{rel:hashlib.sha256((self.root/rel).read_bytes()).hexdigest() for rel in sprint_adapter.FILES}}
        self.save()
    def save(self):self.cap.write_text(json.dumps(self.value))
    def tearDown(self):self.temp.cleanup()
    def test_supported(self):self.assertTrue(sprint_adapter.support(self.root)['supported'])
    def test_unknown_schema(self):
        self.value['contract_version']=2;self.save()
        with self.assertRaises(ValueError):sprint_adapter.support(self.root)
    def test_unknown_fields(self):
        self.value['approved']=True;self.save()
        with self.assertRaises(ValueError):sprint_adapter.support(self.root)
    def test_malformed_file_map_rejected(self):
        self.value['files']=list(self.value['files']);self.save()
        with self.assertRaises(ValueError):sprint_adapter.support(self.root)
    def test_changed_source(self):
        (self.root/'.systems/scripts/sprint_iteration.py').write_text('changed')
        with self.assertRaises(ValueError):sprint_adapter.support(self.root)
    def test_missing_source(self):
        (self.root/'.systems/scripts/manage-sprint').unlink()
        with self.assertRaises(ValueError):sprint_adapter.support(self.root)
    def test_linked_source(self):
        p=self.root/'.systems/scripts/manage-sprint';p.unlink();p.symlink_to(self.cap)
        with self.assertRaises(ValueError):sprint_adapter.support(self.root)
    def test_missing_capability(self):
        self.cap.unlink()
        with self.assertRaises(ValueError):sprint_adapter.support(self.root)
    def test_old_cleanup_remains_supported_without_sprint(self):
        import task_cleanup_adapter as cleanup
        value={'schema':1,'capability':'task-resource-cleanup-v1','contract_version':1,'authority':'none','files':{}}
        for rel in cleanup.FILES:
            p=self.root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('legacy fixture')
            value['files'][rel]=hashlib.sha256(p.read_bytes()).hexdigest()
        cap=self.root/'.systems/ai/capabilities/task-resource-cleanup-v1.json';cap.write_text(json.dumps(value))
        self.assertTrue(cleanup.support(self.root)['supported'])
        with self.assertRaises(ValueError):cleanup.support(self.root,require_sprint=True)
        executor=self.root/'.systems/scripts/task_resource_cleanup.py';executor.write_text('import sprint_iteration')
        value['files']['.systems/scripts/task_resource_cleanup.py']=hashlib.sha256(executor.read_bytes()).hexdigest();cap.write_text(json.dumps(value))
        with self.assertRaises(ValueError):cleanup.support(self.root)
        rel='.systems/scripts/sprint_iteration.py';value['files'][rel]=hashlib.sha256((self.root/rel).read_bytes()).hexdigest();cap.write_text(json.dumps(value))
        self.assertTrue(cleanup.support(self.root,require_sprint=True)['supported'])

    def test_no_local_state_engine(self):self.assertFalse((SCRIPTS/'sprint_iteration.py').exists())
    def test_unavailable_has_no_effect(self):
        before=sorted(str(p) for p in self.root.rglob('*'))
        r=subprocess.run([str(SCRIPTS/'manage-sprint'),'--workflow-root',str(self.root),'--check-support'],capture_output=True)
        self.assertEqual(r.returncode,0);self.assertEqual(before,sorted(str(p) for p in self.root.rglob('*')))


if __name__=='__main__':unittest.main()
