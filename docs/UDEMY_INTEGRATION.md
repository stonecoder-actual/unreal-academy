## Current product policy — 16 October 2026

Sam removed the parent lesson-approval workflow. New missions publish directly
to Jaxon's learning portal; corrections are applied directly through reimport.
Parent setup is for course locations/imports, transcript administration and local
settings. No lesson review queue, publication approval or required practical-work
grading belongs in that interface. All correct knowledge checks complete a
mission automatically and award XP once; practice/show-and-tell is optional.
Preserve existing identities, progress, earned XP and historical work. Keep
question IDs stable when correcting an existing check, and archive the previous
guide locally before replacing it. Source changes still require a corrected,
reimported guide; this is a content-integrity check, not a parent approval step.
This policy supersedes the approval/review workflow in the original vision below.

# Udemy course integration

This milestone adds externally hosted curriculum to the existing local library.
The learner chooses a course and lesson, opens its exact Udemy URL in a new tab,
then returns to Unreal Academy for published checks and practical work.
The original three local courses retain their local video player.

## Boundaries

- Udemy videos are not downloaded, embedded or proxied. The portal does not log
  in to Udemy, retain cookies/passwords, call private Udemy APIs, or synchronize
  Udemy playback/completion. Internet and an authorized signed-in browser are
  needed for the external video. Published portal activities remain local.
- Manual completion means watched/read/completed on Udemy, not demonstrated
  mastery. It awards zero XP. Correct checks use the once-only XP ledger;
  practical activities are optional and require no approval.
- Transcript capture is from the transcript panel in the parent's signed-in
  browser. Raw captures, curriculum manifests and derived lesson drafts belong
  under Git-ignored `data/udemy/`, never source control or image contexts.
- Automatic captions may contain errors. Captured cues have an order but no
  verified timestamps; new discussion sections use null start/end values.
  Do not manufacture timestamps. No automatic lesson-authoring service exists.
- A transcript being captured does not mean a personalized mission is ready.
  Lessons without an authored mission show that one is coming soon.
  Importing an authored guide publishes it directly to Jaxon.

## Import a private manifest

Parent setup → Udemy courses & transcripts accepts a JSON manifest. Importing
updates existing items by stable Udemy identity and preserves playback/watched,
quiz, practical and XP records. Omitted items or transcripts are retained; an
incomplete capture must never erase prior material. Use a complete ordered
outline when updating to retain intended curriculum ordering. Removal/archive
management is not implemented in this milestone.

Example with synthetic content only:

```json
{
  "slug": "example-course",
  "title": "Example course",
  "url": "https://www.udemy.com/course/example-course/",
  "difficulty": "Beginner",
  "lessons": [{
    "external_id": "123",
    "title": "1. Example lesson",
    "section": "Section 1: Example",
    "kind": "video",
    "url": "https://www.udemy.com/course/example-course/learn/lecture/123",
    "duration": null,
    "transcript": {
      "cues": ["Synthetic example text."],
      "captured_at": "2026-10-15T00:00:00Z"
    }
  }]
}
```

Kinds are `video`, `article`, `quiz`; quiz links use `/learn/quiz/{id}`.
Only videos have transcripts. Article and quiz items remain available on Udemy
without fabricated transcript records. IDs and URLs must agree, use canonical
HTTPS `www.udemy.com` paths for the same course, and contain no credentials,
query or fragment. Only actual verified durations should be stored; null is
valid. The UI limits manifest files to 15 MB; nginx allows 15 MB request bodies.

Alternatively, place the manifest in the local data mount and run:

```powershell
docker compose exec -T backend python -m app.external /data/udemy/course-manifest.json
```

Parent setup also lists captured transcripts for review alongside their source
link and capture date. It is local parent navigation, not authenticated access.

## Guided lesson preparation

Use imported portal lesson IDs in `GuideDocument.lesson_id`. The existing
`python -m app.guided /data/path-to-guide.json` validates and publishes a mission
immediately. Reimport applies corrections to the same guide, preserving earned
XP and saving the prior document under `data/backups/guides/`. Keep question IDs
stable for corrections. Preserve source-specific curriculum in local data.

External guides bind to the exact lesson URL hash and captured transcript hash.
Changing either blocks the outdated guide until it is checked, corrected and
reimported. The URL hash is not a hash of remote video bytes; the app cannot
detect changes on Udemy unless the source/transcript is recaptured. Recapturing
a changed transcript does not erase earned XP. No parent approval is needed.

## Schema and verification

Migration 4 adds course source metadata, external item identity/URL/kind/section,
and `lesson_transcripts`. Startup first uses SQLite's backup API to save a
consistent `data/backups/pre-v4-*.sqlite3` snapshot. Keep that backup and current
data separately if rolling back; older application versions reject schema 4.

Run the normal backend suite and frontend build. `test_external.py` uses only
synthetic material to test identity-preserving import/update, transcript storage,
canonical URL validation, duplicate/empty input rejection, source invalidation,
direct publication/corrections, once-only quiz/legacy practical rewards, restart persistence and
pre-v4 migration backup. `tests/verify-design.ps1` checks local video delivery
and external link inventories without writing live progress.

See `UDEMY_VERIFICATION.md` for the actual capture coverage, authored drafts,
executed results and remaining work from this integration.
