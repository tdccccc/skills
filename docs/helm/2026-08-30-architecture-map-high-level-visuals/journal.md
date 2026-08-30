# Initiative journal — architecture-map-high-level-visuals

## 2026-08-30 — note — resume and concurrency check

- evidence: goal.md status active, owner current-session, revision 2; branch `docs/architecture-map-high-level-visuals` at d2d5881, working tree clean; baseline 26/26 architecture-map tests plus the jsdom template suite green.
- change: none (resume only). The older reader-model initiative (2026-08-19) is still marked active with owner `/root` but is stale — its success criteria are already baked into SKILL.md/REFERENCE.md and covered by tests; no concurrent editing risk, this initiative proceeds alone on presentation files.
- disposition: keep reader-model artifacts untouched (not owned here).
- next: execute P1 chunks (contract docs + tests; renderer untouched).

## 2026-08-30 — note — P1 completed: presentation contract established

- evidence: all three chunks went strict Red → Green with repo-wide regression; completion state 35/35 architecture-map tests and 67/67 repo tests green (commits `bc86640`, `959cd47`, `67ed367`).
- change: SKILL.md/REFERENCE.md now define the sparse overview contract — default density of roughly 8–15 core nodes with at most about 12 lifted overview edges (deliberately supersedes the earlier 5–8 top-level target; the old contract test was updated in chunk 1), strict detail exclusion with progressive disclosure placement (L1 map on the canvas; L2–L4 details, failure behavior, and evidence behind the panel, drill-down, or sections), primary-flow selection, the visual language contract (boundary hierarchy, primary-versus-secondary edge emphasis, focus dimming, critical path — never color alone), and the visual acceptance contract (structural / visual / evidence axes kept separate; automated and browser gates; review-time, never a generation-time Chrome/external-asset dependency).
- disposition: renderer and template untouched in P1 (only characterized as the baseline for P2/P3).
- reference: Archify pinned commit used only through the design directions already distilled in goal.md; no clone and no source copy (revisit via web fetch of pinned-commit files if P2 needs concrete visual details).
- next: plan and start P2 renderer phase; plan P3 after P2 is accepted.
## 2026-08-30 — note — P2 completed: renderer v7

- evidence: template version 7 rendered focus/critical-path emphasis, boundary-entry distinction, and light/dark themes; jsdom 122/122 (29 new checks, all Red→Green), unittest 35/35 architecture-map and 67/67 repo green; headless Chrome structural smoke passed 9/9 in both themes at 1600x1000 (commits `9217d68`, `a82c58b`, `b04084b`).
- change: template v7 — on selection, edges classify as path (downstream flow chain, strongest), up (incoming), hi (other connected), dim (unrelated); path nodes get `on-path`; boundary-entry node gets `↑` glyph + stronger dash; new 主题 toggle persists via localStorage; all renderer colors moved to theme-aware vars/palettes; seed shells refreshed.
- disposition: no schema or report-data changes; dark stays default.
- next: plan and start P3 (density advisory, jsdom visual audit, real-browser smoke); real Chrome at two viewports is the final human gate.
