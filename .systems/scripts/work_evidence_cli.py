"""Command dispatcher; mutating actions require explicit owner-approved flag."""
import argparse
import json
import sys
from pathlib import Path

from work_evidence import EvidenceError, file_hash, read_json, require, safe_path
from work_evidence_ledger import Ledger


def main(action=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--input")
    parser.add_argument("--transaction-id")
    parser.add_argument("--manifest-hash")
    parser.add_argument("--lock-hash")
    parser.add_argument("--owner-approved", action="store_true")
    parser.add_argument("--json", action="store_true", help="Output is always structured JSON")
    args = parser.parse_args()
    action = action or Path(sys.argv[0]).name.removeprefix("work-evidence-")
    try:
        ledger = Ledger(args.workspace)
        if action in {"prepare", "apply", "recover", "rebuild", "recover-lock"}:
            require(args.owner_approved, "owner-approval-required", "action")
        if action in {"preview", "prepare"}:
            require(args.input is not None, "input-required", "input")
            path = safe_path(ledger.workspace, args.input)
            expected = file_hash(path)
            candidate = read_json(path)
            result = (ledger.preview(candidate) if action == "preview"
                      else ledger.prepare(candidate, candidate_source=(path, expected)))
        elif action in {"apply", "recover"}:
            result = ledger.apply(args.transaction_id, args.manifest_hash)
        elif action == "rebuild":
            result = ledger.rebuild()
        elif action == "recover-lock":
            result = ledger.recover_lock(args.lock_hash)
        else:
            raise EvidenceError("unsupported-action", "action")
        print(json.dumps(result, ensure_ascii=False, allow_nan=False))
        return 0
    except (EvidenceError, OSError, TypeError, KeyError) as error:
        # Unvalidated source values and private paths must not escape diagnostics.
        category = error.category if isinstance(error, EvidenceError) else "invalid-or-unavailable-input"
        print(json.dumps({"status": "blocked", "category": category}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
