"""Same-origin owner API over a Unix socket; no shell or generic file endpoint."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import hmac
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path, PurePosixPath
import socket
import sqlite3
from socketserver import ThreadingMixIn
import tempfile
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, unquote, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler, ProxyHandler

from silverbullet_tracker import TaskTracker, TrackerError, require
from task_identity import initialize_markdown
from task_store import MAX_TASK, safe_path
from work_evidence import EvidenceError

PREFIX = '/.task-tracker/api/v1/'


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class Application:
    def __init__(self, config, *, tracker=None):
        require(set(config) <= {'workspace', 'socket_path', 'origin', 'allowed_user', 'native_url', 'evidence_level'},
                'unknown-service-config', 400)
        self.config = config
        origin, native = urlsplit(config['origin']), urlsplit(config['native_url'])
        require(origin.scheme in {'http', 'https'} and bool(origin.netloc) and not origin.path,
                'invalid-origin-config', 400)
        require(native.scheme == 'http' and native.hostname == '127.0.0.1' and not native.path,
                'native-auth-must-use-loopback', 400)
        require(isinstance(config.get('allowed_user'), str) and bool(config['allowed_user']), 'owner-required', 400)
        self.tracker = tracker or TaskTracker(config['workspace'], evidence_level=config.get('evidence_level', 'production-readback'))
        self.opener = build_opener(ProxyHandler({}), NoRedirect())

    def authenticate(self, headers):
        cookie = headers.get('Cookie', '')
        require(bool(cookie) and len(cookie) <= 16384, 'authentication-required', 401)
        req = Request(self.config['native_url'] + '/.dashboard/api/profile', headers={
            'Cookie': cookie, 'Host': urlsplit(self.config['origin']).netloc, 'Accept': 'application/json',
            # Native central sessions bind their origin to the reverse-proxy scheme.
            # Use fixed reviewed config, never request-supplied forwarding headers.
            'X-Forwarded-Proto': urlsplit(self.config['origin']).scheme,
            'X-Forwarded-Host': urlsplit(self.config['origin']).netloc})
        try:
            with self.opener.open(req, timeout=5) as response:
                require(response.status == 200 and 'application/json' in response.headers.get('Content-Type', ''),
                        'authentication-required', 401)
                profile = json.loads(response.read(16384))
        except HTTPError:
            raise TrackerError('authentication-required', 401) from None
        except (URLError, OSError, ValueError):
            raise TrackerError('authentication-unavailable', 503) from None
        require(profile.get('username') == self.config['allowed_user'] and profile.get('admin') is True,
                'owner-access-required', 403)
        return profile['username'], cookie

    def authorize_write(self, headers, principal, cookie):
        require(headers.get('Origin') == self.config['origin'], 'origin-rejected', 403)
        require(headers.get('Sec-Fetch-Site', 'same-origin') == 'same-origin', 'origin-rejected', 403)
        expected = self.tracker.csrf(principal, cookie)
        require(hmac.compare_digest(str(headers.get('X-Task-Tracker-CSRF', '')), expected), 'csrf-rejected', 403)

    def create_task(self, path, body, headers):
        lock = safe_path(self.tracker.store.root, self.tracker.store.root / '.ai-system-task-store.lock')
        with os.fdopen(os.open(lock, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600), 'r+') as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            return self._create_task(path, body, headers)

    def _create_task(self, path, body, headers):
        require(headers.get('If-None-Match') == '*' and headers.get('X-Sync-Mode') == 'true', 'create-only-required', 400)
        relative = unquote(path.removeprefix('/.task-create/'))
        parts = PurePosixPath(relative).parts
        require(relative.startswith('tasks/') and relative.endswith('.md') and '\\' not in relative and
                all(p not in {'', '.', '..'} and not p.startswith('.') for p in relative.split('/')),
                'unsafe-task-path', 400)
        target = safe_path(self.tracker.store.root, self.tracker.store.root.joinpath(*parts))
        require(not target.exists(), 'task-title-path-collision', 412)
        text = initialize_markdown(body.decode('utf-8'), created=True, at=self.tracker.clock(), author='human')
        # A prefilled template ID cannot create a second task with the same identity.
        from task_store import frontmatter
        task_id = frontmatter(text)['task_id']
        require(not any(meta.get('task_id') == task_id for _, meta in self.tracker.store.tasks()), 'duplicate-task-id')
        target.parent.mkdir(parents=True, exist_ok=True)
        safe_path(self.tracker.store.root, target.parent)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=target.parent, prefix='.tracker-create-', delete=False) as output:
                temporary = Path(output.name);output.write(text.encode());output.flush();os.fsync(output.fileno())
            os.link(temporary, target, follow_symlinks=False)
        except FileExistsError:
            raise TrackerError('task-title-path-collision', 412) from None
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        return {'status': 'created', 'task_id': task_id}, {
            'X-Last-Modified': str(int(target.stat().st_mtime * 1000)),
            'ETag': '"sha256:' + hashlib.sha256(target.read_bytes()).hexdigest() + '"', 'X-Permission': 'rw'}

    def handle(self, method, raw_path, headers, body=b''):
        parsed = urlsplit(raw_path)
        path = parsed.path
        require(path.startswith(PREFIX) or path.startswith('/.task-create/tasks/'), 'not-found', 404)
        principal, cookie = self.authenticate(headers)
        if method == 'GET':
            require(path == PREFIX + 'state', 'not-found', 404)
            query = parse_qs(parsed.query)
            require(set(query) <= {'task_id'}, 'unknown-query', 400)
            state = self.tracker.state(query.get('task_id', [None])[0])
            return 200, {**state, 'csrf': self.tracker.csrf(principal, cookie)}, {}
        require(method in {'POST', 'PUT'}, 'method-not-allowed', 405)
        self.authorize_write(headers, principal, cookie)
        require(len(body) <= MAX_TASK, 'request-too-large', 413)
        if method == 'PUT':
            require(path.startswith('/.task-create/tasks/') and not parsed.query, 'not-found', 404)
            data, extra = self.create_task(path, body, headers)
            return 201, data, extra
        require('application/json' in headers.get('Content-Type', ''), 'json-required', 415)
        try:
            value = json.loads(body)
        except (ValueError, UnicodeError):
            raise TrackerError('invalid-json', 400) from None
        require(isinstance(value, dict), 'json-object-required', 400)
        if path == PREFIX + 'events':
            require(set(value) <= {'event', 'replay'} and isinstance(value.get('replay', False), bool), 'invalid-event-envelope', 400)
            result = self.tracker.event(value.get('event'), replay=value.get('replay', False))
        elif path == PREFIX + 'wep/preview':
            result = self.tracker.preview(value, principal)
        elif path == PREFIX + 'wep/approve':
            require(set(value) == {'preview_id', 'preview_hash'}, 'invalid-approval', 400)
            result = self.tracker.approve(value['preview_id'], value['preview_hash'], principal)
        elif path == PREFIX + 'wep/refresh':
            require(set(value) == {'preview_id'}, 'invalid-refresh', 400)
            result = self.tracker.refresh_workbook(value['preview_id'])
        else:
            raise TrackerError('not-found', 404)
        return 200, result, {}


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(15)

    def log_message(self, *args):
        pass  # Never log request bodies, paths containing task titles, or session cookies.

    def dispatch(self):
        try:
            length = int(self.headers.get('Content-Length', '0'))
            require(0 <= length <= MAX_TASK, 'request-too-large', 413)
            require(not self.headers.get('Transfer-Encoding'), 'unsupported-transfer', 400)
            body = self.rfile.read(length)
            status, data, extra = self.server.application.handle(self.command, self.path, self.headers, body)
        except TrackerError as error:
            status, data, extra = error.status, {'error': error.code}, {}
        except EvidenceError as error:
            status, data, extra = 409, {'error': error.category}, {}
        except (ValueError, UnicodeError, KeyError, TypeError):
            status, data, extra = 400, {'error': 'invalid-input'}, {}
        except (OSError, sqlite3.Error):
            status, data, extra = 503, {'error': 'storage-unavailable'}, {}
        encoded = json.dumps(data, ensure_ascii=False, allow_nan=False).encode()
        self.send_response(status)
        for name, value in {'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store',
                            'X-Content-Type-Options': 'nosniff', 'Content-Length': str(len(encoded)), **extra}.items():
            self.send_header(name, value)
        self.end_headers();self.wfile.write(encoded)

    do_GET = do_POST = do_PUT = do_DELETE = do_PATCH = do_OPTIONS = dispatch


class UnixServer(ThreadingMixIn, HTTPServer):
    address_family = socket.AF_UNIX
    daemon_threads = True

    def server_bind(self):
        socket.socket.bind(self.socket, self.server_address)
        self.server_name = 'localhost';self.server_port = 0


def main():
    parser = argparse.ArgumentParser(description=__doc__);parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    require(not args.config.is_symlink(), 'unsafe-config')
    config = json.loads(args.config.read_text())
    path = Path(config['socket_path'])
    require(path.is_absolute() and not path.is_symlink() and path.parent.is_dir(), 'unsafe-socket-path')
    lock = os.open(str(path) + '.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    if path.exists():
        require(path.is_socket() and path.stat().st_uid == os.getuid(), 'unknown-existing-socket')
        with socket.socket(socket.AF_UNIX) as probe:
            if probe.connect_ex(str(path)) == 0:
                raise TrackerError('socket-already-active')
        path.unlink()
    app = Application(config);app.tracker.mark_restarted()
    server = UnixServer(str(path), Handler);server.application = app;path.chmod(0o660)
    try:
        server.serve_forever()
    finally:
        server.server_close();path.unlink(missing_ok=True);os.close(lock)


if __name__ == '__main__':
    main()
