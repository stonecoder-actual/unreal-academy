# Unreal Academy

The learning portal combines course videos with transcript-based key takeaways,
automatic knowledge checks, persistent XP and levels. Parent setup
handles video libraries, course imports, transcripts and local settings.

**Installing on Jaxon's laptop? Start with the walkthrough below.** It assumes
nothing is installed and uses the managed installer to keep progress outside
Git and Docker images. The later development commands are for Sam's coding
checkout. See [project status](docs/PROJECT_STATUS.md) for the phased inventory.

## Install on a new Windows laptop

### 1. Install the requirements

Do the setup while signed into **the Windows account Jaxon will use**. A parent
handles administrator prompts, software terms and GitHub/Udemy sign-in.

| Install | What to do |
| --- | --- |
| Windows and hardware | Use a supported 64-bit Windows laptop with virtualization enabled. Check [Docker's Windows requirements](https://docs.docker.com/desktop/setup/install/windows-install/) before downloading. The installer checks for an 8 GB-class machine and at least 10 GB free for builds; videos, Unreal projects, backups and retained releases need additional space. |
| WSL 2 | Follow [Microsoft's WSL setup](https://learn.microsoft.com/en-us/windows/wsl/install). Open **PowerShell as administrator**, run `wsl --install`, restart when requested, and complete its first-run setup. Then run `wsl --update` and `wsl --version`. Docker's supported Hyper-V backend is an alternative. |
| Docker Desktop | Download from [Docker's official Windows installation page](https://docs.docker.com/desktop/setup/install/windows-install/). Install with the WSL 2 backend, open Docker Desktop, complete first-run setup and wait for the engine to be running. Use **Linux containers**. Enable **Start Docker Desktop when you sign in** in its settings. |
| Git for Windows | Download from [the official Git site](https://git-scm.com/install/windows). Keep Git Credential Manager enabled and choose the installer option that makes Git available from the command line. Close and reopen PowerShell afterward. |
| Browser and course tools | Use a browser for the portal and sign into the purchased Udemy course on this laptop. Install [Epic Games Launcher and Unreal Engine](https://www.unrealengine.com/download) separately for following the course activities. They are not required to start the portal. |

Windows PowerShell is included with Windows. **You do not need to install Python,
Node.js, npm, FFmpeg or SQLite on the laptop**; the application dependencies run
inside Docker. Internet is needed for installation, Git updates and Udemy videos.
Installed local lessons and knowledge checks can work offline.

Open a **new ordinary PowerShell window**, not the administrator setup window,
and check:

```powershell
git --version
docker --version
docker compose version
docker info --format '{{.OSType}}'
```

The last command must print `linux`; Compose must be version 2.24.4 or newer.
If a command is not recognized, reopen PowerShell first. If still missing, search
Windows for **Edit environment variables for your account**, edit **Path**, and
add the installed tool's folder. Typical folders are:

```text
Git:    C:\Program Files\Git\cmd
Docker: %LOCALAPPDATA%\Programs\DockerDesktop\resources\bin
        or C:\Program Files\Docker\Docker\resources\bin
```

Choose the folder that actually contains the executable. Add an entry rather
than replacing the existing Path, then reopen PowerShell. If `docker info` cannot
connect, start Docker Desktop and resolve its WSL/setup message before continuing.

### 2. Bring the private curriculum and videos

**GitHub contains the app, not the purchased curriculum or Jaxon's saved data.**
To install the course catalogue, transcripts and all currently authored lessons
(including Udemy sections 1–4), use a consistent database snapshot from Sam's
computer **once, during the first installation**.

On **Sam's computer**, open PowerShell in the existing running development
checkout and run:

```powershell
docker compose exec -T backend python -m app.maintenance backup
```

The result includes a `backup` path such as
`/data/backups/deployments/<timestamp-and-id>.sqlite3`. With this checkout's
`DATA_DIR=./data`, that same file is in
`data\backups\deployments\` inside the checkout. If `DATA_DIR` was customized,
look under that directory instead. Copy **the snapshot named by this command**
privately by USB or another private file transfer; do not copy the active
`academy.sqlite3` while it is in use. The snapshot contains the current catalogue,
lesson checks, playback state, answers and XP; videos are separate.

On **Jaxon's laptop**, create these folders in ordinary PowerShell:

```powershell
New-Item -ItemType Directory -Force C:\UnrealAcademy\Courses, C:\UnrealAcademy\Projects, C:\UnrealAcademy\Transfer
```

Save the snapshot as
`C:\UnrealAcademy\Transfer\academy-initial.sqlite3`. Copy the local course folders
from Sam's `C:\UnrealAcademy\Courses` into the laptop's `Courses` directory,
preserving folder names and matching MP4/SRT files. Keep editable UE5 projects
under `Projects`. Udemy videos remain on Udemy and do not need to be copied.
Keep all these directories outside OneDrive and outside the source checkout.

An empty `Courses` directory is acceptable for Udemy-only use. Missing local
videos will remain unavailable until copied. Omitting the initial snapshot gives
an empty academy, not the authored Udemy curriculum. A later Git update does not
fill it in. For this installation, use the snapshot.

### 3. Clone and install

In ordinary PowerShell under Jaxon's Windows account:

```powershell
git clone --branch main https://github.com/stonecoder-actual/unreal-academy.git C:\UnrealAcademy\Source
Set-Location C:\UnrealAcademy\Source
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Academy.ps1 -Action Check
```

If Git asks, sign in through Git Credential Manager with an account that can read
the private repository. Do not paste a password or access token into these
commands. If `Source` already exists, use the existing checkout; do not delete it
or clone over it. A previously installed academy should use **Update** below.

Once Check passes, install:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Academy.ps1 -Action Install -CoursesDirectory C:\UnrealAcademy\Courses -SeedDatabase C:\UnrealAcademy\Transfer\academy-initial.sqlite3
```

The installer builds the app, starts it, verifies the seeded learner records and
registers automatic Git updates for this Windows user. Initial downloads/builds
can take several minutes. It refuses to replace an existing learner database.
Use the default root `C:\UnrealAcademy`; for another root, follow the
[detailed deployment guide](docs/LAPTOP_DEPLOYMENT.md).

### 4. Open and verify

Open **[http://localhost:3000](http://localhost:3000)** and bookmark it. Compare
Jaxon's XP, completed checks and course list with Sam's seed snapshot. Udemy
sections 1–4 should have notes and questions. In Parent setup, rescan existing
local courses if copied-file metadata differs; preserve their folder names.
Open a local video/caption if using local courses and sign into Udemy separately.

Check the running installation and same-origin API:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\UnrealAcademy\Tools\Academy.ps1 -Action Status
Invoke-RestMethod http://localhost:3000/api/health
```

Health should report `status: ok` and `database: ok`. On later days, start Docker
Desktop, wait for its engine/containers, then open the bookmark. Normal container
restarts retain the database. If the page is unavailable, check Docker Desktop
and run Status; do not reinstall into a different data directory.

## How Jaxon gets updates without losing progress

### Automatic updates

Sam must **commit and push changes to GitHub's `main` branch**. A commit left
only on Sam's computer does not reach the laptop. Docker does not watch Git;
the installed Windows task `unreal-academy-updates` runs the updater at sign-in
(after two minutes) and hourly while Jaxon's account is signed in and the laptop
is on AC power. Keep Docker Desktop running, GitHub access working and internet
connected. A sleeping or logged-out laptop will update later.

The updater fetches `origin/main`, builds a new release and defers the automatic
switch if playback or a quiz answer was saved in the last 30 minutes. It retries
on a later run. An idle page or an unsaved answer does not count as saved activity;
save/finish the current check when taking a break. There is a brief outage during
the switch. After an update, refresh the browser to load the new frontend.

If Windows did not allow automatic-task registration during installation, run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\UnrealAcademy\Tools\Academy.ps1 -Action EnableUpdates
```

### Update now

When Jaxon is finished learning for the moment, run this in ordinary PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\UnrealAcademy\Tools\Academy.ps1 -Action Update
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\UnrealAcademy\Tools\Academy.ps1 -Action Status
```

Manual Update bypasses the recent-activity deferral. Wait for success, refresh
http://localhost:3000, and confirm XP and completed checks. No new commit means
no rebuild or restart. Use this command instead of manually pulling and running
Compose from `Source`; it fetches Git and deploys the correct saved data mounts.

### Where progress lives and how it is protected

| Location | Purpose |
| --- | --- |
| `C:\UnrealAcademy\Data\academy.sqlite3` | Persistent catalogue, transcripts, lesson checks, answers, playback progress and XP. This is outside Git and images. |
| `C:\UnrealAcademy\Data\backups\deployments\` | Consistent database snapshots and record fingerprints made before switching releases. |
| `C:\UnrealAcademy\Source` and `Releases` | Application code and versioned releases; replacing containers does not replace Data. |
| `C:\UnrealAcademy\Logs\deployment.log` | Installation and update results/errors. |

Before exposing the new frontend, the updater checks database integrity and
compares existing learner records with the pre-update snapshot. It verifies
course/lesson identities, settings, playback, quiz attempts, historical
submissions and XP. If these checks fail, it does not expose the candidate as a
successful update. Recovery before frontend exposure can return to the previous
snapshot/images; after possible new learner writes, it keeps the latest data
instead of restoring an older snapshot. See the [recovery details](docs/LAPTOP_DEPLOYMENT.md#4-how-updates-work).

**For every later update, retain the same Data directory. Do not copy Sam's
database over Jaxon's, rerun the seed installation, delete Data, or switch
`DATA_DIR` to an empty folder.** GitHub is not a backup of learner progress.
Make an additional private backup periodically:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\UnrealAcademy\Tools\Academy.ps1 -Action Backup
```

Copy completed snapshot files to a separate private drive for protection from
laptop/drive loss. If an update fails, read the deployment log and retain the
latest Data before repair; do not restore an older database over newer progress.

### New or corrected lesson content is a separate private transfer

Git updates deliver the application, deployment scripts and documentation.
Purchased transcripts and authored checks are private and **do not sync through
GitHub**. The first-install snapshot brings today's curriculum. For later new or
corrected notes, privately copy the authored JSON from Sam's computer and import
it into the existing laptop database:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\UnrealAcademy\Tools\Academy.ps1 -Action ImportGuide -GuideFile C:\UnrealAcademy\Transfer\lesson-63.json
```

The filename above is an example; use the actual supplied JSON. Retain its lesson
and question IDs so earned XP stays associated with the same checks. Import
publishes directly and preserves existing progress; it does not replace the
database. The initial seed retains the catalogue/transcript IDs those files
depend on. See [private content transfer](docs/LAPTOP_DEPLOYMENT.md#6-what-git-updates-do-not-transfer).

## Lesson takeaways and questions

The Blueprints Udemy course is first on the homepage and is Jaxon's starting
course. For each authored video lesson, he follows the instructor on Udemy, reads
the key takeaways here, then answers 3–6 automatically checked questions. The
number depends on the lesson's complexity. Udemy supplies the UE5 activities;
the portal does not add guided missions, projects or written explanations.

First correct answers earn XP once; wrong answers, repeated successes and
watching earn zero. All correct checks finish the lesson quiz, with no parent
grading or approval. Existing progress and earned XP remain saved.

Udemy sections 1–4 now have authored notes for all 60 videos, with 284 knowledge
checks. Readings and Udemy quizzes continue to open on Udemy. Later sections
remain watchable while their portal notes/questions are prepared. See the
[curriculum verification report](docs/UDEMY_SECTIONS_1_4_VERIFICATION.md).

Private transcripts and lesson JSON stay in Git-ignored `data/`. Imports publish
directly; keep existing question IDs when correcting content to preserve rewards.
Previous documents are archived locally. See
[lesson authoring](docs/MISSION_AUTHORING.md) for the development and laptop
import commands. Git delivers application updates; private lesson content is
transferred separately without replacing the laptop database.

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

## Development checkout setup (Sam's computer)

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
mastery: practice the technique in Unreal Engine. Authored lesson notes include
key takeaways and automatic knowledge checks; other videos remain available
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
