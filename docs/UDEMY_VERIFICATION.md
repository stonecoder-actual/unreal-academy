# Udemy verification — 15 October 2026

## Imported course

Unreal Engine 5 Blueprints - The Ultimate Developer Course, slug
`ue5-ultimate-bp-course`, is now the fourth course in the local library.
The signed-in Udemy curriculum contained 11 sections and 221 items: 207 videos,
3 readings and 11 Udemy quizzes. All 207 video transcripts were captured from
the visible transcript panel and imported. Readings/quizzes have no fabricated
video transcript. Canonical quiz and reading routes were checked in the browser.

Private files live under repository `data/udemy/`: `course-manifest.json`,
`outline.json`, individual `transcripts/{lecture-id}.json`, and the two authored
guide documents. The manifest is approximately 2.57 MB. Purchased text and the
database remain Git-ignored and outside Docker build contexts. No videos,
Udemy credentials, cookies or signed media URLs are stored by this integration.

All imported video records had nonempty transcript cues, correct lecture IDs in
the capture URL, and no exact duplicate transcript bodies. This is a coverage
check, not a manual word-for-word accuracy review of 207 automatic transcripts.
Cue timing was not exposed by the inspected transcript elements, so new guides
use untimed discussion sections. Only observed finite media durations are stored;
some are unknown rather than guessed from rounded curriculum labels.

## Personalized drafts

Two unpublished, source-bound drafts were imported for parent review:

- **Our First Project** → “Make a project that opens where you expect”: three
  discussion sections, eight scenario checks (80 XP total) and an optional
  project/map/startup experiment (60 XP after parent approval).
- **Editor Layout** → “Find your way home in the editor”: three discussion
  sections, seven scenario checks (70 XP total) and an optional viewport,
  layout-recovery and hide/show experiment (60 XP after parent approval).

Both include prerequisites, concrete goals, hints/explanations, caveats and a
five-criterion parent rubric. They are based on the captured source, not a
visual review of every demonstration. Neither is published automatically.
The remaining 205 video lessons have transcripts but no personalized guide yet.
Udemy's own quizzes stay on Udemy and do not award portal XP.

Parent setup → Guided lessons shows these drafts. Review the answer key and
criteria before approving. Parent setup → Udemy courses & transcripts supports
reading all captured lesson text alongside its source link.

## Implemented and executed verification

| Check | Result |
| --- | --- |
| Automated backend suite | 26 passed; one existing third-party AnyIO deprecation warning |
| Frontend TypeScript/Vite build | Passed, including final learner wording changes |
| Docker Compose config and startup | Passed; both live services healthy |
| Live same-origin smoke | Frontend/health, all three local video range/caption paths and external course link inventory passed |
| Schema migration | Version 4; consistent pre-v4 backup created; synthetic migration test retained old settings and playback |
| Real restart persistence | All 221 items, 207 transcripts and two drafts retained after backend container restart |
| Existing local progress | All pre-import lesson IDs, playback positions and watched flags matched the saved baseline |
| Existing portal XP | Remained 0; no live test answers, approvals or completion writes |
| Transcript audit | 207 nonempty records, no exact duplicate bodies, source URL/ID alignment verified |
| Learner browser | Fourth course card, 11 grouped sections, selected lecture URL, manual completion control and unpublished-state messaging visible |
| New-tab behavior | Watch on Udemy opened the selected Our First Project lecture in a separate tab while the portal remained open |
| Parent browser | Two unpublished drafts visible; captured-transcript course/lesson selection works |
| Console/whitespace | No captured portal console errors; git diff --check passed |

New backend tests use synthetic content to exercise canonical URL restrictions,
credential/query/foreign-host rejection, duplicate/blank transcript rejection,
upsert identity preservation, restart persistence, source-change invalidation,
draft publication, quiz retries/duplicate awards and practical approval rewards.
The first run required updating the old test's expected number of migration
backups to include the new pre-v4 snapshot; the final suite passed.

## Remaining boundaries

No Udemy playback/completion synchronization, video download, background scraping
service, automatic lesson generator or published-guide revision editor was added.
Published guides cannot be silently rewritten. Remote video changes are not
detected by a URL hash; recapture and review transcripts when curriculum changes.
The real practical exercises have not been performed by the agent. New external
screens were checked on desktop; the existing responsive styles are retained,
but a new physical mobile/touch or screen-reader audit was not performed.

Inspecting the Assets for the Course reading caused Udemy itself to mark that
reading complete automatically. Sam subsequently chose to leave it complete;
no cleanup is pending. This is Udemy state, separate from the untouched portal
completion/XP records. The signed-in browser may also retain brief playback
positions from inspecting video transcripts.

A subsequent lesson-3 drafting milestone adds reflection activities and a
read-only learner preview. See MISSION_AUTHORING.md; course-specific draft and
review notes remain private under data/udemy/.

Next content work is to author/review further missions in manageable batches
using the saved transcripts, not to repeat the capture or invent generic checks
for every lecture. Keep all purchased and derived curriculum in local private
data.
