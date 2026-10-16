# Simple Udemy lessons — 16 October 2026

The project owner requested a smaller learning flow: each Udemy video gets transcript-based
key takeaways and 3–6 automatic multiple-choice checks, depending on complexity.
Udemy handles the UE5 practical work. No guided-mission framing, custom
activities, written answers or parent grading. Remaining curriculum authoring
continues with the project owner after this format change.

## Delivered

- Replaced the mission component with `frontend/src/LessonNotes.tsx`: key
  takeaways followed by all questions, automatic feedback/hints, saved answers
  and once-only XP. Removed the portal activity and mission-step interfaces.
- Homepage features the purchased Blueprints Udemy course with a direct
  start/continue button. It is first in the course list; other Udemy courses
  follow before local courses. Progress uses lesson-quiz terminology.
- Udemy imports require non-empty takeaways, 3–6 questions and `practice: null`.
  Legacy database/API naming remains compatible; no schema migration needed.
- Reviewed the complete captured transcripts for the three existing authored
  Udemy lessons. Converted lesson 3 to four takeaways/three checks, lesson 5 to
  six takeaways/six checks, and lesson 6 to six takeaways/six checks. Retained
  their document/lesson IDs and the question IDs for retained questions.
- Private JSON files live under `data/udemy/lesson3-notes.json`,
  `lesson5-notes.json` and `lesson6-notes.json`. Prior document versions are
  archived locally. Purchased source/lesson content is not included in Git.
- Updated authoring policy, project instructions, README and inventory so future
  lessons follow this format. No new lessons beyond those three were authored.

## Executed checks

- **45 backend tests passed**; one existing third-party AnyIO deprecation warning.
  Added coverage for 3/6-question boundaries, rejected 2/7-question documents,
  required takeaways, rejection of activities, prioritized course ordering and
  retained rewards when correcting/reducing a quiz.
- Frontend TypeScript/Vite production build passed, including the final XP label.
- Compose config passed; current services rebuilt and started healthy.
- Read-only live media/endpoint smoke checks passed for all three local courses
  and the external Udemy catalogue.
- A consistent database snapshot was created before changes. Its learner-record
  fingerprints still match after imports and a backend restart: settings,
  course/lesson identities, playback/watched state, quiz attempts, XP transactions
  and historical submissions were not reset or rewritten. Live XP remains **15**;
  lesson 3 retains all three correct answers.
- Browser verified Udemy as the featured/first course; a pending video clearly
  states its notes are not yet prepared. Lesson 5 shows six knowledge-check forms,
  no textareas and no mission headings. No live answer submissions or watched-state
  changes were used for testing.
- Real isolated Git/Docker laptop integration passed with a three-question
  synthetic lesson: install/import, updates, idle deferral, no-op, dirty/offline
  refusal, interrupted-update recovery, preservation of newer learner writes,
  unhealthy-release recovery and retained synthetic XP/playback. That test stack
  was stopped; the learner's data was not used. Test fixture copying now tolerates
  tracked files removed in the working tree.

## Remaining

Author the rest of the Udemy video curriculum using the accepted takeaways and
3–6-question format. Captured transcripts do not imply finished notes/questions;
unprepared videos stay watchable. App code can update through Git; private lesson
content still transfers separately, as agreed. Historical local-course and
practice records are retained for compatibility and earned-XP preservation, but
no additional portal activity is shown or newly authored.
