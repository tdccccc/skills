# P3 — visual-checks

goal_ref: ../goal.md
created: 2026-08-30T21:27:00+08:00
updated: 2026-08-30T21:27:00+08:00
revision: 1

## Outcome

The repository ships executable visual gates for the P1 acceptance contract: an overview-density advisory in `--validate`, an automated jsdom audit script covering overlap, clipping, routes, readability, interaction, and both themes, and a real-Chrome headless smoke script at desktop and narrow viewports — all wired into the regression suite with skip-if-unavailable semantics, keeping report generation free of Chrome/external-asset dependencies.

## Assumptions

- The jsdom geometry (960x640 fallback viewport, computed SVG attributes) is adequate for deterministic overlap/route/readability audits; viewport-specific behavior belongs to the real-browser smoke.
- Chrome dev/build availability is environment-specific, so every browser-mediated check skips cleanly when the binary is missing, mirroring the existing jsdom skip pattern.
- Density advisory is advisory: it never changes `--validate` exit codes or blocks valid reports.

## Approach

Three test-first chunks: a validate-mode advisory with python contract tests, a shared jsdom audit script wired into the suite over all seed reports, and a real-Chrome smoke script wired in over one seed report at two viewport sizes. Each chunk is accepted with Red → Green and repo-wide regression.

## Chunks

### Chunk 1 — Overview density advisory in `--validate`

- change kind: behavior change
- strategy: strict Red-Green-Refactor
- Red / baseline signal: new python tests fail because `--validate` emits no advisory when a report's top-level module count or lifted-edge estimate exceeds the roughly 15-node / 12-edge overview default.
- Green check: `python3 -m unittest tests.test_architecture_map_skill.ArchitectureMapSkillContractTests.test_validate_density_advisory` passes — valid small reports print `valid` with no advisory; dense fixtures print an `advisory:` line naming the count and the grouping remedy; exit codes stay unchanged (`0` valid, `2` structural failure).
- regression checks: existing validate violation tests, seed `--check` current, jsdom suite, repo-wide suite.
- [ ] implementation and tests accepted

### Chunk 2 — Automated visual audit script (jsdom, no browser)

- change kind: behavior change
- strategy: strict Red-Green-Refactor
- Red / baseline signal: a new python test fails because `tests/audit_architecture_map_visuals.mjs` does not exist and no audit output covers the seed reports.
- Green check: the script exists, is skippable without jsdom, and reports PASS for every seed report across the P1 acceptance gates — overlap (node/label), clipping at fit zoom, routes (no `route-failed` marker, no proper crossings), readability (no hidden-until-hover labels), interaction smoke (drag/pan/zoom/fit/reset/search/drill-down/breadcrumb/panel), and both themes — exit `0` with all PASS.
- regression checks: full suite still green; audit adds no Chrome or external assets to generation.
- [ ] implementation and tests accepted

### Chunk 3 — Real-browser smoke script (headless Chrome, optional)

- change kind: behavior change
- strategy: strict Red-Green-Refactor
- Red / baseline signal: a new python test fails because `tests/smoke_architecture_map_browser.sh` does not exist.
- Green check: with Chrome available, the script renders one seed report at desktop width and narrow width, probes the live DOM (no fatal overlay, diagram active, panel closed, nodes/edges/legend rendered, theme toggles, no console errors captured by injected listeners, no route-failed markers), and exits `0`; without Chrome it prints SKIP and exits `2`.
- regression checks: offline contract and all previous suites remain green; the smoke itself relies only on `google-chrome`/`chromium` discovery and a temp copy outside the repository.
- [ ] implementation and tests accepted

## Phase verification

- `python3 -m unittest discover -s tests -p "test_*.py"` passes end to end with the audit running over every seed report and the smoke over one seed report at both viewports.
- All P1 acceptance-gate names (overlap, clipping, routes, readability, interaction, theme) are exercised by an executable check, and structural/evidence contracts stay green.
- Browser review performed once at desktop and narrow widths on a rendered report as the final human gate.

## Abort / reshape triggers

- If the audit cannot produce deterministic PASS on the existing seed reports, stop and reshape the audit scope or the report fixtures rather than loosening the gates.
- If real-browser smoke proves flaky in this environment (crashes, unstable dumps), keep the script but report it as skipped with an explicit reason instead of concurrency-hiding it.