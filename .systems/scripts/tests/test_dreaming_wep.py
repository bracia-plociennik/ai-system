import sys,unittest,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_work_evidence_ledger import LedgerTests
from test_dreaming_sources import policy
from dreaming_candidates import reconcile,CONSUMERS
import dreaming_wep as b

class Bridge(unittest.TestCase):
    def setUp(self):
        self.f=LedgerTests();self.f.setUp();self.addCleanup(self.f.doCleanups)
        self.scope=policy(self.f.root,owner='sample-workspace');self.scope['roots'][0]['bindings'][0]['project_id']='sample-project'
        entry=self.f.candidate['changes'][0]['entry'];ref=entry['source_refs'][0]
        source=dict(source_root_id='root-a',relative_path=ref['relative_path'],project_id='sample-project',owner_workspace_id='sample-workspace',sha256=ref['sha256'],byte_count=self.f.source.stat().st_size,observed_at=ref['observed_at'],fact_date=ref['fact_date'],evidence_level='owner-attested',source_class='work')
        self.value=reconcile('sample-workspace','sample-project','case-a',[source],dict(facts=[],inferences=[],unknowns=[]),dict(work_id=entry['work_id'],case_ref=None,signals={x:{} for x in CONSUMERS},conflicts=[]))
    def test_native_ledger_no_write_preview_and_retry(self):
        before=self.f.hashes();preview=b.preview(self.f.ws,self.value,self.scope,'ledger',self.f.candidate);self.assertEqual(before,self.f.hashes())
        with self.assertRaises(b.ProtocolError):b.apply(self.f.ws,self.value,self.scope,'ledger',self.f.candidate,preview['binding'],preview['preview_hash'])
        result=b.apply(self.f.ws,self.value,self.scope,'ledger',self.f.candidate,preview['binding'],preview['preview_hash'],owner_approved=True)
        self.assertEqual(result['successor_candidate']['revision'],2);self.assertEqual(len(self.f.ledger.committed()[0]),1)
        b.apply(self.f.ws,self.value,self.scope,'ledger',self.f.candidate,preview['binding'],preview['preview_hash'],owner_approved=True);self.assertEqual(len(self.f.ledger.committed()[0]),1)
    def test_source_drift_owner_and_unknown_time(self):
        request=copy.deepcopy(self.f.candidate);request['changes'][0]['entry']['duration'].update(seconds=None,basis='unknown',evidence_ref=None)
        with self.assertRaises(b.ProtocolError):b.preview(self.f.ws,self.value,self.scope,'ledger',request)
        preview=b.preview(self.f.ws,self.value,self.scope,'ledger',self.f.candidate);self.f.source.write_text('changed')
        with self.assertRaises(b.ProtocolError):b.apply(self.f.ws,self.value,self.scope,'ledger',self.f.candidate,preview['binding'],preview['preview_hash'],owner_approved=True)
        self.assertEqual(len(self.f.ledger.committed()[0]),0)
    def test_request_metadata_not_authority(self):
        req=copy.deepcopy(self.f.candidate);req['owner-approved']=True
        with self.assertRaises(Exception):b.preview(self.f.ws,self.value,self.scope,'ledger',req)

class NativeConsumers(unittest.TestCase):
    def proposed(self,f):
        entry=f.candidate['changes'][0]['entry'];ref=entry['source_refs'][0]
        scope=policy(f.root,owner='sample-workspace');scope['roots'][0]['bindings'][0]['project_id']='sample-project'
        source=dict(source_root_id='root-a',relative_path=ref['relative_path'],project_id='sample-project',owner_workspace_id='sample-workspace',sha256=ref['sha256'],byte_count=f.source.stat().st_size,observed_at=ref['observed_at'],fact_date=ref['fact_date'],evidence_level='owner-attested',source_class='work')
        value=reconcile('sample-workspace','sample-project','case-a',[source],dict(facts=[],inferences=[],unknowns=[]),dict(work_id=entry['work_id'],case_ref='existing-case',signals={x:{} for x in CONSUMERS},conflicts=[]))
        return value,scope
    def test_four_native_derivatives(self):
        from test_work_evidence_docs import DocsTests
        from test_work_evidence_report import ReportTests
        from test_work_evidence_editorial import EditorialTests
        from test_work_evidence_tax_evidence import TaxEvidenceTests
        for kind,klass,attribute,taxpayer in [('documentation',DocsTests,'procedure',None),('report',ReportTests,'policy',None),('editorial',EditorialTests,'request',None),('tax-evidence',TaxEvidenceTests,'bundle','sample-taxpayer')]:
            with self.subTest(consumer=kind):
                fixture=klass();fixture.setUp();self.addCleanup(fixture.doCleanups)
                value,scope=self.proposed(fixture.f);request=getattr(fixture,attribute)
                before=fixture.f.hashes();preview=b.preview(fixture.f.ws,value,scope,kind,request,taxpayer)
                self.assertEqual(before,fixture.f.hashes())
                result=b.apply(fixture.f.ws,value,scope,kind,request,preview['binding'],preview['preview_hash'],owner_approved=True)
                self.assertEqual(result['publication'],'not-authorized');self.assertEqual(result['successor_candidate']['work_id'],value['work_id'])

if __name__=='__main__':unittest.main()
