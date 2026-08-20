# P1 — interactive-template

<!-- Filename must be NN-<slug>.md with NN = N (e.g. P1 → 01-auth.md). -->
<!-- Status lives in goal.md's phase index, not here. -->
goal_ref: ../goal.md
updated: 2026-08-18

## Outcome

The fixed architecture-map template renders a readable diagram that supports direct manipulation and retains all existing report interactions.

## Assumptions

- Vanilla SVG/DOM is sufficient; the report must remain dependency-free.
- Existing jsdom smoke tests can be extended to exercise pointer/wheel behavior without a full browser.

## Approach

Add a small canvas interaction layer around the existing data-driven renderer, persist view-local node positions, improve layered ordering and orthogonal edge routing, then document and test the public interaction contract.

## Test strategy

- change kind: behavior change
- strategy: strict Red-Green-Refactor
- Red / baseline signal: add interaction assertions that fail against the current static renderer (no drag/pan/zoom controls or transform updates).
- Green / regression checks: `node tests/test_architecture_map_template.mjs`; `python3 -m unittest tests/test_architecture_map_skill.py`.
- exception: jsdom has no real pointer geometry; use deterministic synthetic pointer events for state/transform checks and a browser smoke check if available.

## Tasks

- [x] Add canvas controls/state for node drag, background pan, wheel/button zoom, fit, and reset while preserving selection and drill-down.
- [x] Replace avoidable crossing-prone routing/order heuristics with stable layered ordering and orthogonal paths that rerender after movement.
- [x] Extend the template smoke suite and skill contract checks for the interaction contract.

## Verification

- Focused command: `node tests/test_architecture_map_template.mjs` with interaction assertions green.
- Regression command: `python3 -m unittest tests/test_architecture_map_skill.py` green (or explicitly record unavailable dependencies).

## Abort / reshape triggers

- If pointer interaction breaks node click/drill-down semantics in a real browser, keep the existing click contract and reshape the gesture arbitration before proceeding.
- If the new layout materially obscures the overview at the target report's node count, tune the routing/order phase rather than adding a dependency.
