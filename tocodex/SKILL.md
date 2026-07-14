---
name: tocodex
description: 'Use when a Claude Code session should delegate a well-scoped task to Codex CLI for isolated execution, then summarize Codex report. 适用于在 Claude Code 中让 Codex 执行已明确范围的任务并回报结果。'
install-targets: claude
---

# ToCodex

Hand a well-scoped task to Codex CLI for one-shot execution, then read Codex's report and summarize the result.

## Workflow

There is one mode: Agent. Claude judges task complexity, generates an appropriate task.md, and delegates to Codex via a background Agent.

```
User request → judge complexity → write task.md → ask provider → Agent runs codex exec → Agent finishes → read report → summarize
```

---

## Step 1: Judge task complexity

### Simple task (use minimal template)

Use the minimal template when the task falls into **one** of these two categories:

**Category A — Read-only / report-only:**
- Search, browse web, view images, draw mermaid diagrams, run a one-off analysis script
- No source file modifications
- `task_kind: analysis`

**Category B — Low-risk single-file implementation:**
- Single file change, ≤ 50 lines combined additions and deletions
- Does **not** touch test files, config files, dependencies, security, data migrations, or permission boundaries
- `task_kind: implementation`

If it doesn't fit either category, use the full template.

### Complex task (use full template)

Use the full template when **any** of the following is true:

- Multi-file changes or refactoring
- Single file change ≥ 50 lines
- Involves dependency installation or config changes
- Needs test runs or verification steps
- Touches test files, security code, data migrations, or permission boundaries
- High-risk operations requiring user approval

---

## Step 2: Generate task.md

### Minimal template

````markdown
# Codex Task: {task_id}

task_id: {task_id}
target_project: {absolute path}
task_kind: analysis (or implementation for simple code changes)
sandbox: workspace-write
artifact_policy: keep-report-only

## Goal

{one sentence describing the goal}

## Scope

{what is allowed and what is not, one or two sentences}

## Constraints

- Do not run `git add` or `git commit`.
- Preserve unrelated user changes.
- Keep all temporary files under `docs/cc-codex-task/{task_id}/`.

## Report

Write report to:

```text
docs/cc-codex-task/{task_id}/codex-report.md
```

Report must include: status, summary, changed files, and suggested commit message.
````

`task_id` format: `YYYY-MM-DD-short-english-slug`

### Full template

````markdown
# Codex Task: {task_id}

task_id: {task_id}
target_project: {absolute path}
task_kind: implementation | analysis | planning
mode: semi-auto
sandbox: workspace-write
provider: {optional profile}
artifact_policy: keep-report-only
source: claude-code

## Goal

{one or two sentences describing the desired outcome}

## Context

{relevant design context, file paths, previous decisions, etc.}

## Scope

Allowed:

- {what is allowed}
- {what is allowed}

Out of scope:

- {explicitly excluded work}
- {explicitly excluded work}

## Constraints

- Do not run `git add`.
- Do not run `git commit`.
- Do not write temporary files outside `docs/cc-codex-task/{task_id}/`.
- Preserve unrelated user changes.
- Ask for approval before using network access, installing dependencies,
  writing outside the target project, running destructive commands,
  or changing persistent databases.

## Verification

Commands:

- {verification command 1}
- {verification command 2}

Expected result:

- {expected result 1}
- {expected result 2}

## Report

Write report to:

```text
docs/cc-codex-task/{task_id}/codex-report.md
```

Write a report even on failure.
````

### Task directory structure

```text
<target-project>/
  docs/
    cc-codex-task/
      <task-id>/
        task.md
        codex-report.md
        stdout.log
        stderr.log
```

All task artifacts live under `docs/cc-codex-task/<task-id>/`. There is no separate `.codex-runs/` directory — stdout and stderr logs are written alongside the task file and report.

---

## Step 3: Determine provider profile

If the user already mentioned a Codex provider/profile in their request (e.g. "用 bnu 跑", "use kimi"), use it directly — no need to ask.

Otherwise, ask the user which Codex provider/profile to use.

**How to ask:** Present the configured profiles as options via AskUserQuestion. If you don't know what profiles the user has configured, include an "Other" path and offer a sensible default (e.g. `bnu`).

Once the user selects a profile, set the `provider:` field in task.md metadata and pass it as `-p <profile>` when invoking Codex. If the user declines to pick one (or picks "default"), omit the `-p` flag entirely.

---

## Step 4: Invoke Codex via Agent

Before launching, check if the task requires any user approvals (network access, dependency installation, destructive commands, database changes). If so, **obtain approval from the user first** — Codex runs with `-a never` and cannot ask interactively.

Then, launch an Agent with `run_in_background: true` to execute Codex. Inside the Agent, run:

```bash
set -o pipefail
cd <target-project>
codex -a never exec \
  -C <target-project> \
  -s workspace-write \
  --skip-git-repo-check \
  --ephemeral \
  [-p <profile>] \
  [--search] \
  [-i <image-path>] \
  '<canonical prompt>' </dev/null 2>docs/cc-codex-task/<task-id>/stderr.log \
  | tee docs/cc-codex-task/<task-id>/stdout.log
```

Add `--search` for web search tasks. Add `-i <image-path>` for image understanding tasks.

The canonical prompt must reference the task file so Codex reads the full contract:

```
<task>Execute docs/cc-codex-task/<task-id>/task.md in <target-project>. Follow the task contract exactly, do not stage or commit, and write the report to the specified path.</task>
```

### Agent's responsibilities

1. Change to the target project directory
2. Create `docs/cc-codex-task/<task-id>/` directory (if not already created by task.md)
3. Run `codex exec` with the command above, tee-ing stdout/stderr to log files
4. Wait for Codex to finish
5. Read `codex-report.md` from disk. If the report is missing (Codex failed before creating it), **synthesize a failure `codex-report.md`** from `stdout.log`, `stderr.log`, and exit status, then return it as the agent's summary.
6. Return a **distilled summary** of what Codex did: status, changed files, verification results, risks, and suggested commit message. Do NOT return Codex's raw full output.
7. Include the report file path so the main session can read the full report if needed.

### How users see progress

While the Agent runs in the background, the user can press the **↓ arrow key** in Claude Code to expand the Agent's live output.

---

## Step 5: Present the result

The Agent already read `codex-report.md` and returned a summary. Present that summary to the user. If they want more detail, read the full report file from disk.

---

## Step 6 (optional): Follow-up / resume

If a previous task was partially completed or needs follow-up:

1. Create a new `docs/cc-codex-task/<new-task-id>/task.md`
2. Reference the previous task.md and codex-report.md in the new task's `## Context`
3. Copy the previous run's output files into the new task directory (so Codex can reference them)
4. Run with a new Agent

**Do NOT use native `codex resume`.** Each iteration gets a fresh task.md + fresh `codex exec` call, preserving audit trail and reproducibility.

---

## Non-negotiable contract (every task must follow)

The following rules apply to every task.md, whether minimal or full template. The templates may omit these fields, but the behavior must be consistent.

### Command flags

- `-a never` — Codex auto-approves all tool calls
- `-s workspace-write` — even analysis tasks use workspace-write (use `task_kind: analysis` to forbid source edits)
- `--skip-git-repo-check` — skip git repo validation
- `--ephemeral` — one-shot run
- `</dev/null` — close stdin, preventing codex exec from hanging
- stderr redirected to log file (`2>`), reducing Agent context pollution

### Source control

- No `git add`
- No `git commit`
- All temporary files must live under `docs/cc-codex-task/<task-id>/`
- Codex must report the list of changed files
- Codex must suggest a Conventional Commit message

### Safety boundaries

- Network access, dependency installation, writing outside the target project, destructive commands, database changes → require explicit approval
- Preserve user's uncommitted changes (check `git status --short`)

### Report

- Must write `codex-report.md` even on failure
- Must include: status, summary, changed files, verification commands and results, temporary smoke checks, risks and follow-ups, suggested commit message

### Read-only analysis

For search, browse, and analysis tasks:
- Use `task_kind: analysis` + `sandbox: workspace-write`
- Explicitly forbid source edits in the Scope section
- `workspace-write` is only for writing `codex-report.md`

---

## When NOT to use this skill

- The task is still exploratory with no clear implementation boundary
- The user only wants discussion or planning
- The user asks you to implement directly (without Codex)
