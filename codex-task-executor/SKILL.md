---
name: codex-task-executor
description: Use in Codex when executing a Claude-generated task package, especially a task file under docs/tasks/<task-id>/task.md. Follow the shared task contract, modify only scoped files, verify the work, write docs/tasks/<task-id>/codex-report.md, and exit. 适用于 Codex 接收 Claude 生成的任务包并执行后汇报。
install-targets: codex
---

# Codex Task Executor

Use this skill when Codex is asked to execute a Claude-generated task package.

## Responsibilities

Codex must:

1. Read the task file or structured prompt.
2. Confirm the target project path and task id.
3. Follow the declared permission mode.
4. Modify only files within the allowed scope.
5. Put temporary smoke checks and logs under `.codex-runs/<task-id>/`.
6. Promote only valuable regression tests into the project's normal test directories.
7. Run the requested verification commands when possible.
8. Write `docs/tasks/<task-id>/codex-report.md` even on failure.
9. Exit after reporting.

## Shared Contract

Follow `../shared/codex-task-contract.md` when it is available. If it is not available in the working directory, follow the contract included in the invocation prompt.

## Detailed Protocol

Read `references/execution-protocol.md` before making changes.

Use `references/report-template.md` for the final report.

## Git Boundary

By default, do not run:

```bash
git add
git commit
```

Report changed files and suggest a Conventional Commit message instead.
