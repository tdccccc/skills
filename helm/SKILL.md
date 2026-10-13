---
name: helm
description: 'Goal-and-phase workflow for work too long or too uncertain to hold in one sitting: lock a checkable goal, plan only the current phase, accept work on observed evidence, and steer (fix the plan or change the goal) when reality diverges. Use when starting or resuming work that will span sessions or hand off between agents, a migration or broad refactor, or a feature whose path or goal is still uncertain; when the user wants to plan first and then execute; or when they mention helm, goal.md, phase plan, re-steer, or "先定目标再做". Skip well-scoped work that fits one session with obvious success, one-line fixes, and brainstorming with no intent to execute soon.'
install-targets: claude
---

# Helm

Steer work from intent → path → execution, with mid-course correction as a first-class action.

Metaphor: **goal is the destination, the phase plan is the current heading, the journal is the logbook.**

Helm guards against three failures: drifting from the goal, finishing a plan that has stopped making sense, and losing context between sessions. Spend process only where it protects against one of them; everything else is ordinary good engineering that needs no ceremony.

## When to use

Use Helm when at least one holds:

- the work will span sessions or hand off between agents;
- the path or the goal is genuinely uncertain and may change;
- a wrong turn is expensive (migration, broad refactor, multi-component feature).

Do the work directly, without Helm artifacts, for well-scoped changes that fit one session with obvious success, few-line fixes, pure brainstorming, and emergency hotfixes where process costs more than the risk (if an initiative already exists, journal the exception). Executable changes follow `code-change-discipline` either way.

## Artifacts

```text
docs/helm/<initiative-id>/
  goal.md          # Intent, success criteria, phase index — the ONLY status holder
  phases/
    01-<slug>.md   # Detail for one phase: outcome, chunks, verification
  journal.md       # Append-only steer / handoff / decision log (create on first entry)
  research.md      # Optional disposable intake notes
```

**Initiative ID:** `YYYY-MM-DD-short-english-slug` (lowercase kebab-case). Keep the date human-readable; do not add hours or minutes by default. If the ID already exists, first decide whether to resume it; if the work is genuinely separate, prefer a more specific semantic slug; only when no useful distinction exists append `-02`, `-03`, and so on. Never use a timestamp suffix merely to bypass Resume.

**Phase numbering:** filename `NN-<slug>.md` ↔ title `PN` ↔ goal.md index line `PN`. Phase numbers are permanent and monotonic: never reuse a number or add letter suffixes. A replacement or follow-up phase takes the next unused integer — numbers record execution history, so completed phases are never reopened or rewritten.

**Metadata:** goal and phase files carry `created` and `updated` as timezone-aware ISO 8601 timestamps (`YYYY-MM-DDTHH:MM:SS±HH:MM` or `Z`) and an integer revision starting at `revision: 1`. For each logical edit, preserve `created`, set `updated`, and increment `revision` once. Before writing, re-read status, owner, and revision; if they changed since you last read them, reconcile instead of overwriting newer state.

Create files lazily. Templates live in `templates/` next to this file (`goal.md`, `phase.md`, `journal-entry.md`, and `intake-prompt.md` for delegated read-only recon). If they are unreadable, follow the field lists here rather than inventing a parallel scheme.

## Resume first

1. Scan status lines, not whole files: `grep -H "^status:" docs/helm/*/goal.md`. Full-read only `active` goals, a `proposed` goal the user is continuing, or a named initiative the user refers to — even a `done` one.
2. If one matches, read goal.md, the active phase file, and the last few journal entries; restate the **current focus** and **next concrete step**; then continue.
3. Create a new initiative only for genuinely new work or when the user asks.
4. **Owner check:** if `owner` names another session or agent, take over by updating `owner` — unless another agent appears to be working on it right now (fresh edits you did not make, or a journal note saying so); then edit nothing and tell the user. When you take over unfinished phase work, journal a handoff entry.

## Workflow

```
Resume? → Frame goal.md → Plan current phase → Execute chunk → Checkpoint → Complete phase / Close
              ↑                                                   │
              └─────────────── Steer L1 / L2 / L3 ←───────────────┘
```

### 1. Frame — write `goal.md`

Clarify only enough to write a checkable goal; explore the repo when facts live in code (for heavy exploration, delegate read-only recon built from `templates/intake-prompt.md`). Keep goal.md thin: intent, checkable success criteria, non-goals, constraints, a phase index of outcomes with their status, and optional open questions. Detailed steps never belong here.

- **Language:** if the project has `CONTEXT.md` or `CONTEXT-MAP.md`, use its terms and resolve conflicts before writing the goal. Record newly pinned terms there (format per `domain-modeling`); the goal inherits the project's language rather than defining it.
- **Open design decisions:** when a decision blocks a checkable goal, settle it with the user first — ask focused questions directly. Use `grill-with-docs` (or `grill-me` when no docs are needed) only when the user wants a stress test or the result belongs in the glossary or an ADR. Skip the interview when the direction is already clear.
- **Phases:** list only phases the evidence already justifies; a single phase is normal. Add more as you learn.
- **Commits:** record the authorization under Constraints as `Commits: checkpoint commits authorized` or `Commits: none`. Take it from an explicit user instruction or repository policy; otherwise default to `Commits: none` and mention once that checkpoint commits can be enabled.

Set the goal `status: active` and start P1. For large or hard-to-reverse initiatives, keep the goal `proposed` until the user confirms it.

### 2. Plan — write only the current phase

Create the phase file from `templates/phase.md`; later phases stay as index lines until activated.

- One phase = one checkable outcome, small enough to discard or rework without grief (hours, not weeks). Split it if it grows past about seven chunks.
- A chunk is one coherent change the owner can verify and accept on its own. For executable chunks, record the kind and expected first signal per `code-change-discipline` — an expected Red for behavior changes and bug fixes, a Green or performance baseline for refactors and optimizations — plus the checks that will prove it. Tests live inside each chunk, never in a trailing testing chunk.
- **Phase verification** lists the cross-chunk or end-to-end checks the outcome needs beyond the chunk checks.
- Include **Assumptions** and **Abort / reshape triggers**.

### 3. Execute

Work the chunks in this session. `code-change-discipline` owns how executable changes are tested; Helm owns acceptance, phase state, and commits. An expected Red is unaccepted work: never accept it, check off its chunk, or commit it. Run a Checkpoint after each chunk reaches Green (or each delegated report returns), and earlier if something smells wrong.

When the user says to plan only or not to touch code, Helm artifact edits stay in scope (status, phase plans, journal); stop before implementation.

### 4. Checkpoint

Silently ask:

1. Do the goal's success criteria still describe what we should optimize for?
2. Is the current phase outcome still the right next destination?
3. Did this chunk move us toward that outcome, or only produce motion?

| Result | Action |
|--------|--------|
| On track | Accept on observed evidence, tick the chunk, continue |
| Path wrong, goal still right | **L1** or **L2** (see Steer) |
| Goal / success criteria wrong | **L3** — stop implementation first |

**Acceptance** needs observed results that match the chunk's plan: Red-to-Green evidence plus relevant regressions for behavior changes and bug fixes, before-and-after Green evidence for refactors, correctness and measurement evidence for optimizations. State checks not run and any test-first exception with its compensating verification; missing required evidence blocks acceptance. A delegate's "done" is a report, not acceptance.

**Commits** happen only when goal.md Constraints authorize them. Then commit each accepted chunk as an isolated change — its implementation, tests, and the phase-file tick, never unrelated working-tree edits — and commit Helm artifacts once per phase transition, L2/L3 steer, revisit, handoff, or Close; L1 plan edits ride along with the next commit. Messages name the chunk or transition, e.g. `feat(login): password strength meter` or `docs(helm): P2 done`. Without authorization, keep the same acceptance boundaries, avoid mixing in unrelated changes, and report which accepted chunks remain uncommitted.

Before rewriting files on L2 or L3 (or when unsure), tell the user the one-line classification.

### 5. Complete phase and Close

- **Complete a phase** only when every chunk is accepted and each Phase verification check has an observed passing result (or a recorded exception with compensating verification). A failing or unrun phase check keeps the phase `active`: add the fix as a new chunk (L1) or steer. Then mark it `done` and start the next phase, or Close.
- **Close as done:** tick every success criterion in goal.md, or journal a waiver naming the criterion and why; then set the goal `status: done`.
- **Abandon:** set `status: abandoned` and journal why. Do not fake completion.

Transition mechanics live in `REFERENCE.md`.

## Status

Status lives only in goal.md: the top-level `status` line and each phase index line. Phase files carry no status field; the single `active` index line is the current focus.

| Goal `status` | Meaning |
|---------------|---------|
| `proposed` | Drafted or revised, awaiting confirmation; nothing executes |
| `active` | The working initiative |
| `done` | Success criteria met or waived |
| `abandoned` | Stopped on purpose |

Phase index values: `pending` | `active` | `done` | `blocked` | `superseded`.

- There is at most one `active` phase, and only while the goal is `active`; a `proposed`, `done`, or `abandoned` goal has none. Starting a phase on a goal that is not `active` reopens the goal (see `REFERENCE.md` › Start phase).
- One owner per initiative, recorded in goal.md; delegates are never owners. Do not advance different phases in parallel; if work truly needs independently owned phases, split it into separate initiatives.
- Keep goal.md edits small and directional. History lives in the journal — not in extra status fields or `goal-v2.md` copies, unless the user asks for snapshots.

## Steer

When execution disappoints, priorities shift, or the user changes their mind mid-flight, classify and update the files — agreeing in chat is not enough. Read the matching `REFERENCE.md` section before executing a level.

- **L1 — Adjust:** the goal and phase outcome hold; steps, APIs, files, test seams, ordering, or a messy plan need correction. Edit the phase plan in place and keep going.
- **L2 — Reshape:** the phase outcome or approach has failed, but Intent and Success criteria hold. Say `L2 reshape — <why>`, stop digging, supersede the phase, start a replacement under the next unused integer, and decide which tests still express a stable contract.
- **L3 — Steer:** success criteria, non-goals, or core intent no longer match reality. Say `L3 steer — <why>`, freeze feature work, revise goal.md in place, re-phase, journal the evidence, and decide what code and tests to keep, rewrite, discard, or revert. If the user must re-approve the revised goal, leave it `proposed` with no phase `active` and stop until they confirm; otherwise start the new current phase and continue.
- **Revisit completed work:** when new evidence challenges a `done` phase, keep its file and ID and start a new phase under the next unused integer — this reopens a closed goal. Keep the old phase `done` when its accepted outcome still holds and the new phase is follow-up; mark it `superseded` when the evidence invalidates it, and re-check later phases that depended on it. If the evidence changes Intent or Success criteria, it is L3.

After L2, L3, or a revisit, restate the current focus and next concrete step.

An expected Red is evidence that planned behavior is still missing, not a steer signal by itself. Classify only when a failure challenges the test path, phase outcome, or goal.

```
Something feels wrong
  → Still the right success criteria?          no → L3
  → Still the right phase outcome / approach?  no → L2
  → Otherwise                                     → L1
  → Unsure? Run the smallest check (read code, spike, reproduce), then classify.
```

Never "finish the wrong plan first" — wrong-goal work compounds.

**Journal:** create `journal.md` on the first L2, L3, revisit, handoff, abandonment, waiver, or decision you would regret losing. Append entries from `templates/journal-entry.md`; never rewrite old ones.

**Project assets:** L1 never touches `CONTEXT.md` or ADRs. L2 and L3 update them only when the change alters a term's meaning or reverses a recorded decision; link those edits from the journal entry.

## Delegation

Execution stays in this session by default. Independent chunks inside the active phase may go to subagents while the owner keeps acceptance. Delegates never own the initiative, never edit goal.md or journal.md, and never commit. Build each brief and judge each report with `REFERENCE.md` › Delegation contract, then run a Checkpoint on the evidence.

## Mini example

```text
docs/helm/2026-07-18-billing-webhooks/
  goal.md                  # status: active; owner: sess-abc; Commits: none
  phases/
    01-verify-stubs.md     # superseded pure-mock approach — file kept as history
    02-contract-tests.md   # current phase detail — no status field
  journal.md               # L2 entry: why mocks failed, which tests were kept
```

goal index lines:

```text
1. P1 — webhook stubs verified against live event types — status: superseded
2. P2 — webhook handlers pass contract tests on recorded events — status: active
```
