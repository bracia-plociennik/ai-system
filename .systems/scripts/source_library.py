"""Private source library: immutable originals, source-grounded notes, rebuildable search."""
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import sqlite3
import stat
import tempfile
import time
import uuid

from local_paths import resolve_path
from source_library_extract import MAX_BYTES, ExtractionError, count_pages, pdf_page, text_pages

SCHEMA = 1
SOURCE_ID = re.compile(r'src-[a-f0-9]{20}')
DIGEST = re.compile(r'[a-f0-9]{64}')
NOTE_ID = re.compile(r'note-[a-f0-9]{24}')
DEFAULTS = {'schema': 1, 'enabled': False, 'automatic_inbox': True,
            'managed_use': True, 'ocr_languages': ['pol', 'eng']}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    with safe(path).open('rb') as stream:
        result = hashlib.file_digest(stream, 'sha256').hexdigest()
    return result


def now():
    return datetime.now(timezone.utc).isoformat()


def safe(path):
    path = resolve_path(str(path))
    if path.exists() and not (path.is_file() or path.is_dir()):
        raise ValueError('special library path')
    return path


def read_json(path):
    def unique(pairs):
        result = {}
        for k, v in pairs:
            if k in result:
                raise ValueError('duplicate JSON field')
            result[k] = v
        return result
    return json.loads(safe(path).read_text(), object_pairs_hook=unique)


def atomic(path, data):
    path = safe(path)
    fd, name = tempfile.mkstemp(prefix='.library-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(name, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def write_json(path, value):
    atomic(path, (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode())


def normalize(text):
    return ' '.join(text.split())


def render_note(title, value):
    return (f"# {title}\n\nSource: {value['source']}\nVersion: {value['version']}\n"
            f"Anchors: {', '.join(value['locators'])}\nKind: {value['kind']}\n\n"
            + '\n\n'.join(f'## {label}\n{value[key]}' for label, key in
                             [('Source excerpt', 'excerpt'), ('Content', 'content'), ('Source context', 'context'),
                              ('Applies to', 'applies_to'), ('Agent inference', 'inference')]) + '\n')


class Library:
    def __init__(self, root):
        self.root = safe(root)
        self.source_issues = []

    def path(self, *parts):
        p = safe(self.root.joinpath(*parts))
        if not p.is_relative_to(self.root):
            raise ValueError('outside library')
        return p

    def settings(self):
        value = read_json(self.path('settings.json'))
        if set(value) != set(DEFAULTS) or value['schema'] != 1 or type(value['schema']) is not int:
            raise ValueError('unsupported library settings')
        if any(type(value[k]) is not bool for k in ('enabled', 'automatic_inbox', 'managed_use')):
            raise ValueError('invalid library policy')
        if value['ocr_languages'] != ['pol', 'eng']:
            raise ValueError('unsupported OCR languages')
        return value

    @contextmanager
    def locked(self, *, initializing=False):
        if not initializing:
            self.settings()
        lock = self.path('.write.lock')
        fd = os.open(lock, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            yield
        finally:
            os.close(fd)

    def init(self):
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        with self.locked(initializing=True):
            settings = self.path('settings.json')
            if settings.exists():
                self.settings()
                return {'state': 'existing', 'enabled': self.settings()['enabled']}
            allowed = {'inbox', 'sources', 'notes', 'scratch'}
            if any(p.name != '.write.lock' and (p.name not in allowed or not p.is_dir() or any(p.iterdir())) for p in self.root.iterdir()):
                raise ValueError('refusing initialization into populated directory')
            for d in ('inbox', 'sources', 'notes', 'scratch'):
                self.path(d).mkdir(mode=0o700, exist_ok=True)
            write_json(settings, DEFAULTS)
        return {'state': 'initialized', 'enabled': False}

    def toggle(self, enabled):
        with self.locked():
            value = self.settings()
            value['enabled'] = bool(enabled)
            write_json(self.path('settings.json'), value)
        return {'enabled': bool(enabled)}

    def source(self, ident):
        if not isinstance(ident, str) or not SOURCE_ID.fullmatch(ident):
            raise ValueError('unsafe source id')
        source = read_json(self.path('sources', ident, 'source.json'))
        if (set(source) != {'schema', 'id', 'title', 'topics', 'origin_name', 'enabled', 'current'}
                or source['schema'] != 1 or source['id'] != ident or type(source['enabled']) is not bool
                or not isinstance(source['current'], str) or not DIGEST.fullmatch(source['current'])):
            raise ValueError('invalid source metadata')
        if (not isinstance(source['title'], str) or not isinstance(source['origin_name'], str)
                or Path(source['origin_name']).name != source['origin_name']
                or source['origin_name'] in ('', '.', '..') or any(ord(c) < 32 for c in source['origin_name'])
                or not isinstance(source['topics'], list) or not all(isinstance(x, str) for x in source['topics'])):
            raise ValueError('invalid source description')
        return source

    def sources(self):
        result, self.source_issues = [], []
        for p in sorted(self.path('sources').iterdir()):
            try:
                if SOURCE_ID.fullmatch(p.name) and self.path('sources', p.name, 'source.json').exists():
                    result.append(self.source(p.name))
            except (ValueError, OSError, KeyError, TypeError) as e:
                self.source_issues.append({'source': p.name, 'reason': str(e)})
        return result

    def status(self):
        if not self.path('settings.json').exists():
            return {'state': 'not-configured', 'enabled': False}
        settings = self.settings()
        sources = self.sources()
        return {'state': 'configured', 'enabled': settings['enabled'],
                'automatic_inbox': settings['automatic_inbox'], 'managed_use': settings['managed_use'],
                'source_issues': self.source_issues, 'sources': len(sources), 'notes': len(list(self.path('notes').glob('note-*.json'))),
                'pending_inbox': len(list(self.path('inbox').iterdir())),
                'index_available': self.path('index.sqlite').is_file(),
                'tools': {n: bool(shutil.which(n)) for n in ('pdftotext', 'pdfinfo', 'pdftoppm', 'tesseract')}}

    def _revision(self, source, *, complete=False):
        directory = self.path('sources', source['id'], 'revisions', source['current'])
        rev = read_json(safe(directory / 'revision.json'))
        keys = {'schema', 'sha256', 'format', 'page_count', 'completed_pages', 'state', 'pages_sha256', 'error'}
        if (set(rev) != keys or rev['schema'] != 1 or rev['sha256'] != source['current']
                or rev['format'] not in ('.pdf', '.md', '.txt') or rev['state'] not in ('pending', 'partial', 'ready', 'needs-review', 'error')
                or type(rev['completed_pages']) is not int or rev['completed_pages'] < 0):
            raise ValueError('invalid source revision')
        original = safe(directory / ('original' + rev['format']))
        if file_hash(original) != source['current']:
            raise ValueError('source original changed')
        pages_path = safe(directory / 'pages.json')
        if file_hash(pages_path) != rev['pages_sha256']:
            raise ValueError('extracted pages changed')
        pages = read_json(pages_path)
        if not isinstance(pages, list) or len(pages) != rev['completed_pages']:
            raise ValueError('invalid extracted population')
        if complete and rev['state'] not in ('ready', 'needs-review'):
            raise ValueError('source extraction is incomplete')
        return rev, pages, original, directory

    def _save_pages(self, directory, rev, pages):
        write_json(safe(directory / 'pages.json'), pages)
        rev['completed_pages'] = len(pages)
        rev['pages_sha256'] = file_hash(directory / 'pages.json')
        write_json(safe(directory / 'revision.json'), rev)

    def _import(self, incoming, source_id, title, topics):
        incoming = safe(incoming)
        if (not incoming.is_file() or incoming.stat().st_size > MAX_BYTES
                or incoming.suffix.lower() not in ('.pdf', '.md', '.txt')):
            raise ValueError('unsupported input or size')
        if incoming.is_relative_to(self.root) and incoming.parent != self.path('inbox'):
            raise ValueError('import only external file or direct inbox member')
        fingerprint = file_hash(incoming)
        all_sources = self.sources()
        if source_id:
            source = self.source(source_id)
        else:
            # Bytes, not filename, establish deduplication. Inbox names select revisions only.
            matches = [s for s in all_sources if s['current'] == fingerprint]
            if not matches and incoming.parent == self.path('inbox'):
                matches = [s for s in all_sources if s['origin_name'] == incoming.name]
            if len(matches) > 1:
                raise ValueError('ambiguous revision; select source explicitly')
            source = matches[0] if matches else None
        if source is None:
            source = {'schema': 1, 'id': 'src-' + fingerprint[:20],
                      'title': title or incoming.stem, 'topics': topics or [],
                      'origin_name': incoming.name, 'enabled': True, 'current': fingerprint}
        if not source_id and source not in all_sources and self.path('sources', source['id'], 'source.json').exists():
            raise ValueError('existing source metadata needs explicit repair')
        directory = self.path('sources', source['id'], 'revisions', fingerprint)
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        ext = incoming.suffix.lower()
        if not (directory / 'revision.json').exists():
            original = safe(directory / ('original' + ext))
            # Copy to owned staging and verify a stable input before publishing.
            before = incoming.stat()
            fd, temp = tempfile.mkstemp(dir=directory, prefix='.original-')
            try:
                with os.fdopen(fd, 'wb') as out, incoming.open('rb') as inp:
                    shutil.copyfileobj(inp, out, 1024 * 1024)
                    out.flush()
                    os.fsync(out.fileno())
                after = incoming.stat()
                if ((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) !=
                        (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
                        or file_hash(temp) != fingerprint or file_hash(incoming) != fingerprint):
                    raise ValueError('input changed during copy')
                os.replace(temp, original)
            finally:
                if os.path.exists(temp):
                    os.unlink(temp)
            rev = {'schema': 1, 'sha256': fingerprint, 'format': ext, 'page_count': None,
                   'completed_pages': 0, 'state': 'pending', 'pages_sha256': '', 'error': None}
            self._save_pages(directory, rev, [])
        source['current'] = fingerprint
        if title is not None:
            source['title'] = title
        if topics is not None:
            source['topics'] = topics
        write_json(self.path('sources', source['id'], 'source.json'), source)
        # Inbox is retained through actual complete extraction, including crash recovery.
        return source, fingerprint

    def _extract(self, source, deadline):
        rev, pages, original, directory = self._revision(source)
        if rev['state'] in ('ready', 'needs-review'):
            return rev
        rev['error'] = None
        try:
            with tempfile.TemporaryDirectory(prefix='extract-', dir=self.path('scratch')) as scratch:
                if rev['format'] != '.pdf':
                    pages = text_pages(original)
                    rev['page_count'] = len(pages)
                    rev['state'] = 'ready' if any(p['text'].strip() for p in pages) else 'needs-review'
                    self._save_pages(directory, rev, pages)
                    return rev
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return rev
                if rev['page_count'] is None:
                    rev['page_count'] = count_pages(original, scratch, timeout=min(60, max(.1, remaining)))
                    self._save_pages(directory, rev, pages)
                while len(pages) < rev['page_count']:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        break
                    try:
                        page = pdf_page(original, len(pages) + 1, scratch, timeout=min(60, max(.1, remaining)))
                    except ExtractionError as e:
                        if time.monotonic() >= deadline:
                            break
                        raise e
                    pages.append(page)
                    rev['state'] = 'partial'
                    self._save_pages(directory, rev, pages)
                if len(pages) == rev['page_count']:
                    rev['state'] = 'needs-review' if any(p['method'] == 'ocr' or p['quality'] != 'extracted' for p in pages) else 'ready'
                else:
                    rev['state'] = 'partial'
        except (ExtractionError, UnicodeError, ValueError, OSError) as e:
            rev['state'], rev['error'] = 'error', str(e)
        self._save_pages(directory, rev, pages)
        return rev

    def ingest(self, file=None, *, source_id=None, title=None, topics=None, budget=30, retry=False):
        if not isinstance(budget, (int, float)) or not math.isfinite(budget) or budget <= 0:
            raise ValueError('invalid foreground budget')
        if source_id and file is None:
            raise ValueError('source update requires a file')
        deadline = time.monotonic() + budget
        results = []
        with self.locked():
            if not self.settings()['enabled']:
                raise ValueError('library disabled')
            inputs = [Path(file)] if file else sorted(self.path('inbox').iterdir())
            for incoming in inputs:
                if time.monotonic() >= deadline:
                    break
                try:
                    source, fingerprint = self._import(incoming, source_id, title, topics)
                    results.append({'source': source['id'], 'version': fingerprint, 'state': 'imported'})
                except (ValueError, OSError) as e:
                    results.append({'input': incoming.name, 'state': 'error', 'reason': str(e)})
            for source in self.sources():
                if time.monotonic() >= deadline:
                    break
                if not source['enabled']:
                    continue
                try:
                    rev, _, _, _ = self._revision(source)
                except (ValueError, OSError, KeyError, TypeError) as e:
                    results.append({'source': source['id'], 'state': 'error', 'reason': str(e)})
                    continue
                if rev['state'] == 'error' and not retry:
                    continue
                if file and not any(r.get('source') == source['id'] for r in results):
                    continue
                rev = self._extract(source, deadline)
                results.append({'source': source['id'], 'version': source['current'], 'state': rev['state'],
                                'completed_pages': rev['completed_pages'], 'page_count': rev['page_count'], 'error': rev['error']})
                if rev['state'] in ('ready', 'needs-review'):
                    incoming = self.path('inbox', source['origin_name'])
                    if incoming.parent == self.path('inbox') and incoming.is_file() and file_hash(incoming) == source['current']:
                        # Recheck the exact direct-inbox identity just before unlink.
                        before = incoming.stat()
                        if file_hash(incoming) == source['current'] and incoming.stat() == before:
                            incoming.unlink()
            self._rebuild()
        return {'results': results, 'pending_inbox': len(list(self.path('inbox').iterdir()))}

    def source_toggle(self, ident, enabled):
        with self.locked():
            source = self.source(ident)
            source['enabled'] = bool(enabled)
            write_json(self.path('sources', ident, 'source.json'), source)
            self._rebuild()
        return {'source': ident, 'enabled': bool(enabled)}

    def _note(self, path):
        value = read_json(path)
        keys = {'schema', 'id', 'source', 'version', 'pages', 'kind', 'excerpt', 'content', 'context',
                'applies_to', 'inference', 'scope', 'body_sha256', 'title', 'locators'}
        if set(value) != keys or value['schema'] != 1 or not NOTE_ID.fullmatch(value['id']):
            raise ValueError('invalid source note')
        body = self.path('notes', value['id'] + '.md')
        if (file_hash(body) != value['body_sha256']
                or sha(render_note(value['title'], value).encode()) != value['body_sha256']):
            raise ValueError('note body changed outside versioned update')
        return value

    def _selected(self, source, version, numbers):
        if not source['enabled'] or version != source['current']:
            raise ValueError('disabled or stale source version')
        if (not isinstance(numbers, list) or not numbers or len(set(numbers)) != len(numbers)
                or any(type(n) is not int or n < 1 for n in numbers)):
            raise ValueError('invalid page anchors')
        rev, pages, _, _ = self._revision(source, complete=True)
        if any(n > len(pages) for n in numbers):
            raise ValueError('missing source anchor')
        return [pages[n - 1] for n in numbers]

    def save_note(self, value):
        keys = {'source', 'version', 'pages', 'kind', 'excerpt', 'content', 'context', 'applies_to', 'inference', 'scope'}
        if (not isinstance(value, dict) or set(value) != keys or value['kind'] not in ('quote', 'paraphrase')
                or value['scope'] != 'general' or not DIGEST.fullmatch(value['version'])):
            raise ValueError('invalid note input or non-general scope')
        if any(not isinstance(value[k], str) or (k != 'inference' and not value[k].strip())
               or len(value[k]) > 20000 for k in ('excerpt', 'content', 'context', 'applies_to', 'inference')):
            raise ValueError('missing or oversized note field')
        with self.locked():
            if not self.settings()['enabled']:
                raise ValueError('library disabled')
            source = self.source(value['source'])
            pages = self._selected(source, value['version'], value['pages'])
            text = normalize('\n'.join(p['text'] for p in pages))
            if normalize(value['excerpt']) not in text:
                raise ValueError('excerpt is not grounded in selected source pages')
            if value['kind'] == 'quote' and normalize(value['content']) not in text:
                raise ValueError('quote is not literal source text')
            ident = 'note-' + sha((source['id'] + value['version'] + repr(sorted(value['pages']))
                                  + normalize(value['excerpt'])).encode())[:24]
            value = {**value, 'locators': [p['locator'] for p in pages]}
            body = render_note(source['title'], value)
            record = {'schema': 1, 'id': ident, **value, 'title': source['title'], 'body_sha256': sha(body.encode())}
            output = self.path('notes', ident + '.json')
            if output.exists():
                prior = read_json(output)
                expected = render_note(prior['title'], prior)
                if sha(expected.encode()) == prior.get('body_sha256') and self.path('notes', ident + '.md').read_bytes() != expected.encode():
                    # Recover a torn two-file publication from canonical JSON only during an approved write.
                    atomic(self.path('notes', ident + '.md'), expected.encode())
                old = self._note(output)
                if old == record:
                    return {'id': ident, 'state': 'unchanged'}
                archive = self.path('notes', 'history', ident)
                archive.mkdir(parents=True, exist_ok=True, mode=0o700)
                oldhash = file_hash(output)
                for suffix in ('.json', '.md'):
                    saved = safe(archive / (oldhash + suffix))
                    if not saved.exists():
                        atomic(saved, self.path('notes', ident + suffix).read_bytes())
            atomic(self.path('notes', ident + '.md'), body.encode())
            write_json(output, record)
            self._rebuild()
        return {'id': ident, 'state': 'saved'}

    def _entries(self):
        entries, issues = [], []
        sources = {}
        for source in self.sources():
            if not source['enabled']:
                continue
            try:
                _, pages, _, _ = self._revision(source, complete=True)
                sources[source['id']] = source
                for page in pages:
                    if not page['text'].strip():
                        continue
                    for offset in range(0, len(page['text']), 1800):
                        entries.append({'kind': 'source', 'id': f"{source['id']}:{page['page']}:{offset}",
                                        'source': source['id'], 'version': source['current'], 'pages': [page['page']],
                                        'text': page['text'][offset:offset + 2000], 'title': source['title'],
                                        'terms': ' '.join(source['topics']), 'quality': page['quality']})
            except (ValueError, OSError) as e:
                issues.append({'source': source['id'], 'reason': str(e)})
        issues.extend(self.source_issues)
        for path in sorted(self.path('notes').glob('note-*.json')):
            try:
                note = self._note(path)
                source = sources.get(note['source'])
                if source is None or source['current'] != note['version']:
                    continue
                self._selected(source, note['version'], note['pages'])
                entries.append({'kind': 'note', 'id': note['id'], 'source': source['id'],
                                'version': note['version'], 'pages': note['pages'], 'title': source['title'],
                                'terms': note['applies_to'], 'text': '\n'.join(note[k] for k in ('content', 'context', 'applies_to', 'inference')),
                                'quality': 'source-note', 'locators': note['locators'], 'note': {k: note[k] for k in ('kind', 'excerpt', 'content', 'context', 'applies_to', 'inference')}})
            except (ValueError, OSError) as e:
                issues.append({'note': path.stem, 'reason': str(e)})
        return entries, issues

    def _rebuild(self):
        entries, issues = self._entries()
        fd, temp = tempfile.mkstemp(dir=self.root, prefix='.index-')
        os.close(fd)
        try:
            connection = sqlite3.connect(temp)
            try:
                connection.execute('CREATE VIRTUAL TABLE entries USING fts5(text, title, terms, payload UNINDEXED)')
                connection.executemany('INSERT INTO entries VALUES (?,?,?,?)',
                                       [(e['text'], e['title'], e['terms'], json.dumps(e)) for e in entries])
                connection.execute('CREATE TABLE metadata (digest TEXT)')
                connection.execute('INSERT INTO metadata VALUES (?)', (sha(json.dumps(entries, sort_keys=True).encode()),))
                connection.commit()
            finally:
                connection.close()
            with open(temp, 'rb') as stream:
                os.fsync(stream.fileno())
            os.replace(temp, self.path('index.sqlite'))
        finally:
            if os.path.exists(temp):
                os.unlink(temp)
        return {'indexed_entries': len(entries), 'issues': issues}

    def rebuild(self):
        with self.locked():
            return self._rebuild()

    def search(self, query, limit=8):
        if not self.path('settings.json').exists() or not self.settings()['enabled']:
            return {'results': [], 'reason': 'library not configured or disabled'}
        if not isinstance(query, str) or not query.strip() or len(query) > 2000 or not 1 <= limit <= 50:
            raise ValueError('invalid search query or result limit')
        words = re.findall(r'[^\W_]+', query.lower(), re.UNICODE)[:32]
        note_results, note_issues = [], []
        checked = {}
        for path in sorted(self.path('notes').glob('note-*.json')):
            try:
                note = self._note(path)
                text = '\n'.join(note[k] for k in ('content', 'context', 'applies_to', 'inference'))
                if not any(w in (text + ' ' + note['title']).lower() for w in words):
                    continue
                source = self.source(note['source'])
                if not source['enabled'] or source['current'] != note['version']:
                    continue
                key = (source['id'], source['current'])
                if key not in checked:
                    # Verify bytes and page-manifest hash without parsing the whole PDF or its full text.
                    directory = self.path('sources', source['id'], 'revisions', source['current'])
                    rev = read_json(directory / 'revision.json')
                    original = safe(directory / ('original' + rev['format']))
                    if (rev['state'] not in ('ready', 'needs-review') or file_hash(original) != note['version']
                            or file_hash(directory / 'pages.json') != rev['pages_sha256']):
                        raise ValueError('source inputs changed or incomplete')
                    checked[key] = True
                note_results.append({'kind': 'note', 'id': note['id'], 'source': source['id'],
                                     'version': source['current'], 'pages': note['pages'], 'title': source['title'],
                                     'text': text, 'quality': 'source-note', 'locators': note['locators'],
                                     'note': {k: note[k] for k in ('kind', 'excerpt', 'content', 'context', 'applies_to', 'inference')}})
            except (ValueError, OSError, KeyError, TypeError) as e:
                note_issues.append({'note': path.stem, 'reason': str(e)})
        if note_results:
            return {'results': note_results[:limit], 'issues': note_issues, 'retrieval': 'source-notes',
                    'knowledge_role': 'advisory source data'}
        # Revalidate canonical inputs before trusting a derived index; pure fallback never rebuilds it.
        entries, issues = self._entries()
        lookup = {e['id']: e for e in entries}
        words = re.findall(r'[^\W_]+', query.lower(), re.UNICODE)[:32]
        if not words:
            return {'results': [], 'issues': issues}
        index = self.path('index.sqlite')
        rows = []
        if index.exists():
            connection = None
            try:
                connection = sqlite3.connect(index.as_uri() + '?mode=ro&immutable=1', uri=True)
                expected = sha(json.dumps(entries, sort_keys=True).encode())
                if connection.execute('SELECT digest FROM metadata').fetchone() == (expected,):
                    match = ' OR '.join('"' + word.replace('"', '""') + '"' for word in words)
                    rows = [json.loads(row[0]) for row in connection.execute(
                        'SELECT payload FROM entries WHERE entries MATCH ? ORDER BY rank LIMIT ?', (match, limit * 8))]
            except (sqlite3.Error, ValueError, TypeError):
                rows = []
            finally:
                if connection is not None:
                    connection.close()
        if not rows:
            rows = [e for e in entries if any(w in (e['text'] + ' ' + e['title'] + ' ' + e['terms']).lower() for w in words)]
        # Canonical payload wins over stored index values, including tampered ones.
        results = [lookup[e['id']] for e in rows if isinstance(e, dict) and e.get('id') in lookup]
        results.sort(key=lambda e: e['kind'] != 'note')
        return {'results': results[:limit], 'issues': issues, 'knowledge_role': 'advisory source data'}

    def read(self, ident, version, numbers):
        if not self.settings()['enabled']:
            raise ValueError('library disabled')
        source = self.source(ident)
        pages = self._selected(source, version, numbers)
        return {'source': ident, 'title': source['title'], 'version': version, 'pages': pages,
                'original': str(self._revision(source)[2]), 'knowledge_role': 'advisory source data'}
