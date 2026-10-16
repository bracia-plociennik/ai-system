"""T01–T24 integration complements focused/native/legacy WEP evidence."""
import unittest,tempfile,sys,copy,json,os
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.path.insert(0,str(Path(__file__).resolve().parent))
import dreaming_runner as r
import dreaming_guard as g
from test_dreaming_sources import policy
from test_dreaming_runner import capabilities,PRODUCER,analysis,deliver

class Integration(unittest.TestCase):
    def test_shared_repository_split_and_multiple_roots(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);repo=base/'repo';repo.mkdir();other=base/'other';other.mkdir()
            for owner in ['workspace-a','workspace-b']:
                folder=repo/owner;folder.mkdir();(folder/'note.md').write_text(owner+' work, time unknown')
            (other/'note.md').write_text('Workspace A additional note')
            a=policy(repo);a['roots'][0]['bindings']=[dict(prefix=owner,project_id='project-a' if owner.endswith('a') else 'project-b',owner_workspace_id=owner,source_class='work') for owner in ['workspace-a','workspace-b']]
            a['roots'].append(dict(source_root_id='root-b',locator=str(other),kind='repository',bindings=[dict(prefix='',project_id='project-a',owner_workspace_id='workspace-a',source_class='work')]))
            result,body=g.inspect(a,read=True);self.assertEqual(len(body),2);self.assertTrue(all('workspace-b' not in key[1] for key in body))
            b=copy.deepcopy(a);b['owner_workspace_id']='workspace-b';result,body=g.inspect(b,read=True);self.assertEqual(len(body),1);self.assertEqual(next(iter(body))[1],'workspace-b/note.md')
    def test_limits_unknown_remaining_and_unsupported(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for i in range(10):(root/f'note-{i}.md').write_text('Data')
            value=policy(root);value['limits']['entries']=3;result,body=g.inspect(value,read=True)
            self.assertFalse(result['enumeration_complete']);self.assertLess(len(body),10)
    def test_partial_and_crash_before_completion(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);root=base/'repo';root.mkdir();ws=base/'ws';ws.mkdir();(root/'note.md').write_text('A plan')
            p=policy(root);state=r.plan(ws,'partial-a',p,PRODUCER,capabilities(),dict(id='test',version='v1',policy_digest='a'*64));deliver(ws,'partial-a',state)
            output=analysis(state);output['coverage']='partial';r.submit(ws,'partial-a',output)
            self.assertEqual(r.finalize(ws,'partial-a')['result'],'partial')
            state=r.plan(ws,'crash-a',p,PRODUCER,capabilities(),dict(id='test',version='v1',policy_digest='a'*64));deliver(ws,'crash-a',state);r.submit(ws,'crash-a',analysis(state))
            real=r.save
            def crash(path,name,value):
                if name=='completion.json':raise OSError('synthetic interruption')
                return real(path,name,value)
            with patch.object(r,'save',side_effect=crash),self.assertRaises(OSError):r.finalize(ws,'crash-a')
            self.assertFalse((r.directory(ws,'crash-a')/'completion.json').exists());self.assertEqual(r.finalize(ws,'crash-a')['result'],'complete')
    def test_chunk_and_identity_races(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);file=root/'note.md';file.write_text('original')
            real=os.read;changed=False
            def race(fd,size):
                nonlocal changed
                data=real(fd,size)
                if not changed:changed=True;file.write_text('changed content')
                return data
            with patch.object(os,'read',side_effect=race),self.assertRaises(g.GuardError):g.read_file(str(root),'note.md',1024)
    def test_changed_policy_does_not_reuse(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);root=base/'repo';root.mkdir();ws=base/'ws';ws.mkdir();(root/'note.md').write_text('A plan')
            p=policy(root);an=dict(id='test',version='v1',policy_digest='a'*64);state=r.plan(ws,'run-a',p,PRODUCER,capabilities(),an);deliver(ws,'run-a',state);r.submit(ws,'run-a',analysis(state));r.finalize(ws,'run-a')
            p['limits']['chunk_bytes']=8;state=r.plan(ws,'run-b',p,PRODUCER,capabilities(),an,'run-a');self.assertEqual(state['envelope']['inventory'][0]['disposition'],'pending')

if __name__=='__main__':unittest.main()
