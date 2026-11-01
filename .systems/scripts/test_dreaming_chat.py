"""Observable chat-session contracts; all fixtures are synthetic and local."""
import json
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import os
import unittest
from unittest.mock import patch

import dreaming_chat as chat


class Sessions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); (self.root/'sources').mkdir()
        (self.root/'sources/note.md').write_text('A documented result.\n')
        self.cfg = {'schema_version':2,'authority_ref':'synthetic-owner-request',
                    'report_owner':'owner','workspace':str(self.root),
                    'analyzer':{'model':'test','version':'chat-v1','cli_version':'test',
                                'cli_sha256':'0'*64,'executable':'/usr/bin/true'},
                    'sources':[{'id':'personal','root':str(self.root),'prefix':'sources',
                                'owner':'owner','subject_type':'person','subject_id':'owner',
                                'source_class':'personal','audiences':['owner'],'sharing_authority':'owner'}],
                    'recipients':{'owner':{'adapter':'owner-report','lenses':['person','brand','company','systems']},
                                  'tech':{'adapter':'proposal','lenses':['systems']}},'decisions':[]}
        self.config = self.root/'config.json'; chat.atomic(self.config,self.cfg)
        self.stamp = datetime(2026,10,21,2,tzinfo=chat.ZONE)

    def begin(self):
        cfg,s = chat.begin(self.config,self.stamp); return cfg,s,chat.paths(cfg,s['cycle_id'])

    def submit(self,s,p,**overrides):
        ids=list(s['input_hashes'])
        f={'topic':'reported-result','lens':'person','kind':'keep','summary':'Observed report',
           'facts':['The source reports a result.'],'inferences':[],'unknowns':[],
           'actions':['Keep recording outcomes.'],'evidence_ids':ids[:1]}
        value={'cycle_id':s['cycle_id'],'revision':1,'reviewed_chunk_ids':ids,
               'findings':[f],'synthesis_complete':True}
        value.update(overrides); chat.atomic(p['drafts']/'checkpoint.json',value)

    def test_prepare_is_not_review(self):
        _,s,_=self.begin()
        self.assertFalse(s['accepted']); self.assertEqual(s['coverage'][0]['state'],'pending')

    def test_checkpoint_private_report_and_incremental_reuse(self):
        _,s,p=self.begin(); self.submit(s,p)
        done=chat.accept(self.config,s['cycle_id'],self.stamp,final=True)
        self.assertEqual(done['status'],'completed');self.assertEqual(done['coverage_counts']['reviewed'],1)
        self.assertEqual(done['findings'][0]['audiences'],['owner'])
        self.assertTrue((p['report']/'dream-report.md').is_file())
        _,nexts=chat.begin(self.config,self.stamp+timedelta(days=3))
        self.assertEqual(nexts['input_hashes'],{});self.assertEqual(len(nexts['previous_findings']),1)

    def enrichment(self):
        (self.root/'other').mkdir()
        # Copies with different provenance are not independent confirmation.
        (self.root/'other/note.md').write_text('A documented result.\n')
        self.cfg['sources'].append({'id':'work','root':str(self.root),'prefix':'other',
            'owner':'company','subject_type':'project','subject_id':'project',
            'source_class':'work','audiences':['owner','tech'],'sharing_authority':'fixture'})
        chat.atomic(self.config,self.cfg)
        _,s,p=self.begin();ids=list(s['input_hashes'])
        personal=next(cid for cid in ids if chat.load(p['inputs']/(cid+'.json'))['ref']['source_class']=='personal')
        self.submit(s,p,reviewed_chunk_ids=[personal],synthesis_complete=False)
        draft=chat.load(p['drafts']/'checkpoint.json')
        draft['findings'][0]['evidence_ids']=[personal]
        chat.atomic(p['drafts']/'checkpoint.json',draft)
        accepted=chat.accept(self.config,s['cycle_id'],self.stamp)
        draft['revision']=2;draft['reviewed_chunk_ids']=ids
        draft['findings'][0]['evidence_ids']=ids
        return s,p,accepted,draft

    def test_cumulative_enrichment_across_subjects_preserves_knowledge(self):
        s,p,accepted,draft=self.enrichment()
        f=draft['findings'][0];f['facts'].append('Another source records the same result.')
        f['summary']='The recorded result has additional provenance.'
        f['unknowns']=['Independent success remains unverified.']
        draft['synthesis_complete']=True
        chat.atomic(p['drafts']/'checkpoint.json',draft)
        done=chat.accept(self.config,s['cycle_id'],self.stamp,final=True)
        f=done['findings'][0]
        self.assertEqual(done['status'],'completed')
        self.assertEqual(done['coverage_counts']['reviewed'],2)
        self.assertEqual(set(f['owners']),{'owner','company'})
        self.assertNotEqual(f['finding_id'],accepted['findings'][0]['finding_id'])
        self.assertEqual(f['audiences'],['owner'])
        self.assertEqual(f['distinct_source_contents'],1)
        self.assertEqual(len(f['evidence_ids']),2)
        self.assertIn('The source reports a result.',f['facts'])
        self.assertIn('additional provenance',(p['report']/'dream-report.md').read_text())

    def test_checkpoint_rejects_lost_finding_after_subject_enrichment(self):
        s,p,_,draft=self.enrichment();draft['findings']=[]
        chat.atomic(p['drafts']/'checkpoint.json',draft)
        with self.assertRaisesRegex(ValueError,'checkpoint-lost-findings'):
            chat.accept(self.config,s['cycle_id'],self.stamp)
        self.assertEqual(chat.load(p['state'])['checkpoint_revision'],1)

    def test_checkpoint_rejects_lost_facts_or_evidence(self):
        s,p,_,draft=self.enrichment()
        for field in ('facts','evidence_ids'):
            with self.subTest(field=field):
                changed=json.loads(json.dumps(draft))
                if field=='facts':changed['findings'][0][field]=['A replacement claim.']
                else:
                    original=chat.load(p['state'])['findings'][0]['evidence_ids'][0]
                    changed['findings'][0][field]=[cid for cid in draft['reviewed_chunk_ids'] if cid!=original]
                chat.atomic(p['drafts']/'checkpoint.json',changed)
                with self.assertRaisesRegex(ValueError,'checkpoint-lost-claims'):
                    chat.accept(self.config,s['cycle_id'],self.stamp)
                self.assertEqual(chat.load(p['state'])['checkpoint_revision'],1)

    def test_checkpoint_rejects_ambiguous_topic_lens(self):
        s,p,_,draft=self.enrichment()
        duplicate=json.loads(json.dumps(draft['findings'][0]))
        duplicate['evidence_ids']=draft['reviewed_chunk_ids'][:1]
        draft['findings'].append(duplicate)
        chat.atomic(p['drafts']/'checkpoint.json',draft)
        with self.assertRaisesRegex(ValueError,'checkpoint-ambiguous-findings'):
            chat.accept(self.config,s['cycle_id'],self.stamp)
        self.assertEqual(chat.load(p['state'])['checkpoint_revision'],1)

    def test_changed_sources_lose_claims(self):
        _,s,p=self.begin();self.submit(s,p)
        checkpoint=(p['drafts']/'checkpoint.json').read_bytes()
        (self.root/'sources/note.md').write_text('Changed after analysis')
        done=chat.accept(self.config,s['cycle_id'],self.stamp,final=True)
        self.assertEqual(done['findings'],[]);self.assertEqual(done['changed_count'],1)
        self.assertEqual(done['finalization'],{'draft_findings':1,'previous_findings':0,
            'invalidated_findings':1,'verified_findings':0,'changed_sources':1})
        self.assertEqual((p['drafts']/'checkpoint.json').read_bytes(),checkpoint)
        report=(p['report']/'dream-report.md').read_text()
        self.assertIn('wycofane po kontroli aktualności',report)
        self.assertIn('nie są aktualnymi wnioskami',report)
        self.assertNotIn('Observed report',report)

    def test_changed_uncited_context_still_invalidates_claim(self):
        (self.root/'sources/context.md').write_text('Other read context.')
        _,s,p=self.begin();self.submit(s,p)
        draft=chat.load(p['drafts']/'checkpoint.json')
        cited=draft['findings'][0]['evidence_ids'][0]
        other=next(cid for cid in s['input_hashes'] if cid!=cited)
        changed=chat.load(p['inputs']/(other+'.json'))['ref']['path']
        (self.root/changed).write_text('Changed uncited context.')
        done=chat.accept(self.config,s['cycle_id'],self.stamp,final=True)
        self.assertEqual(done['findings'],[])
        self.assertEqual(done['coverage_counts']['reviewed'],1)
        self.assertEqual(done['finalization']['invalidated_findings'],1)

    def test_empty_analysis_is_distinct_from_invalidated_analysis(self):
        _,s,p=self.begin();self.submit(s,p,findings=[])
        done=chat.accept(self.config,s['cycle_id'],self.stamp,final=True)
        self.assertEqual(done['status'],'completed')
        self.assertEqual(done['finalization']['invalidated_findings'],0)
        self.assertNotIn('unieważnia zależne ustalenia',(p['report']/'dream-report.md').read_text())

    def test_revoked_configuration(self):
        _,s,p=self.begin();self.submit(s,p)
        self.cfg['sources'][0]['sharing_authority']='revoked';chat.atomic(self.config,self.cfg)
        with self.assertRaisesRegex(ValueError,'configuration-revoked'):chat.accept(self.config,s['cycle_id'],self.stamp)

    def test_restart_retains_cycle_and_original_deadline(self):
        _,s,_=self.begin();_,resumed=chat.begin(self.config,self.stamp+timedelta(minutes=5),cycle=s['cycle_id'])
        self.assertEqual(resumed['cycle_id'],s['cycle_id']);self.assertEqual(resumed['deadline'],s['deadline'])
        self.assertEqual(resumed['attempt'],2)

    def test_parallel_start_locked(self):
        with chat.lock(self.root/'dreams/chat-control'):
            with self.assertRaises(BlockingIOError):self.begin()

    def test_deadline_not_reset(self):
        _,s,p=self.begin();self.submit(s,p)
        with self.assertRaisesRegex(ValueError,'session-deadline'):
            chat.accept(self.config,s['cycle_id'],self.stamp+timedelta(hours=3))

    def test_no_nonexistent_or_unprepared_evidence(self):
        _,s,p=self.begin();self.submit(s,p,reviewed_chunk_ids=['not-a-chunk'])
        with self.assertRaisesRegex(ValueError,'unprepared-evidence'):chat.accept(self.config,s['cycle_id'],self.stamp)

    def test_malformed_model_checkpoint(self):
        _,s,p=self.begin();chat.atomic(p['drafts']/'checkpoint.json',{'findings':[]})
        with self.assertRaisesRegex(ValueError,'invalid-checkpoint'):chat.accept(self.config,s['cycle_id'],self.stamp)

    def test_symlink_snapshot_rejected(self):
        _,s,p=self.begin();self.submit(s,p)
        cid=next(iter(s['input_hashes']));file=p['inputs']/(cid+'.json');file.unlink();file.symlink_to(self.config)
        with self.assertRaises(OSError):chat.accept(self.config,s['cycle_id'],self.stamp)

    def test_secret_marker_not_staged(self):
        (self.root/'sources/note.md').write_text('password = synthetic-secret-canary-123')
        _,s,_=self.begin();self.assertEqual(s['input_hashes'],{});self.assertEqual(s['coverage'][0]['state'],'blocked')

    def test_custom_token_assignments_never_reach_prepared_inputs(self):
        opaque = 'fixture-' + 'a1B2c3D4' * 3
        cases = [
            'https://example.invalid/audit?' + 'audittoken=' + opaque,
            'httpsmalformed.invalid/audittoken=' + opaque,
            json.dumps({'audit_token': opaque}),
            json.dumps({'password': opaque}),
            'AUDIT-TOKEN = "' + opaque + '"',
            'audittoken%3D%22' + opaque + '%22',
            'audittoken=' + ''.join('%%%02x' % ord(c) for c in opaque),
            json.dumps({'note': json.dumps({'audit_token': opaque})}),
        ]
        for index, text in enumerate(cases):
            with self.subTest(case=index):
                (self.root/'sources/note.md').write_text(text)
                # Distinct manual identities; never reuse a prepared snapshot.
                _, s = chat.begin(self.config, self.stamp, manual=True)
                p = chat.paths(self.cfg, s['cycle_id'])
                self.assertEqual(s['input_hashes'], {})
                self.assertEqual(s['coverage'][0]['state'], 'blocked')
                self.assertEqual(list(p['inputs'].glob('*.json')), [p['inputs']/'brief.json'])

    def test_custom_token_in_model_output_rejected(self):
        opaque = 'fixture-' + 'a1B2c3D4' * 3
        for index, text in enumerate(('audit_token=' + opaque,
                                      json.dumps({'audit_token': opaque}))):
            with self.subTest(case=index):
                _, s = chat.begin(self.config, self.stamp, manual=True)
                p = chat.paths(self.cfg, s['cycle_id'])
                self.submit(s, p)
                draft = chat.load(p['drafts']/'checkpoint.json')
                draft['findings'][0]['summary'] = text
                chat.atomic(p['drafts']/'checkpoint.json', draft)
                with self.assertRaisesRegex(ValueError, 'credential-in-output'):
                    chat.accept(self.config, s['cycle_id'], self.stamp, final=True)
                self.assertFalse((p['report']/'dream-report.md').exists())

    def test_token_prose_and_personal_fields_remain_readable(self):
        (self.root/'sources/note.md').write_text(
            'Token purchase usability is unknown. Token count: 150.\n'
            'Mental clarity: 4. Reflections and goals remain personal.\n'
            'No access token was provided. Tokenization is a topic, not a credential.\n')
        _, s, _ = self.begin()
        self.assertTrue(s['input_hashes'])
        self.assertEqual(s['coverage'][0]['state'], 'pending')

    def test_chunk_limit_does_not_permanently_truncate_file(self):
        (self.root/'sources/note.md').write_text('word '*10000)
        with patch.object(chat,'MAX_CHUNKS',1):
            _,s,p=self.begin();self.submit(s,p);first=chat.accept(self.config,s['cycle_id'],self.stamp,final=True)
            self.assertEqual(first['coverage_counts']['pending'],1)
            _,s2=chat.begin(self.config,self.stamp+timedelta(days=3))
            self.assertTrue(s2['input_hashes']);self.assertFalse(set(s['input_hashes'])&set(s2['input_hashes']))

    def test_slot_winter_summer_and_no_thursday(self):
        with self.assertRaisesRegex(ValueError,'outside-slot'):chat.begin(self.config,datetime(2026,10,22,2,tzinfo=chat.ZONE))
        for stamp in [datetime(2026,7,1,2,tzinfo=chat.ZONE),datetime(2026,12,2,2,tzinfo=chat.ZONE)]:
            _,s=chat.begin(self.config,stamp);self.assertEqual(s['deadline']-stamp.timestamp(),7200)

    def test_duplicate_completed_slot_cannot_overwrite_report(self):
        _,s,p=self.begin();self.submit(s,p);chat.accept(self.config,s['cycle_id'],self.stamp,final=True)
        before=(p['report']/'dream-report.md').read_bytes()
        with self.assertRaisesRegex(ValueError,'cycle-terminal'):self.begin()
        self.assertEqual(before,(p['report']/'dream-report.md').read_bytes())

    def test_analyzer_change_does_not_reuse_old_analysis(self):
        _,s,p=self.begin();self.submit(s,p);chat.accept(self.config,s['cycle_id'],self.stamp,final=True)
        self.cfg['analyzer']['version']='chat-v2';chat.atomic(self.config,self.cfg)
        _,new=chat.begin(self.config,self.stamp+timedelta(days=3))
        self.assertTrue(new['input_hashes']);self.assertEqual(new['previous_findings'],[])

    def test_new_imported_file_precedes_known_history_even_with_old_mtime(self):
        for i in range(3):
            f=self.root/'sources'/f'history-{i}.md';f.write_text(f'History {i}');os.utime(f,(i+1,i+1))
        os.utime(self.root/'sources/note.md',(1,1))
        with patch.object(chat,'MAX_CHUNKS',1):
            _,s,p=self.begin();self.submit(s,p);chat.accept(self.config,s['cycle_id'],self.stamp,final=True)
            f=self.root/'sources/new-import.md';f.write_text('Newly imported evidence');os.utime(f,(1,1))
            cfg,nexts=chat.begin(self.config,self.stamp+timedelta(days=3))
            np=chat.paths(cfg,nexts['cycle_id']);cid=next(iter(nexts['input_hashes']))
            self.assertEqual(chat.load(np['inputs']/(cid+'.json'))['ref']['path'],'sources/new-import.md')

    def test_large_source_does_not_starve_other_owner_perspective(self):
        (self.root/'sources/note.md').write_text('large '*10000)
        (self.root/'company').mkdir();(self.root/'company/brief.md').write_text('Company result')
        self.cfg['sources'].append({'id':'company','root':str(self.root),'prefix':'company','owner':'owner',
            'subject_type':'company','subject_id':'company','source_class':'work','audiences':['owner'],'sharing_authority':'owner'})
        chat.atomic(self.config,self.cfg)
        with patch.object(chat,'MAX_CHUNKS',2):
            _,s,p=self.begin()
            owners={chat.load(p['inputs']/(cid+'.json'))['ref']['source_id'] for cid in s['input_hashes']}
            self.assertEqual(owners,{'personal','company'})

    def test_shared_context_is_small_and_round_trips(self):
        refs=[{'source_id':'synthetic','path':f'source-{i}.md','sha256':'a'*64,'owner':'owner'} for i in range(50)]
        value={'findings':[{'finding_id':str(i),'context_refs':refs,'summary':'A finding'} for i in range(50)],
               'previous_findings':[{'finding_id':str(i),'context_refs':refs,'summary':'A finding'} for i in range(50)]}
        target=self.root/'state.json';chat.atomic(target,value)
        self.assertLess(target.stat().st_size,80000)
        restored=chat.load(target)
        self.assertEqual(len(restored['findings']),50)
        self.assertEqual({chat.digest(r) for r in restored['findings'][0]['context_refs']},{chat.digest(r) for r in refs})
        raw=json.loads(target.read_text());first=next(iter(raw['_context_registry']['refs']))
        raw['_context_registry']['refs'][first]['path']='tampered'
        target.write_text(json.dumps(raw))
        with self.assertRaisesRegex(ValueError,'context-reference-drift'):chat.load(target)

    def test_model_cannot_inject_trusted_context_registry(self):
        _,s,p=self.begin();self.submit(s,p)
        draft=json.loads((p['drafts']/'checkpoint.json').read_text());draft['_context_registry']={'refs':{},'sets':{}}
        (p['drafts']/'checkpoint.json').write_text(json.dumps(draft))
        with self.assertRaisesRegex(ValueError,'invalid-checkpoint'):chat.accept(self.config,s['cycle_id'],self.stamp)

    def test_three_cycles_keep_one_copy_of_each_context_reference(self):
        for number,offset in enumerate((0,3,7)):
            if number:(self.root/'sources'/f'new-{number}.md').write_text(f'New evidence {number}')
            stamp=self.stamp+timedelta(days=offset);cfg,s=chat.begin(self.config,stamp);p=chat.paths(cfg,s['cycle_id'])
            self.submit(s,p);draft=json.loads((p['drafts']/'checkpoint.json').read_text());base=draft['findings'][0]
            draft['findings']=[{**base,'topic':f'topic-{number}-{i}'} for i in range(20)]
            chat.atomic(p['drafts']/'checkpoint.json',draft)
            result=chat.accept(self.config,s['cycle_id'],stamp,final=True)
            newest=[f for f in result['findings'] if f['topic'].startswith(f'topic-{number}-')]
            self.assertEqual(len(newest),20)
            for finding in newest:self.assertEqual(len(finding['context_refs']),number+1)
            self.assertLess((p['control']/'index.json').stat().st_size,200000)


if __name__=='__main__':unittest.main()
