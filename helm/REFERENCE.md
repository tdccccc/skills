# Helm Reference — transitions & steer mechanics

Read this file when executing a **phase transition** or an **L1/L2/L3 steer**, after classifying in SKILL.md. It holds the mechanical steps only — the classification logic lives in SKILL.md.

Status edits happen in the **goal.md phase index only** (single source of truth); phase files carry no status field.

**Git sync:** every standalone transition and steer below ends with one commit of the artifacts it touched (goal.md, phase file, journal.md, and any CONTEXT.md / ADR changes). Accepted implementation chunks are committed at Checkpoint per SKILL.md; this file covers artifact commits only. When one transition calls another, apply the nested transition's state changes but skip its commit; the outermost transition commits the complete state change once. Commit messages name the transition, e.g. `docs(helm): start P3`, `docs(helm): L2 reshape`.

## Phase transitions

### Start phase `PN`

1. Ensure `phases/NN-<slug>.md` exists (create from template if needed).
2. Set the goal.md index line for `PN` to `status: active`; set `owner` to the current session/agent.
3. Any previously `active` line → `done` (if completed) or `blocked` / `pending` as appropriate — never two `active` lines.
4. When Start is standalone, commit the goal.md and new phase file: `docs(helm): start PN`.
5. When Start is nested inside Complete, L2, or L3, do not commit here; the outer transition commits once after all related edits are complete.

### Complete phase `PN`

1. Confirm every chunk's required verification has an observed successful result, including relevant regression checks and any recorded exception's compensating verification.
2. Index line `PN` → `done`.
3. Choose the next phase (or Close if none).
4. If next exists, apply **Start** state changes without its standalone commit; otherwise leave it `pending` and pause if the user stops here.
5. Commit once after the complete state change: `docs(helm): PN done` (add `, start PM` when another phase starts in the same turn).

### Block phase `PN`

1. Index line → `blocked`; journal one line: what blocks it.
2. Either activate another existing phase using Start state changes without a nested commit, or pause the initiative.
3. Commit once: `docs(helm): block PN`.

### Supersede phase `PN`

1. Index line → `superseded`.
2. Allocate the next unused integer `PM`; never reuse `PN` or add a letter suffix.
3. Add `PM` to the goal index and create `phases/MM-<slug>.md` for the replacement path.
4. Leave `PM` pending unless this operation is part of an outer L2/L3 transition that activates it.
5. When standalone, commit once: `docs(helm): supersede PN`.

## Steer action lists

### L1 — Adjust (local)

1. Use L1 when the phase outcome still holds and the plan needs local correction, including a merely messy plan.
2. Edit the current phase tasks / approach in place.
3. On first journal-worthy event, create `journal.md` if missing; append from `templates/journal-entry.md` (optional one-liner for tiny L1).
4. Commit the phase / journal edits once: `docs(helm): L1 adjust PN`.
5. Continue executing.

### L2 — Reshape (path)

1. Tell the user: `L2 reshape — <one line why>`.
2. Stop digging the same hole.
3. Mark the failed phase `superseded`; a local or merely messy plan belongs to L1 instead.
4. Decide which tests still express a stable goal-level contract and which encode the failed path; keep, rewrite, discard, or revert them with the implementation disposition.
5. Update goal.md outcomes/order if the roadmap changes; keep Intent/Success stable.
6. Allocate the next unused integer for the replacement phase, create its file, and apply Start state changes without a nested commit.
7. Append journal: evidence → path change → test / code disposition → next focus.
8. Commit the goal / phase / journal edits once: `docs(helm): L2 reshape`.
9. Resume from the new active phase only.

### L3 — Steer (destination)

1. Tell the user: `L3 steer — <one line why>`.
2. **Freeze** — no more feature work until goal is revised.
3. Create `journal.md` if needed; capture evidence (what we learned; links to reports/logs).
4. **Revise `goal.md` in place** — Intent / Success / Non-goals / Constraints / Phases. Set `status: active` (or `proposed` if user wants to re-confirm), bump `updated`.
5. **Re-phase from reality** — keep still-valuable `done` work; supersede dead phases; allocate the next unused integer for each new phase. If the new direction changes term meanings or reverses decisions, update CONTEXT.md / supersede ADRs (domain-modeling conventions) in the same turn.
6. **Dispose code and tests** — journal what to keep, rewrite, discard, or revert; an old test may encode a destination that is no longer valid.
7. Write the fresh plan for the new current phase and apply Start state changes without a nested commit.
8. Commit the revised goal, plan, journal, and any CONTEXT.md / ADR changes once: `docs(helm): L3 steer`.
9. Resume execution.

## Revisit completed work

Use this when later evidence challenges a phase already marked `done`.

1. Classify first: if Intent or Success criteria changed, use L3; otherwise continue here.
2. Preserve the completed phase file and ID. Allocate the next unused integer `PM` and write a new phase for the investigation or correction.
3. Decide the old phase status from evidence:
   - keep `done` when its original accepted outcome remains valid and `PM` is incremental follow-up;
   - change it to `superseded` when the accepted outcome or approach is no longer trustworthy.
4. Trace dependency impact through later phases. Keep later phases `done` when their outcomes remain valid; mark only invalidated phases `superseded`. Add replacement phases under further unused integers rather than reopening old files.
5. Decide which implementation and tests to keep, rewrite, discard, or revert. Do not assume every dependent artifact is invalid.
6. Append journal: new evidence → old acceptance → affected phase IDs and dependency assessment → code/test disposition → next focus.
7. Apply Start state changes to `PM` without a nested commit. Bump metadata on every edited artifact.
8. Commit the complete revisit once: `docs(helm): revisit PN via PM`.
9. Resume only from the new active phase.

## Metadata updates

For every goal.md or phase-file transition above:

1. Preserve `created`.
2. Set `updated` to a timezone-aware ISO 8601 timestamp (`YYYY-MM-DDTHH:MM:SS±HH:MM`, or `Z`).
3. Increment that file's integer `revision` once for the entire outer transition, even when it contains nested state changes.
4. Before writing, re-read owner, status, revision, and the relevant Git diff. If they changed, reconcile instead of overwriting newer state.

## Handoff (owner change)

- An initiative has one owner and at most one active phase. A handoff transfers the whole initiative; it does not create parallel phase owners.
- Owner change = journal entry (result + next step) + `owner` line update in the same edit turn; commit it once: `docs(helm): handoff to <owner>`.
- Resuming after a handoff: read goal.md + the active phase file + recent journal; restate focus; continue.
