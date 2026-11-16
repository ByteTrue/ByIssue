#!/usr/bin/env python3
"""Exercise the frozen inbox contract over loopback HTTP and subprocess CLI."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import hashlib
import hmac
import http.client
import json
import os
from pathlib import Path
import selectors
import subprocess
import sys
import tempfile
import time

SECRET = 'evaluation-only-local-secret'


def cli(project, *args):
    env = dict(os.environ)
    env.pop('INBOX_SECRET', None)
    return subprocess.run([sys.executable, str(project / 'inbox.py'), *map(str, args)],
                          cwd=project, env=env, capture_output=True, text=True, timeout=10)


@contextmanager
def server(project, db):
    with tempfile.TemporaryFile() as stderr:
        proc = subprocess.Popen([sys.executable, str(project / 'inbox.py'), 'serve', '--db', str(db), '--port', '0'],
                                cwd=project, env=dict(os.environ, INBOX_SECRET=SECRET),
                                stdout=subprocess.PIPE, stderr=stderr)
        try:
            with selectors.DefaultSelector() as ready:
                ready.register(proc.stdout, selectors.EVENT_READ)
                assert ready.select(10), 'server did not announce a port'
            line = proc.stdout.readline()
            announcement = json.loads(line)
            port = announcement['port']
            assert type(port) is int and 0 < port < 65536, announcement
            yield port
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            trailing = proc.stdout.read()
            proc.stdout.close()
            assert not trailing.strip(), 'request logs or secrets written to stdout'
            stderr.seek(0)
            assert SECRET.encode() not in stderr.read(), 'secret leaked to stderr'


def request(port, body, *, stamp=None, signature=None, path='/events', headers=True):
    stamp = str(int(time.time())) if stamp is None else stamp
    digest = hmac.new(SECRET.encode(), stamp.encode() + b'.' + body, hashlib.sha256).hexdigest()
    auth = {'X-Inbox-Timestamp': stamp, 'X-Inbox-Signature': digest if signature is None else signature} if headers else {}
    conn = http.client.HTTPConnection('127.0.0.1', port, timeout=10)
    try:
        conn.request('POST', path, body=body, headers={'Content-Type': 'application/json', **auth})
        response = conn.getresponse()
        raw = response.read()
        assert SECRET.encode() not in raw, 'secret leaked in response'
        return response.status, json.loads(raw)
    finally:
        conn.close()


def accept(project):
    with tempfile.TemporaryDirectory(prefix='inbox-accept-') as tmp:
        root = Path(tmp)
        db = root / 'events.sqlite'
        missing = cli(project, 'serve', '--db', db, '--port', '0')
        assert missing.returncode != 0, 'service started without a secret'
        empty = cli(project, 'list', '--db', db)
        assert empty.returncode == 0 and json.loads(empty.stdout) == [], empty
        rows = [{'id': 'b-build', 'payload': {'status': 'ok', 'attempt': 1}},
                {'id': 'a-build', 'payload': {'title': '构建', 'nested': {'z': True, 'a': [1, None]}}}]
        with server(project, db) as port:
            for row in rows:
                status, result = request(port, json.dumps(row).encode())
                assert (status, result) == (201, {'id': row['id'], 'status': 'stored'}), (status, result)
            equivalent = b'{"payload":{"attempt":1,"status":"ok"}, "id":"b-build"}'
            assert request(port, equivalent) == (200, {'id': 'b-build', 'status': 'duplicate'})
            invalid = [
                (json.dumps({'id': 'b-build', 'payload': {'status': 'changed'}}).encode(), {}, 409),
                (json.dumps({'id': 'b-build', 'payload': {'status': 'ok', 'attempt': True}}).encode(), {}, 409),
                (b'{"id":"unsigned","payload":{}}', {'headers': False}, 401),
                (b'{"id":"bad-sig","payload":{}}', {'signature': '0' * 64}, 401),
                (b'{"id":"stale","payload":{}}', {'stamp': str(int(time.time()) - 600)}, 401),
                (b'{"id":"future","payload":{}}', {'stamp': str(int(time.time()) + 600)}, 401),
                (b'{"id":"bad-time","payload":{}}', {'stamp': 'nan'}, 401),
                (b'{', {}, 400),
                (b'{"id":" ","payload":{}}', {}, 400),
                (b'{"id":"bad-payload","payload":[]}', {}, 400),
                (b'{"id":"extra","payload":{},"other":1}', {}, 400),
                (b'{"id":"nan","payload":{"v":NaN}}', {}, 400),
                (b'{"id":"large","payload":{"v":"' + b'x' * 65536 + b'"}}', {}, 413),
                (b'{"id":"wrong-path","payload":{}}', {'path': '/missing'}, 404),
            ]
            for body, options, expected in invalid:
                status, result = request(port, body, **options)
                assert status == expected and isinstance(result.get('error'), str) and result['error'], (body[:60], status, result)
            concurrent = {'id': 'c-build', 'payload': {'status': 'queued'}}
            with ThreadPoolExecutor(max_workers=6) as pool:
                responses = list(pool.map(lambda _: request(port, json.dumps(concurrent).encode()), range(6)))
            assert sorted(code for code, _ in responses) == [200] * 5 + [201], responses
            for code, value in responses:
                assert value == {'id': 'c-build', 'status': 'stored' if code == 201 else 'duplicate'}, value
            rows.append(concurrent)
        expected = sorted(rows, key=lambda row: row['id'])
        listed = cli(project, 'list', '--db', db)
        assert listed.returncode == 0 and json.loads(listed.stdout) == expected, listed
        with server(project, db) as port:
            assert request(port, json.dumps(rows[0]).encode()) == (200, {'id': 'b-build', 'status': 'duplicate'})
        target = root / 'export.json'
        target.write_text('previous output\n')
        exported = cli(project, 'export', '--db', db, '--output', target)
        assert exported.returncode == 0 and json.loads(exported.stdout) == {'count': 3}, exported
        assert json.loads(target.read_text()) == expected and target.read_bytes().endswith(b'\n')
        before = target.read_bytes()
        invalid_db = root / 'invalid.sqlite'
        invalid_db.write_bytes(b'not a sqlite database')
        failed = cli(project, 'export', '--db', invalid_db, '--output', target)
        assert failed.returncode != 0 and target.read_bytes() == before, failed
        names_before = set(root.iterdir())
        failed = cli(project, 'export', '--db', db, '--output', root / 'missing/export.json')
        assert failed.returncode != 0 and set(root.iterdir()) == names_before, failed
        print('PASS: signed HTTP, validation, idempotency, conflict, concurrency, restart, list and export success/failure preservation')


if __name__ == '__main__':
    accept(Path(sys.argv[1]).resolve())
