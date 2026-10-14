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

## Real-course follow-up

The parent subsequently supplied a local course directory. Connected it through
the Git-ignored `.env` using the existing read-only course mount and imported
the teaching collection inside it. Original files and directories were preserved.

- Imported **33 MP4 lessons**, approximately **14 GB**, with **33 matched SRT files**.
- All 33 videos passed codec checks; import and rescan returned no warnings.
- Display title is `Unreal Engine Megacourse`; numbered sections sort naturally,
  with the Introduction first and Conclusion section last.
- Real video HTTP range check: 206, 100 bytes. Caption endpoint: 200, WebVTT.
- Browser playback: first lesson loaded, resumed at a test checkpoint, played
  without a media error, and displayed real subtitles. No console warnings/errors.
- Playback position survived a backend container restart. Rescan retained
  lesson count, IDs, and saved playback position.
- Restored the original first-lesson playback/watched state after verification,
  leaving all lessons unwatched and the course ready for the student's first start.
- No project files or learning resource downloads were present in the imported
  teaching collection. Resource downloads remain covered by the generated tests.

The real-course playback acceptance check is now complete. The app remains local
at http://localhost:3000; course files and verification artifacts remain outside
Git and container images. No source-code changes were needed for this import.

## Limits

One local student; parent setup is not protected by authentication. Only MP4
lessons and supported resource extensions are imported. SRT matching is by
filename stem in the same folder. First import hashes full videos and runs
synchronously. Course-folder renames are not automatically reconciled. Watched
state is not mastery. Quizzes, assignment review, gamification and AI remain
outside this milestone.
