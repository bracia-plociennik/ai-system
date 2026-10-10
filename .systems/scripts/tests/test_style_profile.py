#!/usr/bin/env python3
"""Synthetic, offline profile state/privacy/atomicity regression tests."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[3]
MODULE = ROOT / '.systems/scripts/lib/style-profile.py'
if not MODULE.exists():
    MODULE = ROOT / '.systems/scripts/style_profile.py'
spec = importlib.util.spec_from_file_location('style_profile', MODULE)
sp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sp)


def change(action, key=None, value=None):
    return {'action': action, 'actor': 'agent' if action == 'observation' else 'owner',
            'key': key, 'value': value,
            'source': {'kind': 'marked-observation' if action == 'observation' else 'owner-correction' if action == 'correction' else 'owner-preference',
                       'reference': 'conversation:synthetic-feedback', 'sha256': hashlib.sha256(b'synthetic feedback').hexdigest()},
            'approval': {'kind': 'owner-profile-opt-in', 'reference': 'decisions/synthetic-profile-opt-in.md',
                         'sha256': hashlib.sha256(b'synthetic exact scope opt in').hexdigest()}}


class StyleProfile(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = 'memory/style-profile-v1.json'
        self.scope = 'synthetic-owner'
        self.profile = sp.apply(self.root, self.path, self.scope, 0, change('init'))

    def apply(self, action, key=None, value=None):
        self.profile = sp.apply(self.root, self.path, self.scope, self.profile['revision'], change(action,key,value))
        return self.profile

    def test_empty_disabled_no_traits(self):
        result=sp.projection(self.profile,self.scope)
        self.assertFalse(result['enabled']);self.assertEqual(result['preferences'],{})
        with self.assertRaises(sp.InvalidProfile):self.apply('correction','language','Polish')

    def test_owner_correction_provenance_revision(self):
        self.apply('enable'); self.apply('correction','language','Polish')
        result=sp.projection(self.profile,self.scope)['preferences']['language']
        self.assertEqual(result['value'],'Polish');self.assertEqual(result['revision'],3)
        self.assertEqual(result['source']['kind'],'owner-correction')

    def test_observation_never_overrides_or_promotes(self):
        self.apply('enable');self.apply('correction','tone','calm')
        for _ in range(5):self.apply('observation','tone','formal')
        self.assertEqual(sp.projection(self.profile,self.scope)['preferences']['tone']['value'],'calm')
        self.apply('observation','verbosity','concise')
        self.assertNotIn('verbosity',sp.projection(self.profile,self.scope)['preferences'])
        self.assertIn('verbosity',sp.projection(self.profile,self.scope)['tentative_keys'])

    def test_confirmation_correction_and_history(self):
        self.apply('enable');self.apply('observation','verbosity','concise');self.apply('confirm','verbosity','concise')
        before=copy.deepcopy(self.profile['events']);self.apply('correction','verbosity','detailed')
        self.assertEqual(self.profile['events'][:-1],before)
        self.assertEqual(sp.projection(self.profile,self.scope)['preferences']['verbosity']['value'],'detailed')
        with self.assertRaises(sp.InvalidProfile):self.apply('confirm','verbosity','another value')

    def test_disable_preference_and_profile(self):
        self.apply('enable');self.apply('correction','tone','plain');self.apply('disable-preference','tone')
        self.assertEqual(sp.projection(self.profile,self.scope)['preferences'],{})
        self.apply('correction','language','Polish');self.apply('disable')
        self.assertEqual(sp.projection(self.profile,self.scope)['preferences'],{})
        with self.assertRaises(sp.InvalidProfile):self.apply('observation','tone','plain')
        self.apply('enable');self.assertIn('language',sp.projection(self.profile,self.scope)['preferences'])

    def test_actor_source_and_approval_required(self):
        self.apply('enable')
        for field,value in [('actor','agent'),('source',{'kind':'marked-observation','reference':'conversation:test','sha256':'a'*64}),('approval',None)]:
            data=change('correction','tone','plain');data[field]=value
            with self.subTest(field=field),self.assertRaises(sp.InvalidProfile):sp.transition(self.profile,self.scope,2,data)
        data=change('observation','tone','plain');data['actor']='owner'
        with self.assertRaises(sp.InvalidProfile):sp.transition(self.profile,self.scope,2,data)

    def test_unsupported_sensitive_or_raw_values(self):
        self.apply('enable')
        for key,value in [('approval','yes'),('deadline','tomorrow'),('tone','token=synthetic-secret'),('tone','https://synthetic.test'),('tone','client: synthetic-name'),('tone','raw\nconversation'),('tone','x'*161),('tone','user@synthetic.test')]:
            with self.subTest(key=key,value=value),self.assertRaises(sp.InvalidProfile):sp.transition(self.profile,self.scope,2,change('correction',key,value))

    def test_foreign_unknown_corrupt_duplicate_and_invalid_history(self):
        with self.assertRaises(sp.InvalidProfile):sp.validate(self.profile,'other-owner')
        for field,value in [('schema',2),('revision',True),('events',[])]:
            p=copy.deepcopy(self.profile);p[field]=value
            with self.subTest(field=field),self.assertRaises(sp.InvalidProfile):sp.validate(p,self.scope)
        p=copy.deepcopy(self.profile);p['events'][0]['actor']='agent'
        with self.assertRaises(sp.InvalidProfile):sp.validate(p,self.scope)
        with self.assertRaises(sp.InvalidProfile):sp.load_json('{"schema":1,"schema":1}')

    def test_path_symlink_traversal_hardlink_fifo(self):
        for bad in ['../memory/style-profile-v1.json','/memory/style-profile-v1.json','.systems/style-profile-v1.json','memory//style-profile-v1.json']:
            with self.subTest(path=bad),self.assertRaises(sp.InvalidProfile):sp.safe_path(self.root,bad)
        foreign=self.root/'foreign';foreign.mkdir();link=self.root/'projects';link.symlink_to(foreign,target_is_directory=True)
        with self.assertRaises(sp.InvalidProfile):sp.safe_path(self.root,'projects/synthetic/memory/style-profile-v1.json')
        link.unlink()
        import os
        os.link(self.root/self.path,self.root/'duplicate.json')
        with self.assertRaises(sp.InvalidProfile):sp.read(self.root,self.path,self.scope)
        (self.root/'duplicate.json').unlink()
        (self.root/self.path).unlink();os.mkfifo(self.root/self.path)
        with self.assertRaises(sp.InvalidProfile):sp.read(self.root,self.path,self.scope)

    def test_revision_and_atomic_error_preserve_bytes(self):
        before=(self.root/self.path).read_bytes()
        with self.assertRaises(sp.InvalidProfile):sp.apply(self.root,self.path,self.scope,0,change('enable'))
        self.assertEqual((self.root/self.path).read_bytes(),before)
        with patch.object(sp.os,'replace',side_effect=OSError('synthetic atomic failure')):
            with self.assertRaises(OSError):sp.apply(self.root,self.path,self.scope,1,change('enable'))
        self.assertEqual((self.root/self.path).read_bytes(),before)
        self.assertEqual(list((self.root/'memory').glob('.style-profile-*')),[])

    def test_concurrent_expected_revision_single_winner(self):
        def writer(_):
            try:sp.apply(self.root,self.path,self.scope,1,change('enable'));return 'applied'
            except sp.InvalidProfile:return 'stale'
        with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(writer,range(4)))
        self.assertEqual(results.count('applied'),1);self.assertEqual(results.count('stale'),3)
        self.assertEqual(sp.read(self.root,self.path,self.scope)['revision'],2)

    def test_file_permissions_and_private_parent(self):
        self.assertEqual((self.root/self.path).stat().st_mode & 0o777,0o600)
        self.assertEqual((self.root/'memory').stat().st_mode & 0o777,0o700)
        (self.root/'memory').chmod(0o755)
        with self.assertRaises(sp.InvalidProfile):sp.apply(self.root,self.path,self.scope,1,change('enable'))

    def test_cli_prepare_read_only_and_projection(self):
        p=self.root/'request.json';p.write_text(json.dumps(change('enable')))
        before=(self.root/self.path).read_bytes()
        args=[sys.executable,'-B',str(MODULE),'prepare','--workspace',str(self.root),'--path',self.path,'--scope',self.scope,'--request',str(p),'--expected-revision','1']
        result=subprocess.run(args,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr);self.assertEqual((self.root/self.path).read_bytes(),before)
        self.assertEqual(json.loads(result.stdout)['revision'],2)


class SystemCanonicalOwners(unittest.TestCase):
    def test_canonical_owner_paths_and_repository_boundary(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for relative in ['memory/style-profile-v1.json', 'project-state/example/memory/style-profile-v1.json',
                             'clients/example/memory/style-profile-v1.json', 'clients/example/project-state/demo/memory/style-profile-v1.json',
                             'owned-assets/example/memory/style-profile-v1.json', 'owned-assets/example/project-state/demo/memory/style-profile-v1.json']:
                value=sp.apply(root,relative,'synthetic-owner',0,change('init'))
                self.assertFalse(sp.projection(value,'synthetic-owner')['enabled'])
            for relative in ['projects/repository/memory/style-profile-v1.json', 'clients/example/projects/repository/memory/style-profile-v1.json',
                             'project-state/../memory/style-profile-v1.json']:
                with self.assertRaises(sp.InvalidProfile):sp.safe_path(root,relative)


if __name__=='__main__':unittest.main()
