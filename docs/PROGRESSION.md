# Developer Guild progression

Approved 16 October 2026. This replaces the old flat 100-XP level calculation.
No XP transactions, quiz attempts or playback records are rewritten.

## Level curve and rewards

| Level | Cumulative XP | Permanent title | Emblem |
| --- | ---: | --- | --- |
| 1 | 0 | Newbie | Spark |
| 3 | 120 | Beginner | Compass |
| 5 | 330 | Novice | Bronze cube |
| 10 | 1,240 | Apprentice | Wrench |
| 15 | 2,700 | Builder | Hammer |
| 20 | 4,710 | World Designer | Globe |
| 25 | 7,270 | Blueprint Adept | Connected nodes |
| 30 | 10,380 | Game Developer | Controller |
| 40 | 18,250 | Unreal Expert | Crystal |
| 50 | 28,320 plus mastery goals | Unreal Master | Gold crown and cube |

For level L, let n = L - 1. Its cumulative threshold is
`50*n + 11*n*(n-1)`, rounded to the nearest ten. Early levels come quickly and
later levels require more learning. `guild-v1` caps the displayed level at 50;
lifetime XP continues accumulating. The frontend handles the cap without a
division by zero or a nonexistent Level 51 goal.

The initial imported library contains 665 videos. The first authored Udemy batch
averaged about 47 XP per video, giving the original roughly 31,000-XP projection.
The completed 207-video Udemy course has 890 checks, about 4.3 checks per video
at the usual 10-XP reward (some early checks award less). Other courses still need
authoring, so this is not a final whole-library XP budget. The course offers 8,885
possible XP. Thresholds remain the approved initial calibration; revisit deliberately
after the remaining purchased courses and final checks are inventoried. Never
silently change the curve based on newly published notes or revoke earned ranks.

Question rewards remain once-only: normally 10 XP, with smaller introductory
rewards. Wrong answers, watching and repeated correct submissions earn none.
There are no XP losses, streak penalties or new portal practical assignments.

## Permanent collection

- A first qualifying XP award persists the rank in `progression_unlocks`.
  Existing XP also unlocks its eligible ranks when progression is first loaded.
- All earned titles and emblems remain available. Equip them independently in
  My progress; selections persist in `progression_equipment`.
- Follow newest rank clears explicit selections and follows the highest earned
  rank automatically. Changing cosmetics never awards or spends XP.
- The nameplate and profile show the equipped emblem/title. Level-ups show a
  short notification; rank milestones show a larger reveal without a duplicate
  level toast. Motion respects the system's reduced-motion preference.
- Locked rewards cannot be equipped through either the UI or API.

## Unreal Master gates

All must be met to earn the final title/emblem:

1. Level 50, requiring at least 28,320 lifetime XP.
2. At least 85% of the mastery track's checks solved overall.
3. At least 75% of the checks in every track course solved.
4. The full planned track has valid published guides and its membership is finalized.

`mastery_plan` records imported video lessons while the track is a draft.
Readings and external quizzes do not count as authored portal checks. Missing
lessons already in the plan stay there; deleting or hiding content cannot make
the goal easier. Pending or outdated guides use an estimate of five checks per
video. Draft metrics are labeled estimates and cannot unlock Master regardless
of XP. Repeated answers count only once, and removed question IDs do not count
toward current checks. Watching alone is not quiz understanding.

Import all intended courses and finish their authoring, then use **Parent setup
→ Mastery track setup → Finalize mastery track**. The API refuses finalization
if planned guides are missing, stale or unavailable. This is one-time curriculum
configuration, not per-lesson approval or grading. The final course inventory is
still pending, so the real track remains a draft today.

Finalization freezes membership. Later imports do not silently extend that
track. Previously earned Master remains unlocked if content is corrected or
becomes unavailable. The title recognizes academy knowledge-check progress;
practical skills continue developing through the purchased instructor's work.

## Persistence and API

Schema 5 adds four tables without modifying existing learner records:
`progression_unlocks`, `progression_equipment`, `mastery_plan`, `mastery_state`.
Migration first creates a consistent `backups/pre-v5-*.sqlite3` snapshot.
The old `settings.xp_per_level` value remains for compatibility but is no longer
used; `/api/xp` returns the span for the learner's current level instead.

- `GET /api/xp`: current curve, lifetime total, level boundaries and cap state.
- `GET /api/progression`: XP, permanent ranks, equipment, next rank and mastery.
- `PUT /api/progression/equipment`: optional `title_id` and/or `icon_id`;
  `null` restores automatic selection for that slot.
- `POST /api/parent/progression/finalize`: finalize a fully authored track.

Unlocks and equipment use the same persistent host database as XP. Deployment
snapshots now fingerprint all four new tables too. Updates must preserve those
records before opening the new frontend. Continue using the managed laptop
updater and private lesson imports; do not replace an existing learner database.
