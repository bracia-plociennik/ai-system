#!/usr/bin/env python3
"""Synthetic missing-producer and contradictory-clause regression tests."""
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('critical_judgment',ROOT/'.systems/scripts/critical_judgment.py')
cj=importlib.util.module_from_spec(spec);spec.loader.exec_module(cj)
class CriticalJudgment(unittest.TestCase):
 def fixture(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);r=Path(t.name)
  for s in ['.systems/ai/core','.systems/ai/workflow','.systems/ai/templates/workflow','.systems/ai/templates/root']:
   p=ROOT/s
   if p.exists():shutil.copytree(p,r/s)
  if (ROOT/'AGENTS.md').exists():shutil.copyfile(ROOT/'AGENTS.md',r/'AGENTS.md')
  return r
 def test_real_product_mapping_is_structural_only(self):
  v=cj.inspect(ROOT);self.assertFalse(v['native_behavior_verified']);self.assertFalse(v['owner_approval_verified'])
 def test_missing_and_linked_required_source_reject(self):
  for kind in ['missing','link']:
   with self.subTest(kind=kind):
    r=self.fixture();p=r/'.systems/ai/core/task-intake.md';p.unlink()
    if kind=='link':p.symlink_to(ROOT/'.systems/ai/core/task-intake.md')
    with self.assertRaises((ValueError,OSError)):cj.inspect(r)
 def test_unreadable_source_rejects(self):
  with mock.patch.object(Path,"read_text",side_effect=PermissionError("synthetic unreadable source")):
   with self.assertRaises(PermissionError):cj.inspect(ROOT)
 def test_plain_prohibition_is_safe(self):
  for s in ['Do not always disagree.','Never always disagree.','Do not change the owner goal without approval.','Never fabricate objections.']:
   cj.contradictions(s)
 def test_unsafe_clause_cannot_hide_behind_prohibition(self):
  for sep in [' but ',' however ','. ',': ',' unless ',' yet ','; ']:
   with self.subTest(sep=sep):
    with self.assertRaises(ValueError):cj.contradictions('Do not always disagree'+sep+'Always disagree with the owner')
 def test_forbidden_authority_and_forced_ceremony(self):
  for s in ['The agent may change scope without approval.','Every answer must include an objection.','Skip required QA because the agent disagrees.']:
   with self.subTest(s=s):
    with self.assertRaises(ValueError):cj.contradictions(s)
 def test_missing_route_and_boundary_reject(self):
  r=self.fixture();p=r/'.systems/ai/core/response-contract.md';p.write_text(p.read_text().replace('critical-judgment.md','unrelated.md'))
  with self.assertRaises(ValueError):cj.inspect(r)
  r=self.fixture();p=r/'.systems/ai/core/critical-judgment.md';p.write_text(p.read_text().replace('verified fact, inference, risk hypothesis and preference','unsupported'))
  with self.assertRaises(ValueError):cj.inspect(r)
 def test_actual_template_fields_not_heading_only(self):
  if not (ROOT/'.systems/ai/core/repository-modes.md').exists():return
  r=self.fixture();p=r/'.systems/ai/templates/workflow/phase-1-architecture.template.md';s=p.read_text().replace('- What-if scenario:', '## What-if scenario');p.write_text(s)
  with self.assertRaises(ValueError):cj.inspect(r)
if __name__=='__main__':unittest.main()
