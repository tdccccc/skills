---
name: claude-codex-runner
description: Use in Claude Code when the user wants Claude to hand an already-scoped coding task, implementation plan, or design document to Codex CLI for one-shot execution, then read Codex's report and summarize the result. 适用于在 Claude Code 中让 Codex 执行已明确范围的任务并回报结果。
install-targets: claude
---

# Claude Codex Runner

Delegate tasks to Codex CLI, then summarize what Codex reports back.

Choose the execution mode based on task complexity:

---

## Agent mode (default) — simple tasks

Use when the task is **well-scoped and doesn't need a formal task file**:
search the web, generate a diagram, understand an image, write a short script,
make a focused code change.

Do NOT write a `task.md`. Instead, **build a direct prompt** and hand it to
Codex via the Agent tool with `run_in_background: true`. The Agent will run
`codex exec` and return the result.

```python
# Pseudocode for the Agent call
Agent(
    subagent_type="general-purpose",
    description="Codex search/diagram/code",
    prompt=(
        "Change to <target-project> and run:\n"
        "codex -a never exec -C <target-project> \\\n"
        "  -s workspace-write --skip-git-repo-check --ephemeral \\\n"
        "  [-p <profile>] '<one-line task description>'\n\n"
        "Wait for Codex to finish, then report back what it did."
    ),
    run_in_background=True,
)
```

- For **web search / browsing**: describe exactly what to fetch in the prompt
- For **diagrams / mermaid**: say "draw a mermaid ... diagram, save to <path>"
- For **image understanding**: include the image path in the prompt
- For **quick code changes**: describe the change precisely

Optionally, you can write a `docs/tasks/<task-id>/task.md` and reference it
in the Agent prompt — useful when a task needs structured constraints but
doesn't need the full Runner lifecycle (status/result/resume).

When the Agent completes, read its output and **summarize for the user**.
If it generated files (diagrams, images, reports), confirm they exist.

---

## Runner mode — complex / multi-step tasks

Use when the task needs **precise scope constraints, verification commands,
multi-file changes, or may need follow-up / resume**:

- cross-file refactors
- tasks that need explicit verification steps
- changes where `git add` / `git commit` boundaries matter
- anything likely to need `resume` for follow-up

**Step 1: write a task file**

Write `docs/tasks/<task-id>/task.md` using the template in
`references/task-template.md` and `references/codex-task-contract.md`.

**Step 2: start Codex in background**

```bash
R=~/.claude/skills/claude-codex-runner/tools/runner
"$R" start docs/tasks/<task-id>/task.md \
  [--provider <profile>]
```

- `start` runs Codex in the background — returns a task-id immediately.
- Default sandbox is `workspace-write` (report + files).
- Passes `-a never` so Codex auto-approves all tool calls.

**Step 3: poll and report**

```bash
"$R" status <task-id>   # includes recent log output; repeat until success/failed
"$R" result <task-id>   # prints the report file
```

For automatic polling, use /loop:

```
/loop 30s codex-runner status <task-id>
```

When done, summarize the result. If a follow-up is needed:

```bash
"$R" resume <task-id> --goal "<follow-up>" --start
```

### Other commands

```bash
"$R" list                          # list all tasks (most recent first)
"$R" cancel <task-id>
```

### Runner flags

`start` flags: `--prompt`, `--project` (default cwd), `--sandbox`
(default `workspace-write`), `--provider`, `--codex-bin`. Pass a task path or
`--prompt`, not both. The runner defaults each synthesized task to
`task_kind: implementation`, `mode: semi-auto`, `artifact_policy: keep-report-only`,
and forbids `git add` / `git commit`.

## Read a reference only when you need it

- `references/task-template.md` + `references/codex-task-contract.md` — when
  hand-writing a detailed task file.
- `references/runner-workflow.md` — for unusual flows (resume chains, debugging
  a stuck or `unknown` run).

## When not to use

- the task is still exploratory with no implementation boundary
- the user only wants discussion or planning
- the user asked Claude Code to implement it directly
