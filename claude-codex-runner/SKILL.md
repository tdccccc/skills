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
  [--sandbox read-only]
```

- `start` runs Codex **in the background** — it returns a task-id immediately.
- `--sandbox read-only` for pure analysis/review (Codex prints report to stdout).
  Omit for implementation (default `workspace-write`, Codex writes
  `docs/tasks/<task-id>/codex-report.md`).
- That `start` call is the only step that needs the user's confirmation.
- The runner passes `-a always` so Codex auto-approves all tool calls without
  waiting for interactive confirmation. Sandbox isolation is the safety boundary.

### Configuring MCP tools for Codex

If you want Codex to have web search, diagram generation, or other MCP-powered
capabilities, configure them in **Codex directly** (not in this runner):

```bash
codex mcp add <name> -- <command>
# or
codex mcp add <name> --url <url>
```

MCP servers added via `codex mcp add` are automatically available in both
interactive and `exec` mode, so the runner does not need any changes to use
them. For image understanding tasks, just pass the image path in the prompt
(e.g. `--prompt "分析这张图 /path/to/fig.png"`); Codex will read it directly.

Then poll and report back:

```bash
"$R" status <task-id>   # includes recent log output; repeat until success/failed
"$R" result <task-id>   # prints the report file, or the stdout/stderr fallback
```

Summarize the result for the user. The runner auto-adds `.codex-runs/` to the
target project's `.gitignore`, so there is no manual git step.

### Automatic polling with /loop

After starting a background task, set up a /loop to poll automatically:

```
/loop 30s codex-runner status <task-id>  # re-checks every ~30s
```

When the status shows `success` or `failed`, call `result` and summarize. Codex
reports `unknown` status if the worker or codex process disappeared without a
clean exit (e.g. OOM kill, terminal close).

> **Note:** /loop yields to your questions — you can keep chatting; the loop
> only fires when idle.

### Foreground mode (streaming)

Use `start-fg` instead of `start` when you want to **watch Codex work in
real time** — output streams to the terminal as it arrives:

```bash
"$R" start-fg --prompt "<task>" --project <dir> --provider <profile>
```

This blocks until Codex finishes. The same log files are written so you can
still use `result` afterward.

## Other commands

```bash
"$R" start docs/tasks/<task-id>/task.md                # run a hand-written task file (background)
"$R" start-fg docs/tasks/<task-id>/task.md              # run a hand-written task file (foreground)
"$R" list                                                # list all tasks (most recent first)
"$R" list --project <dir>                                # list tasks in a specific project
"$R" cancel <task-id>
"$R" resume <task-id> --goal "<follow-up>"               # create a follow-up task file
"$R" resume <task-id> --goal "<follow-up>" --start       # create and start (background)
"$R" resume <task-id> --goal "<follow-up>" --start --foreground  # create and start (foreground)
```

`start` flags: `--prompt`, `--project` (default cwd), `--sandbox` (default
`workspace-write`), `--provider`, `--codex-bin`. Pass a task path or `--prompt`,
not both. The runner defaults each synthesized task to `task_kind: implementation`,
`mode: semi-auto`, `artifact_policy: keep-report-only`, and forbids `git add` /
`git commit`.

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
