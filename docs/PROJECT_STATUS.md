## Current learning format — 16 October 2026

Sam simplified Udemy learning: review each video's actual transcript, highlight
the key takeaways Jaxon needs to understand, and provide 3–6 automatically
checked multiple-choice questions, depending on the video's complexity. Place
all questions after the takeaways. No guided missions, generated activities,
projects, reflection prompts, written explanations or parent grading. Udemy's
instructor supplies the practical activities; Jaxon follows along in UE5.
Put the purchased Blueprints Udemy course first on the homepage and feature it
as his starting course. Keep saved answers, progress and once-only XP.

This replaces earlier mission/optional-activity plans. The three already-authored
Udemy lessons are being converted now; authoring the remaining video curriculum
is the next step with Sam. Captured transcripts are source material, not finished
lessons. Continue publishing lesson notes directly, with private manual content
transfer and automatic Git application updates as already agreed.

# Unreal Academy inventory — 16 October 2026

This is the current roadmap checkpoint. Historical phase documents record what
was true when each milestone shipped; the direct-publication policy in
`AGENTS.md`, `PROJECT_SPEC.md` and `MISSION_AUTHORING.md` supersedes their old
parent approval requirements. Sam is satisfied with the lesson design/layout.

| Milestone | Status | Delivered / remaining |
| --- | --- | --- |
| Phase 1: foundation | Complete | React/TypeScript, FastAPI, persistent SQLite, Compose, loopback-only port 3000, same-origin API, health checks, builds and automated tests. |
| Phase 2: local learning | Complete | Three local courses, natural lesson ordering, MP4 playback/ranges, SRT captions, resources, saved playback/watched state, imports/rescans that retain identities. |
| Phase 3: guided learning pilot | Working pilot complete; curriculum expansion ongoing | Four authored missions: local lesson 4 and Udemy lessons 3, 5 and 6. Direct publishing/corrections, automatic checks, hints, feedback, once-only XP, levels and optional practical activities. Full-course guided content has not been authored. |
| Udemy integration | Catalogue/transcript milestone complete | 221 curriculum items; 207 video transcripts captured. Exact Udemy links open separately. Udemy playback/completion does not sync; purchased media stay on Udemy. |
| Learner interface | Accepted | Consistent course cards/difficulty labels, dashboard, student workspace and real progress; parent area handles administration. No redesign needed before deployment. |
| Phase 4: laptop deployment | Implemented and locally tested; actual laptop rollout pending | Windows setup, requirement checks/download links, Git-based release updates, local data backups, persistence checks and recovery. Publish the final changes, then verify installation/credentials/scheduled execution on Jaxon's laptop. |

## Immediate remaining work

1. Commit and publish the final reviewed source changes to the existing
   repository when Sam authorizes it. Deployment/update tools have passed local
   backend, Windows and isolated Git/Docker integration checks.
   Merely editing this computer does not distribute an update.
2. Prepare Jaxon's Windows account with Git, Docker Desktop/Linux containers,
   repository read access and course files. Install under `C:\UnrealAcademy`.
3. If retaining today's learning state, transfer a consistent SQLite backup
   once during initial setup. It contains catalogue IDs, transcripts, guides,
   settings and progress. Never replace the laptop database during later updates.
4. Run the laptop acceptance checklist, including an actual Git update,
   scheduled task run, offline use and a restart with progress retained.
5. Continue transcript-based missions using the accepted lesson format. Expand
   in small batches rather than claiming the captured transcripts are finished
   learning activities. Keep existing question IDs when correcting questions.

## Future scope, deliberately not part of this deployment milestone

- Purchased GameDev.tv/additional Udemy catalogue integration when source details
  and the desired courses are supplied.
- Private curriculum package export/import/sync that merges new guides while
  retaining the laptop's IDs, attempts, XP and progress. Application code updates
  do not distribute private authored guides stored in the database.
  Sam explicitly chose automatic application updates with private manual mission
  transfers for now; use the deployment script's ImportGuide action.
- Durable off-device backup/restore tooling and a tested disaster-recovery drill.
  Deployment snapshots on the same drive are not protection from drive loss.
- Optional richer achievements/cosmetics; current XP is a progress marker.
- Accounts/authentication, shared-network hosting and multi-user operation.
- Optional AI-assisted authoring; no live AI tutor or runtime AI dependency.
- Release hardening: protected release branch, dependency/security automation,
  immutable registry images/complete transitive locks, image signing if needed.
  Current updates build the chosen Git commit locally rather than using a registry.

## Current data and boundaries

The development app uses Git-ignored `data/academy.sqlite3` and a read-only
`C:\UnrealAcademy\Courses` mount. Schema version is 4. On the deployment-managed
laptop these become `C:\UnrealAcademy\Data` and the configured course directory,
outside the Git checkout and release images. The student remains one local Jaxon
profile; Parent setup is navigation, not an authenticated boundary.

Last pre-deployment live check: **15 XP**, lesson 3's three checks solved, four
published missions, three local courses plus the external Udemy course. No real
learner answers should be submitted for deployment testing. See
`LAPTOP_DEPLOYMENT.md` and the deployment verification report for executed results.
