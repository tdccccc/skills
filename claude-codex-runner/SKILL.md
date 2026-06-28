---
name: claude-codex-runner
description: Use in Claude Code when the user wants Claude to hand an already-scoped coding task, implementation plan, or design document to Codex CLI for one-shot execution, then read Codex's report and summarize the result. 适用于在 Claude Code 中让 Codex 执行已明确范围的任务并回报结果。
install-targets: claude
---

# Claude Codex Runner

Delegate an already-scoped coding or analysis task to Codex CLI, then summarize
what Codex reports back.

## Quick start — the default path

For a request like "run codex -p <profile> to <task>", **this file is all you
need**. Do NOT read the reference files, do NOT open `runner.py`, do NOT run
`--help`. Build one command and run it:

```bash
R=~/.claude/skills/claude-codex-runner/tools/codex-runner/codex-runner
"$R" start --prompt "<task, one or two lines>" \
  --project <target-project-dir> \
  --provider <profile> \
  [--sandbox read-only] \
  --background
```

- `--sandbox read-only` for pure analysis/review — Codex prints its report to
  stdout. Omit it for implementation (default `workspace-write`, Codex writes
  `docs/tasks/<task-id>/codex-report.md`).
- That `start` call is the only step that needs the user's confirmation.

Then follow the run and report back:

```bash
"$R" status <task-id>   # repeat until success / failed / cancelled
"$R" result <task-id>   # prints the report file, or the stdout/stderr fallback
```

Summarize the result for the user. The runner auto-adds `.codex-runs/` to the
target project's `.gitignore`, so there is no manual git step.

## Other commands

```bash
"$R" start docs/tasks/<task-id>/task.md --background        # run a hand-written task file
"$R" cancel <task-id>
"$R" resume <task-id> --goal "<follow-up>" [--start --background]
```

`start` flags: `--prompt`, `--project` (default cwd), `--sandbox` (default
`workspace-write`), `--provider`, `--background`, `--codex-bin`. Pass a task
path or `--prompt`, not both. The runner defaults each synthesized task to
`task_kind: implementation`, `mode: semi-auto`, `artifact_policy: keep-report-only`,
and forbids `git add` / `git commit`.

## Read a reference only when you need it

The quick-start path needs none of these. Open one only for the matching case:

- `references/task-template.md` + `references/codex-task-contract.md` — when
  hand-writing a detailed `docs/tasks/<id>/task.md` and you need the exact
  scope / permission-mode / artifact / report rules.
- `references/runner-workflow.md` — for unusual flows (resume chains, foreground
  debugging, a stuck or `unknown` run).

## When not to use

- the task is still exploratory with no implementation boundary
- the user only wants discussion or planning
- the user asked Claude Code to implement it directly
