#!/usr/bin/env python3
"""Adapter/global installer controls on artificial homes, no real account changes."""
import hashlib,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));import luna_first_adapter as adapter;import luna_first_install as m

class Install(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.root=Path(self.t.name);self.home=self.root/'home';self.home.mkdir();(self.home/'.codex').mkdir();self.agents=self.home/'.codex/AGENTS.md';self.agents.write_text('Existing owner startup\n');self.source=self.root/'bundle';self.source.mkdir();(self.source/'skill').mkdir();(self.source/'skill/SKILL.md').write_text('test source only');(self.source/'profiles').mkdir()
  for name in ['luna-first-luna.toml','luna-first-sol.toml']:(self.source/'profiles'/name).write_text('name="fixture"\n')
  self.update_manifest();self.inst=self.root/'AGENTS.md';self.inst.write_text('local');self.original=self.agents.read_bytes()
 def update_manifest(self):
  inv=m.items(self.source);inv.pop('manifest.json',None);m.store(self.source/'manifest.json',{'schema':1,'files':inv})
 def plan(self):return m.plan(self.source,self.home,[self.inst],'actual-test-fixture-not-owner-consent')
 def test_plan_has_no_effect(self):
  value=self.plan();self.assertFalse((self.home/'.config').exists());self.assertFalse(value['execution_authorized']);self.assertEqual(self.agents.read_bytes(),self.original)
 def test_requires_explicit_apply_gate(self):
  with self.assertRaises(ValueError):m.apply(self.plan())
 def test_apply_inspect_disable(self):
  value=self.plan();out=m.apply(value,True);self.assertTrue(out['active']);self.assertFalse(out['root_chat_model_changed']);m.disable(self.home,True);self.assertFalse(m.inspect(self.home)['active']);self.assertEqual(self.agents.read_bytes(),self.original)
 def test_foreign_profile_conflict(self):
  p=self.home/'.codex/agents';p.mkdir();(p/'luna-first-luna.toml').write_text('foreign')
  with self.assertRaises(ValueError):self.plan()
 def test_foreign_skill_conflict(self):
  (self.home/'.agents/skills/luna-first').mkdir(parents=True)
  with self.assertRaises(ValueError):self.plan()
 def test_instruction_budget(self):
  self.inst.write_text('x'*16400)
  with self.assertRaises(ValueError):self.plan()
 def test_source_drift_rejected(self):
  value=self.plan();(self.source/'skill/SKILL.md').write_text('changed')
  with self.assertRaises(ValueError):m.apply(value,True)
 def test_owner_config_drift_rejected(self):
  value=self.plan();self.agents.write_text('changed independently')
  with self.assertRaises(ValueError):m.apply(value,True)
 def test_profile_tamper_inactive(self):
  m.apply(self.plan(),True);(self.home/'.codex/agents/luna-first-luna.toml').write_text('tampered');self.assertFalse(m.inspect(self.home)['active'])
 def test_bundle_tamper_inactive(self):
  out=m.apply(self.plan(),True);(Path(out['component'])/'skill/SKILL.md').write_text('tampered');self.assertFalse(m.inspect(self.home)['active'])
 def test_disable_preserves_foreign_instructions(self):
  m.apply(self.plan(),True);self.agents.write_bytes(self.agents.read_bytes()+b'Other owner instruction\n');m.disable(self.home,True);self.assertEqual(self.agents.read_bytes(),self.original+b'Other owner instruction\n')
 def test_links_rejected(self):
  link=self.root/'linked';link.symlink_to(self.home,target_is_directory=True)
  with self.assertRaises(ValueError):m.plan(self.source,link,[self.inst],'test')
 def test_tampered_plan_rejected(self):
  value=self.plan();value['agents_after']='replacement'
  with self.assertRaises(ValueError):m.apply(value,True)
 def test_no_reset_on_repeat_apply(self):
  value=self.plan();m.apply(value,True)
  with self.assertRaises(ValueError):m.apply(value,True)
 def test_adapter_pin(self):
  root=self.root/'workflow'
  for rel in adapter.FILES:
   f=root/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_text('fixture source\n')
  cap=root/'.systems/ai/capabilities/luna-first-v1.json';cap.parent.mkdir(parents=True);m.store(cap,{'schema':1,'capability':'luna-first-v1','contract_version':1,'authority':'none','files':{r:m.digest((root/r).read_bytes()) for r in adapter.FILES}})
  self.assertTrue(adapter.support(root)['supported']);(root/'.systems/scripts/luna_first.py').write_text('changed')
  with self.assertRaises(ValueError):adapter.support(root)
 def test_unknown_counterpart_rejected(self):
  root=self.root/'workflow';root.mkdir()
  with self.assertRaises(OSError):adapter.support(root)

if __name__=='__main__':unittest.main()
