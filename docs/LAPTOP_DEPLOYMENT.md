# Put Unreal Academy on Jaxon's Windows laptop

Use these steps when you are ready to deploy. They do not install anything on
Jaxon's laptop remotely. App changes must first be committed and pushed to
`https://github.com/stonecoder-actual/unreal-academy` on branch `main`; files only
edited on Sam's computer will not reach the laptop.

## 1. Requirements and downloads

| Requirement | Install/check |
| --- | --- |
| Supported 64-bit Windows, hardware virtualization, enough RAM | Use a supported Windows 11 laptop. Docker's current Windows requirements list 8 GB RAM minimum; 16 GB+ is preferable when also using Unreal Engine. Check the vendor's supported Windows builds/backends before installation. |
| Docker Desktop with Linux containers and Compose 2.24.4+ | [Official Windows download, requirements and setup](https://docs.docker.com/desktop/setup/install/windows-install/). Start Docker Desktop and finish its first-run setup yourself. |
| WSL 2, if using Docker's default WSL backend | [Microsoft WSL installation](https://learn.microsoft.com/en-us/windows/wsl/install), [Docker WSL setup](https://docs.docker.com/desktop/features/wsl/). Administrator setup/reboot may be needed. A working supported Hyper-V backend is also accepted by the script. |
| Git for Windows | [Official Git download](https://git-scm.com/install/windows). Enable Git on PATH and reopen PowerShell after installation. |
| Windows PowerShell 5.1+ | Included with Windows. No Python, Node.js, npm or FFmpeg installation is needed on the laptop; those run in Docker. |
| Storage | The script requires 10 GB free for build/update headroom, **plus** enough room for videos, projects, retained releases and backups. Course libraries can be much larger. |
| Repository access and internet | Use the Windows account Jaxon will actually use. Give its Git credential manager read access to the private repository. Do not put a token/password in the URL or script. Internet is needed for install/updates and Udemy; local learning remains usable offline. |

Turn on Docker Desktop's **Start Docker Desktop when you sign in** setting.
Keep the laptop account signed in for its background update task. The script
does not install software, accept licenses, change machine PATH, enable Windows
features, or grant administrator rights silently. Missing tools stop with links.

## 2. Copy the videos and prepare the first data transfer

Keep these ordinary Windows directories outside OneDrive and Git:

```text
C:\UnrealAcademy\Courses\   purchased folders/videos/captions/resources
C:\UnrealAcademy\Projects\  Jaxon's editable Unreal projects
```

Preserve the course top-level folder names and MP4/SRT relationships. Do not
clone or copy the source repository into the Courses directory. Copying a whole
course is a file operation, not a Git operation. Video files are not bundled in
the application and local video courses must exist on the laptop.

To bring over the current lesson notes/catalogue and Jaxon's progress, make a
consistent database snapshot on Sam's computer after deploying the current code:

```powershell
docker compose exec -T backend python -m app.maintenance backup
```

This prints a backup path such as `/data/backups/deployments/<id>.sqlite3`.
Copy that **snapshot file** privately to the laptop, for example
`C:\UnrealAcademy\Transfer\academy-initial.sqlite3`. Do not copy a live SQLite
file while the app is writing; a raw copy can omit WAL data. The snapshot includes
captured transcripts, authored takeaways/checks, catalogue IDs, progress and XP. It does
not contain MP4 videos or external Udemy authentication. Keep it out of Git.

Use the snapshot only on the first install. If you omit it, you get an empty
academy; import courses through Parent setup, and separately author/import its
lesson notes. A fresh course import creates different IDs, so the initial snapshot
is the easiest way to retain the current curriculum and saved state. Make a fresh
snapshot for this transfer: sections 1–4 now contain 60 video lessons and 284
checks, so a snapshot made before that publication will not contain the batch.

## 3. Install (one command after cloning)

Open ordinary PowerShell **as the same Windows user Jaxon will use**. First clone
and sign in through Git's normal credential prompt if requested:

```powershell
git clone https://github.com/stonecoder-actual/unreal-academy.git C:\UnrealAcademy\Source
cd C:\UnrealAcademy\Source
```

Check prerequisites without deploying:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Academy.ps1 -Action Check
```

Install with the initial private database snapshot:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Academy.ps1 -Action Install -CoursesDirectory C:\UnrealAcademy\Courses -SeedDatabase C:\UnrealAcademy\Transfer\academy-initial.sqlite3
```

For an empty academy, omit `-SeedDatabase`. For another installation directory,
add `-Root "D:\UnrealAcademy"` to **every** command. Paths with spaces are supported.
Do not use a broad root such as `C:\` or an existing development repository.

The installer checks Git, available RAM/storage, Docker's Linux engine and
Compose; fetches the configured branch; builds a release; validates loopback-only
ports and the stable data mount; backs up any initial database; starts/verifies
the app; and registers automatic updates for this user. It refuses to overwrite
an existing database with a seed or reuse another running Docker project.
If registration is denied by Windows policy, the app is still installed: correct
the account/task permission issue and use `-Action EnableUpdates` below.

Open **http://localhost:3000**. In Parent setup confirm the course folder list.
Rescan the existing courses if file metadata changed during transfer; retain
their top-level names and avoid renaming their imported identities. Check a
local video/caption and a Udemy link. Sign in to Udemy on the laptop separately.

For this managed installation, use `Tools\Academy.ps1` for operations. Do **not**
run bare `docker compose up` from `Source/`: that is the development workflow and
can point at a different data directory. The managed launcher always supplies
the installed release and its absolute data/library mounts.

## 4. How updates work

Docker does **not** watch Git. A Windows Scheduled Task calls this script at
user logon (two-minute delay) and hourly while the account is signed in and the
laptop is on AC power. See [Windows task triggers](https://learn.microsoft.com/en-us/powershell/module/scheduledtasks/new-scheduledtasktrigger)
and [Compose container updates](https://docs.docker.com/reference/cli/docker/compose/up/).

The updater fetches `origin/main` and checks whether a newer descendant commit
exists. It does not merge into or reset the source working copy. Each commit gets
a separate Git worktree and image tags, preserving the previous release. Dirty
source/releases and rewritten/diverged Git history stop the update for review.
No new commit means no rebuild/restart. Network/auth/build failures leave the
running version alone. Automatic Git access never opens a login prompt.

After building, automatic updates defer if a quiz answer or playback save was
recorded in the last 30 minutes. They retry next hour. This is based on saved
activity, not a perfect browser-presence detector; an idle page or unsaved radio
selection does not block updates. Manual updates deliberately bypass this idle
check. Builds can use CPU/RAM; the portal has a brief outage while switching.

Before switching, services stop, a SQLite-consistent backup and record
fingerprints are saved, and the new backend starts against the **same Data
directory**. Existing course/lesson identities, settings, playback, attempts,
submissions and XP must match before the frontend starts. Compatible migrations
may add columns; a migration that changes old learner records requires a reviewed
deployment-tool adjustment rather than silently rewriting progress.

If backend startup/migration/persistence validation fails before the frontend
opens, the updater retains the failed database, restores the snapshot and starts
the previous images. If the frontend might already have accepted learner writes,
it never restores an older database automatically; it retains the latest data,
logs the problem, and retries on the next update. Review persistent failures.
Do not manually downgrade images against an incompatible migrated database.

An on-disk deployment transaction also records interrupted switches. After a
power loss or terminated updater, the next run recovers from local images before
contacting Git, so offline Git does not prevent recovery. Before frontend exposure
it restores the pre-switch snapshot; after exposure it resumes the candidate
without restoring old data. A task already switching is allowed to finish if the
laptop changes to battery power.

All successful updates keep `Data\academy.sqlite3`, the library and settings
outside Git/images. They never copy Sam's development database onto an existing
laptop installation, delete volumes, reset XP or import test learner records.

## 5. Everyday commands

```powershell
# Check installed commit, containers and scheduled updater.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\UnrealAcademy\Tools\Academy.ps1 -Action Status

# Update now (choose a time Jaxon is not learning).
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\UnrealAcademy\Tools\Academy.ps1 -Action Update

# Make a consistent private database backup without stopping learning.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\UnrealAcademy\Tools\Academy.ps1 -Action Backup

# Disable / re-enable the hourly/logon task without removing the app or data.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\UnrealAcademy\Tools\Academy.ps1 -Action DisableUpdates
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\UnrealAcademy\Tools\Academy.ps1 -Action EnableUpdates
```

The task is named `unreal-academy-updates`. Its entry point lives in `Tools/`,
outside the changing Git checkout, and is refreshed after successful deployment.
No SYSTEM task, stored Windows password, public listener or Docker socket mount
is added. A lock file prevents two updater processes from switching together.
Log: `C:\UnrealAcademy\Logs\deployment.log`. Installation settings: `install.json`;
running release: `current.json`; absolute mounts: `academy.env`.

Keep Docker Desktop running. If Git credentials expire, sign in interactively in
PowerShell, then run Update again. Offline checks may report errors in the log;
the existing portal still runs. The task does not wake a sleeping laptop or update
while logged out. Sleeping/battery-only use can delay automatic updates.

## 6. What Git updates do not transfer

Git delivers application code, schema migrations, deployment scripts and docs.
Purchased transcripts and authored lesson JSON/database rows are intentionally
excluded. **New lesson notes authored on Sam's computer will not appear automatically
on the laptop through this updater.** They need a separate private transfer and
guide reimport against retained IDs; a safe content-only sync is a later milestone.
Do not solve this by uploading purchased curriculum or overwriting the laptop DB.

Initial transfer: use the snapshot once. Later corrections: privately copy the
guide JSON onto the laptop, preserving lesson/question IDs, then use:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\UnrealAcademy\Tools\Academy.ps1 -Action ImportGuide -GuideFile C:\UnrealAcademy\Transfer\new-lesson.json
```

It privately copies the JSON into Data/imports and calls the guide CLI for the
active release. The guide publishes directly, archives the previous version and
preserves earned XP. It cannot create missing course/transcript records or map
unrelated fresh catalogue IDs; use the initial snapshot and retain identities.

The updater also does not update Docker Desktop, Git, Windows, Unreal Engine or
Udemy content automatically. Manage those through their normal vendor installers.

## 7. Laptop acceptance and recovery checklist

- [ ] Run Check and Install; localhost UI and `/api/health` work.
- [ ] Course names, 60 Udemy video lessons in sections 1–4 and expected XP match
      the fresh seed snapshot. Later sections still have pending notes.
- [ ] Local playback/captions/resources work; Udemy opens in its signed-in browser.
- [ ] Complete a real next check, restart Docker/laptop, and confirm saved XP/playback.
- [ ] Task Scheduler shows the correct Windows user, logon/hourly triggers and success.
- [ ] Publish an intentional tested source commit; confirm a new installed commit
  and unchanged learning state after the next eligible scheduled run.
- [ ] Disconnect internet; verify local learning still works and update errors do
  not stop the running app. Udemy remains an online service.
- [ ] Copy deployment snapshots to a separate private drive periodically. Same-drive
  snapshots and retained releases are not disaster recovery or cross-device sync.

Old releases/images/backups are retained automatically. Monitor disk space;
there is no automatic destructive pruning. If startup fails, inspect the log and
retain the latest Data directory before repair. Never delete Data, use a new
DATA_DIR as a troubleshooting shortcut, or restore an old backup over new progress.

The deployment workflow has an isolated integration check in
`tests/verify-laptop-update.ps1`. It creates its own local Git origin, loopback
port, Docker project and synthetic data; it never pushes to GitHub or uses Jaxon's
database. Actual laptop setup remains a separate acceptance step.

Rechecked for the laptop README update on 16 October 2026: the full isolated
Git/Docker integration passed fresh installation, private lesson import, saved
XP/playback across an update, recent-activity deferral, no-op updates,
dirty/offline refusal, interrupted-update recovery, preservation of newer writes
after frontend exposure, and recovery from an unhealthy release. The disposable
test services were stopped afterward. This verifies the update mechanism;
complete the checklist above on the actual laptop after installing there.
