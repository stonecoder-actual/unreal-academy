"""Install versioned portal notes using external identities, never learner snapshots."""
import hashlib
import json
from pathlib import Path

from .database import connect
from .external import ExternalCourse, import_external

BUNDLE = Path(__file__).parent.parent / 'curriculum' / 'udemy.json'


def sync_curriculum(database, root, bundle_path=None):
    # Import lazily: guided source validation also reads the bindings written here.
    from .guided import GuideDocument, import_guide
    payload = json.loads(Path(bundle_path or BUNDLE).read_text(encoding='utf-8'))
    if payload.get('format') != 1:
        raise ValueError('Unsupported bundled curriculum format')
    course = ExternalCourse.model_validate(payload['course'])
    if any(lesson.transcript is not None for lesson in course.lessons):
        raise ValueError('The Git curriculum must not contain purchased transcripts')
    videos = {f'lecture:{l.external_id}' for l in course.lessons if l.kind == 'video'}
    if set(payload['guides']) != videos:
        raise ValueError('Every bundled video requires exactly one lesson document')
    documents = {}
    for identity, raw in payload['guides'].items():
        if 'lesson_id' in raw:
            raise ValueError('Bundles use external identities, not machine-specific lesson IDs')
        doc = GuideDocument.model_validate({**raw, 'lesson_id':'pending'})
        if not 3 <= len(doc.questions) <= 6 or not doc.takeaways or doc.practice is not None:
            raise ValueError('Bundled videos require takeaways, 3–6 checks and no portal activities')
        sections = {s.id for s in doc.sections}
        if len(sections) != len(doc.sections) or len({q.id for q in doc.questions}) != len(doc.questions):
            raise ValueError('Duplicate section/question identity')
        if any(q.section not in sections or q.correct >= len(q.options) or len(set(q.options)) != len(q.options)
               or not q.hint.strip() or not q.explanation.strip() for q in doc.questions):
            raise ValueError('Invalid bundled knowledge check')
        documents[identity] = doc
    # Validate the entire package before changing catalogue or guide rows.
    with connect(database) as db:
        db.execute('BEGIN IMMEDIATE')
        result = import_external(database, course.model_dump(), _connection=db)
        lessons = {r['external_id']:r['id'] for r in db.execute(
            'SELECT id,external_id FROM lessons WHERE course_id=?', (result['course_id'],))}
        for identity, document in documents.items():
            lesson_id = lessons[identity]
            canonical = document.model_dump(exclude={'lesson_id'})
            content_hash = hashlib.sha256(json.dumps(canonical, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
            db.execute('''INSERT INTO bundled_lesson_sources(lesson_id,content_hash) VALUES(?,?)
                ON CONFLICT(lesson_id) DO UPDATE SET content_hash=excluded.content_hash''', (lesson_id,content_hash))
            import_guide(database, root, {**canonical, 'lesson_id':lesson_id}, _connection=db)
    return {**result, 'published_videos':len(documents)}
