# Git-distributed portal curriculum

Policy change approved 17 October 2026: Git distributes the authored portal
takeaways/questions and Udemy lesson links. No private content transfer is needed.
This supersedes the previous private-package instructions for this course.

`backend/curriculum/udemy.json` contains the 221-item course catalogue and 207
video lesson documents, with 890 questions. It contains no video files, full
transcripts, Udemy credentials, machine-specific lesson UUIDs or learner records.
Videos and instructor activities remain on Udemy.

On backend startup, `app.bundled.sync_curriculum` validates the full package,
upserts the catalogue by course slug and lecture/quiz identity, and imports the
authored documents against that machine's existing lesson IDs. A fresh SQLite
database starts with no answers and zero XP. Existing guide/question IDs, attempts,
watched state, settings, XP and rewards remain local and unchanged.

Schema 6 adds `bundled_lesson_sources`: hashes of the shipped authored content.
It does not create fake transcripts. Guides use these bindings for content
integrity; unrelated private imports still require their own captured source.
Before migration, the database creates a consistent pre-v6 backup.

## Corrections

Edit the bundled JSON, retaining external identities and existing question IDs.
Preserve question meaning for already-earned awards; use a new question ID for
a genuinely new check. Validate/build/test, commit and push. The laptop updater
installs the revised content at the next eligible update. Previous guide versions
are archived locally. Repeated imports or correct answers cannot farm XP.

Raw purchased transcripts used for authoring remain ignored under `data/udemy/`.
Do not commit them, learner databases, cookies, passwords, local data or backups.
The older private ZIP remains a historical artifact and is no longer required.

## Paused courses and progression

The default learner catalogue shows Udemy only. Other course records and their
learning history remain in SQLite. Their cards, guide index and mastery cards
are hidden. Existing mastery membership and the approved 50-level curve are
retained; hiding courses must not revoke rewards or silently make Master easier.
The current Udemy course offers 8,885 XP; higher ranks anticipate more courses.

Core tests opt out of bundled fixtures using `ACADEMY_BUNDLED_CURRICULUM=0` and
`ACADEMY_UDEMY_ONLY=0`; normal installations use the enabled defaults. These flags
are not required for setup. The read-only empty course mount remains compatible
with existing deployments.

See [executed verification](BUNDLED_CURRICULUM_VERIFICATION.md) for installation,
update and data-preservation results.
