# P1 — presentation-contract

goal_ref: ../goal.md
created: 2026-08-30T15:56:18+08:00
updated: 2026-08-30T21:12:00+08:00
revision: 2

## Outcome

The architecture-map skill has a concise, test-backed contract for presenting a sparse high-level system map without expanding into implementation detail or a general-purpose diagram generator.

## Assumptions

- The existing report-data model can express the required boundaries, node roles, primary flows, secondary dependencies, details, and source anchors with small or no schema changes.
- Existing focus, search, path, drill-down, and details interactions can be refined rather than replaced wholesale.
- The older active reader-model initiative may overlap conceptually, but this initiative can remain isolated by limiting P1 to reusable presentation rules and tests.

## Approach

Turn the agreed design direction into a small set of enforceable synthesis, rendering, and review rules. Start with characterization tests, add focused failing contract tests for missing rules, then make the minimum documentation and test-fixture changes needed to establish the contract before touching renderer behavior.

## Chunks

### Chunk 1 — High-level synthesis and information hierarchy contract

- change kind: behavior change
- strategy: strict Red-Green-Refactor
- Red / baseline signal: focused architecture-map contract tests fail because they do not yet require an 8–15-node overview target, strict detail exclusion, primary-flow selection, or progressive disclosure placement.
- Green check: `pytest -q tests/test_architecture_map_skill.py` passes with assertions covering the new high-level synthesis contract.
- regression checks: run the full relevant architecture-map test set and confirm existing current-state, evidence, schema, and offline-output contracts remain Green.
- [x] implementation and tests accepted

### Chunk 2 — Visual language, focus, and critical-path contract

- change kind: behavior change
- strategy: strict Red-Green-Refactor
- Red / baseline signal: focused template/skill tests fail because node-type encoding, boundary hierarchy, primary-versus-secondary edge emphasis, non-color cues, focus dimming, and critical-path isolation are not fully specified or asserted.
- Green check: focused skill and template tests pass with the presentation rules expressed independently of any Archify implementation.
- regression checks: existing interaction, keyboard, search, drill-down, and self-contained HTML tests remain Green.
- [x] implementation and tests accepted

### Chunk 3 — Visual acceptance contract

- change kind: behavior change
- strategy: strict Red-Green-Refactor
- Red / baseline signal: validation guidance/tests fail because they do not yet distinguish structural validity, visual readability, and evidence validity or require overlap, clipping, route, viewport, and theme checks.
- Green check: focused tests pass for explicit automated and human/browser visual acceptance gates.
- regression checks: repository architecture-map tests pass without introducing Chrome or external assets as a generation-time hard dependency.
- [x] implementation and tests accepted

## Phase verification

- `pytest -q tests/test_architecture_map_skill.py` passes.
- Relevant template/interaction tests pass and no existing evidence, current-state, or self-contained output contract is weakened.
- Review the resulting guidance once for scope: it teaches high-level presentation and progressive disclosure, not additional diagram types or deeper implementation modeling.

## Abort / reshape triggers

- If the contract requires a second architecture source model or Archify-compatible IR, stop and reshape around the existing report-data model.
- If visual rules force more nodes, deeper drill-down, or implementation inventories onto the main canvas, stop and simplify the information hierarchy.
- If overlap with the active reader-model initiative would require editing the same files concurrently, pause implementation and reconcile ownership before proceeding.
