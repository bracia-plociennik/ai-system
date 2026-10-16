import unittest,sys,tempfile,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.path.insert(0,str(Path(__file__).resolve().parent))
import dreaming_overview as v
import dreaming_runner as r
from test_dreaming_sources import policy
from test_dreaming_runner import capabilities,PRODUCER,deliver,analysis

class Overview(unittest.TestCase):
    def fixture(self,base,owner='workspace-a',mode='counts-only'):
        root=base/'repo';root.mkdir(parents=True);ws=base/'ws';ws.mkdir();(root/'note.md').write_text('A work plan. Time unknown.')
        p=policy(root,owner);p['sharing']={'recipient':'owner','mode':mode,'authority_ref':'synthetic-owner-sharing'}
        state=r.plan(ws,'run-a',p,PRODUCER,capabilities(),{'id':'test','version':'v1','policy_digest':'a'*64});deliver(ws,'run-a',state);r.submit(ws,'run-a',analysis(state));completion=r.finalize(ws,'run-a')
        return ws,p,completion
    def test_two_workspace_counts_no_paths(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);inputs=[]
            for owner in ['workspace-a','workspace-b']:
                ws,p,c=self.fixture(base/owner,owner);inputs.append(dict(projection=v.projection(ws,'run-a',p,'owner'),completion=c,current_scope=p))
            result=v.overview(inputs,'owner');self.assertEqual(len(result['scopes']),2);self.assertNotIn(str(base),str(result));self.assertNotIn('workspace-a',str(result));self.assertTrue(all(not s['reviewed_text'] for s in result['scopes']))
    def test_revoked_wrong_recipient_and_drift(self):
        with tempfile.TemporaryDirectory() as td:
            ws,p,c=self.fixture(Path(td));packet=v.projection(ws,'run-a',p,'owner')
            with self.assertRaises(v.ProtocolError):v.validate(packet,c,p,'stranger')
            p['sharing']['mode']='none';result=v.overview([dict(projection=packet,completion=c,current_scope=p)],'owner');self.assertEqual(result['scopes'][0]['state'],'unavailable')
    def test_exact_reviewed_text_and_private(self):
        with tempfile.TemporaryDirectory() as td:
            ws,p,c=self.fixture(Path(td),mode='reviewed-text');draft=v.projection(ws,'run-a',p,'owner');cid=draft['projection']['candidate_ids'][0]
            texts=[dict(candidate_id=cid,title='Reusable campaign helper',reason='Replay evidence is missing')]
            draft=v.projection(ws,'run-a',p,'owner',texts);review=dict(projection_hash=draft['projection_hash'],recipient='owner',approved_by='owner',authority_ref='synthetic-exact-review')
            packet=v.projection(ws,'run-a',p,'owner',texts,review);v.validate(packet,c,p,'owner')
            packet['projection']['reviewed_text'][0]['title']='Changed'
            with self.assertRaises(v.ProtocolError):v.validate(packet,c,p,'owner')
            texts[0]['title']='/home/private/name/topic'
            with self.assertRaises(v.ProtocolError):v.projection(ws,'run-a',p,'owner',texts)
    def test_aggregator_never_reads_private_corpus(self):
        from unittest.mock import patch
        with patch.object(v,'load',side_effect=AssertionError('unexpected read')):
            result=v.overview([dict(projection={},completion={},current_scope={})],'owner');self.assertEqual(result['scopes'][0]['state'],'unavailable')
    def test_local_export_rechecks_current_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            ws,p,c=self.fixture(Path(td));(Path(td)/'repo/note.md').write_text('Changed ignored source')
            with self.assertRaises(ValueError):v.projection(ws,'run-a',p,'owner')

if __name__=='__main__':unittest.main()
