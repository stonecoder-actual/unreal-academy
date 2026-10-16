# Unreal Academy

Phase 3 adds guided missions, automatic knowledge checks, optional practical
activities, persistent XP and levels to the local course player. Parent setup
handles video libraries, course imports, transcripts and local settings.

For the phased inventory, read [current project status](docs/PROJECT_STATUS.md).
To install on Jaxon's laptop and enable automatic Git updates, use the
[Windows deployment guide](docs/LAPTOP_DEPLOYMENT.md) and `scripts/Academy.ps1`.
That managed installation keeps data outside Git and verifies progress before
opening an updated release. The direct Compose commands below remain the
development workflow; use the managed script for the laptop installation.

## Guided missions

Authored missions publish straight to Jaxon's portal. There is no approval queue.
Existing drafts become available on backend startup. Open a course or the
dashboard's guided mission to learn; lessons without a mission remain watchable.

All correct knowledge checks complete a mission automatically. First correct
answers earn the authored XP once; wrong answers, repeats and watching earn zero.
Levels advance every 100 XP. Practical steps and showing progress to a parent
are optional, with no written submission, grading wait or new practice XP.
Previously earned XP, submissions and playback progress remain saved.

Purchased transcripts and authored JSON stay in private, Git-ignored `data/`.
Publish a mission or apply a correction with:

```powershell
docker compose exec -T backend python -m app.guided /data/path-to-guide.json
```

Import validates and publishes immediately. Reimport updates the existing guide;
keep question IDs stable for corrections so earned XP is not awarded again.
Previous documents are archived under `data/backups/guides/`. Source changes
block outdated guides until they are checked and reimported. Refresh the portal
after importing. See [mission authoring](docs/MISSION_AUTHORING.md).

Schema migration 3 first saves a consistent `data/backups/pre-v3-*.sqlite3`
snapshot. It retains existing courses/playback and adds guided documents, quiz
attempts, a unique-key XP ledger, and practical submissions. Rollback to Phase 2
requires the matching pre-v3 backup while the app is stopped; preserve current
data separately first.

## Architecture

Open http://localhost:3000. nginx serves the compiled frontend and forwards
`/api/` requests to FastAPI on the private Compose network. The browser uses
relative URLs, so frontend and API share one origin without CORS configuration.
Only port 3000 is published, bound to `127.0.0.1`. SQLite lives in the host
`data/academy.sqlite3` file, not in a disposable container. `data/` is ignored
by Git and is outside both Docker build contexts.
Course files are mounted read-only at `/courses`, outside container images.

## Requirements and installation (Windows PowerShell)

Install and start Docker Desktop with Linux containers and Docker Compose.
No host Node.js or Python installation is required. Initial builds require
Internet access to download images and dependencies; the built app runs offline.

```powershell
docker --version
docker compose version
docker info
Copy-Item .env.example .env
docker compose config
docker compose up --build -d --wait
```

Do not overwrite an existing `.env`; edit it instead. `DATA_DIR` defaults to
`./data`. For another Windows location, use a forward-slash absolute path such
as `C:/UnrealAcademy/data` and permit Docker Desktop access to it. Keep this
directory private and outside source control. Visit http://localhost:3000 and
save a welcome message to exercise real database persistence.

## Add your first lessons (parent)

Recommended Windows storage, outside OneDrive and the code repository:

```text
C:\UnrealAcademy\Courses\
  Beginner Unreal\
    01 - Introduction.mp4
    01 - Introduction.srt
    02 - The Editor.mp4
    02 - The Editor.srt
    Resources\
      Project.zip
      Guide.pdf
C:\UnrealAcademy\Projects\
```

Copy a few purchased lessons into their course folder. Preserve original names
and relationships; do not upload them to GitHub. Matching subtitles must have
the same filename stem as the MP4 in the same folder and use UTF-8 encoding.
Subfolders are supported. Numbered names are sorted naturally (`2` before `10`).

Set this line in your local `.env` (copy `.env.example` first if needed):

```dotenv
COURSES_DIR=C:/UnrealAcademy/Courses
```

Use forward slashes for Windows paths, and permit Docker Desktop access to that
directory. `COURSES_DIR` defaults to the Git-ignored `./courses` directory for
local development until you configure another location. After changing the path:

```powershell
docker compose up --build -d --wait
```

Open **Parent setup**, click **Refresh folders**, select the course, and click
**Import / rescan course**. First import reads each video to calculate a hash and
checks its duration/codecs, so large courses take longer. Review import notes.
Add more files later and rescan; ordinary rescans preserve progress and do not
duplicate lessons. Do not rename the top-level course folder after importing:
that currently creates a separate course. Unambiguous lesson renames within a
course preserve progress. A changed video's content generates a warning; saved
progress is retained, so review its watched state if the lesson content changed.
Deleted videos remain listed as missing so their progress is retained.

Resources with the same filename stem beside a lesson attach to that lesson.
Other supported files appear under shared **Course resources**. ZIP, 7z, RAR,
PDF, text/Markdown/JSON/CSV, common images, Unreal project/assets/maps, FBX/OBJ/
Blend and WAV/MP3 resources are supported. Other files and executables are not
served. Package complete Unreal project directories as ZIP files for download;
the app does not generate project archives. Copy/extract editable projects into
your Windows Projects folder before opening them in Unreal Engine.

## Start learning (student)

1. Open http://localhost:3000 and stay on **My learning**.
2. Choose **Start learning** on a course card.
3. Use the lesson list to choose a video and press Play.
4. Turn on captions using the player's subtitle controls, if subtitles exist.
5. Choose a playback speed and download any lesson resources you need.
6. Pause the video before leaving. Your playback position saves on this computer.
7. Open the course again with **Continue learning** to resume an unfinished lesson.

Playback saves approximately every 10 seconds, on pause/end, and when leaving
the lesson or hiding the page. Power loss or an abrupt browser close can lose
the last checkpoint. Reaching the end marks the lesson watched; you can also
use **I watched this lesson** or undo that state to start it again from the
beginning. Watching does not establish
mastery: practice the technique in Unreal Engine. Published guided lessons include
automatically checked quizzes and optional practical work; other videos remain available
without invented quizzes. Progress is for one local student.

## Video compatibility and conversion

For the linked Udemy course, use **Watch on Udemy** to open a selected lecture in
a new tab, then return for published portal activities. Use the portal's manual
completion button after watching/reading; Udemy progress and playback do not sync.
Opening a link and marking completion award zero XP. Parent setup includes private
manifest import and captured transcript review. See
[Udemy integration](docs/UDEMY_INTEGRATION.md) and
[capture/verification results](docs/UDEMY_VERIFICATION.md).

The local-video conversion instructions below apply to imported MP4 courses.

The importer uses ffprobe (included in the backend image) to check formats.
H.264 8-bit 4:2:0 MP4 video with AAC/MP3 or no audio is accepted. Unsupported,
unreadable, or unverified formats are flagged and not offered for playback.
Actual playback also depends on the browser. Originals are never modified.

For a flagged video, create an output folder and convert into the data directory:

```powershell
docker compose exec backend python -c "from pathlib import Path; Path('/data/converted').mkdir(exist_ok=True)"
docker compose exec backend ffmpeg -n -i "/courses/Beginner Unreal/01 - Introduction.mp4" -c:v libx264 -pix_fmt yuv420p -c:a aac -movflags +faststart "/data/converted/01 - Introduction.mp4"
```

`-n` prevents overwriting an existing output. The result is in
`data/converted/` on Windows (or your configured `DATA_DIR`). Copy it and any
matching SRT/resources into a separate playable course folder, then import that
folder. Keep the purchased originals as your archive. Conversion can consume
CPU and take substantial time; run it while Unreal Engine is closed if needed.

## Verification

```powershell
docker compose --profile test run --build --rm backend-tests
docker compose build frontend
docker compose config --quiet
docker compose ps
Invoke-RestMethod http://localhost:3000/api/health
Invoke-WebRequest http://localhost:3000 -UseBasicParsing
./tests/verify-compose.ps1
```

Frontend builds run TypeScript checking followed by Vite compilation. Backend
tests use temporary databases, checking health, reading/writing, persistence
across application instances, invalid input, schema migration/backups, imports,
rescans, moved/replaced/missing videos, captions, resource downloads, byte ranges,
path safety, and newer-schema rejection. Test videos are generated locally by
FFmpeg; no purchased course content is included in the test suite.
The included GitHub Actions workflow runs these checks if the code is hosted
later; no repository publication is required for local use.

The PowerShell smoke test checks the live frontend and same-origin API, writes
a unique message, restarts the backend container, verifies persistence, and
restores the original message. Run it from the repository root with the app up.

For the separate Phase 2 media smoke test, generate synthetic fixtures and start
an isolated stack on loopback port 3001. This uses its own Git-ignored database
and media, never the real course library. Run the backend test command above
first to build the test image, then:

```powershell
$fixturePath = Join-Path $PWD 'data/phase2-verification/courses'
New-Item -ItemType Directory -Force $fixturePath | Out-Null
docker run --rm --mount "type=bind,source=$fixturePath,target=/fixtures" unreal-academy-backend-tests python tests/create_media_fixture.py
docker compose -p unreal-academy-verification -f compose.yaml -f tests/compose.verification.yaml up --build -d --wait
./tests/verify-phase2.ps1
docker compose -p unreal-academy-verification -f compose.yaml -f tests/compose.verification.yaml stop
```

The smoke test checks the full proxy path for importing/rescanning, video byte
ranges, captions, attachment downloads, and progress after restart and container
replacement. It requires loopback port 3001 to be free. Test files stay under
`data/phase2-verification/`; stopping the test stack preserves them for reuse.

Check persistence with a non-sensitive message (this changes the welcome setting):

```powershell
$body = @{welcome_message = 'Persistence check'} | ConvertTo-Json
Invoke-RestMethod http://localhost:3000/api/settings -Method Put -ContentType 'application/json' -Body $body
docker compose restart backend
docker compose up -d --wait
(Invoke-RestMethod http://localhost:3000/api/settings).welcome_message
```

The last command should return `Persistence check`. Refresh the browser to see
the stored message. Container replacement also retains this bind-mounted file:
`docker compose up -d --force-recreate --wait`. Test this after making a backup.

## API and schema

- `GET /api/health`: service and database readiness, Phase 1 indicator.
- `GET /api/settings`: read the persisted welcome message.
- `PUT /api/settings`: JSON `{"welcome_message":"Hello"}`; 1–200 characters.
- `GET /api/library/folders`: discover course folders in the configured mount.
- `POST /api/courses/import`: JSON `{"folder":"Beginner Unreal"}`; import/rescan.
- `GET /api/courses` and `GET /api/courses/{id}`: catalogue and lesson details.
- `GET /api/lessons/{id}/video`: MP4 streaming, including HTTP byte ranges.
- `GET /api/lessons/{id}/captions`: matched SRT converted to WebVTT.
- `GET /api/resources/{id}/download`: original resource as an attachment.
- `PUT /api/lessons/{id}/progress`: JSON `{"position":42,"watched":false}`;
  omit `watched` to preserve its current value.
- `GET /api/xp`: XP total, current level and progress to the next level.
- `GET /api/lessons/{id}/guide`: published guided lesson and saved learning state.
- `POST /api/guides/{id}/questions/{question}/answer`: JSON `{"answer":"exact option text"}`.
- Legacy practice submission, review and publication endpoints remain for historical compatibility; the current portal does not use them.

`backend/app/schema.sql` initializes schema version 1 using SQLite `user_version`.
The `settings` table has a text primary key and non-null text value. Initial data
uses `INSERT OR IGNORE`, so restarts preserve edits. SQL writes are parameterized
and committed in a transaction. Startup rejects databases with a newer version.
`migration_002.sql` upgrades to version 2 with courses, lessons, resources and
lesson progress. Startup first saves a consistent pre-upgrade SQLite backup to
`data/backups/pre-v2-*.sqlite3`, then applies the migration transactionally. The
welcome setting is retained. Newer database versions are rejected. Never restore
a Phase 1 image against a version 2 database; use the matching version 1 backup
while the app is stopped, preserving the current database separately first.

## Operations, backups, updates, and rollback

```powershell
docker compose logs --tail 100
docker compose stop
docker compose start
docker compose down
```

`down` removes containers and networks but retains the host data directory.
Never delete `data/` to troubleshoot. For a consistent backup, stop the app,
copy the entire data directory to a dated folder under `backups/` (Git-ignored),
then start the app. A local backup is not protection against loss of the laptop;
retain a separate private copy as appropriate.

Before upgrading, stop and back up the data, retain the previous source revision
or images, review schema compatibility, then run `docker compose up --build -d
--wait`. Updates are explicit; source pushes do not update this computer.
For rollback, restore compatible previous code/images. If schema compatibility
changed, restore the matching backup while containers are stopped; preserve the
current database separately first. Do not blindly run older code on newer data.

## Troubleshooting and limitations

If `docker` is not found, add its installation `resources/bin` directory to PATH
and restart the terminal. If the engine is unavailable, start Docker Desktop.
If port 3000 is occupied, stop the conflicting service before launching.
For an unavailable API, check `docker compose ps` and backend logs; health checks
must pass before the frontend starts. For storage failures, check that Docker can
write to `DATA_DIR`. The UI reports connection and save failures rather than
pretending they succeeded.

This is an unauthenticated localhost development app. Parent setup is navigation,
not an access-control boundary. Keep its loopback binding;
LAN deployment is a separate milestone. Resource limits are not imposed yet;
adjust Docker Desktop CPU/memory settings to coexist with Unreal Engine.
Runtime images use version tags and direct dependencies are pinned, with a
frontend lockfile; image digests and a complete Python transitive lock are not
yet used. No purchased curriculum is bundled. First imports hash entire videos;
the synchronous import design is intended for modest local courses. Hidden files
and symlinks are skipped. Missing or ambiguous subtitles are not guessed. Moving
a course to a different top-level folder name is not automatically reconciled.

## Layout

`frontend/` contains the student library/player, parent setup, TypeScript build and nginx proxy.
`backend/` contains the API, import/media logic, schema/migration and pytest suite.
`compose.yaml` defines runtime services and an isolated test profile.
`docs/` contains project requirements and agent instructions.
`.github/workflows/verify.yml` provides automated build/test verification.

## Learner interface redesign

The dashboard, course library, learning workspace, progress profile and parent
setup screens share a responsive visual system. XP and learning records reflect
saved results. Badge and cosmetic concepts remain development-only demonstrations.

See [design audit and rationale](docs/DESIGN_REDESIGN.md) and
[verification results and limitations](docs/DESIGN_VERIFICATION.md).
Run `./tests/verify-design.ps1` for read-only live endpoint/media smoke checks.
The isolated UI test override is `tests/compose.design-verification.yaml`; use
project name `unreal-academy-design-verification` with both Compose files to keep
its database separate. Never run reward tests against Jaxon's live database.
