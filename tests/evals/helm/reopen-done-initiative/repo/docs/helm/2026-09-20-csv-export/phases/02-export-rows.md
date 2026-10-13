# P2 — export-rows

goal_ref: ../goal.md
created: 2026-09-20T15:20:00+08:00
updated: 2026-09-21T16:30:00+08:00
revision: 2

## Outcome

`export_orders` writes one CSV row per order under the header.

## Chunks

### Chunk 1 — Rows for every order

- change: each order becomes one `id,customer,note` row
- kind: behavior
- first signal: Red — `test_one_row_per_order` fails because only the header is returned
- checks: `python3 -m unittest test_export`; `python3 -m unittest`
- [x] accepted on observed evidence

## Phase verification

- The sample export (notes `gift`, `rush`) opens in a spreadsheet with one column per field.
