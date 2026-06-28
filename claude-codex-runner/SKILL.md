---
name: claude-codex-runner
description: Use in Claude Code when the user wants Claude to hand an already-scoped coding task, implementation plan, or design document to Codex CLI for one-shot execution, then read Codex's report and summarize the result. 适用于在 Claude Code 中让 Codex 执行已明确范围的任务并回报结果。
install-targets: claude
---

# Claude Codex Runner

Use this skill when the user wants Claude Code to delegate a bounded task to Codex CLI.

## Responsibilities

Claude Code must:

1. Confirm the task is scoped enough for Codex.
2. For a detailed task, write `docs/tasks/<task-id>/task.md` in the target project.
3. For a small one-off task, use runner `--prompt` mode, which synthesizes a task file automatically.
4. Ensure `.codex-runs/` is ignored by the target project's `.gitignore`.
5. Invoke Codex through the local runner by default.
6. Use runner `status`, `result`, `cancel`, or `resume` when needed.
7. Read `docs/tasks/<task-id>/codex-report.md` or runner `result`.
8. Summarize Codex's result for the user.

## Shared Contract

Follow `references/codex-task-contract.md`.

## Detailed Workflow

Read `references/runner-workflow.md` before invoking Codex.

Use `references/task-template.md` when writing `docs/tasks/<task-id>/task.md`.

## Defaults

- Task mode: task file
- Task kind: `implementation`
- Permission mode: `semi-auto`
- Codex sandbox: `workspace-write` for task-file runs; `read-only` only for stdout-only analysis or planning
- Artifact policy: `keep-report-only`
- Report path: `docs/tasks/<task-id>/codex-report.md`
- Temporary artifacts: `.codex-runs/<task-id>/`
- Git behavior: Codex must not stage or commit by default
- Provider profile: optional `provider` value passed to `codex exec -p`
- Invocation: `claude-codex-runner/tools/codex-runner/codex-runner start docs/tasks/<task-id>/task.md --background`
- One-off shortcut: `claude-codex-runner/tools/codex-runner/codex-runner start --prompt "<one-line task>" --background` (synthesizes the task file in the current project)
- State and logs: `.codex-runs/<task-id>/run.json`, `stdout.log`, and `stderr.log`
- Resume: audited follow-up task via `claude-codex-runner/tools/codex-runner/codex-runner resume <task-id> --goal "<follow-up goal>"`

## When Not To Use

Do not use this skill when:

- the task is still exploratory and has no implementation boundary
- the user only wants discussion or planning
- the user has asked Claude Code to implement the task directly
