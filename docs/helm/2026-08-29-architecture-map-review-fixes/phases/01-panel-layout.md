# P1 — Detail panel anchored to the diagram view

<!-- Filename must be NN-<slug>.md with NN = N (e.g. P1 → 01-auth.md). -->
<!-- Status lives in goal.md's phase index, not here. -->
goal_ref: ../goal.md
updated: 2026-08-29

## Outcome

The `#panel` detail drawer is anchored inside `#view-diagram`, so in a wide desktop viewport it starts below the tab bar and never covers the topbar, tabs, or search box, while the ≤1100px bottom sheet and all existing interaction behavior are preserved.

## Assumptions

- `#view-diagram` (`position:relative`) is the correct containing block: its top edge is exactly the tab bar's bottom edge in all viewports (verified: 1400×900 probe, tabs bottom = 112 = fixed panel top).
- The panel is only ever open while the diagram view is active (`closePanel()` runs on every section-tab switch), so hiding it together with `#view-diagram` when a section tab is active changes nothing observable.
- jsdom cannot verify real geometry, so a DOM-structure assertion plus a headless-Chrome layout probe together form the acceptance evidence.

## Approach

Move `<aside id="panel"></aside>` from body level into `<main id="view-diagram">` (after `#canvas-wrap`). No CSS changes needed: the existing `#view-diagram.panel-open #canvas-wrap{margin-right:400px}` reservation and the ≤1100px bottom-sheet media query already size the reserved column; the panel's `top:0` then resolves against the diagram view instead of the viewport. Bump `architecture-map-template-version` 3 → 4 and refresh every eval seed report with the refresh script (the skill's own migration mechanism).

## Test strategy

- change kind: bug fix (renderer layout) + versioned template migration
- strategy: strict Red-Green-Refactor, with a headless-Chrome layout probe as compensating geometry verification (jsdom has no layout engine)
- Red / baseline signal: `node tests/test_architecture_map_template.mjs` — new check "detail panel is anchored inside the diagram view" (`#view-diagram #panel` non-null) fails against the current template; Chrome probe on current template shows `panel.top (0) < topbar.bottom (73)` and the search box fully inside the panel's box
- Green / regression checks:
  - `node tests/test_architecture_map_template.mjs` → all checks pass (new anchor check + all existing interaction checks)
  - `python3 -m pytest tests/test_architecture_map_skill.py -q` → green, including `test_seed_reports_use_the_current_template_shell` after seed refresh and the updated version assertion
  - Chrome probe @1400×900: `panel.top >= tabs.bottom`, search box not covered; Chrome probe @900×700: bottom sheet below the topbar, search visible
- exception: none — the DOM-structure test is automatable; the Chrome probe complements it because pixel geometry is not observable in jsdom (observed numbers recorded in Verification)

## Tasks

- [x] Add the jsdom anchor check to `tests/test_architecture_map_template.mjs` and observe the expected Red
- [x] Move the panel element into `#view-diagram`, bump the template version meta to 4, update the python version assertion
- [x] Refresh all eval seed reports with `scripts/refresh-template.mjs`, run both suites, re-run the Chrome probes, and record observed geometry

## Verification

- Red observed: `node tests/test_architecture_map_template.mjs` → `FAIL: detail panel is anchored inside the diagram view`, 89/90
- Green observed: same suite → 90/90; `python3 -m pytest tests/test_architecture_map_skill.py -q` → 26 passed, 22 subtests passed (includes seed `--check` vs v4)
- Chrome probe @1400×900 (before → after): PANEL t=0,l=1000,b=813 → t=112,l=1000,b=813; TOPBAR b=73; TABS t=73,b=112; SEARCH t=21,b=50,l=1160,r=1380 — panel now starts exactly at the tab bar's bottom edge; search fully visible
- Chrome probe @900×700 (after): bottom sheet PANEL t=356,b=613,l=0,r=900 — below the topbar (b=73) and search (b=50)
- Screenshot archived at /tmp/final-wide.png (wide, panel open, search visible)
- Checks not run: no headless-browser step in CI (jsdom-only); the Chrome probe is local compensating verification, which is why the jsdom suite pins the DOM anchor structurally

## Abort / reshape triggers

- If moving the panel breaks any existing jsdom interaction check (panel open/close, bottom sheet, tab switching), stop: the DOM move assumption is wrong — reshape to a CSS-only fix (e.g. `top` offset against the chrome height) instead of the DOM move.
- If the Chrome probe at 900×700 shows the bottom sheet covering the topbar after the fix, L2: the media query needs an explicit viewport-relative anchor for the sheet.
