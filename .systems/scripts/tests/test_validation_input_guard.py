"""Public runner/guard regressions with actual concurrent processes and synthetic data."""
from pathlib import Path
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT/'.systems/scripts'
spec=importlib.util.spec_from_file_location('guard_test_subject',SCRIPTS/'validation_input_guard.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)

class GuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='validation-guard-test-')
        self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)
        self.repo=self.base/'repo';self.repo.mkdir()
        self.scripts=self.repo/'.systems/scripts';self.scripts.mkdir(parents=True)
        self.source=self.repo/'.systems/payload.txt';self.source.write_text('source v1\n')
        self.runtime=self.repo/'workspace/projects/selected';self.runtime.mkdir(parents=True)
        self.input=self.runtime/'status.md';self.input.write_text('input v1\n')
        subprocess.run(['git','init','-q',str(self.repo)],check=True)
        self.git('config','user.name','Synthetic Test');self.git('config','user.email','test@example.invalid')
        (self.repo/'.gitignore').write_text('workspace/\n')
        self.commit()
    def git(self,*args):
        return subprocess.run(['git','-C',str(self.repo),*args],check=True,capture_output=True)
    def commit(self):
        self.git('add','.');self.git('commit','-qm','synthetic')
    def test_source_identity_ignores_tracked_and_untracked_runtime_writes(self):
        # Force tracked runtime to reproduce a historical dev workspace too.
        self.git('add','-f','workspace/projects/selected/status.md');self.git('commit','-qm','runtime')
        before=g.product_digest(self.repo);guard=g.Guard(self.repo)
        child=subprocess.Popen([sys.executable,'-c','from pathlib import Path;import sys; p=Path(sys.argv[1]); p.write_text("changed runtime"); (p.parent/"new.log").write_text("peer")',str(self.input)])
        self.assertEqual(child.wait(),0)
        self.assertEqual(g.product_digest(self.repo),before);self.assertEqual(guard.finish()['state'],'stable')
    def test_source_add_delete_mode_and_restore_invalidate(self):
        for action in ['add','delete','mode','restore']:
            with self.subTest(action=action):
                path=self.source;path.write_text('source v1\n');path.chmod(0o644)
                (self.repo/'.systems/new.txt').unlink(missing_ok=True)
                guard=g.Guard(self.repo)
                if action=='add':(self.repo/'.systems/new.txt').write_text('new')
                elif action=='delete':path.unlink()
                elif action=='mode':path.chmod(0o755)
                else:path.write_text('different');path.write_text('source v1\n')
                with self.assertRaises(g.InputChanged):guard.finish()
    def test_selected_inputs_guard_siblings_and_exact_outputs(self):
        output=self.runtime/'output.log';output.write_text('start')
        guard=g.Guard(self.repo,[self.runtime],[output])
        output.write_text('more output')
        (self.runtime.parent/'sibling').mkdir();(self.runtime.parent/'sibling/status.md').write_text('peer')
        self.assertEqual(guard.finish()['state'],'stable')
        self.input.write_text('changed')
        with self.assertRaises(g.InputChanged):guard.finish()
    def test_missing_link_special_and_source_output_fail_closed(self):
        with self.assertRaises(g.InputChanged):g.Guard(self.repo,[self.base/'missing'])
        link=self.repo/'.systems/link';link.symlink_to(self.base)
        with self.assertRaises(g.InputChanged):g.Guard(self.repo)
        link.unlink()
        with self.assertRaises(g.InputChanged):g.Guard(self.repo,[self.runtime],[self.repo/'.systems'])
        fifo=self.runtime/'fifo';os.mkfifo(fifo)
        with self.assertRaises(g.InputChanged):g.Guard(self.repo,[self.runtime])
    def test_read_twice_detects_preflight_change_and_namespace_replace(self):
        guard=g.Guard(self.repo,[self.runtime]);self.runtime.rename(self.runtime.with_name('old'))
        self.runtime.mkdir();self.input.write_text('input v1\n')
        with self.assertRaises(g.InputChanged):guard.finish()
    def install_runner_fixture(self):
        workflow=(SCRIPTS/'validate-workflow').exists()
        names=['validation_input_guard.py','durable_runtime.py']
        if workflow:
            names+=['validate-workflow','resolve-workflow-env','run-with-timeout']
            (self.scripts/'lib').mkdir()
            for n in ['validation-timing.py','validation-scope.py']:
                shutil.copy2(SCRIPTS/'lib'/n,self.scripts/'lib'/n)
            checks=['check-required-artifacts','check-branch-policy','check-naming','check-status-consistency','check-qa-evidence','check-full-qa-verification','check-contract-compliance']
            args=[str(self.scripts/'validate-workflow'),'--profile','fast','--project','selected']
        else:
            names+=['validate-ai-system','validation_runner.py','validation_support.py','execution_efficiency.py','smoke_coverage.py']
            checks=['check-privacy-boundary','check-required-artifacts']
            (self.scripts/'validation-dependencies.json').write_text(json.dumps({'checks':{n:{'dependencies':[]} for n in checks}}))
            args=[str(self.scripts/'validate-ai-system'),'--profile','fast','--validation-input-root',str(self.runtime)]
        for n in names:shutil.copy2(SCRIPTS/n,self.scripts/n)
        for n in checks:(self.scripts/n).write_text('#!/bin/sh\nexit 0\n');(self.scripts/n).chmod(0o755)
        hook=self.scripts/checks[0]
        hook.write_text('#!/usr/bin/env python3\nimport os,time\nfrom pathlib import Path\nPath(os.environ["VCG_READY"]).touch()\nwhile not Path(os.environ["VCG_GO"]).exists(): time.sleep(.01)\nraise SystemExit(int(os.environ.get("VCG_EXIT","0")))\n')
        hook.chmod(0o755);self.commit()
        env={k:v for k,v in os.environ.items() if not k.startswith(('AI_SYSTEM_','AI_WORKFLOW_','TARGET_REPO_ROOT','TASK_RESOURCE_'))}
        env.update(AI_WORKFLOW_WORKSPACE_HOME=str(self.repo/'workspace'),VCG_READY=str(self.base/'ready'),VCG_GO=str(self.base/'go'),PYTHONDONTWRITEBYTECODE='1')
        return args,env
    def run_concurrent(self,action,check_exit=0):
        args,env=self.install_runner_fixture();env['VCG_EXIT']=str(check_exit)
        log=self.runtime/'run.log'
        with log.open('w') as stream:
            process=subprocess.Popen(args,cwd=self.repo,env=env,stdout=stream,stderr=subprocess.STDOUT)
            try:
                deadline=time.monotonic()+20
                while not (self.base/'ready').exists():
                    if process.poll() is not None or time.monotonic()>deadline:
                        self.fail('runner never reached controlled check: '+log.read_text())
                    time.sleep(.02)
                action();(self.base/'go').touch();code=process.wait(timeout=30)
            finally:
                if process.poll() is None:process.kill();process.wait()
        return code,log.read_text()
    def test_public_untimed_runner_allows_other_project_writes_and_own_log(self):
        def write():
            sibling=self.runtime.parent/'other';sibling.mkdir()
            p=subprocess.run([sys.executable,'-c','from pathlib import Path;import sys;(Path(sys.argv[1])/"check.log").write_text("peer")',str(sibling)])
            self.assertEqual(p.returncode,0)
        code,log=self.run_concurrent(write)
        self.assertEqual(code,0,log);self.assertIn('COMPLETE' if (SCRIPTS/'validate-workflow').exists() else 'VALIDATION_RESULT',log)
    def test_public_untimed_runner_rejects_source_changes(self):
        code,log=self.run_concurrent(lambda:self.source.write_text('changed while check running'))
        self.assertEqual(code,75,log);self.assertIn('input-changed',log)
    def test_public_runner_rejects_selected_input_changes(self):
        code,log=self.run_concurrent(lambda:self.input.write_text('changed while check running'))
        self.assertEqual(code,75,log);self.assertIn('input-changed',log)
    def test_public_runner_preserves_original_failed_exit(self):
        code,log=self.run_concurrent(lambda:None,check_exit=7)
        self.assertEqual(code,7,log)
        self.assertNotIn('result=pass',log)

    def test_public_runner_timeout_is_not_success(self):
        args,env=self.install_runner_fixture()
        result=subprocess.run(args+['--timeout-seconds','0.5'],cwd=self.repo,env=env,capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,124,result.stdout+result.stderr)
        self.assertIn('timeout',result.stdout+result.stderr)
        self.assertNotIn('result=pass',result.stdout)
    def test_unpacked_product_still_gets_a_content_guard(self):
        shutil.rmtree(self.repo/'.git')  # Only the owned disposable synthetic fixture.
        (self.base/'.git').mkdir()  # Unrelated broken ancestor must not own an unpacked source.
        guard=g.Guard(self.repo)
        self.assertEqual(guard.finish()['state'],'stable')
        self.source.write_text('changed archive source')
        with self.assertRaises(g.InputChanged):guard.finish()
    def test_unreadable_input_does_not_get_success(self):
        self.input.chmod(0)
        try:
            if os.geteuid()!=0:
                with self.assertRaises((OSError,ValueError)):g.Guard(self.repo,[self.runtime])
        finally:self.input.chmod(0o600)
    def test_comparison_keeps_legacy_and_rejects_mixed_source_scopes(self):
        if not (SCRIPTS/'validate-workflow').exists():
            return  # System has a separate frozen comparison format, unchanged.
        import importlib.machinery
        import types
        loader=importlib.machinery.SourceFileLoader('comparison_guard_test',str(SCRIPTS/'report-validation-comparison'))
        comparison=types.ModuleType(loader.name);comparison.__file__=loader.path;loader.exec_module(comparison)
        digest=g.product_digest(self.repo);manifests=[]
        old_cwd=Path.cwd()
        try:
            os.chdir(self.repo)
            for i in range(3):
                timing=self.base/('run-'+str(i)+'.tsv');output=self.base/('run-'+str(i)+'.json')
                run=digest+'-synthetic-'+str(i)
                rows=[['smoke-test','core','1','pass','smoke-all','2',run,'child','smoke-suite-wall'],
                      ['smoke-suite-wall','smoke','2','pass','smoke-all','2',run,'wall','validation-wall'],
                      ['check-validator-smoke-tests','smoke','2','pass','full','2',run,'child','validation-wall'],
                      ['validation-wall','wall','3','pass','full','2',run,'wall','none']]
                timing.write_text(comparison.timing.HEADER+''.join('\t'.join(row)+'\n' for row in rows))
                comparison.capture(types.SimpleNamespace(timing=str(timing),output=str(output),scope_fingerprint='synthetic',input_fingerprint='synthetic',setup_regime='synthetic'))
                self.assertEqual(comparison.load_manifest(output)['source_scope'],'product-v1')
                manifests.append(str(output))
            self.assertEqual(comparison.summarize(types.SimpleNamespace(manifests=manifests))['result'],'complete-baseline')
            legacy=json.loads(Path(manifests[0]).read_text());legacy['schema_version']=2;legacy.pop('source_scope')
            path=self.base/'legacy.json';path.write_text(json.dumps(legacy));before=path.read_bytes()
            self.assertEqual(comparison.load_manifest(path)['source_scope'],'legacy-repository-v1')
            self.assertEqual(before,path.read_bytes())
            with self.assertRaisesRegex(ValueError,'drift'):
                comparison.summarize(types.SimpleNamespace(manifests=[str(path),*manifests[1:]]))
        finally:os.chdir(old_cwd)

if __name__=='__main__':unittest.main()
