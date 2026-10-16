# Phase 4 verification — 16 October 2026

## Delivered

- `scripts/Academy.ps1`: Windows PowerShell 5.1 installer, requirement checks,
  exact-commit Git worktrees/images, persistent absolute mounts, loopback-only
  ports, manual/automatic updates, status, backup and private guide import.
- Current-user hourly/logon task definition; no elevated/SYSTEM task, stored
  password or automatic prerequisite installation. Overlap prevention and
  deferral after recent playback/quiz events.
- `backend/app/maintenance.py`: consistent SQLite backup including WAL state,
  integrity checks, preservation verification, idle detection and recovery that
  retains the failed database and SQLite sidecars. No schema migration introduced.
- On-disk update transaction supports interruption recovery before Git access.
  Pre-exposure recovery restores the snapshot; post-exposure recovery keeps newer
  learner writes. Previous releases/images/backups remain available.
- `PROJECT_STATUS.md`, `PHASE_4_PLAN.md`, `LAPTOP_DEPLOYMENT.md`, README and agent
  guidance record inventory, downloads, setup, updates and rollout boundaries.
- Windows workflow checks added alongside the existing backend/frontend CI.

## Executed checks

1. Backend Docker suite: **37 passed**, one existing third-party AnyIO deprecation
   warning. Includes new snapshot/restore, WAL, readiness, compatible added schema
   columns/settings, changed-XP rejection, corrupt input and sidecar retention.
2. Windows PowerShell 5.1 checks passed: parsing, JSON handling, paths with spaces,
   loopback/data-mount guards, and real ScheduledTasks definition objects. The
   final tests never register a task.
3. Real isolated Git/Docker integration passed with an independent local Git
   origin, random loopback port, unique Compose project and synthetic learner:
   fresh install, private guide import, first-correct 5 XP, playback/watched and
   setting persistence across an update; idle deferral; no-op without container
   replacement; dirty checkout refusal; offline refusal without losing service;
   interrupted-switch recovery before offline fetch; retention of writes made
   after frontend exposure; and recovery of old images/data after a deliberately
   unhealthy backend release. Test stacks were stopped and fixtures retained.
4. Frontend TypeScript/Vite builds and Compose configuration passed during the
   isolated installations and current development-stack rebuild.
5. Final live read-only smoke checks passed: frontend/same-origin health, three
   local course video ranges/captions, external link inventory and production
   preview exclusion. Both development services are healthy; only
   `127.0.0.1:3000` is published. the learner's **15 XP**, three solved lesson 3 checks
   and completion were unchanged.
6. Created and verified a consistent private initial-transfer snapshot at
   `data/backups/deployments/20261016T194835Z-e31a7c325b10467ba8f1c1da682ee3a5.sqlite3`.
   Its matching JSON manifest verified existing records without writing learner
   progress. This snapshot remains Git-ignored; copy it privately when deploying.

The integration tests do not use the learner's live database or push to GitHub. A first
task-definition test mistakenly registered its disposable test task because of
Windows module autoload replacing its stub; that task was immediately disabled
and removed. Final tests construct definitions without calling registration.
The temporary task was confirmed absent; no updater was enabled on the developer's machine.

## What still needs real-world acceptance

- Publish the final local changes to the existing repository after review.
  The remote may already contain an earlier deployment iteration; the final
  working tree still needs publication. No commits/pushes were made by this task
  to the application repository; test commits used local disposable origins.
- Actual installation on the learner's laptop, its private-repository credentials,
  Docker auto-start and an actual scheduled run under his Windows account.
- Initial private snapshot/video transfer and a check that all paths/media work
  after moving to the laptop. Follow the guide's laptop acceptance checklist.
- Per the developer's choice, new/revised missions transfer privately for now. Automatic
  updates deliver app code, not copyrighted transcripts or authored database rows.
- Retention cleanup/off-device disaster recovery and immutable registry/image
  distribution remain future work. Backups/releases are not pruned automatically.

No new mobile/UI audit was needed: this milestone does not change lesson design
or layout. The guide links to current official Docker, Git and Microsoft setup
documentation rather than silently installing or accepting licenses.
