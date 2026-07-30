---
name: helm
description: 'Personal intent workflow: lock a goal, plan one phase at a time, execute with checkpoints, and steer (change plan or goal) when reality diverges. Use when starting or continuing a multi-step feature, refactor, migration, or initiative; when the user wants to plan then execute; or mentions helm, goal.md, re-steer, phase plan, or "先定目标再做". Not for one-line fixes or pure brainstorming with no intent to execute soon.'
install-targets: claude
---

# Helm

Steer work from intent → path → execution, with mid-course correction as a first-class action.

Metaphor: **goal is the destination, phase plan is the current heading, journal is the logbook.**

Default path is **in-session execution**. tocodex is optional and only for well-scoped delegated slices.

## Artifacts

```text
docs/helm/<initiative-id>/
  goal.md                 # Intent, success criteria, phase index (keep thin)
  research.md             # Optional dirty notes from intake
  journal.md              # Append-only steer / decision log (create on first entry)
  phases/
    01-<slug>.md          # Detailed plan for one phase
    02-<slug>.md
```

`<initiative-id>`: `YYYY-MM-DD-short-english-slug` (lowercase kebab-case, no spaces).

**Phase numbering:** filename `NN-<slug>.md` ↔ title `PN` ↔ goal.md phase line `PN`. Keep them aligned (e.g. `01-auth-api.md` = P1).

Create files lazily. Do not pre-create every phase file.

### Templates

Templates live next to this `SKILL.md`:

- `templates/goal.md`
- `templates/phase.md`
- `templates/journal-entry.md`

Resolve paths relative to **this skill’s install directory** (the directory containing this `SKILL.md`, e.g. `~/.claude/skills/helm/` after install). If templates are unreadable, use the field lists in this skill as fallback — do not invent a parallel scheme.

---

## Resume (do this first)

Before creating a new initiative:

1. Scan `docs/helm/*/goal.md` for `status: active` (or a still-open `proposed` the user is clearly continuing).
2. If one matches the user’s request, **resume it**: read `goal.md`, the current phase file, and recent `journal.md` entries.
3. Restate **current focus** and **next concrete step**, then continue (plan / execute / steer).
4. Only create a new `<initiative-id>` when this is genuinely new work, or the user asks for a fresh initiative.

---

## Workflow

```
Resume? → Intake → Frame goal.md → Plan current phase only → Execute → Checkpoint
                       ↑                                           │
                       └──────── Steer L1 / L2 / L3 ←──────────────┘
```

### 0. Intake

Clarify enough to write a goal. Explore the repo when facts live in code. Optional: dump raw notes into `research.md` (disposable; promote only what belongs into goal fields).

Skip formal intake when the work is already well-scoped; go to Frame or Resume.

### 1. Frame — write `goal.md`

Copy from `templates/goal.md`. Keep it **thin**:

- Intent (1–2 sentences)
- Success criteria (checkable)
- Non-goals
- Constraints (hard limits)
- Phase index: **outcomes only**, no steps
- Current focus (`PN`)
- Open questions (optional; resolve by editing goal/phase and removing the item)

Phases in goal.md are titles + outcomes + **mirrored** status. Detailed steps never belong here.

After writing, briefly confirm with the user if the initiative is large or irreversible. For small personal work, writing `goal.md` and setting `status: active` is enough.

### 2. Plan — write only the current phase

Create or update `phases/NN-<slug>.md` from `templates/phase.md`.

Rules:

- **Only detail the current focus phase.** Later phases stay as titles in goal.md until activated.
- One phase = one checkable outcome, small enough to discard or rework without grief.
- Include **Assumptions** and **Abort / reshape triggers**.
- Prefer ≤ 7 concrete tasks. If more, split phases.
- When the phase becomes the working phase, run **Phase start** (below) so goal index and phase file stay in sync.

### 3. Execute

Work the phase task list in this session by default.

After each meaningful chunk (or each delegated report), run a **Checkpoint**. Do not wait until the whole phase ends if something smells wrong.

### 4. Checkpoint

Silently classify, then act:

1. Do the **goal success criteria** still describe what we should optimize for?
2. Is the **current phase outcome** still the right next destination?
3. Did this chunk move us toward that outcome, or only produce motion?

| Result | Action |
|--------|--------|
| On track | Continue / check off tasks |
| Path wrong, goal still right | **L1** or **L2** (see Steer) |
| Goal / success criteria wrong | **L3** — stop implementation first |

**Surface to the user** a one-line classification before rewriting files on **L2 or L3** (and when unsure). L1 may stay silent if the fix is obvious and local.

### 5. Close

- **Done:** all success criteria checked, **or** explicitly waived in `journal.md` (name which criterion and why). Set goal `status: done`.
- **Abandoned:** set `status: abandoned` + one journal entry with why. Do not fake completion.

---

## Status lifecycle

**goal.md `status`:**

| Value | Meaning |
|-------|---------|
| `proposed` | Drafted, not yet the working initiative |
| `active` | Current working initiative (normal state while doing work) |
| `done` | Success criteria met or waived |
| `abandoned` | Stopped on purpose |

**Do not leave goal status stuck on a steer event.** L3 is recorded in `journal.md`. After revising the goal and resuming work, goal status is **`active`** again (unless closing as done/abandoned).

Optional one-line note under Intent or in journal is enough history; no `status: steered` field.

**phase `status`:** `pending` | `active` | `done` | `blocked` | `superseded`

**Dual status rule:** the phase file is authoritative for detail; the goal.md phase index **mirrors** the same status for that `PN`. **Whenever phase status or current focus changes, update both files in the same edit turn.**

Only one phase should be `active` at a time.

---

## Phase transitions

Apply these whenever focus moves. Always sync **goal.md** (Phases list + Current focus + `updated`) **and** the phase file.

### Start phase `PN`

1. Ensure `phases/NN-<slug>.md` exists (create from template if needed).
2. Set that phase file `status: active`.
3. Set goal index line for `PN` to `active`; set **Current focus** to `PN`.
4. Any previously `active` phase → `done` (if completed) or leave `blocked`/`pending` as appropriate — never two `active`.

### Complete phase `PN`

1. Phase file → `status: done`; goal index → `done`.
2. Choose next phase (or Close if none).
3. If next exists → **Start** it (or leave next `pending` and set Current focus only if user pauses).

### Block phase `PN`

1. External dependency or wait → phase + goal index `blocked`.
2. Journal one line: what blocks it.
3. Either switch Current focus to another phase, or pause the initiative.

### Supersede phase `PN`

1. Phase file → `status: superseded` (keep the file).
2. Goal index → `superseded` (or replace that slot with a new `PN` outcome if re-cutting the roadmap).
3. Add a new phase file when the replacement path needs its own plan (`02-…` or `01-b-…` if redoing the same slot’s intent under a new approach). Prefer **new file + superseded old** when outcome or approach failed; in-place rewrite only for small corrections that keep the same outcome (L1-scale).

---

## Steer protocol

When execution disappoints or priorities shift, **classify before rewriting everything**.

### L1 — Adjust (local)

**Signal:** steps, APIs, file choices, or ordering are wrong; phase outcome and goal still hold.

**Do:**

1. Edit the current phase plan tasks / approach in place (same outcome).
2. On first journal-worthy event, create `journal.md` if missing; append from `templates/journal-entry.md` (optional one-liner for tiny L1).
3. Continue executing.

### L2 — Reshape (path)

**Signal:** phase outcome is wrong or the approach failed, but Intent + Success criteria still hold.

**Do:**

1. Tell the user: `L2 reshape — <one line why>`.
2. Stop digging the same hole.
3. Mark the failed phase **superseded** (default). In-place rewrite only if the outcome stays the same and the plan was merely messy.
4. Update goal.md phase index outcomes/order if the roadmap changes; keep Intent/Success stable.
5. **Start** the new current phase plan.
6. Append journal: evidence → path change → next focus.
7. Resume from the new current focus only.

### L3 — Steer (destination)

**Signal:** success criteria, non-goals, or core intent no longer match reality / user desire.

**Do:**

1. Tell the user: `L3 steer — <one line why>`.
2. **Freeze** — no more feature work until goal is revised.
3. Create `journal.md` if needed; capture evidence (what we learned; links to reports/logs).
4. **Revise `goal.md` in place** — Intent / Success / Non-goals / Constraints / Phases. Set `status: active` (or `proposed` if user wants to re-confirm), bump `updated`.
5. **Re-phase from reality** — keep still-valuable `done` work; supersede dead phases; set a new Current focus.
6. **Dispose code** — journal what to keep vs discard/revert.
7. Write/start a fresh plan for the new current phase.
8. Resume execution.

Personal rule: **in-place goal + append-only journal**, not version forests (`goal-v2.md`), unless the user asks for snapshots.

### Decision tree

```
Something feels wrong
  → Still the right success criteria?
       no  → L3 steer
       yes → Still the right phase outcome / approach?
                no  → L2 reshape
                yes → L1 adjust
  → Unsure? Smallest check (read code, spike, reproduce), then classify.
  → L2/L3: say the classification to the user before editing files.
```

Never “finish the wrong plan first.” Wrong goal work compounds.

### Journal bootstrap

- Create `journal.md` on the first L2, L3, abandonment, success-criteria waiver, or any decision you would regret losing.
- Each entry: copy structure from `templates/journal-entry.md` and append (never rewrite old entries).

---

## Phase sizing

A good phase:

- States one outcome in one sentence
- Has verification you can actually run or inspect
- Is cheap enough to throw away (rough guide: hours, not weeks)
- Names abort triggers for its riskiest assumptions

A bad phase: “implement the whole feature + tests + docs + refactor.”

---

## Optional: tocodex

Helm does **not** require tocodex. Use it only when a phase task is well-scoped and you deliberately delegate to Codex.

1. Goal + current phase plan must exist.
2. **Always** put execution artifacts under `docs/tocodex/<task-id>/` (task.md, report.md, logs). Do not invent a second tree under `docs/helm/.../runs/`.
3. Codex only sees what you put in the task contract: in task.md **Context**, link the initiative `goal.md` and current phase file (repo-relative paths).
4. Optionally note the tocodex task id in `journal.md` or the phase file for traceability.
5. On report return, run Checkpoint before the next task.
6. If Checkpoint says L3, revise goal **before** any new tocodex task.

Helm owns intent; tocodex owns one-shot execution contracts.

---

## When NOT to use Helm

- Single-file / few-line fix with obvious success
- Pure brainstorming with no intent to execute soon (short scoping chat is fine if the next step is Frame)
- User explicitly wants freeform chat only
- Emergency hotfix where process cost exceeds risk (if an initiative already exists, journal the exception)

---

## Mini example

```text
docs/helm/2026-07-18-billing-webhooks/
  goal.md          # Intent: reliable Stripe webhooks; Success: retry + idempotency checks
  phases/
    01-verify-stubs.md   # P1 active — prove event types against current API
  journal.md       # (after L2) superseded pure-mock approach; next P1b contract tests
```

goal phase line: `1. P1 — verify webhook stubs against live event types — status: active`  
phase file: `01-verify-stubs.md` with `status: active` and matching Outcome.

---

## Agent habits

- Prefer editing existing helm files over inventing new doc schemes.
- Resume active initiatives before creating new ones.
- When changing phase status or focus, update **goal.md and phase file together**.
- After any L2/L3, restate **current focus** and **next concrete step** to the user.
- Do not expand goal.md into a novel; push detail into the active phase plan.
- Do not write detailed plans for future phases “just in case.”
- When the user changes their mind mid-flight, classify L1/L2/L3 and update files — don’t only agree in chat.
