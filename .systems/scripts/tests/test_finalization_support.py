import copy,json,tempfile,unittest,sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from finalization_support import preview,sha

class CompletionTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  (self.root/'input').write_text('v1');(self.root/'evidence').write_text('observed')
  self.record={'contract':'task-finalization-v1','work_id':'synthetic','kind':'code','dod':'Bounded result','approval_reference':'synthetic-owner','inputs':{'input':sha(self.root/'input')},'steps':[{'id':'tests','depends_on':[],'status':'succeeded','evidence':{'evidence':sha(self.root/'evidence')}},{'id':'review','depends_on':['tests'],'status':'pending','evidence':{}}]}
 def test_completion_is_not_authority(self):
  r=preview(self.record,self.root);self.assertEqual(r['next_steps'],['review']);self.assertFalse(r['permission_granted']);self.assertFalse(r['formal_closure'])
 def test_changed_input_invalidates_all(self):
  (self.root/'input').write_text('v2');r=preview(self.record,self.root);self.assertFalse(r['completed']);self.assertFalse(r['next_steps'])
 def test_stale_evidence_blocks_dependents(self):
  self.record['steps'][1].update(status='succeeded',evidence=self.record['steps'][0]['evidence'])
  (self.root/'evidence').write_text('changed');self.assertEqual(len(preview(self.record,self.root)['blocked']),2)
 def test_dependency_order_independent(self):
  self.record['steps'].reverse();self.assertEqual(preview(self.record,self.root)['next_steps'],['review'])
 def test_cycle_and_duplicate_rejected(self):
  self.record['steps'][0]['depends_on']=['review']
  with self.assertRaises(ValueError):preview(self.record,self.root)
  self.record['steps'][0]['depends_on']=[];self.record['steps'][1]['id']='tests'
  with self.assertRaises(ValueError):preview(self.record,self.root)
 def test_unknown_effect_is_never_retried(self):
  self.record['steps'][0]['status']='uncertain';self.assertFalse(preview(self.record,self.root)['next_steps'])
 def test_failed_qa_cannot_be_closure(self):
  self.record['steps'][0]['status']='failed';self.assertEqual(preview(self.record,self.root)['status'],'incomplete')
 def test_record_commands_rejected(self):
  self.record['steps'][0]['command']='touch forbidden'
  with self.assertRaises(ValueError):preview(self.record,self.root)
 def test_symlinks_and_escape_rejected(self):
  (self.root/'linked').symlink_to(self.root/'input');self.record['inputs']={'linked':sha(self.root/'input')}
  with self.assertRaises(ValueError):preview(self.record,self.root)
  self.record['inputs']={'../input':'0'*64}
  with self.assertRaises(ValueError):preview(self.record,self.root)
 def test_no_success_without_readback(self):
  self.record['steps'][0]['evidence']={}
  with self.assertRaises(ValueError):preview(self.record,self.root)
 def test_excluded_optional_step_not_executed(self):
  self.record['steps'][1]['status']='excluded';r=preview(self.record,self.root);self.assertEqual(r['status'],'ready-for-review');self.assertFalse(r['formal_closure'])

if __name__=='__main__':unittest.main()
