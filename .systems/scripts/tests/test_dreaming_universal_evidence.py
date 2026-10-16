"""Pure cross-product contract tests; synthetic provenance only."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dreaming_universal_evidence import findings, route


class Contract(unittest.TestCase):
    def sample(self, personal=False):
        ref = {'owner':'owner','subject_type':'project','subject_id':'project','source_class':'personal' if personal else 'work',
               'audiences':['owner'] if personal else ['owner','technical'], 'sha256':'a'*64}
        chunks = [{'chunk_id':'evidence','ref':ref}]
        raw = {'findings':[{'topic':'repeatable-procedure','lens':'systems','kind':'keep','summary':'Procedure documented.',
            'facts':['Source describes a procedure.'],'inferences':[],'unknowns':['No result verified.'],
            'actions':['Review the procedure.'],'evidence_ids':['evidence']}]}
        return raw,chunks
    def test_generic_not_forced_to_work_entry(self):
        raw,chunks=self.sample(); chunks[0]['ref']['subject_type']='company'
        f=findings(raw,chunks,'owner')[0]
        self.assertNotIn('work_id',f); self.assertNotIn('duration',f)
    def test_identity_stable_across_evidence_version(self):
        raw,chunks=self.sample(); first=findings(raw,chunks,'owner')[0]
        chunks[0]['ref']['sha256']='b'*64
        self.assertEqual(first['finding_id'],findings(raw,chunks,'owner')[0]['finding_id'])
    def test_personal_context_not_reclassified_by_selective_citation(self):
        raw,chunks=self.sample(); private=self.sample(True)[1][0];private['chunk_id']='private'
        f=findings(raw,chunks+[private],'owner')[0]
        self.assertEqual(f['audiences'],['owner']);self.assertEqual(f['privacy'],'personal')
    def test_independent_recipient_decisions(self):
        raw,chunks=self.sample();fs=findings(raw,chunks,'owner')
        recipients={r:{'lenses':['systems'],'adapter':'proposal'} for r in ('owner','technical')}
        d={'finding_id':fs[0]['finding_id'],'recipient':'technical','state':'rejected','authority_ref':'owner:decision'}
        packets=route(fs,recipients,'owner',[d])
        self.assertTrue(packets['owner']['findings']);self.assertFalse(packets['technical']['findings'])
    def test_unknown_citation_rejected(self):
        raw,chunks=self.sample();raw['findings'][0]['evidence_ids']=['made-up']
        with self.assertRaisesRegex(ValueError,'uncited-finding'):findings(raw,chunks,'owner')
    def test_duplicates_are_not_independent_sources(self):
        raw,chunks=self.sample();chunks.append({'chunk_id':'copy','ref':dict(chunks[0]['ref'])})
        raw['findings'][0]['evidence_ids'].append('copy')
        self.assertEqual(findings(raw,chunks,'owner')[0]['distinct_source_contents'],1)

    def test_derived_context_preserves_personal_taint(self):
        raw,chunks=self.sample();private=self.sample(True)[1][0]['ref']
        chunks[0]['refs']=[chunks[0]['ref']]
        chunks[0]['context_refs']=[chunks[0]['ref'],private]
        del chunks[0]['ref']
        f=findings(raw,chunks,'owner')[0]
        self.assertEqual(f['privacy'],'personal')
        self.assertEqual(f['audiences'],['owner'])

    def test_implemented_state_needs_quality_reference(self):
        raw,chunks=self.sample();fs=findings(raw,chunks,'owner')
        recipients={'owner':{'lenses':['systems'],'adapter':'owner-report'}}
        decision={'finding_id':fs[0]['finding_id'],'recipient':'owner','state':'implemented','authority_ref':'owner:decision'}
        with self.assertRaisesRegex(ValueError,'implemented-needs-quality-evidence'):route(fs,recipients,'owner',[decision])

if __name__=='__main__':unittest.main()
