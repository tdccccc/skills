# Architecture map high-level visuals

status: active
created: 2026-08-30T15:56:18+08:00
updated: 2026-08-30T21:16:00+08:00
revision: 3
owner: current-session

## Intent

Keep architecture-map focused on a high-level, evidence-backed understanding of the whole system while improving how that understanding is presented. Borrow Archify's visual design ideas—clear hierarchy, boundaries, focus, path emphasis, and visual quality checks—without adopting its full IR, diagram catalog, or implementation-level detail.

## Success criteria

- [ ] The skill defines a sparse high-level overview with roughly 8–15 core nodes, clear system boundaries, and only the relationships needed to understand the whole architecture.
- [ ] The main canvas communicates system shape at a glance; responsibilities, evidence, failure behavior, and source anchors remain available through progressive disclosure rather than crowding the graph.
- [ ] Node focus and critical-path presentation highlight relevant upstream/downstream relationships while suppressing unrelated visual noise.
- [ ] Visual rules make node types, boundaries, primary flows, and secondary dependencies consistently distinguishable without relying on color alone.
- [ ] Automated checks and browser review cover overlap, clipping, broken routes, readability, interaction, and light/dark presentation where supported.
- [ ] Existing current-state, evidence, `init`/`update`/`audit`, and self-contained offline HTML contracts remain intact and covered by regression tests.

## Non-goals

- Adopting Archify's Typed IR, renderer implementation, or complete delivery pipeline.
- Adding workflow, sequence, dataflow, lifecycle, or implementation-detail diagram modes.
- Turning the architecture map into a directory, class, function, or unlimited drill-down browser.
- Maintaining multiple independent architecture models or permanent Before/Delta/After history in the report.
- Copying Archify source code or adding it as a runtime dependency.

## Constraints

- Preserve the report as a high-level map of the repository's current implemented architecture, not a complete code inventory.
- Production and executable-configuration evidence remain the basis for behavioral claims; visual polish must not weaken evidence gates.
- Prefer adapting the existing report-data model and self-contained template over introducing a parallel source of truth.
- Default overview density should stay within roughly 8–15 core nodes; a second level is justified only when a top-level boundary cannot otherwise be understood.
- Preserve unrelated working-tree changes and isolate implementation work from the existing active architecture-map initiative.
- Treat `https://github.com/tt-a1i/archify` at commit `4ac500a498267f18bda42b3c82b51edb8f9c1baf` as a read-only design reference. Do not require a checkout; if implementation needs repeated source inspection, clone it outside this repository (for example `/tmp/archify-reference`) and keep it untracked.

## Phases

1. P1 — A tested presentation contract defines the high-level information hierarchy, visual language, focus behavior, path behavior, and visual acceptance gates — status: done
2. P2 — The shared renderer presents the high-level system map with consistent boundaries, hierarchy, focus, and critical-path emphasis — status: active
3. P3 — Automated and real-browser visual checks demonstrate readable, stable reports without regressing evidence or offline behavior — status: pending
