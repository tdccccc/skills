# Architecture map interaction and layout

status: done
updated: 2026-08-18
owner: /root

## Intent

Improve the architecture-map skill's generated HTML so large current-state diagrams remain readable and operable: users can move around the canvas, reposition nodes, and inspect relationships without losing the existing drill-down and evidence views.

## Success criteria

- [x] The template supports node dragging, canvas panning, wheel/button zoom, and a fit/reset action in an offline single-file report.
- [x] Edge routing and layout reduce avoidable crossings/overlap while preserving direction, labels, selection, search, and drill-down behavior.
- [x] Focused interaction/regression tests cover the new behavior and the skill authoring guidance explains the interaction contract.
- [x] The requested arxiv-daily report is reviewed against implementation evidence and its HTML shell is migrated to the browser-smoked interactive template while preserving `report-data` exactly.

## Non-goals

- Redesigning the arxiv-daily implementation or changing its runtime architecture.
- Adding external JavaScript/CSS dependencies or a server requirement.
- Treating the visual report as implementation evidence without source verification.

## Constraints

- Keep the report self-contained and compatible with direct offline browser opening.
- Preserve the existing JSON data schema and current behavior contracts unless a change is required for interaction.
- Respect the architecture-map evidence rules: report content remains current-state and code-evidenced.

## Phases

<!-- Single source of truth for phase status. PN ↔ filename NN. Outcomes only — no steps. The active line is the current focus. -->
1. P1 — An interactive, routed diagram template passes focused and regression checks — status: done
2. P2 — The skill guidance and requested arxiv-daily artifact reflect the accepted renderer — status: done
