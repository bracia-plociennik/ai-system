"""Observable chat-session contracts; all fixtures are synthetic and local."""
import json
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
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

    def test_changed_sources_lose_claims(self):
        _,s,p=self.begin();self.submit(s,p)
        (self.root/'sources/note.md').write_text('Changed after analysis')
        done=chat.accept(self.config,s['cycle_id'],self.stamp,final=True)
        self.assertEqual(done['findings'],[]);self.assertEqual(done['changed_count'],1)

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


if __name__=='__main__':unittest.main()
