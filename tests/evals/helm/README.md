# Helm behavior evals

These scenarios check what an agent actually does with the Helm skill, not only what the skill text says. Each case covers a lifecycle branch that is easy to get wrong.

| Case | Branch under test |
|------|-------------------|
| `reopen-done-initiative` | New evidence against a closed initiative reopens the goal and starts a new phase |
| `l3-needs-confirmation` | A goal change awaiting approval leaves the goal `proposed` with no active phase |
| `phase-verification-gate` | Accepted chunks are not enough; a failing phase-level check keeps the phase open |
| `small-task-skips-helm` | A small, well-scoped change is done directly without Helm artifacts |

Each case contains:

- `prompt.md` — the user request, sent verbatim;
- `case.json` — machine-checked `state_checks` plus reviewer-judged `hard_failures`;
- `repo/` — the seed repository.

## Run a case

1. Copy `repo/` into a fresh temporary directory, then `git init` and commit it there. Never run an agent inside the canonical fixture.
2. Start a fresh agent in that copy with the Helm skill installed and send `prompt.md`. Do not show it `case.json`.
3. Check the final state:

   ```bash
   python3 tests/evals/helm/check_state.py tests/evals/helm/<case> <copy>
   ```

4. Read the transcript against `hard_failures`. Any hit fails the case even when every state check passes.

`tests/test_helm_skill.py` keeps the fixtures honest: every untouched seed must fail its checks, and a scripted reference outcome must pass them.
