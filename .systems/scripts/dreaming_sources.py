"""Explicit opt-in registry validator. Inspection is metadata-only."""
from dreaming_guard import registry,inspect,GuardError
from dreaming_provider_v1 import parse_json,ProtocolError
import argparse,json,sys
from pathlib import Path

def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['inspect']);parser.add_argument('--request',required=True)
    args=parser.parse_args()
    try:
        path=Path(args.request)
        if path.stat().st_size>1048576:raise GuardError('oversized-request')
        value=parse_json(path.read_text());result,_=inspect(value)
        print(json.dumps(result,sort_keys=True));return 0
    except (OSError,ValueError,TypeError,KeyError):print(json.dumps({'error':'invalid-or-unavailable-scope'}),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
