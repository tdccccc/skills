# P2 — tag-filter

goal_ref: ../goal.md
created: 2026-09-27T09:10:00+08:00
updated: 2026-09-27T11:20:00+08:00
revision: 2

## Outcome

Search results can be narrowed to articles carrying one tag.

## Chunks

### Chunk 1 — Single-tag filter

- change: `search(..., tag="rust")` keeps only articles tagged `rust`
- kind: behavior
- first signal: Red — `search` rejects the `tag` argument
- checks: `python3 -m unittest test_search`
- [x] accepted on observed evidence

### Chunk 2 — Unknown tags return no results

- change: a tag no article carries yields an empty list
- kind: behavior
- first signal: Red — new test expects `[]` for `tag="go"`
- checks: `python3 -m unittest test_search`
- [ ] accepted on observed evidence

## Phase verification

- `python3 -m unittest` passes.
