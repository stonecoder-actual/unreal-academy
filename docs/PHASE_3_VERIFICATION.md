# Phase 3 verification

Implemented and verified October 14, 2026 (America/New_York).

## Delivered

- Generic guided lesson API and parent-reviewed draft publication.
- Seven-section lesson 4 pilot, 12 scenario checks with hints, explanations and
  timestamp navigation, plus an optional parent-reviewed practical task.
- Quiz attempts, persistent XP ledger, levels, written practical evidence,
  parent feedback and resubmission. Each award is unique and transactional.
- Schema 3 with a pre-v3 SQLite backup, retaining existing courses and playback.
- Student level bar, quiz feedback, earned-check state and parent review UI.

The actual course-derived document and detailed instructional analysis are local
private artifacts: `data/lesson4-guided.json` and `data/lesson4-analysis.md`.
They are excluded from Git and container images. The main database contains the
draft attached to video 4. It has not been published for the student.

## Checks actually run

- Backend: **14 tests passed**, one third-party Starlette/AnyIO deprecation
  warning. Includes draft gating, wrong/correct answers, successful retries,
  duplicate and concurrent rewards, input validation, practical feedback and
  repeated approval, source changes, immutable publication, level boundaries,
  preserved Phase 2 data, and application restart persistence.
- Frontend: TypeScript and Vite production build passed.
- `docker compose config --quiet`: passed. Main frontend remains bound to
  `127.0.0.1:3000`; backend has no published host port.
- Docker Compose build/start: passed; both main services healthy.
- Main migration created a consistent pre-v3 backup. Existing 33-lesson course
  catalogue remains present; main XP is zero and guide status is draft.
- Isolated snapshot site on `127.0.0.1:3002` used the read-only course files and
  a separate database under `data/phase3-verification/`. No test awards or fake
  practical submissions were written to Jaxon's database.
- Browser: parent preview and test-copy publication; guided route opens video 4;
  wrong answer gives no XP; correct retry gives 10; repeated answer gives zero;
  a section button seeks to 1:59; saved progress and quiz state survive refresh.
- Live smoke: all 12 checks yield 120 XP, Level 2, and 20/100 toward Level 3.
  Repeated checks add zero. Submitting evidence alone adds zero.
- Browser: parent request for changes, student revision via the actual form,
  mandatory rubric checklist and feedback, and test-only approval add 60 XP.
  Result: 180 XP, Level 2, with 20 XP remaining to Level 3.
- Backend restart retained all 180 test XP, solved checks and practice approval.
  Repeated practical approval awarded zero.
- Browser console during verification reported no warnings/errors.

## Remaining parent action and limitations

Review the actual draft, answer key, UE5 caveats and practical rubric under
Parent setup. Approve lesson for Jaxon publishes it and enables Start guided
lesson on the course card. This follows the project's parent-approval requirement
for generated curriculum. The full implementation and draft are reviewable now.

The practical exercise is authored guidance grounded in the subtitles. It has
not been carried out in Unreal Engine during these website tests. Browser test
evidence and approvals were explicitly labeled automated test data; they are
not claims of demonstrated Unreal proficiency. The parent must observe the real
project or local screenshots before awarding Jaxon's practical XP.

Screenshot uploads, automatic Unreal project grading, accounts, mastery-based
unlocking, and a published-curriculum revision editor remain future work. Parent
controls are not authenticated, as documented since Phase 2. Published guides
cannot be silently edited; changed sources block use and need a reviewed revision.

The main app is left running. The isolated verification stack is stopped after
checks, preserving its test data locally. No repository publication was performed.
