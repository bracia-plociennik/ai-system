#!/usr/bin/env python3
import sys
from pathlib import Path
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import phase_x


class Maintenance(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.home=Path(self.temp.name)
        self.a=self.home/'a';self.b=self.home/'b';self.a.mkdir();self.b.mkdir()
        self.registry=self.home/'ai-system-workspaces.md'
        self.registry.write_text('| workspace-id | path | default | status | scope | notes |\n| a | a | yes | active | private | |\n| b | b | no | paused | company | |\n')
    def tearDown(self):self.temp.cleanup()
    def test_one_and_all_are_read_only(self):
        before=sorted(str(p) for p in self.home.rglob('*'))
        self.assertEqual(phase_x.targets(self.a),[str(self.a)])
        self.assertEqual(phase_x.targets(all_workspaces=True,system_home=self.home),[str(self.a),str(self.b)])
        self.assertEqual(before,sorted(str(p) for p in self.home.rglob('*')))
    def test_ambiguous_or_missing_selector(self):
        with self.assertRaises(ValueError):phase_x.targets()
        with self.assertRaises(ValueError):phase_x.targets(self.a,True,self.home)
        with self.assertRaises(ValueError):phase_x.targets(all_workspaces=True)
    def test_symlink_and_traversal_are_rejected(self):
        link=self.home/'linked';link.symlink_to(self.a,target_is_directory=True)
        with self.assertRaises(ValueError):phase_x.targets(link)
        self.registry.write_text('| a | ../a | yes | active | private | |')
        with self.assertRaises(ValueError):phase_x.targets(all_workspaces=True,system_home=self.home)
    def test_overlap_duplicate_and_missing_are_not_silently_skipped(self):
        self.registry.write_text('| a | a | yes | active | private | |\n| b | a | no | active | company | |')
        with self.assertRaises(ValueError):phase_x.targets(all_workspaces=True,system_home=self.home)
        self.registry.write_text('| a | missing | yes | active | private | |')
        with self.assertRaises(ValueError):phase_x.targets(all_workspaces=True,system_home=self.home)
    def test_missing_owner_does_not_hide_independent_targets(self):
        self.registry.write_text(self.registry.read_text()+'| absent | missing | no | active | company | |\n')
        findings=[]
        selected=phase_x.targets(all_workspaces=True,system_home=self.home,findings=findings)
        self.assertEqual(selected,[str(self.a),str(self.b)])
        self.assertEqual(findings[0]['state'],'blocked')

    def test_planned_is_not_created(self):
        self.registry.write_text(self.registry.read_text()+'| planned | absent | no | planned | company | |\n')
        self.assertEqual(len(phase_x.targets(all_workspaces=True,system_home=self.home)),2)
        self.assertFalse((self.home/'absent').exists())


if __name__=='__main__':unittest.main()
