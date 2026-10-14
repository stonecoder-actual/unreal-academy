import hashlib
import json
import os
import uuid
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from .database import connect, initialize
from .library import safe_path


class Question(BaseModel):
    id: str = Field(pattern=r'^[a-z0-9-]+$', max_length=80)
    section: str
    prompt: str = Field(min_length=10, max_length=1500)
    options: list[str] = Field(min_length=2, max_length=6)
    correct: int = Field(ge=0)
    explanation: str
    hint: str
    xp: int = Field(default=10, ge=1, le=100)


class Section(BaseModel):
    id: str
    title: str
    start: float = Field(ge=0, allow_inf_nan=False)
    end: float = Field(gt=0, allow_inf_nan=False)
    objective: str
    notes: list[str]
    pause_prompt: str


class Practice(BaseModel):
    title: str
    estimated_minutes: int
    steps: list[str]
    criteria: list[str]
    troubleshooting: list[str]
    xp: int = Field(default=60, ge=1, le=200)


class GuideDocument(BaseModel):
    lesson_id: str
    title: str
    overview: str
    prerequisites: list[str]
    objectives: list[str]
    corrections: list[str]
    references: list[dict[str, str]]
    sections: list[Section] = Field(min_length=1, max_length=30)
    questions: list[Question] = Field(min_length=1, max_length=100)
    practice: Practice


def source(db, lesson_id, root):
    row = db.execute('SELECT l.*,c.folder FROM lessons l JOIN courses c ON c.id=l.course_id WHERE l.id=?', (lesson_id,)).fetchone()
    if not row or not row['available'] or not row['caption_path']:
        raise HTTPException(409, 'This guide needs an available lesson and matching subtitles')
    subtitle = safe_path(root, f"{row['folder']}/{row['caption_path']}")
    video = safe_path(root, f"{row['folder']}/{row['relative_path']}")
    try:
        stat = video.stat()
        if stat.st_size != row['file_size'] or stat.st_mtime_ns != row['modified_ns']:
            raise HTTPException(409, 'Video changed; rescan and review the guided lesson')
        return row['content_hash'], hashlib.sha256(subtitle.read_bytes()).hexdigest(), row['duration']
    except OSError as error:
        raise HTTPException(409, 'Source files are missing or unreadable') from error


def import_guide(database, root, document):
    parsed = GuideDocument.model_validate(document)
    section_ids = [s.id for s in parsed.sections]
    ids = [q.id for q in parsed.questions]
    if len(set(ids)) != len(ids) or len(set(section_ids)) != len(section_ids):
        raise ValueError('Question and section IDs must be unique')
    if any(q.correct >= len(q.options) or q.section not in section_ids for q in parsed.questions):
        raise ValueError('Question answer or section is invalid')
    with connect(database) as db:
        video_hash, subtitle_hash, duration = source(db, parsed.lesson_id, root)
        if any(s.end <= s.start or (duration and s.end > duration + 1) for s in parsed.sections):
            raise ValueError('Section times are outside the lesson')
        doc = parsed.model_dump_json()
        existing = db.execute('SELECT * FROM guided_lessons WHERE lesson_id=?', (parsed.lesson_id,)).fetchone()
        if existing:
            if existing['document'] == doc and existing['video_hash'] == video_hash and existing['subtitle_hash'] == subtitle_hash:
                return existing['id']
            if existing['status'] == 'published':
                raise ValueError('Published guides are immutable; use a reviewed revision workflow')
            db.execute('UPDATE guided_lessons SET document=?,video_hash=?,subtitle_hash=? WHERE id=?', (doc, video_hash, subtitle_hash, existing['id']))
            return existing['id']
        guide_id = str(uuid.uuid4())
        db.execute('INSERT INTO guided_lessons(id,lesson_id,status,document,video_hash,subtitle_hash) VALUES(?,?,\'draft\',?,?,?)',
                   (guide_id, parsed.lesson_id, doc, video_hash, subtitle_hash))
        return guide_id


def xp_summary(db):
    total = db.execute('SELECT COALESCE(SUM(amount),0) FROM xp_transactions').fetchone()[0]
    step = int(db.execute("SELECT value FROM settings WHERE key='xp_per_level'").fetchone()[0])
    level = total // step + 1
    return {'total_xp': total, 'level': level, 'level_xp': total % step,
            'xp_per_level': step, 'xp_to_next_level': step - total % step}


class Answer(BaseModel):
    model_config = ConfigDict(extra='forbid')
    answer: str = Field(max_length=1500)


class Evidence(BaseModel):
    model_config = ConfigDict(extra='forbid')
    prediction: str = Field(min_length=20, max_length=2000)
    observation: str = Field(min_length=20, max_length=2000)
    explanation: str = Field(min_length=20, max_length=2000)


class Review(BaseModel):
    decision: Literal['approved', 'changes_requested']
    feedback: str = Field(min_length=5, max_length=2000)


def create_guided_router(database, root):
    router = APIRouter(prefix='/api')

    def get_guide(db, guide_id, published=True):
        row = db.execute('SELECT * FROM guided_lessons WHERE id=?', (guide_id,)).fetchone()
        if not row or (published and row['status'] != 'published'):
            raise HTTPException(404, 'Published guided lesson not found')
        video_hash, subtitle_hash, _ = source(db, row['lesson_id'], root)
        if (video_hash, subtitle_hash) != (row['video_hash'], row['subtitle_hash']):
            raise HTTPException(409, 'Source changed; this guide needs parent review before use')
        return row, json.loads(row['document'])

    @router.get('/xp')
    def xp():
        with connect(database) as db:
            return xp_summary(db)

    @router.get('/guided-lessons')
    def list_guides():
        with connect(database) as db:
            return [dict(r) for r in db.execute("SELECT g.id,g.lesson_id,g.status,l.course_id FROM guided_lessons g JOIN lessons l ON l.id=g.lesson_id WHERE g.status='published'")]

    @router.get('/lessons/{lesson_id}/guide')
    def student_guide(lesson_id: str):
        with connect(database) as db:
            row = db.execute("SELECT id FROM guided_lessons WHERE lesson_id=? AND status='published'", (lesson_id,)).fetchone()
            if not row:
                return None
            guide, doc = get_guide(db, row['id'])
            solved = [r[0].split(':', 2)[-1] for r in db.execute("SELECT award_key FROM xp_transactions WHERE guide_id=? AND award_key LIKE 'question:%'", (guide['id'],))]
            latest = db.execute('SELECT * FROM practice_submissions WHERE guide_id=? ORDER BY created_at DESC,rowid DESC LIMIT 1', (guide['id'],)).fetchone()
            return {'id': guide['id'], 'status': guide['status'], 'document': {**doc, 'questions': [{k:v for k,v in q.items() if k not in ('correct','explanation')} for q in doc['questions']]},
                    'solved': solved, 'submission': dict(latest) if latest else None, 'xp': xp_summary(db)}

    @router.post('/guides/{guide_id}/questions/{question_id}/answer')
    def answer_question(guide_id: str, question_id: str, payload: Answer):
        with connect(database) as db:
            db.execute('BEGIN IMMEDIATE')
            guide, doc = get_guide(db, guide_id)
            question = next((q for q in doc['questions'] if q['id'] == question_id), None)
            if not question or payload.answer not in question['options']:
                raise HTTPException(400, 'Choose a valid answer to this question')
            correct = payload.answer == question['options'][question['correct']]
            db.execute('INSERT INTO quiz_attempts(guide_id,question_id,answer,correct) VALUES(?,?,?,?)', (guide_id, question_id, payload.answer, correct))
            awarded = 0
            if correct:
                inserted = db.execute('INSERT OR IGNORE INTO xp_transactions(award_key,guide_id,amount,reason) VALUES(?,?,?,?)',
                    (f'question:{guide_id}:{question_id}', guide_id, question['xp'], f"Knowledge check: {question_id}"))
                awarded = question['xp'] if inserted.rowcount else 0
            return {'correct': correct, 'awarded_xp': awarded, 'explanation': question['explanation'], 'xp': xp_summary(db)}

    @router.post('/guides/{guide_id}/practice')
    def submit_practice(guide_id: str, payload: Evidence):
        with connect(database) as db:
            db.execute('BEGIN IMMEDIATE')
            get_guide(db, guide_id)
            latest = db.execute('SELECT status FROM practice_submissions WHERE guide_id=? ORDER BY created_at DESC,rowid DESC LIMIT 1', (guide_id,)).fetchone()
            if latest and latest['status'] in ('pending','approved'):
                raise HTTPException(409, 'Your work is already awaiting review or approved')
            submission_id = str(uuid.uuid4())
            db.execute('INSERT INTO practice_submissions(id,guide_id,evidence) VALUES(?,?,?)', (submission_id, guide_id, payload.model_dump_json()))
            return {'id': submission_id, 'status':'pending', 'awarded_xp':0}

    @router.get('/parent/guides')
    def parent_guides():
        with connect(database) as db:
            result = []
            for row in db.execute('SELECT * FROM guided_lessons'):
                try:
                    get_guide(db, row['id'], published=False)
                    source_error = None
                except HTTPException as error:
                    source_error = error.detail
                result.append({**dict(row), 'document':json.loads(row['document']), 'source_error':source_error})
            return result

    @router.post('/parent/guides/{guide_id}/publish')
    def publish(guide_id: str):
        with connect(database) as db:
            get_guide(db, guide_id, published=False)
            db.execute("UPDATE guided_lessons SET status='published' WHERE id=?", (guide_id,))
        return {'status':'published'}

    @router.get('/parent/submissions')
    def submissions():
        with connect(database) as db:
            return [dict(r) for r in db.execute('SELECT * FROM practice_submissions ORDER BY created_at DESC,rowid DESC')]

    @router.post('/parent/submissions/{submission_id}/review')
    def review(submission_id: str, payload: Review):
        with connect(database) as db:
            db.execute('BEGIN IMMEDIATE')
            submission = db.execute('SELECT * FROM practice_submissions WHERE id=?', (submission_id,)).fetchone()
            if not submission:
                raise HTTPException(404, 'Submission not found')
            if submission['status'] == 'changes_requested':
                raise HTTPException(409, 'Review the student\'s new submission after they revise the work')
            _, doc = get_guide(db, submission['guide_id'])
            if submission['status'] == 'approved' and payload.decision != 'approved':
                raise HTTPException(409, 'Approved evidence and its XP cannot be revoked here')
            db.execute('UPDATE practice_submissions SET status=?,feedback=? WHERE id=?', (payload.decision, payload.feedback, submission_id))
            awarded = 0
            if payload.decision == 'approved':
                inserted = db.execute('INSERT OR IGNORE INTO xp_transactions(award_key,guide_id,amount,reason) VALUES(?,?,?,?)',
                    (f"practice:{submission['guide_id']}", submission['guide_id'], doc['practice']['xp'], 'Parent-approved practice'))
                awarded = doc['practice']['xp'] if inserted.rowcount else 0
            return {'status':payload.decision, 'awarded_xp':awarded, 'xp':xp_summary(db)}

    return router


if __name__ == '__main__':
    import sys
    database = Path(os.getenv('DATABASE_PATH','/data/academy.sqlite3'))
    root = Path(os.getenv('COURSES_ROOT','/courses'))
    initialize(database)
    print(import_guide(database, root, json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'))))
