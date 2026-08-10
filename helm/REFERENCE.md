# Helm Reference — transitions & steer mechanics

Read this file when executing a **phase transition** or an **L1/L2/L3 steer**, after classifying in SKILL.md. It holds the mechanical steps only — the classification logic lives in SKILL.md.

Status edits happen in the **goal.md phase index only** (single source of truth); phase files carry no status field.

**Git sync:** every transition and steer below ends with a commit of the helm artifacts it touched (goal.md, phase file, journal.md, and any CONTEXT.md / ADR changes). Accepted implementation chunks are committed at Checkpoint per SKILL.md; this file covers the artifact commits only. Commit messages name the transition, e.g. `docs(helm): start P3`, `docs(helm): journal L2`.

## Phase transitions

### Start phase `PN`

1. Ensure `phases/NN-<slug>.md` exists (create from template if needed).
2. Set the goal.md index line for `PN` to `status: active`; set `owner` to the current session/agent.
3. Any previously `active` line → `done` (if completed) or `blocked` / `pending` as appropriate — never two `active` lines.
4. Commit the goal.md (and new phase file) change: `docs(helm): start PN`.

### Complete phase `PN`

1. Confirm every required phase verification has an observed successful result, including the relevant regression checks and any recorded exception's compensating verification.
2. Confirm every accepted meaningful chunk in `PN` has completed its enabled technical-report handoff with `updated` or `no-impact`.
3. If any handoff is `blocked`, surface and resolve it before transition; Helm does not edit the report or convert the result mechanically into phase `status: blocked`.
4. Index line `PN` → `done`.
5. Choose next phase (or Close if none).
6. If next exists → **Start** it (or leave it `pending` and pause if the user stops here).
7. Commit the goal.md index change: `docs(helm): PN done` (add `, start PN+1` when the next phase starts in the same turn).

Do not run another whole-report sweep merely because the phase is ending when no new accepted diff exists. Do not add report state to goal.md or the phase file. If a reporting blocker causes a cross-session pause, record the blocker and next step with the existing journal mechanics.

### Block phase `PN`

1. Index line → `blocked`; journal one line: what blocks it.
2. Either switch the `active` line to another phase, or pause the initiative.
3. Commit: `docs(helm): block PN`.

### Supersede phase `PN`

1. Index line → `superseded` (or replace that slot’s outcome if re-cutting the roadmap).
2. Create a new phase file for the replacement path (`02-…` or `01-b-…` if redoing the same slot’s intent under a new approach).
3. Prefer **new file + superseded old** when outcome or approach failed; in-place rewrite only for small corrections that keep the same outcome (L1-scale).
4. Commit: `docs(helm): supersede PN`.

## Steer action lists

### L1 — Adjust (local)

1. Edit the current phase plan tasks / approach in place (same outcome).
2. On first journal-worthy event, create `journal.md` if missing; append from `templates/journal-entry.md` (optional one-liner for tiny L1).
3. Commit the phase / journal edits: `docs(helm): L1 adjust PN`.
4. Continue executing.

### L2 — Reshape (path)

1. Tell the user: `L2 reshape — <one line why>`.
2. Stop digging the same hole.
3. Mark the failed phase **superseded** (default). In-place rewrite only if the outcome stays the same and the plan was merely messy.
4. Decide which tests still express a stable goal-level contract and which encode the failed path; keep, rewrite, discard, or revert them with the implementation disposition.
5. Update goal.md index outcomes/order if the roadmap changes; keep Intent/Success stable.
6. **Start** the new current phase (see transitions).
7. Append journal: evidence → path change → test / code disposition → next focus.
8. Commit the goal / phase / journal edits: `docs(helm): L2 reshape`.
9. Resume from the new active phase only.

### L3 — Steer (destination)

1. Tell the user: `L3 steer — <one line why>`.
2. **Freeze** — no more feature work until goal is revised.
3. Create `journal.md` if needed; capture evidence (what we learned; links to reports/logs).
4. **Revise `goal.md` in place** — Intent / Success / Non-goals / Constraints / Phases. Set `status: active` (or `proposed` if user wants to re-confirm), bump `updated`.
5. **Re-phase from reality** — keep still-valuable `done` work; supersede dead phases; mark a new `active` index line. If the new direction changes term meanings or reverses decisions, update CONTEXT.md / supersede ADRs (domain-modeling conventions) in the same turn.
6. **Dispose code and tests** — journal what to keep, rewrite, discard, or revert; an old test may encode a destination that is no longer valid.
7. Write/start a fresh plan for the new active phase and select its test strategy from the revised outcome.
8. Commit the revised goal, plan, journal, and any CONTEXT.md / ADR changes: `docs(helm): L3 steer`.
9. Resume execution.

## Technical-report handoff mechanics

Run this only after the owner has accepted an isolated meaningful implementation chunk at Checkpoint and only when technical-report maintenance is enabled.

1. Assemble the accepted scope and exclusions.
2. Isolate its diff or exact changed paths from unrelated working-tree changes.
3. Include verification commands / checks, observed results, and skipped verification.
4. Include the goal intent, active phase outcome, constraints, and the chunk's role; for L2/L3, include the final keep/discard/revert disposition.
5. Invoke `technical-report` without proposing an impact verdict, target wording, or affected sections.
6. Consume one result:
   - `updated` or `no-impact` → handoff complete; owner may check off the chunk;
   - `blocked` → surface the blocker and retry after resolution; leave the chunk incomplete.

The input locates current implementation; it is not report content. The specialized skill owns implementation investigation, impact assessment, and report edits. It does not own Helm goal, journal, task, or status transitions.

## Handoff (parallel agents)

- Owner change = journal entry (result + next step) + `owner` line update in the same edit turn; commit it in the same turn: `docs(helm): handoff to <owner>`.
- Resuming after a handoff: read goal.md + the active phase file + recent journal; restate focus; continue.
- Never double-write the same phase — parallel agents work **different** phases.
