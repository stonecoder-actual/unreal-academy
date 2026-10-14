import copy
import json
import sqlite3
import subprocess
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from app.guided import import_guide
from app.main import create_app


@pytest.fixture
def guided(tmp_path):
    root = tmp_path / 'courses'
    folder = root / 'Test course'
    folder.mkdir(parents=True)
    subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=blue:s=160x90:d=3',
                    '-c:v','libx264','-pix_fmt','yuv420p',str(folder / 'Lesson.mp4')], check=True)
    (folder / 'Lesson.srt').write_text('1\n00:00:00,000 --> 00:00:02,000\nTest.\n')
    database = tmp_path / 'academy.sqlite3'
    with TestClient(create_app(database, root)) as client:
        course_id = client.post('/api/courses/import',json={'folder':'Test course'}).json()['course_id']
        lesson_id = client.get('/api/courses/'+course_id).json()['lessons'][0]['id']
    document = {'lesson_id':lesson_id, 'title':'Test mission', 'overview':'A test guide.',
                'prerequisites':[], 'objectives':['Explain a prediction.'], 'corrections':[], 'references':[],
                'sections':[{'id':'first','title':'First','start':0,'end':2,'objective':'Predict','notes':[], 'pause_prompt':'Think'}],
                'questions':[{'id':'test-question','section':'first','prompt':'Which is the test answer?',
                              'options':['A valid answer','A wrong answer'],'correct':0,'explanation':'A reason.', 'hint':'Think.', 'xp':10}],
                'practice':{'title':'Test task','estimated_minutes':10,'steps':['Build'], 'criteria':['Explain'], 'troubleshooting':[], 'xp':60}}
    guide_id = import_guide(database, root, document)
    return database, root, document, guide_id


def publish(client, guide_id):
    assert client.post(f'/api/parent/guides/{guide_id}/publish').status_code == 200


def test_draft_review_answers_rewards_and_restart(guided):
    database, root, document, guide_id = guided
    answer_url = f'/api/guides/{guide_id}/questions/test-question/answer'
    with TestClient(create_app(database, root)) as client:
        assert client.get(f"/api/lessons/{document['lesson_id']}/guide").json() is None
        assert client.post(answer_url,json={'answer':'A valid answer'}).status_code == 404
        assert client.get('/api/parent/guides').json()[0]['status'] == 'draft'
        client.put(f"/api/lessons/{document['lesson_id']}/progress", json={'position':2,'watched':True})
        assert client.get('/api/xp').json()['total_xp'] == 0
        publish(client, guide_id)
        guide = client.get(f"/api/lessons/{document['lesson_id']}/guide").json()
        assert 'correct' not in guide['document']['questions'][0]
        assert 'explanation' not in guide['document']['questions'][0]
        wrong = client.post(answer_url,json={'answer':'A wrong answer'}).json()
        assert wrong['correct'] is False and wrong['awarded_xp'] == 0
        correct = client.post(answer_url,json={'answer':'A valid answer'}).json()
        assert correct['correct'] and correct['awarded_xp'] == 10
        assert client.post(answer_url,json={'answer':'A valid answer'}).json()['awarded_xp'] == 0
        assert client.post(answer_url,json={'answer':'A valid answer','xp':9999}).status_code == 422
        assert client.post(answer_url,json={'answer':'not an option'}).status_code == 400
    with TestClient(create_app(database, root)) as client:
        assert client.get('/api/xp').json()['total_xp'] == 10
        assert client.get(f"/api/lessons/{document['lesson_id']}/guide").json()['solved'] == ['test-question']
        assert client.post(answer_url,json={'answer':'A valid answer'}).json()['awarded_xp'] == 0


def test_concurrent_correct_answers_award_once(guided):
    database, root, _, guide_id = guided
    with TestClient(create_app(database, root)) as client:
        publish(client, guide_id)
        with ThreadPoolExecutor(max_workers=6) as pool:
            results = list(pool.map(lambda _: client.post(f'/api/guides/{guide_id}/questions/test-question/answer',json={'answer':'A valid answer'}).json(), range(12)))
        assert sum(r['awarded_xp'] for r in results) == 10
        assert client.get('/api/xp').json()['total_xp'] == 10


def test_practice_feedback_and_idempotent_approval(guided):
    database, root, document, guide_id = guided
    evidence = {'prediction':'I predict that the child follows its parent.',
                'observation':'I observed the child following the parent.',
                'explanation':'The child inherits its parent transform.'}
    with TestClient(create_app(database, root)) as client:
        publish(client, guide_id)
        assert client.post(f'/api/guides/{guide_id}/practice',json={}).status_code == 422
        first = client.post(f'/api/guides/{guide_id}/practice',json=evidence).json()
        assert first['awarded_xp'] == 0
        assert client.post(f'/api/guides/{guide_id}/practice',json=evidence).status_code == 409
        review_url = f"/api/parent/submissions/{first['id']}/review"
        client.post(review_url,json={'decision':'changes_requested','feedback':'Please demonstrate the spawn setting too.'})
        second = client.post(f'/api/guides/{guide_id}/practice',json=evidence).json()
        review_url = f"/api/parent/submissions/{second['id']}/review"
        assert client.post(review_url,json={'decision':'approved','feedback':'I checked the editor and each criterion.'}).json()['awarded_xp'] == 60
        assert client.post(review_url,json={'decision':'approved','feedback':'I checked the editor again.'}).json()['awarded_xp'] == 0
        assert client.get('/api/xp').json()['total_xp'] == 60
        assert client.get(f"/api/lessons/{document['lesson_id']}/guide").json()['submission']['status'] == 'approved'


def test_source_change_and_immutable_published_content(guided):
    database, root, document, guide_id = guided
    with TestClient(create_app(database, root)) as client:
        publish(client, guide_id)
        changed = copy.deepcopy(document)
        changed['questions'][0]['xp'] = 90
        with pytest.raises(ValueError,match='immutable'):
            import_guide(database, root, changed)
        (root / 'Test course' / 'Lesson.srt').write_text('Changed subtitles')
        assert client.get(f"/api/lessons/{document['lesson_id']}/guide").status_code == 409
        assert client.post(f'/api/guides/{guide_id}/questions/test-question/answer',json={'answer':'A valid answer'}).status_code == 409
        assert client.get('/api/parent/guides').json()[0]['source_error']
        assert client.get('/api/xp').json()['total_xp'] == 0


def test_migration_preserves_phase_two_and_level_boundary(guided):
    database, root, _, guide_id = guided
    with sqlite3.connect(database) as db:
        assert db.execute('PRAGMA user_version').fetchone()[0] == 3
        db.execute('INSERT INTO xp_transactions(award_key,guide_id,amount,reason) VALUES(?,?,?,?)', ('test-boundary',guide_id,100,'Test boundary'))
    with TestClient(create_app(database, root)) as client:
        summary = client.get('/api/xp').json()
        assert summary['level'] == 2 and summary['level_xp'] == 0 and summary['xp_to_next_level'] == 100
        assert len(client.get('/api/courses').json()) == 1
    backup = next((database.parent / 'backups').glob('pre-v3-*.sqlite3'))
    with sqlite3.connect(backup) as db:
        assert db.execute('PRAGMA user_version').fetchone()[0] == 2


def test_real_phase_two_progress_survives_upgrade(tmp_path):
    from pathlib import Path
    database = tmp_path / 'academy.sqlite3'
    with sqlite3.connect(database) as db:
        db.executescript(Path('app/schema.sql').read_text())
        db.executescript(Path('app/migration_002.sql').read_text())
        db.execute("INSERT INTO courses(id,folder,title) VALUES('course','Folder','Existing course')")
        db.execute("INSERT INTO lessons(id,course_id,relative_path,title,content_hash,file_size,modified_ns) VALUES('lesson','course','video.mp4','Existing lesson','hash',10,1)")
        db.execute("INSERT INTO lesson_progress(lesson_id,position,watched) VALUES('lesson',42,1)")
    with TestClient(create_app(database,tmp_path/'courses')) as client:
        lesson=client.get('/api/courses/course').json()['lessons'][0]
        assert lesson['position']==42 and lesson['watched']==1
        assert client.get('/api/xp').json()['total_xp']==0
    backup = next((tmp_path/'backups').glob('pre-v3-*.sqlite3'))
    with sqlite3.connect(backup) as db:
        assert db.execute("SELECT position FROM lesson_progress WHERE lesson_id='lesson'").fetchone()[0]==42
