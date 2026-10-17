import copy
import json
import sqlite3

import pytest
from fastapi.testclient import TestClient

from app import bundled
from app.database import connect, initialize
from app.external import import_external
from app.main import create_app
from app.maintenance import fingerprint, open_readonly


@pytest.fixture
def shipped(monkeypatch):
    monkeypatch.setenv('ACADEMY_BUNDLED_CURRICULUM', '1')
    monkeypatch.setenv('ACADEMY_UDEMY_ONLY', '1')
    return json.loads(bundled.BUNDLE.read_text(encoding='utf-8'))


def test_fresh_install_has_complete_udemy_curriculum_without_private_data(tmp_path, shipped):
    path = tmp_path/'academy.sqlite3'
    with TestClient(create_app(path)) as client:
        courses = client.get('/api/courses').json()
        assert len(courses) == 1 and courses[0]['source_type'] == 'udemy'
        assert courses[0]['lesson_count'] == 221
        index = client.get('/api/guided-lessons').json()
        assert len(index) == 207
        questions = 0
        for guide in index:
            response = client.get(f"/api/lessons/{guide['lesson_id']}/guide")
            assert response.status_code == 200
            public = response.json()
            doc = public['document']
            questions += len(doc['questions'])
            assert doc['takeaways'] and doc['practice'] is None
            assert 3 <= len(doc['questions']) <= 6
            assert all('correct' not in q and 'explanation' not in q for q in doc['questions'])
            assert public['solved'] == []
        assert questions == 890 and client.get('/api/xp').json()['total_xp'] == 0
        mastery = client.get('/api/progression').json()['mastery']
        assert mastery['authored_videos'] == mastery['videos'] == 207
        assert mastery['planned_checks'] == 890
        assert mastery['finalized'] is False
    with connect(path) as db:
        assert db.execute('SELECT COUNT(*) FROM lesson_transcripts').fetchone()[0] == 0
        assert db.execute('PRAGMA user_version').fetchone()[0] == 6


def test_curriculum_update_preserves_answers_xp_playback_equipment_and_ids(tmp_path, shipped, monkeypatch):
    path = tmp_path/'academy.sqlite3'
    # An independently imported catalogue must be matched by external identity.
    initialize(path)
    imported = import_external(path, shipped['course'])
    with connect(path) as db:
        original_lessons = dict(db.execute('SELECT external_id,id FROM lessons'))
    identity = next(iter(shipped['guides']))
    document = shipped['guides'][identity]
    question = document['questions'][0]
    lesson_id = original_lessons[identity]
    url = f'/api/lessons/{lesson_id}/guide'
    with TestClient(create_app(path)) as client:
        assert client.get('/api/courses').json()[0]['id'] == imported['course_id']
        guide_id = client.get(url).json()['id']
        endpoint = f"/api/guides/{guide_id}/questions/{question['id']}/answer"
        answer = {'answer':question['options'][question['correct']]}
        assert client.post(endpoint, json=answer).json()['awarded_xp'] == question['xp']
        client.put(f'/api/lessons/{lesson_id}/progress', json={'position':21,'watched':True}).raise_for_status()
        client.put('/api/settings', json={'welcome_message':'Local persistence sentinel'}).raise_for_status()
        client.put('/api/progression/equipment', json={'title_id':'newbie','icon_id':'newbie'}).raise_for_status()
    with open_readonly(path) as db:
        before = fingerprint(db)
    revised = copy.deepcopy(shipped)
    revised['guides'][identity]['questions'][0]['explanation'] += ' A revised explanation.'
    package = tmp_path/'updated.json'
    package.write_text(json.dumps(revised), encoding='utf-8')
    monkeypatch.setattr(bundled, 'BUNDLE', package)
    with TestClient(create_app(path)) as client:
        public = client.get(url).json()
        assert public['id'] == guide_id and question['id'] in public['solved']
        assert client.get('/api/xp').json()['total_xp'] == question['xp']
        with open_readonly(path) as db:
            assert fingerprint(db) == before
        retry = client.post(endpoint, json=answer).json()
        assert retry['awarded_xp'] == 0 and retry['explanation'].endswith('A revised explanation.')
    with TestClient(create_app(path)) as client:
        assert client.get(url).json()['id'] == guide_id
        assert client.get('/api/xp').json()['total_xp'] == question['xp']
    with connect(path) as db:
        assert dict(db.execute('SELECT external_id,id FROM lessons')) == original_lessons
        assert db.execute('SELECT COUNT(*) FROM courses').fetchone()[0] == 1
    assert list((tmp_path/'backups/guides').glob('*.json'))


def test_hidden_local_course_and_progress_are_retained(tmp_path, shipped):
    path = tmp_path/'academy.sqlite3'
    initialize(path)
    with connect(path) as db:
        db.execute("INSERT INTO courses(id,folder,title) VALUES('local','local','Paused local course')")
        db.execute("INSERT INTO lessons(id,course_id,relative_path,title,content_hash,file_size,modified_ns,available,item_kind) VALUES('local-video','local','01.mp4','Paused video','hash',1,1,1,'video')")
        db.execute("INSERT INTO lesson_progress(lesson_id,position,watched) VALUES('local-video',12,1)")
        db.execute("INSERT INTO mastery_plan(lesson_id,course_id) VALUES('local-video','local')")
    with TestClient(create_app(path)) as client:
        assert all(c['source_type'] == 'udemy' for c in client.get('/api/courses').json())
        assert client.get('/api/courses/local').status_code == 404
        track = client.get('/api/progression').json()['mastery']
        assert track['paused_courses'] == 1
        assert len(track['courses']) == 1
        assert track['videos'] == 208  # Hiding must not silently shrink mastery.
    with connect(path) as db:
        assert db.execute("SELECT position,watched FROM lesson_progress WHERE lesson_id='local-video'").fetchone()[:] == (12,1)
        assert db.execute("SELECT COUNT(*) FROM courses WHERE id='local'").fetchone()[0] == 1


def test_invalid_bundle_fails_before_catalogue_changes(tmp_path, shipped):
    path = tmp_path/'academy.sqlite3'
    initialize(path)
    shipped['guides'].pop(next(iter(shipped['guides'])))
    invalid = tmp_path/'invalid.json'
    invalid.write_text(json.dumps(shipped), encoding='utf-8')
    with pytest.raises(ValueError, match='Every bundled video'):
        bundled.sync_curriculum(path, tmp_path, invalid)
    with connect(path) as db:
        assert db.execute('SELECT COUNT(*) FROM courses').fetchone()[0] == 0


def test_late_import_failure_rolls_back_the_entire_package(tmp_path, shipped):
    path = tmp_path/'academy.sqlite3'
    initialize(path)
    # This passes outer document validation, then fails the section-time guard.
    identity = list(shipped['guides'])[-1]
    shipped['guides'][identity]['sections'][0].update(start=10, end=5)
    invalid = tmp_path/'late-invalid.json'
    invalid.write_text(json.dumps(shipped), encoding='utf-8')
    with pytest.raises(ValueError, match='Section times'):
        bundled.sync_curriculum(path, tmp_path, invalid)
    with connect(path) as db:
        for table in ('courses','lessons','guided_lessons','bundled_lesson_sources'):
            assert db.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0] == 0
