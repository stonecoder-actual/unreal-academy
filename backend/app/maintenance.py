"""Offline deployment tools. Never initialize/migrate a database while backing it up."""
import argparse
import hashlib
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from contextlib import closing, contextmanager

# Only learner/identity records: guide publication can legitimately change at startup.
TABLES = ('settings', 'courses', 'lessons', 'lesson_progress', 'quiz_attempts',
          'xp_transactions', 'practice_submissions', 'progression_unlocks',
          'progression_equipment', 'mastery_plan', 'mastery_state')


@contextmanager
def open_readonly(path):
    db = sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True)
    try:
        yield db
    finally:
        db.close()


def fingerprint(db):
    present = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    result = {}
    for table in TABLES:
        if table not in present:
            continue
        # Name comes only from TABLES; retain columns so compatible migrations may add fields.
        columns = [r[1] for r in db.execute(f'PRAGMA table_info({table})')]
        rows = sorted((list(r) for r in db.execute(f'SELECT * FROM {table}')), key=lambda r: json.dumps(r))
        raw = json.dumps(rows, ensure_ascii=False, separators=(',', ':')).encode()
        result[table] = {'columns': columns, 'count': len(rows), 'sha256': hashlib.sha256(raw).hexdigest()}
    return result


def backup(database):
    database = Path(database)
    if not database.exists():
        return {'empty': True}
    folder = database.parent / 'backups' / 'deployments'
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{uuid.uuid4().hex}.sqlite3'
    with open_readonly(database) as source, closing(sqlite3.connect(target)) as dest:
        if source.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise RuntimeError('Database integrity check failed; deployment stopped')
        source.backup(dest)
    with open_readonly(target) as db:
        result = {'empty': False, 'backup': str(target), 'schema': db.execute('PRAGMA user_version').fetchone()[0],
                  'tables': fingerprint(db)}
    target.with_suffix('.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result


def verify(database, manifest):
    saved = json.loads(Path(manifest).read_text(encoding='utf-8'))
    with open_readonly(database) as db:
        if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise RuntimeError('Updated database integrity check failed')
        for table, expected in saved['tables'].items():
            columns = expected['columns']
            # Columns originated in a local snapshot, but still quote identifiers safely.
            names = ','.join('"' + c.replace('"', '""') + '"' for c in columns)
            rows = sorted((list(r) for r in db.execute(f'SELECT {names} FROM "{table}"')), key=lambda r: json.dumps(r))
            if table == 'settings':
                # Migrations may add defaults; existing settings must retain their values.
                with open_readonly(saved['backup']) as previous:
                    keys = {r[0] for r in previous.execute('SELECT key FROM settings')}
                key_column = columns.index('key')
                rows = [r for r in rows if r[key_column] in keys]
            raw = json.dumps(rows, ensure_ascii=False, separators=(',', ':')).encode()
            if len(rows) != expected['count'] or hashlib.sha256(raw).hexdigest() != expected['sha256']:
                raise RuntimeError(f'Existing {table} records changed; keep frontend stopped and roll back')
    return {'verified': True}


def readiness(database, idle_minutes=30):
    if not Path(database).exists():
        return {'ready': True}
    with open_readonly(database) as db:
        present = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for table, column in (('lesson_progress', 'updated_at'), ('quiz_attempts', 'created_at')):
            if table in present and db.execute(
                f"SELECT 1 FROM {table} WHERE datetime({column}) > datetime('now', ?) LIMIT 1",
                (f'-{idle_minutes} minutes',),
            ).fetchone():
                return {'ready': False, 'reason': 'Recent learner activity; retry on the next scheduled check'}
    return {'ready': True}


def restore(database, snapshot):
    """Run only with both services stopped. Preserve the failed DB and sidecars."""
    database, snapshot = Path(database), Path(snapshot)
    allowed = (database.parent / 'backups' / 'deployments').resolve()
    if snapshot.resolve().parent != allowed or not snapshot.is_file():
        raise ValueError('Restore requires a deployment snapshot from this data directory')
    with open_readonly(snapshot) as db:
        if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise RuntimeError('Snapshot integrity check failed')
    retained = allowed / f'failed-{uuid.uuid4().hex}'
    retained.mkdir()
    for suffix in ('', '-wal', '-shm', '-journal'):
        original = Path(str(database) + suffix)
        if original.exists():
            original.rename(retained / original.name)
    with open_readonly(snapshot) as source, closing(sqlite3.connect(database)) as dest:
        source.backup(dest)
    return {'restored': True, 'retained_failed_data': str(retained)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['backup', 'verify', 'readiness', 'restore'])
    parser.add_argument('--database', default=os.getenv('DATABASE_PATH', '/data/academy.sqlite3'))
    parser.add_argument('--snapshot')
    args = parser.parse_args()
    if args.action in ('verify', 'restore') and not args.snapshot:
        parser.error('--snapshot is required')
    result = {'backup': lambda: backup(args.database), 'readiness': lambda: readiness(args.database),
              'verify': lambda: verify(args.database, args.snapshot),
              'restore': lambda: restore(args.database, args.snapshot)}[args.action]()
    print(json.dumps(result))


if __name__ == '__main__':
    main()
