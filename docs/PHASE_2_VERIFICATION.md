# Phase 2 verification

Verified locally on October 13, 2026 (America/New_York), using Docker Desktop
29.8.2 and Compose 5.5.1 with Linux containers.

## Results

- Backend suite: **8 passed**, with one third-party Starlette/AnyIO deprecation
  warning. Includes schema migration and backup, persistent settings, course
  import/rescan, lesson renames, replaced/missing media, an empty rescan, video
  byte ranges (206 and invalid-range 416), subtitles, resource downloads, path
  traversal/symlink protection and progress validation/persistence.
- Frontend: TypeScript checking and Vite production build passed after the final
  watched-state control change.
- `docker compose config --quiet`: passed. The runtime frontend publishes only
  `127.0.0.1:3000`; the backend has no published host port. Course mount is read-only.
- Main application upgrade/build/start: passed; both services healthy. Health
  responds with phase 2 and database status `ok`. Existing welcome text retained.
- Consistent pre-v2 database backup exists in `data/backups/`. Backup filenames
  use UTC timestamps; this session's backup is dated October 14 in UTC.
- Isolated live smoke test: passed through nginx on `127.0.0.1:3001` using
  generated H.264 test media. Verified import/rescan, 100-byte HTTP range,
  WebVTT captions, attachment download, and saved position/watched state after
  backend restart and container replacement.
- Browser: verified the course card, lesson layout, video loading and playing,
  visible captions, 1.5x playback, resume at the stored 1.5-second checkpoint,
  parent rescan success, and marking a lesson unwatched to reset to the start.
  No browser console errors/warnings were reported during the verification.
- Main library is empty and shows the parent-setup guidance. Generated test
  media was kept separate from the main library and database.
- `git diff --check`: passed. Database, migration backups, generated fixtures,
  and local course directory are ignored by Git.

The isolated test stack is stopped after verification; the main app remains
running at http://localhost:3000. The browser screenshot of the generated lesson
is saved locally under `data/phase2-verification/browser-preview.png` (Git-ignored).
No GitHub repository was created or published.

## Remaining acceptance step

No purchased course location has been supplied yet. The parent must copy the
first few MP4/SRT/resource files into a course folder, set `COURSES_DIR` to the
host library path, recreate the app, and import that folder. A real-course
playback check is still required before declaring the learning workflow ready
for the student. Recommended folders and setup are documented in the README.

## Limits

One local student; parent setup is not protected by authentication. Only MP4
lessons and supported resource extensions are imported. SRT matching is by
filename stem in the same folder. First import hashes full videos and runs
synchronously. Course-folder renames are not automatically reconciled. Watched
state is not mastery. Quizzes, assignment review, gamification and AI remain
outside this milestone.
