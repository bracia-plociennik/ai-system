"""Optional explicit paired-source tests; standalone CI never implies pair support."""
import copy
import json
import os
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[3]
SOURCE=os.environ.get('ASA_WORKFLOW_SOURCE')

@unittest.skipUnless(SOURCE,'explicit paired Workflow source not selected; no pair-support claim')
class PairedLead(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow=Path(SOURCE)
        assert cls.workflow.is_absolute() and not cls.workflow.is_symlink()
        cls.module=runpy.run_path(str(cls.workflow/'.systems/scripts/lib/coordinator-status.py'))

    def test_shared_golden_scope_and_actor_parity(self):
        corpus=json.loads((ROOT/'.systems/scripts/tests/fixtures/work-lead-v1.json').read_text())
        self.assertEqual(corpus['contract'],'work-lead-v1')
        outcomes=[]
        for case in corpus['cases']:
            record=dict(work_lead=case['lead'],mandate_state='issued',valid_until=None,
                        context_binding='resolved',evidence_refs=[case['lead']['mandate_ref']])
            if case['shape']=='invalid':
                with self.subTest(case=case['name']), self.assertRaises(ValueError):
                    self.module['inspect_work_lead'](record,case['request'],case['target'],'phase-4-implementation')
            else:
                out=self.module['inspect_work_lead'](record,case['request'],case['target'],'phase-4-implementation')
                self.assertFalse(out['execution_authorized'])
                self.assertFalse(out['provenance_verified'])
                if case['actual_consent']=='out-of-scope':self.assertEqual(out['next_allowed_action'],'inspect')
                else:
                    self.assertEqual(out['scope_check'],'matched');outcomes.append(out)
        self.assertEqual(len(outcomes),2)
        self.assertEqual(outcomes[0],outcomes[1])

    def test_public_wrapper_schema3_cannot_promote_missing_quality(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);repo=root/'repo'
            subprocess.run(['git','init','-q',str(repo)],check=True)
            subprocess.run(['git','-C',str(repo),'-c','user.name=Synthetic','-c','user.email=test@example.invalid',
                            'commit','--allow-empty','-qm','fixture'],check=True)
            owner=root/'runtime/projects/synthetic';owner.mkdir(parents=True)
            (owner/'status.md').write_text('| `current-phase` | `phase-4-implementation` |\n')
            lead=copy.deepcopy(json.loads((ROOT/'.systems/scripts/tests/fixtures/work-lead-v1.json').read_text())['cases'][1]['lead'])
            lead['resource_roots']=[str(repo)]
            record=dict(work_lead=lead,mandate_state='issued',valid_until=None,context_binding='resolved',evidence_refs=['actual-request'])
            (owner/'lead.json').write_text(json.dumps(record))
            args=[str(self.workflow/'.systems/scripts/report-coordinator-status'),'--workflow',str(repo),
                  '--workspace',str(root/'runtime'),'--repo',str(repo),'--project','synthetic',
                  '--schema-version','3','--lead-record','lead.json','--resource',str(repo/'calc.py'),
                  '--requested-action','implementation','--requested-phase','phase-4-implementation']
            result=subprocess.run(args,capture_output=True,text=True)
            out=json.loads(result.stdout)
            self.assertEqual(result.returncode,1)
            self.assertEqual(out['schema_version'],3)
            self.assertEqual(out['scope_check'],'matched')
            self.assertEqual(out['actual_gate'],'unknown')
            self.assertFalse(out['execution_authorized'])
            self.assertEqual(out['authority_check'],'unknown')

if __name__=='__main__':unittest.main()
