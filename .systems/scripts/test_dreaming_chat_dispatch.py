"""Default owner settings and observable queue/recovery contracts. Synthetic only."""
from datetime import timedelta
import ast
import hashlib
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import dreaming_chat as session
import dreaming_chat_dispatch as dispatch
from test_dreaming_chat import Sessions


def standard():
    return {'cwd':'/synthetic','model':'gpt-6.1-sol','approvalPolicy':'on-request',
            'approvalsReviewer':'auto_review','activePermissionProfile':{'id':':workspace'},
            'sandbox':{'type':'workspaceWrite'},'collaborationMode':{'mode':'default'}}


class Controller(Sessions):
    def setUp(self):
        super().setUp()
        self.c={'thread_id':'00000000-0000-0000-0000-000000000000',
                'mode':'approve-for-me','executable':'/usr/bin/true','poll_seconds':1,
                'source_config':str(self.config)}
        self.digest=session.digest(dispatch.standard_settings(standard()))

    def test_delayed_auto_consumption_is_reconciled_without_replay(self):
        _,s,p=self.begin();events=[];seen=iter([None,{'id':'late-own','status':'inProgress'}])
        class Client:
            def rpc(_,method,params):
                events.append(method)
                if method=='thread/queue/add':return {'queuedSubmission':{'id':'q1'}}
                if method=='thread/queue/start':raise RuntimeError('already auto-consumed')
        mod=SimpleNamespace(RpcError=RuntimeError,submission_turn=lambda *a,**k:next(seen))
        with patch.object(dispatch.time,'sleep'):
            result=dispatch.queue(Client(),mod,self.c,s,p,{},'synthetic')
        self.assertEqual(result['turn_id'],'late-own')
        self.assertEqual(events.count('thread/queue/add'),1)
        self.assertFalse(any(m.startswith(('config/','thread/settings/')) for m in events))

    def test_queue_does_not_change_owner_settings_and_clears_previous_phase_identity(self):
        _,s,p=self.begin();events=[]
        class Client:
            def rpc(_,method,params):
                events.append(method)
                if method.startswith(('thread/settings/','config/')):
                    raise AssertionError('owner settings must remain unchanged')
                if method=='thread/queue/add':return {'queuedSubmission':{'id':'q1'}}
                if method=='thread/queue/start':return {'turn':{'id':'own','status':'inProgress'}}
        mod=SimpleNamespace(RpcError=RuntimeError,submission_turn=lambda *a,**k:{'id':'own','status':'inProgress'})
        old={'turn_id':'previous-analysis','queued_id':'old-q'}
        self.assertEqual(dispatch.queue(Client(),mod,self.c,s,p,old,'synthetic')['turn_id'],'own')
        self.assertEqual(old['queued_id'],'q1')

    def test_start_response_lost_but_own_turn_readback_succeeds(self):
        _,s,p=self.begin()
        class Client:
            def rpc(_,method,params):
                if method=='thread/queue/add':return {'queuedSubmission':{'id':'q1'}}
                if method=='thread/queue/start':raise TimeoutError('lost response')
        mod=SimpleNamespace(RpcError=RuntimeError,submission_turn=lambda *a,**k:{'id':'own','status':'inProgress'})
        self.assertEqual(dispatch.queue(Client(),mod,self.c,s,p,{},'synthetic')['turn_id'],'own')

    def test_unresolved_identity_stays_uncertain_and_is_not_replayed(self):
        _,s,p=self.begin();calls=[]
        class Client:
            def rpc(_,method,params):
                calls.append(method)
                if method=='thread/queue/add':return {'queuedSubmission':{'id':'q1'}}
                if method=='thread/queue/start':raise RuntimeError('busy')
        with patch.object(dispatch,'await_own_turn',return_value=None):
            with self.assertRaisesRegex(ValueError,'turn-identity-unresolved'):
                dispatch.queue(Client(),SimpleNamespace(RpcError=RuntimeError),self.c,s,p,{},'synthetic')
        self.assertEqual(calls.count('thread/queue/add'),1)
        self.assertEqual(session.load(p['control']/'dispatch.json')['status'],'uncertain')

    def test_queue_add_response_lost_is_not_replayed(self):
        _,s,p=self.begin();count=[]
        class Client:
            def rpc(_,method,params):
                if method=='thread/queue/add':count.append(1);raise TimeoutError('disconnect')
        with self.assertRaises(TimeoutError):
            dispatch.queue(Client(),SimpleNamespace(RpcError=RuntimeError),self.c,s,p,{},'prompt')
        self.assertEqual(len(count),1)
        self.assertEqual(session.load(p['control']/'dispatch.json')['status'],'uncertain')

    def test_readback_timeout_is_bounded(self):
        mod=SimpleNamespace(submission_turn=lambda *a,**k:None)
        with patch.object(dispatch.time,'monotonic',side_effect=[0,31]):
            self.assertIsNone(dispatch.await_own_turn(None,mod,self.c,'own'))

    def test_only_standard_owner_mode_and_configured_model_are_accepted(self):
        self.assertEqual(dispatch.standard_settings(standard())['model'],'gpt-6.1-sol')
        for field,value in [('approvalPolicy','never'),('approvalsReviewer','user'),
                            ('activePermissionProfile',{'id':'any-custom'}),
                            ('sandbox',{'type':'dangerFullAccess'}),
                            ('model','other-model'),('collaborationMode',{'mode':'plan'})]:
            with self.subTest(field=field):
                with self.assertRaises(ValueError):dispatch.standard_settings({**standard(),field:value})

    def test_standard_settings_drift_blocks_without_mutation(self):
        class Client:
            def rpc(_,method,params):
                self.assertEqual(method,'thread/resume')
                return {**standard(),'cwd':'/changed'}
        with self.assertRaisesRegex(ValueError,'owner-settings-drift'):
            dispatch.verify_settings(Client(),self.c,self.digest)

    def test_native_probe_uses_builtin_workspace_and_no_private_reads(self):
        class Client:
            def rpc(_,method,params):
                self.assertEqual(method,'command/exec')
                self.assertEqual(params['command'],['/usr/bin/true'])
                self.assertEqual(params['permissionProfile'],':workspace')
                return {'exitCode':0}
        proof=dispatch.native_probe(Client(),standard())
        self.assertFalse(proof['model_started'])
        self.assertFalse(proof['os_manifest_read_isolation'])
        self.assertEqual(proof['settings_digest'],self.digest)

    def test_unavailable_native_tools_block_before_analysis(self):
        class Client:
            def rpc(self,*_):return {'exitCode':1}
        with self.assertRaisesRegex(ValueError,'native-tools-unavailable'):
            dispatch.native_probe(Client(),standard())

    def test_legacy_custom_profile_config_is_rejected(self):
        path=self.root/'legacy-controller.json'
        session.atomic(path,{'schema_version':1,'profile_id':'dreaming-chat'})
        with self.assertRaisesRegex(ValueError,'invalid-controller-config'):
            dispatch.controller_config(path,recovery=True)

    def test_cleanup_never_interrupts_an_unrelated_turn_or_mutates_settings(self):
        _,s,p=self.begin();calls=[]
        session.atomic(p['control']/'dispatch.json',{'status':'uncertain','client_id':'own',
                       'thread_id':self.c['thread_id']})
        class Client:
            def rpc(_,method,params):
                calls.append(method)
                if method=='thread/queue/list':return {'data':[]}
                raise AssertionError('unexpected mutation')
        mod=SimpleNamespace(submission_turn=lambda *a,**k:None)
        dispatch.cancel_owned(Client(),mod,self.c,self.cfg,p)
        self.assertEqual(calls,['thread/queue/list'])
        self.assertEqual(session.load(p['control']/'dispatch.json')['status'],'uncertain')

    def test_foreign_thread_cleanup_is_rejected(self):
        _,s,p=self.begin()
        session.atomic(p['control']/'dispatch.json',{'status':'running','thread_id':'other'})
        with self.assertRaisesRegex(ValueError,'controller-target-drift'):
            dispatch.cancel_owned(None,None,self.c,self.cfg,p)

    def test_failed_cleanup_waits_only_for_own_turn(self):
        _,s,p=self.begin();events=[]
        session.atomic(p['control']/'dispatch.json',{'status':'running','client_id':'own',
                       'turn_id':'own-turn','thread_id':self.c['thread_id']})
        class Client:
            def rpc(_,method,params):events.append((method,params));return {}
        mod=SimpleNamespace(submission_turn=lambda *a,**k:{'id':'own-turn','status':'inProgress'})
        with patch.object(dispatch.time,'monotonic',side_effect=[0,31]):
            with self.assertRaisesRegex(ValueError,'own-turn-still-active'):
                dispatch.cancel_owned(Client(),mod,self.c,self.cfg,p)
        self.assertEqual(events,[('turn/interrupt',{'threadId':self.c['thread_id'],'turnId':'own-turn'})])

    def test_busy_slot_expiry_never_starts_late(self):
        class Client:
            def rpc(self,*_):raise AssertionError('no RPC outside schedule')
        with patch.object(session,'clock',return_value=self.stamp+timedelta(hours=1)):
            self.assertFalse(dispatch.wait_idle(Client(),self.c,False))

    def test_prompt_preserves_manifest_and_private_proposal_boundaries(self):
        _,s,p=self.begin();prompt=dispatch.analysis_prompt(s,p)
        self.assertIn(str(p['drafts']/'checkpoint.json'),prompt)
        self.assertIn(str(p['report']/'dream-report.md'),prompt)
        self.assertIn('nie zmieniaj ustawień',prompt)
        self.assertIn('nie odczytuj oryginałów',prompt)
        self.assertNotIn('BEGIN DREAMING RENDER',prompt)

    def test_analysis_validation_precedes_verified_summary(self):
        _,s,p=self.begin();self.submit(s,p);events=[]
        class Client:
            def rpc(_,method,params):
                events.append(method)
                if method=='thread/queue/add':return {'queuedSubmission':{'id':'summary-q'}}
                if method=='thread/queue/start':return {'turn':{'id':'summary-t'}}
        def own(_client,pid,**kwargs):
            summary=pid.endswith(':summary')
            return {'id':'summary-t' if summary else 'analysis-t','status':'completed',
                    'items':[{'type':'agentMessage','phase':'final_answer',
                              'text':str(p['report']/'dream-report.md') if summary else 'pending verification'}]}
        d={'controller_config':'fixture','settings_digest':self.digest,
           'client_id':'analysis','turn_id':'analysis-t','phase':'analysis'}
        with patch.object(dispatch,'controller_config',return_value=(self.c,self.cfg)),\
             patch.object(dispatch,'verify_settings'),patch.object(session,'clock',return_value=self.stamp):
            result=dispatch.monitor(Client(),SimpleNamespace(RpcError=RuntimeError,submission_turn=own),
                                    self.c,self.cfg,s,p,d)
        self.assertEqual(result['status'],'completed')
        self.assertEqual(session.load(p['control']/'dispatch.json')['status'],'finalized')
        self.assertTrue((p['report']/'dream-report.md').exists())
        self.assertFalse(any(m.startswith(('config/','thread/settings/')) for m in events))

    def test_controller_change_cancels_before_accepting_checkpoint(self):
        _,s,p=self.begin();self.submit(s,p)
        with patch.object(dispatch,'controller_config',return_value=({**self.c,'thread_id':'changed'},self.cfg)),\
             patch.object(session,'clock',return_value=self.stamp):
            with self.assertRaisesRegex(ValueError,'controller-config-drift'):
                dispatch.monitor(None,None,self.c,self.cfg,s,p,{'controller_config':'fixture'})
        self.assertEqual(session.load(p['state'])['checkpoint_revision'],0)

    def test_controller_contains_no_settings_or_configuration_write_calls(self):
        tree=ast.parse(Path(dispatch.__file__).read_text())
        methods=[n.args[0].value for n in ast.walk(tree) if isinstance(n,ast.Call)
                 and isinstance(n.func,ast.Attribute) and n.func.attr=='rpc'
                 and n.args and isinstance(n.args[0],ast.Constant)]
        self.assertFalse(any(m.startswith(('config/','thread/settings/')) for m in methods))
        self.assertFalse(any(name in vars(dispatch) for name in ('install_profile','restore_settings','permissions')))

    def test_large_installed_runtime_is_hashable_but_linked_runtime_is_not(self):
        binary=self.root/'runtime.bin'
        with binary.open('wb') as stream:stream.truncate(270*1024*1024)
        with binary.open('rb') as stream:expected=hashlib.file_digest(stream,'sha256').hexdigest()
        self.assertEqual(dispatch.pinned_digest(binary),expected)
        link=self.root/'linked-runtime';link.symlink_to(binary)
        with self.assertRaises(OSError):dispatch.pinned_digest(link)


if __name__=='__main__':unittest.main()
