# Phase 3: Guided learning pilot

Deliver one parent-reviewed guided lesson attached to an imported video. The
initial private draft is for lesson 4, not the introductory administrative video.
Do not store transcripts, course-specific generated curriculum or student work
in Git or images. The authored draft and detailed analysis are under `data/`.

## Learning design

Read the complete subtitles before authoring. Segment meaningful concepts, give
each segment an objective, timestamp, brief notes, prediction prompt, hint and
one or two scenario-based checks. Prefer diagnosing a plausible mistake or predicting
a result over recalling a menu position, asset name or exact keyboard shortcut.
Correct transcription errors and flag technical oversimplifications with primary
documentation. Supply a navigation warm-up rather than assuming skipped videos
contained no necessary prerequisites.

Use a practical exercise only when supported by what is actually taught. Require
prediction, observation and explanation; a parent inspects the editor or locally
saved screenshots against explicit criteria. This first implementation accepts
written evidence and parent review, not uploaded images or automatic grading of
Unreal projects. The task's steps are authored guidance and have not been executed
in Unreal Engine during automated website verification.

## XP and levels

Each first correct question earns its configured XP (pilot: 10). An incorrect
answer earns zero, includes feedback, and may be retried without penalty. The
same check never awards XP again, including after a browser refresh or concurrent
duplicate requests. There is no watch-time reward, speed bonus or answer streak.
The pilot has 12 checks: 120 quiz XP. Its optional practical task earns 60 XP only
after parent approval, once per guide. Total possible pilot XP: 180.

Level starts at 1, with one additional level per 100 lifetime XP by default.
`settings.xp_per_level` stores that positive threshold; keep it consistent while
reviewing early lessons. Level 2 starts at 100 XP; level 3 at 200. No power-ups,
content locks or mastery certification are inferred from a level. Practice and
quiz achievement are distinct from video watching.

## Persistence and integrity

Schema version 3 adds guided lesson documents with draft/published state, quiz
attempts, an immutable positive XP ledger with unique award keys, and practical
submissions with feedback. A consistent pre-v3 database backup precedes migration.
Correct-answer evaluation and XP inserts run in one serialized SQLite transaction.
Published documents cannot be silently edited by the import CLI. Source video
and subtitle hashes bind a guide to its evidence; changed/missing sources block
use until reviewed. Video mtime/size changes require a rescan first.

Student responses omit answer keys and explanations until answering. Parent
review shows the full draft and key. As in Phase 2, Parent setup is not secured
by accounts: this assumes a trusted local single-student installation. Server
validation prevents supplied XP amounts; it does not prevent a child with access
to parent controls or local files from seeing answers. Authentication is separate.

## Acceptance

- Existing courses and playback data survive schema upgrade with a backup.
- Drafts are unavailable for student answers until parent publication.
- Wrong answers, correct answers, retries and restart persistence behave as stated.
- Concurrent duplicate answers and repeated practice approvals cannot multiply XP.
- Source changes stop use of stale curriculum; published content is immutable.
- Student and parent interfaces render, section buttons seek correctly, feedback
  and earned state survive refresh, and XP/level progress updates from the server.
- Test using separate generated-media data; leave the learner's real XP untouched.
- Actual draft is fully available for parent review; publication is the parent's
  final content decision, after implementation and verification are complete.
