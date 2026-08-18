---
name: helm
description: 'Personal intent workflow: lock a goal, plan one phase at a time, execute with checkpoints, and steer (change plan or goal) when reality diverges. Use when starting or continuing a multi-step feature, refactor, migration, or initiative; when the user wants to plan then execute; or mentions helm, goal.md, re-steer, phase plan, or "先定目标再做". Not for one-line fixes or pure brainstorming with no intent to execute soon.'
install-targets: claude
---

# Helm

Steer work from intent → path → execution, with mid-course correction as a first-class action.

Metaphor: **goal is the destination, phase plan is the current heading, journal is the logbook.**

Default path is **in-session execution**; a well-scoped phase may be delegated to a subagent.

## Artifacts

```text
docs/helm/<initiative-id>/
  goal.md                 # Intent, success criteria, phase index — the ONLY status holder
  research.md             # Optional disposable intake notes (decisions belong in journal, not here)
  journal.md              # Append-only steer / handoff / decision log (create on first entry)
  phases/
    01-<slug>.md          # Detail for one phase: outcome, approach, tasks, verification
```

`<initiative-id>`: `YYYY-MM-DD-short-english-slug` (lowercase kebab-case, no spaces).

**Phase numbering:** filename `NN-<slug>.md` ↔ title `PN` ↔ goal.md index line `PN`. Keep them aligned (e.g. `01-auth-api.md` = P1). A superseded slot redone under a new approach uses `01-b-<slug>.md`.

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
4. Only create a new `<initiative-id>` when this is genuinely new work, or the user asks for a fresh initiative.

**Concurrency check:** if goal.md `owner` names a different session/agent than you, read the journal first — if the latest entry is a handoff or the work has clearly paused, take over and update `owner`; if another agent appears mid-phase, do not edit anything; tell the user.

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

**Technical-report orientation:** if the project has an established technical report, first understand the initiative scope, then consult only its compact overview / section index and sections relevant to that scope. Do not load a long report in full by default; expand only when the work genuinely crosses the whole system. The report is orientation, not implementation truth — verify material facts against source code and executable configuration. Helm neither audits nor edits the report during Intake.

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
- Do not add report-impact guesses, report edits, or a parallel report-status field to the phase plan; synchronization is a post-acceptance handoff.
- When the phase becomes the working phase, mark its index line `active` (see REFERENCE.md).

### 3. Execute

Work the phase task list in this session by default. Every change to code, tests, or executable configuration also follows **`code-change-discipline`**; that skill owns the baseline strategy while Helm owns phase state, acceptance, reporting handoff, and commit points.

For a feature or bug-fix chunk, observe the expected Red before touching production logic, make the minimum production change, observe Green, refactor while staying Green, then run relevant regression checks. For a behavior-preserving refactor or optimization, follow its planned Green baseline or measurement strategy instead of manufacturing Red.

An expected Red is unaccepted work: do not accept it, invoke `technical-report`, check off its task, or commit it. After each Green candidate chunk (or each delegated report), run a **Checkpoint**. A delegated report claiming “done” is not acceptance — the report must carry verification evidence, and the Checkpoint decides. Do not wait until the whole phase ends if something smells wrong.

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

A chunk is **accepted** only when its required verification has an observed result, the Checkpoint is On track, and the owner accepts the isolated change as serving the phase outcome. Evidence must match the planned strategy: behavior changes and bug fixes carry observed **Red and Green evidence** plus relevant regressions; behavior-preserving refactors carry **before-and-after Green evidence**; optimizations carry **correctness and baseline/result evidence**. State **checks not run**, test-first exceptions, and compensating verification explicitly; missing required evidence blocks acceptance. For L2/L3, decide what code and tests to keep, rewrite, discard, or revert first; synchronize only work retained and re-accepted under the current phase context.

**Git sync — commit points:** commits are part of acceptance, not a separate decision. Once a chunk is accepted (and, when enabled, its technical-report handoff reached `updated` or `no-impact`), commit its **isolated change** — only that chunk's implementation and tests, never mixed working-tree edits — then check it off. Phase transitions, steers (L1/L2/L3), journal entries, and Close each end with a commit of the helm artifacts they touched (goal.md, phase files, journal.md); the mechanical steps are in REFERENCE.md. Commit messages name the chunk or transition, e.g. `feat(login): password strength meter` or `docs(helm): P2 done`. Never commit unaccepted mid-flight work, and respect an explicit user preference to skip commits.

**Surface to the user** a one-line classification before rewriting files on **L2 or L3** (and when unsure). L1 may stay silent if the fix is obvious and local.

#### Technical-report handoff

Technical-report maintenance is enabled when the project already has an established report (normally `docs/technical-report.html`) or the user explicitly enabled / requested one. Red, Green, and refactor are internal steps of one candidate chunk and never trigger separate reporting handoffs. After accepting each meaningful implementation chunk, invoke the independent **`technical-report`** skill once before checking off that chunk or completing its phase. If maintenance was explicitly enabled but no report exists yet, invoke its `init` mode for the first handoff, passing the accepted scope as investigation context; later handoffs use `update`.

Give `technical-report` investigation context, not report prose or an impact verdict:

- the accepted change scope, including relevant behavior and explicit exclusions;
- only that chunk's isolated diff or exact changed paths — never an unrelated mixed working-tree diff;
- verification performed, observed results, and anything not run;
- the relevant goal intent, phase outcome, constraints, and the chunk's role.

Helm decides **when** to synchronize. `technical-report` independently investigates the current implementation and decides **whether and how** to synchronize it. Helm must not pre-filter “small” changes, dictate affected sections or conclusions, edit the technical report directly, or turn the user prompt / change rationale / phase history into report content.

Consume the result exactly:

| `technical-report` result | Helm action |
|---------------------------|-------------|
| `updated` | Reporting handoff is satisfied; continue. |
| `no-impact` | Accept the skill's impact judgment without re-deciding it; continue. |
| `blocked` | Surface the blocker; do not substitute a Helm edit or complete the chunk / phase / initiative until resolved and retried. |

A reporting `blocked` result does not mechanically set the Helm phase to `status: blocked` or imply L1/L2/L3. Apply Helm classification only if the underlying evidence changes the path or goal. Do not add a parallel report-status field. Phase completion and Close check that all accepted chunks reached `updated` or `no-impact`; they do not trigger a duplicate whole-report sweep when there is no new accepted diff.

### 5. Close

- **Done:** first confirm every success criterion is checked or explicitly waived in `journal.md` (name which criterion and why). When technical-report maintenance is enabled, also confirm every accepted meaningful chunk completed its handoff with `updated` or `no-impact`; a missing handoff and `blocked` both prevent Close. Then set goal `status: done` and commit the closing state (`docs(helm): <slug> done`).
- Close does not run a speculative final report sweep and Helm never edits the technical report to unblock itself.
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

- One `owner` per initiative (a session/agent id) in goal.md. Only the owner changes goal.md status / owner lines. **Delegates (subagents) are never owners**: read-only on goal.md and journal.md. They may write only the implementation artifacts assigned by the contract; final phase task check-off and every `status` transition belong to the owner after acceptance and any required technical-report handoff.
- Different phases may run in parallel under different owners; **the same phase is never double-written**.
- Handoff = one journal entry (result + next step) + `owner` change, in the same edit turn.
- Keep goal.md edits small and directional (a status or owner line) — never full rewrites.
- `updated:` on goal.md and phase files is the staleness signal when a new session resumes.

---

## Steer

When execution disappoints or priorities shift, **classify before rewriting everything**. The mechanical steps for transitions and each level live in **`REFERENCE.md`** — read it before executing them.

**L1 — Adjust (local):** steps, APIs, file choices, test seams, or ordering are wrong; phase outcome and goal still hold. Edit the phase plan in place, keep executing.

**L2 — Reshape (path):** phase outcome is wrong or the approach failed, but Intent + Success criteria still hold. Tell the user `L2 reshape — <one line why>`, stop digging, re-plan, and decide which tests still express a stable contract versus the failed path.

**L3 — Steer (destination):** success criteria, non-goals, or core intent no longer match reality. Tell the user `L3 steer — <one line why>`, **freeze** feature work, revise goal.md in place, re-phase, journal evidence, and explicitly keep, rewrite, discard, or revert tests together with implementation before resuming.

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

Execution stays in this session by default; a well-scoped phase may be delegated to a subagent. Delegates are never owners (see Status & concurrency): state in the contract what to read (goal.md, the phase file, recent journal entries, CONTEXT.md if present) and that goal.md / journal.md are read-only. For executable changes, include the planned **test strategy**, **target test**, **expected Red or Green baseline**, Green and regression commands, and any approved exception. Their execution report must return the candidate change scope, isolated diff / exact changed paths, **observed Red, Green, and regression results** as applicable, **checks not run**, and relevant phase context. If the expected evidence cannot be obtained, the delegate stops and reports why rather than bypassing the strategy. A normal execution delegate must not judge technical-report impact, invoke `technical-report`, or edit the project's technical report. On report return, run a Checkpoint; “done” is not acceptance (see Checkpoint). When technical-report maintenance is enabled, leave final task check-off to the owner after the accepted chunk's reporting handoff reaches `updated` or `no-impact`; commits are the owner's act — delegates never commit.

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
  journal.md       # (after L2) superseded pure-mock approach; next P1b contract tests
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
