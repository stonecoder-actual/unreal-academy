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


def test_reflection_kind_and_small_rewards(guided):
    database, root, document, guide_id = guided
    document = copy.deepcopy(document)
    document['practice'].update(kind='reflection', xp=15)
    document['questions'][0]['xp'] = 5
    assert import_guide(database, root, document) == guide_id
    with TestClient(create_app(database, root)) as client:
        assert client.get('/api/parent/guides').json()[0]['document']['practice']['kind'] == 'reflection'
        assert client.get(f"/api/lessons/{document['lesson_id']}/guide").json()['status'] == 'published'
        assert client.get('/api/xp').json()['total_xp'] == 0
        publish(client, guide_id)
        answer = f'/api/guides/{guide_id}/questions/test-question/answer'
        assert client.post(answer, json={'answer':'A wrong answer'}).json()['awarded_xp'] == 0
        assert client.post(answer, json={'answer':'A valid answer'}).json()['awarded_xp'] == 5
        assert client.post(answer, json={'answer':'A valid answer'}).json()['awarded_xp'] == 0
        evidence = {'prediction':'SYNTHETIC: choose a small learning goal.',
                    'observation':'SYNTHETIC: discuss a plan with a parent.',
                    'explanation':'SYNTHETIC: explain a useful improvement.'}
        result = client.post(f'/api/guides/{guide_id}/practice', json=evidence).json()
        assert result['awarded_xp'] == 0
        review = f"/api/parent/submissions/{result['id']}/review"
        assert client.post(review, json={'decision':'approved','feedback':'Synthetic reflection reviewed.'}).json()['awarded_xp'] == 15
        assert client.post(review, json={'decision':'approved','feedback':'Repeated synthetic review.'}).json()['awarded_xp'] == 0
    with TestClient(create_app(database, root)) as client:
        guide = client.get(f"/api/lessons/{document['lesson_id']}/guide").json()
        assert guide['document']['practice']['kind'] == 'reflection'
        assert guide['xp']['total_xp'] == 20


def test_legacy_published_guide_can_be_reimported_unchanged(guided):
    database, root, document, guide_id = guided
    with TestClient(create_app(database, root)) as client:
        publish(client, guide_id)
    # Published documents from before activity kinds had no kind field.
    with sqlite3.connect(database) as db:
        stored = json.loads(db.execute('SELECT document FROM guided_lessons WHERE id=?', (guide_id,)).fetchone()[0])
        stored['practice'].pop('kind', None)
        legacy_json = json.dumps(stored)
        db.execute('UPDATE guided_lessons SET document=? WHERE id=?', (legacy_json, guide_id))
    assert import_guide(database, root, document) == guide_id
    with sqlite3.connect(database) as db:
        assert db.execute('SELECT document FROM guided_lessons WHERE id=?', (guide_id,)).fetchone()[0] == legacy_json
    document['practice']['kind'] = 'reflection'
    assert import_guide(database, root, document) == guide_id


def test_unknown_activity_kind_rejected(guided):
    database, root, document, _ = guided
    document['practice']['kind'] = 'automatic-public-post'
    with pytest.raises(ValueError):
        import_guide(database, root, document)


def test_quiz_only_mission_completes_without_parent_or_written_work(guided):
    database, root, document, guide_id = guided
    document = copy.deepcopy(document)
    document['practice'] = None
    document['questions'] = [{**document['questions'][0], 'id':f'quiz-{index}', 'xp':5} for index in range(3)]
    assert import_guide(database, root, document) == guide_id
    url = f"/api/lessons/{document['lesson_id']}/guide"
    with TestClient(create_app(database, root)) as client:
        assert client.get(url).json()['status'] == 'published'
        publish(client, guide_id)
        assert client.get(url).json()['completed'] is False
        assert client.get(url).json()['document']['practice'] is None
        for index in range(3):
            answer = f'/api/guides/{guide_id}/questions/quiz-{index}/answer'
            assert client.post(answer,json={'answer':'A wrong answer'}).json()['awarded_xp'] == 0
            assert client.get(url).json()['completed'] is False
            assert client.post(answer,json={'answer':'A valid answer'}).json()['awarded_xp'] == 5
            assert client.post(answer,json={'answer':'A valid answer'}).json()['awarded_xp'] == 0
            assert client.get(url).json()['completed'] is (index == 2)
        evidence = {'prediction':'Synthetic unused written response.',
                    'observation':'Synthetic unused written response.',
                    'explanation':'Synthetic unused written response.'}
        assert client.post(f'/api/guides/{guide_id}/practice',json=evidence).status_code == 409
        assert client.get('/api/parent/submissions').json() == []
        assert client.get('/api/xp').json()['total_xp'] == 15
    with TestClient(create_app(database, root)) as client:
        guide = client.get(url).json()
        assert guide['completed'] is True
        assert guide['submission'] is None
        assert len(guide['solved']) == 3
        assert client.get('/api/xp').json()['total_xp'] == 15
        assert client.post(f'/api/guides/{guide_id}/questions/quiz-0/answer',json={'answer':'A valid answer'}).json()['awarded_xp'] == 0


def test_direct_publication_answers_rewards_and_restart(guided):
    database, root, document, guide_id = guided
    answer_url = f'/api/guides/{guide_id}/questions/test-question/answer'
    with TestClient(create_app(database, root)) as client:
        assert client.get(f"/api/lessons/{document['lesson_id']}/guide").json()['status'] == 'published'
        assert client.get('/api/parent/guides').json()[0]['status'] == 'published'
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


def test_source_change_blocks_until_direct_reimport(guided):
    database, root, document, guide_id = guided
    with TestClient(create_app(database, root)) as client:
        publish(client, guide_id)
        changed = copy.deepcopy(document)
        changed['questions'][0]['xp'] = 90
        assert import_guide(database, root, changed) == guide_id
        (root / 'Test course' / 'Lesson.srt').write_text('Changed subtitles')
        assert client.get(f"/api/lessons/{document['lesson_id']}/guide").status_code == 409
        assert client.post(f'/api/guides/{guide_id}/questions/test-question/answer',json={'answer':'A valid answer'}).status_code == 409
        assert client.get('/api/parent/guides').json()[0]['source_error']
        assert client.get('/api/xp').json()['total_xp'] == 0
        assert import_guide(database, root, changed) == guide_id
        assert client.get(f"/api/lessons/{document['lesson_id']}/guide").status_code == 200


def test_migration_preserves_phase_two_and_level_boundary(guided):
    database, root, _, guide_id = guided
    with sqlite3.connect(database) as db:
        assert db.execute('PRAGMA user_version').fetchone()[0] == 4
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


def test_corrections_preserve_progress_rewards_and_document_history(guided):
    database, root, document, guide_id = guided
    url = f"/api/lessons/{document['lesson_id']}/guide"
    answer = f'/api/guides/{guide_id}/questions/test-question/answer'
    with TestClient(create_app(database, root)) as client:
        client.put(f"/api/lessons/{document['lesson_id']}/progress", json={'position':2,'watched':True})
        assert client.post(answer,json={'answer':'A valid answer'}).json()['awarded_xp'] == 10
        # Even a guide with a practical task completes without a submission.
        assert client.get(url).json()['completed'] is True
        document['title'] = 'Corrected mission'
        document['questions'][0]['xp'] = 90
        assert import_guide(database,root,document) == guide_id
        assert client.get(url).json()['document']['title'] == 'Corrected mission'
        assert client.get(url).json()['solved'] == ['test-question']
        assert client.post(answer,json={'answer':'A valid answer'}).json()['awarded_xp'] == 0
        assert client.get('/api/xp').json()['total_xp'] == 10
        snapshots = list((database.parent/'backups'/'guides').glob('*.json'))
        archived = json.loads(snapshots[0].read_text())
        assert archived['id'] == guide_id
        assert json.loads(archived['document'])['title'] == 'Test mission'
        # Removing a check never erases its XP or counts it as a different check.
        document['questions'][0]['id'] = 'new-question'
        import_guide(database,root,document)
        assert client.get(url).json()['solved'] == []
        assert client.get(url).json()['completed'] is False
    with TestClient(create_app(database,root)) as client:
        assert client.get('/api/xp').json()['total_xp'] == 10
        course = client.get('/api/courses').json()[0]['id']
        lesson = client.get('/api/courses/'+course).json()['lessons'][0]
        assert lesson['position'] == 2 and lesson['watched'] == 1


def test_startup_releases_legacy_drafts_once_without_awarding_xp(guided):
    database, root, document, guide_id = guided
    with sqlite3.connect(database) as db:
        db.execute("UPDATE guided_lessons SET status='draft' WHERE id=?", (guide_id,))
    for _ in range(2):
        with TestClient(create_app(database,root)) as client:
            assert client.get(f"/api/lessons/{document['lesson_id']}/guide").json()['status'] == 'published'
            assert client.get('/api/xp').json()['total_xp'] == 0
    assert len(list((database.parent/'backups'/'guides').glob('pre-direct-publication-*.json'))) == 1
