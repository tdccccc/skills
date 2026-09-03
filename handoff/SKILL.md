---
name: handoff
description: 'Create or resume a concise, verifiable handoff between Claude Code sessions. Use only when explicitly invoked with /handoff. This is a standalone workflow: do not invoke, combine with, or update other skills while it is active.'
disable-model-invocation: true
install-targets: claude
---

# Handoff

Transfer active work between Claude Code sessions through one reviewable Markdown file. Keep the handoff short enough to scan and complete enough that a fresh session does not need the old conversation.

This is a standalone workflow. While it is active, do not invoke or follow another skill, delegate to another skill, or update another skill's workflow state. Complete the handoff operation and stop.

## Usage

Create a handoff (normally no argument is needed):

```text
/handoff
```

The skill derives a short filename topic from the active task. An optional topic only overrides that inferred label when the user wants a specific filename:

```text
/handoff <topic>
```

`<topic>` is only a short filename label, such as `checkout-timeout`; it is not another skill and does not invoke one. Ask for a topic only when the active task does not provide enough information to infer a reliable name.

Resume from a handoff:

```text
/handoff resume docs/handoffs/<file>.md
```

Delete a consumed or obsolete handoff:

```text
/handoff clean docs/handoffs/<file>.md
```

## Boundaries

The create flow may only create a new file under `docs/handoffs/`. The resume flow reads and verifies a handoff but does not modify it. The clean flow may delete only the specific handoff file the user names under `docs/handoffs/`, after inspecting it and confirming when deletion has not already been explicitly requested.

Do not:

- continue implementation, planning, review, or documentation work after completing the handoff operation;
- invoke or mix with other skills, even if their files or workflow state are present;
- modify `CLAUDE.md`, auto memory, hooks, settings, plans, goals, status files, or another skill's artifacts;
- create, switch, or delete branches, commits, tags, pull requests, or issues;
- stage, commit, push, revert, reset, or discard changes;
- export or copy the full session transcript;
- include secrets, credentials, personal data, or large raw command output;
- overwrite an existing handoff.

Treat files produced by other workflows as ordinary project files. Read one only when it is directly relevant to the current task; do not apply the workflow that created it or update its state.

## Create a handoff

### 1. Choose the destination

Write to:

```text
docs/handoffs/YYYY-MM-DD-<topic>.md
```

Use the current local date. Normally infer a short kebab-case topic from the active task's goal, issue, feature, or bug; prefer the user's explicit topic only as a filename override. Keep it specific enough to recognize later and usually two to five words. Ask the user only when no reliable topic can be inferred from the current conversation or repository context; do not ask merely because the command omitted an argument.

Create `docs/handoffs/` when it does not exist. If the target filename already exists, append `-2`, `-3`, and so on; never replace an earlier handoff.

### 2. Capture observable state

Before writing, inspect applicable repository instructions and collect the equivalent of:

```text
git status --short --branch
git rev-parse HEAD
git diff --stat
git log --oneline -5
```

Read the full diff only when needed to describe uncommitted work accurately. Preserve unrelated user changes and distinguish them from task changes when the evidence allows it. If the directory is not a Git repository, say so in the handoff and continue with observable file state.

Use the current conversation and repository as evidence. Do not guess missing requirements, completed work, test outcomes, or reasons. Mark unknown information as `Unknown`, unstated requirements as `Not stated`, and checks not run as `NOT RUN`.

### 3. Keep only continuation-critical information

Include:

- the goal and acceptance criteria;
- completed and remaining work;
- the current implementation state;
- consequential decisions and their reasons;
- failed approaches worth avoiding or retry conditions;
- commands or checks actually run and their observed results;
- blockers and unresolved questions;
- a small set of key repository-relative file paths, with line numbers when useful;
- branch, HEAD, modified and untracked files;
- ordered next steps, each with an expected result and verification where practical.

Exclude conversation chronology, generic repository descriptions, repeated facts, speculative advice, and large logs. Prefer a precise fact or short error excerpt over raw output.

### 4. Write this structure

```markdown
# Handoff: <topic>

- Created: YYYY-MM-DD
- Branch: <branch or Not a Git repository>
- HEAD: <full commit SHA or N/A>
- Working tree: <clean or concise summary>

## Goal

<Original goal in one to three sentences.>

## Acceptance criteria

- [x] <Satisfied criterion>
- [ ] <Unsatisfied criterion>
- [ ] <Unknown or not stated criterion, if relevant>

## Completed

- <Completed, persisted work with relevant paths.>

## Current state

<Where the implementation stopped and any important uncommitted state.>

## Decisions

- **Decision:** <Choice made>
  **Reason:** <Why>
  **Implication:** <Constraint for the next session>

## Failed approaches

- **Tried:** <Approach>
  **Why it failed:** <Observed reason or evidence>
  **Retry only if:** <Condition that would make retry useful>

Use `None recorded.` when there is no useful failed approach.

## Verification

| Command or check | Result | Notes |
|---|---|---|
| `<command actually run>` | PASS / FAIL | <Concise observed evidence> |
| `<relevant check not run>` | NOT RUN | <Reason> |

## Remaining work

- [ ] <Unfinished work, blocker, or unresolved question.>

## Next steps

1. <Concrete first action>
   - Expected: <Observable result>
   - Verify: `<command or check>`
2. <Next action>

## Key files

- `path/to/file:line` — <Why it matters>

## Git state

- Modified: <paths or None>
- Untracked: <paths or None>
- Recent relevant commit: `<SHA> <subject>` or `None identified`

## Resume checks

1. Compare the current branch and HEAD with this handoff.
2. Inspect the current working tree before editing.
3. Confirm that the key files still exist and remain relevant.
4. Treat verification above as historical evidence and rerun affected checks after newer changes.
5. Report material differences before overwriting, reverting, or building on conflicting state.
```

Omit empty decision entries rather than adding filler. Keep the file concise; add detail only when it changes what the next session should do.

### 5. Review and stop

Read the complete handoff after writing it. Check that a session with no conversation history can identify the goal, distinguish completed from remaining work, understand the Git state, avoid known dead ends, and execute the first next step.

Return:

- the created repository-relative path;
- a one-sentence summary of what remains;
- a reminder that the handoff is temporary and should be deleted after the receiving session has verified and consumed it;
- this copyable prompt with the actual path substituted:

```text
/handoff resume docs/handoffs/<file>.md
```

Then stop. Do not continue the transferred task unless the user starts a separate request.

## Resume a handoff

Require one handoff path under `docs/handoffs/`. If the user supplies only a filename or stem, search that directory. Resume directly only when exactly one file matches; if multiple files match, list them and ask the user to choose.

### 1. Read and verify

Read the complete handoff, then inspect the current equivalent of:

```text
git status --short --branch
git rev-parse HEAD
git diff --stat
git log --oneline -5
```

Compare the current branch, HEAD, modified files, untracked files, and relevant recent commits with the recorded state. Confirm that listed key files still exist. Read only the key files needed to validate the first next step.

Do not treat the handoff as authoritative when the repository disagrees with it. Verification results in the handoff are historical evidence, not proof of the current state.

### 2. Report the resume result

Write the resume report in Chinese by default, regardless of the language used in the handoff file. Use another language only when the user explicitly requests it.

Return a concise resume report containing:

- the goal;
- the first next step;
- whether branch, HEAD, and working tree match;
- missing or materially changed key files;
- checks that should be rerun;
- any difference that must be resolved before safe continuation.

If material state differs, stop after reporting it. Do not overwrite, revert, or reconcile anything.

If state matches, state that the handoff is ready and give the exact first action. Also state that the file remains temporary: delete it with `/handoff clean <path>` only after the receiving session has verified the repository state, captured any still-needed information, and no longer needs the file for recovery. Stop there: resuming verifies and re-anchors the task; implementation begins only in a separate user request, outside this skill.

## Clean up a handoff

Handoff documents are temporary coordination artifacts, not permanent project documentation. Remove them promptly once the receiving session has verified the repository state, understood the remaining work, and no longer needs the handoff for recovery. Keep a handoff while it is still the only reliable record of unfinished work, an unresolved blocker, or uncommitted state.

Require one explicit path under `docs/handoffs/`; do not bulk-delete, infer a target from recency, or clean unrelated files. Resolve the path and confirm it remains inside that directory, then read the complete file before deletion.

When the user explicitly invokes `/handoff clean <path>`, that invocation authorizes deletion of that named handoff after the safety checks above; no second confirmation is needed. If cleanup was only suggested or implied, ask for confirmation before deleting because deletion is hard to reverse.

Before deleting, check that:

- the file is a handoff document rather than unrelated project documentation;
- the current repository does not materially conflict with the state the receiving session relied on;
- no continuation-critical information exists only in the handoff;
- the user has not named a different file.

If any check fails or continuation-critical information would be lost, do not delete the file; report the reason and what must be preserved first. Otherwise delete only the named file, remove `docs/handoffs/` only if it becomes empty, and report the deleted repository-relative path. Do not stage, commit, or continue other work.