import sqlite3
import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def library(tmp_path):
    root = tmp_path / 'courses'
    course = root / 'Beginner'
    course.mkdir(parents=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'color=c=blue:s=160x90:d=3',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', str(course / '01 Intro.mp4')], check=True)
    (course / '01 Intro.srt').write_text('1\n00:00:00,000 --> 00:00:02,000\nHello <b>builder</b>!\n', encoding='utf-8')
    (course / '01 Intro.txt').write_text('Build a room.', encoding='utf-8')
    (course / 'Resources').mkdir()
    (course / 'Resources' / 'guide.pdf').write_bytes(b'course guide fixture')
    return tmp_path / 'data' / 'academy.sqlite3', root, course


def import_and_detail(client):
    response = client.post('/api/courses/import', json={'folder': 'Beginner'})
    assert response.status_code == 200, response.text
    return client.get('/api/courses/' + response.json()['course_id']).json()


def test_import_playback_captions_resources_and_restart(library):
    database, root, _ = library
    with TestClient(create_app(database, root)) as client:
        assert client.get('/api/library/folders').json() == {'folders': ['Beginner']}
        course = import_and_detail(client)
        lesson = course['lessons'][0]
        assert lesson['playable'] == 1
        assert lesson['duration'] == pytest.approx(3, abs=.2)
        video = client.get(f"/api/lessons/{lesson['id']}/video", headers={'Range': 'bytes=0-99'})
        assert video.status_code == 206
        assert len(video.content) == 100
        assert video.headers['content-range'].startswith('bytes 0-99/')
        invalid = client.get(f"/api/lessons/{lesson['id']}/video", headers={'Range': 'bytes=99999999-'})
        assert invalid.status_code == 416
        captions = client.get(f"/api/lessons/{lesson['id']}/captions")
        assert captions.text.startswith('WEBVTT')
        assert '00:00:02.000' in captions.text
        assert '<b>' not in captions.text
        assert len(course['resources']) == 2
        associated = next(r for r in course['resources'] if r['lesson_id'])
        resource = client.get(f"/api/resources/{associated['id']}/download")
        assert resource.text == 'Build a room.'
        assert 'attachment' in resource.headers['content-disposition']
        response = client.put(f"/api/lessons/{lesson['id']}/progress", json={'position': 1.5, 'watched': True})
        assert response.status_code == 200
        assert len(client.get('/api/courses').json()) == 1
        assert import_and_detail(client)['lessons'][0]['id'] == lesson['id']
    with TestClient(create_app(database, root)) as client:
        lesson = import_and_detail(client)['lessons'][0]
        assert lesson['position'] == 1.5
        assert lesson['watched'] == 1
        client.put(f"/api/lessons/{lesson['id']}/progress", json={'position': 1})
        assert client.get('/api/courses').json()[0]['watched_count'] == 1


def test_rescan_move_missing_and_replaced_video(library):
    database, root, folder = library
    with TestClient(create_app(database, root)) as client:
        lesson = import_and_detail(client)['lessons'][0]
        client.put(f"/api/lessons/{lesson['id']}/progress", json={'position': 2, 'watched': True})
        source = folder / lesson['relative_path']
        source.rename(folder / '02 Renamed.mp4')
        moved = import_and_detail(client)['lessons'][0]
        assert moved['id'] == lesson['id'] and moved['position'] == 2
        (folder / '02 Renamed.mp4').write_bytes(b'replacement video')
        replaced = import_and_detail(client)['lessons'][0]
        assert replaced['position'] == 2 and replaced['watched'] == 1
        assert replaced['playable'] == 0
        # A missing lesson is retained, not silently deleted with its progress.
        (folder / '01 Other.mp4').write_bytes(b'another video')
        (folder / '02 Renamed.mp4').unlink()
        lessons = import_and_detail(client)['lessons']
        missing = next(row for row in lessons if row['id'] == lesson['id'])
        assert missing['available'] == 0
        assert client.get(f"/api/lessons/{lesson['id']}/video").status_code == 404
        (folder / '01 Other.mp4').unlink()
        empty = import_and_detail(client)
        assert all(row['available'] == 0 for row in empty['lessons'])
        assert next(row for row in empty['lessons'] if row['id'] == lesson['id'])['position'] == 2


def test_paths_validation_and_missing_ids(library):
    database, root, _ = library
    with TestClient(create_app(database, root)) as client:
        for folder in ('..', '../data', '/etc', 'Beginner/Resources'):
            assert client.post('/api/courses/import', json={'folder': folder}).status_code == 400
        assert client.get('/api/courses/missing').status_code == 404
        assert client.get('/api/resources/missing/download').status_code == 404
        assert client.get('/api/lessons/missing/video').status_code == 404
        lesson = import_and_detail(client)['lessons'][0]
        for position in (-1, 604801, 'NaN', 'Infinity'):
            assert client.put(f"/api/lessons/{lesson['id']}/progress", json={'position': position}).status_code == 422
        result = client.put(f"/api/lessons/{lesson['id']}/progress", json={'position': 100})
        assert result.json()['position'] <= 3.1


def test_multiple_courses_nested_paths_names_and_english_captions(library):
    database, root, folder = library
    second = root / 'Wrapper' / 'Actual course'
    second.mkdir(parents=True)
    (second / '001-Intro-source.mp4').write_bytes((folder / '01 Intro.mp4').read_bytes())
    (second / '001-Intro-english-source.srt').write_text('1\n00:00:00,110 --> 00:00:02,0\nEnglish\n')
    (second / '001-Intro-persian-source.srt').write_text('Other language')
    with TestClient(create_app(database, root)) as client:
        first = import_and_detail(client)
        first_id = first['lessons'][0]['id']
        client.put(f'/api/lessons/{first_id}/progress', json={'position': 1.5, 'watched': True})
        response = client.post('/api/courses/import', json={'folder': 'Wrapper/Actual course', 'title': 'Gameplay Ability System'})
        assert response.status_code == 200
        second_id = response.json()['course_id']
        second = client.get(f'/api/courses/{second_id}').json()
        assert second['title'] == 'Gameplay Ability System'
        lesson = second['lessons'][0]
        assert lesson['position'] == 0 and lesson['watched'] == 0
        caption = client.get(f"/api/lessons/{lesson['id']}/captions").text
        assert 'English' in caption and '00:00:02.000' in caption
        client.put(f"/api/lessons/{lesson['id']}/progress", json={'position': 2})
        assert client.get('/api/xp').json()['total_xp'] == 0
    with TestClient(create_app(database, root)) as client:
        assert client.get(f"/api/courses/{first['id']}").json()['lessons'][0]['position'] == 1.5
        assert client.get(f'/api/courses/{second_id}').json()['lessons'][0]['position'] == 2
        assert client.post('/api/courses/import', json={'folder': 'Wrapper/Actual course'}).json()['course_id'] == second_id
        assert client.get(f'/api/courses/{second_id}').json()['title'] == 'Gameplay Ability System'


def test_symlink_escape(library):
    database, root, folder = library
    outside = root.parent / 'secret.txt'
    outside.write_text('private')
    (folder / 'secret.txt').symlink_to(outside)
    with TestClient(create_app(database, root)) as client:
        course = import_and_detail(client)
        assert all(r['relative_path'] != 'secret.txt' for r in course['resources'])
        lesson = course['lessons'][0]
        (folder / lesson['relative_path']).unlink()
        (folder / lesson['relative_path']).symlink_to(outside)
        assert client.get(f"/api/lessons/{lesson['id']}/video").status_code == 400


def test_migration_backup_preserves_phase_one(tmp_path):
    database = tmp_path / 'academy.sqlite3'
    with sqlite3.connect(database) as db:
        db.executescript(Path('app/schema.sql').read_text())
        db.execute("UPDATE settings SET value='Existing welcome'")
    with TestClient(create_app(database, tmp_path / 'courses')) as client:
        assert client.get('/api/settings').json()['welcome_message'] == 'Existing welcome'
    backups = list((tmp_path / 'backups').glob('pre-v2-*.sqlite3'))
    assert len(backups) == 1
    with sqlite3.connect(backups[0]) as db:
        assert db.execute('PRAGMA user_version').fetchone()[0] == 1
        assert db.execute('SELECT value FROM settings').fetchone()[0] == 'Existing welcome'
    with sqlite3.connect(database) as db:
        assert db.execute('PRAGMA user_version').fetchone()[0] == 3
    with TestClient(create_app(database, tmp_path / 'courses')):
        pass
    assert len(list((tmp_path / 'backups').glob('*'))) == 2
