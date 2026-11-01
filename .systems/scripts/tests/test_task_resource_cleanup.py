"""System consumer compatibility; Workflow remains the only executor."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
import durable_runtime
import task_cleanup_adapter


class Consumer(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        for name in task_cleanup_adapter.FILES:
            p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('fixture source '+name)
        import hashlib
        self.manifest={'schema':1,'capability':'task-resource-cleanup-v1','contract_version':1,'files':{p:hashlib.sha256((self.root/p).read_bytes()).hexdigest() for p in task_cleanup_adapter.FILES},'authority':'none'}
        self.path=self.root/'.systems/ai/capabilities/task-resource-cleanup-v1.json';self.path.parent.mkdir(parents=True)
        self.path.write_text(json.dumps(self.manifest))
    def tearDown(self):self.temp.cleanup()
    def test_complete_consumer_source(self):self.assertTrue(task_cleanup_adapter.support(self.root)['supported'])
    def test_missing_consumer_rejected(self):
        self.path.unlink()
        with self.assertRaises(ValueError):task_cleanup_adapter.support(self.root)
    def test_unknown_version_rejected(self):
        self.manifest['contract_version']=2;self.path.write_text(json.dumps(self.manifest))
        with self.assertRaises(ValueError):task_cleanup_adapter.support(self.root)
    def test_missing_input_rejected(self):
        self.manifest['files'].pop(next(iter(task_cleanup_adapter.FILES)));self.path.write_text(json.dumps(self.manifest))
        with self.assertRaises(ValueError):task_cleanup_adapter.support(self.root)
    def test_changed_executor_rejected(self):
        (self.root/'.systems/scripts/manage-task-resources').write_text('changed')
        with self.assertRaises(ValueError):task_cleanup_adapter.support(self.root)
    def test_linked_consumer_rejected(self):
        p=self.root/'.systems/scripts/manage-task-resources';p.unlink();p.symlink_to(self.path)
        with self.assertRaises(ValueError):task_cleanup_adapter.support(self.root)
    def test_protected_output_in_task_tree(self):
        with self.assertRaises(ValueError):durable_runtime.guard_output(self.root/'.worktrees/repo/work/qa.md')
    def test_system_has_no_deletion_engine(self):
        self.assertFalse((HERE/'task_resource_cleanup.py').exists())
        source=(HERE/'task_cleanup_adapter.py').read_text()
        self.assertNotIn('rmtree(',source);self.assertNotIn("'worktree', 'remove'",source)
    def test_failed_support_performs_no_delegation(self):
        self.path.unlink();before=set(self.root.rglob('*'))
        r=subprocess.run([str(HERE/'manage-task-resources'),'--workflow-root',str(self.root),'apply','--record',str(self.root/'nonexistent'),'--id','any','--approved'],capture_output=True)
        self.assertNotEqual(r.returncode,0);self.assertEqual(before,set(self.root.rglob('*')))

    def test_bound_worktree_uses_canonical_workflow_and_runtime(self):
        import agent_context
        bound=durable_runtime.load(HERE.parents[1])
        storage=Path(bound['workspace'])/'projects/task-resource-cleanup-v1/evidence' if bound else HERE.parents[1]/'ai-workflow-workspace'
        storage_created = not storage.exists()
        storage.mkdir(parents=True,exist_ok=True)
        # Model durable-vs-worktree roles for isolated OS-tmp smoke copies only.
        # Real bound-source runs retain the production OS-root guard unchanged.
        from contextlib import nullcontext
        from unittest.mock import patch
        adapter = patch.object(durable_runtime, 'OS_TEMP_ROOTS', ()) if any(storage.is_relative_to(r) for r in durable_runtime.OS_TEMP_ROOTS) else nullcontext()
        with adapter, tempfile.TemporaryDirectory(dir=storage) as raw:
            root=Path(raw);repo=root/'canonical';repo.mkdir()
            def git(path,*args):
                return subprocess.check_output(['git','-C',str(path),*args],stderr=subprocess.PIPE,text=True).strip()
            git(repo,'init');git(repo,'-c','user.name=Synthetic','-c','user.email=synthetic@example.invalid','commit','--allow-empty','-m','fixture')
            workflow=repo/'ai-workflow';workflow.mkdir();git(workflow,'init')
            for path in ['.systems/scripts/resolve-workflow-env','AGENTS.md']:
                file=workflow/path;file.parent.mkdir(parents=True,exist_ok=True);file.write_text('# synthetic fixture')
            git(workflow,'add','.');git(workflow,'-c','user.name=Synthetic','-c','user.email=synthetic@example.invalid','commit','-m','fixture')
            work=root/'.worktrees/repo/work';work.parent.mkdir(parents=True);git(repo,'worktree','add','-b','codex/fixture',str(work))
            runtime=root/'durable';runtime.mkdir();record=runtime/'work.json'
            record.write_text(json.dumps({'task_resource_cleanup':{'schema':1,'canonical':durable_runtime.identity(repo),'workspace':str(runtime)}}))
            durable_runtime.bind(work,repo,runtime,record)
            actual=agent_context.workflow_context(work,environment={'HOME':str(root)})
            self.assertEqual(actual,(workflow,runtime,'target'))
            with self.assertRaises(agent_context.ContextError):
                agent_context.workflow_context(work,environment={'HOME':str(root),'AI_WORKFLOW_WORKSPACE_HOME':str(repo)})
        if storage_created:
            try:
                storage.rmdir()
            except OSError:
                pass  # A concurrent test owns any newly present content.

    def test_explicit_canonical_can_select_consumer_without_existing_record(self):
        import shutil
        target=self.root/'target';nested=target/'ai-workflow'
        shutil.copytree(self.root/'.systems',nested/'.systems')
        result=subprocess.run([str(HERE/'manage-task-resources'),'--canonical',str(target),'--check-support'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(json.loads(result.stdout)['supported'])


if __name__=='__main__':unittest.main(verbosity=2)
