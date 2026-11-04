"""Cross-cycle evidence/decision regressions. Synthetic files only."""
import copy
from datetime import timedelta
import unittest
import test_dreaming_chat as fixture
import dreaming_chat as chat


class CrossCycle(fixture.Sessions):
    def cycle_one(self):
        cfg, s, p = self.begin(); self.submit(s, p)
        return cfg, chat.accept(self.config, s['cycle_id'], self.stamp, final=True)

    def test_changed_prior_is_not_presented_as_current_context(self):
        _, first = self.cycle_one()
        (self.root/'sources/note.md').write_text('A newer outcome replaces the old report.')
        _, s = chat.begin(self.config, self.stamp + timedelta(days=3))
        self.assertEqual(s['previous_findings'], [])
        self.assertEqual(s['discarded_previous_findings'], 1)
        self.assertIn(first['findings'][0]['finding_id'], s['finding_lineage'][0]['ids'])
        brief=chat.load(chat.paths(self.cfg,s['cycle_id'])['inputs']/'brief.json')
        self.assertEqual(brief['previous_findings'], [])

    def test_cross_cycle_owner_enrichment_replaces_logical_topic(self):
        (self.root/'sources/second.md').write_text('The same scope, second source.')
        self.cfg['sources'][0]['subject_type']='project'
        chat.atomic(self.config,self.cfg)
        _,first=self.cycle_one()
        _,s=chat.begin(self.config,self.stamp+timedelta(days=3))
        old=first['findings'][0]; newer=copy.deepcopy(old)
        # IDs depend on subjects; logical replacement is deliberately independent.
        newer['finding_id']='new-provenance-id';newer['summary']='Updated outcome'
        merged=chat.merge_findings(s['previous_findings'],[newer],s['finding_lineage'])
        self.assertEqual(len(merged),1)
        self.assertEqual(merged[0]['finding_id'],'new-provenance-id')
        self.assertIn(old['finding_id'],merged[0]['decision_aliases'])

    def test_versions_of_same_locator_do_not_mask_stale_evidence(self):
        _,s,p=self.begin();self.submit(s,p)
        first=chat.accept(self.config,s['cycle_id'],self.stamp)['findings'][0]
        old=copy.deepcopy(first);old['context_refs'][0]['sha256']='f'*64
        fps={(r['source_id'],r['path']):r['sha256'] for r in first['context_refs']}
        self.assertEqual(chat.current_cache([old],fps),[])
        self.assertEqual(chat.current_cache([first],fps),[first])
        both=copy.deepcopy(first);both['context_refs'].extend(old['context_refs'])
        self.assertEqual(chat.current_cache([both],fps),[])

    def test_polluted_cache_fails_closed_until_reviewed(self):
        _,s,p=self.begin();self.submit(s,p)
        first=chat.accept(self.config,s['cycle_id'],self.stamp)['findings'][0]
        other=copy.deepcopy(first);other['finding_id']='other-id'
        fps={(r['source_id'],r['path']):r['sha256'] for r in first['context_refs']}
        self.assertEqual(chat.current_cache([first,other],fps),[])
        with self.assertRaisesRegex(ValueError,'ambiguous-current-findings'):
            chat.merge_findings([],[first,other])

    def test_rejected_deferred_and_implemented_survive_rekey(self):
        cfg,first=self.cycle_one();old=first['findings'][0];new=copy.deepcopy(old)
        new['finding_id']='new-provenance-id'
        merged=chat.merge_findings([old],[new])
        for state in ('rejected','deferred','implemented'):
            with self.subTest(state=state):
                decision={'finding_id':old['finding_id'],'recipient':'owner','state':state,'authority_ref':'owner-decision'}
                if state=='implemented':decision['quality_evidence']={'source_id':'personal','path':'sources/note.md','sha256':'a'*64}
                cfg['decisions']=[decision]
                packet=chat.report_route(cfg,merged)['owner']
                self.assertEqual(packet['findings'],[])
                self.assertEqual(packet['decisions'][0]['authority_ref'],'owner-decision')
                self.assertEqual(cfg['decisions'][0]['finding_id'],old['finding_id'])

    def test_conflicting_alias_decisions_do_not_choose_a_winner(self):
        cfg,first=self.cycle_one();old=first['findings'][0];new=copy.deepcopy(old);new['finding_id']='new-id'
        cfg['decisions']=[{'finding_id':f,'recipient':'owner','state':state,'authority_ref':'original-owner'} for f,state in [(old['finding_id'],'rejected'),('new-id','accepted')]]
        with self.assertRaisesRegex(ValueError,'conflicting-logical-decisions'):
            chat.report_route(cfg,chat.merge_findings([old],[new]))

    def test_aliases_do_not_transfer_technical_recipient_approval(self):
        cfg,first=self.cycle_one();old=first['findings'][0];new=copy.deepcopy(old);new['finding_id']='new-id';new['lens']='systems';new['audiences']=['owner','tech']
        cfg['decisions']=[{'finding_id':old['finding_id'],'recipient':'tech','state':'accepted','authority_ref':'technical-owner'}]
        merged=chat.merge_findings([old],[new]);packet=chat.report_route(cfg,merged)['tech']
        self.assertEqual(packet['decisions'],[])
        self.assertEqual(packet['findings'][0]['state'],'proposed')
        self.assertNotIn('decision_aliases',packet['findings'][0])


    def test_real_second_cycle_rekeys_and_honors_owner_deferral(self):
        from unittest.mock import patch
        (self.root/'other').mkdir();(self.root/'other/note.md').write_text('Company result')
        self.cfg['sources'].append({'id':'work','root':str(self.root),'prefix':'other',
            'owner':'company','subject_type':'project','subject_id':'project',
            'source_class':'work','audiences':['owner','tech'],'sharing_authority':'fixture'})
        chat.atomic(self.config,self.cfg)
        with patch.object(chat,'MAX_CHUNKS',1):
            cfg,s,p=self.begin();self.submit(s,p)
            first=chat.accept(self.config,s['cycle_id'],self.stamp,final=True)
        old=first['findings'][0]
        self.cfg['decisions']=[{'finding_id':old['finding_id'],'recipient':'owner','state':'deferred','authority_ref':'owner-wait'}]
        chat.atomic(self.config,self.cfg)
        _,s=chat.begin(self.config,self.stamp+timedelta(days=3));p=chat.paths(self.cfg,s['cycle_id'])
        self.assertEqual(len(s['input_hashes']),1)
        self.submit(s,p)
        done=chat.accept(self.config,s['cycle_id'],self.stamp+timedelta(days=3),final=True)
        self.assertEqual(len(done['findings']),1)
        self.assertNotEqual(done['findings'][0]['finding_id'],old['finding_id'])
        self.assertIn(old['finding_id'],done['findings'][0]['decision_aliases'])
        self.assertEqual(done['finalization']['superseded_findings'],1)
        self.assertNotIn('### Observed report',(p['report']/'dream-report.md').read_text())

    def test_code_cache_reset_keeps_only_same_manifest_decision_lineage(self):
        cfg,first=self.cycle_one();old=first['findings'][0]
        p=chat.paths(cfg,first['cycle_id']);idx=chat.load(p['control']/'index.json')
        idx['scope_key']='obsolete-analyzer';chat.atomic(p['control']/'index.json',idx)
        _,s=chat.begin(self.config,self.stamp+timedelta(days=3))
        self.assertEqual(s['previous_findings'],[])
        self.assertIn(old['finding_id'],s['finding_lineage'][0]['ids'])
        self.cfg['sources'][0]['sharing_authority']='new-source-owner-scope'
        chat.atomic(self.config,self.cfg)
        _,other=chat.begin(self.config,self.stamp+timedelta(days=7))
        self.assertEqual(other['finding_lineage'],[])

    def test_alias_collision_rejected(self):
        cfg,first=self.cycle_one();a=first['findings'][0];b=copy.deepcopy(a)
        b['topic']='other-topic';b['finding_id']='other-id';b['decision_aliases']=[a['finding_id']]
        with self.assertRaisesRegex(ValueError,'ambiguous-decision-alias'):
            chat.report_route(cfg,[a,b])


    def test_legacy_reset_with_owner_decisions_cannot_reopen_by_rekey(self):
        cfg,first=self.cycle_one();p=chat.paths(cfg,first['cycle_id'])
        idx=chat.load(p['control']/'index.json');idx.pop('lineage_scope');idx['scope_key']='old-code'
        chat.atomic(p['control']/'index.json',idx)
        self.cfg['decisions']=[{'finding_id':first['findings'][0]['finding_id'],
            'recipient':'owner','state':'rejected','authority_ref':'original-owner'}]
        chat.atomic(self.config,self.cfg)
        with self.assertRaisesRegex(ValueError,'unverified-decision-lineage'):
            chat.begin(self.config,self.stamp+timedelta(days=3))


if __name__=='__main__':unittest.main()
