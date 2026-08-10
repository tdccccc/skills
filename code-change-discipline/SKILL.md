---
name: code-change-discipline
description: 'Baseline discipline for changing source code, tests, or executable configuration, including schema, migrations, build, CI, and deployment behavior. Use whenever implementing, fixing, refactoring, or optimizing executable behavior — including one-line and few-line fixes — even when the user does not mention testing. Select a test strategy before editing and require observed evidence. Not for read-only investigation or pure prose/documentation edits.'
install-targets: claude
---

# Code Change Discipline

Choose the test strategy before changing executable behavior. The behavior and risk determine the strategy; file type and line count do not.

This skill owns the baseline change discipline. A coordinating workflow such as Helm may add planning, acceptance, reporting, or commit gates without weakening these rules.

## Classify the change

Classify each coherent change before editing production logic:

| Change kind | Default strategy |
|-------------|------------------|
| New or changed behavior | Strict Red → Green → Refactor |
| Bug fix | Reproduce the bug with a failing regression test, then Red → Green → Refactor |
| Behavior-preserving refactor | Establish a Green characterization or contract baseline; keep it Green |
| Optimization | Establish correctness checks and a repeatable baseline; optimize, then compare |
| Non-behavioral edit | Run proportionate verification; do not manufacture a test cycle |

Treat configuration, schemas, migrations, templates, build logic, CI, and deployment files as behavioral when they can change an executable outcome. Documentation, comments, formatting, and mechanically regenerated artifacts normally need proportionate verification rather than TDD.

## Apply the selected strategy

### Behavior changes and bug fixes

1. Write or adjust the smallest behavior test that expresses the missing or incorrect observable outcome.
2. Run it before changing production logic.
3. Confirm an expected Red caused by the target behavior being absent or wrong.
4. Write the minimum production change needed for that behavior.
5. Run the same test and observe Green.
6. Refactor only while the tests stay Green.
7. Run relevant regression checks after the focused test is Green.

Prefer a stable public, contract, API, CLI, UI, persistence, or component boundary over private implementation details. A test should survive reasonable internal refactoring.

### What counts as Red

A valid Red reaches the intended behavioral contract and fails for the expected reason. When adding a typed API, an expected compiler or type-checker failure caused specifically by the missing contract may be the first valid Red; after introducing the smallest compilable surface, continue to a behavioral Red when further behavior remains. Do not bypass the type system merely to turn an expected contract failure into a runtime failure.

A syntax or collection error unrelated to the requested contract, broken fixture, environment failure, flaky result, or unrelated pre-existing failure is not TDD evidence; fix or isolate it before proceeding.

If the new test already passes, stop and investigate. The behavior may already exist, the assertion may not exercise it, or the requested change may differ from the current assumption. Do not damage a test to manufacture Red.

### Behavior-preserving refactors

Confirm existing coverage or add a Green characterization or contract baseline before restructuring production code. Keep that baseline and relevant regressions Green throughout the refactor. Do not manufacture a Red when the intended behavior is unchanged.

If adding a test seam requires production edits, make the smallest behavior-preserving seam change under the Green baseline before starting a later behavior-changing Red/Green cycle.

### Optimizations

Establish correctness checks and a repeatable performance baseline before optimizing. Preserve correctness, compare the same measurement before and after, and state environmental limits or variance. Do not manufacture a functional Red for an optimization whose behavior should remain unchanged.

A stable performance acceptance threshold may be treated as the focused failing check. An unstable benchmark is evidence for investigation, not a reliable gate.

### Non-behavioral edits

For prose, comments, formatting, or mechanical regeneration, use the cheapest check that can catch the plausible mistake: rendering, linting, generation consistency, or inspection. If investigation shows an executable outcome changed, reclassify the work before editing further.

## Exceptions

A missing test seam, exploratory spike, emergency repair, destructive migration, external dependency, hardware boundary, or unavailable environment may prevent a meaningful automated Red. Do not silently relabel manual verification as TDD.

Before continuing under an exception, record:

- the reason test-first cannot be followed now;
- the affected change scope;
- compensating verification and its observed result;
- the follow-up regression test or other debt, when one is still required.

Treat exploratory spike code as disposable until it re-enters the appropriate strategy and passes its evidence gate. During an emergency repair, restore service with the safest available check, then add the regression test as soon as the emergency constraint is gone. Never claim an unobserved Red, Green, baseline, or regression result.

## Protect the working tree

Inspect applicable repository instructions and the working-tree status before editing. Preserve unrelated user changes, keep the change coherent and minimal, and do not broaden it with opportunistic cleanup.

When a test exposes a wrong assumption about the requested behavior or implementation path, stop and reclassify or re-plan rather than forcing the current edit through.

## Finish with evidence

Run the focused check and relevant regression checks appropriate to the change and risk. Then inspect the final diff and working-tree status for accidental or unrelated edits.

Report:

- the changed behavior and paths;
- test strategy used;
- observed results, including Red/baseline and Green when applicable;
- checks not run and why;
- remaining risks or promised follow-up.

Never replace an observed result with “should pass.”

## Workflow ownership

Following this skill does not authorize a commit. Staging, committing, reporting handoffs, and final acceptance belong to the upper-level workflow or an explicit user request. When Helm is active, its Checkpoint and commit rules own those transitions; a delegate returns evidence and changed paths to the owner.
