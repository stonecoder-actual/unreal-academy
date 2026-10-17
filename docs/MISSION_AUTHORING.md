# Lesson takeaways and knowledge checks

Current policy: 17 October 2026. The accepted learner flow stays simple:

1. Open the video on Udemy and follow its instructor's activities in UE5.
2. Return to the portal and read the key takeaways.
3. Answer 3–6 automatic multiple-choice checks at the end.

No guided missions, generated activities, written answers, parent grading or
approval queue. Watching and knowledge checks are separate; rewards do not claim
that practical work has been assessed.

## Authoring

Read the complete available transcript before authoring. Highlight central ideas
in concise notes. Use three checks for light videos and four to six for substantial
content. Prefer plausible choices, predictions and troubleshooting to menu trivia.
Every check needs a hint and immediate explanation. Keep `practice: null`.

All 207 Udemy videos across sections 1–11 are authored: 890 questions. Non-video
articles/quizzes remain links to Udemy. Existing lesson layout is accepted.

## Publication and corrections

The user now wants authored portal curriculum distributed in Git. Edit
`backend/curriculum/udemy.json`, preserving the course slug, external lecture/quiz
identities and existing question IDs. Keep the documents portable: no machine
lesson UUIDs, learner records, raw transcripts or credentials. Run backend tests
and builds, then commit/push. Backend startup validates and merges the bundle;
laptop app updates now include authored lesson updates automatically.

On correction, retain IDs for the same question. A genuinely new check needs a
new identity. Previous documents are archived locally. Existing attempts, XP,
unlock/equipment records and watched state are retained. Wrong answers, watching
and repeated successes award zero; first correct answers award the defined XP.
Never replace an existing learner database to distribute curriculum.

Raw purchased transcripts used for review remain ignored under `data/udemy/`.
Earlier private packages and publication reports are historical artifacts, not
installation requirements. See `BUNDLED_CURRICULUM.md` for the current mechanism.
