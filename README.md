# Unreal Academy

Local learning portal built with React, FastAPI, SQLite and Docker. Supports
local videos, Udemy links, lesson takeaways, automatic knowledge checks and XP.
Runs at **http://localhost:3000**; published ports bind to `127.0.0.1` only.

## Laptop installation

### 1. Install requirements

- **WSL 2:** follow [Microsoft's setup](https://learn.microsoft.com/en-us/windows/wsl/install).
  Run `wsl --install` in administrator PowerShell, restart if requested, then
  run `wsl --update`.
- **Docker Desktop:** [download and requirements](https://docs.docker.com/desktop/setup/install/windows-install/).
  Use Linux containers with WSL 2. Start Docker Desktop and enable startup at sign-in.
- **Git for Windows:** [download](https://git-scm.com/install/windows).
  Enable command-line access and Git Credential Manager during installation.

Use the learner's Windows account for Docker and portal setup. No host Python,
Node.js, FFmpeg or SQLite installation is needed. Allow at least 10 GB free for
builds, plus storage for courses, projects, releases and backups.

Open a new ordinary PowerShell window and verify:

```powershell
git --version
docker compose version
docker info --format '{{.OSType}}'
```

Compose must be 2.24.4+; the last command must print `linux`. If a command is
missing, reopen PowerShell or add its installed executable folder to your user
Path. Complete [Docker/WSL setup](docs/LAPTOP_DEPLOYMENT.md#1-requirements-and-downloads)
before continuing. Install [Unreal Engine](https://www.unrealengine.com/download)
separately for course activities.

### 2. Transfer curriculum and initial data

GitHub contains application code, **not purchased curriculum or learner data**.
On the existing computer, run this from its running development checkout:

```powershell
docker compose exec -T backend python -m app.maintenance backup
```

Copy the returned snapshot privately to the laptop as
`C:\UnrealAcademy\Transfer\academy-initial.sqlite3`. A returned path under
`/data/backups/` maps to the configured host data directory's `backups` folder.
Use this consistent snapshot, not a copy of the active database.

Create the laptop folders and copy local course folders into `Courses`, keeping
their names and matching MP4/SRT files. Keep these directories outside OneDrive.
Udemy-only use can leave `Courses` empty.

```powershell
New-Item -ItemType Directory -Force C:\UnrealAcademy\Courses, C:\UnrealAcademy\Projects, C:\UnrealAcademy\Transfer
```

The initial snapshot includes the catalogue, transcripts, authored checks,
progress and XP. Videos transfer separately. Without a seed, installation starts
with an empty academy. **Seed only on the first installation.**

### 3. Clone and install

Run in ordinary PowerShell using the learner's Windows account. Sign in through
Git Credential Manager with repository read access if prompted.

```powershell
git clone --branch main https://github.com/stonecoder-actual/unreal-academy.git C:\UnrealAcademy\Source
Set-Location C:\UnrealAcademy\Source
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Academy.ps1 -Action Check
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Academy.ps1 -Action Install -CoursesDirectory C:\UnrealAcademy\Courses -SeedDatabase C:\UnrealAcademy\Transfer\academy-initial.sqlite3
```

Open **http://localhost:3000**. Verify the course list, completed checks and XP.
Use Parent setup to rescan copied local courses if needed. Sign into Udemy
separately. On later days, start Docker Desktop and open the same address.
For an existing installation, use Update below rather than Install.

## Updates

Changes must be **committed and pushed to `main`**. The installed Windows task
checks Git at sign-in and hourly while the account is signed in, the laptop is
on AC power, and Docker/internet are available. Automatic switches defer after
playback or quiz activity saved within the last 30 minutes. Docker itself does
not watch Git. Refresh the browser after an update.

To update manually, finish the current lesson first, then run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\UnrealAcademy\Tools\Academy.ps1 -Action Update
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\UnrealAcademy\Tools\Academy.ps1 -Action Status
```

Manual updates bypass the activity delay. No new commit means no restart.
If task registration failed during installation, run the same script with
`-Action EnableUpdates`. Use the managed script rather than manually pulling
and running Compose from `Source`.

### Progress and XP protection

- Learner data stays in `C:\UnrealAcademy\Data\academy.sqlite3`, outside Git and images.
- Each release switch creates a consistent backup and verifies existing learner
  records before opening the new frontend. Failed checks block that release.
- Keep the same Data directory. **Never replace the laptop database with another
  computer's database after initial setup, delete Data, or reseed during updates.**
- Back up periodically and copy completed snapshots to a separate private drive:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\UnrealAcademy\Tools\Academy.ps1 -Action Backup
```

Backups are under `Data\backups\deployments`; logs are under
`Logs\deployment.log`. See [update recovery](docs/LAPTOP_DEPLOYMENT.md#4-how-updates-work)
if an update fails. Retain current data before repair.

### Private lesson updates

New transcripts and authored checks transfer separately from Git. Copy the
supplied lesson JSON privately, preserve lesson/question IDs, then import:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\UnrealAcademy\Tools\Academy.ps1 -Action ImportGuide -GuideFile C:\UnrealAcademy\Transfer\lesson.json
```

All 207 Udemy videos now have takeaways and 890 checks. The complete private
transfer package is `data/udemy/private-transfer-2026-10-17.zip` on the authoring
computer. Its README covers batch import into an originally seeded laptop;
Git updates alone do not deliver it.

Import publishes directly and preserves earned XP; it does not replace the
database. Udemy provides practical activities. Portal checks award XP once per
correct question; watching and repeated successes award none.

## Levels and rewards

Developer Guild has 50 levels and ten permanent title/emblem unlocks, from
Newbie to Unreal Master. Level 2 needs 50 XP; Level 50 needs 28,320 XP. Equip
earned titles and emblems in **My progress**. Master also requires 85% of track
checks overall and 75% in each course after the complete track is finalized.
Existing XP is retained. See [progression rules](docs/PROGRESSION.md).

## Development

For a development checkout only; laptop installations use the managed script.
Copy `.env.example` to `.env` once and configure `COURSES_DIR` and `DATA_DIR`.
Keep data and purchased materials out of Git. Course mounts are read-only.

```powershell
docker compose up --build -d --wait
docker compose --profile test run --build --rm backend-tests
docker compose build frontend
docker compose config --quiet
Invoke-RestMethod http://localhost:3000/api/health
```

The frontend proxies `/api` to FastAPI on the same origin. SQLite retains progress
across container replacements. This is a single-learner localhost app; Parent
setup is not authentication.

## Documentation

- [Laptop setup, troubleshooting and recovery](docs/LAPTOP_DEPLOYMENT.md)
- [Project status](docs/PROJECT_STATUS.md)
- [Lesson authoring and private imports](docs/MISSION_AUTHORING.md)
- [Udemy integration](docs/UDEMY_INTEGRATION.md)
- [Local-course import plan and behavior](docs/PHASE_2_PLAN.md)
