# P3 — Search, validator, and documentation polish

<!-- Filename must be NN-<slug>.md with NN = N (e.g. P1 → 01-auth.md). -->
<!-- Status lives in goal.md's phase index, not here. -->
goal_ref: ../goal.md
updated: 2026-08-30

## Outcome

Search matches `notes` and `evidence` in addition to label/summary/detail, Escape clears the search filter along with the selection, `--validate` rejects duplicate section titles, the module `summary` length guidance matches what node widths can display, and the duplicated REFERENCE checklist items are collapsed onto their canonical homes — with every contract-test-asserted phrase still passing.

## Assumptions

- Both template changes (search haystack, Escape) ship as one template version bump (4 → 5) with a single seed refresh, since the version meta belongs to the shell as a whole.
- The contract tests pin many REFERENCE phrases; the dedupe must preserve every asserted phrase (or update the assertion deliberately). The full python suite is the safety net.
- The summary guidance change is documentation: node width math (96–240px, text area `w−18`, CJK at 11px) caps visible CJK at ~7–20 characters, so "thirty characters" is unreachable for CJK.

## Approach

1. Renderer: extend the `matches()` haystack with `notes` and `evidence`; extend the Escape handler to clear the search input and `state.query`. Bump the version meta to 5, refresh seeds, update the python version assertions (installed 5, future 6).
2. Validator: track seen section titles in `--validate` and report `duplicate section title`; add the python subtest case.
3. Docs: fix the REFERENCE summary-length guidance; collapse REFERENCE "Content-boundary checklist" items that merely restate SKILL's Content contract, the `--validate`-covered structural invariants, or "Validation before writing" rendering checks into references to those canonical homes. Keep the audit-specific items.

## Test strategy

- change kind: behavior change (search/Escape), bug-class hardening (validator), non-behavioral (docs)
- strategy: strict Red-Green for the two behaviors and the validator; proportional contract assertions for the docs
- Red / baseline signal:
  - jsdom: "search matches module evidence and notes" (a token present only in `evidence` dims the node today) and "escape clears the search filter" (dims persist today) fail
  - python: new "duplicate section title" subtest fails (exit 0, no message today)
- Green / regression checks: `node tests/test_architecture_map_template.mjs` all green; `python3 -m pytest tests/test_architecture_map_skill.py -q` all green (this also proves no asserted phrase was lost in the dedupe); seeds pass `--check` vs v5
- exception: none

## Tasks

- [x] Search haystack + Escape behavior with jsdom tests (Red → Green), version bump 4 → 5, seed refresh, python version assertions
- [x] `--validate` duplicate section title with python subtest (Red → Green)
- [x] REFERENCE summary-length guidance + "Content-boundary checklist" dedupe with contract assertions (proportional)

## Verification

- Red observed (single run, all four): jsdom 90/92 — `FAIL: search matches module notes and evidence [ 'a', 'b' ]` and `FAIL: escape clears the search filter`; python `SUBFAILED(violation='duplicate section title') ... AssertionError: 0 != 2 ... valid:`; phrase assertion in `test_reader_first...` failing
- Green observed: jsdom 92/92; python 26 passed, 23 subtests passed (seed `--check` vs v5 included; no asserted phrase lost in the dedupe)
- Final headless-Chrome smoke on the v5 shell @1400×900: 6 nodes, 6 edges, PANEL t=112 (below tab bar), SEARCH t=21,b=50 fully visible
- Checks not run: no headless-browser step in CI (jsdom-only); Chrome probes are local compensating verification

## Abort / reshape triggers

- If the checklist dedupe breaks asserted phrases that the dedupe was supposed to keep, stop: restore the removed text and narrow the dedupe scope (L1) rather than weakening the contract tests.
- If the search change slows rendering noticeably (full re-render per keystroke already exists, so expectation: no regression), profile before accepting.
