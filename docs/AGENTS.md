# Unreal Academy — Agent Instructions

Read docs/PROJECT_SPEC.md before implementing features.

## Development rules
- Progression uses the Developer Guild curve in docs/PROGRESSION.md. Preserve XP, permanent unlocks and equipped cosmetics through migrations and Git updates. Mastery includes the whole planned curriculum, never only published quizzes.
- Keep personal names out of tracked files and future commit identities; use generic learner/developer labels.
- Work on one implementation milestone at a time.
- Do not implement unrelated future features.
- Prefer small, maintainable changes.
- Keep student data, course materials, and secrets out of Git.
- Bind published application ports to 127.0.0.1.
- Preserve SQLite data across container rebuilds.
- Write automated tests for new backend behavior.
- Run relevant tests before reporting completion.
- Do not claim success when tests have not run.
- Do not use mock functionality as a substitute for required persistence.
- Request approval before destructive operations.
- Do not publish or distribute purchased curriculum.

## Current milestone
Phase 4: Windows laptop deployment and controlled Git updates preserving progress.
Current learning task: simplify Udemy to transcript-based key takeaways and 3–6 automatically checked questions per video; finish the remaining curriculum with the project owner next.

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
- Purchased transcripts and derived course-specific curriculum stay in Git-ignored local data.
- Authentication and live AI integration remain future work.
- Deployment-managed laptop data stays outside Git/release checkouts. Use scripts/Academy.ps1 and its stored absolute mounts.
- Build updates before downtime; preserve old images, back up SQLite, and verify existing learner records before opening the frontend.
- Git distributes application code only. Private course transcripts and authored missions require separate local transfer; never overwrite a laptop database to distribute content.
