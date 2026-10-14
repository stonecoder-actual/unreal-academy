import hashlib
import json
import math
import re
import sqlite3
import subprocess
import threading
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field

from .database import connect

RESOURCE_TYPES = {'.zip', '.7z', '.rar', '.pdf', '.txt', '.md', '.json', '.csv',
                  '.png', '.jpg', '.jpeg', '.webp', '.uproject', '.uasset', '.umap',
                  '.fbx', '.obj', '.blend', '.wav', '.mp3'}


def natural_key(value):
    return [int(part) if part.isdigit() else part.casefold()
            for part in re.split(r'(\d+)', str(value))]


def safe_path(root: Path, relative: str):
    base = root.resolve()
    candidate = (base / relative).resolve()
    if not candidate.is_relative_to(base) or candidate == base:
        raise HTTPException(400, 'Path must stay inside the course library')
    return candidate


def digest(path: Path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def probe(path: Path):
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)],
            capture_output=True, text=True, timeout=30, check=True)
        info = json.loads(result.stdout)
        streams = info.get('streams', [])
        video = next((s.get('codec_name') for s in streams if s.get('codec_type') == 'video'), None)
        audio = next((s.get('codec_name') for s in streams if s.get('codec_type') == 'audio'), None)
        duration = float(info['format']['duration'])
        if not math.isfinite(duration) or duration <= 0:
            raise ValueError('Invalid video duration')
        pixel_format = next((s.get('pix_fmt') for s in streams if s.get('codec_type') == 'video'), None)
        return duration, video, audio, video == 'h264' and pixel_format in ('yuv420p', 'yuvj420p') and audio in (None, 'aac', 'mp3')
    except (subprocess.SubprocessError, KeyError, ValueError, OSError):
        return None, None, None, False


def srt_to_vtt(path: Path):
    text = path.read_text(encoding='utf-8-sig').replace('\r\n', '\n')
    # Do not pass arbitrary subtitle markup through to the browser.
    text = re.sub(r'<[^>]*>', '', text)
    text = re.sub(r'(\d{2}:\d{2}:\d{2}),(\d{1,3})', lambda m: m[1] + '.' + m[2].ljust(3, '0'), text)
    return 'WEBVTT\n\n' + text


class ImportRequest(BaseModel):
    folder: str = Field(min_length=1, max_length=500)
    title: str | None = Field(default=None, min_length=1, max_length=200)


class ProgressUpdate(BaseModel):
    position: float = Field(ge=0, le=604800, allow_inf_nan=False)
    watched: bool | None = None


def create_library_router(database: Path, root: Path):
    router = APIRouter(prefix='/api')
    import_lock = threading.Lock()

    def lesson_row(db, lesson_id):
        row = db.execute('SELECT l.*, c.folder FROM lessons l JOIN courses c ON c.id=l.course_id WHERE l.id=?', (lesson_id,)).fetchone()
        if row is None:
            raise HTTPException(404, 'Lesson not found')
        return row

    def existing_file(relative):
        file = safe_path(root, relative)
        if not file.is_file():
            raise HTTPException(404, 'File is missing from the local course folder')
        return file

    @router.get('/library/folders')
    def folders():
        if not root.is_dir():
            return {'folders': []}
        return {'folders': sorted([p.name for p in root.iterdir()
                                   if p.is_dir() and not p.is_symlink() and not p.name.startswith('.')], key=natural_key)}

    @router.post('/courses/import')
    def import_course(payload: ImportRequest):
        folder = safe_path(root, payload.folder)
        if not folder.is_dir() or folder.is_symlink():
            raise HTTPException(400, 'Select a course folder inside the library')
        folder_key = folder.relative_to(root.resolve()).as_posix()
        if not import_lock.acquire(blocking=False):
            raise HTTPException(409, 'Another import is running; try again when it finishes')
        try:
            files = sorted([p for p in folder.rglob('*') if p.is_file() and not p.is_symlink()
                            and p.resolve().is_relative_to(folder)
                            and not any(part.startswith('.') for part in p.relative_to(folder).parts)], key=natural_key)
            videos = [p for p in files if p.suffix.lower() == '.mp4']
            relative_files = {p.relative_to(folder).as_posix(): p for p in files}
            warnings = []
            with connect(database) as db:
                course = db.execute('SELECT * FROM courses WHERE folder=?', (folder_key,)).fetchone()
                course_id = course['id'] if course else str(uuid.uuid4())
                old = list(db.execute('SELECT * FROM lessons WHERE course_id=?', (course_id,)))
                by_path = {row['relative_path']: row for row in old}
            if not videos and not course:
                raise HTTPException(400, 'This folder contains no MP4 lessons')
            if not videos:
                warnings.append('No videos found; existing lessons are marked missing and their progress is retained')
            # Hash/probe before the write transaction so playback progress isn't blocked.
            records = []
            for video in videos:
                relative = video.relative_to(folder).as_posix()
                stat = video.stat()
                previous = by_path.get(relative)
                unchanged = previous and previous['file_size'] == stat.st_size and previous['modified_ns'] == stat.st_mtime_ns
                content_hash = previous['content_hash'] if unchanged else digest(video)
                metadata = (previous['duration'], previous['video_codec'], previous['audio_codec'], previous['playable']) if unchanged else probe(video)
                captions = [p for name, p in relative_files.items()
                            if p.parent == video.parent and p.stem.casefold() == video.stem.casefold() and p.suffix.lower() == '.srt']
                if not captions:
                    # Some exports insert a language tag before the source suffix.
                    captions = [p for p in files if p.parent == video.parent and p.suffix.lower() == '.srt'
                                and re.sub(r'-(english|en)(?=-|$)', '', p.stem, flags=re.I).casefold() == video.stem.casefold()]
                caption = captions[0].relative_to(folder).as_posix() if len(captions) == 1 else None
                if caption:
                    try:
                        srt_to_vtt(folder / caption)
                    except UnicodeError:
                        warnings.append(f'{relative}: subtitles must be UTF-8; captions skipped')
                        caption = None
                if not metadata[3]:
                    warnings.append(f'{relative}: unverified or unsupported video/audio codecs; see conversion instructions')
                records.append((relative, content_hash, stat, metadata, caption))
            with connect(database) as db:
                db.execute('INSERT OR IGNORE INTO courses(id,folder,title) VALUES(?,?,?)', (course_id, folder_key, payload.title or folder.name))
                if payload.title:
                    db.execute('UPDATE courses SET title=? WHERE id=?', (payload.title.strip(), course_id))
                db.execute('UPDATE lessons SET available=0 WHERE course_id=?', (course_id,))
                db.execute('UPDATE resources SET available=0 WHERE course_id=?', (course_id,))
                matched = set()
                current_paths = {record[0] for record in records}
                for relative, content_hash, stat, metadata, caption in records:
                    previous = by_path.get(relative)
                    if not previous:
                        candidates = [row for row in old if row['content_hash'] == content_hash
                                      and row['relative_path'] not in current_paths and row['id'] not in matched]
                        previous = candidates[0] if len(candidates) == 1 else None
                    lesson_id = previous['id'] if previous else str(uuid.uuid4())
                    matched.add(lesson_id)
                    # Never erase saved student progress as a side effect of a rescan.
                    if previous and previous['content_hash'] != content_hash:
                        warnings.append(f'{relative}: video content changed; saved progress retained. Review its watched state')
                    db.execute('''INSERT INTO lessons(id,course_id,relative_path,title,content_hash,file_size,modified_ns,duration,video_codec,audio_codec,playable,caption_path,available)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,1) ON CONFLICT(id) DO UPDATE SET
                        relative_path=excluded.relative_path,title=excluded.title,content_hash=excluded.content_hash,
                        file_size=excluded.file_size,modified_ns=excluded.modified_ns,duration=excluded.duration,
                        video_codec=excluded.video_codec,audio_codec=excluded.audio_codec,playable=excluded.playable,
                        caption_path=excluded.caption_path,available=1''',
                        (lesson_id, course_id, relative, Path(relative).stem, content_hash, stat.st_size, stat.st_mtime_ns, *metadata, caption))
                active = list(db.execute('SELECT id,relative_path FROM lessons WHERE course_id=? AND available=1', (course_id,)))
                for resource in files:
                    if resource.suffix.lower() not in RESOURCE_TYPES:
                        continue
                    relative = resource.relative_to(folder).as_posix()
                    associated = [row['id'] for row in active if Path(row['relative_path']).parent == Path(relative).parent
                                  and Path(row['relative_path']).stem.casefold() == resource.stem.casefold()]
                    lesson_id = associated[0] if len(associated) == 1 else None
                    db.execute('''INSERT INTO resources(id,course_id,lesson_id,relative_path,available) VALUES(?,?,?,?,1)
                        ON CONFLICT(course_id,relative_path) DO UPDATE SET lesson_id=excluded.lesson_id,available=1''',
                        (str(uuid.uuid4()), course_id, lesson_id, relative))
            return {'course_id': course_id, 'lessons': len(videos), 'warnings': warnings}
        except (OSError, sqlite3.Error) as error:
            raise HTTPException(400, 'Import failed; check that the files are readable and try again') from error
        finally:
            import_lock.release()

    @router.get('/courses')
    def courses():
        with connect(database) as db:
            return [dict(row) for row in db.execute('''SELECT c.*, COUNT(l.id) AS lesson_count,
                COALESCE(SUM(p.watched),0) AS watched_count,
                SUM(CASE WHEN p.position > 0 OR p.watched=1 THEN 1 ELSE 0 END) AS started_count FROM courses c
                LEFT JOIN lessons l ON l.course_id=c.id AND l.available=1
                LEFT JOIN lesson_progress p ON p.lesson_id=l.id GROUP BY c.id ORDER BY c.title''')]

    @router.get('/courses/{course_id}')
    def course_detail(course_id: str):
        with connect(database) as db:
            course = db.execute('SELECT * FROM courses WHERE id=?', (course_id,)).fetchone()
            if course is None:
                raise HTTPException(404, 'Course not found')
            lessons = [dict(row) for row in db.execute('''SELECT l.*, COALESCE(p.position,0) AS position,
                COALESCE(p.watched,0) AS watched, p.updated_at FROM lessons l
                LEFT JOIN lesson_progress p ON l.id=p.lesson_id WHERE l.course_id=?''', (course_id,))]
            lessons.sort(key=lambda row: natural_key(row['relative_path']))
            for row in lessons:
                row.pop('content_hash')
            resources = [dict(row) for row in db.execute('SELECT * FROM resources WHERE course_id=? AND available=1', (course_id,))]
            return {**dict(course), 'lessons': lessons, 'resources': resources}

    @router.put('/lessons/{lesson_id}/progress')
    def update_progress(lesson_id: str, payload: ProgressUpdate):
        with connect(database) as db:
            lesson = lesson_row(db, lesson_id)
            if not lesson['available']:
                raise HTTPException(409, 'Lesson is missing; rescan the course after restoring it')
            position = min(payload.position, lesson['duration']) if lesson['duration'] else payload.position
            db.execute('''INSERT INTO lesson_progress(lesson_id,position,watched) VALUES(?,?,?)
                ON CONFLICT(lesson_id) DO UPDATE SET position=excluded.position,
                watched=COALESCE(?,lesson_progress.watched),updated_at=CURRENT_TIMESTAMP''',
                (lesson_id, position, int(payload.watched or False), payload.watched))
            return dict(db.execute('SELECT * FROM lesson_progress WHERE lesson_id=?', (lesson_id,)).fetchone())

    @router.get('/lessons/{lesson_id}/video')
    def video(lesson_id: str):
        # FileResponse implements standards-compliant byte ranges from the HTTP Range header.
        with connect(database) as db:
            lesson = lesson_row(db, lesson_id)
        file = existing_file(f"{lesson['folder']}/{lesson['relative_path']}")
        return FileResponse(file, media_type='video/mp4')

    @router.get('/lessons/{lesson_id}/captions')
    def captions(lesson_id: str):
        with connect(database) as db:
            lesson = lesson_row(db, lesson_id)
        if not lesson['caption_path']:
            raise HTTPException(404, 'No matching subtitles')
        file = existing_file(f"{lesson['folder']}/{lesson['caption_path']}")
        try:
            return Response(srt_to_vtt(file), media_type='text/vtt')
        except UnicodeError as error:
            raise HTTPException(422, 'Subtitles must be encoded as UTF-8') from error

    @router.get('/resources/{resource_id}/download')
    def download(resource_id: str):
        with connect(database) as db:
            resource = db.execute('''SELECT r.*,c.folder FROM resources r JOIN courses c ON c.id=r.course_id
                WHERE r.id=? AND r.available=1''', (resource_id,)).fetchone()
        if resource is None:
            raise HTTPException(404, 'Resource not found')
        file = existing_file(f"{resource['folder']}/{resource['relative_path']}")
        return FileResponse(file, media_type='application/octet-stream', filename=file.name)

    return router
