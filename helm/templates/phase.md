# P{N} — {slug}

<!-- Filename must be NN-<slug>.md with NN = N (e.g. P1 → 01-auth.md). -->
<!-- Phase numbers are permanent integers: replacements take the next unused number. -->
<!-- Status lives in goal.md's phase index, not here. -->
goal_ref: ../goal.md
created: {YYYY-MM-DDTHH:MM:SS±HH:MM}
updated: {YYYY-MM-DDTHH:MM:SS±HH:MM}
revision: 1

## Outcome

{One sentence: what is true when this phase is done.}

## Assumptions

- {Assumption that might be wrong}

## Approach

{Short path description — not an essay.}

## Chunks

<!-- kind: behavior | bug fix | refactor | optimization | non-behavioral.
     first signal: the expected Red for behavior changes and bug fixes, the Green or performance
     baseline to preserve for refactors and optimizations, or "n/a" for non-behavioral edits.
     Add `- exception:` only when test-first is infeasible: reason, compensating verification, follow-up. -->

### Chunk 1 — {one coherent, independently acceptable change}

- change: {what becomes true}
- kind: {kind}
- first signal: {expected Red or baseline, with the command}
- checks: {focused Green check and relevant regression checks, with expected signals}
- [ ] accepted on observed evidence

### Chunk 2 — {one coherent, independently acceptable change}

- change: {what becomes true}
- kind: {kind}
- first signal: {signal}
- checks: {checks}
- [ ] accepted on observed evidence

## Phase verification

<!-- Cross-chunk or end-to-end checks; an observed pass is required before the phase is done. -->
- {Check and expected signal}

## Abort / reshape triggers

- If {signal}, stop and reshape (L2) or steer (L3) instead of pushing.
