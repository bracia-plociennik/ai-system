#!/usr/bin/env python3
"""Independent synthetic Git tree/index/live and contract regression tests."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
MODULE = ROOT / '.systems/scripts/lib/intent-brief.py'
if not MODULE.exists():MODULE = ROOT / '.systems/scripts/intent_brief.py'
spec=importlib.util.spec_from_file_location('intent_brief',MODULE)
ib=importlib.util.module_from_spec(spec);spec.loader.exec_module(ib)


class IntentBrief(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.git('init','-q');self.git('config','core.filemode','true')
        pins={}
        for relative in sorted(ib.SOURCES):
            path=self.root/relative;path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text('synthetic source '+relative+'\n');path.chmod(0o755 if relative.endswith('/style-profile') else 0o644)
            pins[relative]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'mode':'100755' if path.stat().st_mode & 0o100 else '100644'}
        self.git('add','.');self.commit=self.commit_sources()
        self.profile={'contract':'intent-to-execution-brief-v1','semantic_version':1,'tested_commit':self.commit,
                      'mode_mapping':{'auto':'auto','human':'human-coop'},'delivery_mapping':{'auto-unconstrained':'auto-unbounded'},'sources':pins}
        self.path=self.root/'profile.json';self.save()

    def git(self,*args):
        r=subprocess.run(['git','-C',str(self.root),*args],text=True,capture_output=True);self.assertEqual(r.returncode,0,r.stderr);return r.stdout.strip()
    def commit_sources(self):
        self.git('-c','user.name=Synthetic fixture','-c','user.email=fixture@example.invalid','commit','-qm','synthetic source fixture');return self.git('rev-parse','HEAD')
    def save(self):self.path.write_text(json.dumps(self.profile))
    def assess(self,head=None):return ib.verify(self.root,self.path,head or self.commit)

    def test_exact_source_and_later_metadata_commit(self):
        result=self.assess();self.assertEqual(result['sources'],16);self.assertFalse(result['native_behavior_verified']);self.assertFalse(result['owner_approval_verified'])
        self.git('add','profile.json');later=self.commit_sources();self.assertEqual(self.assess(later)['tested_commit'],self.commit)

    def test_unknown_version_keys_and_source_population(self):
        for key,value in [('semantic_version',True),('semantic_version',2),('tested_commit','0'*40),('mode_mapping',{'auto':'human-coop'}),('extra',True)]:
            with self.subTest(key=key,value=value):
                old=copy.deepcopy(self.profile);self.profile[key]=value;self.save()
                with self.assertRaises(ib.InvalidCapability):self.assess()
                self.profile=old;self.save()
        for shape in ['missing','extra']:
            old=copy.deepcopy(self.profile)
            if shape=='missing':self.profile['sources'].pop('AGENTS.md')
            else:self.profile['sources']['../foreign']={'sha256':'a'*64,'mode':'100644'}
            self.save()
            with self.assertRaises(ib.InvalidCapability):self.assess()
            self.profile=old;self.save()

    def test_live_source_missing_symlink_mode_and_bytes(self):
        source=self.root/'AGENTS.md';original=source.read_bytes()
        for shape in ['bytes','missing','symlink','mode']:
            with self.subTest(shape=shape):
                if shape=='bytes':source.write_text('changed')
                elif shape=='missing':source.unlink()
                elif shape=='symlink':source.unlink();source.symlink_to(self.path)
                else:source.chmod(0o755)
                with self.assertRaises(ib.InvalidCapability):self.assess()
                if source.is_symlink():source.unlink()
                source.write_bytes(original);source.chmod(0o644)

    def test_index_changed_with_live_restored_rejects(self):
        source=self.root/'AGENTS.md';original=source.read_bytes();source.write_text('staged drift');self.git('add','AGENTS.md');source.write_bytes(original)
        with self.assertRaises(ib.InvalidCapability):self.assess()

    def test_arbitrary_live_restamp_cannot_change_tested_tree(self):
        source=self.root/'AGENTS.md';source.write_text('new incompatible source');self.git('add','AGENTS.md')
        self.profile['sources']['AGENTS.md']['sha256']=hashlib.sha256(source.read_bytes()).hexdigest();self.save()
        with self.assertRaises(ib.InvalidCapability):self.assess()

    def test_committed_drift_and_wrong_handoff_reject(self):
        with self.assertRaises(ib.InvalidCapability):self.assess('0'*40)
        source=self.root/'AGENTS.md';original=source.read_bytes();source.write_text('committed drift');self.git('add','AGENTS.md');later=self.commit_sources();source.write_bytes(original);self.git('add','AGENTS.md')
        with self.assertRaises(ib.InvalidCapability):self.assess(later)

    def test_profile_link_and_duplicate_json(self):
        self.path.write_text('{"contract":"intent-to-execution-brief-v1","contract":"intent-to-execution-brief-v1"}')
        with self.assertRaises(ib.InvalidCapability):self.assess()
        self.save();linked=self.root/'linked.json';linked.symlink_to(self.path)
        with self.assertRaises(ib.InvalidCapability):ib.verify(self.root,linked,self.commit)

    def test_contract_and_embedded_advisory_sections(self):
        brief=(ROOT/'.systems/ai/core/intent-to-execution-brief.md').read_text()
        style=(ROOT/'.systems/ai/core/style-profile.md').read_text()
        for term in ['provenance','disposition','original','independent QA','stop phase','Unknown dependencies','Current task instructions','Human']:
            self.assertIn(term,brief)
        for term in ['tentative','disabled','expected_revision','0700','0600','owner','semantic privacy','not authority','160']:
            self.assertIn(term,style)
        self.assertEqual(len(ib.SOURCES),16)

    def test_independent_behavior_fixture_population(self):
        fixture=ROOT/'.systems/scripts/tests/fixtures/intent-to-execution-brief-v1.json'
        data=json.loads(fixture.read_text())
        self.assertEqual(data['privacy'],'synthetic-only');self.assertEqual(data['schema'],1)
        self.assertEqual([c['id'] for c in data['cases']],[f'B{i:02d}' for i in range(1,26)])
        for case in data['cases']:
            self.assertEqual(set(case),{'id','owner_request','context','oracle','modes'})
            self.assertTrue(case['owner_request']);self.assertIn('ceiling',case['oracle'])
            self.assertTrue(set(case['modes'])<={'auto','human'})

    def test_candidate_live_only_cannot_attest_support(self):
        result=ib.candidate(self.root,self.path)
        self.assertEqual(result['authority'],'none');self.assertFalse(result['capability_verified'])
        self.profile['sources'].pop('AGENTS.md');self.save()
        with self.assertRaises(ib.InvalidCapability):ib.candidate(self.root,self.path)

    def test_nested_directory_cannot_borrow_parent_repository_identity(self):
        nested = self.root / 'nested'
        nested.mkdir()
        for relative in sorted(ib.SOURCES):
            source = self.root / relative
            target = nested / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
            target.chmod(source.stat().st_mode & 0o777)
        self.git('add', 'nested')
        head = self.commit_sources()
        self.profile['tested_commit'] = head
        self.save()
        with self.assertRaises(ib.InvalidCapability):
            ib.verify(nested, self.path, head)


if __name__=='__main__':unittest.main()
