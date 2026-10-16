import unittest,sys,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import dreaming_candidates as c
from dreaming_contracts import CONSUMERS

def evidence(h='a'):
    return dict(source_root_id='root-a',relative_path='note.md',project_id='project-a',owner_workspace_id='workspace-a',sha256=h*64,byte_count=1,observed_at='2026-10-12T12:00:00+00:00',fact_date='unknown',evidence_level='observed',source_class='work')
def context():return dict(work_id=None,case_ref=None,signals={x:{} for x in CONSUMERS},conflicts=[])
def claims(h='a'):return dict(facts=[dict(text='DONE label, elapsed time unknown',source_hashes=[h*64],evidence_level='observed')],inferences=[],unknowns=[])
def make(ref=None,ctx=None,previous=None,decision=None):return c.reconcile('workspace-a','project-a','case-a',ref or [evidence()],claims((ref or [evidence()])[0]['sha256'][0]),ctx or context(),previous,decision)

class Candidates(unittest.TestCase):
    def test_done_no_hours_many_sources(self):
        ref=evidence();second=copy.deepcopy(ref);second['relative_path']='duplicate.md'
        v=make([ref,ref,second]);self.assertIsNone(c.summary(v)['actual_seconds']);self.assertEqual(c.summary(v)['work_events'],0);self.assertEqual(c.summary(v)['distinct_source_bytes'],1)
        self.assertEqual(v['consumer_readiness']['ledger']['state'],'needs-evidence')
    def test_existing_case_readiness_independent(self):
        ctx=context();ctx.update(work_id='event-a',case_ref='case-existing')
        ctx['signals']['report']={x:'a'*64 for x in c.REQUIREMENTS['report']};v=make(ctx=ctx)
        self.assertEqual(v['intent'],'enrich-case');self.assertEqual(v['work_id'],'event-a');self.assertEqual(v['consumer_readiness']['report']['state'],'ready-for-review');self.assertEqual(v['consumer_readiness']['documentation']['state'],'needs-evidence')
    def test_rejected_needs_new_evidence_and_decision(self):
        prior=make();decision=dict(state='rejected',candidate_hash=c.digest(prior),decision_ref='decision-a',reopen_approved=False)
        with self.assertRaises(c.ProtocolError):make([evidence('b')],previous=prior,decision=decision)
        decision['reopen_approved']=True;v=make([evidence('b')],previous=prior,decision=decision);self.assertEqual(v['revision'],2);self.assertEqual(v['predecessor_hash'],c.digest(prior))
    def test_cross_owner_conflicts(self):
        ref=evidence();ref['owner_workspace_id']='workspace-b'
        with self.assertRaises(c.ProtocolError):make([ref])
        ctx=context();ctx['conflicts']=['Different source hashes need current owner review'];v=make(ctx=ctx)
        self.assertTrue(all(x['state']=='needs-owner-decision' for x in v['consumer_readiness'].values()))
    def test_recorded_rejection_cannot_disappear_and_idempotency(self):
        prior=make();self.assertEqual(make(previous=prior),prior)
        decision=dict(state='rejected',candidate_hash=c.digest(prior),decision_ref='decision-a',reopen_approved=False)
        rejected=c.record_decision(prior,decision)
        with self.assertRaises(c.ProtocolError):make([evidence('b')],previous=rejected)
        ctx=context();ctx['case_ref']='case-existing';updated=make(ctx=ctx,previous=prior)
        self.assertEqual(updated['intent'],'enrich-case');self.assertEqual(updated['revision'],2)

if __name__=='__main__':unittest.main()
