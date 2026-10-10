import importlib.machinery
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
from local_paths import LocalPathError, resolve_path


class LocalPathsTests(unittest.TestCase):
    def test_mac_vps_custom_install_and_spaces(self):
        for home in ['/Users/sample', '/home/sample', '/srv/Home With Spaces']:
            env = {'HOME': home, 'AI_SYSTEM_HOME': home + '/custom-system',
                   'AI_SYSTEM_WORKSPACE_HOME': home + '/ambient'}
            ws = Path(home) / 'selected'
            self.assertEqual(resolve_path('~/tasks', environment=env), Path(home) / 'tasks')
            self.assertEqual(resolve_path('${AI_SYSTEM_HOME}/tasks', environment=env),
                             Path(home) / 'custom-system/tasks')
            self.assertEqual(resolve_path('$HOME/tasks', environment=env), Path(home) / 'tasks')
            self.assertEqual(resolve_path('${AI_SYSTEM_WORKSPACE_HOME}/work-evidence',
                                          workspace=ws, environment=env), ws / 'work-evidence')

    def test_relative_requires_explicit_base_and_does_not_create(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = resolve_path('missing/../repo', base=Path(tmp), allow_relative=True)
            self.assertEqual(path, Path(tmp) / 'repo')
            self.assertFalse(path.exists())
        with self.assertRaises(LocalPathError): resolve_path('relative')

    def test_invalid_and_recursive_expressions(self):
        for value in ['', '${UNKNOWN}/x', '${HOME', '$(touch /tmp/never)', '~someone/x',
                      '/tmp/\x00x', '${AI_SYSTEM_WORKSPACE_HOME}/x']:
            with self.subTest(value=value), self.assertRaises(LocalPathError):
                resolve_path(value, environment={'HOME': '/tmp'})
        for root in ['relative', '${HOME}/again', '/tmp/\nunsafe']:
            with self.assertRaises(LocalPathError):
                resolve_path('${HOME}/x', environment={'HOME': root})

    def test_symlink_and_parent_traversal_are_not_hidden(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / 'real').mkdir(); (root / 'alias').symlink_to(root / 'real')
            for tail in ['alias', 'alias/new', 'alias/../new']:
                with self.assertRaises(LocalPathError): resolve_path(root / tail)

    def test_default_system_root_is_module_install_not_cwd(self):
        self.assertEqual(resolve_path('${AI_SYSTEM_HOME}/tasks', environment={}),
                         SCRIPTS.parents[1] / 'tasks')

    def test_task_configuration_and_write_dedup_without_ui(self):
        loader = importlib.machinery.SourceFileLoader('task_candidates_paths', str(SCRIPTS/'propose-task-candidates'))
        spec = importlib.util.spec_from_loader(loader.name, loader); module = importlib.util.module_from_spec(spec); loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); tasks=root/'vault/TaskNotes/Tasks'; tasks.mkdir(parents=True)
            config=root/'config.md'; config.write_text('---\nenabled: true\nvault_path: ${AI_SYSTEM_HOME}/vault\n---\n')
            with patch.dict(os.environ, {'AI_SYSTEM_HOME': str(root)}):
                vault=module.task_vault_from_config(config, root)
            self.assertEqual(vault, root/'vault')
            candidate={'source_session_date':'2026-10-09','source_plan_item_id':'fixture-paths',
                       'source_type':'daily-check-in-v4','type':'task','title':'Fixture path task',
                       'description':'Synthetic fixture', 'status':'open','priority':'normal',
                       'tags':['AI','6d/do'],'contexts':[],'projects':[], 'project':'',
                       'scheduled':'','due':'','bucket':'do'}
            written,skipped,_,_=module.write_candidates([candidate],vault)
            self.assertEqual(len(written),1); self.assertEqual(skipped,0)
            task=written[0]; task.write_text(task.read_text().replace('status: "open"','status: "waiting"')+'\nOwner body preserved.\n')
            before=task.read_bytes()
            written,skipped,_,_=module.write_candidates([candidate],vault)
            self.assertEqual(written,[]); self.assertEqual(skipped,1)
            self.assertEqual(task.read_bytes(),before)
            with self.assertRaises(ValueError):
                config.write_text('---\nenabled: false\nvault_path: /tmp\n---\n')
                module.task_vault_from_config(config, root)

    def test_preflight_missing_variable_repo_and_invalid_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); env=dict(os.environ, AI_SYSTEM_HOME=str(root), PYTHONDONTWRITEBYTECODE='1')
            result=subprocess.run([sys.executable,'-B',str(SCRIPTS/'project-orchestration-preflight'),
                                   '--workspace', str(root), '--repo','${AI_SYSTEM_HOME}/missing'],
                                  env=env,capture_output=True,text=True)
            import json
            value=json.loads(result.stdout)
            self.assertEqual(value['source_availability'],'pending')
            self.assertEqual(value['result'],'blocked')
            self.assertFalse((root/'missing').exists())
            result=subprocess.run([sys.executable,'-B',str(SCRIPTS/'project-orchestration-preflight'),
                                   '--workspace','${UNKNOWN}/ws','--repo',str(root)],
                                  env=env,capture_output=True,text=True)
            self.assertEqual(json.loads(result.stdout)['result'],'blocked')

    def test_preflight_link_and_explicit_root_use_same_selected_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); repo=root/'repo'; repo.mkdir()
            subprocess.run(['git','init','-q',str(repo)],check=True)
            state=root/'project-state/demo'; state.mkdir(parents=True)
            (state/'links.md').write_text('repo-path: ${AI_SYSTEM_WORKSPACE_HOME}/repo\n')
            r=subprocess.run([sys.executable,'-B',str(SCRIPTS/'project-orchestration-preflight'),
                              '--workspace',str(root),'--repo','${AI_SYSTEM_HOME}/repo',
                              '--project-state','project-state/demo'],capture_output=True,text=True,
                             env=dict(os.environ,AI_SYSTEM_HOME=str(root),AI_SYSTEM_WORKSPACE_HOME='/ambient',PYTHONDONTWRITEBYTECODE='1'))
            import json
            value=json.loads(r.stdout)
            self.assertEqual(value['repository'],str(repo))
            self.assertNotIn('explicit repo and project-state repo-path disagree',value['blockers'])

    def test_freshness_explicit_variable_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); repo=root/'repo'; repo.mkdir()
            subprocess.run(['git','init','-q',str(repo)],check=True)
            r=subprocess.run([sys.executable,'-B',str(SCRIPTS/'report-workspace-freshness'),
                              '--repo','${AI_SYSTEM_HOME}/repo'],capture_output=True,text=True,
                             env=dict(os.environ,AI_SYSTEM_HOME=str(root),PYTHONDONTWRITEBYTECODE='1'))
            import json
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertEqual(json.loads(r.stdout)['repositories'][0]['path'],str(repo))


if __name__ == '__main__': unittest.main()
