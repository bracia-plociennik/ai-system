"""Actual guarded provider -> runner -> canonical case -> native WEP regressions."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parent)]
import dreaming_runner as r
import dreaming_wep as bridge
import test_work_evidence_ledger as fixtures
from test_dreaming_runner import begin, deliver, capabilities, PRODUCER
from test_dreaming_sources import policy


def response(state, rows, findings):
    return dict(analyzer=state['analyzer'], policy_digest=r.digest(state['policy']),
                read_receipt_ids=[row['read_receipt']['receipt_id'] for row in rows],
                covered_chunks=[c['chunk_id'] for row in rows for c in row['read_receipt']['chunk_map']],
                findings=findings, coverage='complete', unresolved_conflicts=[])


def finding(rows, name='finding-a', text='Observed work, replay and time unverified.', **extra):
    return dict(finding_id=name, source_hashes=list(dict.fromkeys(row['source_ref']['sha256'] for row in rows)),
                facts=[text], inferences=[], unknowns=['Independent replay unconfirmed.'],
                native_state='unknown', native_quality='unknown', **extra)


class SourceToCase(unittest.TestCase):
    def simple(self, projects=False, same_bytes=False):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        base=Path(tmp.name);source=base/'sources';source.mkdir();ws=base/'workspace';ws.mkdir()
        for name,text in [('a','Project A deployed.'),('b','Project B planned.')]:
            (source/name).mkdir();(source/name/'note.md').write_text('Same work note.' if same_bytes else text)
        scope=policy(source)
        if projects:
            scope['roots'][0]['bindings']=[dict(prefix=k,project_id='project-'+k,owner_workspace_id='workspace-a',source_class='work') for k in ['a','b']]
        state=r.plan(ws,'run-a',scope,PRODUCER,capabilities(),dict(id='reviewer',version='v1',policy_digest='a'*64))
        deliver(ws,'run-a',state)
        return source,ws,state,[row for row in state['envelope']['inventory'] if row['read_receipt']]

    def test_duplicate_id_rejected_then_corrected_without_loss(self):
        _,ws,state,rows=self.simple()
        first=response(state,[rows[0]],[finding([rows[0]],text='Fact A')]);r.submit(ws,'run-a',first)
        before=(ws/'dreams/runs/run-a/state.json').read_bytes()
        self.assertEqual(r.submit(ws,'run-a',first)['receipt_id'],r.digest(first))
        with self.assertRaises(ValueError):r.submit(ws,'run-a',response(state,[rows[1]],[finding([rows[1]],text='Fact B')]))
        self.assertEqual(before,(ws/'dreams/runs/run-a/state.json').read_bytes())
        r.submit(ws,'run-a',response(state,[rows[1]],[finding([rows[1]],'finding-b','Fact B')]))
        self.assertEqual(r.finalize(ws,'run-a')['result'],'complete')
        report=r.load(ws/'dreams/runs/run-a/report.json')
        self.assertEqual({f['facts'][0] for f in report['findings']},{'Fact A','Fact B'})
        self.assertEqual(len(r.load(ws/'dreams/runs/run-a/candidates.json')),2)

    def test_mixed_project_rejected_then_split_preserves_citations(self):
        _,ws,state,rows=self.simple(projects=True)
        before=(ws/'dreams/runs/run-a/state.json').read_bytes()
        with self.assertRaises(ValueError):r.submit(ws,'run-a',response(state,rows,[finding(rows)]))
        self.assertEqual(before,(ws/'dreams/runs/run-a/state.json').read_bytes())
        facts=[finding([row],'finding-'+row['source_ref']['project_id'],row['source_ref']['project_id']) for row in rows]
        r.submit(ws,'run-a',response(state,rows,facts));r.finalize(ws,'run-a')
        packets=r.load(ws/'dreams/runs/run-a/candidates.json')
        self.assertEqual(len(packets),2)
        for packet in packets:
            self.assertEqual(packet['facts'][0]['text'],packet['project_id'])
            self.assertEqual(packet['facts'][0]['source_hashes'],[packet['evidence_refs'][0]['sha256']])

    def test_later_complete_response_does_not_erase_prior_findings(self):
        _,ws,state,rows=self.simple()
        r.submit(ws,'run-a',response(state,rows,[finding([rows[0]],'fact-a','First fact')]))
        r.submit(ws,'run-a',response(state,rows,[finding([rows[1]],'fact-b','Second fact')]))
        r.finalize(ws,'run-a');report=r.load(ws/'dreams/runs/run-a/report.json')
        self.assertEqual({f['facts'][0] for f in report['findings']},{'First fact','Second fact'})
        self.assertEqual(len(report['analysis_receipts']),2)
        r.plan(ws,'run-b',state['policy'],PRODUCER,capabilities(),state['analyzer'],'run-a')
        self.assertEqual(r.finalize(ws,'run-b')['result'],'complete')
        reused=r.load(ws/'dreams/runs/run-b/report.json')
        self.assertEqual({f['facts'][0] for f in reused['findings']},{'First fact','Second fact'})
        self.assertEqual(len(reused['analysis_receipts']),2)

    def test_identical_bytes_in_different_projects_need_scoped_receipts(self):
        _,ws,state,rows=self.simple(projects=True,same_bytes=True)
        with self.assertRaises(ValueError):r.submit(ws,'run-a',response(state,rows,[finding([rows[0]])]))
        for row in rows:
            r.submit(ws,'run-a',response(state,[row],[finding([row],'finding-'+row['source_ref']['project_id'])]))
        r.finalize(ws,'run-a')
        packets=r.load(ws/'dreams/runs/run-a/candidates.json')
        self.assertEqual(len(packets),2)
        self.assertTrue(all(all(ref['project_id']==p['project_id'] for ref in p['evidence_refs']) for p in packets))

    def native_case(self, fixture=None, run='native-a', previous=None):
        f=fixture or fixtures.LedgerTests()
        if fixture is None:f.setUp();self.addCleanup(f.doCleanups);f.commit()
        entry=next(iter(f.ledger.committed()[0].values()))
        src=f.root/'dream-source';src.mkdir(exist_ok=True)
        (src/'entry.json').write_text(json.dumps(entry))
        (src/'one.md').write_text('An observed outcome, not a replay proof.')
        (src/'two.md').write_text('A separate note about the same explicit work event.')
        scope=policy(f.root,owner='sample-workspace')
        scope['roots'][0]['bindings']=[dict(prefix=prefix,project_id='sample-project',owner_workspace_id='sample-workspace',source_class='work') for prefix in ['dream-source','confirmation.json']]
        state=r.plan(f.ws,run,scope,PRODUCER,capabilities(),dict(id='reviewer',version='v1',policy_digest='a'*64),previous)
        deliver(f.ws,run,state)
        rows=[row for row in state['envelope']['inventory'] if row['read_receipt']]
        native=next(row for row in rows if row['relative_path']=='dream-source/entry.json')
        # Each independently identified lesson explicitly cites the canonical entry.
        fs=[finding(list({row['relative_path']:row,native['relative_path']:native}.values()),'finding-'+str(i)) for i,row in enumerate(rows)]
        r.submit(f.ws,run,response(state,rows,fs));r.finalize(f.ws,run)
        packets=r.load(f.ws/'dreams/runs'/run/'candidates.json')
        self.assertEqual(len(packets),1)
        v=packets[0];self.assertEqual(v['work_id'],entry['work_id']);self.assertEqual(v['case_ref'],entry['entry_id']);self.assertEqual(v['intent'],'enrich-case')
        self.assertTrue(all(x['state']=='needs-evidence' for x in v['consumer_readiness'].values()))
        return f,v,scope,entry

    def test_native_entry_three_notes_one_case_without_added_hours(self):
        f,v,_,entry=self.native_case()
        self.assertGreaterEqual(len(v['evidence_refs']),3)
        self.assertEqual(len(f.ledger.committed()[0]),1)
        self.assertEqual(next(iter(f.ledger.committed()[0].values()))['duration'],entry['duration'])

    def test_existing_case_native_report_preview_and_apply_keep_ledger(self):
        import test_work_evidence_report as reports
        fixture=reports.ReportTests();fixture.setUp();self.addCleanup(fixture.doCleanups);fixture.f.commit()
        f,v,scope,entry=self.native_case(fixture.f)
        fixture.policy['texts']=[fixture.approve(entry)]
        before=f.hashes();pv=bridge.preview(f.ws,v,scope,'report',fixture.policy)
        self.assertEqual(f.hashes(),before)
        with self.assertRaises(ValueError):bridge.apply(f.ws,v,scope,'report',fixture.policy,pv['binding'],pv['preview_hash'])
        result=bridge.apply(f.ws,v,scope,'report',fixture.policy,pv['binding'],pv['preview_hash'],owner_approved=True)
        self.assertEqual(result['publication'],'not-authorized')
        self.assertEqual(list(f.ledger.committed()[0].values()),[entry])

    def test_existing_case_unknown_time_cannot_make_ledger_entry(self):
        f,v,scope,_=self.native_case();request=copy.deepcopy(f.candidate)
        request['changes'][0]['entry']['duration'].update(seconds=None,basis='unknown',evidence_ref=None)
        before=f.hashes()
        with self.assertRaises(ValueError):bridge.preview(f.ws,v,scope,'ledger',request)
        self.assertEqual(before,f.hashes())

    def test_case_context_cannot_invent_identity_from_prose(self):
        _,ws,state,rows=self.simple()
        ctx=dict(work_id='invented-work',case_ref='invented-case',identity_source_hashes=[rows[0]['source_ref']['sha256']],signals={c:{} for c in bridge.CONSUMERS},conflicts=[])
        with self.assertRaises(ValueError):r.submit(ws,'run-a',response(state,rows,[finding(rows,case_context=ctx)]))

    def test_changed_multi_source_analysis_is_not_partially_reused(self):
        source,ws,state,rows=self.simple()
        r.submit(ws,'run-a',response(state,rows,[finding(rows)]));r.finalize(ws,'run-a')
        (source/'b/note.md').write_text('Changed evidence.')
        current=r.plan(ws,'run-b',state['policy'],PRODUCER,capabilities(),state['analyzer'],'run-a')
        self.assertEqual(sum(row['disposition']=='reused-unchanged' for row in current['envelope']['inventory']),0)
        self.assertEqual(r.finalize(ws,'run-b')['result'],'partial')

    def test_wrong_owner_project_invalid_ids_and_conflicting_identities(self):
        for field,value in [('owner_workspace','other-workspace'),('project_id','other-project'),('work_id','not-native-uuid'),('work_id','{00000000-0000-4000-8000-000000000099}')]:
            with self.subTest(field=field):
                f=fixtures.LedgerTests();f.setUp();self.addCleanup(f.doCleanups);f.commit()
                source=f.root/'dream-source';source.mkdir();entry=copy.deepcopy(next(iter(f.ledger.committed()[0].values())));entry[field]=value
                (source/'entry.json').write_text(json.dumps(entry));scope=policy(source,owner='sample-workspace');scope['roots'][0]['bindings'][0]['project_id']='sample-project'
                state=r.plan(f.ws,'wrong-a',scope,PRODUCER,capabilities(),dict(id='reviewer',version='v1',policy_digest='a'*64));deliver(f.ws,'wrong-a',state)
                rows=[row for row in state['envelope']['inventory'] if row['read_receipt']]
                r.submit(f.ws,'wrong-a',response(state,rows,[finding(rows)]));r.finalize(f.ws,'wrong-a')
                packet=r.load(f.ws/'dreams/runs/wrong-a/candidates.json')[0]
                self.assertIsNone(packet['work_id']);self.assertIsNone(packet['case_ref'])
                self.assertTrue(all(c['state']=='needs-evidence' for c in packet['consumer_readiness'].values()))
        f=fixtures.LedgerTests();f.setUp();self.addCleanup(f.doCleanups);f.commit();source=f.root/'dream-source';source.mkdir()
        entry=copy.deepcopy(next(iter(f.ledger.committed()[0].values())));(source/'first.json').write_text(json.dumps(entry))
        entry['work_id']='00000000-0000-4000-8000-000000000099';(source/'second.json').write_text(json.dumps(entry))
        scope=policy(source,owner='sample-workspace');scope['roots'][0]['bindings'][0]['project_id']='sample-project'
        state=r.plan(f.ws,'conflict-a',scope,PRODUCER,capabilities(),dict(id='reviewer',version='v1',policy_digest='a'*64));deliver(f.ws,'conflict-a',state)
        rows=[row for row in state['envelope']['inventory'] if row['read_receipt']]
        r.submit(f.ws,'conflict-a',response(state,rows,[finding(rows)]));r.finalize(f.ws,'conflict-a')
        packet=r.load(f.ws/'dreams/runs/conflict-a/candidates.json')[0]
        self.assertIsNone(packet['work_id']);self.assertTrue(all(c['state']=='needs-owner-decision' for c in packet['consumer_readiness'].values()))

    def test_source_to_all_native_consumers_preserves_approvals_and_ledger(self):
        import test_work_evidence_docs as docs
        import test_work_evidence_editorial as editorial
        import test_work_evidence_tax_evidence as tax
        for consumer,klass,attr,taxpayer in [('documentation',docs.DocsTests,'procedure',None),('editorial',editorial.EditorialTests,'request',None),('tax-evidence',tax.TaxEvidenceTests,'bundle','sample-taxpayer')]:
            with self.subTest(consumer=consumer):
                fixture=klass();fixture.setUp();self.addCleanup(fixture.doCleanups)
                if not fixture.f.ledger.committed()[0]:fixture.f.commit()
                f,v,scope,entry=self.native_case(fixture.f);original_request=copy.deepcopy(getattr(fixture,attr));request=copy.deepcopy(original_request)
                if consumer=='documentation':request['work_ids']=[entry['work_id']]
                before=f.hashes();pv=bridge.preview(f.ws,v,scope,consumer,request,taxpayer)
                self.assertEqual(before,f.hashes())
                result=bridge.apply(f.ws,v,scope,consumer,request,pv['binding'],pv['preview_hash'],owner_approved=True)
                self.assertEqual(result['publication'],'not-authorized');self.assertEqual(list(f.ledger.committed()[0].values()),[entry])
                self.assertEqual(getattr(fixture,attr),original_request)
        f,v,scope,entry=self.native_case();request=copy.deepcopy(f.candidate)
        updated=request['changes'][0]['entry'];updated.update(revision=entry['revision']+1,previous_revision_hash=bridge.native_digest(entry),reason='Synthetic confirmed correction')
        before=f.hashes();pv=bridge.preview(f.ws,v,scope,'ledger',request);self.assertEqual(before,f.hashes())
        result=bridge.apply(f.ws,v,scope,'ledger',request,pv['binding'],pv['preview_hash'],owner_approved=True)
        self.assertEqual(len(f.ledger.committed()[0]),1);self.assertEqual(next(iter(f.ledger.committed()[0].values()))['duration'],entry['duration'])
        self.assertEqual(result['publication'],'not-authorized')

    def test_case_identity_stable_when_analysis_ids_change(self):
        f,v,scope,entry=self.native_case()
        state=r.plan(f.ws,'renamed-b',scope,PRODUCER,capabilities(),dict(id='reviewer',version='v1',policy_digest='a'*64),'native-a')
        self.assertTrue(all(row['disposition']=='reused-unchanged' for row in state['envelope']['inventory'] if row['read_receipt']))
        rows=[row for row in state['envelope']['inventory'] if row['read_receipt']]
        native=next(row for row in rows if row['relative_path']=='dream-source/entry.json')
        r.submit(f.ws,'renamed-b',response(state,rows,[finding([native],name='renamed-finding',text='New useful observation on the same work.')]))
        r.finalize(f.ws,'renamed-b');packets=r.load(f.ws/'dreams/runs/renamed-b/candidates.json')
        self.assertEqual(len(packets),1);new=packets[0]
        self.assertEqual(new['candidate_id'],v['candidate_id']);self.assertEqual(new['revision'],2);self.assertEqual(new['predecessor_hash'],r.digest(v))
        self.assertEqual(new['work_id'],entry['work_id']);self.assertTrue(all(c['state']=='needs-evidence' for c in new['consumer_readiness'].values()))

    def test_documentation_cannot_link_different_existing_work(self):
        import test_work_evidence_docs as docs
        fixture=docs.DocsTests();fixture.setUp();self.addCleanup(fixture.doCleanups);fixture.f.commit()
        f,v,scope,entry=self.native_case(fixture.f)
        other=copy.deepcopy(entry);other.update(entry_id='00000000-0000-4000-8000-000000000098',work_id='00000000-0000-4000-8000-000000000099')
        f.commit(dict(schema_version=1,changes=[dict(entry=other)]))
        request=copy.deepcopy(fixture.procedure);request['work_ids']=[other['work_id']]
        before=f.hashes()
        with self.assertRaises(ValueError):bridge.preview(f.ws,v,scope,'documentation',request)
        self.assertEqual(before,f.hashes())

    def test_source_snapshot_does_not_authorize_a_different_native_work(self):
        import test_work_evidence_report as reports
        fixture=reports.ReportTests();fixture.setUp();self.addCleanup(fixture.doCleanups);fixture.f.commit()
        f,_,scope,entry=self.native_case(fixture.f)
        path=f.root/'dream-source/entry.json';data=json.loads(path.read_text());data['work_id']='00000000-0000-4000-8000-000000000099';path.write_text(json.dumps(data))
        state=r.plan(f.ws,'snapshot-b',scope,PRODUCER,capabilities(),dict(id='reviewer',version='v1',policy_digest='a'*64));deliver(f.ws,'snapshot-b',state)
        rows=[row for row in state['envelope']['inventory'] if row['read_receipt']]
        native=next(row for row in rows if row['relative_path']=='dream-source/entry.json')
        r.submit(f.ws,'snapshot-b',response(state,rows,[finding([native])]))
        r.finalize(f.ws,'snapshot-b');v=r.load(f.ws/'dreams/runs/snapshot-b/candidates.json')[0]
        fixture.policy['texts']=[fixture.approve(entry)];before=f.hashes()
        with self.assertRaises(ValueError):bridge.preview(f.ws,v,scope,'report',fixture.policy)
        fixture.policy['texts']=[]
        with self.assertRaises(ValueError):bridge.preview(f.ws,v,scope,'report',fixture.policy)
        self.assertEqual(before,f.hashes())


if __name__=='__main__':unittest.main()
