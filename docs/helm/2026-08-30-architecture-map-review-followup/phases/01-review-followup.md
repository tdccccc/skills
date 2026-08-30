# P1 — review follow-up

goal_ref: ../goal.md
updated: 2026-08-30

## Outcome

Search containment, section-tab title uniqueness, and the documented validator contract agree and are protected by focused regressions.

## Assumptions

- Invalid non-array `notes` / `evidence` should be silently omitted from search rather than crashing, while `--validate` continues to reject them.
- Section titles are display labels: surrounding whitespace is not identity, and `架构` is reserved by the fixed diagram tab.
- These changes do not alter the data schema or require a template-version bump unless renderer shell behavior changes incompatibly.

## Approach

Add focused failing checks first, then make the smallest renderer and validator changes and update only the drifting REFERENCE statements. Keep Escape, breadcrumb, and broader cleanup candidates out of scope.

## Test strategy

- change kind: bug fix
- strategy: strict Red-Green-Refactor
- Red / baseline signal: focused jsdom check fails because search clears the canvas for non-array fields; focused Python subtests fail because whitespace-equivalent and reserved section titles pass validation and documentation omits the executable rule.
- Green / regression checks: focused checks pass; `node tests/test_architecture_map_template.mjs` reports all checks passed; `python3 -m pytest tests/test_architecture_map_skill.py -q` reports all tests/subtests passed.

## Tasks

- [x] Add a jsdom regression for non-array searchable fields, observe Red, then make search containment total and observe Green.
- [x] Add validator regressions for trimmed duplicate titles and the reserved architecture-tab title, observe Red, then enforce both and observe Green.
- [x] Align REFERENCE validator coverage and validation-gate wording; pin relevant contract text if appropriate.
- [x] Run focused and full regressions, checkpoint the isolated change, then close the initiative.

## Verification

- Red — `node tests/test_architecture_map_template.mjs`: `TypeError: (n.notes || []).join is not a function`; containment checks failed with 0 nodes; 92/94 passed.
- Red — `python3 -m pytest tests/test_architecture_map_skill.py -q`: whitespace-equivalent and reserved `架构` titles were accepted, and validator documentation assertions failed.
- Green — `node tests/test_architecture_map_template.mjs`: 94/94 checks passed.
- Green — `python3 -m pytest tests/test_architecture_map_skill.py -q`: 27 passed, 25 subtests passed.
- Regression — every seed report returned `current` under `refresh-template.mjs --check`; `git diff --check` passed.
- Architecture-map handoff not enabled: the repository has no established `docs/architecture-map.html` report.

## Abort / reshape triggers

- If containing invalid fields requires changing the report schema or accepting them in `--validate`, stop and reshape rather than weakening validation.
- If reserving `架构` breaks an established valid seed/report, inspect the contract before changing the invariant.
- If the fixes require Escape, breadcrumb, or reader-model changes, leave them as separate follow-ups.
