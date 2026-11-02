"""Synthetic new-task SPOR flow; no live store, events or owner data."""
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

S=Path(__file__).resolve().parents[1];sys.path.insert(0,str(S));sys.path.insert(0,str(S/'tests'))
import test_finalization_artifacts as fixture
import finalization_artifacts as product
from spor_new_tasks import prepare_task_request,new_tasks_readiness
from task_store import TaskStore


class NewTasks(unittest.TestCase):
    setUp=fixture.SporTests.setUp
    request=fixture.SporTests.request
    hooks=fixture.SporTests.hooks

    def setup_package(self,weekly=False):
        request=self.request(weekly)
        vault=self.ws/'tasks/vault';(vault/'tasks').mkdir(parents=True)
        (self.ws/'tasks/task-store.local.md').write_text('---\nschema_version: 1\nenabled: true\nprofile: silverbullet-v1\nvault_path: '+str(vault)+'\n---\n')
        key='future_plan_items_json' if weekly else 'planned_items_json'
        day=request['properties'].get('plan_week_start',request['date'])
        item={'id':'report','title':'Approved report','stream':'build','definition_of_done':'Owner checked result',
              'deadline':day+'T10:10','task_bucket':'do','mapping':{'scope':'workspace'}}
        request['properties'][key]=json.dumps([item]);request['confirmed_properties']=[key]
        return request,key,item

    def run_flow(self,weekly=False):
        request,key,item=self.setup_package(weekly)
        normalized,prepared=prepare_task_request(self.ws,request,['report'])
        calls=[];hooks=self.hooks(calls);store=TaskStore.load(self.ws);created=[]
        def tasks(path,h):
            calls.append('tasks');written,_=store.write_prepared(prepared['plan']);created.extend(written)
            return {'status':'verified','source_sha256':h}
        hooks['tasks']=tasks
        with patch.object(product,'publish',wraps=product.publish) as publish:
            result=product.finalize_spor(self.ws,normalized,apply=True,approved=True,integrations=('tasks','calendar'),hooks=hooks,
                preflights={'tasks':lambda c,h:new_tasks_readiness(self.ws,c,h,prepared),'calendar':self.preflight_calendar()})
        self.assertEqual(result['status'],'finalized');self.assertEqual(publish.call_count,1)
        self.assertEqual(calls,['indexes','renderer','tasks','calendar']);self.assertEqual(len(created),1)
        self.assertEqual(created[0].read_text(),prepared['plan']['entries'][0]['body'])
        self.assertIn('Owner checked result',created[0].read_text());self.assertIn('author: "ai"',created[0].read_text())
        self.assertIn(str(created[0].relative_to(self.ws)),(self.ws/result['path']).read_text())
        return result,normalized,prepared

    def preflight_calendar(self):
        def ready(candidate,h):
            p=self.ws/candidate['draft']['path']
            return {'status':'ready','candidate_sha256':h,'inputs':{str(p.relative_to(self.ws)):hashlib.sha256(p.read_bytes()).hexdigest()}}
        return ready

    def test_daily_single_write_and_single_task_calendar_stage(self):self.run_flow()
    def test_weekly_single_write_and_single_task_calendar_stage(self):self.run_flow(True)

    def test_preview_is_pure_and_manifest_binds_frozen_bytes(self):
        r,_,_=self.setup_package();before={str(p):p.read_bytes() for p in self.ws.rglob('*') if p.is_file()}
        normalized,prepared=prepare_task_request(self.ws,r,['report'])
        result=product.finalize_spor(self.ws,normalized,integrations=('tasks',),hooks=self.hooks([]),
            preflights={'tasks':lambda c,h:new_tasks_readiness(self.ws,c,h,prepared)})
        self.assertEqual(result['status'],'preview')
        self.assertEqual(before,{str(p):p.read_bytes() for p in self.ws.rglob('*') if p.is_file()})
        self.assertFalse((TaskStore.load(self.ws).root/'.ai-system-task-store.lock').exists())
        proof=result['preflight']['integrations']['tasks']['creation_manifest'][0]
        self.assertEqual(proof['after_sha256'],hashlib.sha256(prepared['plan']['entries'][0]['body'].encode()).hexdigest())

    def test_late_bad_item_and_sanitized_collision_create_nothing(self):
        r,key,item=self.setup_package();bad=copy.deepcopy(item);bad.update(id='second',title='Approved/report')
        first=copy.deepcopy(item);first['title']='Approved#report'
        r['properties'][key]=json.dumps([first,bad]);before=set(self.ws.rglob('*'))
        with self.assertRaisesRegex(ValueError,'batch-task-path-collision'):prepare_task_request(self.ws,r,['report','second'])
        self.assertEqual(before,set(self.ws.rglob('*')))
        bad.update(title='Second',deadline='invalid');r['properties'][key]=json.dumps([item,bad])
        with self.assertRaises((ValueError,SystemExit)):prepare_task_request(self.ws,r,['report','second'])
        self.assertEqual(before,set(self.ws.rglob('*')))

    def test_missing_mapping_unconfirmed_unknown_and_duplicate_selection(self):
        r,key,item=self.setup_package();r['confirmed_properties']=[]
        with self.assertRaisesRegex(ValueError,'confirmed'):prepare_task_request(self.ws,r,['report'])
        r['confirmed_properties']=[key];item.pop('mapping');r['properties'][key]=json.dumps([item])
        with self.assertRaisesRegex(ValueError,'mapping'):prepare_task_request(self.ws,r,['report'])
        for ids in (['missing'],['report','report']):
            with self.assertRaises(ValueError):prepare_task_request(self.ws,r,ids)

    def test_exact_identity_reuse_preserves_human_edits_and_closed_is_rejected(self):
        r,_,_=self.setup_package();_,first=prepare_task_request(self.ws,r,['report']);store=TaskStore.load(self.ws)
        written,_=store.write_prepared(first['plan']);p=written[0]
        p.write_text(p.read_text().replace('author: "ai"','author: "human"')+'\nManual note\n');before=p.read_bytes()
        _,again=prepare_task_request(self.ws,r,['report']);created,reused=store.write_prepared(again['plan'])
        self.assertEqual(created,[]);self.assertEqual(reused,[p]);self.assertEqual(p.read_bytes(),before)
        p.write_text(p.read_text().replace('status: "open"','status: "DONE"'))
        with self.assertRaisesRegex(ValueError,'closed-task'):prepare_task_request(self.ws,r,['report'])

    def test_unrelated_identity_target_collision_and_duplicate_source_are_rejected(self):
        r,_,_=self.setup_package();_,prepared=prepare_task_request(self.ws,r,['report']);store=TaskStore.load(self.ws)
        p=Path(prepared['plan']['entries'][0]['path']);p.parent.mkdir(parents=True);p.write_text('---\ntype: task\n---\nManual task')
        with self.assertRaisesRegex(ValueError,'path-collision'):prepare_task_request(self.ws,r,['report'])
        p.unlink();written,_=store.write_prepared(prepared['plan'])
        (store.task_dir/'duplicate.md').write_bytes(written[0].read_bytes())
        with self.assertRaisesRegex(ValueError,'ambiguous-task-source'):prepare_task_request(self.ws,r,['report'])

    def test_population_insertion_during_other_preflight_blocks_before_canonical(self):
        r,_,_=self.setup_package();normalized,prepared=prepare_task_request(self.ws,r,['report']);store=TaskStore.load(self.ws)
        def changed(c,h):
            (store.task_dir/'new.md').write_text('---\ntype: task\n---\nNew task')
            return self.preflight_calendar()(c,h)
        with patch.object(product,'publish',wraps=product.publish) as publish:
            with self.assertRaisesRegex(ValueError,'population changed'):product.finalize_spor(self.ws,normalized,apply=True,approved=True,
                integrations=('tasks','calendar'),hooks=self.hooks([]),preflights={'tasks':lambda c,h:new_tasks_readiness(self.ws,c,h,prepared),'calendar':changed})
        # publish may enter its guard, but must not create canonical or task.
        self.assertFalse((self.ws/'personal-ops/check-ins-v4').exists());self.assertFalse(Path(prepared['plan']['entries'][0]['path']).exists())

    def test_permissions_symlink_and_size_fail_before_creation(self):
        r,_,_=self.setup_package();store=TaskStore.load(self.ws)
        with patch('task_store.MAX_TASK',100),self.assertRaisesRegex(ValueError,'size-bound'):
            prepare_task_request(self.ws,r,['report'])
        with patch('task_store.os.access',return_value=False),self.assertRaisesRegex(ValueError,'not-writable'):
            prepare_task_request(self.ws,r,['report'])
        outside=self.ws/'outside';outside.mkdir();(store.task_dir/'bez-klienta').symlink_to(outside,target_is_directory=True)
        with self.assertRaisesRegex(ValueError,'unsafe-task-path'):prepare_task_request(self.ws,r,['report'])

    def test_plan_and_candidate_drift_rejected_before_write(self):
        r,_,_=self.setup_package();normalized,prepared=prepare_task_request(self.ws,r,['report']);store=TaskStore.load(self.ws)
        changed=copy.deepcopy(prepared['plan']);changed['entries'][0]['body']+='changed'
        with self.assertRaisesRegex(ValueError,'changed-task-create-plan'):store.write_prepared(changed)
        candidate=product.spor_candidate(self.ws,normalized);candidate['properties']['planned_items_json']='[]'
        with self.assertRaisesRegex(ValueError,'match final'):new_tasks_readiness(self.ws,candidate,'a'*64,prepared)

    def test_duplicate_source_inserted_during_commit_is_partial_and_never_erased(self):
        r,_,_=self.setup_package();normalized,prepared=prepare_task_request(self.ws,r,['report']);store=TaskStore.load(self.ws)
        hooks=self.hooks([]);real_link=os.link
        def raced_link(a,b,**kwargs):
            real_link(a,b,**kwargs)
            (store.task_dir/'racing-task.md').write_bytes(Path(b).read_bytes())
        def tasks(path,h):
            with patch('task_store.os.link',side_effect=raced_link):store.write_prepared(prepared['plan'])
            return {'status':'verified','source_sha256':h}
        hooks['tasks']=tasks
        result=product.finalize_spor(self.ws,normalized,apply=True,approved=True,integrations=('tasks',),hooks=hooks,
            preflights={'tasks':lambda c,h:new_tasks_readiness(self.ws,c,h,prepared)})
        self.assertEqual(result['status'],'partial');self.assertEqual(result['next_step'],'tasks')
        self.assertTrue((self.ws/result['path']).is_file());self.assertTrue((store.task_dir/'racing-task.md').is_file())
        entry=result['preflight']['integrations']['tasks']['creation_manifest'][0]
        self.assertEqual(hashlib.sha256((self.ws/entry['path']).read_bytes()).hexdigest(),entry['after_sha256'])


if __name__=='__main__':unittest.main()
