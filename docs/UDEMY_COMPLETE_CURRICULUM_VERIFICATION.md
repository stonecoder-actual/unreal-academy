> Update — 17 October 2026: Git now ships the authored portal notes/checks and
> Udemy lesson links. No private transfer is needed. Raw transcripts and learner
> records stay local. Non-Udemy courses are hidden. See [bundled curriculum](BUNDLED_CURRICULUM.md).
> Earlier publication/storage details below describe the historical private batch.

# Complete Udemy video curriculum — 17 October 2026

All 207 videos across sections 1–11 are published privately to the local portal.
Each video has transcript-based takeaways followed by 3–6 automatic knowledge
checks, with hints, explanations and once-only XP. Udemy supplies practical work.
No generated activities, written submissions or parent approval were added.

## Coverage

| Section | Videos | Questions |
| --- | ---: | ---: |
| 1 | 15 | 68 |
| 2 | 8 | 35 |
| 3 | 15 | 69 |
| 4 | 22 | 112 |
| 5 | 8 | 36 |
| 6 | 10 | 46 |
| 7 | 10 | 44 |
| 8 | 37 | 157 |
| 9 | 14 | 53 |
| 10 | 50 | 194 |
| 11 | 18 | 76 |
| Total | 207 | 890 |

This batch adds 147 videos and 606 questions. Sections 1–4 retain their exact
documents, guide IDs and question IDs. All 14 non-video curriculum items remain
external Udemy links. The complete course offers 8,885 possible XP; this does not
alter the level curve or finalize the whole-library mastery plan.

## Executed checks

- Read the complete captured transcripts before authoring the remaining videos.
  Validation confirms each reviewed transcript hash still matches the source.
- All 147 documents passed schema, unique-ID, answer-index, unique-option,
  non-empty takeaways/hints/explanations, 3–6-question and no-activity checks.
- Imported each new document twice into a disposable SQLite clone. Guide IDs
  stayed stable and all learner-table fingerprints were unchanged by imports.
- Tested all 606 new questions with 1,818 synthetic answer submissions in that
  clone: wrong, correct, repeated correct. Wrong/repeated answers awarded zero;
  first successes awarded their defined XP. All explanations matched and quizzes
  completed automatically. Restarting the isolated app retained XP/completion.
- Backend suite: **62 passed**, one third-party AnyIO deprecation warning.
- Frontend Docker build passed using the existing cached TypeScript/Vite build.
  No frontend or backend application code changed in this content milestone.
- `docker compose config --quiet` passed. Frontend returned HTTP 200;
  same-origin `/api/health` reported service/database ready. Containers healthy;
  published port remains `127.0.0.1:3000`.
- Paused both live services, created a consistent backup, imported the validated
  content and restarted. Learner-table fingerprints matched both immediately
  after import and after restart, including playback, answers, XP, settings,
  permanent unlocks, equipment and mastery-plan records. No live test answers.
- Verified all 207 published lesson APIs through the frontend: takeaways, question
  counts, preserved existing guide IDs and no exposed correct-answer keys.
- Created a private ZIP with all 207 lesson documents, a checksum manifest and
  laptop import instructions. Its archive integrity passed; importing every
  packaged document into another disposable clone retained all guide IDs and
  learner-table fingerprints.

## Private artifacts and laptop delivery

`data/udemy/remaining/` contains the reviewed sources/hashes, manual authoring
files, 147 generated documents, validator/publisher and executed test/publication
reports. The publication report records the consistent pre-import backup path.
The earlier batch remains under `data/udemy/sections1-4/`.

`data/udemy/private-transfer-2026-10-17.zip` contains all 207 video lesson JSON
files and private import instructions. SHA-256:
`f073b6a7353f573c9a7fec79b5dc6cbeccebd9cc7cfcdeae5041c8606d611ae1`.
The package requires an originally seeded laptop catalogue and captured
transcripts; it does not remap independently imported lesson identities.

All source transcripts, authored course content, packages, backups and learner
data remain Git-ignored. GitHub receives application documentation and coverage
metadata only. A first laptop installation can use a fresh consistent seed;
an existing seeded installation imports the content-only package. Never overwrite
an existing learner database to deliver curriculum.

No local publication issue remains. Private transfer and acceptance on the actual
laptop still need to be performed there. Other courses' curricula and final
whole-library mastery calibration remain separate milestones.
