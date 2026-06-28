---
name: claude-codex-runner
description: Use in Claude Code when the user wants Claude to hand an already-scoped coding task, implementation plan, or design document to Codex CLI for one-shot execution, then read Codex's report and summarize the result. 适用于在 Claude Code 中让 Codex 执行已明确范围的任务并回报结果。
---

# Claude Codex Runner

Use this skill when the user wants Claude Code to delegate a bounded task to Codex CLI.

## Responsibilities

Claude Code must:

1. Confirm the task is scoped enough for Codex.
2. Prefer task-file mode and create `docs/tasks/<task-id>/task.md` in the target project.
3. Use prompt mode only for small one-off tasks where the user does not need a saved task file.
4. Ensure `.codex-runs/` is ignored by the target project's `.gitignore`.
5. Invoke Codex as a one-shot process with `codex exec`.
6. Read `docs/tasks/<task-id>/codex-report.md`.
7. Summarize Codex's result for the user.

## Shared Contract

Follow `../shared/codex-task-contract.md`.

## Detailed Workflow

Read `references/runner-workflow.md` before invoking Codex.

Use `references/task-template.md` when writing `docs/tasks/<task-id>/task.md`.

## Defaults

- Task mode: task file
- Permission mode: `semi-auto`
- Artifact policy: `keep-report-only`
- Report path: `docs/tasks/<task-id>/codex-report.md`
- Temporary artifacts: `.codex-runs/<task-id>/`
- Git behavior: Codex must not stage or commit by default

## When Not To Use

Do not use this skill when:

- the task is still exploratory and has no implementation boundary
- the user only wants discussion or planning
- the work requires long-running background service management
- the user has asked Claude Code to implement the task directly
