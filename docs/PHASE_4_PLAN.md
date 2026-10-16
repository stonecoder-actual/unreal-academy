# Phase 4: Laptop deployment and updates

This milestone follows the accepted Phase 3 learning layout and independently
completed quizzes. The full purchased curriculum is an ongoing content task,
not a prerequisite for testing the laptop deployment. See `PROJECT_STATUS.md`.

## Scope

- One Windows PowerShell entry point for prerequisite checks, initial Git install,
  manual updates, scheduled updates, status, consistent backups and private guide
  import. Link to official prerequisites; do not silently install dependencies.
- Existing repository `stonecoder-actual/unreal-academy`, branch `main`.
- Separate source/release checkout, read-only course directory, private Data and
  editable Projects. Only `127.0.0.1:3000` is published by default.
- Current-user Task Scheduler trigger at logon and hourly, no stored Windows
  password or elevated/SYSTEM task. Automatic updates defer for recent learner
  events, handle offline Git and avoid rebuilding unchanged commits.
- Build new images from the exact fetched descendant commit before stopping the
  portal. Refuse dirty checkouts, changed data mounts and exposed network ports.
- Back up SQLite consistently, validate old learner records after migration,
  then expose the frontend. Preserve previous images/releases and failed data.
- Recover interrupted switches before Git access; never restore an older database
  after a frontend may have accepted newer learner writes.
- Document first-time private snapshot transfer and course copy; later app updates
  cannot replace the learner's database or silently distribute purchased curriculum.

## Acceptance

1. PowerShell 5.1 checks pass without needing host Python or Node.
2. Backend tests cover backup/WAL handling, integrity, schema compatibility,
   readiness, progress validation and non-destructive failed-data retention.
3. An isolated local Git origin can install and update an isolated Docker stack.
   Synthetic XP, watched state, playback and settings survive updates.
4. No new commit is a no-op; recent learning defers automatic switch; dirty or
   offline Git cannot take down a healthy installation.
5. Deliberately broken backend release recovers the previous release/data. Both
   pre-exposure and post-exposure interrupted switches preserve learner state.
6. Compose config, frontend build and live development health still pass.
7. Git publication and actual learner laptop setup are separate final steps. Do not
   describe them as completed by isolated tests on the developer's computer.

## Remaining release work

Review/commit/push these changes when authorized, then execute the guide on the
actual laptop and verify its credential manager, Docker auto-start and a real
scheduled run. Verify the repository's intended visibility and access before
distribution. A Git remote URL alone does not establish its visibility.

Private automatic curriculum sync, multi-user accounts, network hosting,
registry publishing and broad AI/gamification additions are outside this phase.
