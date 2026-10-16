import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


@contextmanager
def connect(path: Path):
    db = sqlite3.connect(path, timeout=15)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys = ON')
    try:
        with db:
            yield db
    finally:
        db.close()


def initialize(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with connect(path) as db:
        version = db.execute('PRAGMA user_version').fetchone()[0]
        if version > 4:
            raise RuntimeError('Database schema is newer than this application')
        if version == 0:
            db.executescript(Path(__file__).with_name('schema.sql').read_text())
            version = 1
        if version == 1:
            # SQLite's backup API creates a consistent pre-migration snapshot.
            backups = path.parent / 'backups'
            backups.mkdir(exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            backup = sqlite3.connect(backups / f'pre-v2-{stamp}.sqlite3')
            try:
                db.backup(backup)
            finally:
                backup.close()
            db.executescript(Path(__file__).with_name('migration_002.sql').read_text())
            version = 2
        if version == 2:
            backups = path.parent / 'backups'
            backups.mkdir(exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            backup = sqlite3.connect(backups / f'pre-v3-{stamp}.sqlite3')
            try:
                db.backup(backup)
            finally:
                backup.close()
            db.executescript(Path(__file__).with_name('migration_003.sql').read_text())
            version = 3
        if version == 3:
            backups = path.parent / 'backups'
            backups.mkdir(exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            backup = sqlite3.connect(backups / f'pre-v4-{stamp}.sqlite3')
            try:
                db.backup(backup)
            finally:
                backup.close()
            db.executescript(Path(__file__).with_name('migration_004.sql').read_text())
