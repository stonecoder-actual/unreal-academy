# Unreal Academy inventory — 17 October 2026

Current deployment: Udemy only, with Git-distributed authored portal content. No private transfer or seed is needed for a fresh installation. Non-Udemy records are hidden and preserved.

The accepted lesson layout remains unchanged. Udemy supplies practical activities;
the portal supplies transcript-based takeaways and 3–6 automatic checks per video.
No generated activities, written answers, grading or publication approval queue.

| Milestone | Status | Delivered / remaining |
| --- | --- | --- |
| Phase 1: foundation | Complete | React/TypeScript, FastAPI, persistent SQLite, same-origin API, loopback-only Compose deployment and automated tests. |
| Phase 2: local learning | Complete | Three local courses, MP4 playback/ranges, SRT captions, resources, saved playback/watched state and identity-preserving rescans. |
| Phase 3: learning checks | Framework and complete Udemy video curriculum delivered | All 207 videos in sections 1–11 have takeaways and 890 checks. Hints, immediate feedback, automatic quiz completion and once-only XP. Other local-course curricula remain to be authored; historical local pilot retained. |
| Udemy integration | Complete for the purchased Blueprints course | 221 external curriculum items; all 207 video transcripts captured and reviewed. Videos open on Udemy; playback/completion does not sync from Udemy. |
| Learner interface | Accepted | Standard course cards/difficulty labels, Udemy first, learner workspace and progress. Parent area handles essential administration. |
| Phase 4: laptop deployment | Implemented/tested; actual laptop acceptance pending | Windows requirements, setup, controlled Git updates, backups and learner-record verification. Authored portal curriculum ships with Git updates. |

Developer Guild progression has 50 levels, ten titles/emblems, permanent unlocks
and independent equipment. The 665-video mastery plan remains a draft while other
courses await authoring. Completing Udemy alone does not establish whole-track
Unreal Master eligibility. The approved level curve has not changed.

## Publication and preservation

Sections 5–11 add 147 videos and 606 questions to the existing 60/284. Existing
documents, guide/question IDs, quiz answers, playback, XP, unlocks, equipment,
settings and mastery-plan records remain unchanged. Tests used a disposable
database; no synthetic answers were submitted to the live learner account.
See [complete curriculum verification](UDEMY_COMPLETE_CURRICULUM_VERIFICATION.md).

Application code/docs, Udemy links and authored portal notes/checks are distributed
through the existing Git repository. Raw transcripts and learner data remain
private. Startup installs/merges all 207 video quizzes without a transfer package.

## Immediate remaining work

1. Complete actual laptop acceptance in `LAPTOP_DEPLOYMENT.md`: Git credentials,
   Docker startup, scheduled update, offline behavior and progress after restart.
2. Clone and install on the laptop using the README. Existing installations use
   Update and retain local progress. Do not seed or overwrite an existing learner DB.
3. Re-enable and author other courses only when requested.
   Preserve current checks and rewards when correcting existing material.
4. Inventory the remaining purchased courses before finalizing whole-track mastery.

## Deferred scope

- Additional GameDev.tv/Udemy integration when source details are supplied.
- Additional course bundling when those courses are requested.
- Off-device backup automation and a tested disaster-recovery drill.
- Authentication, multiple learners, network hosting and live AI integration.
- Additional achievements and release/security hardening.

## Storage boundaries

Development uses Git-ignored `data/academy.sqlite3`, schema 6, and read-only course
mounts. Managed laptop data lives at `C:\UnrealAcademy\Data` outside Git releases.
Keep purchased content, learner information and secrets out of Git. Parent setup
is navigation, not an authentication boundary. Historical phase reports retain
their original dates and are superseded by the current policy and this inventory.
