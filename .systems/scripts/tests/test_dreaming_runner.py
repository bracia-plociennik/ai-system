import os,sys,tempfile,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_dreaming_sources import policy
import dreaming_runner as r

# Explicit override is portable across canonical checkouts and auxiliary worktrees.
_test_root = Path(__file__).resolve()
_candidates = [_test_root.parents[5]/'ai-workflow/ai-workflow-dreaming-wep-dev',
               _test_root.parents[4]/'ai-workflow-dreaming-wep-dev',
               _test_root.parents[3]/'ai-workflow']
PRODUCER = Path(os.environ['DREAMING_TEST_PROVIDER']) if os.environ.get('DREAMING_TEST_PROVIDER') else next(
    (p for p in _candidates if (p/'.systems/scripts/dreaming_evidence_reader.py').is_file()), _candidates[-1])
def capabilities():
    import subprocess
    return json.loads(subprocess.check_output([sys.executable,'-B',str(PRODUCER/'.systems/scripts/dreaming-evidence'),'capabilities'],text=True))['source_fingerprints']
def analysis(state,text='Source records a plan, execution unknown.'):
    rows=[x for x in state['envelope']['inventory'] if x['read_receipt']]
    return {'analyzer':state['analyzer'],'policy_digest':r.digest(state['policy']),
            'read_receipt_ids':[x['read_receipt']['receipt_id'] for x in rows],
            'covered_chunks':[c['chunk_id'] for x in rows for c in x['read_receipt']['chunk_map']],
            'findings':[{'finding_id':'finding-a','source_hashes':[rows[0]['source_ref']['sha256']],
                         'facts':[text],'inferences':[],'unknowns':['time and execution'],'native_state':'unknown','native_quality':'unknown'}] if rows else [],
            'coverage':'complete','unresolved_conflicts':[]}
def begin(root,workspace,name='run-a',previous=None):
    return r.plan(workspace,name,policy(root),PRODUCER,capabilities(),{'id':'test-reviewer','version':'v1','policy_digest':'a'*64},previous)
def deliver(workspace,name,state):
    for row in state['envelope']['inventory']:
        if row['read_receipt']:
            for c in row['read_receipt']['chunk_map']:r.read(workspace,name,c['chunk_id'])

class Runner(unittest.TestCase):
    def test_read_without_analysis_partial(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);root=base/'source';root.mkdir();ws=base/'ws';ws.mkdir();(root/'note.md').write_text('A plan')
            state=begin(root,ws);deliver(ws,'run-a',state);result=r.finalize(ws,'run-a');self.assertEqual(result['result'],'partial')
            self.assertEqual(r.finalize(ws,'run-a'),result)
    def test_complete_reuse_drift(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);root=base/'source';root.mkdir();ws=base/'ws';ws.mkdir();file=root/'note.md';file.write_text('A plan')
            state=begin(root,ws);deliver(ws,'run-a',state);r.submit(ws,'run-a',analysis(state));self.assertEqual(r.finalize(ws,'run-a')['result'],'complete')
            reused=begin(root,ws,'run-b','run-a');self.assertEqual(reused['envelope']['inventory'][0]['disposition'],'reused-unchanged');self.assertEqual(r.finalize(ws,'run-b')['result'],'complete')
            file.write_text('A changed plan')
            with self.assertRaises(r.GuardError):r.finalize(ws,'run-a')
    def test_undisclosed_analysis(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);root=base/'source';root.mkdir();ws=base/'ws';ws.mkdir();(root/'note.md').write_text('A plan')
            state=begin(root,ws)
            with self.assertRaises(r.GuardError):r.submit(ws,'run-a',analysis(state))
    def test_owner_policy_and_provider_drift(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);root=base/'source';root.mkdir();ws=base/'ws';ws.mkdir();(root/'note.md').write_text('A plan')
            cap=capabilities();cap['.systems/scripts/dreaming_guard.py']='0'*64
            with self.assertRaises(r.GuardError):r.plan(ws,'run-a',policy(root),PRODUCER,cap,{'id':'test','version':'v1','policy_digest':'a'*64})
    def test_atomic_conflict_and_lock(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);r.save(root,'report.json',{'a':1});r.save(root,'report.json',{'a':1})
            with self.assertRaises(r.GuardError):r.save(root,'report.json',{'a':2})
            with r.lock(root):
                with self.assertRaises(FileExistsError):
                    with r.lock(root):pass
    def test_unicode_policy_has_one_digest(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);root=base/'żółć';root.mkdir();ws=base/'ws';ws.mkdir();(root/'notatka.md').write_text('Zażółć. Plan only.')
            state=begin(root,ws);self.assertEqual(state['envelope']['policy_digest'],r.digest(state['policy']))
            deliver(ws,'run-a',state);r.submit(ws,'run-a',analysis(state));self.assertEqual(r.finalize(ws,'run-a')['result'],'complete')
    def test_workspace_output_does_not_feed_back(self):
        with tempfile.TemporaryDirectory() as td:
            ws=Path(td);(ws/'note.md').write_text('A work plan')
            state=begin(ws,ws);deliver(ws,'run-a',state);r.submit(ws,'run-a',analysis(state))
            self.assertEqual(r.finalize(ws,'run-a')['result'],'complete')
            reused=begin(ws,ws,'run-b','run-a')
            self.assertEqual(r.finalize(ws,'run-b')['result'],'complete')
            self.assertEqual(sum(row['disposition']=='reused-unchanged' for row in reused['envelope']['inventory']),1)
            self.assertTrue(all(row['read_receipt'] is None for row in reused['envelope']['inventory'] if row['relative_path']=='dreams'))
    def test_changed_source_preserves_case_history(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);root=base/'source';root.mkdir();ws=base/'ws';ws.mkdir();file=root/'note.md';file.write_text('A plan')
            state=begin(root,ws);deliver(ws,'run-a',state);r.submit(ws,'run-a',analysis(state));r.finalize(ws,'run-a')
            old=r.load(ws/'dreams/runs/run-a/candidates.json')[0]
            file.write_text('A changed plan')
            state=begin(root,ws,'run-b','run-a');deliver(ws,'run-b',state);r.submit(ws,'run-b',analysis(state,'A changed plan, execution unknown.'));r.finalize(ws,'run-b')
            new=r.load(ws/'dreams/runs/run-b/candidates.json')[0]
            self.assertEqual(new['candidate_id'],old['candidate_id']);self.assertEqual(new['revision'],2)
            self.assertEqual(new['predecessor_hash'],r.digest(old));self.assertIsNone(new['work_id'])

if __name__=='__main__':unittest.main()
