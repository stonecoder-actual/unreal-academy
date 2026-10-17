## Approved progression — 16 October 2026

Use the Developer Guild progression in `PROGRESSION.md`: 50 levels, ten permanent
titles and original emblems, independent cosmetic equipment and milestone reveals.
Level 2 starts at 50 XP and Level 50 at 28,320 XP. Unreal Master additionally needs
85% of the full track's checks overall and 75% in each course, after all planned
guides are authored and track membership is finalized. Pending lessons count in
draft estimates; published content alone must not make mastery easy. Preserve
existing XP and permanently earned rewards. No new practical assignments or grading.

## Current learning format — 16 October 2026

The project owner simplified Udemy learning: review each video's actual transcript, highlight
the key takeaways the learner needs to understand, and provide 3–6 automatically
checked multiple-choice questions, depending on the video's complexity. Place
all questions after the takeaways. No guided missions, generated activities,
projects, reflection prompts, written explanations or parent grading. Udemy's
instructor supplies the practical activities; the learner follows along in UE5.
Put the purchased Blueprints Udemy course first on the homepage and feature it
as his starting course. Keep saved answers, progress and once-only XP.

This replaces earlier mission/optional-activity plans. As of 17 October 2026,
all 207 Udemy videos across sections 1–11 have published takeaways and 890
automatic checks based on their captured transcripts. Preserve existing lesson,
guide and question identities when correcting content. Continue publishing notes
directly, with private manual content transfer and Git application updates.

## Current product policy — 16 October 2026

The project owner removed the parent lesson-approval workflow. New missions publish directly
to the learning portal; corrections are applied directly through reimport.
Parent setup is for course locations/imports, transcript administration and local
settings. No lesson review queue, publication approval or required practical-work
grading belongs in that interface. All correct knowledge checks complete a
mission automatically and award XP once; practice/show-and-tell is optional.
Preserve existing identities, progress, earned XP and historical work. Keep
question IDs stable when correcting an existing check, and archive the previous
guide locally before replacing it. Source changes still require a corrected,
reimported guide; this is a content-integrity check, not a parent approval step.
This policy supersedes the approval/review workflow in the original vision below.

## 1. Summary of Changes

I reviewed the Unreal Academy prompt for contradictions, ambiguous requirements, deployment risks, and instructions that could cause Codex to produce an incomplete application.

Assessment: The prompt is well structured and does not require a major rewrite. However, I identified four issues worth correcting before giving it to Codex.

1. GitHub versus local storage: The prompt correctly excludes videos and student data from GitHub, but it should explicitly define GitHub as the source-code and container-image distribution system, not the backup for the entire application.
2. Offline AI curriculum generation: The application must work offline, but AI-generated curriculum may require an external service. The prompt should distinguish offline learning from optional online content generation.
3. Windows Docker resource access: Docker Desktop can serve course files from Windows directories, but Unreal Engine project files should remain directly accessible to Unreal Engine on Windows. This needs an explicit shared-folder strategy.
4. Deployment reliability: The prompt requests rollback and database migrations without specifying compatibility safeguards. Rolling back an image does not necessarily roll back a database schema.

These are preventive corrections based on prompt inspection, not failures observed during execution.

### Targeted changes

Change 1 — Clarify the storage and backup model

```
- Be developed and version-controlled in a private GitHub repository.
+ Be developed and version-controlled in a private GitHub repository,
+ with GitHub used for source control and application distribution,
+ not as the sole backup for course files or student progress.
```

This prevents Codex from incorrectly treating GitHub as a complete application backup.

Change 2 — Clarify offline functionality

```
- Function offline for all core learning activities after installation
- and content import.
+ Function offline for all core student learning activities after
+ installation, content import, and curriculum publication.
+ Optional AI generation may require Internet access.
```

This preserves the offline requirement without imposing it on optional AI services.

Change 3 — Clarify Windows file access

```
+ Course and project files must be accessible through ordinary
+ Windows directories, including files the learner needs to open in
+ Unreal Engine. Docker must not become the exclusive location
+ of editable Unreal projects.
```

This avoids creating a technically functional learning portal that makes practical Unreal Engine exercises unnecessarily difficult.

Change 4 — Make upgrades and rollback safe

```
- Database migration and backup procedures.
- Version pinning and rollback support.
+ Database migrations with pre-upgrade backups and compatibility checks.
+ Version pinning and documented rollback procedures that account
+ for database schema compatibility and persistent data.
```

This addresses a common deployment failure: successfully rolling back the application image while leaving an incompatible database schema in place.

## 2. Final Updated Prompt

```

# Role

Act as a senior full-stack software architect, DevOps engineer, instructional designer, and game-based learning specialist. Design and implement a production-quality, self-hosted Unreal Engine learning platform for a 10-year-old beginner.

Prioritize maintainability, educational effectiveness, child safety, straightforward deployment, and reliable functionality over unnecessary technical complexity. Challenge weak architectural assumptions and recommend simpler, more robust alternatives when appropriate.

# Goal

Build **Unreal Academy**, a gamified, browser-based learning management system that transforms purchased Unreal Engine video courses and their supporting resources into an engaging, structured learning experience.

The application must:
1. Run locally on a Windows laptop using Docker Desktop, subject to confirming the laptop supports Docker and Unreal Engine simultaneously.
2. Be developed and version-controlled in a private GitHub repository, with GitHub used for source control and application distribution, not as the sole backup for course files or student progress.
3. Support repeatable builds, deployment, upgrades, and rollback through Docker and GitHub.
4. Store course videos, resource files, and persistent student progress locally, outside disposable containers.
5. Automatically import and organize existing video courses, using supplied `.srt` subtitles when available.
6. Turn lessons into structured learning activities, quizzes, practical Unreal Engine assignments, and larger projects.
7. Gamify learning with XP, levels, achievements, skill progression, and unlockable content.
8. Provide separate student and parent interfaces.
9. Function offline for all core student learning activities after installation, content import, and curriculum publication. Optional AI generation may require Internet access.
10. Be extensible without requiring substantial architectural changes.

The primary measure of success is demonstrated Unreal Engine proficiency, not video consumption or accumulated XP.

# Context

## Student and learning objectives

The primary audience is young learners interested in Unreal Engine 5 and creating their own games.

The platform should be engaging, age-appropriate, visually polished, and inspired by video-game progression systems without becoming distracting.

Use:
- Short, achievable learning objectives.
- Interactive quizzes and knowledge checks.
- Practical Blueprint and Unreal Engine exercises.
- Progressive difficulty and prerequisite skills.
- Constructive feedback and scaffolded hints.
- Meaningful rewards for demonstrated competence.
- Larger capstone projects that combine previously learned skills.

Avoid excessive repetitive rewards, artificial engagement mechanics, and automatically granting mastery for watching videos.

## Existing curriculum

The parent already owns Unreal Engine educational courses containing:
- MP4 instructional videos.
- Supporting resources, including potential Unreal projects, assets, archives, and documents.
- Subtitle files in `.srt` format for at least some lessons.

The curriculum is currently stored on a Debian media server but can be copied to the child's laptop.

Do not assume the directory structure, subtitle coverage, codecs, course licensing, or resource associations until inspected.

The application must support a course import workflow that:
1. Scans existing folders recursively.
2. Identifies videos, subtitles, and associated resources.
3. Preserves original files and directory relationships.
4. Extracts video metadata and associates matching subtitles.
5. Uses `.srt` files as the preferred textual source instead of unnecessarily retranscribing videos.
6. Optionally transcribes videos lacking subtitles when an appropriate transcription capability is configured.
7. Builds searchable lesson transcripts with timestamps.
8. Produces draft course outlines, lesson summaries, objectives, quizzes, and practical challenges from the actual instructional material.
9. Allows parent review, correction, and approval before publishing AI-generated curriculum.
10. Supports rescanning without duplicating courses or erasing student progress.

AI-generated content must be grounded in the course material, distinguish prerequisites from newly taught skills, and avoid inventing techniques or resource requirements.

## Application architecture

Prefer a modern, maintainable web application with:
- React and TypeScript frontend.
- Python FastAPI backend.
- SQLite database for local persistence.
- Embedded HTML5 video playback with HTTP range support.
- Docker Compose for deployment.
- Local bind mounts or named volumes for persistent data.
- Automated tests and GitHub Actions for build verification.

These are preferred technologies, not immutable requirements. Explain any materially better alternatives before deviating.

The application must not require Jellyfin.

Videos and course resources must remain outside the Git repository and Docker image by default. GitHub is for application source, deployment definitions, documentation, and non-sensitive configuration templates—not large copyrighted course files, personal data, secrets, or the live progress database.

Course and project files must be accessible through ordinary Windows directories, including files the learner needs to open in Unreal Engine. Docker must not become the exclusive location of editable Unreal projects.

Support browser-compatible video playback, resume positions, captions, playback-speed adjustment, and accessible resource downloads. Detect incompatible codecs and provide a documented conversion process without destroying originals.

Keep the application accessible on localhost by default. Do not expose it to the Internet or local network unnecessarily. If LAN access is enabled later, require appropriate authentication and network protections.

## Learning experience

Create the following core modules:

**Student dashboard**
- Current level and XP progress.
- Continue-learning section.
- Available courses and missions.
- Recently earned achievements.
- Skill progression and recommended next lesson.

**Course player**
- Embedded instructional videos.
- Subtitle support.
- Timestamped lesson navigation.
- Associated resources and project downloads.
- Lesson summaries and knowledge checks.
- Resume playback and progress tracking.

**Quest and challenge engine**
- Knowledge quizzes with explanations.
- Practical Unreal Engine building assignments.
- Explicit acceptance criteria.
- Hints that progressively increase in specificity.
- Challenge submissions with screenshots, descriptions, or project evidence.
- Parent review and approval.
- Remediation and retry opportunities.

**Gamification**
- XP for meaningful learning actions.
- Configurable level thresholds.
- Skill trees and prerequisites.
- Achievements and badges.
- Module completion rewards.
- Capstone or boss projects.
- Anti-farming protections and idempotent XP awards.

Do not equate a passed quiz with practical mastery. Distinguish watched, understood, practiced, and demonstrated skill states.

**Parent dashboard**
- Course import and management.
- Curriculum review and publishing.
- Learning progress and skill mastery.
- Challenge submission approval.
- XP adjustments with audit history.
- Data export, backup, and restore.
- Configuration of learning goals and optional study sessions.

## AI integration

Design an optional AI-assisted curriculum-generation pipeline that uses subtitles, course documents, and other authorized resources.

Initially, AI can assist the parent in generating and reviewing curriculum. The student-facing learning experience must work without an AI subscription, Internet connection, or API key.

A future interactive AI tutor may be considered, but do not implement unrestricted student-facing AI chat in the initial release.

Any future AI feature for a child under 13 must undergo a separate child-safety, privacy, and applicable platform-policy review before deployment. Do not assume ChatGPT parental controls authorize independent ChatGPT access for a 10-year-old.

## GitHub and Docker deployment

Create a private GitHub repository structure supporting:
- Clear separation of frontend, backend, deployment, tests, and documentation.
- Reproducible Docker builds.
- Versioned container images through GitHub Container Registry where appropriate.
- GitHub Actions for linting, testing, vulnerability checks, and image builds.
- A documented first-install procedure.
- A simple, controlled update procedure.
- Persistent storage across image replacements.
- Database migrations with pre-upgrade backups and compatibility checks.
- Version pinning and documented rollback procedures that account for database schema compatibility and persistent data.
- `.env.example` configuration with no committed secrets.
- Health checks and useful application logs.

Do not assume that pushing code to GitHub automatically updates the child's laptop. Define an explicit and safe update mechanism.

Ensure Docker Desktop resource usage does not unnecessarily interfere with Unreal Engine performance.

## Implementation boundaries

Do not begin by creating an elaborate interface while leaving backend features simulated.

Prioritize an end-to-end working vertical slice:
- Import one real course.
- Play a video with subtitles.
- Download an associated resource.
- Complete a quiz.
- Submit a practical assignment.
- Approve the assignment as a parent.
- Award XP exactly once.
- Restart the container and retain all progress.

Expand only after this workflow is verified.

# Output Format

Work in the following order.

## 1. Architecture assessment
Present the recommended architecture, component responsibilities, deployment topology, persistent storage design, and key technical tradeoffs.

Identify consequential assumptions, risks, and potential simplifications.

## 2. Product requirements
Define MVP functionality, future enhancements, user roles, learning workflows, and measurable acceptance criteria.

## 3. Data and curriculum model
Define the relationships among courses, modules, lessons, transcripts, resources, skills, quizzes, challenges, submissions, achievements, and XP transactions.

Explain how imported files are identified and linked without losing progress when files move or courses are updated.

## 4. Implementation plan
Divide development into small, independently testable milestones with clear dependencies and completion criteria.

## 5. Repository and deployment
Specify repository structure, Docker configuration, storage volumes, GitHub Actions, versioning, backups, and update procedures.

## 6. Implementation
When the architecture is sufficiently defined and repository/file-editing capabilities are available, implement the application incrementally.

Write actual working code rather than pseudocode or decorative mockups. Include database migrations, error handling, security controls, and automated tests.

Do not claim implementation or tests are complete unless they were actually executed and verified.

## 7. Verification
For each milestone, report:
- Implemented functionality.
- Tests executed and results.
- Remaining limitations.
- Security or data-integrity concerns.
- Manual verification steps.
- Next recommended milestone.

Do not introduce additional frameworks, services, databases, or infrastructure without a clear benefit.

# Refinement

If critical information is missing and the answer would materially affect the quality or correctness of the response, ask the minimum number of specific questions needed. Otherwise, make reasonable assumptions, state them when relevant, and proceed with the task.

```
