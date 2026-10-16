"""Explicit v2 sources. Metadata enumeration does not authorize a body read."""
import os
import re
import stat
from pathlib import Path, PurePosixPath
from dreaming_guard import read_file, open_root, hash_bytes
from dreaming_universal_evidence import need, slug, digest, LENSES

DENY = {'.git', 'node_modules', '.venv', 'vendor', '__pycache__', '.cache', '.obsidian',
        'dist', 'build', 'coverage', 'target', 'dreams', 'credentials', 'secrets',
        'humans', 'scheduler', 'logs', 'archive', 'backups'}
TEXT = {'.md', '.txt', '.json', '.jsonl', '.py', '.js', '.ts', '.tsx', '.jsx', '.php',
        '.css', '.html', '.sh', '.yaml', '.yml', '.toml'}
CREDENTIAL = re.compile(rb'(?i)(?:-----BEGIN [A-Z ]*PRIVATE KEY|\b(?:sk-[a-z0-9_-]{16,}|gh[pousr]_[a-z0-9]{16,})|\b(?:api[_-]?key|password|access[_-]?token|client[_-]?secret)\s*[:=]\s*[\x22\x27]?[a-z0-9_+/.-]{8,})')
CHUNK_BYTES = 16384
MAX_FILE = 1048576


def relative(path):
    need(isinstance(path, str) and path and not PurePosixPath(path).is_absolute() and
         '\\' not in path and '\0' not in path and
         all(p not in ('', '.', '..') for p in path.split('/')), 'unsafe-path')
    return path


def config(value):
    required = {'schema_version', 'authority_ref', 'report_owner', 'workspace', 'analyzer', 'sources', 'recipients', 'decisions'}
    need(isinstance(value, dict) and required <= set(value) <= required | {'scope_gaps', 'model_data_authority'}, 'invalid-config')
    need(isinstance(value.get('scope_gaps', {}), dict), 'invalid-scope-gaps')
    if 'model_data_authority' in value:
        authority = value['model_data_authority']
        need(isinstance(authority, dict) and set(authority) == {'provider', 'scope', 'authority_ref'} and authority['provider'] == 'openai-codex' and authority['scope'] in ('one-off', 'recurring') and isinstance(authority['authority_ref'], str) and authority['authority_ref'], 'invalid-model-data-authority')
    need(type(value['schema_version']) is int and value['schema_version'] == 2, 'unsupported-config')
    need(isinstance(value['authority_ref'], str) and value['authority_ref'], 'missing-authority')
    slug(value['report_owner'])
    path = Path(value['workspace']); need(path.is_absolute(), 'invalid-workspace')
    fd = open_root(str(path)); os.close(fd)
    analyzer = value['analyzer']
    need(isinstance(analyzer, dict) and set(analyzer) == {'model', 'version', 'cli_version', 'cli_sha256', 'executable'}, 'invalid-analyzer')
    for x in analyzer.values(): need(isinstance(x, str) and x, 'unpinned-analyzer')
    need(re.fullmatch('[0-9a-f]{64}', analyzer['cli_sha256']), 'unpinned-cli')
    need(Path(analyzer['executable']).is_absolute(), 'invalid-executable'); slug(analyzer['version'])
    need(isinstance(value['recipients'], dict) and value['report_owner'] in value['recipients'], 'missing-owner-recipient')
    for key, recipient in value['recipients'].items():
        slug(key)
        need(isinstance(recipient, dict) and set(recipient) == {'lenses', 'adapter'} and
             recipient['adapter'] in ('owner-report', 'proposal', 'wep') and
             isinstance(recipient['lenses'], list) and recipient['lenses'] and
             set(recipient['lenses']) <= set(LENSES), 'invalid-recipient')
        need((key == value['report_owner']) == (recipient['adapter'] == 'owner-report'), 'invalid-owner-adapter')
    need(isinstance(value['decisions'], list), 'invalid-decisions')
    need(isinstance(value['sources'], list) and value['sources'], 'missing-sources')
    seen = set(); scopes = []
    for source in value['sources']:
        required = {'id', 'root', 'prefix', 'owner', 'subject_type', 'subject_id', 'source_class', 'audiences', 'sharing_authority'}
        need(isinstance(source, dict) and required <= set(source) <= required | {'ownership_fields', 'ownership_json', 'native_owner_id'}, 'invalid-source')
        if 'ownership_fields' in source:
            need(isinstance(source['ownership_fields'], dict) and source['ownership_fields'] and all(isinstance(k, str) and isinstance(v, str) for k,v in source['ownership_fields'].items()), 'invalid-ownership-fields')
        if 'native_owner_id' in source:
            slug(source['native_owner_id'])
            need(source['owner'] == value['report_owner'] and source['root'] == value['workspace'] and source['native_owner_id'] == Path(value['workspace']).name and source.get('ownership_json', {}).get('owner_workspace') == source['native_owner_id'], 'unbound-native-owner-alias')
        if 'ownership_json' in source:
            need(isinstance(source['ownership_json'], dict) and source['ownership_json'] and all(isinstance(k, str) and isinstance(v, (str, int)) for k,v in source['ownership_json'].items()), 'invalid-ownership-json')
        for field in ('id', 'owner', 'subject_id'): slug(source[field])
        need(source['id'] not in seen, 'duplicate-source'); seen.add(source['id']); relative(source['prefix'])
        need(source['subject_type'] in ('person', 'brand', 'company', 'project', 'system'), 'invalid-subject')
        need(source['source_class'] in ('work', 'source', 'personal'), 'invalid-source-class')
        need(isinstance(source['audiences'], list) and source['audiences'] and
             set(source['audiences']) <= set(value['recipients']) and
             value['report_owner'] in source['audiences'], 'invalid-audiences')
        root = Path(source['root']); need(root.is_absolute(), 'invalid-root')
        need(not any(p.is_symlink() for p in (root, *root.parents)), 'linked-root')
        need(root == root.resolve(), 'noncanonical-root')
        target = root / source['prefix']
        for p in (target, *target.parents):
            if p == root.parent: break
            need(not p.is_symlink(), 'linked-scope')
        for prior in scopes:
            need(target != prior and target not in prior.parents and prior not in target.parents, 'overlapping-scope')
            if target.exists() and prior.exists(): need(not os.path.samefile(target, prior), 'aliased-scope')
        scopes.append(target)
        if source['owner'] != value['report_owner']:
            need(isinstance(source['sharing_authority'], str) and source['sharing_authority'], 'unshared-owner')
        if source['source_class'] == 'personal':
            need(source['owner'] == value['report_owner'] and
                 set(source['audiences']) == {value['report_owner']}, 'personal-audience')
    return value


def classify(source, path):
    parts = tuple(p.casefold() for p in PurePosixPath(path).parts); name = parts[-1]
    if any(p in DENY or 'ocr' in p or p.endswith('.assets') for p in parts): return 'excluded'
    if 'dump' in parts and 'incoming' in parts: return 'excluded'
    if name == '.env' or name.startswith('.env.') or PurePosixPath(name).suffix in ('.pem', '.key', '.p12', '.pfx'): return 'excluded'
    if 'personal-ops' in parts and source['source_class'] != 'personal': return 'excluded'
    if source['source_class'] != 'personal' and any(p in ('health', 'finance', 'financial', 'private-finance', 'budget', 'medical') for p in parts): return 'excluded'
    suffix = PurePosixPath(name).suffix
    eligible = suffix in TEXT or (source['source_class'] == 'source' and suffix in ('', '.mjs', '.service', '.timer', '.template'))
    return 'pending' if eligible else 'unsupported'


def inventory(value, check=lambda: None):
    """Explicit sources only. Walk uses no symlink traversal; read rechecks dirfds."""
    result = []
    for source in value['sources']:
        root = Path(source['root']); target = root / source['prefix']; check()
        if not target.exists():
            result.append({'source_id': source['id'], 'path': source['prefix'], 'state': 'missing'}); continue
        paths = [target] if target.is_file() or target.is_symlink() else None
        def walked():
            def onerror(_): raise ValueError('inventory-unavailable')
            for directory, dirs, files in os.walk(target, followlinks=False, onerror=onerror):
                check()
                blocked = [d for d in dirs if (Path(directory)/d).is_symlink() or
                           classify(source, (Path(directory)/d/'placeholder.md').relative_to(root).as_posix()) == 'excluded']
                for d in blocked:
                    dirs.remove(d); yield Path(directory)/d
                for f in files: yield Path(directory)/f
        for path in paths if paths is not None else walked():
            check(); rel = path.relative_to(root).as_posix(); state = classify(source, rel); info = path.lstat()
            if stat.S_ISLNK(info.st_mode) or (stat.S_ISREG(info.st_mode) and info.st_nlink != 1): state = 'excluded'
            elif not stat.S_ISREG(info.st_mode): state = 'excluded'
            elif info.st_size > MAX_FILE: state = 'unsupported'
            result.append({'source_id': source['id'], 'path': rel, 'state': state,
                           'size': info.st_size, 'mtime_ns': info.st_mtime_ns})
            need(len(result) <= 200000, 'inventory-limit')
    return sorted(result, key=lambda r: (r['source_id'], r['path']))


def read(source, row):
    relative(row['path'])
    need(row['path'] == source['prefix'] or row['path'].startswith(source['prefix']+'/'), 'out-of-scope-source')
    need(row['state'] == 'pending' and row['source_id'] == source['id'] and
         classify(source, row['path']) == 'pending', 'forbidden-source')
    data = read_file(source['root'], row['path'], MAX_FILE, prescreen=False)
    need(not CREDENTIAL.search(data), 'credential-marker')
    try: data.decode('utf-8')
    except UnicodeDecodeError: raise ValueError('unsupported-encoding') from None
    if 'ownership_json' in source:
        from dreaming_provider_v1 import parse_json
        doc = parse_json(data.decode('utf-8'))
        need(isinstance(doc, dict) and all(doc.get(k) == v for k,v in source['ownership_json'].items()), 'native-ownership-drift')
    if 'ownership_fields' in source:
        fields = frontmatter(data.decode('utf-8'))
        need(all(fields.get(k, '') == v for k, v in source['ownership_fields'].items()), 'task-ownership-drift')
    return data


def frontmatter(text):
    if not text.startswith('---\n'): return {}
    end = text.find('\n---', 4)
    if end < 0 or end > 16384: return {}
    result = {}
    for line in text[4:end].splitlines():
        match = re.fullmatch(r'([a-z_]+):[ \t]*(.*)', line)
        if match:
            key, value = match.groups()
            need(key not in result, 'duplicate-task-field')
            result[key] = value.strip().strip('\"\'')
    return result


def chunks(source, row, data):
    result = []; start = 0; fingerprint = hash_bytes(data)
    ref = {'source_id': source['id'], 'path': row['path'], 'owner': source['owner'],
           'subject_type': source['subject_type'], 'subject_id': source['subject_id'],
           'source_class': source['source_class'], 'audiences': source['audiences'],
           'sha256': fingerprint, 'byte_count': len(data)}
    if 'native_owner_id' in source: ref['native_owner_id'] = source['native_owner_id']
    while start < len(data) or not result:
        end = min(len(data), start + CHUNK_BYTES)
        while end > start:
            try: text = data[start:end].decode('utf-8'); break
            except UnicodeDecodeError: end -= 1
        if end == start: text = ''
        result.append({'chunk_id': digest([ref, start, end]), 'ref': ref, 'start': start, 'end': end,
                       'sha256': hash_bytes(data[start:end]), 'text': text})
        start = end
        if not data: break
    return result
