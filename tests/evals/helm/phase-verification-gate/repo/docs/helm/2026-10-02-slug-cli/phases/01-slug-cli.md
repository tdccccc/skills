# P1 — slug-cli

goal_ref: ../goal.md
created: 2026-10-02T14:10:00+08:00
updated: 2026-10-03T10:15:00+08:00
revision: 3

## Outcome

`python3 cli.py "<title>"` prints the URL slug for the title.

## Chunks

### Chunk 1 — Slugify titles

- change: `slugify("Hello, World!")` returns `hello-world`
- kind: behavior
- first signal: Red — `slug.py` does not exist yet
- checks: `python3 -m unittest test_slug`
- [x] accepted on observed evidence

### Chunk 2 — CLI argument parsing

- change: `cli.py` takes the title as its positional argument
- kind: behavior
- first signal: Red — `cli.py` does not exist yet
- checks: `python3 -m unittest test_cli`; `python3 -m unittest`
- [x] accepted on observed evidence

## Phase verification

- `python3 cli.py "Hello, World!"` prints `hello-world`.
- `python3 -m unittest` passes.

## Abort / reshape triggers

- If slugs need transliteration to be useful, stop and steer (L3).
