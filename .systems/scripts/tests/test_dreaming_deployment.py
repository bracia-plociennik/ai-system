import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dreaming_config_draft import draft
from dreaming_deployment import render


class Deployment(unittest.TestCase):
    def test_render_schedule_and_bounds_without_activating(self):
        files=render('/opt/owner-system','/opt/private-owner/config.json')
        timer=files['dreaming-universal.timer'];service=files['dreaming-universal.service']
        self.assertIn('Thu,Sat *-*-* 02:00:00 Europe/Warsaw',timer)
        self.assertIn('Persistent=false',timer)
        self.assertIn('TimeoutStartSec=7200',service)
        self.assertIn('KillMode=control-group',service)
        self.assertIn('Restart=no',service)
        self.assertNotIn('@SYSTEM_HOME@',service)
        self.assertNotIn('propozycje-spor',service+timer)
    def test_unit_path_injection_rejected(self):
        for value in ('/opt/a\nExecStart=/bin/true','/opt/%h','relative','/opt/../elsewhere','/opt/with space'):
            with self.assertRaises(ValueError):render(value,'/opt/config.json')
    def test_manifest_tasks_use_metadata_and_current_owner_namespace(self):
        with tempfile.TemporaryDirectory() as td:
            home=Path(td);owner=home/'owner';company=home/'company';system=home/'system';workflow=home/'workflow'
            for p in (owner,company,system,workflow):p.mkdir()
            (system/'.systems').mkdir();(workflow/'.systems').mkdir()
            (owner/'personal-ops/check-ins-v4').mkdir(parents=True)
            (company/'clients/client-a').mkdir(parents=True)
            tasks=owner/'tasks/TaskNotes/Tasks';tasks.mkdir(parents=True)
            (tasks/'misleading-personal-name.md').write_text('---\nworkspace: owner\nowner_scope: client\nclient: client-a\n---\nTask')
            (tasks/'misleading-company-name.md').write_text('No owner metadata.')
            value,gaps=draft(home,('owner',owner),('company',company),system,workflow,'fixture','/usr/bin/true','fixture','owner:approved')
            selected=[s for s in value['sources'] if 'misleading-personal-name' in s['prefix']]
            self.assertEqual(selected[0]['owner'],'company')
            self.assertEqual(selected[0]['ownership_fields']['client'],'client-a')
            self.assertEqual(gaps['task_gap_count'],1)
            self.assertTrue(any('check-ins-v4' in s['prefix'] for s in value['sources']))
            self.assertNotIn('model_data_authority',value)
    def test_ambiguous_entity_does_not_guess_task_owner(self):
        with tempfile.TemporaryDirectory() as td:
            home=Path(td);owner=home/'owner';company=home/'company';system=home/'system';workflow=home/'workflow'
            for p in (owner,company,system,workflow):p.mkdir()
            for p in (owner,company):(p/'clients/same').mkdir(parents=True)
            (company/'status.md').write_text('Company fixture status.')
            tasks=owner/'tasks/TaskNotes/Tasks';tasks.mkdir(parents=True)
            (tasks/'task.md').write_text('---\nworkspace: owner\nowner_scope: client\nclient: same\n---\nTask')
            value,gaps=draft(home,('owner',owner),('company',company),system,workflow,'fixture','/usr/bin/true','fixture','owner:approved')
            self.assertEqual(gaps['task_gap_count'],1)
            self.assertFalse(any(s['prefix'].endswith('task.md') for s in value['sources']))

if __name__=='__main__':unittest.main()
