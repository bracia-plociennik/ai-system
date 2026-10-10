import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from unittest.mock import patch

from test_work_evidence_ledger import LedgerTests
from work_evidence import EvidenceError, canonical_bytes, digest, file_hash, validate_config
from work_evidence_ledger import Ledger
from work_evidence_recovery import init_preview


class PathContextTests(LedgerTests):
    def portable(self):
        raw=copy.deepcopy(self.config)
        raw['ledger_roots']=['${AI_SYSTEM_WORKSPACE_HOME}']
        raw['source_roots']={alias:str(path).replace(str(self.root),'${AI_SYSTEM_HOME}',1)
                             for alias,path in raw['source_roots'].items()}
        self.ledger.config_path.write_bytes(canonical_bytes(raw))
        self.environment=patch.dict(os.environ, {'AI_SYSTEM_HOME':str(self.root)})
        self.environment.start(); self.addCleanup(self.environment.stop)
        self.ledger=Ledger(self.ws)
        return raw

    def test_raw_configuration_preserved_and_new_v2_manifest(self):
        raw=self.portable(); original=self.ledger.config_path.read_bytes()
        resolved=validate_config(raw,self.ws)
        self.assertEqual(raw['ledger_roots'],['${AI_SYSTEM_WORKSPACE_HOME}'])
        self.assertEqual(resolved['ledger_roots'],[str(self.ws)])
        prepared,result=self.commit()
        self.assertEqual(prepared['manifest']['schema_version'],2)
        self.assertEqual(prepared['manifest']['path_context'], self.ledger.loaded_path_context)
        self.assertEqual(prepared['manifest']['snapshot']['config_hash'],file_hash(self.ledger.config_path))
        self.assertEqual(self.ledger.config_path.read_bytes(),original)
        self.assertEqual(len(self.ledger.committed()[0]),1)

    def legacy(self):
        prepared=self.ledger.prepare(self.candidate)
        old=copy.deepcopy(prepared['manifest']); old['schema_version']=1; old.pop('path_context')
        path=self.ledger.runtime('transactions/'+old['transaction_id']+'/manifest.json')
        path.write_bytes(canonical_bytes(old))
        return old,path,digest(old)

    def test_v1_literal_apply_preserves_original_manifest(self):
        old,path,expected=self.legacy(); original=path.read_bytes()
        self.ledger.apply(old['transaction_id'],expected)
        self.ledger.apply(old['transaction_id'],expected)
        self.assertEqual(path.read_bytes(),original)
        self.assertEqual(len(self.ledger.committed()[0]),1)

    def test_v1_dynamic_replay_and_prepare_dedup_rejected(self):
        self.portable(); old,path,expected=self.legacy(); original=path.read_bytes()
        for call in [lambda:self.ledger.apply(old['transaction_id'],expected),
                     lambda:self.ledger.prepare(self.candidate)]:
            with self.assertRaises(EvidenceError) as raised: call()
            self.assertEqual(raised.exception.category,'legacy-path-context-unverifiable')
        self.assertEqual(path.read_bytes(),original)
        self.assertFalse((self.ws/'work-log').exists())

    def test_context_drift_with_same_raw_hash_in_process_and_new_process(self):
        self.portable(); prepared=self.ledger.prepare(self.candidate)
        changed=self.root/'changed'; changed.mkdir()
        for alias,original in self.config['source_roots'].items():
            (changed/Path(original).relative_to(self.root)).mkdir(parents=True,exist_ok=True)
        before=self.hashes(); rawhash=file_hash(self.ledger.config_path)
        with patch.dict(os.environ,{'AI_SYSTEM_HOME':str(changed)}):
            with self.assertRaises(EvidenceError) as raised:
                self.ledger.apply(prepared['transaction_id'],prepared['manifest_hash'])
            self.assertEqual(raised.exception.category,'stale-path-context')
            loaded=Ledger(self.ws)
            with self.assertRaises(EvidenceError) as raised:
                loaded.apply(prepared['transaction_id'],prepared['manifest_hash'])
            self.assertEqual(raised.exception.category,'stale-path-context')
            with self.assertRaises(EvidenceError): loaded.prepare(self.candidate)
            cli=Path(__file__).resolve().parents[1]/'work-evidence-recover'
            r=subprocess.run([str(cli),'--workspace',str(self.ws),'--transaction-id',prepared['transaction_id'],
                              '--manifest-hash',prepared['manifest_hash'],'--owner-approved'],
                             capture_output=True,text=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
            self.assertNotEqual(r.returncode,0)
            self.assertEqual(json.loads(r.stderr)['category'],'stale-path-context')
        self.assertEqual(file_hash(self.ledger.config_path),rawhash)
        self.assertEqual(self.hashes(),before)

    def test_unknown_and_malformed_context_rejected(self):
        prepared=self.ledger.prepare(self.candidate)
        for version in [0,3,True]:
            value=copy.deepcopy(prepared['manifest']); value['schema_version']=version
            with self.assertRaises(EvidenceError): self.ledger.validate_manifest(value,replay=True)
        for change in [{'schema_version':2},{'workspace':'relative'}, {'ledger_roots':['/same','/same']},
                       {'source_roots':{'alias':'${HOME}/source'}}, {'extra':True}]:
            value=copy.deepcopy(prepared['manifest']); value['path_context'].update(change)
            with self.assertRaises(EvidenceError): self.ledger.validate_manifest(value,replay=True)

    def test_history_can_be_read_after_fixture_relocation_without_replay(self):
        self.portable(); prepared,_=self.commit()
        original=self.hashes()
        moved=self.root/'moved/sample-workspace'; shutil.copytree(self.ws,moved)
        loaded=Ledger(moved)
        self.assertEqual(len(loaded.committed()[0]),1)
        with self.assertRaises(EvidenceError): loaded.apply(prepared['transaction_id'],prepared['manifest_hash'])
        # Original source, revisions, receipts and manifest bytes remain unchanged.
        for path,checksum in original.items(): self.assertEqual(file_hash(self.root/path),checksum)

    def test_init_preview_keeps_request_expressions_and_owner_escape_rejects(self):
        request={'schema_version':1,'config':copy.deepcopy(self.config),'entities':copy.deepcopy(self.registry)}
        new=self.root/'new-workspace'; new.mkdir()
        request['config']['workspace_id']=new.name
        request['config']['ledger_roots']=['${AI_SYSTEM_WORKSPACE_HOME}']
        original=copy.deepcopy(request)
        preview=init_preview(new,request)
        self.assertEqual(request,original)
        self.assertIn('${AI_SYSTEM_WORKSPACE_HOME}',preview['files']['work-evidence/config.json'])
        unsafe=copy.deepcopy(request['config']); unsafe['ledger_roots']=[str(self.root)]
        with self.assertRaises(EvidenceError): validate_config(unsafe,new)

    def test_portable_crash_recovery_exactly_once(self):
        self.portable()
        self.test_crash_at_each_stage_retry_exactly_once()
