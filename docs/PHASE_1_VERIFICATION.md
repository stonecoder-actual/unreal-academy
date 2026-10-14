# Phase 1 verification

Verified locally on October 13, 2026 using Docker Desktop 29.8.2 and
Docker Compose 5.5.1 with Linux containers.

- Read `docs/AGENTS.md` and `docs/PROJECT_SPEC.md`; no root `AGENTS.md` exists.
- `docker compose config`: passed. Only `127.0.0.1:3000` is published;
  the backend has no published host port.
- `docker compose --profile test run --build --rm backend-tests`: 3 passed.
  One third-party Starlette/AnyIO deprecation warning, with no test failures.
- `docker compose up --build -d --wait`: passed; both services healthy.
- Frontend build: TypeScript checking and Vite 6.4.4 production build passed.
- npm dependency audit after updating Vite: zero reported vulnerabilities.
- Frontend HTTP response: 200, with the Unreal Academy page title.
- `http://localhost:3000/api/health`:
  `{"status":"ok","database":"ok","phase":1}`.
- `tests/verify-compose.ps1`: passed live settings write/read, backend container
  restart, readiness checks, and persistence read after restart. Restored the
  original welcome message afterward.
- Host SQLite file exists at `data/academy.sqlite3`; `git check-ignore` confirms
  it is excluded from Git.

The app was left running at http://localhost:3000. No GitHub repository was
created or published. Existing project documents were preserved.

## Remaining limitations

No connected browser was available for a visual UI check. HTTP and asset build
verification passed, but browser rendering and interactive form use should be
checked manually by opening the page, confirming the connected status, saving
a message, and refreshing it. The fetch URLs are relative and the API is proxied
on the same origin, avoiding cross-origin requests by construction.

The backend test warning is a dependency deprecation warning. Dependencies and
container version tags are pinned at the direct level, but Python transitive
dependencies and image digests are not fully locked. Future milestones should
add migrations for any new schema and retain pre-upgrade backups.
