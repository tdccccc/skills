# Architecture map review follow-up

status: done
updated: 2026-08-30
owner: session-2026-08-30-tiandc

## Intent

Resolve the strongest actionable findings recovered from the interrupted review of PR #7: preserve renderer containment during search, make section-tab title uniqueness match the UI, and align validator documentation with executable behavior.

## Success criteria

- [x] Search does not throw or blank the diagram when `notes` or `evidence` is present but not an array.
- [x] `--validate` rejects whitespace-equivalent section titles and titles that collide with the fixed architecture tab.
- [x] REFERENCE accurately lists duplicate section-title validation and points to the actual validation gates.
- [x] Focused Red/Green evidence and both architecture-map test suites are green.

## Non-goals

- Escape/IME behavior, pan/zoom preservation, or breadcrumb layout changes.
- Broader search indexing, schema redesign, or renderer performance work.
- The active `2026-08-19-architecture-map-reader-model` initiative.

## Constraints

- Preserve the single-file offline report and current `report-data` schema.
- Keep this follow-up to one phase and do not use subagents.
- Do not modify or commit the untracked round-3 `handoff.md`.
- Use isolated commits for accepted implementation and Helm close state.

## Phases

<!-- Single source of truth for phase status. PN ↔ filename NN. Outcomes only — no steps. The active line is the current focus. -->
1. P1 — Search containment, tab-title uniqueness, and validator documentation are aligned and regression-tested — status: done
