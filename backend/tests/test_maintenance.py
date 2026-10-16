import sqlite3

import pytest

from app.database import initialize
from app.maintenance import backup, readiness, restore, verify


def fixture_db(tmp_path):
    path = tmp_path / 'academy.sqlite3'
    initialize(path)
    with sqlite3.connect(path) as db:
        db.execute("INSERT INTO courses(id,folder,title) VALUES('course','Folder','Course')")
        db.execute("INSERT INTO lessons(id,course_id,relative_path,title,content_hash,file_size,modified_ns) VALUES('lesson','course','v.mp4','Lesson','hash',1,1)")
        db.execute("INSERT INTO lesson_progress(lesson_id,position,watched,updated_at) VALUES('lesson',42,1,'2000-01-01 00:00:00')")
        db.execute("INSERT INTO guided_lessons(id,lesson_id,status,document,video_hash,subtitle_hash) VALUES('guide','lesson','published','{}','a','b')")
        db.execute("INSERT INTO xp_transactions(award_key,guide_id,amount,reason) VALUES('one','guide',15,'Test XP')")
    return path


def test_deployment_snapshot_and_roundtrip_restore_retains_failed_data(tmp_path):
    path = fixture_db(tmp_path)
    result = backup(path)
    manifest = str(result['backup']).replace('.sqlite3', '.json')
    assert verify(path, manifest) == {'verified': True}
    with sqlite3.connect(path) as db:
        db.execute('UPDATE lesson_progress SET position=0')
    with pytest.raises(RuntimeError, match='lesson_progress'):
        verify(path, manifest)
    journal = path.with_name(path.name + '-journal')
    journal.write_bytes(b'Synthetic retained journal')
    recovery = restore(path, result['backup'])
    assert not journal.exists()
    assert (path.parent / recovery['retained_failed_data'] / journal.name).exists()
    assert verify(path, manifest)['verified']
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT position FROM lesson_progress').fetchone()[0] == 42
        assert db.execute('SELECT SUM(amount) FROM xp_transactions').fetchone()[0] == 15
    with sqlite3.connect(recovery['retained_failed_data'] + '/academy.sqlite3') as db:
        assert db.execute('SELECT position FROM lesson_progress').fetchone()[0] == 0


def test_backup_is_not_a_migration_and_supports_wal(tmp_path):
    path = fixture_db(tmp_path)
    with sqlite3.connect(path) as db:
        db.execute('PRAGMA journal_mode=WAL')
        db.execute("UPDATE settings SET value='WAL checkpoint' WHERE key='welcome_message'")
        db.commit()
        saved = backup(path)
        with sqlite3.connect(saved['backup']) as snap:
            assert snap.execute("SELECT value FROM settings WHERE key='welcome_message'").fetchone()[0] == 'WAL checkpoint'
    old = tmp_path / 'old.sqlite3'
    with sqlite3.connect(old) as db:
        db.execute('CREATE TABLE settings(key TEXT PRIMARY KEY,value TEXT)')
        db.execute('PRAGMA user_version=1')
    assert backup(old)['schema'] == 1
    with sqlite3.connect(old) as db:
        assert db.execute('PRAGMA user_version').fetchone()[0] == 1


def test_idle_detection_and_missing_database(tmp_path):
    path = fixture_db(tmp_path)
    assert readiness(path)['ready']
    with sqlite3.connect(path) as db:
        db.execute('UPDATE lesson_progress SET updated_at=CURRENT_TIMESTAMP')
    assert not readiness(path)['ready']
    absent = tmp_path / 'absent.sqlite3'
    assert backup(absent) == {'empty': True}
    assert readiness(absent)['ready']
    assert not absent.exists()


def test_added_schema_columns_allowed_but_earned_xp_changes_rejected(tmp_path):
    path = fixture_db(tmp_path)
    saved = backup(path)
    manifest = str(saved['backup']).replace('.sqlite3', '.json')
    with sqlite3.connect(path) as db:
        db.execute('ALTER TABLE lesson_progress ADD COLUMN extra TEXT')
        db.execute("INSERT INTO settings(key,value) VALUES('new_migration_default','default')")
    assert verify(path, manifest)['verified']
    with sqlite3.connect(path) as db:
        db.execute('UPDATE xp_transactions SET amount=999')
    with pytest.raises(RuntimeError, match='xp_transactions'):
        verify(path, manifest)


def test_restore_rejects_external_snapshot_and_bad_integrity(tmp_path):
    path = fixture_db(tmp_path)
    outside = tmp_path / 'outside.sqlite3'
    outside.write_text('Not a database')
    with pytest.raises(ValueError, match='deployment snapshot'):
        restore(path, outside)
    path.write_text('Not a database')
    with pytest.raises(sqlite3.DatabaseError):
        backup(path)
