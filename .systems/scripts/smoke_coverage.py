"""Source-bound smoke transaction ownership and assertion population."""
import hashlib
import json
import re
from pathlib import Path


def population(root):
    scripts = Path(root) / ".systems/scripts"
    text = (scripts / "check-validator-smoke-tests").read_text()
    starts = list(re.finditer(r'^if \[\[ "\$suite" == "all" \|\| "\$suite" == "([a-z-]+)" \]\]; then\n', text, re.M))
    if len(starts) != 7:
        raise ValueError("Missing smoke transaction ownership")
    suites = {}
    cases = json.loads((scripts / "smoke/negative-expectations.json").read_text())["cases"]
    for index, start in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else text.index('\npython3 -B "$repo_root/.systems/scripts/smoke_assertion.py"', start.end())
        body = text[start.end():end].rstrip()
        suites[start[1]] = {"body_sha256": hashlib.sha256(body.encode()).hexdigest(),
            "negative_ids": sorted(name for name, case in cases.items() if case["suite"] == start[1]),
            "ownership": "setup + mutations + helper/direct assertions + restoration; isolated temporary root cleanup"}
    tests = (scripts / "tests/test_validation_integrity.py").read_text()
    return {"contract": 1, "suites": suites,
            "integrity_test_body_sha256": hashlib.sha256(tests.encode()).hexdigest(),
            "integrity_tests": sorted(re.findall(r'^    def (test_[a-z0-9_]+)\(', tests, re.M)),
            "negative_causes": cases}
