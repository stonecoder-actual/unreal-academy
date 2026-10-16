# Direct mission publication — 16 October 2026

The project owner requested removing parental lesson approval and keeping Parent setup focused
on library configuration and essential administration. This overrides the old
approval requirements in earlier design and milestone verification documents.

## Changes

- `backend/app/guided.py`: imports publish immediately; corrections preserve
  guide IDs and the XP ledger, archive previous documents privately, filter
  obsolete solved-check IDs, and complete missions from correct checks alone.
- `backend/app/main.py`: startup releases legacy drafts after archiving them.
  Existing source-integrity checks still block stale content until reimport.
- `frontend/src/Guided.tsx`: removed parent publication, answer-key preview and
  practical grading screens; practical activities are optional instructions
  without submissions or new activity XP.
- `frontend/src/main.tsx`, `Library.tsx`, `Progress.tsx`, `ExternalImport.tsx`:
  administration-only setup, quiz-based mission selection/completion, updated
  student progress and copy.
- Guided/external backend tests cover direct publication, edits, source changes,
  preserved once-only rewards, automatic completion and restart persistence.
- README, agent instructions, project policy and authoring/Udemy docs describe
  direct publication so subsequent work does not restore the approval gate.

## Executed checks

- Backend Docker test suite: **32 passed**, one existing third-party AnyIO
  deprecation warning. Synthetic temporary data only; no live learner answers.
- Frontend: TypeScript checking and Vite production build passed, including the
  final administration-copy update.
- `docker compose config --quiet`: passed.
- `docker compose up --build -d --wait`: both services healthy. Only the frontend
  publishes a port, bound to `127.0.0.1:3000`.
- Live frontend returned HTTP 200; same-origin `/api/health` returned healthy.
- Read-only `tests/verify-design.ps1` passed for the frontend, three local course
  video ranges/captions, Udemy link inventory and production preview exclusion.
- All four authored guides returned published student documents with valid
  source bindings. Lesson 3 retained three solved checks and completed state.
- Restarted the backend and confirmed **15 XP**, three solved lesson 3 checks
  and completion survived. No live answers, review approvals or data resets were
  used for testing.
- Browser inspection confirmed administration-only Parent setup, a directly
  accessible student mission, automatic quiz feedback controls, optional practice
  without a submission form, and a dashboard showing one completed mission.

## Limits

No schema migration was needed. Historical submissions, attempts and practical
awards remain stored. Deprecated publication/practice review API routes remain
for compatibility, but the current portal does not use them. Direct corrections
are made through the private JSON import command; there is no new in-browser
curriculum editor. No curriculum beyond the existing authored guides was added.
No new mobile or assistive-technology audit was performed for this workflow edit.
