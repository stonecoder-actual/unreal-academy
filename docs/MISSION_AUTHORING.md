# Lesson takeaways and knowledge checks

Current policy: 16 October 2026. This supersedes the previous guided-mission and
optional-practice format. The filename is retained so existing links still work.

## The entire learner flow

1. Watch the lesson on Udemy and follow its instructor's UE5 activities.
2. Return to the portal and read the highlighted key takeaways.
3. Answer 3–6 multiple-choice knowledge checks at the end.

No mission framing, invented projects, extra exercises, reflection tasks,
written explanation questions, parent grading or approval queue. Do not add
show-and-tell as another portal step. Udemy supplies the practical work.

## Author each video from its transcript

Read the complete captured transcript before writing. Pick the concepts Jaxon
needs to understand, using short, clear bullets. Do not pad notes with every
mouse click or turn administrative content into an Unreal technical lesson.
Use 3 questions for a light/orientation video; 4–6 for more substantial material.
Ask about the central ideas using plausible choices, predictions or simple
troubleshooting. Avoid trivia, ambiguous answers, and unsupported claims.
Give each question a helpful hint and immediate explanation. All questions go
after the takeaways; every answer is automatically checked.

`takeaways` is a non-empty list in the private lesson JSON. Keep `practice: null`.
The import validator enforces 3–6 questions and no activities for Udemy lessons.
Legacy document/section fields and `/guide` API names remain for compatibility;
they do not create additional learner steps. Historical local-course documents
remain readable, and historical practice records/earned XP are retained.

## Publish and correct

Keep purchased transcripts and authored JSON in Git-ignored `data/udemy/`.
Development checkout:

```powershell
docker compose exec -T backend python -m app.guided /data/udemy/lesson5-notes.json
```

Managed laptop installation:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\UnrealAcademy\Tools\Academy.ps1 -Action ImportGuide -GuideFile C:\UnrealAcademy\Transfer\lesson5-notes.json
```

Imports publish directly. Keep lesson IDs and existing question IDs for corrections.
The prior document is archived under `data/backups/guides/`; prior answers and XP
stay saved. Removed checks no longer count toward the current quiz, but their
earned XP is not deleted. Source changes block outdated notes until checked and
reimported. Never replace Jaxon's live database to deliver a new lesson.

First correct answers earn XP once; wrong answers, retries after success and
watching earn zero. Levels advance every 100 XP. No practical-work rewards are
created by the current portal. Application updates use Git; lesson content is
transferred privately, as Sam chose.

## Current coverage

The existing Udemy lessons are 3 (three checks), 5 (six checks) and 6 (six checks).
Their private files are `lesson3-notes.json`, `lesson5-notes.json` and
`lesson6-notes.json`. The remaining video lessons are not yet authored; they show
a clear pending-notes message while remaining watchable. Work with Sam on the
rest of the curriculum after this format update.
