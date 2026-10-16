import unittest,tempfile,sys,os,copy
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import dreaming_guard as g

def policy(root,owner='workspace-a',kind='workspace',source_class='work'):
    return {'schema_version':1,'owner_workspace_id':owner,'authority_ref':'synthetic-owner-session','profile':'work-materials',
            'roots':[{'source_root_id':'root-a','locator':str(root),'kind':kind,'bindings':[{'prefix':'','project_id':'project-a','owner_workspace_id':owner,'source_class':source_class}]}],
            'limits':{'files':1000,'file_bytes':1048576,'total_bytes':67108864,'entries':10000,'chunk_bytes':16384},
            'sharing':{'recipient':None,'mode':'none','authority_ref':None}}

class Sources(unittest.TestCase):
    def test_denied_never_read(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'.env').write_text('secret');(root/'good.md').write_text('A work note')
            with patch.object(g,'read_file',wraps=g.read_file) as opened:
                result,body=g.inspect(policy(root),read=True)
                self.assertEqual(opened.call_count,1);self.assertEqual(len(body),1)
                self.assertEqual(result['inventory'][0]['disposition'],'excluded')
    def test_same_class_every_origin(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'renamed.md').write_text('private')
            for kind in ['workspace','repository','workflow']:
                with patch.object(g,'read_file') as opened:
                    result,body=g.inspect(policy(root,kind=kind,source_class='raw-personal'),read=True)
                    opened.assert_not_called();self.assertFalse(body)
    def test_secret_prescreen_and_links(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'renamed.md').write_text('api_key=synthetic');(root/'link.md').symlink_to(root/'renamed.md')
            result,body=g.inspect(policy(root),read=True);self.assertFalse(body)
            self.assertEqual({r['disposition'] for r in result['inventory']},{'blocked'})
    def test_alias_overlap_ownership(self):
        with tempfile.TemporaryDirectory() as td:
            v=policy(Path(td));v['roots'].append(copy.deepcopy(v['roots'][0]));v['roots'][1]['source_root_id']='root-b'
            with self.assertRaises(g.GuardError):g.registry(v)
            v=policy(Path(td));v['roots'][0]['bindings'].append(dict(prefix='child',project_id='project-b',owner_workspace_id='workspace-b',source_class='work'))
            with self.assertRaises(g.GuardError):g.registry(v)
    def test_limits_missing_unsupported(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'a.md').write_text('abc');(root/'b.pdf').write_bytes(b'x')
            result,_=g.inspect(policy(root),read=True);self.assertIn('unsupported',[r['disposition'] for r in result['inventory']])
            value=policy(root);value['limits']['file_bytes']=1
            result,body=g.inspect(value,read=True);self.assertFalse(body)
            value=policy(root/'missing');result,_=g.inspect(value);self.assertEqual(result['inventory'][0]['disposition'],'missing')
    def test_hardlink(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'one.md').write_text('text');os.link(root/'one.md',root/'two.md')
            result,body=g.inspect(policy(root),read=True);self.assertFalse(body)
    def test_metadata_only_and_narrow(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'one.md').write_text('text')
            with patch.object(g,'read_file') as opened:g.inspect(policy(root));opened.assert_not_called()
            value=policy(root);value['profile']='narrow-only';result,body=g.inspect(value,read=True);self.assertFalse(body)
    def test_nested_roots_require_disjoint_read_scopes(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'notes').mkdir();(root/'notes/a.md').write_text('Work note')
            nested=root/'repo';nested.mkdir();(nested/'ai-workflow-workspace').mkdir();(nested/'ai-workflow-workspace/b.md').write_text('Project note')
            value=policy(root);value['roots'][0]['bindings'][0]['prefix']='notes'
            child=copy.deepcopy(value['roots'][0]);child.update(source_root_id='root-b',locator=str(nested),kind='repository');child['bindings'][0]['prefix']='ai-workflow-workspace';value['roots'].append(child)
            result,body=g.inspect(value,read=True);self.assertEqual(len(body),2)
            value['roots'][0]['bindings'][0]['prefix']=''
            with self.assertRaises(g.GuardError):g.registry(value)
    def test_root_replacement_during_read_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);root=base/'source';root.mkdir();(root/'note.md').write_text('original work')
            real=os.read;changed=False
            def race(fd,size):
                nonlocal changed
                data=real(fd,size)
                if not changed:
                    changed=True;root.rename(base/'old-source');root.mkdir();(root/'note.md').write_text('replacement work')
                return data
            with patch.object(os,'read',side_effect=race),self.assertRaises(g.GuardError):g.read_file(str(root),'note.md',1024)

if __name__=='__main__':unittest.main()
