# Git-ready Udemy deployment — 17 October 2026

The portal now defaults to Udemy only. Git includes the authored takeaways and
quizzes plus all course links. Fresh installation needs no local course files,
private curriculum package, transcript transfer or seeded learner database.
Videos remain on Udemy; progress and XP remain on the individual machine.

## Delivered

- `backend/curriculum/udemy.json`: 221 curriculum items, 207 video lessons and
  890 automatic questions, without raw transcripts, credentials or learner IDs.
- Startup validates and atomically merges the catalogue and guides by external
  identities. An import failure rolls back the whole content transaction.
- Schema 6 stores authored-content hash bindings; no fake transcripts are created.
  Existing databases receive a consistent pre-migration backup.
- Non-Udemy course/detail/guide-index and mastery cards are hidden. Historical
  course records, learning progress and full mastery membership remain saved.
- The Windows installer creates its empty compatibility course directory itself.
  The README no longer asks for a seed, video library or manual content transfer.
- Existing laptop updates distribute both app changes and authored lesson changes,
  retaining local answers, watched state, XP, unlocks and equipped cosmetics.

## Executed verification

- Backend: **67 passed**, one third-party AnyIO deprecation warning.
- Fresh database: one Udemy course, 221 items, 207 published video quizzes,
  890 questions, zero learner XP and zero purchased transcript rows.
- Tested every fresh lesson API for takeaways, 3–6 questions, no activities and
  redacted answer keys.
- Tested revised bundled content across restarts: explanations update, existing
  guide/question IDs and solved answers persist, retries award zero XP, and all
  learner-table fingerprints remain unchanged by the update.
- Independently imported catalogue IDs are reused without duplicate lessons.
- Invalid content is rejected; a late import failure rolls back all catalogue,
  source-binding and guide changes.
- A hidden local course retains its watched state and mastery membership.
- Migrated a disposable copy of the actual development database with the final
  code: every previous learner-table fingerprint and guide/question ID matched.
- Frontend TypeScript/Vite build and both Docker images passed.
- `docker compose config --quiet` passed.
- Real isolated Windows Git/Docker integration passed fresh no-seed/no-course-path
  installation, shipped curriculum coverage, a Git release update, unchanged
  XP/playback/equipment/settings, recent-activity deferral, no-op checks,
  dirty/offline refusal, interrupted-update recovery, preservation of newer
  post-exposure writes and rollback from an unhealthy release. Disposable services
  were stopped after the test.
- Live deployment paused services, made a consistent backup, replaced containers
  and verified previous learner records before reopening the frontend.
- Live verification: one visible course; all four stored course records retained;
  207 published video quizzes and 890 questions; 35 existing XP unchanged.
  Every video quiz API passed after container replacement. Frontend HTTP 200,
  same-origin health ready, both services healthy and only loopback port 3000.

No application/content publication blocker remains. The actual laptop still
needs the README installation and acceptance steps; a new machine starts a new
local learner profile. Existing laptop installations use Update. Git never
uploads, replaces or synchronizes learner progress between machines.
