# Search filters

status: active
created: 2026-09-25T09:30:00+08:00
updated: 2026-09-27T11:20:00+08:00
revision: 3
owner: session-2026-09-27

## Intent

Help users find saved articles faster by narrowing keyword search results.

## Success criteria

- [x] Search matches article titles case-insensitively.
- [ ] Users can narrow search results to a single tag.
- [ ] The CLI exposes the tag filter.

## Non-goals

- Full-text search over article bodies.

## Constraints

- Standard library only.
- Commits: none

## Phases

1. P1 — Case-insensitive title search is tested — status: done
2. P2 — Search results can be narrowed to one tag — status: active
3. P3 — The tag filter is exposed in the CLI — status: pending
