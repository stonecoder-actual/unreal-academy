# Laptop installation and updates

## Requirements

- Windows with hardware virtualization and a supported Docker Desktop backend.
- [WSL 2 setup](https://learn.microsoft.com/en-us/windows/wsl/install).
- [Docker Desktop download/setup](https://docs.docker.com/desktop/setup/install/windows-install/):
  use Linux containers; keep Docker running and enable startup at sign-in.
- [Git for Windows](https://git-scm.com/install/windows) with command-line access
  and Git Credential Manager. Reopen PowerShell after installation.
- At least 10 GB free for builds, releases and backups, plus Unreal Engine/project storage.

The installer checks Git, Docker Linux engine, Compose 2.24.4+ and disk space.
No host Python/Node/SQLite or local video library is required. Use the learner's
Windows account. Install Unreal Engine separately for Udemy activities.

## Install

```powershell
git clone https://github.com/stonecoder-actual/unreal-academy.git C:\UnrealAcademy\Source
Set-Location C:\UnrealAcademy\Source
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Academy.ps1 -Action Check
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Academy.ps1 -Action Install
```

Open http://localhost:3000. Sign in to Udemy separately. All 221 curriculum links
and 207 video lesson quizzes are installed automatically. No private seed or
transfer package is needed. A fresh machine starts with zero progress/XP.

The script creates an empty Courses folder for the read-only compatibility
mount; no files need to be placed there. Local courses are hidden for now.
Existing installations retain their historical courses and progress in storage.

## Updates and persistence

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\UnrealAcademy\Tools\Academy.ps1 -Action Update
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\UnrealAcademy\Tools\Academy.ps1 -Action Status
```

The installed task `unreal-academy-updates` checks the configured Git branch at
sign-in and hourly while signed in/on AC power. Docker and internet must be
available. Automatic updates defer after learning activity within 30 minutes;
manual Update bypasses this delay. No new commit means no rebuild or restart.
Refresh the browser after deployment. Sleeping/logged-out laptops do not update.

The updater builds the selected commit before downtime, retains the old release,
backs up SQLite, starts the candidate backend and verifies previous learner
records before opening the frontend. Bundled lesson updates merge by external
course/lecture identities and retain guide/question identities and XP awards.
It never copies another machine's learner database into an existing installation.

| Path under `C:\UnrealAcademy` | Purpose |
| --- | --- |
| `Source`, `Releases` | Git checkout and versioned app releases |
| `Data\academy.sqlite3` | Local progress, answers, XP, rewards and catalogue |
| `Data\backups` | Consistent migration/deployment and guide snapshots |
| `Tools\Academy.ps1` | Stable updater entry point |
| `Logs\deployment.log` | Setup/update diagnostics |
| `install.json`, `current.json`, `academy.env` | Installation, active release and absolute mounts |

Progress stays in Data outside Git/releases. Never delete or replace Data, reseed
an existing installation, or install over it to apply updates. The old optional
SeedDatabase/ImportGuide parameters remain for compatibility; neither is needed
for this Udemy setup. Raw purchased transcripts and learner data stay out of Git.

## Backup and troubleshooting

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\UnrealAcademy\Tools\Academy.ps1 -Action Backup
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\UnrealAcademy\Tools\Academy.ps1 -Action EnableUpdates
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\UnrealAcademy\Tools\Academy.ps1 -Action DisableUpdates
```

- Command missing: reopen PowerShell; verify its installation is on PATH.
- Docker unavailable: start Docker Desktop and check Linux-container mode.
- Git access expired: sign in interactively with repository read access, then Update.
- Update failed: inspect the log and retain current Data. A candidate failing before
  frontend exposure can recover the saved database/release. Once frontend access
  could have accepted new progress, automatic recovery retains newer learner data.
- Offline: the installed portal still runs; Udemy videos and Git updates need internet.
- Copy completed snapshots to a separate private drive. Same-drive backups do not
  protect against drive loss. Old releases/backups are retained; no destructive pruning.

## Acceptance on the actual laptop

- [ ] Fresh install shows only Udemy: 221 items, 207 video quizzes, 890 questions.
- [ ] Udemy opens in a signed-in tab; notes and quizzes work in the portal.
- [ ] Answer a check, restart Docker/laptop and verify saved XP/completion.
- [ ] Perform Update and verify the same answers, watched state and equipped rewards.
- [ ] Scheduled task runs under the correct user; offline use leaves the app running.
- [ ] Backups exist and completed copies are stored privately off-device.

`tests/verify-laptop-update.ps1` exercises isolated fresh Git installation and
deployment/recovery with disposable data. It never uses the learner's database.
