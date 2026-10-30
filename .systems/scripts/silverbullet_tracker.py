"""Owner-scoped task timer. Operational state is separate from committed WEP."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import os
from pathlib import Path
import sqlite3
import uuid
from zoneinfo import ZoneInfo

from task_store import TaskStore, frontmatter, safe_path as task_path
from work_evidence import (EvidenceError, canonical_bytes, digest, file_hash,
                           read_json, validate_registry)
from work_evidence_ledger import Ledger, atomic_write
from work_evidence_xlsx import Tracker as Workbook

ZONE = ZoneInfo('Europe/Warsaw')
NAMESPACE = uuid.UUID('f24f8042-0839-4b44-90a4-0aaec42481ec')
ACTIONS = {'start', 'pause', 'resume', 'stop', 'complete', 'reopen', 'resolve', 'discard'}


class TrackerError(ValueError):
    def __init__(self, code, status=409):
        self.code, self.status = code, status
        super().__init__(code)


def require(value, code, status=409):
    if not value:
        raise TrackerError(code, status)


def uid(value):
    try:
        require(isinstance(value, str) and str(uuid.UUID(value)) == value, 'invalid-id', 400)
    except (ValueError, AttributeError):
        raise TrackerError('invalid-id', 400) from None
    return value


def moment(value):
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
        require(result.utcoffset() is not None, 'timestamp-needs-offset', 400)
        return result.astimezone(timezone.utc)
    except (ValueError, TypeError, AttributeError):
        raise TrackerError('invalid-timestamp', 400) from None


def stamp(value):
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def split_interval(start, end):
    start, end = moment(start).replace(microsecond=0), moment(end).replace(microsecond=0)
    require(end >= start, 'clock-review-required')
    require(end - start <= timedelta(days=366), 'clock-review-required')
    result = []
    while True:
        day = start.astimezone(ZONE).date()
        boundary = datetime.combine(day + timedelta(days=1), datetime.min.time(), ZONE).astimezone(timezone.utc)
        until = min(end, boundary)
        result.append({'day': day.isoformat(), 'start': stamp(start), 'end': stamp(until),
                       'seconds': int((until - start).total_seconds())})
        if until == end:
            return result
        start = until


class TaskTracker:
    def __init__(self, workspace, *, clock=None, evidence_level='production-readback'):
        self.workspace = Path(workspace).resolve(strict=True)
        self.store = TaskStore.load(self.workspace)
        require(self.store.profile == 'silverbullet-v1', 'silverbullet-store-required')
        self.home = self.workspace / 'work-evidence/silverbullet-tracker'
        task_path(self.workspace, self.home)
        self.home.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.evidence_level = evidence_level
        require(evidence_level in {'production-readback', 'local-test'}, 'invalid-evidence-level', 400)
        self.path = self.home / 'state.sqlite3'
        require(not self.path.is_symlink(), 'unsafe-state-path')
        with self.db() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY,path TEXT NOT NULL,work_id TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY,task_id TEXT NOT NULL,state TEXT NOT NULL,
                    review INTEGER NOT NULL DEFAULT 0,status TEXT NOT NULL DEFAULT 'partial',
                    correction TEXT,created TEXT NOT NULL,receipt TEXT);
                CREATE UNIQUE INDEX IF NOT EXISTS one_active ON runs((1)) WHERE state='active';
                CREATE TABLE IF NOT EXISTS segments(id TEXT PRIMARY KEY,run_id TEXT NOT NULL,
                    start TEXT NOT NULL,end TEXT,basis TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY,run_id TEXT,task_id TEXT NOT NULL,
                    intent_hash TEXT NOT NULL,payload TEXT NOT NULL,result TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS approvals(id TEXT PRIMARY KEY,run_id TEXT NOT NULL,
                    body TEXT NOT NULL,hash TEXT NOT NULL,state TEXT NOT NULL,receipt TEXT);
            ''')
            db.execute("INSERT OR IGNORE INTO meta VALUES('version','0')")
            db.execute("INSERT OR IGNORE INTO meta VALUES('secret',?)", (uuid.uuid4().hex + uuid.uuid4().hex,))
            db.execute("INSERT OR IGNORE INTO meta VALUES('schema','1')")
            require(db.execute("SELECT value FROM meta WHERE key='schema'").fetchone()[0] == '1', 'unsupported-state-schema')
        self.path.chmod(0o600)

    @contextmanager
    def db(self):
        task_path(self.workspace, self.path)
        require(not self.path.exists() or self.path.stat().st_nlink == 1, 'unsafe-state-path')
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def version(db):
        return int(db.execute("SELECT value FROM meta WHERE key='version'").fetchone()[0])

    @staticmethod
    def bump(db):
        db.execute("UPDATE meta SET value=CAST(value AS INTEGER)+1 WHERE key='version'")
        return TaskTracker.version(db)

    def csrf(self, principal, cookie):
        with self.db() as db:
            secret = db.execute("SELECT value FROM meta WHERE key='secret'").fetchone()[0]
        return hmac.new(secret.encode(), (principal + ':' + hashlib.sha256(cookie.encode()).hexdigest()).encode(), hashlib.sha256).hexdigest()

    def mark_restarted(self):
        with self.db() as db:
            if db.execute("SELECT 1 FROM runs WHERE state='active'").fetchone():
                db.execute("UPDATE runs SET review=1 WHERE state='active'")
                self.bump(db)

    def task(self, task_id):
        uid(task_id)
        found = []
        for path, data in self.store.tasks():
            if data.get('task_id') == task_id:
                found.append((path, data))
        require(bool(found), 'task-not-synced')
        require(len(found) == 1, 'task-identity-ambiguous')
        path, data = found[0]
        require('.conflicted-' not in path.name, 'task-conflict-needs-resolution')
        require(not list(path.parent.glob(path.stem + '.conflicted-*.md')), 'task-conflict-needs-resolution')
        return path, data

    def remember_task(self, db, task_id):
        path, meta = self.task(task_id)
        row = db.execute('SELECT * FROM tasks WHERE id=?', (task_id,)).fetchone()
        work_id = row['work_id'] if row else str(uuid.uuid5(NAMESPACE, self.workspace.name + ':' + task_id))
        db.execute('INSERT INTO tasks VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET path=excluded.path',
                   (task_id, path.relative_to(self.store.root).as_posix(), work_id))
        return path, meta, work_id

    def event(self, request, *, replay=False):
        require(isinstance(request, dict), 'invalid-event', 400)
        allowed = {'operation_id', 'task_id', 'run_id', 'segment_id', 'device_id', 'action',
                   'occurred_at', 'expected_version', 'correction', 'reason', 'task_path'}
        require(set(request) <= allowed, 'unknown-event-field', 400)
        for key in ('operation_id', 'task_id', 'device_id'):
            uid(request.get(key))
        action, run_id = request.get('action'), request.get('run_id')
        require(action in ACTIONS, 'invalid-action', 400)
        if run_id is not None:
            uid(run_id)
        require(run_id is not None or action in {'complete', 'reopen'}, 'run-required', 400)
        if action in {'start', 'resume'}:
            uid(request.get('segment_id'))
        moment(request.get('occurred_at'))
        require(type(request.get('expected_version')) is int and request['expected_version'] >= 0,
                'invalid-version', 400)
        intent_hash = digest(request)
        now = stamp(self.clock())
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            previous = db.execute('SELECT * FROM events WHERE id=?', (request['operation_id'],)).fetchone()
            if previous:
                require(previous['intent_hash'] == intent_hash, 'operation-id-content-conflict')
                return json.loads(previous['result'])
            self.remember_task(db, request['task_id'])
            run = db.execute('SELECT * FROM runs WHERE id=?', (run_id,)).fetchone() if run_id else None
            require(not run or run['task_id'] == request['task_id'], 'run-task-conflict')
            active = db.execute("SELECT * FROM runs WHERE state='active'").fetchone()
            at = stamp(moment(request['occurred_at'])) if replay else now
            basis = 'owner-confirmed' if replay else 'measured'
            stale = request['expected_version'] != self.version(db) and run_id is not None and action != 'reopen'
            collision = action in {'start', 'resume'} and active is not None
            if stale or collision or (replay and action != 'start' and run_id and not run):
                if not replay:
                    raise TrackerError('pause-current-timer-first' if collision else 'stale-state')
                if not run:
                    db.execute('INSERT INTO runs(id,task_id,state,review,created) VALUES(?,?,?,1,?)',
                               (run_id, request['task_id'], 'conflict', at))
                else:
                    db.execute('UPDATE runs SET review=1 WHERE id=?', (run_id,))
                if active:
                    db.execute('UPDATE runs SET review=1 WHERE id=?', (active['id'],))
                result = {'status': 'conflict', 'code': 'offline-conflict-review-required',
                          'run_id': run_id, 'event_at': at, 'basis': basis, 'version': self.bump(db)}
            else:
                if action == 'start':
                    require(run is None, 'run-already-exists')
                    db.execute('INSERT INTO runs(id,task_id,state,created) VALUES(?,?,?,?)',
                               (run_id, request['task_id'], 'active', at))
                    db.execute('INSERT INTO segments VALUES(?,?,?,NULL,?)',
                               (request['segment_id'], run_id, at, basis))
                elif action == 'resume':
                    require(run and run['state'] == 'paused', 'run-not-paused')
                    db.execute("UPDATE runs SET state='active' WHERE id=?", (run_id,))
                    db.execute('INSERT INTO segments VALUES(?,?,?,NULL,?)',
                               (request['segment_id'], run_id, at, basis))
                elif action in {'pause', 'stop', 'complete'}:
                    if run:
                        require(run['state'] in {'active', 'paused'}, 'run-not-open')
                        if run['state'] == 'active':
                            segment = db.execute('SELECT * FROM segments WHERE run_id=? AND end IS NULL', (run_id,)).fetchone()
                            require(segment is not None, 'active-segment-missing')
                            bad_clock = moment(at) < moment(segment['start'])
                            db.execute('UPDATE segments SET end=?,basis=? WHERE id=?',
                                       (at, 'owner-confirmed' if basis == 'owner-confirmed' or segment['basis'] == 'owner-confirmed' else 'measured', segment['id']))
                            if bad_clock:
                                db.execute('UPDATE runs SET review=1 WHERE id=?', (run_id,))
                        db.execute('UPDATE runs SET state=?,status=? WHERE id=?',
                                   ('paused' if action == 'pause' else 'stopped', 'done' if action == 'complete' else run['status'], run_id))
                    else:
                        require(action == 'complete', 'run-not-found')
                elif action == 'reopen':
                    pass  # A status reversal never starts or resumes a timer.
                elif action in {'resolve', 'discard'}:
                    require(run and not run['receipt'] and run['state'] != 'active', 'stop-before-resolution')
                    require(not db.execute("SELECT 1 FROM runs WHERE review=1 AND state='active'").fetchone(), 'stop-conflicting-timer-first')
                    reason = request.get('reason')
                    require(isinstance(reason, str) and 0 < len(reason.strip()) <= 2000, 'resolution-reason-required', 400)
                    correction = self.correction(request.get('correction'), reason) if action == 'resolve' else None
                    db.execute('UPDATE runs SET state=?,review=0,correction=? WHERE id=?',
                               ('stopped' if action == 'resolve' else 'discarded', json.dumps(correction) if correction else None, run_id))
                result = {'status': 'accepted', 'run_id': run_id, 'event_at': at,
                          'basis': basis, 'version': self.bump(db)}
            if run_id and ((replay and moment(at) > self.clock() + timedelta(minutes=5)) or (not replay and abs((moment(request['occurred_at']) - self.clock()).total_seconds()) > 120)):
                db.execute('UPDATE runs SET review=1 WHERE id=?', (run_id,))
            db.execute('INSERT INTO events VALUES(?,?,?,?,?,?)',
                       (request['operation_id'], run_id, request['task_id'], intent_hash,
                        json.dumps(request, sort_keys=True), json.dumps(result)))
            return result

    @staticmethod
    def correction(values, reason):
        require(isinstance(values, dict) and 0 < len(values) <= 366, 'correction-days-required', 400)
        for day, seconds in values.items():
            try:
                require(datetime.fromisoformat(day).date().isoformat() == day, 'invalid-correction-day', 400)
            except (TypeError, ValueError):
                raise TrackerError('invalid-correction-day', 400) from None
            require(type(seconds) is int and 0 <= seconds <= int(((datetime.fromisoformat(day).replace(tzinfo=ZONE) + timedelta(days=1)).astimezone(timezone.utc) - datetime.fromisoformat(day).replace(tzinfo=ZONE).astimezone(timezone.utc)).total_seconds()), 'invalid-correction-seconds', 400)
        require(isinstance(reason, str) and bool(reason.strip()), 'correction-reason-required', 400)
        return {'days': values, 'reason': reason.strip()}

    def state(self, task_id=None):
        if task_id:
            uid(task_id)
        with self.db() as db:
            rows = db.execute('SELECT * FROM runs ORDER BY created DESC').fetchall()
            runs = []
            for row in rows:
                if task_id and row['task_id'] != task_id and row['state'] != 'active' and not row['review']:
                    continue
                value = dict(row)
                value['correction'] = json.loads(value['correction']) if value['correction'] else None
                value['receipt'] = json.loads(value['receipt']) if value['receipt'] else None
                value['segments'] = [dict(x) for x in db.execute('SELECT * FROM segments WHERE run_id=? ORDER BY start', (row['id'],))]
                value['events'] = [json.loads(x['payload']) for x in db.execute('SELECT payload FROM events WHERE run_id=? ORDER BY rowid', (row['id'],))]
                task = db.execute('SELECT path FROM tasks WHERE id=?', (row['task_id'],)).fetchone()
                value['path'] = task['path'] if task else ''
                runs.append(value)
            registry = Ledger(self.workspace).registry
            return {'version': self.version(db), 'server_now': stamp(self.clock()), 'runs': runs,
                    'entities': registry['entities'], 'owner_workspace': self.workspace.name}

    def bind(self, task_id, db):
        path, meta, work_id = self.remember_task(db, task_id)
        ledger = Ledger(self.workspace)
        task_ref = 'silverbullet:' + task_id
        with ledger.lock():
            registry = read_json(ledger.registry_path)
            matches = [b for b in registry['task_bindings'] if b['task_ref'] == task_ref]
            if matches:
                require(len(matches) == 1 and matches[0]['owner_workspace'] == self.workspace.name and
                        matches[0]['work_id'] == work_id, 'task-binding-conflict')
            else:
                registry['task_bindings'].append({'task_ref': task_ref, 'owner_workspace': self.workspace.name, 'work_id': work_id})
                validate_registry(registry)
                require(file_hash(ledger.registry_path) == ledger.loaded_registry_hash, 'registry-changed')
                atomic_write(ledger.registry_path, canonical_bytes(registry))
        return path, meta, work_id, task_ref

    def preview(self, request, principal):
        require(isinstance(request, dict) and set(request) <= {'run_id', 'outcome', 'client_id', 'project_id',
                'unassigned_confirmed', 'correction', 'reason', 'time_confirmed'}, 'invalid-preview', 400)
        run_id = uid(request.get('run_id'))
        outcome = request.get('outcome', '')
        require(isinstance(outcome, str) and 0 < len(outcome.strip()) <= 10000, 'outcome-required', 400)
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            run = db.execute('SELECT * FROM runs WHERE id=?', (run_id,)).fetchone()
            require(run and run['state'] == 'stopped', 'stop-before-preview')
            require(not run['receipt'], 'run-already-approved')
            require(not db.execute('SELECT 1 FROM runs WHERE review=1').fetchone(), 'resolve-time-conflicts-first')
            path, task, work_id, task_ref = self.bind(run['task_id'], db)
            segments = [dict(x) for x in db.execute('SELECT * FROM segments WHERE run_id=? ORDER BY start', (run_id,))]
            correction = json.loads(run['correction']) if run['correction'] else None
            if request.get('correction') is not None:
                correction = self.correction(request['correction'], request.get('reason', ''))
            pieces = []
            if correction:
                for day, seconds in sorted(correction['days'].items()):
                    pieces.append({'day': day, 'seconds': seconds, 'basis': 'owner-confirmed'})
            else:
                for segment in segments:
                    require(segment['end'] is not None, 'open-segment')
                    for piece in split_interval(segment['start'], segment['end']):
                        pieces.append({**piece, 'basis': segment['basis']})
            require(bool(pieces), 'no-recorded-time')
            require(all(p['basis'] == 'measured' for p in pieces) or request.get('time_confirmed') is True,
                    'owner-time-confirmation-required', 400)
            client, project = request.get('client_id'), request.get('project_id')
            if client is None or project is None:
                require(request.get('unassigned_confirmed') is True, 'confirm-unassigned-identity', 400)
            preview_id = str(uuid.uuid4())
            approval_path = task_path(self.workspace, self.home / 'approvals' / (preview_id + '.json'))
            proposal = {'schema_version': 1, 'run': dict(run), 'segments': segments, 'correction': correction,
                        'pieces': pieces, 'principal': principal, 'approval_receipt': str(approval_path.relative_to(self.workspace)),
                        'task_source': {'path': str(path.relative_to(self.store.root)), 'sha256': file_hash(path)},
                        'outcome': outcome.strip(), 'client_id': client, 'project_id': project}
            proposal_path = task_path(self.workspace, self.home / 'evidence' / (preview_id + '.json'))
            proposal_path.parent.mkdir(mode=0o700, exist_ok=True)
            atomic_write(proposal_path, canonical_bytes(proposal), immutable=True)
            ledger = Ledger(self.workspace)
            require(Path(ledger.config['source_roots'].get('tracker', '')) == self.workspace / 'work-evidence', 'tracker-source-alias-required')
            recorded = stamp(self.clock())
            candidate = {'schema_version': 1, 'changes': [], 'sessions': []}
            piece_bindings = []
            for index, piece in enumerate(pieces):
                entry_id = str(uuid.uuid5(NAMESPACE, run_id + ':entry:' + str(index)))
                session_id = str(uuid.uuid5(NAMESPACE, run_id + ':session:' + str(index)))
                piece_work_id = str(uuid.uuid5(NAMESPACE, work_id + ':' + run_id + ':' + str(index)))
                piece_ref = task_ref + '/runs/' + run_id + '/pieces/' + str(index)
                piece_bindings.append({'task_ref': piece_ref, 'owner_workspace': self.workspace.name, 'work_id': piece_work_id})
                source = {'root_alias': 'tracker', 'relative_path': proposal_path.relative_to(self.workspace / 'work-evidence').as_posix(),
                          'sha256': file_hash(proposal_path), 'observed_at': recorded, 'fact_date': piece['day'],
                          'evidence_level': 'owner-attested' if piece['basis'] == 'owner-confirmed' else self.evidence_level}
                timing = ({'kind': 'interval',
                           'start': moment(piece['start']).astimezone(ZONE).replace(microsecond=0).isoformat(),
                           'end': moment(piece['end']).astimezone(ZONE).replace(microsecond=0).isoformat(),
                           'timezone': 'Europe/Warsaw'}
                          if piece['basis'] == 'measured' else {'kind': 'date', 'date': piece['day']})
                duration = {'seconds': piece['seconds'], 'basis': piece['basis'], 'evidence_ref': 0, 'session_id': session_id}
                entry = {'schema_version': 1, 'entry_id': entry_id, 'work_id': piece_work_id, 'revision': 1,
                         'previous_revision_hash': None, 'owner_workspace': self.workspace.name,
                         'performed_on': piece['day'], 'recorded_at': recorded, 'actor_kind': 'human',
                         'client_id': client, 'project_id': project, 'task_ref': piece_ref,
                         'title_internal': str(task.get('title') or path.stem), 'activity_kind': 'task-work',
                         'outcome': outcome.strip(), 'status': run['status'], 'duration': duration,
                         'timing': timing, 'source_refs': [source], 'visibility': 'internal'}
                candidate['changes'].append({'row_id': str(uuid.uuid5(NAMESPACE, run_id + ':row:' + str(index))), 'entry': entry})
                candidate['sessions'].append({'schema_version': 1, 'session_id': session_id,
                    'owner_workspace': self.workspace.name, 'performed_on': piece['day'], 'recorded_at': recorded,
                    'timing': timing, 'duration': duration, 'allocations': [{'entry_id': entry_id, 'seconds': piece['seconds']}],
                    'source_refs': [source]})
            # Native WEP deliberately requires one work_id per entry. Keep that invariant.
            with ledger.lock():
                registry = read_json(ledger.registry_path)
                for binding in piece_bindings:
                    old = [b for b in registry['task_bindings'] if b['task_ref'] == binding['task_ref']]
                    require(not old or old == [binding], 'task-binding-conflict')
                    if not old:
                        registry['task_bindings'].append(binding)
                validate_registry(registry)
                require(file_hash(ledger.registry_path) == ledger.loaded_registry_hash, 'registry-changed')
                atomic_write(ledger.registry_path, canonical_bytes(registry))
            ledger = Ledger(self.workspace)
            native = ledger.preview(candidate)
            require(not native['warnings'], 'overlapping-human-time-review-required')
            body = {'id': preview_id, 'run_id': run_id, 'candidate': candidate, 'snapshot': native['snapshot'],
                    'task_source': proposal['task_source'], 'task_id': run['task_id'], 'version': self.version(db),
                    'approval_path': str(approval_path), 'principal': principal,
                    'total_seconds': sum(p['seconds'] for p in pieces), 'pieces': pieces, 'correction': correction,
                    'outcome': outcome.strip(), 'client_id': client, 'project_id': project}
            checksum = digest(body)
            db.execute('INSERT INTO approvals VALUES(?,?,?,?,?,NULL)',
                       (preview_id, run_id, json.dumps(body, sort_keys=True), checksum, 'preview'))
            return {'preview_id': preview_id, 'preview_hash': checksum, 'total_seconds': body['total_seconds'],
                    'pieces': pieces, 'outcome': body['outcome'], 'status': run['status'], 'correction': correction,
                    'client_id': client, 'project_id': project, 'snapshot': native['snapshot'],
                    'evidence': {'source': 'tracker:' + source['relative_path'], 'sha256': source['sha256']},
                    'task_ref': task_ref, 'task_work_id': work_id}

    def approve(self, preview_id, checksum, principal, *, failpoint=None):
        uid(preview_id)
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT * FROM approvals WHERE id=?', (preview_id,)).fetchone()
            require(row and hmac.compare_digest(row['hash'], str(checksum)), 'stale-preview')
            body = json.loads(row['body'])
            require(body['principal'] == principal, 'approval-owner-conflict', 403)
            if row['state'] == 'committed':
                return json.loads(row['receipt'])
            run = db.execute('SELECT * FROM runs WHERE id=?', (row['run_id'],)).fetchone()
            require(not run['receipt'] or row['state'] == 'prepared', 'run-already-approved')
            ledger = Ledger(self.workspace)
            if row['state'] == 'preview':
                path, _ = self.task(body['task_id'])
                require(file_hash(path) == body['task_source']['sha256'], 'task-changed-repreview')
                require(body['version'] == self.version(db) and body['snapshot'] == ledger.snapshot(), 'state-changed-repreview')
                proof = {'schema_version': 1, 'principal': principal, 'approved_at': stamp(self.clock()),
                         'preview_id': preview_id, 'preview_hash': checksum, 'candidate_hash': digest(body['candidate'])}
                approval_path = task_path(self.workspace, Path(body['approval_path']));approval_path.parent.mkdir(mode=0o700, exist_ok=True)
                if approval_path.exists():
                    old = read_json(approval_path)
                    require(old['preview_hash'] == checksum and old['principal'] == principal, 'approval-proof-conflict')
                else:
                    atomic_write(approval_path, canonical_bytes(proof), immutable=True)
                candidate_path = task_path(self.workspace, self.home / 'candidates' / (preview_id + '.json'))
                candidate_path.parent.mkdir(mode=0o700, exist_ok=True)
                if not candidate_path.exists():
                    atomic_write(candidate_path, canonical_bytes(body['candidate']), immutable=True)
                prepared = ledger.prepare(body['candidate'], candidate_source=(candidate_path, file_hash(candidate_path)))
                saved = {'transaction_id': prepared['transaction_id'], 'manifest_hash': prepared['manifest_hash']}
                db.execute("UPDATE approvals SET state='prepared',receipt=? WHERE id=?", (json.dumps(saved), preview_id))
                db.commit()  # Persist recovery coordinates before the native transaction.
                db.execute('BEGIN IMMEDIATE')
            else:
                saved = json.loads(row['receipt'])
            committed = next((c for c in ledger.committed()[2] if c['transaction_id'] == saved['transaction_id']), None)
            if committed:
                require(committed['manifest_hash'] == saved['manifest_hash'], 'transaction-receipt-conflict')
            else:
                ledger.apply(saved['transaction_id'], saved['manifest_hash'], failpoint=failpoint)
            receipt = {'status': 'committed', **saved, 'preview_id': preview_id, 'xlsx_status': 'pending'}
            db.execute("UPDATE approvals SET state='committed',receipt=? WHERE id=?", (json.dumps(receipt), preview_id))
            db.execute('UPDATE runs SET receipt=? WHERE id=?', (json.dumps(receipt), row['run_id']))
            self.bump(db)
        return self.refresh_workbook(preview_id)

    def refresh_workbook(self, preview_id):
        uid(preview_id)
        with self.db() as db:
            row = db.execute('SELECT * FROM approvals WHERE id=?', (preview_id,)).fetchone()
            require(row and row['state'] == 'committed', 'approval-not-committed')
            receipt = json.loads(row['receipt'])
            try:
                Workbook(Ledger(self.workspace)).export()
                receipt['xlsx_status'] = 'current'
            except (EvidenceError, OSError, ValueError, ImportError):
                receipt['xlsx_status'] = 'pending'
            db.execute('UPDATE approvals SET receipt=? WHERE id=?', (json.dumps(receipt), preview_id))
            db.execute('UPDATE runs SET receipt=? WHERE id=?', (json.dumps(receipt), row['run_id']))
            return receipt
