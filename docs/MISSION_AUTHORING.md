# Mission authoring and direct publication

Current policy: 16 October 2026. Sam removed publication approval and parent
grading from the learning flow. Parent setup manages course libraries, imports,
captured transcripts and local settings. Review queues, answer-key previews and
approval forms have been removed. Earlier verification notes describe history.

Work one lesson at a time until Sam asks to expand the curriculum. Use the actual
transcript, with age-appropriate explanations, useful scenario questions, plausible
distractors, hints and immediate feedback. Label adaptations honestly. Do not
invent technical skills for an administrative video. For new Udemy missions,
group multiple-choice questions at the end. No required written/oral explanation.

## Publish or correct a mission

Keep purchased transcripts and authored JSON under Git-ignored `data/`. Run:

```powershell
docker compose exec -T backend python -m app.guided /data/path-to-guide.json
```

Import validates the source, structure and timestamps and publishes immediately.
Refresh Jaxon's portal to see it. Existing drafts are released on backend startup;
their previous records are archived first. Importing a correction updates the
same guide and immediately replaces the student-facing content. No approval step.

Keep the lesson ID and existing question IDs for corrections. New IDs mean new
questions. Earned XP and attempts are retained; changing a question's reward
does not grant previously earned XP again. Removed checks no longer count toward
the current mission, but their historical XP stays saved. Identical reimports
do not create another backup. Previous documents and source hashes are archived
under `data/backups/guides/` before changes. These private snapshots supplement
regular full database backups; they are not a one-click rollback facility.

Source hashes still bind guides to local media/subtitles or captured external
transcripts. If those change, answers are blocked until the mission is checked,
corrected and reimported against the new source. No parent publication gate.

## Completion and XP

Every mission completes when all its current checks have been answered correctly.
Watching, wrong answers and repeat correct answers earn zero XP. First correct
answers earn the authored amount exactly once, including across restarts and
corrections. Levels advance every 100 XP. A level is a progress marker.

Use `practice: null` for quiz-only lessons. An authored practice object provides
optional steps, criteria and troubleshooting. The portal has no submission or
approval forms and awards no new practical-work XP. Jaxon can show progress to
Sam whenever he likes. Do not claim an unassessed activity proves mastery.

Historical submissions and earned practice XP remain stored. Deprecated API
routes are retained for compatibility with that historical workflow; they are
not used by the current portal. No schema migration or learner-data reset is
needed for this change.
