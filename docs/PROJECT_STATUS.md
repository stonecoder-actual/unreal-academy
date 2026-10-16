## Current learning format — 16 October 2026

The project owner simplified Udemy learning: review each video's actual transcript, highlight
the key takeaways the learner needs to understand, and provide 3–6 automatically
checked multiple-choice questions, depending on the video's complexity. Place
all questions after the takeaways. No guided missions, generated activities,
projects, reflection prompts, written explanations or parent grading. Udemy's
instructor supplies the practical activities; the learner follows along in UE5.
Put the purchased Blueprints Udemy course first on the homepage and feature it
as his starting course. Keep saved answers, progress and once-only XP.

This replaces earlier mission/optional-activity plans. Sections 1–4 are now
authored and published for all 60 videos, with 284 checks. Sections 5 onward
still need authoring. Continue publishing lesson notes directly, with private
manual content transfer and automatic Git application updates as already agreed.

# Unreal Academy inventory — 16 October 2026

This is the current roadmap checkpoint. Historical phase documents record what
was true when each milestone shipped; the direct-publication policy in
`AGENTS.md`, `PROJECT_SPEC.md` and `MISSION_AUTHORING.md` supersedes their old
parent approval requirements. the project owner is satisfied with the lesson design/layout.

| Milestone | Status | Delivered / remaining |
| --- | --- | --- |
| Phase 1: foundation | Complete | React/TypeScript, FastAPI, persistent SQLite, Compose, loopback-only port 3000, same-origin API, health checks, builds and automated tests. |
| Phase 2: local learning | Complete | Three local courses, natural lesson ordering, MP4 playback/ranges, SRT captions, resources, saved playback/watched state, imports/rescans that retain identities. |
| Phase 3: learning checks | Framework and Udemy sections 1–4 complete; later sections pending | All 60 videos in sections 1–4 have takeaways and 284 automatic checks. Direct publishing/corrections, hints, feedback, once-only XP and levels. Udemy supplies practical work; no portal activities or parent grading. Historical local lesson 4 is retained. |
| Udemy integration | Catalogue/transcript milestone complete | 221 curriculum items; 207 video transcripts captured. Exact Udemy links open separately. Udemy playback/completion does not sync; purchased media stay on Udemy. |
| Learner interface | Accepted | Consistent course cards/difficulty labels, dashboard, student workspace and real progress; parent area handles administration. No redesign needed before deployment. |
| Phase 4: laptop deployment | Source published and locally tested; actual laptop rollout pending | Windows setup, requirement checks/download links, Git-based release updates, local data backups, persistence checks and recovery. App source through e1bdea3 is on main. Verify installation/credentials/scheduled execution on the learner's laptop; private curriculum transfers separately. |

Developer Guild progression is implemented: 50 levels, ten permanent titles and
emblems, independent equipment and rank reveals. The complete-curriculum mastery
track remains a draft until remaining courses are imported and their checks are
authored. See `PROGRESSION.md`; existing XP/progress remain intact.

## Immediate remaining work

1. Application/deployment source through e1bdea3 has been pushed to the existing
   repository. This curriculum publication is local/private and is not delivered
   by Git. Transfer its lesson JSON with ImportGuide when setting up the laptop.
2. Prepare the learner's Windows account with Git, Docker Desktop/Linux containers,
   repository read access and course files. Install under `C:\UnrealAcademy`.
3. If retaining today's learning state, transfer a consistent SQLite backup
   once during initial setup. It contains catalogue IDs, transcripts, guides,
   settings and progress. Never replace the laptop database during later updates.
4. Run the laptop acceptance checklist, including an actual Git update,
   scheduled task run, offline use and a restart with progress retained.
5. Continue with Udemy section 5 onward using the accepted takeaways/checks
   format. Sections 1–4 are complete. Keep existing question IDs when correcting
   questions and never add portal practical activities.

## Future scope, deliberately not part of this deployment milestone

- Purchased GameDev.tv/additional Udemy catalogue integration when source details
  and the desired courses are supplied.
- Private curriculum package export/import/sync that merges new guides while
  retaining the laptop's IDs, attempts, XP and progress. Application code updates
  do not distribute private authored guides stored in the database.
  the project owner explicitly chose automatic application updates with private manual mission
  transfers for now; use the deployment script's ImportGuide action.
- Durable off-device backup/restore tooling and a tested disaster-recovery drill.
  Deployment snapshots on the same drive are not protection from drive loss.
- Additional achievements beyond the implemented Developer Guild ranks/emblems.
- Accounts/authentication, shared-network hosting and multi-user operation.
- Optional AI-assisted authoring; no live AI tutor or runtime AI dependency.
- Release hardening: protected release branch, dependency/security automation,
  immutable registry images/complete transitive locks, image signing if needed.
  Current updates build the chosen Git commit locally rather than using a registry.

## Current data and boundaries

The development app uses Git-ignored `data/academy.sqlite3` and a read-only
`C:\UnrealAcademy\Courses` mount. Schema version is 5. On the deployment-managed
laptop these become `C:\UnrealAcademy\Data` and the configured course directory,
outside the Git checkout and release images. The student remains one local learner
profile; Parent setup is navigation, not an authenticated boundary.

After publishing sections 1–4: **15 XP**, lesson 3's three checks still solved,
60 published Udemy lesson quizzes plus the retained local pilot, three local
courses and the external Udemy course. All learner-table fingerprints match the
pre-publication snapshot. No synthetic answers were submitted to the live app.
See `UDEMY_SECTIONS_1_4_VERIFICATION.md` and `LAPTOP_DEPLOYMENT.md`.
