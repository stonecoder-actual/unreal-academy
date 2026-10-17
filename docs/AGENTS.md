# Unreal Academy — Agent Instructions

Read docs/PROJECT_SPEC.md before implementing features.

## Development rules
- Progression uses the Developer Guild curve in docs/PROGRESSION.md. Preserve XP, permanent unlocks and equipped cosmetics through migrations and Git updates. Mastery includes the whole planned curriculum, never only published quizzes.
- Keep personal names out of tracked files and future commit identities; use generic learner/developer labels.
- Work on one implementation milestone at a time.
- Do not implement unrelated future features.
- Prefer small, maintainable changes.
- Keep student data, raw purchased media/transcripts, and secrets out of Git.
- Bind published application ports to 127.0.0.1.
- Preserve SQLite data across container rebuilds.
- Write automated tests for new backend behavior.
- Run relevant tests before reporting completion.
- Do not claim success when tests have not run.
- Do not use mock functionality as a substitute for required persistence.
- Request approval before destructive operations.
- Per the 17 October 2026 user instruction, ship authored portal takeaways/checks and Udemy lesson links through Git. Do not ship purchased videos, raw transcripts, credentials or learner data.

## Current milestone
Phase 4: Windows laptop deployment and controlled Git updates preserving progress.
Current learning task: simplify Udemy to transcript-based key takeaways and 3–6 automatically checked questions per video; all 207 Udemy videos are authored and shipped as bundled portal notes/checks in Git. Default to Udemy-only visibility, preserving hidden course history. Preserve this format and existing identities for corrections.

## Required stack
- React and TypeScript
- FastAPI
- SQLite
- Docker Compose

## Definition of done
- Frontend loads in the browser.
- Backend health endpoint responds successfully.
- SQLite data persists across container restarts.
- Docker Compose builds successfully.
- Basic automated tests pass.
- README includes setup and verification instructions.
- Course folders are mounted read-only; original course files stay outside images.
- Import/rescan preserves lesson identities and unchanged playback progress.
- Video range requests, matching subtitles, and resource downloads work.
- Playback position and watched state persist across restarts.
- Existing Phase 1 data is backed up before schema migration.
- Correct knowledge checks earn XP once; retries, duplicate requests and restarts cannot farm awards.
- Publish lesson takeaways/checks directly; no guided missions, generated activities, written explanations or parent grading.
- Each new Udemy video lesson needs key takeaways and 3–6 multiple-choice checks based on its complete transcript.
- Udemy handles all practical work; do not create separate portal activities. Put the Blueprints Udemy course first.
- Parent setup covers course libraries, imports, transcripts and essential administration.
- Corrections preserve guide/question identities and earned XP; archive previous documents locally.
- All correct knowledge checks complete the lesson quiz automatically; preserve existing question IDs and once-only rewards.
- Watching and quiz understanding are separate; do not imply optional practice has been assessed.
- Raw purchased transcripts stay in Git-ignored local data. Authored portal notes/checks live in backend/curriculum/udemy.json and sync idempotently on startup.
- Authentication and live AI integration remain future work.
- Deployment-managed laptop data stays outside Git/release checkouts. Use scripts/Academy.ps1 and its stored absolute mounts.
- Build updates before downtime; preserve old images, back up SQLite, and verify existing learner records before opening the frontend.
- Git distributes application code, Udemy links and authored portal curriculum. Fresh installs require no private transfer or seed. Merge by external identities and preserve guide/question IDs; never overwrite learner databases to distribute content.
