"""Import private, browser-captured Udemy manifests. Never fetch credentials or media."""
import hashlib
import json
import os
import uuid
from contextlib import nullcontext
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .database import connect, initialize


def udemy_url(value, slug, kind=None, external_id=None):
    url = urlsplit(value)
    path = f'/course/{slug}/'
    if kind:
        path += f"learn/{'quiz' if kind == 'quiz' else 'lecture'}/{external_id}"
    if (url.scheme != 'https' or url.netloc != 'www.udemy.com' or url.path.rstrip('/') != path.rstrip('/')
            or url.query or url.fragment):
        raise ValueError('Use a canonical https://www.udemy.com course or lesson URL without query or fragment')
    return value


class Transcript(BaseModel):
    model_config = ConfigDict(extra='forbid')
    cues: list[str] = Field(min_length=1, max_length=10000)
    captured_at: str = Field(min_length=10, max_length=80)

    @model_validator(mode='after')
    def valid_text(self):
        if any(not text.strip() or len(text) > 10000 for text in self.cues) or sum(map(len, self.cues)) > 2000000:
            raise ValueError('Transcript contains empty or oversized cues')
        return self


class ExternalLesson(BaseModel):
    model_config = ConfigDict(extra='forbid')
    external_id: str = Field(pattern=r'^\d{1,15}$')
    title: str = Field(min_length=1, max_length=300)
    section: str = Field(min_length=1, max_length=300)
    kind: Literal['video','article','quiz'] = 'video'
    url: str = Field(max_length=500)
    duration: float | None = Field(default=None, gt=0, le=604800, allow_inf_nan=False)
    transcript: Transcript | None = None


class ExternalCourse(BaseModel):
    model_config = ConfigDict(extra='forbid')
    slug: str = Field(pattern=r'^[a-z0-9][a-z0-9-]{0,150}$')
    title: str = Field(min_length=1, max_length=200)
    url: str = Field(max_length=500)
    difficulty: Literal['Beginner','Intermediate','Advanced'] = 'Beginner'
    lessons: list[ExternalLesson] = Field(min_length=1, max_length=2000)

    @model_validator(mode='after')
    def valid_links(self):
        udemy_url(self.url, self.slug)
        keys = [(l.kind == 'quiz', l.external_id) for l in self.lessons]
        if len(set(keys)) != len(keys):
            raise ValueError('Duplicate curriculum item IDs')
        for lesson in self.lessons:
            udemy_url(lesson.url, self.slug, lesson.kind, lesson.external_id)
            if lesson.kind != 'video' and lesson.transcript:
                raise ValueError('Only video items can have a transcript')
        return self


def import_external(database, payload, *, _connection=None):
    parsed = ExternalCourse.model_validate(payload)
    key = 'udemy:' + parsed.slug
    with (nullcontext(_connection) if _connection is not None else connect(database)) as db:
        if _connection is None:
            db.execute('BEGIN IMMEDIATE')
        row = db.execute('SELECT id FROM courses WHERE folder=?', (key,)).fetchone()
        course_id = row['id'] if row else str(uuid.uuid4())
        db.execute('''INSERT INTO courses(id,folder,title,source_type,source_url,difficulty) VALUES(?,?,?,'udemy',?,?)
            ON CONFLICT(folder) DO UPDATE SET title=excluded.title,source_url=excluded.source_url,difficulty=excluded.difficulty''',
            (course_id, key, parsed.title.strip(), parsed.url, parsed.difficulty))
        # An import is an upsert: omitted items/transcripts never erase existing data or progress.
        for order, lesson in enumerate(parsed.lessons, 1):
            identity = ('quiz:' if lesson.kind == 'quiz' else 'lecture:') + lesson.external_id
            row = db.execute('SELECT id FROM lessons WHERE course_id=? AND external_id=?', (course_id, identity)).fetchone()
            lesson_id = row['id'] if row else str(uuid.uuid4())
            db.execute('''INSERT INTO lessons(id,course_id,relative_path,title,content_hash,file_size,modified_ns,
                duration,playable,available,external_id,external_url,item_kind,section_title)
                VALUES(?,?,?,?,?,0,0,?,1,1,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
                title=excluded.title,relative_path=excluded.relative_path,duration=COALESCE(excluded.duration,lessons.duration),
                external_url=excluded.external_url,content_hash=excluded.content_hash,section_title=excluded.section_title,
                item_kind=excluded.item_kind,available=1''',
                (lesson_id,course_id,f'{order:04d}-{identity}',lesson.title.strip(),hashlib.sha256(lesson.url.encode()).hexdigest(),
                 lesson.duration,identity,lesson.url,lesson.kind,lesson.section.strip()))
            if lesson.transcript:
                cues = json.dumps(lesson.transcript.cues, ensure_ascii=False)
                db.execute('''INSERT INTO lesson_transcripts(lesson_id,cues,content_hash,captured_at,source_url)
                    VALUES(?,?,?,?,?) ON CONFLICT(lesson_id) DO UPDATE SET cues=excluded.cues,
                    content_hash=excluded.content_hash,captured_at=excluded.captured_at,source_url=excluded.source_url''',
                    (lesson_id,cues,hashlib.sha256(cues.encode()).hexdigest(),lesson.transcript.captured_at,lesson.url))
        count = db.execute('SELECT COUNT(*) FROM lesson_transcripts t JOIN lessons l ON l.id=t.lesson_id WHERE l.course_id=?', (course_id,)).fetchone()[0]
    return {'course_id':course_id,'imported_items':len(parsed.lessons),'captured_transcripts':count}


def create_external_router(database):
    router = APIRouter(prefix='/api/parent')

    @router.post('/external-courses/import')
    def import_course(payload: ExternalCourse):
        return import_external(database, payload.model_dump())

    @router.get('/lessons/{lesson_id}/transcript')
    def transcript(lesson_id: str):
        with connect(database) as db:
            row = db.execute('SELECT * FROM lesson_transcripts WHERE lesson_id=?', (lesson_id,)).fetchone()
            if row is None:
                raise HTTPException(404, 'No captured transcript for this lesson')
            return {**dict(row),'cues':json.loads(row['cues'])}

    return router


if __name__ == '__main__':
    import sys
    database = Path(os.getenv('DATABASE_PATH','/data/academy.sqlite3'))
    initialize(database)
    print(json.dumps(import_external(database,json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig')))))
