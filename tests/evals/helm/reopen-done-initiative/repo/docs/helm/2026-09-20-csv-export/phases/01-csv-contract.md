# P1 — csv-contract

goal_ref: ../goal.md
created: 2026-09-20T10:05:00+08:00
updated: 2026-09-20T15:10:00+08:00
revision: 2

## Outcome

The CSV columns and their order (`id,customer,note`) are fixed by a tested contract.

## Chunks

### Chunk 1 — Header contract

- change: `export_orders([])` returns only the header row
- kind: behavior
- first signal: Red — `export_orders` does not exist yet
- checks: `python3 -m unittest test_export`
- [x] accepted on observed evidence

## Phase verification

- `python3 -m unittest` passes.
