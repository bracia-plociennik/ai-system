"""Create one anonymous saved workbook for visual QA only."""
import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True
root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(root / ".systems/scripts"))
sys.path.insert(0, str(root / ".systems/scripts/tests"))
import test_work_evidence_xlsx as tests

test = tests.XlsxTests()
test.setUp()
try:
    test.add()
    test.apply()
    destination = Path(__file__).with_name("sample-tracker.xlsx")
    shutil.copyfile(test.tracker.path, destination)
    print(destination.name)
finally:
    test.doCleanups()
