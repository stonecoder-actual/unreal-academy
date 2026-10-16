# Progression verification

Verified 16 October 2026 for the Developer Guild progression release.

## Automated checks

- Backend: 62 tests passed. One existing third-party AnyIO deprecation warning.
- TypeScript and Vite production build passed.
- Docker Compose configuration validation and production image builds passed.
- Tests cover level boundaries and cap, permanent unlocks, locked equipment rejection, independent title/emblem selection, once-only XP, whole-library mastery gates, stale transcripts, finalization and schema-4 migration preservation.
- The isolated laptop updater integration passed: fresh install, private lesson import, idle deferral, Git update, no-op, dirty/offline refusal, interrupted-update recovery and failed-release rollback. XP, playback, unlocked ranks and selected cosmetics survived.

## Browser and deployment

- An isolated synthetic learner verified independent equipment selection and persistence after reload. A correct answer crossed the Level 10 threshold, unlocked Apprentice and displayed its milestone reveal.
- The production portal rendered the new nameplate and reward collection in My progress. No quiz answers or cosmetic selections were submitted against the real learner during verification.
- Production was rebuilt and started successfully. Frontend and API checks passed.
- The schema-4 deployment snapshot verified all existing learner-table fingerprints after migration, before opening the frontend.
- A second snapshot and container restart verified the full schema-5 preservation manifest, including unlocks, equipment and mastery configuration.
- Final production state: 35 XP, Level 1, Newbie; 665 planned videos, 61 authored guides. Existing progress was retained.

## Remaining work

The mastery track remains a draft. Import the remaining intended courses, finish their knowledge checks and deliberately confirm the final XP calibration before finalizing it. Draft estimates cannot unlock Unreal Master. Desktop browser behavior was checked; a separate mobile-device review has not been performed.

See [progression rules](PROGRESSION.md) for thresholds and reward requirements.
