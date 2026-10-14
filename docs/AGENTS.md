# Unreal Academy — Agent Instructions

Read docs/PROJECT_SPEC.md before implementing features.

## Development rules
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
Phase 2: Local course import and lesson playback.

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
- Quizzes, assignment review, authentication, gamification, and AI remain future work.
