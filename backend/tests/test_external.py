import copy
import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.guided import import_guide
from app.main import create_app


def manifest():
    base = 'https://www.udemy.com/course/test-blueprints/'
    return {'slug':'test-blueprints','title':'Test Blueprints','url':base,'difficulty':'Beginner',
            'lessons':[{'external_id':'123','title':'1. A synthetic lesson','section':'Section 1: Test',
                        'kind':'video','url':base+'learn/lecture/123','duration':120,
                        'transcript':{'cues':['Synthetic test transcript.','This is not purchased curriculum.'],
                                      'captured_at':'2026-10-15T00:00:00Z'}},
                       {'external_id':'456','title':'Reading','section':'Section 1: Test','kind':'article',
                        'url':base+'learn/lecture/456'},
                       {'external_id':'123','title':'Quiz','section':'Section 1: Test','kind':'quiz',
                        'url':base+'learn/quiz/123'}]}


def test_external_import_progress_rescan_and_restart(tmp_path):
    database=tmp_path/'academy.sqlite3'
    with TestClient(create_app(database)) as client:
        result=client.post('/api/parent/external-courses/import',json=manifest())
        assert result.status_code==200, result.text
        course_id=result.json()['course_id']
        assert result.json()['captured_transcripts']==1
        course=client.get('/api/courses/'+course_id).json()
        assert course['source_type']=='udemy' and len(course['lessons'])==3
        lesson=course['lessons'][0]
        assert lesson['transcript_status']=='captured'
        assert course['lessons'][1]['transcript_status']=='not_applicable'
        lesson_id=lesson['id']
        assert client.get(f'/api/lessons/{lesson_id}/video').status_code==409
        assert client.get(f'/api/lessons/{lesson_id}/captions').status_code==404
        assert client.get(f'/api/parent/lessons/{lesson_id}/transcript').json()['cues']==manifest()['lessons'][0]['transcript']['cues']
        client.put(f'/api/lessons/{lesson_id}/progress',json={'position':0,'watched':True})
        updated=manifest(); updated['lessons'][0]['title']='Renamed lesson'
        updated['lessons'][0].pop('transcript')
        assert client.post('/api/parent/external-courses/import',json=updated).json()['course_id']==course_id
        assert client.get('/api/xp').json()['total_xp']==0
    with TestClient(create_app(database)) as client:
        lesson=client.get('/api/courses/'+course_id).json()['lessons'][0]
        assert lesson['id']==lesson_id and lesson['watched']==1 and lesson['transcript_status']=='captured'
        assert client.get('/api/courses').json()[0]['watched_count']==1


@pytest.mark.parametrize('bad_url',[
    'javascript:alert(1)', 'http://www.udemy.com/course/test-blueprints/learn/lecture/123',
    'https://www.udemy.com.evil.test/course/test-blueprints/learn/lecture/123',
    'https://user:pass@www.udemy.com/course/test-blueprints/learn/lecture/123',
    'https://www.udemy.com/course/another-course/learn/lecture/123',
    'https://www.udemy.com/course/test-blueprints/learn/lecture/999',
    'https://www.udemy.com/course/test-blueprints/learn/lecture/123?token=secret'])
def test_external_url_validation(tmp_path,bad_url):
    with TestClient(create_app(tmp_path/'test.sqlite3')) as client:
        payload=manifest();payload['lessons'][0]['url']=bad_url
        assert client.post('/api/parent/external-courses/import',json=payload).status_code==422
        assert client.get('/api/courses').json()==[]


def test_external_guides_rewards_and_source_change(tmp_path):
    database=tmp_path/'test.sqlite3';root=tmp_path/'courses'
    with TestClient(create_app(database,root)) as client:
        cid=client.post('/api/parent/external-courses/import',json=manifest()).json()['course_id']
        lesson_id=client.get('/api/courses/'+cid).json()['lessons'][0]['id']
        document={'lesson_id':lesson_id,'title':'Synthetic lesson notes','overview':'Synthetic test only.',
                  'takeaways':['Understand the idea in this synthetic transcript.'],
                  'prerequisites':[],'objectives':['Explain.'],'corrections':[],'references':[],
                  'sections':[{'id':'test','title':'Discuss','start':None,'end':None,'objective':'Explain',
                               'notes':['A test note.'],'pause_prompt':'Why?'}],
                  'questions':[{'id':'test','section':'test','prompt':'Which synthetic answer is correct?',
                                'options':['Correct','Incorrect'],'correct':0,'explanation':'Test explanation.',
                                'hint':'Test hint.','xp':10}],
                  'practice':None}
        document['questions'] += [{**document['questions'][0], 'id':f'other-{index}'} for index in range(2)]
        gid=import_guide(database,root,document)
        assert client.get(f'/api/lessons/{lesson_id}/guide').json()['status']=='published'
        answer=f'/api/guides/{gid}/questions/test/answer'
        assert client.post(answer,json={'answer':'Incorrect'}).json()['awarded_xp']==0
        assert client.post(answer,json={'answer':'Correct'}).json()['awarded_xp']==10
        assert client.post(answer,json={'answer':'Correct'}).json()['awarded_xp']==0
        student=client.get(f'/api/lessons/{lesson_id}/guide').json()
        assert 'correct' not in student['document']['questions'][0]
        evidence={'prediction':'SYNTHETIC TEST ONLY prediction.','observation':'SYNTHETIC TEST ONLY observation.',
                  'explanation':'SYNTHETIC TEST ONLY explanation.'}
        assert client.post(f'/api/guides/{gid}/practice',json=evidence).status_code==409
    with TestClient(create_app(database,root)) as client:
        assert client.get('/api/xp').json()['total_xp']==10
        assert client.get(f'/api/lessons/{lesson_id}/guide').json()['solved']==['test']
        changed=manifest();changed['lessons'][0]['transcript']['cues']=['Changed transcript requires review.']
        client.post('/api/parent/external-courses/import',json=changed)
        assert client.post(answer,json={'answer':'Correct'}).status_code==409
        assert client.get('/api/parent/guides').json()[0]['source_error']
        assert import_guide(database,root,document)==gid
        assert client.get(f'/api/lessons/{lesson_id}/guide').status_code==200
        assert client.post(answer,json={'answer':'Correct'}).json()['awarded_xp']==0
        assert client.get('/api/xp').json()['total_xp']==10


@pytest.mark.parametrize('question_count,with_activity,takeaways,accepted', [
    (3,False,['A key idea from the transcript.'],True),
    (6,False,['A key idea from the transcript.'],True),
    (2,False,['A key idea from the transcript.'],False),
    (7,False,['A key idea from the transcript.'],False),
    (3,True,['A key idea from the transcript.'],False),
    (3,False,[],False),
    (3,False,['   '],False),
])
def test_udemy_notes_require_takeaways_three_to_six_checks_and_no_activities(tmp_path,question_count,with_activity,takeaways,accepted):
    database=tmp_path/'academy.sqlite3';root=tmp_path/'courses'
    with TestClient(create_app(database,root)) as client:
        cid=client.post('/api/parent/external-courses/import',json=manifest()).json()['course_id']
        lesson_id=client.get('/api/courses/'+cid).json()['lessons'][0]['id']
        document={'lesson_id':lesson_id,'title':'Lesson notes','overview':'Synthetic transcript only.',
                  'prerequisites':[],'objectives':[],'corrections':[],'references':[],
                  'takeaways':takeaways,
                  'sections':[{'id':'notes','title':'Key takeaways','objective':'Understand','notes':[], 'pause_prompt':''}],
                  'questions':[{'id':f'check-{i}','section':'notes','prompt':'Which answer matches this idea?',
                                'options':['Correct','Incorrect'],'correct':0,'explanation':'A reason.', 'hint':'Think.', 'xp':5}
                               for i in range(question_count)],
                  'practice':{'title':'Do not create this activity','estimated_minutes':5,'steps':['Build'],
                              'criteria':['Explain'],'troubleshooting':[],'xp':60} if with_activity else None}
        if not accepted:
            with pytest.raises(ValueError):
                import_guide(database,root,document)
            assert client.get(f'/api/lessons/{lesson_id}/guide').json() is None
            return
        gid=import_guide(database,root,document)
        for index in range(question_count):
            answer=f'/api/guides/{gid}/questions/check-{index}/answer'
            assert client.post(answer,json={'answer':'Correct'}).json()['awarded_xp']==5
        doc=client.get(f'/api/lessons/{lesson_id}/guide').json()
        assert doc['completed'] and doc['document']['takeaways']==takeaways
        assert doc['document']['practice'] is None
        assert len(doc['document']['questions'])==question_count
        # Correcting takeaways/questions never awards existing checks again.
        document['takeaways']=['Corrected transcript-based takeaway.']
        document['questions']=document['questions'][:3]
        assert import_guide(database,root,document)==gid
        assert client.get('/api/xp').json()['total_xp']==question_count*5
        assert client.post(f'/api/guides/{gid}/questions/check-0/answer',json={'answer':'Correct'}).json()['awarded_xp']==0


def test_udemy_course_is_first_before_alphabetically_earlier_local_courses(tmp_path):
    database=tmp_path/'academy.sqlite3'
    with TestClient(create_app(database)) as client:
        with sqlite3.connect(database) as db:
            db.execute("INSERT INTO courses(id,folder,title) VALUES('local','Local','AAA local course')")
        payload=manifest()
        client.post('/api/parent/external-courses/import',json=payload)
        preferred=manifest()
        preferred.update(slug='ue5-ultimate-bp-course',title='ZZZ preferred Udemy',url='https://www.udemy.com/course/ue5-ultimate-bp-course/')
        for lesson in preferred['lessons']:
            lesson['url']=lesson['url'].replace('/test-blueprints/', '/ue5-ultimate-bp-course/')
        assert client.post('/api/parent/external-courses/import',json=preferred).status_code==200
        courses=client.get('/api/courses').json()
        assert courses[0]['folder']=='udemy:ue5-ultimate-bp-course'
        assert courses[1]['source_type']=='udemy'
        assert courses[2]['id']=='local'


def test_external_rejects_duplicate_and_blank_transcripts(tmp_path):
    with TestClient(create_app(tmp_path/'test.sqlite3')) as client:
        payload=manifest();payload['lessons'].append(copy.deepcopy(payload['lessons'][0]))
        assert client.post('/api/parent/external-courses/import',json=payload).status_code==422
        payload=manifest();payload['lessons'][0]['transcript']['cues']=['   ']
        assert client.post('/api/parent/external-courses/import',json=payload).status_code==422


def test_v4_migration_preserves_existing_data_with_backup(tmp_path):
    database=tmp_path/'test.sqlite3'
    app_dir=__import__('pathlib').Path(__file__).parents[1]/'app'
    with sqlite3.connect(database) as db:
        for script in ('schema.sql','migration_002.sql','migration_003.sql'):
            db.executescript((app_dir/script).read_text())
        db.execute("UPDATE settings SET value='Keep my message' WHERE key='welcome_message'")
        db.execute("INSERT INTO courses(id,folder,title) VALUES('existing','Existing course','Existing')")
        db.execute("INSERT INTO lessons(id,course_id,relative_path,title,content_hash,file_size,modified_ns) VALUES('lesson','existing','a.mp4','Old','hash',1,1)")
        db.execute("INSERT INTO lesson_progress(lesson_id,position,watched) VALUES('lesson',12.5,1)")
    with TestClient(create_app(database)) as client:
        assert client.get('/api/settings').json()['welcome_message']=='Keep my message'
        assert client.get('/api/courses/existing').json()['lessons'][0]['position']==12.5
    backups=list((tmp_path/'backups').glob('pre-v4-*.sqlite3'))
    assert len(backups)==1
    with sqlite3.connect(backups[0]) as db:
        assert db.execute('PRAGMA user_version').fetchone()[0]==3
    with sqlite3.connect(database) as db:
        assert db.execute('PRAGMA user_version').fetchone()[0]==4
