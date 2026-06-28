# Runner Workflow

This workflow is for Claude Code when delegating a task to Codex CLI.

## 1. Decide Whether Delegation Is Appropriate

Delegate only when:

- the user has approved a design or implementation plan
- the target project path is known
- the allowed scope is clear
- verification commands can be named

Continue the conversation instead of invoking Codex when:

- requirements are unclear
- the task needs product or design choices
- the user asked for explanation only

## 2. Choose Task Mode

Default to task-file mode:

```text
docs/tasks/<task-id>/task.md
```

Use prompt mode only when all of these are true:

- the task is small
- the user does not need a saved task file
- the prompt still includes the same fields as the task template

## 3. Create Task ID

Use:

```text
YYYY-MM-DD-<slug>
```

Example:

```text
2026-06-28-add-login-validation
```

## 4. Prepare Directories

Inside the target project, ensure:

```text
docs/tasks/<task-id>/
.codex-runs/<task-id>/smoke/
.codex-runs/<task-id>/logs/
.codex-runs/<task-id>/tmp/
.codex-runs/<task-id>/artifacts/
```

## 5. Maintain `.gitignore`

If the target project has `.gitignore` and it does not contain `.codex-runs/`, append:

```gitignore
.codex-runs/
```

If the target project has no `.gitignore`, create it with:

```gitignore
.codex-runs/
```

Record this change in Codex's task constraints and in Claude's final summary.

## 6. Write Task File

Write:

```text
docs/tasks/<task-id>/task.md
```

Use `references/task-template.md`.

The task must include:

- absolute target project path
- permission mode
- artifact policy
- allowed scope
- out-of-scope items
- verification commands
- report path

## 7. Invoke Codex

Use a one-shot invocation:

```bash
codex exec "Read shared/codex-task-contract.md semantics from the prompt below. Execute the task at docs/tasks/<task-id>/task.md in <target-project>. Follow the Codex task executor protocol. Write the report to docs/tasks/<task-id>/codex-report.md and exit."
```

Include the relevant shared contract text or a concise copy of its rules in the invocation prompt, because Codex may not have this skills repository in its working directory.

## 8. Read Report

Read:

```text
docs/tasks/<task-id>/codex-report.md
```

If the report is missing, summarize Codex stdout and stderr and tell the user that Codex did not complete the reporting protocol.

## 9. Summarize For User

Report:

- status
- changed files
- verification results
- promoted tests
- temporary smoke checks
- risks and follow-ups
- suggested commit message
- whether commit splitting may be needed

Claude Code owns final staging and committing unless the user explicitly asks otherwise.
