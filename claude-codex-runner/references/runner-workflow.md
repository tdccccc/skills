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
- task kind
- permission mode
- Codex sandbox
- optional provider profile
- artifact policy
- allowed scope
- out-of-scope items
- verification commands
- report path

## 7. Select Codex Invocation Options

Use these defaults:

```yaml
task_kind: implementation
mode: semi-auto
sandbox: workspace-write
```

Use `sandbox: read-only` for analysis or planning tasks that should not modify source files.

Use `workspace-write` instead when the run must write `docs/tasks/<task-id>/codex-report.md`, a plan file, or other explicitly allowed documentation output. In that case, keep `task_kind: analysis` or `task_kind: planning` and state that source edits are forbidden.

If the user specifies a provider/profile, preserve it as:

```yaml
provider: <profile-name>
```

and pass it to Codex with `-p <profile-name>`.

Do not ask for model or reasoning effort unless the user explicitly asks; use the user's Codex config defaults.

## 8. Invoke Codex Through The Runner

Use the local runner by default:

```bash
tools/codex-runner/codex-runner start docs/tasks/<task-id>/task.md --background
```

Run this from the skills repository, or use the executable by absolute path.

The runner:

- parses the task file
- builds the Codex command
- passes `provider` as `codex exec -p <profile-name>` when set
- starts Codex with `stdin` disconnected
- captures stdout and stderr
- writes `.codex-runs/<task-id>/run.json`
- lets Claude Code keep the main conversation active while Codex runs

If foreground execution is preferred for a short task, omit `--background`:

```bash
tools/codex-runner/codex-runner start docs/tasks/<task-id>/task.md
```

## 9. Manage Background Runs

Check status:

```bash
tools/codex-runner/codex-runner status <task-id>
```

Read the report or fallback logs:

```bash
tools/codex-runner/codex-runner result <task-id>
```

Cancel a run:

```bash
tools/codex-runner/codex-runner cancel <task-id>
```

Create an audited follow-up task:

```bash
tools/codex-runner/codex-runner resume <task-id> --goal "<follow-up goal>"
```

Create and start the follow-up task:

```bash
tools/codex-runner/codex-runner resume <task-id> --goal "<follow-up goal>" --start --background
```

`resume` means `resume-audited`: the runner reads the previous `task.md` and `codex-report.md`, writes a new follow-up task directory, and optionally starts that task. It does not use native `codex resume`.

## 10. Direct Codex Fallback

Use direct `codex exec` only when the local runner is unavailable or the user explicitly asks for direct execution.

Use a one-shot invocation:

```bash
codex -a never exec \
  -C "<target-project>" \
  -s "<sandbox>" \
  --skip-git-repo-check \
  --ephemeral \
  "prompt" </dev/null 2>/dev/null
```

If `provider` is set, add it before the prompt:

```bash
-p "<provider>"
```

Always redirect stdin with `</dev/null`; `codex exec` reads stdin and can hang if the harness leaves it open.

Suppress stderr with `2>/dev/null` by default to keep Codex thinking/progress output out of Claude Code's context. If the command fails, rerun or inspect stderr only as needed for debugging.

Use a compact XML-shaped prompt wrapper:

```xml
<task>
Execute docs/tasks/<task-id>/task.md in <target-project>.
</task>

<execution_contract>
Follow the Codex task contract included below. The task file is authoritative.
Use sandbox <sandbox>. Do not stage or commit unless the task explicitly allows it.
</execution_contract>

<output_contract>
Write docs/tasks/<task-id>/codex-report.md, then exit.
</output_contract>

<action_safety>
Keep changes tightly scoped. Preserve unrelated user work. Put temporary files under .codex-runs/<task-id>/.
</action_safety>
```

Include the relevant shared contract text or a concise copy of its rules in the invocation prompt, because Codex may not have this skills repository in its working directory.

## 11. Read Report

Read:

```text
docs/tasks/<task-id>/codex-report.md
```

If using the runner, prefer:

```bash
tools/codex-runner/codex-runner result <task-id>
```

If the report is missing, summarize Codex stdout and stderr and tell the user that Codex did not complete the reporting protocol.

## 12. Summarize For User

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
