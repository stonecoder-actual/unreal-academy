"""Permanent cosmetic rewards; XP remains in the original once-only ledger."""
import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict

from .database import connect

MAX_LEVEL = 50
RANKS = [
    ('newbie', 'Newbie', 1, 'spark', 'bronze'),
    ('beginner', 'Beginner', 3, 'compass', 'bronze'),
    ('novice', 'Novice', 5, 'cube', 'bronze'),
    ('apprentice', 'Apprentice', 10, 'wrench', 'bronze'),
    ('builder', 'Builder', 15, 'hammer', 'silver'),
    ('world-designer', 'World Designer', 20, 'globe', 'silver'),
    ('blueprint-adept', 'Blueprint Adept', 25, 'nodes', 'violet'),
    ('game-developer', 'Game Developer', 30, 'controller', 'violet'),
    ('unreal-expert', 'Unreal Expert', 40, 'crystal', 'violet'),
    ('unreal-master', 'Unreal Master', 50, 'crown', 'gold'),
]


def threshold(level):
    n = level - 1
    # Round half upward to a multiple of ten. All inputs here are integers.
    return ((50*n + 11*n*(n-1) + 5) // 10) * 10


def xp_summary(db):
    total = db.execute('SELECT COALESCE(SUM(amount),0) FROM xp_transactions').fetchone()[0]
    level = max(n for n in range(1, MAX_LEVEL+1) if total >= threshold(n))
    floor = threshold(level)
    ceiling = threshold(level+1) if level < MAX_LEVEL else floor
    return dict(total_xp=total, level=level, level_xp=min(total-floor, ceiling-floor),
                xp_per_level=ceiling-floor, xp_to_next_level=max(0, ceiling-total),
                level_floor_xp=floor, next_level_xp=ceiling, max_level=MAX_LEVEL,
                at_max_level=level == MAX_LEVEL, curve_version='guild-v1')


def mastery(db, root=None):
    finalized = bool(db.execute('SELECT finalized FROM mastery_state WHERE id=1').fetchone()[0])
    if not finalized:
        # Draft membership includes imported videos, including unauthored lessons.
        # Keep missing lessons already in the plan; rescans must not shrink goals.
        db.execute("INSERT OR IGNORE INTO mastery_plan(lesson_id,course_id) SELECT id,course_id FROM lessons WHERE available=1 AND item_kind='video'")
    awards = {r[0] for r in db.execute("SELECT award_key FROM xp_transactions WHERE award_key LIKE 'question:%'")}
    courses = {}
    for row in db.execute('''SELECT p.lesson_id,p.course_id,c.title,l.available,l.content_hash,l.external_url,
        g.id AS guide_id,g.document,g.status,g.video_hash,g.subtitle_hash,t.content_hash AS transcript_hash
        FROM mastery_plan p JOIN courses c ON c.id=p.course_id JOIN lessons l ON l.id=p.lesson_id
        LEFT JOIN guided_lessons g ON g.lesson_id=l.id
        LEFT JOIN lesson_transcripts t ON t.lesson_id=l.id'''):
        course = courses.setdefault(row['course_id'], dict(course_id=row['course_id'], title=row['title'],
            videos=0, authored_videos=0, planned_checks=0, solved_checks=0))
        course['videos'] += 1
        current = (row['available'] and row['status'] == 'published' and row['video_hash'] == row['content_hash']
                   and (not row['external_url'] or row['subtitle_hash'] == row['transcript_hash']))
        if current and not row['external_url'] and root is not None:
            # Reuse the local file/subtitle guard; changing files without a rescan
            # must not allow a stale guide to qualify for final mastery.
            from .guided import source
            try:
                video_hash, subtitle_hash, _ = source(db, row['lesson_id'], root)
                current = (video_hash, subtitle_hash) == (row['video_hash'], row['subtitle_hash'])
            except HTTPException:
                current = False
        try:
            questions = json.loads(row['document'])['questions'] if current else []
        except (ValueError, KeyError, TypeError):
            questions = []
        if questions:
            course['authored_videos'] += 1
            course['planned_checks'] += len(questions)
            course['solved_checks'] += sum(f"question:{row['guide_id']}:{q['id']}" in awards for q in questions)
        else:
            course['planned_checks'] += 5  # Estimate only; never enables early mastery.
    result = list(courses.values())
    for c in result:
        c['required_checks'] = (c['planned_checks'] * 75 + 99) // 100
        c['percent'] = round(c['solved_checks'] / c['planned_checks'] * 100, 1) if c['planned_checks'] else 0
        c['complete'] = c['solved_checks'] >= c['required_checks']
    planned = sum(c['planned_checks'] for c in result)
    solved = sum(c['solved_checks'] for c in result)
    ready = bool(result) and all(c['authored_videos'] == c['videos'] for c in result)
    required = (planned * 85 + 99) // 100
    eligible = finalized and ready and solved >= required and all(c['complete'] for c in result)
    return dict(finalized=finalized, ready_to_finalize=ready, eligible=eligible,
        courses=sorted(result, key=lambda c:c['title']), planned_checks=planned, solved_checks=solved,
        required_checks=required, overall_percent=round(solved/planned*100, 1) if planned else 0,
        overall_target_percent=85, course_target_percent=75,
        videos=sum(c['videos'] for c in result), authored_videos=sum(c['authored_videos'] for c in result),
        estimate=not ready)


def progression(db, root=None):
    summary = xp_summary(db)
    track = mastery(db, root)
    for rank_id, _, level, _, _ in RANKS:
        if summary['level'] >= level and (rank_id != 'unreal-master' or track['eligible']):
            db.execute('INSERT OR IGNORE INTO progression_unlocks(rank_id) VALUES(?)', (rank_id,))
    unlocked = dict(db.execute('SELECT rank_id,unlocked_at FROM progression_unlocks'))
    ranks = [dict(id=rid, title=title, level=level, xp=threshold(level), icon=icon, material=material,
                  unlocked=rid in unlocked, unlocked_at=unlocked.get(rid), requires_mastery=rid=='unreal-master')
             for rid,title,level,icon,material in RANKS]
    highest = next(r for r in reversed(ranks) if r['unlocked'])
    equipment = db.execute('SELECT title_id,icon_id FROM progression_equipment WHERE id=1').fetchone()
    by_id = {r['id']:r for r in ranks}
    return {**summary, 'ranks':ranks, 'highest_rank':highest,
        'equipped_title':by_id.get(equipment['title_id'], highest),
        'equipped_icon':by_id.get(equipment['icon_id'], highest),
        'equipment':dict(equipment), 'next_rank':next((r for r in ranks if not r['unlocked']), None),
        'mastery':track}


class Equipment(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title_id: str | None = None
    icon_id: str | None = None


def create_progression_router(database, root):
    router = APIRouter(prefix='/api')

    @router.get('/progression')
    def get_progression():
        with connect(database) as db:
            db.execute('BEGIN IMMEDIATE')
            return progression(db, root)

    @router.put('/progression/equipment')
    def equip(payload: Equipment):
        with connect(database) as db:
            db.execute('BEGIN IMMEDIATE')
            result = progression(db, root)
            unlocked = {r['id'] for r in result['ranks'] if r['unlocked']}
            for key in payload.model_fields_set:
                value = getattr(payload,key)
                if value is not None and value not in unlocked:
                    raise HTTPException(403, 'Earn this rank before equipping its reward')
                # Column names come from the model, never from a free-form request.
                db.execute(f'UPDATE progression_equipment SET {key}=? WHERE id=1', (value,))
            return progression(db, root)

    @router.post('/parent/progression/finalize')
    def finalize():
        with connect(database) as db:
            db.execute('BEGIN IMMEDIATE')
            track = mastery(db, root)
            if not track['ready_to_finalize']:
                raise HTTPException(409, 'Finish authoring all planned video checks before finalizing the mastery track')
            db.execute('UPDATE mastery_state SET finalized=1 WHERE id=1')
            return progression(db, root)

    return router
