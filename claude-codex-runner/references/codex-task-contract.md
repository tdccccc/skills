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
- task kind
- permission mode
- Codex sandbox
- Codex provider profile when needed
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

## Task Kinds And Codex Sandbox

Default:

```yaml
task_kind: implementation
sandbox: workspace-write
```

Supported task kinds:

- `implementation`: Codex may edit files within the declared scope. Use `sandbox: workspace-write`.
- `analysis`: Codex should inspect and report without editing source files. Use `sandbox: read-only` only for stdout-only analysis; use `workspace-write` when Codex must write `codex-report.md`.
- `planning`: Codex should read the project and produce a plan without editing source files. Use `sandbox: read-only` only for stdout-only planning; use `workspace-write` when Codex must write plan or report files.

Sandbox mapping:

- `semi-auto` implementation tasks use `workspace-write`.
- analysis and planning tasks use `read-only` for stdout-only runs.
- task-file runs that require writing `docs/tasks/<task-id>/codex-report.md` use `workspace-write`, even for analysis or planning, but source edits remain forbidden unless the task kind is `implementation`.
- `auto` tasks use `workspace-write` by default. Use `danger-full-access` only when the user explicitly permits broad access.

## Codex Provider Profile

Optional:

```yaml
provider: <profile-name>
```

When set, Claude Code should pass it to Codex as:

```bash
codex exec -p <profile-name> ...
```

`-p` is the Codex CLI profile flag. Use it for provider/profile selection without adding model or reasoning-effort fields to the task contract.

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

## Background Runner State

When Claude Code uses the local runner, the runner owns these files:

```text
.codex-runs/<task-id>/run.json
.codex-runs/<task-id>/stdout.log
.codex-runs/<task-id>/stderr.log
```

`run.json` records:

- task id
- absolute task path
- absolute target project path
- run directory
- report path
- status
- worker pid
- Codex pid and process group id
- started and finished timestamps
- exit code
- provider profile
- sandbox
- final Codex command array

Statuses:

- `queued`: background worker has been created but Codex has not started.
- `running`: Codex has started.
- `success`: Codex exited 0.
- `failed`: Codex exited non-zero or the worker failed.
- `cancelled`: Claude Code or the user cancelled the run.
- `unknown`: state says running, but no worker or Codex process is alive and no final status was written.

The runner captures stdout and stderr into the log files. Codex must still write the normal report to `docs/tasks/<task-id>/codex-report.md`.

## Runner Commands

Preferred background invocation:

```bash
claude-codex-runner/tools/codex-runner/codex-runner start docs/tasks/<task-id>/task.md --background
```

Follow-up commands:

```bash
claude-codex-runner/tools/codex-runner/codex-runner status <task-id>
claude-codex-runner/tools/codex-runner/codex-runner result <task-id>
claude-codex-runner/tools/codex-runner/codex-runner cancel <task-id>
claude-codex-runner/tools/codex-runner/codex-runner resume <task-id> --goal "<follow-up goal>"
```

`resume` means `resume-audited`: read the previous `task.md` and `codex-report.md`, create a new `docs/tasks/<follow-up-task-id>/task.md`, and optionally start it. It does not use native `codex resume`.

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
