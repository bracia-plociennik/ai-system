import copy
import hashlib
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dreaming_cycle as cycle
import dreaming_universal_sources as sources
from dreaming_universal_evidence import findings, route, digest, response_schema
from dreaming_analyzer import CodexAnalyzer, namespace_args, bounded_process


class Analyzer:
    def __init__(self, callback=None): self.calls = []; self.callback = callback; self.preflighted = False
    def preflight(self): self.preflighted = True
    def __call__(self, chunks, context, timeout):
        assert self.preflighted
        self.calls.append(copy.deepcopy(chunks))
        if self.callback: return self.callback(chunks, context, timeout)
        ref = chunks[0].get('ref', chunks[0].get('refs', [{}])[0])
        return {'findings': [{'topic': 'regular-learning', 'lens': 'person' if ref['source_class'] == 'personal' else 'systems',
            'kind': 'keep', 'summary': 'Widać regularne uczenie się.', 'facts': ['Zapisano pracę nad materiałem.'],
            'inferences': ['Może pomagać w realizacji celów.'], 'unknowns': ['Nie znamy efektu.'],
            'actions': ['Kontynuować i mierzyć rezultat.'], 'evidence_ids': [c['chunk_id'] for c in chunks]}]}


class Universal(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.workspace = self.root/'owner-home'; self.workspace.mkdir()
        (self.root/'personal').mkdir(); (self.root/'product').mkdir()
        (self.root/'personal/day.md').write_text('sleep_hours: 7\ncalories: 2100\nRefleksja: uczę się codziennie.\n')
        (self.root/'product/readme.md').write_text('A reusable procedure was documented.\n')
        self.cfg = {'schema_version': 2, 'authority_ref': 'owner-approved:test', 'report_owner': 'owner',
            'workspace': str(self.workspace), 'analyzer': {'model': 'fixture', 'version': 'v2',
                'cli_version': 'fixture', 'cli_sha256': '0'*64, 'executable': '/usr/bin/true'},
            'sources': [self.source('personal', 'personal', ['owner']), self.source('product', 'source', ['owner', 'system', 'wep'])],
            'recipients': {'owner': {'lenses': ['person', 'brand', 'company', 'systems'], 'adapter': 'owner-report'},
                'system': {'lenses': ['systems'], 'adapter': 'proposal'}, 'wep': {'lenses': ['systems'], 'adapter': 'wep'}},
            'decisions': []}
        self.stamp = datetime(2026, 10, 15, 2, 0, tzinfo=ZoneInfo('Europe/Warsaw'))
    def source(self, name, cls, audiences):
        return {'id': name, 'root': str(self.root), 'prefix': name, 'owner': 'owner',
                'subject_type': 'person' if cls == 'personal' else 'project', 'subject_id': name,
                'source_class': cls, 'audiences': audiences, 'sharing_authority': ''}
    def run_cycle(self, analyzer=None, stamp=None, **kw):
        return cycle.run(self.cfg, analyzer=analyzer or Analyzer(), stamp=stamp or self.stamp, **kw)
    def artifacts(self, completion):
        root = self.workspace/'dreams/runs'/completion['run_id']
        return {p.stem: json.loads(p.read_text()) for p in root.glob('*.json')}
    def test_personal_and_work_many_consumers_no_source_writes(self):
        baseline = {p: p.read_bytes() for p in self.root.glob('*/*.md')}
        a = Analyzer(); c = self.run_cycle(a); out = self.artifacts(c)
        self.assertEqual(c['result'], 'complete')
        self.assertEqual(out['report']['coverage']['reviewed'], 2)
        for rid in ('system', 'wep'):
            self.assertTrue(out['packets'][rid]['findings'])
            self.assertTrue(all(f['privacy'] != 'personal' for f in out['packets'][rid]['findings']))
            self.assertNotIn('sleep_hours', json.dumps(out['packets'][rid]))
        self.assertEqual({p: p.read_bytes() for p in baseline}, baseline)
        self.assertEqual(len([c for c in a.calls if 'ref' in c[0]]), 2)
    def test_owner_synthesis_context_cannot_taint_technical_packet(self):
        rows = sources.inventory(self.cfg)
        cs = [c for row in rows for c in sources.chunks(next(s for s in self.cfg['sources'] if s['id'] == row['source_id']), row,
              sources.read(next(s for s in self.cfg['sources'] if s['id'] == row['source_id']), row))]
        work = next(c for c in cs if c['ref']['source_class'] == 'source')
        raw = Analyzer()(cs, [], 1) if False else {'findings': [{'topic': 'x', 'lens': 'systems', 'kind': 'improve',
            'summary': 'Private context must not leave.', 'facts': [], 'inferences': ['Example'], 'unknowns': [],
            'actions': [], 'evidence_ids': [work['chunk_id']]}]}
        f = findings(raw, cs, 'owner')[0]
        self.assertEqual(f['privacy'], 'personal'); self.assertEqual(f['audiences'], ['owner'])
    def test_unchanged_sources_reuse_analysis_but_new_synthesis(self):
        self.run_cycle(); a = Analyzer()
        c = self.run_cycle(a, datetime(2026, 10, 17, 2, 0, tzinfo=self.stamp.tzinfo))
        self.assertEqual(c['result'], 'complete')
        self.assertFalse(any('ref' in batch[0] for batch in a.calls))

    def test_repeated_work_topic_in_private_synthesis_preserves_context(self):
        from dreaming_verify import verify

        def response(chunks, context, timeout):
            # Cite only work evidence, even when synthesis sees private context.
            work = [c for c in chunks if c.get('ref', c.get('refs', [{}])[0])['source_class'] != 'personal']
            chosen = work or chunks
            raw = Analyzer()
            raw.preflight()
            return raw(chosen, context, timeout)

        completion = self.run_cycle(Analyzer(response))
        out = self.artifacts(completion)
        self.assertTrue(verify(str(self.workspace), completion['run_id'])['bundle_verified'])
        self.assertEqual(completion['result'], 'complete')
        merged = next(f for f in out['report']['findings'] if f['lens'] == 'systems')
        self.assertEqual(merged['audiences'], ['owner'])
        self.assertEqual(merged['privacy'], 'personal')
        self.assertEqual({r['source_class'] for r in merged['context_refs']}, {'personal', 'source'})
        self.assertFalse(out['packets']['system']['findings'])
        self.assertFalse(out['packets']['wep']['findings'])
        records = [r for r in out.values() if isinstance(r, dict) and r.get('kind') in ('analysis', 'synthesis')]
        items = [f for r in records for f in r['findings']]
        for ordered in (items, list(reversed(items)), items + items):
            finding = next(f for f in cycle.merge_findings(ordered) if f['lens'] == 'systems')
            self.assertEqual({digest(r) for r in finding['context_refs']}, {digest(r) for r in merged['context_refs']})
            self.assertEqual(finding['audiences'], ['owner'])
            self.assertEqual(finding['privacy'], 'personal')
    def test_same_size_same_mtime_edit_invalidates_reuse(self):
        self.run_cycle(); path = self.root/'product/readme.md'; before = path.stat()
        data = path.read_bytes(); path.write_bytes(data.replace(b'reusable', b'repeated')); os.utime(path, ns=(before.st_atime_ns,before.st_mtime_ns))
        a = Analyzer(); self.run_cycle(a, datetime(2026, 10, 17, 2, 0, tzinfo=self.stamp.tzinfo))
        self.assertTrue(any('ref' in batch[0] for batch in a.calls))
    def test_source_change_during_analysis_not_reviewed(self):
        def cb(cs, context, timeout):
            (self.root/'product/readme.md').write_text('changed')
            return {'findings': []}
        c = self.run_cycle(Analyzer(cb)); out = self.artifacts(c)
        self.assertNotEqual(c['result'], 'complete')
        self.assertEqual(next(r['state'] for r in out['inventory'] if r['source_id'] == 'product'), 'pending')
    def test_credentials_blocked_personal_fields_allowed(self):
        (self.root/'personal/secret.md').write_text('password: supersecret123\n')
        c = self.run_cycle(); out = self.artifacts(c)
        self.assertEqual(out['report']['coverage']['blocked'], 1)
        self.assertEqual(out['report']['coverage']['reviewed'], 2)
    def test_denied_sources_not_opened(self):
        (self.root/'product/.env').write_text('private')
        (self.root/'product/cache.assets').mkdir(); (self.root/'product/cache.assets/ocr.md').write_text('private')
        (self.root/'product/link.md').symlink_to(self.root/'personal/day.md')
        rows = sources.inventory(self.cfg)
        for row in rows:
            if row['state'] == 'excluded':
                with self.assertRaises(ValueError), patch.object(sources, 'read_file', side_effect=AssertionError('body read')):
                    sources.read(self.cfg['sources'][1], row)
    def test_personal_recipient_policy_cannot_be_broadened(self):
        self.cfg['sources'][0]['audiences'].append('system')
        with self.assertRaisesRegex(ValueError, 'personal-audience'): sources.config(self.cfg)
    def test_overlap_missing_source_unsupported(self):
        self.cfg['sources'].append({**self.cfg['sources'][1], 'id': 'alias'})
        with self.assertRaisesRegex(ValueError, 'overlapping-scope'): sources.config(self.cfg)
        self.cfg['sources'].pop()
        (self.root/'product/binary.pdf').write_bytes(b'pdf')
        self.cfg['sources'].append({**self.source('missing', 'work', ['owner']), 'prefix': 'not-there'})
        c = self.run_cycle(); out = self.artifacts(c)
        self.assertEqual(out['report']['coverage']['missing'], 1); self.assertEqual(out['report']['coverage']['unsupported'], 1)
    def test_invalid_model_response_not_reviewed_and_other_scope_continues(self):
        def cb(cs, context, timeout):
            if cs[0].get('ref', {}).get('source_class') == 'personal': return {'findings': [{'invented': True}]}
            return {'findings': []}
        c = self.run_cycle(Analyzer(cb)); out = self.artifacts(c)
        self.assertNotEqual(c['result'], 'complete'); self.assertEqual(out['report']['coverage']['reviewed'], 1)
    def test_model_unavailable_retried_once(self):
        def cb(*_): raise ValueError('analyzer-unavailable')
        a = Analyzer(cb); c = self.run_cycle(a)
        self.assertEqual(c['result'], 'blocked'); self.assertEqual(len(a.calls), 4) # two isolated scopes
    def test_whole_cycle_lock_and_idempotent_slot(self):
        with cycle.cycle_lock(self.workspace):
            with self.assertRaisesRegex(ValueError, 'cycle-already-running'): self.run_cycle()
        c = self.run_cycle(); a = Analyzer(); self.assertEqual(c, self.run_cycle(a)); self.assertEqual(a.calls, [])
    def test_rejected_decision_stays_per_recipient(self):
        c = self.run_cycle(); packets = self.artifacts(c)['packets']; fid = packets['system']['findings'][0]['finding_id']
        self.cfg['decisions'] = [{'finding_id': fid, 'recipient': 'system', 'state': 'rejected', 'authority_ref': 'owner:test'}]
        c = self.run_cycle(stamp=datetime(2026, 10, 17, 2, 0, tzinfo=self.stamp.tzinfo)); packets = self.artifacts(c)['packets']
        self.assertFalse(packets['system']['findings']); self.assertTrue(packets['wep']['findings'])
        self.cfg['decisions'] = []
        c = self.run_cycle(stamp=datetime(2026, 10, 22, 2, 0, tzinfo=self.stamp.tzinfo)); packets = self.artifacts(c)['packets']
        self.assertFalse(packets['system']['findings'])
    def test_preflight_failure_before_private_read(self):
        a = Analyzer(); a.preflight = lambda: (_ for _ in ()).throw(ValueError('isolation-unavailable'))
        with patch.object(cycle, 'read', side_effect=AssertionError('private read')):
            c = self.run_cycle(a)
        self.assertEqual(c['result'], 'blocked'); self.assertEqual(a.calls, [])
    def test_chunking_utf8_and_no_1000_file_ceiling_for_history(self):
        data = ('ą'*20000).encode(); source = self.cfg['sources'][0]
        row = {'source_id': source['id'], 'path': 'personal/a.md', 'state': 'pending'}
        cs = sources.chunks(source, row, data)
        self.assertEqual(''.join(c['text'] for c in cs).encode(), data)
        for i in range(1005): (self.root/'product'/f'{i}.md').write_text('x')
        self.assertEqual(len(sources.inventory(self.cfg)), 1007)
    def test_timeout_is_partial_and_next_cycle_can_continue(self):
        ticks = [0]
        def clock(): return ticks[0]
        a = Analyzer(lambda *_: (ticks.__setitem__(0, 6901), {'findings': []})[1])
        c = self.run_cycle(a, clock=clock)
        self.assertEqual(c['result'], 'partial')
        out = self.artifacts(c); self.assertGreater(out['report']['coverage']['pending'], 0)
        c = self.run_cycle(stamp=datetime(2026, 10, 17, 2, 0, tzinfo=self.stamp.tzinfo))
        self.assertEqual(c['result'], 'complete')
    def test_slots_timezone_dst_and_no_daytime_catchup(self):
        z = ZoneInfo('Europe/Warsaw')
        for stamp in (datetime(2026, 7, 2, 2, tzinfo=z), datetime(2026, 12, 3, 2, tzinfo=z)):
            self.assertIsNotNone(cycle.slot(stamp)); self.assertIsNotNone(cycle.slot(stamp.astimezone(ZoneInfo('UTC'))))
        self.assertIsNone(cycle.slot(datetime(2026, 10, 15, 4, tzinfo=z)))
        self.assertIsNone(cycle.slot(datetime(2026, 10, 16, 2, tzinfo=z)))
        self.assertEqual(cycle.run(self.cfg, Analyzer(), datetime(2026, 10, 15, 9, tzinfo=z))['result'], 'skipped')
    def test_namespace_does_not_mount_workspace_home_or_host_config(self):
        args = namespace_args()
        self.assertNotIn(str(Path.home()), args); self.assertNotIn(str(self.workspace), args)
        self.assertIn('--clearenv', args); self.assertNotIn('--ro-bind / /', ' '.join(args))
    def test_subprocess_timeout_and_safe_error(self):
        import subprocess
        with self.assertRaises(subprocess.TimeoutExpired): bounded_process([sys.executable, '-c', 'import time;time.sleep(5)'], '', .05)
        self.assertEqual(cycle.error_code(OSError('/private/name')), 'operation-unavailable')
    def test_contract_schema_and_uncited_findings(self):
        self.assertEqual(response_schema()['additionalProperties'], False)
        cs = sources.chunks(self.cfg['sources'][0], {'path': 'personal/day.md'}, b'hello')
        a = Analyzer(); a.preflight(); response = a(cs, [], 10)
        response['findings'][0]['evidence_ids'] = ['invented']
        with self.assertRaisesRegex(ValueError, 'uncited-finding'): findings(response, cs, 'owner')

    def test_historical_pages_preserve_progress_across_many_cycles(self):
        # Time expires after a few accepted batches: the next cycle must advance,
        # retaining older verified analysis rather than oscillating between pages.
        self.cfg['sources'] = [self.cfg['sources'][1]]
        for i in range(18):
            (self.root/'product'/f'page-{i:02d}.md').write_text('x'*20000)
        seen = set(); histories = []
        for date in (15,17,22,24,29,31):
            tick = [0]
            def cb(batch, context, timeout):
                tick[0] += 1500
                if tick[0] < 6900:
                    for c in batch:
                        if 'ref' in c:
                            self.assertNotIn(c['chunk_id'], seen)
                            seen.add(c['chunk_id'])
                return {'findings': []}
            c = self.run_cycle(Analyzer(cb), datetime(2026,10,date,2,tzinfo=self.stamp.tzinfo), clock=lambda:tick[0])
            histories.append(self.artifacts(c)['report']['history_reviewed'])
        self.assertEqual(histories[-1],19)
        self.assertEqual(histories,sorted(histories))
        self.assertEqual(len(seen),37)
    def test_changed_policy_never_reuses_prior_receipts(self):
        self.run_cycle(); self.cfg['authority_ref']='owner:new-scope'; a=Analyzer()
        self.run_cycle(a,datetime(2026,10,17,2,tzinfo=self.stamp.tzinfo))
        self.assertTrue(any('ref' in batch[0] for batch in a.calls))
    def test_crash_after_checkpoint_recovers_only_next_slot(self):
        with patch.object(cycle,'markdown',side_effect=RuntimeError('simulated crash')):
            with self.assertRaises(RuntimeError):self.run_cycle()
        with self.assertRaisesRegex(ValueError,'interrupted-slot-next-cycle-required'):self.run_cycle()
        a=Analyzer();c=self.run_cycle(a,datetime(2026,10,17,2,tzinfo=self.stamp.tzinfo))
        self.assertEqual(c['result'],'complete')
        self.assertFalse(any('ref' in batch[0] for batch in a.calls))
    def test_completed_report_tamper_rejected(self):
        c=self.run_cycle();p=self.workspace/'dreams/runs'/c['run_id']/'report.json'
        p.write_text('{}')
        with self.assertRaisesRegex(ValueError,'completed-artifact-drift'):self.run_cycle()
    def test_ownership_change_in_task_metadata_blocks_read(self):
        path=self.root/'product/task.md';path.write_text('---\nworkspace: owner\nproject: one\n---\nTask')
        src={**self.cfg['sources'][1],'ownership_fields':{'workspace':'owner','project':'one'}}
        row={'source_id':'product','path':'product/task.md','state':'pending'}
        self.assertTrue(sources.read(src,row))
        path.write_text('---\nworkspace: company\nproject: one\n---\nTask')
        with self.assertRaisesRegex(ValueError,'task-ownership-drift'):sources.read(src,row)
    def test_native_wep_identity_from_json_and_markdown_without_time_inference(self):
        import uuid
        work=str(uuid.uuid4());entry=str(uuid.uuid4())
        doc={'schema_version':1,'entry_id':entry,'work_id':work,'revision':1,'owner_workspace':'owner',
             'project_id':'product','duration':{'actual_seconds':123},'source_refs':[],'status':'committed'}
        (self.root/'product/entry.json').write_text(json.dumps(doc))
        c=self.run_cycle();p=self.artifacts(c)['packets']['wep']['wep_candidates']
        self.assertEqual(len(p),1);self.assertEqual(p[0]['work_id'],work)
        self.assertEqual(p[0]['intent'],'enrich-case')
        self.assertIn('confirmed-time',p[0]['consumer_readiness']['ledger']['missing_fields'])
    def test_source_symlink_root_and_hardlink_blocked(self):
        (self.root/'alias').symlink_to(self.root/'product',target_is_directory=True)
        self.cfg['sources'][1]['root']=str(self.root/'alias')
        with self.assertRaisesRegex(ValueError,'linked-root'):sources.config(self.cfg)
        self.cfg['sources'][1]['root']=str(self.root)
        os.link(self.root/'product/readme.md',self.root/'product/hard.md')
        self.assertTrue(all(r['state']=='excluded' for r in sources.inventory(self.cfg) if r['source_id']=='product'))
    def test_analyzer_rejects_execution_events_and_accepts_nonfatal_item_errors(self):
        import dreaming_analyzer as module
        spec={**self.cfg['analyzer'],'cli_sha256':hashlib.sha256(Path('/usr/bin/true').read_bytes()).hexdigest()}
        a=CodexAnalyzer(spec);a.ready=True
        events=[{'type':'item.completed','item':{'type':'error','message':'startup warning'}},
                {'type':'item.completed','item':{'type':'agent_message','text':'{"findings":[]}'}},
                {'type':'turn.completed'}]
        with patch.object(module,'bounded_process',return_value='\n'.join(json.dumps(e) for e in events)):
            self.assertEqual(a([],[],1),{'findings':[]})
        events.insert(0,{'type':'item.started','item':{'type':'command_execution'}})
        with patch.object(module,'bounded_process',return_value='\n'.join(json.dumps(e) for e in events)):
            with self.assertRaisesRegex(ValueError,'unexpected-analyzer-tool'):a([],[],1)

    def test_analyzer_selects_readonly_profile_with_credential_read_denials(self):
        import tomllib
        import dreaming_analyzer as module
        spec={**self.cfg['analyzer'],'cli_sha256':hashlib.sha256(Path('/usr/bin/true').read_bytes()).hexdigest()}
        analyzer=CodexAnalyzer(spec, self.root/'synthetic-auth.json');analyzer.ready=True
        events=[{'type':'item.completed','item':{'type':'agent_message','text':'{"findings":[]}'}},
                {'type':'turn.completed'}]
        with patch.object(module,'bounded_process',return_value='\n'.join(json.dumps(e) for e in events)) as execute:
            self.assertEqual(analyzer([],[],1),{'findings':[]})
        command=execute.call_args.args[0]
        config=tomllib.loads('\n'.join(command[i+1] for i,value in enumerate(command) if value=='-c'))
        self.assertEqual(config['default_permissions'],'dreaming')
        profile=config['permissions']['dreaming']
        self.assertEqual(profile['extends'],':read-only')
        self.assertEqual(profile['filesystem'],{'/private':'deny','/proc':'deny','/runner':'deny',':workspace_roots':'deny'})
        self.assertIs(profile['network']['enabled'],False)
        self.assertNotIn('--sandbox',command)
        self.assertNotIn('sandbox_mode',config)
        self.assertIn('--ignore-user-config',command)
        self.assertIn('--strict-config',command)
        disabled={command[i+1] for i,value in enumerate(command) if value=='--disable'}
        self.assertTrue({'shell_tool','apps','plugins','hooks','multi_agent','code_mode_host'} <= disabled)
    def test_cycle_config_rejects_raw_private_broadened_recipients(self):
        self.cfg['sources'][0]['owner']='other-owner'
        self.cfg['sources'][0]['sharing_authority']='owner:says-yes'
        with self.assertRaisesRegex(ValueError,'personal-audience'):sources.config(self.cfg)

    def test_external_payload_authority_is_separate_from_local_read_approval(self):
        backend=CodexAnalyzer(self.cfg['analyzer'])
        with patch.object(backend,'preflight'), patch.object(cycle,'read',side_effect=AssertionError('private read')):
            c=self.run_cycle(backend)
        self.assertEqual(c['result'],'blocked')
        self.assertIn('model-data-authority-required',self.artifacts(c)['report']['errors'])
    def test_one_off_payload_approval_does_not_enable_recurring_cycle(self):
        self.cfg['model_data_authority']={'provider':'openai-codex','scope':'one-off','authority_ref':'owner:one-pilot'}
        backend=CodexAnalyzer(self.cfg['analyzer'])
        with patch.object(backend,'preflight'), patch.object(cycle,'read',side_effect=AssertionError('private read')):
            c=self.run_cycle(backend)
        self.assertEqual(c['result'],'blocked')

    def test_universal_bundle_and_legacy_workspace_checker_interoperate(self):
        import subprocess
        from dreaming_verify import verify
        c=self.run_cycle()
        self.assertTrue(verify(self.workspace,c['run_id'])['bundle_verified'])
        script=Path(cycle.__file__).parent/'check-dreaming-mode'
        result=subprocess.run([str(script),'--workspace',str(self.workspace)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
    def test_report_state_drift_cannot_downgrade_to_legacy(self):
        from dreaming_verify import verify
        c=self.run_cycle();p=self.workspace/'dreams/runs'/c['run_id']/'state.json'
        state=json.loads(p.read_text());state['config']['sources'][0]['audiences'].append('system');p.write_text(json.dumps(state))
        with self.assertRaisesRegex(ValueError,'completed-state-drift'):verify(self.workspace,c['run_id'])

    def test_real_native_workspace_alias_preserved_without_changing_generic_owner(self):
        import uuid
        work=str(uuid.uuid4());entry=str(uuid.uuid4());native=self.workspace.name
        (self.workspace/'work-log').mkdir()
        doc={'schema_version':1,'entry_id':entry,'work_id':work,'revision':1,'owner_workspace':native,
             'project_id':'product','duration':{},'source_refs':[],'status':'committed'}
        (self.workspace/'work-log/entry.json').write_text(json.dumps(doc))
        self.cfg['sources']=[{'id':'native-log','root':str(self.workspace),'prefix':'work-log/entry.json',
            'owner':'owner','subject_type':'project','subject_id':'product','source_class':'work',
            'audiences':['owner','wep'],'sharing_authority':'','native_owner_id':native,
            'ownership_json':{'owner_workspace':native,'work_id':work}}]
        c=self.run_cycle();packets=self.artifacts(c)['packets']
        self.assertEqual(packets['wep']['findings'][0]['owners'],['owner'])
        self.assertEqual(packets['wep']['wep_candidates'][0]['owner_workspace_id'],native)
        self.assertEqual(packets['wep']['wep_candidates'][0]['work_id'],work)
        from dreaming_verify import verify
        self.assertTrue(verify(self.workspace,c['run_id'])['bundle_verified'])
    def test_native_owner_alias_requires_local_namespace_and_identity_proof(self):
        self.cfg['sources'][1]['native_owner_id']='someone-else'
        with self.assertRaisesRegex(ValueError,'unbound-native-owner-alias'):sources.config(self.cfg)

    def test_source_reader_rejects_forged_row_outside_registered_prefix(self):
        row={'state':'pending','source_id':'product','path':'personal/day.md'}
        with patch.object(sources,'read_file',side_effect=AssertionError('body opened')):
            with self.assertRaisesRegex(ValueError,'out-of-scope-source'):sources.read(self.cfg['sources'][1],row)
    def test_implemented_decision_requires_current_registered_quality_evidence(self):
        c=self.run_cycle(); fid=self.artifacts(c)['packets']['system']['findings'][0]['finding_id']
        decision={'finding_id':fid,'recipient':'system','state':'implemented','authority_ref':'owner:completed'}
        self.cfg['decisions']=[decision]
        with self.assertRaisesRegex(ValueError,'implemented-needs-quality-evidence'):
            self.run_cycle(stamp=datetime(2026,10,17,2,tzinfo=self.stamp.tzinfo))
        p=self.root/'product/readme.md'
        decision['quality_evidence']={'source_id':'product','path':'product/readme.md','sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
        c=self.run_cycle(stamp=datetime(2026,10,17,2,tzinfo=self.stamp.tzinfo))
        self.assertEqual(c['result'],'complete')
        decision['quality_evidence']['sha256']='0'*64
        c=self.run_cycle(stamp=datetime(2026,10,22,2,tzinfo=self.stamp.tzinfo))
        self.assertEqual(c['result'],'blocked')

if __name__ == '__main__': unittest.main()
