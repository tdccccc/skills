# Helm Reference — transitions, steers, handoffs, delegation

Read the matching section before executing a phase transition, a steer, a revisit, a handoff, or a delegation. Classification lives in SKILL.md; this file holds the mechanics.

Every operation below is one logical edit: change status only in goal.md, bump each edited file's metadata once (preserve `created`, set `updated`, increment `revision`), append the journal entry where required, then — only when goal.md Constraints authorize commits — commit the touched artifacts once, e.g. `docs(helm): start P3`. An operation that starts another phase folds Start's state changes into the same edit and commit.

## Phase transitions

### Start phase `PN`

1. Ensure `phases/NN-<slug>.md` exists (create it from the template if needed).
2. Make sure the goal may run a phase, reopening it when needed:
   - `active` stays `active`;
   - `done` → `active`: new work against a closed initiative reopens it;
   - `proposed` → `active` only once the user has confirmed the goal; otherwise stop without starting;
   - `abandoned` → `active` only after the user confirms restarting; journal that decision.
3. Move any other `active` line to `done`, `blocked`, or `pending` as appropriate; set `PN` to `active` and `owner` to the current session or agent.

### Complete phase `PN`

1. Confirm every chunk is accepted and each **Phase verification** check has an observed passing result, or a recorded exception with compensating verification.
2. If a phase-level check fails or was not run, leave PN `active`: record the fix as a new chunk (L1) or steer, and tell the user what failed. Do not mark it done.
3. Otherwise set `PN` → `done`, then Start the next phase, Close when the success criteria are met, or pause with no phase `active`. Commit: `docs(helm): PN done` (append `, start PM` when another phase starts).

### Block phase `PN`

1. Index line → `blocked`; journal what blocks it.
2. Start another existing phase, or pause the initiative. Commit: `docs(helm): block PN`.

### Supersede phase `PN`

1. Index line → `superseded`.
2. Add the replacement under the next unused integer `PM` (never reuse `PN` or add a letter suffix) and create its phase file.
3. Leave `PM` `pending` unless an enclosing L2, L3, or revisit starts it. Commit: `docs(helm): supersede PN`.

## Steer

### L1 — Adjust (local)

1. Edit the current phase's chunks or approach in place; a one-line journal note is optional.
2. No standalone commit: the edit rides along with the next chunk or transition commit.
3. Continue executing.

### L2 — Reshape (path)

1. Tell the user `L2 reshape — <one line why>` and stop digging the same hole.
2. Supersede the failed phase and Start its replacement under the next unused integer.
3. Decide which tests still express a stable goal-level contract and which encode the failed path; keep, rewrite, discard, or revert them together with the implementation.
4. Update goal.md outcomes or order if the roadmap changed; keep Intent and Success criteria stable.
5. Journal: evidence → path change → code/test disposition → next focus.
6. Commit `docs(helm): L2 reshape`, restate the focus, and resume from the new active phase only.

### L3 — Steer (destination)

1. Tell the user `L3 steer — <one line why>`; **freeze** feature work.
2. Journal the evidence: what we learned, with links to reports or logs.
3. Revise goal.md in place — Intent, Success criteria, Non-goals, Constraints, Phases. Keep still-valuable `done` phases, supersede dead ones, and add new phases under the next unused integers.
4. Decide which code and tests to keep, rewrite, discard, or revert — an old test may encode a destination that is no longer valid — and journal it.
5. If the new direction changes term meanings or reverses recorded decisions, update `CONTEXT.md` or supersede the ADR in the same edit (per `domain-modeling`).
6. Branch:
   - **Needs re-approval** (the user asked to confirm, or the change is large or hard to reverse): set the goal `status: proposed`, leave no phase `active`, commit `docs(helm): L3 steer (proposed)`, present the revised goal, and stop until the user confirms. On confirmation, Start the new current phase.
   - **Already approved:** write the plan for the new current phase, Start it, commit `docs(helm): L3 steer`, restate the focus, and continue.

## Revisit completed work

Use this when later evidence challenges a phase already marked `done`, including one in a closed initiative.

1. Classify first: if Intent or Success criteria changed, use L3; otherwise continue here.
2. Preserve the completed phase file and ID. Allocate the next unused integer `PM` and write its phase file for the investigation or correction.
3. Set the old phase from evidence: keep `done` when its accepted outcome remains valid and `PM` is incremental follow-up; change it to `superseded` when the accepted outcome or approach is no longer trustworthy.
4. Trace dependency impact through later phases: keep phases whose outcomes remain valid `done`; supersede only invalidated ones and add replacements under further unused integers.
5. Decide which implementation and tests to keep, rewrite, discard, or revert; do not assume every dependent artifact is invalid.
6. Journal: new evidence → old acceptance → affected phases and dependency assessment → code/test disposition → next focus.
7. Start `PM`; on a `done` goal this reopens it to `active`. If a success criterion is no longer met, untick it. Commit: `docs(helm): revisit PN via PM`.

## Handoff

- An initiative has one owner and at most one active phase. A handoff transfers the whole initiative; it never creates parallel phase owners.
- In one edit, append a journal entry (result so far + next step) and update `owner`. Commit: `docs(helm): handoff to <owner>`.
- The receiving session reads goal.md, the active phase file, and recent journal entries, restates the focus, and continues.

## Delegation contract

**Brief** — give the delegate:

- what to read: goal.md, the active phase file, recent journal entries, and `CONTEXT.md` if present;
- the chunk to implement and its write scope; goal.md and journal.md are read-only;
- the chunk's planned checks: test strategy, target test, expected Red or Green baseline, Green and regression commands, and any approved exception;
- that it must not commit or delegate further, and must stop and report when the planned evidence cannot be obtained rather than bypass the strategy.

**Report** — require back:

- the changed paths and isolated diff scope;
- observed Red, Green, and regression results as applicable, taken from actual runs;
- checks not run and why, plus blockers or surprises relevant to the phase.

The owner runs a Checkpoint on the report; ticking the chunk and committing stay with the owner. For read-only intake recon, build the brief from `templates/intake-prompt.md` instead.
