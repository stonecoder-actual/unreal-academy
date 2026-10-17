import json
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.database import initialize, connect
from app.main import create_app
from app.maintenance import backup, verify
from app.progression import threshold, xp_summary


@pytest.fixture
def academy(tmp_path):
    path = tmp_path / 'academy.sqlite3'
    initialize(path)
    with connect(path) as db:
        for name in ('a','b'):
            db.execute('INSERT INTO courses(id,folder,title,source_type) VALUES(?,?,?,?)',(name,name,'Synthetic '+name,'udemy'))
            db.execute('''INSERT INTO lessons(id,course_id,relative_path,title,content_hash,file_size,modified_ns,external_url)
                VALUES(?,?,?,?,?,?,?,?)''',(name,name,'lecture:'+name,'Synthetic '+name,'video',1,1,'https://www.udemy.com/course/synthetic/learn/lecture/'+name))
            db.execute('INSERT INTO lesson_transcripts(lesson_id,cues,content_hash,captured_at,source_url) VALUES(?,?,?,?,?)',
                (name,'["Synthetic transcript"]','transcript','2026-01-01','https://www.udemy.com/'))
            document=dict(lesson_id=name,title='Synthetic',takeaways=['Synthetic fact.'],overview='Synthetic test only.',prerequisites=[],objectives=[],corrections=[],references=[],
                sections=[dict(id='checks',title='Checks',start=None,end=None,objective='Test',notes=[],pause_prompt='')],practice=None,
                questions=[dict(id=f'q-{n}',section='checks',prompt='Which synthetic option is correct?',options=['Correct','Wrong'],correct=0,explanation='Synthetic reason.',hint='Synthetic hint.',xp=10) for n in range(4)])
            db.execute("INSERT INTO guided_lessons(id,lesson_id,status,document,video_hash,subtitle_hash) VALUES(?,?,'published',?,'video','transcript')",('g-'+name,name,json.dumps(document)))
    return path


def give_xp(path, amount):
    with connect(path) as db:
        db.execute("INSERT INTO xp_transactions(award_key,guide_id,amount,reason) VALUES('synthetic-balance','g-a',?,'Synthetic only')",(amount,))


@pytest.mark.parametrize('xp,level,left',[(0,1,50),(49,1,1),(50,2,70),(119,2,1),(120,3,100),(28319,49,1),(28320,50,0),(50000,50,0)])
def test_curve_boundaries_and_cap(academy,xp,level,left):
    if xp: give_xp(academy,xp)
    with connect(academy) as db:
        result=xp_summary(db)
    assert result['level']==level and result['xp_to_next_level']==left
    assert result['total_xp']==xp
    assert result['at_max_level']==(level==50)


def test_milestones_and_increasing_level_cost():
    assert [threshold(n) for n in (1,3,5,10,15,20,25,30,40,50)] == [0,120,330,1240,2700,4710,7270,10380,18250,28320]
    costs=[threshold(n+1)-threshold(n) for n in range(1,50)]
    assert costs==sorted(costs) and all(c>0 for c in costs)


def test_equipment_is_independent_persistent_and_cannot_equip_locked(academy):
    give_xp(academy,1240)
    with TestClient(create_app(academy)) as client:
        result=client.get('/api/progression').json()
        assert result['highest_rank']['id']=='apprentice'
        assert result['equipped_title']['id']=='apprentice'
        assert client.put('/api/progression/equipment',json={'title_id':'unreal-master'}).status_code==403
        assert client.put('/api/progression/equipment',json={'evil_column':'newbie'}).status_code==422
        assert client.put('/api/progression/equipment',json={'title_id':"x'; DROP TABLE settings;--"}).status_code==403
        result=client.put('/api/progression/equipment',json={'title_id':'newbie','icon_id':'novice'}).json()
        assert result['equipped_title']['id']=='newbie' and result['equipped_icon']['id']=='novice'
        original_dates={r['id']:r['unlocked_at'] for r in result['ranks'] if r['unlocked']}
    with TestClient(create_app(academy)) as client:
        result=client.get('/api/progression').json()
        assert result['total_xp']==1240 and result['equipped_icon']['id']=='novice'
        assert {r['id']:r['unlocked_at'] for r in result['ranks'] if r['unlocked']}==original_dates
        assert client.put('/api/progression/equipment',json={'title_id':None,'icon_id':None}).json()['equipped_title']['id']=='apprentice'


def test_mastery_requires_whole_track_breadth_finalization_and_level(academy):
    with TestClient(create_app(academy)) as client:
        assert client.post('/api/parent/progression/finalize').status_code==200
        # All four from A and two from B: 75% overall, but B also below 75%.
        for name,count in [('a',4),('b',2)]:
            for n in range(count): client.post(f'/api/guides/g-{name}/questions/q-{n}/answer',json={'answer':'Correct'})
        result=client.get('/api/progression').json()
        assert not result['mastery']['eligible']
        give_xp(academy,28320)
        assert not client.get('/api/progression').json()['ranks'][-1]['unlocked']
        client.post('/api/guides/g-b/questions/q-2/answer',json={'answer':'Correct'})
        result=client.get('/api/progression').json()
        assert result['mastery']['overall_percent']==87.5
        assert result['mastery']['eligible'] and result['highest_rank']['id']=='unreal-master'
        # Earned Master remains unlocked even after a source becomes unavailable.
        with connect(academy) as db: db.execute("UPDATE lessons SET available=0 WHERE id='b'")
        assert client.get('/api/progression').json()['highest_rank']['id']=='unreal-master'


def test_high_xp_alone_cannot_unlock_master_or_draft_finalization(academy):
    give_xp(academy,50000)
    with connect(academy) as db:
        db.execute("INSERT INTO lessons(id,course_id,relative_path,title,content_hash,file_size,modified_ns) VALUES('pending','a','pending.mp4','Pending','h',1,1)")
    with TestClient(create_app(academy)) as client:
        result=client.get('/api/progression').json()
        assert result['level']==50 and result['highest_rank']['id']=='unreal-expert'
        assert result['mastery']['videos']==3 and result['mastery']['planned_checks']==13
        assert not result['mastery']['ready_to_finalize']
        assert client.post('/api/parent/progression/finalize').status_code==409
        assert not client.get('/api/progression').json()['ranks'][-1]['unlocked']
        with connect(academy) as db: db.execute("UPDATE lessons SET available=0 WHERE id='pending'")
        assert client.get('/api/progression').json()['mastery']['videos']==3


def test_large_course_cannot_mask_low_completion_in_another(academy):
    # Five equal lessons in A, one in B: 22/24 solved overall, but B only 50%.
    with connect(academy) as db:
        original=json.loads(db.execute("SELECT document FROM guided_lessons WHERE id='g-a'").fetchone()[0])
        for n in range(4):
            name=f'added-{n}'
            db.execute("INSERT INTO lessons(id,course_id,relative_path,title,content_hash,file_size,modified_ns,external_url) VALUES(?,'a',?,'Synthetic','video',1,1,'https://www.udemy.com/')",(name,name))
            db.execute("INSERT INTO lesson_transcripts VALUES(?,'[]','transcript','2026-01-01','https://www.udemy.com/')",(name,))
            original['lesson_id']=name
            db.execute("INSERT INTO guided_lessons(id,lesson_id,status,document,video_hash,subtitle_hash) VALUES(?,?,'published',?,'video','transcript')",('g-'+name,name,json.dumps(original)))
        for guide in ['g-a']+[f'g-added-{n}' for n in range(4)]+['g-b']:
            for n in range(2 if guide=='g-b' else 4):
                db.execute('INSERT INTO xp_transactions(award_key,guide_id,amount,reason) VALUES(?,?,10,?)',(f'question:{guide}:q-{n}',guide,'Synthetic'))
    give_xp(academy,28320)
    with TestClient(create_app(academy)) as client:
        client.post('/api/parent/progression/finalize')
        result=client.get('/api/progression').json()
        assert result['mastery']['overall_percent']>85
        assert not result['mastery']['eligible'] and not result['ranks'][-1]['unlocked']


def test_xp_unlocks_once_at_answer_and_retries_do_not_farm(academy):
    give_xp(academy,110)
    with TestClient(create_app(academy)) as client:
        url='/api/guides/g-a/questions/q-0/answer'
        assert client.post(url,json={'answer':'Wrong'}).json()['awarded_xp']==0
        assert client.post(url,json={'answer':'Correct'}).json()['awarded_xp']==10
        with connect(academy) as db:
            assert db.execute("SELECT COUNT(*) FROM progression_unlocks WHERE rank_id='beginner'").fetchone()[0]==1
        assert client.post(url,json={'answer':'Correct'}).json()['awarded_xp']==0
        assert client.get('/api/xp').json()['total_xp']==120


def test_finalized_track_does_not_expand_with_later_courses(academy):
    with TestClient(create_app(academy)) as client:
        assert client.post('/api/parent/progression/finalize').status_code==200
        with connect(academy) as db:
            db.execute("INSERT INTO lessons(id,course_id,relative_path,title,content_hash,file_size,modified_ns) VALUES('later','a','later.mp4','Later','h',1,1)")
        assert client.get('/api/progression').json()['mastery']['videos']==2


def test_v4_migration_preserves_records_and_snapshot(academy,tmp_path):
    # Construct a genuine version 4 database without any progression tables.
    old=tmp_path/'old.sqlite3'
    app_dir=Path(__file__).parents[1]/'app'
    with sqlite3.connect(old) as db:
        for file in ['schema.sql','migration_002.sql','migration_003.sql','migration_004.sql']:
            db.executescript((app_dir/file).read_text())
        db.execute("UPDATE settings SET value='Keep this' WHERE key='welcome_message'")
    saved=backup(old)
    initialize(old)
    assert verify(old,Path(saved['backup']).with_suffix('.json'))['verified']
    with sqlite3.connect(old) as db: assert db.execute('PRAGMA user_version').fetchone()[0]==6
    assert list((old.parent/'backups').glob('pre-v5-*.sqlite3'))
    # New cosmetic state is included in future deployment preservation checks.
    with TestClient(create_app(academy)) as client: client.get('/api/progression')
    saved=backup(academy)
    with connect(academy) as db: db.execute("UPDATE progression_equipment SET title_id='newbie' WHERE id=1")
    with pytest.raises(RuntimeError,match='progression_equipment'):
        verify(academy,Path(saved['backup']).with_suffix('.json'))
