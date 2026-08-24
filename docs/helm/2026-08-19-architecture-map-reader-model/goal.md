# Architecture map reader model

status: active
updated: 2026-08-19
owner: /root

## Intent

Make architecture-map reports explain a repository as a small set of runtime, business, data, and trust boundaries that a new maintainer can follow. Keep diagrams interactive, but make the main path and the five supporting sections understandable without decoding package names or abstract architecture prose.

## Success criteria

- [ ] The skill requires a reader-first architecture model, explicit Host-to-use-case traceability, and a sparse main-spine edge pass for every drill-down.
- [ ] Cross-cutting sections use direct actor/action/result language, ordered flows, and comparison tables instead of abstract inventories.
- [ ] The arxiv-daily report matches verified implementation semantics and its overview/Core views have no route failures or proper edge crossings.
- [ ] Desktop and narrow real-browser smoke checks cover diagram interaction, panel layout, tabs, scrolling, and console output.

## Non-goals

- Changing arxiv-daily runtime code or product behavior.
- Adding external assets, a server requirement, or a new report format.
- Committing the working-tree changes in this task.

## Constraints

- Preserve the single-file offline HTML contract and the existing report-data schema.
- Keep implementation claims supported by production source or executable configuration.
- Preserve unrelated user changes in both repositories.

## Phases

1. P1 — The skill and arxiv-daily report are reader-first, semantically accurate, and browser-verified — status: active
