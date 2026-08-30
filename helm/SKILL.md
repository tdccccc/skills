---
name: helm
description: 'Personal intent workflow: lock a goal, plan one phase at a time, execute with checkpoints, and steer (change plan or goal) when reality diverges. Use when starting or continuing a multi-step feature, refactor, migration, or initiative; when the user wants to plan then execute; or mentions helm, goal.md, re-steer, phase plan, or "先定目标再做". Not for one-line fixes or pure brainstorming with no intent to execute soon.'
install-targets: claude
---

# Helm

Steer work from intent → path → execution, with mid-course correction as a first-class action.

Metaphor: **goal is the destination, phase plan is the current heading, journal is the logbook.**

Default path is **in-session execution**; independent chunks inside the active phase may be delegated to subagents while the main session remains owner.

## Artifacts

```text
docs/helm/<initiative-id>/
  goal.md                 # Intent, success criteria, phase index — the ONLY status holder
  research.md             # Optional disposable intake notes (decisions belong in journal, not here)
  journal.md              # Append-only steer / handoff / decision log (create on first entry)
  phases/
    01-<slug>.md          # Detail for one phase: outcome, approach, tasks, verification
```

`<initiative-id>`: `YYYY-MM-DD-short-english-slug` (lowercase kebab-case, no spaces). Keep the date human-readable; do not add hours or minutes by default. If the candidate ID already exists: first decide whether to Resume or revisit it; if the work is genuinely separate, prefer a more specific semantic slug; only when no useful distinction exists append `-02`, `-03`, and so on. Never use a timestamp suffix merely to bypass Resume.

**Phase numbering:** filename `NN-<slug>.md` ↔ title `PN` ↔ goal.md index line `PN`. Keep them aligned (e.g. `01-auth-api.md` = P1). Phase numbers are permanent and monotonic: never reuse a number or add letter suffixes. When a phase is superseded, its replacement takes the next unused integer (for example, superseded P1 is followed by replacement P3 when P2 already exists). New evidence about completed work also creates a new phase under the next unused integer; never reopen or rewrite the old phase plan as if history had not happened.

**Artifact metadata:** goal and phase files record `created` and `updated` as timezone-aware ISO 8601 timestamps (`YYYY-MM-DDTHH:MM:SS±HH:MM`, or `Z`) plus an integer `revision`. Start at `revision: 1`. Whenever an artifact is edited, preserve `created`, set `updated` to the actual edit time, and increment that artifact's revision once for the whole logical edit. These fields are staleness hints; before writing, still re-read owner, status, revision, and the relevant Git diff.

Create files lazily. Do not pre-create every phase file.

### Templates

Templates live next to this `SKILL.md`:

- `templates/goal.md`
- `templates/phase.md`
- `templates/journal-entry.md`
- `templates/intake-prompt.md` — copy-paste delegation prompt for read-only intake recon (a prompt template, not a doc template)

Resolve paths relative to **this skill’s install directory** (the directory containing this `SKILL.md`). If templates are unreadable, use the field lists in this skill as fallback — do not invent a parallel scheme.

---

## Resume (do this first)

Before creating a new initiative:

1. **Scan status lines first, not whole files**: `grep -H "^status:" docs/helm/*/goal.md` (or list the dirs and read the status line only). Full-read only candidates: `status: active`, or a still-open `proposed` the user is clearly continuing. If nothing is active/proposed, stop scanning — no need to read every goal.md to confirm.
2. If one matches the user’s request, **resume it**: read goal.md, the current phase file (the `active` index line, if any), and recent journal.md entries (last ~5 unless hunting a specific decision).
3. Restate **current focus** and **next concrete step**, then continue (plan / execute / steer).
4. Only create a new `<initiative-id>` when this is genuinely new work, or the user asks for a fresh initiative. If its date + slug already exists, follow the ID collision rule above rather than adding a clock time.

**Concurrency check:** if goal.md `owner` names a different session/agent than you, read the journal first — if the latest entry is a handoff or the work has clearly paused, take over and update `owner`; if another agent appears mid-phase, do not edit anything; tell the user. Before any Helm artifact edit, re-read its `revision` and relevant status/owner lines; if they changed since planning the edit, stop and reconcile instead of overwriting newer state.

---

## Workflow

```
Resume? → Intake → Frame goal.md → Plan current phase only → Execute → Checkpoint
                       ↑                                           │
                       └────────── Steer L1 / L2 / L3 ←────────────┘
```

### 0. Intake

Clarify enough to write a goal. Explore the repo when facts live in code. Optional: dump raw notes into `research.md` (disposable; promote only what belongs into goal fields).

**Language alignment:** read the project's root `CONTEXT.md` (or `CONTEXT-MAP.md`) before framing — essential when starting a new project or taking over an unfamiliar one. Use its vocabulary in goal.md; on conflict, resolve the term before the goal. When intake pins a new term, write it back to CONTEXT.md (create lazily if missing; format per `domain-modeling`) — the goal inherits the project's language, it does not define it.

**Design gate:** if the goal or big framework isn't settled — or the user wants the design stress-tested — run `grill-with-docs` first (design phase); its outputs (CONTEXT.md, docs/adr/) are the project assets helm consumes. Helm starts once the direction is locked. A mid-execution “grill me” means: pause, grill the current plan, land conclusions in the phase file / journal, then resume.

Skip formal intake when the work is already well-scoped; go to Frame or Resume.

### 1. Frame — write `goal.md`

Copy from `templates/goal.md`. Keep it **thin**:

- Intent (1–2 sentences)
- Success criteria (checkable)
- Non-goals
- Constraints (hard limits)
- Phase index: **outcomes only**, no steps — each line carries its `status`
- Open questions (optional; resolve by editing goal/phase and removing the item)

Phases in goal.md are titles + outcomes + **status**. Detailed steps never belong here.

After writing, briefly confirm with the user if the initiative is large or irreversible. For small personal work, writing `goal.md` and setting `status: active` is enough.

### 2. Plan — write only the current phase

Create or update `phases/NN-<slug>.md` from `templates/phase.md`.

Rules:

- **Only detail the current focus phase.** Later phases stay as index lines in goal.md until activated.
- One phase = one checkable outcome, small enough to discard or rework without grief (hours, not weeks).
- Include **Assumptions** and **Abort / reshape triggers**.
- Prefer ≤ 7 concrete tasks. If more, split phases.
- Make task boundaries and verification concrete enough that the owner can isolate and accept one meaningful implementation chunk at a time.
- For every chunk that changes code, tests, or executable configuration, record its **change kind**, **test strategy**, **expected Red or Green baseline**, and **Green and regression checks**. Record a justified exception and compensating verification when test-first is not feasible.
- Tests belong inside each behavioral chunk; never defer them to a horizontal testing task at the end of the phase.
- A bad phase: “implement the whole feature + tests + docs + refactor.”
- When the phase becomes the working phase, mark its index line `active` (see REFERENCE.md).

### 3. Execute

Work the phase task list in this session by default. Every change to code, tests, or executable configuration also follows **`code-change-discipline`**; that skill owns the baseline strategy while Helm owns phase state, acceptance, and commit points.

For a feature or bug-fix chunk, observe the expected Red before touching production logic, make the minimum production change, observe Green, refactor while staying Green, then run relevant regression checks. For a behavior-preserving refactor or optimization, follow its planned Green baseline or measurement strategy instead of manufacturing Red.

An expected Red is unaccepted work: do not accept it, check off its task, or commit it. After each Green candidate chunk (or each delegated report), run a **Checkpoint**. A delegated report claiming “done” is not acceptance — the report must carry verification evidence, and the Checkpoint decides. Do not wait until the whole phase ends if something smells wrong.

### 4. Checkpoint

Silently classify, then act:

1. Do the **goal success criteria** still describe what we should optimize for?
2. Is the **current phase outcome** still the right next destination?
3. Did this chunk move us toward that outcome, or only produce motion?

| Result | Action |
|--------|--------|
| On track | Accept only with observed verification evidence, then continue / check off tasks |
| Path wrong, goal still right | **L1** or **L2** (see Steer) |
| Goal / success criteria wrong | **L3** — stop implementation first |

A chunk is **accepted** only when its required verification has an observed result, the Checkpoint is On track, and the owner accepts the isolated change as serving the phase outcome. Evidence must match the planned strategy: behavior changes and bug fixes carry observed **Red and Green evidence** plus relevant regressions; behavior-preserving refactors carry **before-and-after Green evidence**; optimizations carry **correctness and baseline/result evidence**. State **checks not run**, test-first exceptions, and compensating verification explicitly; missing required evidence blocks acceptance. For L2/L3, decide what code and tests to keep, rewrite, discard, or revert first; only retained work can be re-accepted under the current phase context.

**Git sync — commit points:** commits are the default way Helm keeps accepted work small, recoverable, and separated from unrelated changes. Once a chunk is accepted, commit its **isolated change** — only that chunk's implementation and tests, never mixed working-tree edits — then check it off. Phase transitions, steers (L1/L2/L3), journal entries, and Close each end with one commit of the artifacts they touched (goal.md, phase files, journal.md); the mechanical steps are in REFERENCE.md. Commit messages name the chunk or transition, e.g. `feat(login): password strength meter` or `docs(helm): P2 done`. Treat invoking Helm for an initiative as approval for these scoped checkpoint commits unless the user or a higher-priority execution policy says otherwise. Respect an explicit preference to skip commits. If commits are unavailable or disallowed, keep the same acceptance boundaries, report that the checkpoint remains uncommitted, and avoid accumulating unrelated changes.

**Surface to the user** a one-line classification before rewriting files on **L2 or L3** (and when unsure). L1 may stay silent if the fix is obvious and local.

### 5. Close

- **Done:** first confirm every success criterion is checked or explicitly waived in `journal.md` (name which criterion and why). Then set goal `status: done` and commit the closing state (`docs(helm): <slug> done`).
- **Abandoned:** set `status: abandoned` + one journal entry with why, then commit. Do not fake completion.

---

## Status & concurrency

**Status lives in goal.md only.** The phase index line’s `status` is the single source of truth; phase files carry **no status field**. The single `active` line IS the current focus — there is no separate field to keep in sync.

**goal.md `status`:**

| Value | Meaning |
|-------|---------|
| `proposed` | Drafted, not yet the working initiative |
| `active` | Current working initiative (normal state while doing work) |
| `done` | Success criteria met or waived |
| `abandoned` | Stopped on purpose |

**Phase `status` values (in the goal.md index only):** `pending` | `active` | `done` | `blocked` | `superseded`. Never two `active` lines. After an L3 revision the goal is `active` again (unless closing); history stays in journal.md — no `status: steered` field.

**Parallel agents:**

- One `owner` per initiative (a session/agent id) in goal.md. Only the owner changes goal.md status / owner lines. **Delegates (subagents) are never owners**: read-only on goal.md and journal.md. They may write only the implementation artifacts assigned by the contract; final phase task check-off and every `status` transition belong to the owner after acceptance.
- An initiative has one owner and at most one active phase. Do not advance different phases in parallel. Parallelism is limited to independent implementation chunks inside the active phase, coordinated and accepted by the same owner. If work truly needs independently owned phases, split it into separate initiatives.
- Handoff = one journal entry (result + next step) + `owner` change, in the same edit turn.
- Keep goal.md edits small and directional (a status or owner line) — never full rewrites.
- `created`, `updated`, and `revision` on goal.md and phase files help a new session detect stale context. They do not replace re-reading owner/status/revision and the relevant Git diff before writing.

---

## Steer

When execution disappoints or priorities shift, **classify before rewriting everything**. The mechanical steps for transitions and each level live in **`REFERENCE.md`** — read it before executing them.

**L1 — Adjust (local):** the phase outcome and goal still hold; steps, APIs, file choices, test seams, ordering, or a merely messy plan need correction. Edit the phase plan in place, keep executing.

**L2 — Reshape (path):** the phase outcome is wrong or its approach has genuinely failed, but Intent + Success criteria still hold. Tell the user `L2 reshape — <one line why>`, stop digging, supersede the phase, create a replacement under the next unused integer, and decide which tests still express a stable contract versus the failed path.

**L3 — Steer (destination):** success criteria, non-goals, or core intent no longer match reality. Tell the user `L3 steer — <one line why>`, **freeze** feature work, revise goal.md in place, re-phase, journal evidence, and explicitly keep, rewrite, discard, or revert tests together with implementation before resuming.

### Revisit completed work

When new evidence challenges a completed phase, preserve its file and ID and create a new phase under the next unused integer. The new phase represents the later investigation or correction; phase numbers record execution history, not component hierarchy.

- Keep the old phase `done` when its accepted outcome was valid and the new phase is incremental follow-up caused by later evidence or requirements.
- Change the old phase to `superseded` when new evidence invalidates its accepted outcome or approach. The journal preserves that it was previously accepted and explains why the conclusion changed.
- Re-evaluate every later phase whose acceptance depended on the challenged result. Keep trustworthy phases `done`; mark only invalidated outcomes `superseded`, then add any needed replacement phases using new integers.
- If the evidence changes Intent or Success criteria, classify L3 instead of treating it as ordinary rework.
- Append a journal entry with the evidence, affected phases, dependency assessment, code/test disposition, and next focus. Apply the mechanics in REFERENCE.md.

An expected Red is evidence that the planned behavior is still missing, not a steer signal by itself. Classify only when the failure challenges the test path, phase outcome, or goal.

**Asset maintenance:** steering changes only what must change. L1 never touches CONTEXT.md or ADRs; L2 touches them only if the failure exposed a terminology error or reversed a decision. L3: if the new direction changes a term's meaning or reverses a decision, update CONTEXT.md / supersede the ADR in the same edit turn (format per `domain-modeling`) and link the changes from the journal entry.

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

Never “finish the wrong plan first.” Wrong-goal work compounds.

Personal rule: **in-place goal + append-only journal**, not version forests (`goal-v2.md`), unless the user asks for snapshots.

### Journal bootstrap

- Create `journal.md` on the first L2, L3, abandonment, success-criteria waiver, or any decision you would regret losing.
- Each entry: copy structure from `templates/journal-entry.md` and append (never rewrite old entries). Commit the entry together with the steer's goal/phase edits (see Git sync).

---

## Delegation (subagents)

Execution stays in this session by default; independent chunks inside the active phase may be delegated to subagents. Delegates are never owners (see Status & concurrency): state in the contract what to read (goal.md, the phase file, recent journal entries, CONTEXT.md if present) and that goal.md / journal.md are read-only. For executable changes, include that chunk's planned **test strategy**, **target test**, **expected Red or Green baseline**, Green and regression commands, and any approved exception. Their execution report must return the candidate change scope, isolated diff / exact changed paths, **observed Red, Green, and regression results** as applicable, **checks not run**, and relevant phase context. If the expected evidence cannot be obtained, the delegate stops and reports why rather than bypassing the strategy. On report return, run a Checkpoint; “done” is not acceptance. Final task check-off and commits are the owner's acts — delegates never commit.

**Intake recon (read-only research):** when intake needs heavy repo exploration, delegate it instead of reading everything in-session. Compose the contract from `templates/intake-prompt.md`. Key rules: status lines via grep before full goal.md reads; code verification scoped to what the near-term phase will plausibly touch (file:line only for a few anchor points); unknown answers are valid output; report comes back concise — the main session may dump it into `research.md` for reuse when planning.

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
  goal.md          # Intent: reliable Stripe webhooks; owner: sess-abc
  phases/
    01-verify-stubs.md   # detail for P1 only — no status field
  journal.md       # (after L2) superseded P1 pure-mock approach; replacement P2 uses contract tests
```

goal index line: `1. P1 — verify webhook stubs against live event types — status: active`

---

## Agent habits

- Prefer editing existing helm files over inventing new doc schemes.
- Resume active initiatives before creating new ones; check `owner` before editing.
- Status changes touch **only** the goal.md index line — never invent parallel state fields.
- Commit every accepted chunk's isolated change and every artifact transition — accepted work does not sit uncommitted.
- After any L2/L3, restate **current focus** and **next concrete step** to the user.
- Do not expand goal.md into a novel; push detail into the active phase plan.
- When the user changes their mind mid-flight, classify L1/L2/L3 and update files — don’t only agree in chat.
