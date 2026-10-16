# Udemy sections 1–4 — 16 October 2026

Published privately to the local learning portal at http://localhost:3000.
This report contains coverage and verification metadata only. Purchased
transcripts and derived lesson content are not distributed through Git.

## Coverage

| Section | Video lessons with takeaways | Automatic questions |
| --- | ---: | ---: |
| 1: Introduction | 15 | 68 |
| 2: The Blueprint Visual Scripting System | 8 | 35 |
| 3: Vectors and Rotators | 15 | 69 |
| 4: Bad Bot | 22 | 112 |
| Total | 60 | 284 |

Reviewed the captured transcripts and authored 57 new video lessons. The three
existing video lessons retain their documents, guide IDs and question IDs.
Every video has highlighted takeaways followed by 3–6 multiple-choice questions,
with hints, immediate explanations and once-only XP. Answer positions vary.
No additional activities, written submissions or parent approval were added.
Two readings and four existing Udemy quizzes remain external Udemy items.
Sections 5 onward still require authoring.

Questions emphasize the central concepts, predictions and troubleshooting.
Light introductory videos have fewer questions; denser programming lessons have
more. Notes distinguish recorded menu/version details from enduring concepts.
They do not repeat misleading generalizations in automatic captions, including
the claim that all scalar constants must be integers or that vector scalar
multiplication is the only possible vector-related multiplication operation.
No unverified transcript timestamps are invented.

## Private files

- `data/udemy/sections1-4/sources.json`: captured transcript content and hashes.
- `data/udemy/sections1-4/author.py`: manual curriculum authoring source.
- `data/udemy/sections1-4/output/lesson-NN.json`: 60 importable lesson documents.
- `data/udemy/sections1-4/publish.py`: batch validator, isolated tests, publication
  and read-only live verification.
- `data/udemy/sections1-4/test-report.json` and `publication-report.json`: results,
  lesson/guide identities and consistent SQLite snapshot locations.

All are excluded from Git by `data/`. The importer binds each guide to its
current external lesson and captured transcript hash. The batch validator
checks that the hash still matches the reviewed source before importing.
Private JSON must be transferred separately when installing on Jaxon's laptop;
Git application updates do not carry curriculum or replace learner databases.

## Executed verification

- Backend suite: **45 passed**, one existing third-party AnyIO deprecation warning.
- All 60 documents passed schema, unique-ID, source-hash, answer-index,
  option-uniqueness, 3–6-question and no-activity validation before publication.
- Imported the entire batch twice into a temporary SQLite clone. Guide IDs were
  stable and learner-table fingerprints were unchanged by imports.
- Tested all **284 questions** with **852 synthetic submissions**, exclusively
  against that temporary clone: wrong answer, correct answer and repeated correct
  answer. Wrong answers and repeated successes gave zero XP; first correct
  answers gave the defined reward unless already earned in the copied state.
  Every explanation matched its authored question; all quizzes completed.
- Restarted the isolated app and verified all quiz completions and XP persisted.
- Took a consistent live SQLite backup before publication. All learner-table
  fingerprints matched immediately after the 60 imports. No live quiz answers
  were submitted during verification.
- Verified the student API for all 60 lessons through the frontend origin:
  published status, takeaways, question counts and no exposed answer key.
- The first restart check detected one newly saved watched-state row for lesson
  1. Inspection confirmed every original learner record remained present and
  unchanged, with no quiz or XP additions. Kept that new watched state; no data
  were restored or removed. Took a fresh snapshot, restarted the backend again,
  and verified an exact learner-table match and all 60 lesson APIs afterward.
- Existing lesson 3 still has all three correct checks, is complete, and total
  live XP remains **15**. The existing lessons 3, 5 and 6 keep their guide IDs.
- `docker compose config --quiet` passed; frontend and backend containers are
  healthy. The frontend returns HTTP 200 and same-origin `/api/health` reports
  service/database ready. No image changes or rebuild were needed for content.
- Browser checked a lesson from each of the four sections. Takeaways precede
  automatic questions; section 4 Game Mode displays six checks and no textareas.

Updated README, current project inventory and lesson-authoring coverage.
No application code, schema or original course files changed. Nothing from this
private curriculum batch was pushed to GitHub. No unresolved publication issue;
later-section authoring and private laptop transfer remain separate work.
