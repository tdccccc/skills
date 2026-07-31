# Helm Reference — transitions & steer mechanics

Read this file when executing a **phase transition** or an **L1/L2/L3 steer**, after classifying in SKILL.md. It holds the mechanical steps only — the classification logic lives in SKILL.md.

Status edits happen in the **goal.md phase index only** (single source of truth); phase files carry no status field.

## Phase transitions

### Start phase `PN`

1. Ensure `phases/NN-<slug>.md` exists (create from template if needed).
2. Set the goal.md index line for `PN` to `status: active`; set `owner` to the current session/agent.
3. Any previously `active` line → `done` (if completed) or `blocked` / `pending` as appropriate — never two `active` lines.

### Complete phase `PN`

1. Index line `PN` → `done`.
2. Choose next phase (or Close if none).
3. If next exists → **Start** it (or leave it `pending` and pause if the user stops here).

### Block phase `PN`

1. Index line → `blocked`; journal one line: what blocks it.
2. Either switch the `active` line to another phase, or pause the initiative.

### Supersede phase `PN`

1. Index line → `superseded` (or replace that slot’s outcome if re-cutting the roadmap).
2. Create a new phase file for the replacement path (`02-…` or `01-b-…` if redoing the same slot’s intent under a new approach).
3. Prefer **new file + superseded old** when outcome or approach failed; in-place rewrite only for small corrections that keep the same outcome (L1-scale).

## Steer action lists

### L1 — Adjust (local)

1. Edit the current phase plan tasks / approach in place (same outcome).
2. On first journal-worthy event, create `journal.md` if missing; append from `templates/journal-entry.md` (optional one-liner for tiny L1).
3. Continue executing.

### L2 — Reshape (path)

1. Tell the user: `L2 reshape — <one line why>`.
2. Stop digging the same hole.
3. Mark the failed phase **superseded** (default). In-place rewrite only if the outcome stays the same and the plan was merely messy.
4. Update goal.md index outcomes/order if the roadmap changes; keep Intent/Success stable.
5. **Start** the new current phase (see transitions).
6. Append journal: evidence → path change → next focus.
7. Resume from the new active phase only.

### L3 — Steer (destination)

1. Tell the user: `L3 steer — <one line why>`.
2. **Freeze** — no more feature work until goal is revised.
3. Create `journal.md` if needed; capture evidence (what we learned; links to reports/logs).
4. **Revise `goal.md` in place** — Intent / Success / Non-goals / Constraints / Phases. Set `status: active` (or `proposed` if user wants to re-confirm), bump `updated`.
5. **Re-phase from reality** — keep still-valuable `done` work; supersede dead phases; mark a new `active` index line. If the new direction changes term meanings or reverses decisions, update CONTEXT.md / supersede ADRs (domain-modeling conventions) in the same turn.
6. **Dispose code** — journal what to keep vs discard/revert.
7. Write/start a fresh plan for the new active phase.
8. Resume execution.

## Handoff (parallel agents)

- Owner change = journal entry (result + next step) + `owner` line update in the same edit turn.
- Resuming after a handoff: read goal.md + the active phase file + recent journal; restate focus; continue.
- Never double-write the same phase — parallel agents work **different** phases.
