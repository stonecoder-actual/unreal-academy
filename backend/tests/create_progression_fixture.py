"""Create an isolated browser fixture; refuses to overwrite any database."""
import json
from pathlib import Path

from app.database import initialize, connect
from app.external import import_external
from app.guided import import_guide

root=Path('/fixtures')
database=root/'academy.sqlite3'
if database.exists():
    raise SystemExit('Fixture already exists; use a new isolated directory')
(root/'courses').mkdir(parents=True,exist_ok=True)
initialize(database)
base='https://www.udemy.com/course/synthetic-guild/'
course=import_external(database,dict(slug='synthetic-guild',title='SYNTHETIC · Guild verification',url=base,
    lessons=[dict(external_id='1',title='1. Synthetic rank check',section='Synthetic only',url=base+'learn/lecture/1',
        transcript=dict(cues=['Synthetic test content. Not a purchased course.'],captured_at='2026-10-16T00:00:00Z'))]))
with connect(database) as db:
    lesson=db.execute('SELECT id FROM lessons WHERE course_id=?',(course['course_id'],)).fetchone()[0]
doc=dict(lesson_id=lesson,title='Synthetic rank check',overview='Isolated verification.',prerequisites=[],objectives=[],corrections=[],references=[],
    takeaways=['This is a synthetic test environment. No real learner data is used.'],practice=None,
    sections=[dict(id='checks',title='Checks',start=None,end=None,objective='Verify rewards',notes=[],pause_prompt='')],
    questions=[dict(id=f'check-{n}',section='checks',prompt=f'Synthetic check {n}: which choice verifies a correct answer?',
        options=['Correct test choice','Incorrect test choice'],correct=0,explanation='The correct synthetic choice earns XP once.',hint='Use the correct test choice.',xp=10) for n in range(3)])
guide=import_guide(database,root/'courses',doc)
with connect(database) as db:
    db.execute("INSERT INTO xp_transactions(award_key,guide_id,amount,reason) VALUES('synthetic-start',?,1230,'Synthetic balance only')",(guide,))
(root/'fixture.json').write_text(json.dumps(dict(lesson_id=lesson,guide_id=guide)))
print('Synthetic fixture created: 1230 XP, next rank at 1240 XP.')
