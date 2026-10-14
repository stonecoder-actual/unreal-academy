# Phase 2: First usable course

This milestone adds local course discovery/import, a student lesson library,
video playback with captions and speed controls, resource downloads, and saved
playback/watched state. Quizzes, practical assignment submission/review,
authentication, gamification and AI remain future work.

## Architecture and storage

Retain the Phase 1 React, nginx, FastAPI and SQLite deployment. Mount a dedicated
course directory read-only at `/courses`; course files remain ordinary Windows
files. Each direct child directory is a course, with recursively discovered MP4
lessons. Only the frontend's loopback port is published. Every API/media URL is
served under the existing same-origin `/api` proxy.

SQLite migration 2 adds courses, lessons, resources and single-student progress.
A SQLite backup is created in `data/backups/` before applying the transactional
migration; Phase 1 settings are retained. Versions newer than 2 are rejected.
Course folders define course identities. Lesson paths identify normal rescans;
SHA-256 content hashes recover IDs for unambiguous renames within the same course.
Unchanged size/mtime avoids hashing/probing again. Removed lessons remain in the
database as missing, preserving their progress. Replacing video content at the
same path generates a review warning and retains its progress. Moving a course folder
to a different name is not an automatic course rename in this milestone.

## File rules and tradeoffs

MP4 lessons sort naturally by their relative path, so numbered lesson names
order correctly. Matching UTF-8 SRT files in the same directory convert to WebVTT
on demand. Same-stem resources in the same directory belong to that lesson;
other supported resources are listed as shared course resources. Resource types
are allowlisted; executables and arbitrary source files are not served. Hidden
files and symlinks are skipped, and every download resolves within the library.

ffprobe checks duration and codecs before playback is offered. H.264 8-bit 4:2:0
with AAC/MP3 or no audio is accepted; other or unreadable formats need review or
conversion. This is a conservative compatibility check, not a guarantee for
every browser. Originals are never converted automatically. Full first-import
hashing can take time on large courses; imports serialize while progress writes
remain available. The import request allows up to 10 minutes of proxy inactivity;
very large imports may eventually need background jobs.

Playback saves approximately every 10 seconds and on pause, end, navigation,
or page hiding. Browser termination or power loss can lose the latest checkpoint.
Watched is a viewing state, not a claim of skill mastery. There is no user account
system; this milestone assumes one student on a private local computer.

## Acceptance checks

1. Upgrade the Phase 1 database and retain the welcome setting and backup.
2. Import a course, rescan it, and retain IDs and saved progress.
3. Serve video with HTTP 206 ranges, captions as WebVTT, and attachment downloads.
4. Reject path escapes, handle missing media, and report unsupported codecs.
5. Persist playback position and watched state after application/container restart.
6. Pass backend tests, frontend type/build checks and Compose validation.
7. Connect a real purchased course and verify playback in the student's browser.

Automated fixtures are generated test videos, not purchased content. The final
real-course acceptance check depends on the parent copying lessons into a course
folder and configuring its host path.
