import sys, json, unittest, copy, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dreaming_contracts as d

def specimen():
    return dict(schema_version=1,candidate_id=str(uuid.uuid4()),revision=1,predecessor_hash=None,
                owner_workspace_id="workspace-a",project_id="project-a",intent="new-case",case_ref=None,
                work_id=None,evidence_refs=[],facts=[],inferences=[],unknowns=[],
                consumer_readiness={x:dict(state="needs-evidence",missing_fields=["identity"],evidence_hashes=[]) for x in d.CONSUMERS},
                privacy_state="private",prior_decision_ref=None)

class Contracts(unittest.TestCase):
    def test_provider_roundtrip_and_drift(self):
        f=json.loads((Path(__file__).resolve().parents[2]/"ai/templates/dreaming/evidence/v1/provider-fixture.json").read_text())
        d.consume(f,f["capability"],f["capability"]["source_fingerprints"])
        self.assertEqual(f["evidence"][0]["native_state"],"promoted")
        with self.assertRaises(d.ProtocolError): d.consume(f,f["capability"],{})
    def test_candidate_unknown_and_authority(self):
        v=specimen();d.candidate(v);self.assertIsNone(v["work_id"])
        v["owner-approved"]=True
        with self.assertRaises(d.ProtocolError): d.candidate(v)
    def test_five_consumers_and_revision(self):
        v=specimen();v["consumer_readiness"].pop("ledger")
        with self.assertRaises(d.ProtocolError):d.candidate(v)
        v=specimen();v["revision"]=2
        with self.assertRaises(d.ProtocolError):d.candidate(v)
    def test_uncited_fact(self):
        v=specimen();v["facts"]=[dict(text="DONE",source_hashes=[],evidence_level="observed")]
        with self.assertRaises(d.ProtocolError):d.candidate(v)

if __name__ == "__main__":unittest.main()
