# Architecture map review fixes

status: active
updated: 2026-08-29
owner: session-2026-08-29-tiandc

## Intent

Resolve the confirmed bugs and agreed improvements from the 2026-08-29 review of the architecture-map skill: the detail panel covering the topbar/search in wide viewports, the contradictory no-report mode resolution in update/audit, and the smaller renderer/validator/documentation findings.

## Success criteria

- [ ] In a wide desktop viewport the detail panel no longer covers the topbar, tabs, or search box (headless-Chrome layout probe), while the ≤1100px bottom sheet still works.
- [ ] SKILL.md and REFERENCE.md state one consistent no-report resolution for `update` / `audit`, pinned by the contract tests.
- [ ] Search matches `notes` and `evidence` too; `--validate` rejects duplicate section titles; Escape also clears the search filter.
- [ ] The module `summary` length guidance matches what node widths can display, and the duplicated REFERENCE checklist items have one canonical home.
- [ ] Full test suite is green (python contract + jsdom template suite) and every eval seed report passes `--check` against the bumped template version.

## Non-goals

- The active `2026-08-19-architecture-map-reader-model` initiative (different owner/intent); its files stay untouched.
- Redesigning the layout/routing engine, adding keyboard graph navigation, or changing the report-data schema.
- Moving `#legend` (visually correct today) or other cosmetic shell changes beyond the listed fixes.

## Constraints

- Preserve the single-file offline HTML contract and the report-data schema.
- Template changes follow the skill's own versioned migration: bump `architecture-map-template-version` and refresh all seed reports with `scripts/refresh-template.mjs`.
- Contract-test phrases that remain true must keep passing; any dedupe must preserve asserted phrases or update the assertions deliberately.
- One isolated commit per accepted chunk on a feature branch (repo default branch is `main`).

## Phases

<!-- Single source of truth for phase status. PN ↔ filename NN. Outcomes only — no steps. The active line is the current focus. -->
1. P1 — Detail panel anchored to the diagram view; no topbar/search coverage on desktop, bottom sheet preserved — status: done
2. P2 — One consistent no-report resolution for update/audit across SKILL.md and REFERENCE.md, pinned by tests — status: active
3. P3 — Search covers notes/evidence, duplicate section title validation, Escape clears search, summary guidance and checklist dedupe — status: pending
