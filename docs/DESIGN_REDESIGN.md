# Unreal Academy: learning studio redesign

## Audit

Reviewed the running dashboard, first-course navigation, published video 4 mission, quiz controls, practice form, and parent review. Baseline full-page screenshots are saved in the local ChatGPT project workspace as `redesign-before-dashboard.png`, `redesign-before-lesson.png`, and `redesign-before-parent.png`; these contain private course content and are not committed.

Strengths: actual SQLite progress, shared XP, idempotent awards, useful scenario checks, parent-reviewed builds, working captions and resource downloads. Preserve all of these.

Highest-impact problems:

- Large branding consumes the first viewport; no obvious next learning objective.
- Course cards are consistent after recent fixes, but titles do all the visual work. No distinctive academy identity.
- A course resume can lead back to administrative videos while the real guided mission remains buried.
- Long, ungrouped lesson lists are especially difficult with 330 lessons. Module context and search are absent.
- Resources, video status, checks and practical tasks compete in one long undifferentiated page.
- XP is a detached counter; there is no learner profile or clear presentation of demonstrated work.
- Parent and learner interfaces have the same hierarchy. Empty/error/loading states are mostly bare paragraphs.
- Generic article/section styles cause accidental spacing interactions. No centralized color, semantic-state or responsive system.

Technical constraints: React 19/TypeScript/Vite, no router or UI framework; nginx same-origin API; offline operation; no achievement ledger, avatar preferences or prerequisite graph. Existing course difficulty is manually assigned by source folder. Course titles stay intact. Do not infer mastery from video counts. Do not add new reward rules in this iteration.

## Focused research

Public product pages and official documentation reviewed on October 14, 2026. Authenticated dashboards were not accessed; this is a focused pattern review, not a usability study of those products.

| Reference | Observed pattern | Application here |
| --- | --- | --- |
| [TryHackMe](https://tryhackme.com/) | Named learning paths, visible difficulty and hands-on work | Course families, explicit difficulty and a mission linked to real practice |
| [HTB Academy](https://academy.hackthebox.com/catalogue/paths) | Modules grouped into skill and role paths | Organize existing course folders as expandable modules; no invented prerequisite locks |
| [OffSec learning paths](https://help.offsec.com/hc/en-us/articles/4403415786132-OffSec-Learning-Paths-FAQ) | Curated sequences give direction within a large library | Keep browsing distinct from the recommended next mission |
| [Duolingo home redesign](https://blog.duolingo.com/new-duolingo-home-screen-design/) | A guided next step reduces decisions about what to study | One primary mission action; no streak penalties, competitive ranks or virtual currency |
| [Codecademy path design](https://www.codecademy.com/resources/blog/?p=8362) | Modules make long curricula easier to navigate | Search and grouping for hundreds of lessons |
| [Brilliant features](https://brilliant.org/help/features/) | Guided learning with interactive practice checkpoints | Watch → understand → build, with nearby hints and explanatory feedback |
| [Khan Academy mastery](https://support.khanacademy.org/hc/en-us/articles/360007253831-What-is-self-paced-Mastery) | Skills are measured through assessment | Separate watched videos, correct checks and approved practical work |

These sources establish product patterns, not proof that this redesign improves Jaxon's outcomes. The dark palette, geometric artwork and violet identity are design judgments, chosen to suit his existing preference and the game-development context. Validate comprehension with Jaxon in actual use.

Accessibility reference: [WCAG text contrast](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) requires 4.5:1 for ordinary text, 3:1 for qualifying large text. [Target size guidance](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) informs hit areas; this UI aims for 44px controls. Labels and icons accompany semantic colors.

## Design direction and system

Identity: a calm game-development studio. Graphite backgrounds, warm pale text, violet actions, teal success and amber intermediate/practice states. Original SVG cubes connect the identity to constructing worlds without external images, fonts, tracking or requests.

- Tokens: `frontend/src/tokens.css`; background/surface/text/accent/semantic colors, radii, spacing and sidebar width.
- Type: locally available Segoe UI/system sans; responsive 30–42px page titles, compact headings and readable learning copy. Metadata is subordinate; never truncate lesson or course titles.
- Layout: persistent desktop workspace sidebar, compact mobile header, content max-width, aligned course cards, collapsible/searchable lesson modules. No redundant per-course navigation tabs.
- Components: `Icon`, `Avatar`, `CourseArt`, `Difficulty`, `Meter`, `LevelRing`; shared `XPPanel`, `Evidence`, and profile presentation.
- Actions: primary violet for the next mission, neutral course actions, visible keyboard focus, busy/disabled states. Filters and navigation use semantic controls.
- Feedback: inline errors, saved-state messages, explanatory quiz feedback, real XP/level notification with manual dismiss. No automatic dismiss deadline or confetti.
- Motion: brief state entry and hover feedback, no loops; reduced-motion preference disables animation and transitions.
- Dialogs/tooltips: avoid adding modal friction to current flows. Static dialog layout and accessibility requirements appear in the development preview. Important information stays visible instead of hover-only tooltips.
- Responsive: three course columns on desktop, two on tablet, one on small phones; stacked learning workspace and bounded lesson list at smaller widths.

## Priorities and integration boundaries

**P0 — visual and navigation:** shell, tokens, original icon/art system, dashboard recommendation, library cards, visible status, responsive layout, keyboard focus, preserved API/video/progress behavior.

**P1 — present real learning:** profile using existing XP and guided records, separate checks/builds, section progress, parent feedback, contextual resources, grouped lesson list, search, next-video navigation. This adds frontend presentation/selection logic, not new backend rewards.

**P2 — preview only:** achievement collection, earned/locked badge art, cosmetic variants, equipped/available/locked avatar states, sample level-up/empty/partial progress. `DesignPreview.tsx` is accessible only in Vite development mode with `?design-preview`; production ignores that parameter.

Future backend requirements: stable achievement definitions and unique award keys; event-based eligibility and audit history; persisted cosmetic selection/entitlements; explicit parent-reviewed prerequisites; optional learner preference and motion settings. Badge rules should reference correct knowledge and observed practical work. Cosmetic availability must never imply unearned progress. A live modal needs focus trapping, Escape handling and focus restoration. No backend changes or new packages are part of this redesign.

## Implementation checkpoint

Rendered the first dashboard implementation at 1280px before refining guided and parent screens. The next action was visible above the fold, all three course cards had equal heights, and no horizontal overflow was detected. Saved `redesign-checkpoint-dashboard.png`. The subsequent lesson pass adds staged learning guidance and feedback while retaining the tested endpoint contracts.

## Verification

See `DESIGN_VERIFICATION.md` for executed checks, screenshots, limitations and before/after findings.
