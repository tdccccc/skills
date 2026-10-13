# Slug CLI

status: active
created: 2026-10-02T14:00:00+08:00
updated: 2026-10-03T10:15:00+08:00
revision: 2
owner: session-2026-10-03

## Intent

Give writers a command that turns an article title into a URL slug.

## Success criteria

- [ ] `python3 cli.py "Hello, World!"` prints `hello-world`.
- [ ] `python3 -m unittest` passes.

## Non-goals

- Transliterating non-ASCII titles.

## Constraints

- Standard library only.
- Commits: none

## Phases

1. P1 — A `cli.py` command prints the slug for a title — status: active
