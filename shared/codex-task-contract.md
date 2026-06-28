# Codex Task Contract

This contract defines how Claude Code hands work to Codex CLI and how Codex reports back.

## Roles

- Claude Code prepares the task, writes or injects the task package, invokes Codex once, reads the report, and summarizes the result for the user.
- Codex reads the task package, modifies only the target project within the declared scope, runs verification, writes a report, and exits.

## Default Directory Layout in the Target Project

```text
<target-project>/
  docs/
    tasks/
      <task-id>/
        task.md
        codex-report.md
        claude-summary.md
  .codex-runs/
    <task-id>/
      smoke/
      logs/
      tmp/
      artifacts/
```

## Task ID

Use `YYYY-MM-DD-<slug>`, for example `2026-06-28-add-login-validation`.

The slug should be lowercase ASCII with words separated by hyphens.

## Task File

Default path:

```text
docs/tasks/<task-id>/task.md
```

The task file must include:

- task id
- target project absolute path
- permission mode
- artifact policy
- goal
- context
- allowed scope
- out-of-scope items
- constraints
- verification commands
- report path

## Report File

Default path:

```text
docs/tasks/<task-id>/codex-report.md
```

Codex must write this report even when the task fails.

## Permission Modes

### semi-auto

This is the default mode.

Allowed:

- read and write files inside the target project
- run existing tests, formatters, linters, builds, and local verification commands
- create `docs/tasks/<task-id>/`
- create `.codex-runs/<task-id>/`
- update or create `.gitignore` to include `.codex-runs/`

Not allowed without explicit user approval:

- network access
- installing dependencies
- writing outside the target project
- destructive commands such as mass deletion or history rewrites
- database migrations that change persistent state
- `git add`
- `git commit`

### auto

This mode is opt-in and must be explicitly written in the task file.

Allowed only when the task file explicitly lists the capability:

- install dependencies
- use network access
- run project-specific setup commands
- stage or commit files

Even in `auto`, Codex must preserve unrelated user changes and report every high-risk action it ran.

## Artifact Policy

Default:

```yaml
artifact_policy: keep-report-only
```

Supported values:

- `keep-report-only`: keep `task.md` and `codex-report.md`; temporary files may remain under ignored `.codex-runs/<task-id>/` during the run but should not be treated as source artifacts.
- `keep-run-artifacts`: keep `.codex-runs/<task-id>/` for later inspection.
- `promote-useful-tests`: Codex may move valuable temporary tests into the project's normal test directories and must explain why they are permanent tests.

## Temporary Artifacts

Temporary files must stay under:

```text
.codex-runs/<task-id>/
```

Use these subdirectories:

- `smoke/`: one-off smoke scripts and reproduction checks
- `logs/`: command output and debugging logs
- `tmp/`: intermediate files
- `artifacts/`: screenshots, generated samples, benchmark outputs, and other evidence

Codex must not leave files such as `test.js`, `smoke.py`, or `tmp-output.json` in the target project root.

## Tests

Temporary verification checks belong in:

```text
.codex-runs/<task-id>/smoke/
```

Permanent regression tests belong in the target project's existing test locations, such as:

```text
tests/
test/
spec/
__tests__/
src/**/*.test.ts
```

If Codex promotes a temporary check to a permanent test, the report must include the new path and the reason it prevents a future regression.

## Git Boundaries

Default behavior:

- Codex must not run `git add`.
- Codex must not run `git commit`.
- Codex must report changed files.
- Codex must suggest a Conventional Commit message.
- Codex must say whether the work appears to contain multiple independent commit intents.

Claude Code or the user owns final staging and committing.

## Required Report Sections

The report must include:

- status: `success`, `partial`, or `failed`
- summary
- changed files
- verification commands and results
- promoted tests
- temporary smoke checks
- risks and follow-ups
- suggested commit message
- notes for Claude
