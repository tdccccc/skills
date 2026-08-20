# P2 — review-and-migration

goal_ref: ../goal.md
updated: 2026-08-18

## Outcome

The skill documents the renderer/migration contract, the arxiv-daily report has an evidence-backed review, and the requested report uses the accepted interactive shell without changing its report data.

## Assumptions

- The existing arxiv-daily `report-data` block should be preserved while upgrading renderer behavior.
- Semantic report corrections should be made only after the owner accepts the subagent's evidence-backed findings; this phase does not silently rewrite project architecture claims.

## Approach

Add a versioned shell marker and atomic refresh utility, synchronize eval seed shells, review the named report against production source, browser-smoke the target-data preview, then migrate the requested report shell exactly.

## Test strategy

- change kind: behavior-preserving migration tooling plus documentation
- strategy: Green characterization baseline and proportionate checks
- Red / baseline signal: refresh contract initially failed because the version marker/utility were absent; current reports and seed shells were stale before synchronization.
- Green / regression checks: `NODE_PATH=/home/tiandc/Documents/code/deepseek-harness/node_modules/.pnpm/jsdom@29.1.1_@noble+hashes@2.3.0/node_modules python3 -m unittest discover -s tests -p 'test_*.py'`; `node architecture-map/scripts/refresh-template.mjs --check` for all seed reports; target-data route audit.
- exception: none; the target shell migration preserves `report-data` byte-for-byte and is independently checkable with `refresh-template.mjs --check`.

## Tasks

- [x] Version the renderer shell and add an atomic report-shell refresh/check utility that preserves JSON data.
- [x] Update architecture-map guidance, readability gates, and migration instructions; synchronize eval seed reports.
- [x] Review the named arxiv-daily report against source evidence and record the semantic corrections needed for a future content audit.

## Verification

- `79/79` focused template checks passed after the final aggregation/routing additions.
- `43` Python repository tests passed; all five seed reports and the requested arxiv-daily report report `current`; target root and drill-down audits report zero node collisions and zero route failures, with only one known root-view edge crossing left after route-interaction penalties.
- A Playwright Chromium smoke test verified node drag/reset, canvas pan, zoom/fit, drill-down, rerouting, and clean console output on a preview that is byte-identical to the migrated target.

## Abort / reshape triggers

- If the owner wants semantic report corrections rather than only a renderer migration, start a separate audit phase so those claims are re-proved independently.
