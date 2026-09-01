# P2 — renderer-high-level-presentation

goal_ref: ../goal.md
created: 2026-08-30T21:14:00+08:00
updated: 2026-08-30T21:26:00+08:00
revision: 2

## Outcome

The shared template (version 7) renders the sparse high-level map with the P1 visual language: focus and critical-path emphasis that highlights upstream/downstream relationships and dims unrelated material, a visually distinct boundary-entry node, and light/dark presentation — all without new diagram modes, deeper drill-down, or schema changes.

## Assumptions

- The P1 contract is implementable with the existing report-data model and edge `kind`: no new fields or second source of truth are needed (the critical path is derived from `flow` edges at focus time).
- Seed report shells can be refreshed mechanically (`refresh-template.mjs` preserves each data block exactly), so template-version bumps stay isolated per chunk.
- Dark remains the default theme; light is an explicit toggle persisted for the session, matching the "where supported" success criterion without changing default visuals.

## Approach

Change the template only (`templates/architecture-map.html`), in three independently acceptable renderer chunks, each test-first in the jsdom behavior suite with the Python contract tests as regression. Each chunk that touches the shell re-runs the seed refresh so every seed report stays on the current shell.

## Chunks

### Chunk 1 — Focus and critical-path emphasis

- change kind: behavior change
- strategy: strict Red-Green-Refactor
- Red / baseline signal: new jsdom focus suite fails because selecting a node does not yet classify connected edges into upstream (`up`), downstream connected (`hi`), and flow-chain critical path (`path`) classes, and the existing selection test still expects the old single highlight class.
- Green check: `node tests/test_architecture_map_template.mjs` prints all checks passed, including the new focus suite (chain fixture: incoming edge `up`, outgoing flow chain `path`, dep-connected `hi`, unrelated `dim`; path nodes carry `on-path`).
- regression checks: full `python3 -m unittest tests.test_architecture_map_skill` (35 tests), seed reports `--check` current after refresh, all 61–67 repo tests green.
- [x] implementation and tests accepted

### Chunk 2 — Boundary-entry visual distinction

- change kind: behavior change
- strategy: strict Red-Green-Refactor
- Red / baseline signal: new jsdom assertions fail because the boundary-entry node (drill-down parent) is not yet distinguishable from external-context nodes (no `boundary-entry` class or glyph, no distinct border width).
- Green check: same jsdom suite passes with the drill-down's `__parent` node carrying `boundary-entry` plus an `↑` glyph and stronger dashed border, while external-context nodes keep only the plain dashed style.
- regression checks: interaction suite (drill-down, breadcrumb, back-navigation), contract tests, repo-wide unittest suite.
- [x] implementation and tests accepted

### Chunk 3 — Light/dark theme support

- change kind: behavior change
- strategy: strict Red-Green-Refactor
- Red / baseline signal: new jsdom assertions fail because the shell has no theme switch: no `data-theme` attribute handling, no light palette, and no toolbar action.
- Green check: theme suite passes — default `dark`, toolbar `主题` action flips `data-theme` and re-renders nodes/legend with the light palette, preference persists in `localStorage`, and no external assets are added.
- regression checks: offline contract (no external URLs), shell UI language, all suites above, seed refresh stays current.
- [x] implementation and tests accepted

## Phase verification

- `python3 -m unittest tests.test_architecture_map_skill` passes (contract + regression + jsdom behavior suites).
- Seed reports and the arxiv fixture render with the new emphasis classes and both themes without route-failure markers; `--validate`/`--check` remain `valid`/`current`.
- Review once for scope: the renderer gains emphasis, boundary distinction, and theme only — no workflow/sequence/dataflow modes, no deeper drill-down, no implementation inventory on the canvas.

## Abort / reshape triggers

- If conveying emphasis requires new node types, depth levels, or an implementation inventory on the main canvas, stop and simplify the presentation instead of extending the model.
- If path emphasis makes any rendered overview or drill-down denser or less readable (more route failures, more hidden labels), reshape the emphasis scope instead of shipping it.
- If the jsdom characterization of an existing interaction contradicts the P1 contract, resolve the contract question (L1/L2) before the renderer change.