"""Chat transport safety and recovery, without model calls or private data."""
from datetime import timedelta
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import dreaming_chat as session
import dreaming_chat_dispatch as dispatch
from test_dreaming_chat import Sessions


class Controller(Sessions):
    # Session fixture/tests are inherited so both surfaces exercise the same contract.
    def setUp(self):
        super().setUp()
        self.c={'thread_id':'00000000-0000-0000-0000-000000000000',
                'profile_id':'dreaming-chat','executable':'/usr/bin/true','poll_seconds':1,
                'source_config':str(self.config)}

    def test_exact_input_output_roots_without_workspace_or_home_grant(self):
        _,s,p=self.begin();profile=dispatch.permissions(self.c,p)
        self.assertEqual(profile['filesystem'][':root'],'deny')
        self.assertEqual(profile['filesystem'][str(p['inputs'])],'read')
        self.assertEqual(profile['filesystem'][str(p['drafts'])],'write')
        self.assertNotIn(':workspace_roots',profile['filesystem'])
        self.assertFalse(profile['network']['enabled'])

    def test_native_probe_rejects_fake_restricted_profile(self):
        _,s,p=self.begin()
        class Client:
            def rpc(self,*_):return {'exitCode':0,'stdout':json.dumps({'input':True,'outside':True,'credential':True,'output':True,'input_write':True,'credential_env':False})}
        with self.assertRaisesRegex(ValueError,'native-isolation-failed'):dispatch.native_probe(Client(),self.c,p)

    def test_native_probe_unavailable_does_not_start_analysis(self):
        _,s,p=self.begin()
        class Client:
            def rpc(self,*_):return {'exitCode':1,'stdout':''}
        with self.assertRaisesRegex(ValueError,'native-isolation-unavailable'):dispatch.native_probe(Client(),self.c,p)

    def test_queue_reserves_and_restricts_before_input(self):
        _,s,p=self.begin();events=[]
        class Client:
            def rpc(_,method,params):
                events.append(method)
                if method=='thread/settings/update':
                    self.assertEqual(params['permissions'],'dreaming-chat')
                    self.assertTrue((p['control']/'dispatch.json').exists())
                if method=='thread/queue/add':return {'queuedSubmission':{'id':'q1'}}
                if method=='thread/queue/start':return {'turn':{'id':'t1'}}
        mod=SimpleNamespace(RpcError=RuntimeError,submission_turn=lambda *a,**k:{'id':'t1','status':'inProgress'})
        d=dispatch.queue(Client(),mod,self.c,s,p,{},'synthetic prompt')
        self.assertEqual(events[0],'thread/settings/update');self.assertEqual(d['turn_id'],'t1')
        self.assertIn(s['cycle_id'],d['client_id'])

    def test_queue_response_lost_is_not_replayed(self):
        _,s,p=self.begin();count=[]
        class Client:
            def rpc(_,method,params):
                if method=='thread/queue/add':count.append(1);raise TimeoutError('synthetic disconnect')
        mod=SimpleNamespace(RpcError=RuntimeError)
        with self.assertRaises(TimeoutError):dispatch.queue(Client(),mod,self.c,s,p,{},'prompt')
        self.assertEqual(len(count),1)
        saved=session.load(p['control']/'dispatch.json');self.assertEqual(saved['status'],'reserved')

    def test_failed_cleanup_never_restores_live_turn(self):
        _,s,p=self.begin();events=[]
        session.atomic(p['control']/'dispatch.json',{'status':'running','client_id':'own','turn_id':'own-turn','restore':{'permissions':':workspace'}})
        class Client:
            def rpc(_,method,params):events.append((method,params));return {}
        mod=SimpleNamespace(submission_turn=lambda *a,**k:{'id':'own-turn','status':'inProgress'})
        with patch.object(dispatch.time,'monotonic',side_effect=[0,31]):
            with self.assertRaisesRegex(ValueError,'own-turn-still-active'):dispatch.cancel_owned(Client(),mod,self.c,self.cfg,p)
        self.assertEqual(events[0][1]['turnId'],'own-turn')
        self.assertFalse(any(m=='thread/settings/update' for m,_ in events))

    def test_busy_slot_expiry_never_starts_late(self):
        class Client:
            def rpc(self,*_):raise AssertionError('no RPC outside schedule')
        with patch.object(session,'clock',return_value=self.stamp+timedelta(hours=1)):
            self.assertFalse(dispatch.wait_idle(Client(),self.c,False))

    def test_prompt_contains_actual_analysis_checkpoint_and_report(self):
        _,s,p=self.begin();prompt=dispatch.analysis_prompt(s,p)
        self.assertIn(str(p['drafts']/'checkpoint.json'),prompt)
        self.assertIn(str(p['report']/'dream-report.md'),prompt)
        self.assertNotIn('BEGIN DREAMING RENDER',prompt)

    def test_profile_change_revokes_access_before_more_work(self):
        _,s,p=self.begin();profile=dispatch.permissions(self.c,p)
        class Client:
            def rpc(self,*_):return {'config':{'permissions':{'dreaming-chat':profile}}}
        dispatch.verify_profile(Client(),self.c,p)
        profile['filesystem'][':root']='read'
        with self.assertRaisesRegex(ValueError,'permission-profile-drift'):dispatch.verify_profile(Client(),self.c,p)

    def test_analysis_validation_precedes_verified_summary(self):
        _,s,p=self.begin();self.submit(s,p);events=[]
        class Client:
            def rpc(_,method,params):
                events.append(method)
                if method=='thread/queue/add':return {'queuedSubmission':{'id':'summary-q'}}
                if method=='thread/queue/start':return {'turn':{'id':'summary-t'}}
        def own(_client,pid,**kwargs):
            is_summary=pid.endswith(':summary')
            return {'id':'summary-t' if is_summary else 'analysis-t','status':'completed',
                    'items':[{'type':'agentMessage','phase':'final_answer','text':str(p['report']/'dream-report.md') if is_summary else 'pending verification'}]}
        mod=SimpleNamespace(RpcError=RuntimeError,submission_turn=own)
        d={'controller_config':'fixture','restore':{},'client_id':'analysis','turn_id':'analysis-t','phase':'analysis'}
        with patch.object(dispatch,'controller_config',return_value=(self.c,self.cfg)),patch.object(dispatch,'verify_profile'),patch.object(session,'clock',return_value=self.stamp):
            result=dispatch.monitor(Client(),mod,self.c,self.cfg,s,p,d)
        self.assertEqual(result['status'],'completed')
        self.assertEqual(session.load(p['control']/'dispatch.json')['status'],'finalized')
        self.assertTrue((p['report']/'dream-report.md').exists())

    def test_controller_change_cancels_before_accepting_checkpoint(self):
        _,s,p=self.begin();self.submit(s,p)
        changed={**self.c,'thread_id':'different'}
        d={'controller_config':'fixture'}
        with patch.object(dispatch,'controller_config',return_value=(changed,self.cfg)),patch.object(session,'clock',return_value=self.stamp):
            with self.assertRaisesRegex(ValueError,'controller-config-drift'):
                dispatch.monitor(None,None,self.c,self.cfg,s,p,d)
        self.assertEqual(session.load(p['state'])['checkpoint_revision'],0)

    def test_large_installed_runtime_is_hashable_but_linked_runtime_is_not(self):
        binary=self.root/'runtime.bin'
        with binary.open('wb') as stream:stream.truncate(270*1024*1024)
        with binary.open('rb') as stream:expected=hashlib.file_digest(stream,'sha256').hexdigest()
        self.assertEqual(dispatch.pinned_digest(binary),expected)
        link=self.root/'linked-runtime';link.symlink_to(binary)
        with self.assertRaises(OSError):dispatch.pinned_digest(link)


if __name__=='__main__':unittest.main()
