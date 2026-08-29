# P2 — One consistent no-report resolution for update/audit

<!-- Filename must be NN-<slug>.md with NN = N (e.g. P1 → 01-auth.md). -->
<!-- Status lives in goal.md's phase index, not here. -->
goal_ref: ../goal.md
updated: 2026-08-29

## Outcome

SKILL.md's `### update` and `### audit` sections state the same no-report resolution as the `## Modes` decision rules and REFERENCE.md's mode mechanics: plain update/audit without a report falls back to `init`; `blocked` with an `init` recommendation applies only when the user explicitly insists on update/audit semantics for an established report. Contract tests pin all three statements.

## Assumptions

- The `## Modes` decision rules + REFERENCE mode mechanics + the `insisted-update-no-report` eval (expects `blocked`) define the intended canonical rule; only the two SKILL.md section closers are wrong.
- Pinning exact phrases in the contract tests is the repo's established convention for doc consistency (existing tests already assert dozens of phrases), so the test is proportional verification rather than manufactured TDD.

## Approach

Rewrite only the two closing lines of SKILL.md `### update` (line ~234) and `### audit` (line ~249) to state the fallback-then-blocked rule and reference the mode resolution. REFERENCE.md already matches and is left untouched. Add section-scoped assertions to `test_modes_and_result_contract_are_explicit`.

## Test strategy

- change kind: non-behavioral (skill documentation), verified through the repo's contract-test convention
- strategy: contract assertions first (Red), doc edit (Green) — proportional verification per code-change-discipline; the asserted phrases are the executable surface of this fix
- Red / baseline signal: `python3 -m pytest tests/test_architecture_map_skill.py::ArchitectureMapSkillContractTests::test_modes_and_result_contract_are_explicit -q` fails on the new "fall back to `init`" / "explicitly insists" assertions in the `### update` / `### audit` sections
- Green / regression checks: same test green; full `python3 -m pytest tests/test_architecture_map_skill.py -q` green; `node tests/test_architecture_map_template.mjs` green (untouched)
- exception: none

## Tasks

- [x] Add section-scoped contract assertions for the no-report resolution (Red observed)
- [x] Rewrite the `### update` / `### audit` closers in SKILL.md (Green)
- [x] Run the full suites and record results

## Verification

- Red observed: focused test stashed against the old SKILL.md → `AssertionError: 'fall back to `init`' not found in ... If no report exists, return `blocked` and recommend `init`; do not silently create a partial report.` (1 failed)
- Green observed: after the fix, `python3 -m pytest tests/test_architecture_map_skill.py -q` → 26 passed, 22 subtests passed; `node tests/test_architecture_map_template.mjs` → 90/90 (untouched)
- Checks not run: none relevant — docs-only change pinned by contract assertions

## Abort / reshape triggers

- If the intended rule turns out to be the opposite (always `blocked` when no report), the `## Modes` rules, REFERENCE, and the `insisted-update-no-report` eval would all need reinterpretation — stop and confirm the canonical rule with the user before editing (that would be L3, not a wording fix).
