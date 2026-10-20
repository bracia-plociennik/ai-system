"""JSON command interface and fixed-owner discovery for a private source library."""
import argparse
from pathlib import Path
import json
import math
import sys

sys.dont_write_bytecode = True
from source_library import Library, safe, read_json

MUTATING = {'init', 'enable', 'disable', 'ingest', 'note', 'source-disable', 'source-enable', 'rebuild'}


def discover(cwd):
    # Registered System resolves ownership; no scan of arbitrary homes or memory.
    import agent_context
    context = agent_context.resolve_context(cwd, tool='codex')
    if context['binding_status'] != 'resolved' or context['context_kind'] not in ('management', 'repository', 'worktree', 'personal'):
        raise ValueError('not a resolved managed context')
    record, installed, _, env = agent_context.registration()
    rows, _ = agent_context.workspace_registry(installed, env)
    owners = [root for ident, root, _ in rows if ident == record['owner_workspace_id']]
    if len(owners) != 1:
        raise ValueError('registered personal owner unavailable')
    # Deliberately fixed relative to registered personal owner, never selected company.
    return safe(owners[0] / 'documents/library')


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['status', *sorted(MUTATING), 'search', 'read'])
    p.add_argument('--library', help='Explicit approved library root; required for init')
    p.add_argument('--cwd', type=Path, default=Path.cwd(), help='Actual managed working directory')
    p.add_argument('--approved', action='store_true', help='Caller verified actual action/root authority; flag is not consent')
    p.add_argument('--read-only', action='store_true')
    p.add_argument('--file', type=Path)
    p.add_argument('--source')
    p.add_argument('--version')
    p.add_argument('--pages', nargs='+', type=int)
    p.add_argument('--title')
    p.add_argument('--topics', nargs='+')
    p.add_argument('--query')
    p.add_argument('--limit', type=int, default=8)
    p.add_argument('--budget-seconds', type=float, default=30)
    p.add_argument('--all', action='store_true', help='Explicit foreground batch without automatic thirty-second cutline')
    p.add_argument('--retry-errors', action='store_true', help='Explicit retry after diagnosis; ordinary scans do not repeat errors')
    p.add_argument('--note-json', type=Path)
    a = p.parse_args(argv)
    try:
        if a.action in MUTATING and (a.read_only or not a.approved):
            raise ValueError('mutation requires current scoped approval and writable mode')
        if a.action == 'init' and not a.library:
            raise ValueError('init requires an explicit library root')
        root = safe(a.library) if a.library else discover(a.cwd)
        lib = Library(root)
        # Discovery does not activate cross-project access without installed policy.
        if not a.library and lib.path('settings.json').exists() and not lib.settings()['managed_use']:
            raise ValueError('managed library use disabled')
        if a.action == 'status':
            result = lib.status()
        elif a.action == 'init':
            result = lib.init()
        elif a.action in ('enable', 'disable'):
            result = lib.toggle(a.action == 'enable')
        elif a.action == 'ingest':
            result = lib.ingest(a.file, source_id=a.source, title=a.title, topics=a.topics,
                                budget=315360000 if a.all else a.budget_seconds, retry=a.retry_errors)
        elif a.action == 'search':
            result = lib.search(a.query, a.limit)
        elif a.action == 'read':
            result = lib.read(a.source, a.version, a.pages)
        elif a.action == 'note':
            if a.note_json is None:
                raise ValueError('--note-json required')
            result = lib.save_note(read_json(safe(a.note_json)))
        elif a.action in ('source-disable', 'source-enable'):
            result = lib.source_toggle(a.source, a.action == 'source-enable')
        else:
            result = lib.rebuild()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if a.action == 'ingest' and any(r.get('state') == 'error' for r in result['results']):
            return 1
        return 0
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as e:
        print(json.dumps({'state': 'error', 'reason': str(e)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
