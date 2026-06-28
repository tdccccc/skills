# Codex Execution Protocol

This protocol is for Codex when executing a Claude-generated task.

## 1. Read The Task

Read the task file declared by Claude. The default path is:

```text
docs/tasks/<task-id>/task.md
```

Extract:

- `task_id`
- `target_project`
- `task_kind`
- `mode`
- `sandbox`
- `provider`
- `artifact_policy`
- goal
- context
- allowed scope
- out-of-scope items
- constraints
- verification commands
- report path

If the task is provided directly in the prompt, treat the prompt as the task file.

If the invocation prompt includes XML blocks such as `<task>`, `<execution_contract>`, `<output_contract>`, or `<action_safety>`, treat them as routing and safety instructions. The task file remains authoritative for scope, verification, and report path.

If Claude Code invoked you through its local Codex runner, treat the runner as process management only. The runner owns `run.json`, `stdout.log`, `stderr.log`, cancellation, and audited follow-up task creation. Your job is still a single task execution: read the task, work within scope, write the report, and exit.

## 2. Confirm Working Directory

Work inside `target_project`.

If the current working directory is not the target project, change to the target project before reading or writing project files.

Do not write outside `target_project` unless the task explicitly allows it and the user has approved that capability.

If `sandbox` is `read-only`, do not modify source files and do not assume report-file writes are possible. For `analysis` or `planning` tasks running with `workspace-write`, write only the explicitly allowed plan/report paths and do not edit source files.

## 3. Prepare Run Directories

Ensure these directories exist:

```text
docs/tasks/<task-id>/
.codex-runs/<task-id>/smoke/
.codex-runs/<task-id>/logs/
.codex-runs/<task-id>/tmp/
.codex-runs/<task-id>/artifacts/
```

Ensure `.gitignore` contains:

```gitignore
.codex-runs/
```

If `.gitignore` changes, mention it in the report.

## 4. Preserve User Work

Before editing, inspect the working tree:

```bash
git status --short
```

Treat existing changes as user changes. Do not revert them. If an existing change overlaps the task, work with it and describe the overlap in the report.

## 5. Implement Within Scope

Only modify files that are necessary for the task goal and allowed by the task scope.

Temporary reproduction checks, smoke scripts, command logs, and generated samples must go under:

```text
.codex-runs/<task-id>/
```

Do not leave temporary files in the project root.

## 6. Tests

Use temporary smoke checks for one-off verification:

```text
.codex-runs/<task-id>/smoke/
```

Use project test directories for permanent tests that should prevent regressions:

```text
tests/
test/
spec/
__tests__/
src/**/*.test.ts
```

When promoting a test, explain the path and reason in the report.

## 7. Verification

Run the commands listed in the task file when possible.

For each command, capture:

- command
- pass, fail, or not run
- short notes with the important output

If a command cannot run because dependencies are missing, network is blocked, or permission is required, do not silently skip it. Mark it as `not run` and explain the blocker.

## 8. Git Boundary

Default behavior:

```text
Do not run git add.
Do not run git commit.
```

Report changed files and suggest a Conventional Commit message.

If the changes contain multiple independent intents, say that the user should consider splitting commits.

## 9. Report

Write the report to:

```text
docs/tasks/<task-id>/codex-report.md
```

If the sandbox is `read-only`, do not attempt to write the report file. Instead, print the full structured report to **stdout** as your final message, then exit.

Use `references/report-template.md`.

Always write a report, including failed and partial runs.

## 10. Exit

After writing the report, stop. Do not keep background processes running.

Do not run native `codex resume` for runner-managed follow-ups. Audited resume is represented as a new task file that includes the previous task and report as context.
