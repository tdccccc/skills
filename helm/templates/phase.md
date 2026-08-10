# P{N} — {slug}

<!-- Filename must be NN-<slug>.md with NN = N (e.g. P1 → 01-auth.md). -->
<!-- Status lives in goal.md's phase index, not here. -->
goal_ref: ../goal.md
updated: {YYYY-MM-DD}

## Outcome

{One sentence: what is true when this phase is done.}

## Assumptions

- {Assumption that might be wrong}
- {Assumption that might be wrong}

## Approach

{Short path description — not an essay.}

## Test strategy

- change kind: {behavior change | bug fix | behavior-preserving refactor | optimization | non-behavioral}
- strategy: {strict Red-Green-Refactor | Green characterization baseline | correctness + performance baseline | proportionate check}
- Red / baseline signal: {focused command and expected failure reason, or the Green baseline to preserve}
- Green / regression checks: {focused and relevant regression commands with expected signals}
- exception: {why test-first is infeasible and the compensating verification; omit when none}

## Tasks

- [ ] {One coherent, independently acceptable behavior chunk with its tests}
- [ ] {One coherent, independently acceptable behavior chunk with its tests}
- [ ] {Non-behavioral task, if needed}

## Verification

- {Focused command or check and observed success signal}
- {Relevant regression command or check and observed success signal}

## Abort / reshape triggers

- If {signal}, stop and reshape (L2) or steer (L3) instead of pushing.
- If {signal}, ...
