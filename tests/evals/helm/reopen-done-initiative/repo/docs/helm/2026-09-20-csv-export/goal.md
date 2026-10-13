# CSV order export

status: done
created: 2026-09-20T10:02:00+08:00
updated: 2026-09-21T16:40:00+08:00
revision: 4
owner: session-2026-09-21

## Intent

Let support staff download all orders as CSV so they can reconcile them in a spreadsheet.

## Success criteria

- [x] `export_orders` returns a header row plus one row per order.
- [x] The export opens in a spreadsheet with one column per field.

## Non-goals

- Filtering or paging orders.

## Constraints

- Standard library only.
- Commits: none

## Phases

1. P1 — The CSV columns and their order are fixed by a tested contract — status: done
2. P2 — `export_orders` writes one CSV row per order — status: done
