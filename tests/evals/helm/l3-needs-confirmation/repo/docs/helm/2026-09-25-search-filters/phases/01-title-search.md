# P1 — title-search

goal_ref: ../goal.md
created: 2026-09-25T09:40:00+08:00
updated: 2026-09-26T17:05:00+08:00
revision: 2

## Outcome

`search` matches article titles case-insensitively.

## Chunks

### Chunk 1 — Case-insensitive title match

- change: `search(articles, "packaging")` matches "Python Packaging"
- kind: behavior
- first signal: Red — `search` does not exist yet
- checks: `python3 -m unittest test_search`
- [x] accepted on observed evidence

## Phase verification

- `python3 -m unittest` passes.
