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
- {Assumption that might be wrong}

## Approach

{Short path description — not an essay.}

## Chunks

### Chunk 1 — {one coherent, independently acceptable change}

- change kind: {behavior change | bug fix | behavior-preserving refactor | optimization | non-behavioral}
- strategy: {strict Red-Green-Refactor | Green characterization baseline | correctness + performance baseline | proportionate check}
- Red / baseline signal: {focused command and expected failure reason, or the Green baseline to preserve}
- Green check: {focused command and expected success signal}
- regression checks: {relevant commands and expected signals}
- exception: {why test-first is infeasible and the compensating verification; omit when none}
- [ ] implementation and tests accepted

### Chunk 2 — {one coherent, independently acceptable change}

- change kind: {kind}
- strategy: {strategy}
- Red / baseline signal: {signal}
- Green check: {check}
- regression checks: {checks}
- exception: {omit when none}
- [ ] implementation and tests accepted

## Phase verification

- {End-to-end or cross-chunk check and observed success signal}
- {Relevant phase-level regression check and observed success signal}

## Abort / reshape triggers

- If {signal}, stop and reshape (L2) or steer (L3) instead of pushing.
- If {signal}, ...
