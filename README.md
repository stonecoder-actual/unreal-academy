# Unreal Academy

Local Udemy learning portal: 207 videos, key takeaways, 890 automatic knowledge
checks and XP. Lesson links and portal curriculum are included in Git.
Videos and practical activities stay on Udemy; sign in there separately.

## Install on a Windows laptop

1. Install [WSL 2](https://learn.microsoft.com/en-us/windows/wsl/install),
   [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)
   and [Git for Windows](https://git-scm.com/install/windows). Restart if prompted.
2. Start Docker Desktop in **Linux containers** mode. Enable startup at sign-in.
3. Open ordinary PowerShell under the learner's Windows account:

```powershell
git clone https://github.com/stonecoder-actual/unreal-academy.git C:\UnrealAcademy\Source
Set-Location C:\UnrealAcademy\Source
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Academy.ps1 -Action Check
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Academy.ps1 -Action Install
```

Open **http://localhost:3000**. All Udemy lessons are ready. No course-folder,
database, transcript or lesson-file transfer is needed. New installations start
with zero XP. Repository access may require Git sign-in. No host Python, Node.js
or SQLite installation is needed. Install [Unreal Engine](https://www.unrealengine.com/download)
separately for the instructor's activities.

On later days, start Docker Desktop and open the same address.

## Updates

The installer checks Git at sign-in and hourly while signed in, on AC power,
with Docker and internet available. Automatic updates wait until no learning
activity has been saved for 30 minutes. Refresh the browser after an update.
Both app changes and revised portal lessons now arrive through Git.

To update immediately, finish the current lesson and run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\UnrealAcademy\Tools\Academy.ps1 -Action Update
```

Use **Update**, not Install, on an existing installation. If scheduled task
registration failed, run the same script with `-Action EnableUpdates`.

## Progress stays on the laptop

- SQLite at `C:\UnrealAcademy\Data\academy.sqlite3` stores progress, answers, XP
  and unlocked/equipped rewards, outside Git and release images.
- Updates merge curriculum using stable course/lesson/question identities.
  Existing earned XP is retained; correct answers award XP once.
- Each deployment backs up and verifies existing learner records before opening
  the updated portal. Never delete Data, reseed, or replace its database.
- Non-Udemy courses are hidden for now. Existing records remain saved.
- Progress is per machine; cloning on another laptop starts a separate learner.

Manual backup:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\UnrealAcademy\Tools\Academy.ps1 -Action Backup
```

Copy completed backups from `Data\backups\deployments` to a separate private
drive periodically. Git is not a backup for learner progress.

## Development

From a normal checkout with Docker running:

```powershell
docker compose up --build -d --wait
docker compose --profile test run --build --rm backend-tests
docker compose build frontend
docker compose config --quiet
```

Compose defaults to ignored `./data` for local persistence. Keep that directory
between updates. Laptop installations use the managed script above instead.
Only `127.0.0.1:3000` is published; `/api` uses the frontend's origin.

[Laptop troubleshooting](docs/LAPTOP_DEPLOYMENT.md) ·
[Project status](docs/PROJECT_STATUS.md) ·
[Levels and rewards](docs/PROGRESSION.md) ·
[Bundled curriculum](docs/BUNDLED_CURRICULUM.md)
