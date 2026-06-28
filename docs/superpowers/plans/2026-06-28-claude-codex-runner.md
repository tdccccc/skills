# Claude Codex Runner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a personal two-skill workflow where Claude Code prepares tasks and invokes Codex CLI once, while Codex executes the task, verifies it, writes a report, and exits.

**Architecture:** Create two focused skills plus one shared contract. `claude-codex-runner` owns task packaging and Codex invocation; `codex-task-executor` owns task execution and reporting; `shared/codex-task-contract.md` defines the stable interface between them. Task records live under `docs/tasks/<task-id>/`, while temporary execution artifacts live under `.codex-runs/<task-id>/`.

**Tech Stack:** Markdown-based Claude/Codex skills, Codex CLI (`codex exec`), shell verification with `rg`, `find`, and `git`.

---

## Scope Check

This is one cohesive workflow with two skill entry points and one shared protocol. The plan does not add a wrapper script in `tools/`; that can be extracted later after the Markdown protocol proves stable.

The current repository root contains an invalid `.git` directory and `article-summary/` is its own Git repository. This plan includes commit commands as implementation checkpoints, but execution should first confirm whether the root `skills/` directory will be converted into the personal skills package repository. If root Git remains invalid, run the verification steps and skip commit commands while reporting that commits were not possible.

## File Structure

- Create `README.md`: describes this personal skills package and how skills are organized.
- Create `shared/codex-task-contract.md`: the single source of truth for task directories, permission modes, artifact policy, report format, and commit boundaries.
- Create `claude-codex-runner/SKILL.md`: Claude Code side skill trigger and high-level workflow.
- Create `claude-codex-runner/references/task-template.md`: canonical task file template under `docs/tasks/<task-id>/task.md`.
- Create `claude-codex-runner/references/runner-workflow.md`: detailed Claude-side procedure for preparing, invoking, and summarizing Codex work.
- Create `codex-task-executor/SKILL.md`: Codex side skill trigger and high-level execution duties.
- Create `codex-task-executor/references/execution-protocol.md`: detailed Codex-side execution rules.
- Create `codex-task-executor/references/report-template.md`: canonical report template under `docs/tasks/<task-id>/codex-report.md`.

## Task 1: Add Personal Skills Package README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create the package README**

Create `README.md` with this content:

```markdown
# Personal Skills

This repository is a personal skills package for Claude Code and Codex workflows.

## Skills

- `article-summary/` summarizes astronomy and academic papers into structured Chinese notes.
- `claude-codex-runner/` lets Claude Code package a task and invoke Codex CLI for one-shot execution.
- `codex-task-executor/` tells Codex how to execute Claude-generated task packages and write structured reports.

## Shared Protocols

- `shared/codex-task-contract.md` defines the task and report contract used by `claude-codex-runner` and `codex-task-executor`.

## Layout

```text
skills/
  README.md
  shared/
    codex-task-contract.md
  claude-codex-runner/
    SKILL.md
    references/
      task-template.md
      runner-workflow.md
  codex-task-executor/
    SKILL.md
    references/
      execution-protocol.md
      report-template.md
  article-summary/
    SKILL.md
    references/
      summary-template.md
```

## Conventions

- Each skill directory contains one `SKILL.md`.
- Supporting instructions and templates live in `references/`.
- Shared contracts used by multiple skills live in `shared/`.
- Task records generated in target projects use `docs/tasks/<task-id>/`.
- Temporary Codex execution artifacts in target projects use `.codex-runs/<task-id>/` and should be ignored by Git.
```

- [ ] **Step 2: Verify the README exists and mentions every top-level component**

Run:

```bash
test -f README.md
rg "claude-codex-runner|codex-task-executor|shared/codex-task-contract.md|article-summary" README.md
```

Expected: `test` exits with code 0, and `rg` prints all four matched terms.

- [ ] **Step 3: Commit the README if root Git is valid**

Run:

```bash
git rev-parse --is-inside-work-tree
git add README.md
git commit -m "docs: describe personal skills package"
```

Expected: `git rev-parse` prints `true`, and the commit succeeds. If `git rev-parse` fails because root Git is invalid, do not create a commit; record this in the implementation report.

## Task 2: Add Shared Codex Task Contract

**Files:**
- Create: `shared/codex-task-contract.md`

- [ ] **Step 1: Create the shared contract directory**

Run:

```bash
mkdir -p shared
```

Expected: `shared/` exists.

- [ ] **Step 2: Create the shared contract**

Create `shared/codex-task-contract.md` with this content:

```markdown
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
```

- [ ] **Step 3: Verify the contract covers the agreed defaults**

Run:

```bash
rg "semi-auto|auto|keep-report-only|docs/tasks/<task-id>/task.md|docs/tasks/<task-id>/codex-report.md|.codex-runs/<task-id>|must not run `git add`|must not run `git commit`" shared/codex-task-contract.md
```

Expected: `rg` prints matches for every listed default and Git boundary.

- [ ] **Step 4: Commit the shared contract if root Git is valid**

Run:

```bash
git rev-parse --is-inside-work-tree
git add shared/codex-task-contract.md
git commit -m "docs: define codex task contract"
```

Expected: commit succeeds when root Git is valid. If root Git is invalid, skip the commit and record that in the implementation report.

## Task 3: Add Claude Code Runner Skill

**Files:**
- Create: `claude-codex-runner/SKILL.md`
- Create: `claude-codex-runner/references/task-template.md`
- Create: `claude-codex-runner/references/runner-workflow.md`

- [ ] **Step 1: Create the Claude runner directories**

Run:

```bash
mkdir -p claude-codex-runner/references
```

Expected: `claude-codex-runner/references/` exists.

- [ ] **Step 2: Create `claude-codex-runner/SKILL.md`**

Create `claude-codex-runner/SKILL.md` with this content:

```markdown
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
```

- [ ] **Step 3: Create `claude-codex-runner/references/task-template.md`**

Create `claude-codex-runner/references/task-template.md` with this content:

```markdown
# Codex Task: {{title}}

task_id: {{task_id}}
target_project: {{absolute_target_project_path}}
mode: semi-auto
artifact_policy: keep-report-only
source: claude-code

## Goal

{{one_or_two_sentences_describing_the_requested_outcome}}

## Context

{{relevant_context_from_claude_conversation_design_docs_and_local_files}}

## Scope

Allowed:

- {{allowed_file_or_module_or_behavior_1}}
- {{allowed_file_or_module_or_behavior_2}}

Out of scope:

- {{explicitly_excluded_work_1}}
- {{explicitly_excluded_work_2}}

## Constraints

- Do not run `git add`.
- Do not run `git commit`.
- Do not write temporary files outside `.codex-runs/{{task_id}}/`.
- Preserve unrelated user changes.
- Follow the existing project style.
- Ask for approval before using network access, installing dependencies, writing outside the target project, running destructive commands, or changing persistent databases.
- Ensure `.codex-runs/` is present in `.gitignore`.

## Verification

Commands:

- {{verification_command_1}}
- {{verification_command_2}}

Expected result:

- {{expected_success_condition_1}}
- {{expected_success_condition_2}}

## Report

Write report to:

```text
docs/tasks/{{task_id}}/codex-report.md
```

Use the report structure from the Codex task executor protocol.
```

- [ ] **Step 4: Create `claude-codex-runner/references/runner-workflow.md`**

Create `claude-codex-runner/references/runner-workflow.md` with this content:

```markdown
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
```

- [ ] **Step 5: Verify Claude runner files**

Run:

```bash
test -f claude-codex-runner/SKILL.md
test -f claude-codex-runner/references/task-template.md
test -f claude-codex-runner/references/runner-workflow.md
rg "codex exec|docs/tasks/<task-id>/task.md|.codex-runs/<task-id>|semi-auto|keep-report-only|Do not run `git commit`" claude-codex-runner
```

Expected: all `test` commands exit with code 0, and `rg` prints matches from the three created files.

- [ ] **Step 6: Commit the Claude runner skill if root Git is valid**

Run:

```bash
git rev-parse --is-inside-work-tree
git add claude-codex-runner
git commit -m "feat(claude-codex-runner): add codex delegation workflow"
```

Expected: commit succeeds when root Git is valid. If root Git is invalid, skip the commit and record that in the implementation report.

## Task 4: Add Codex Task Executor Skill

**Files:**
- Create: `codex-task-executor/SKILL.md`
- Create: `codex-task-executor/references/execution-protocol.md`
- Create: `codex-task-executor/references/report-template.md`

- [ ] **Step 1: Create the Codex executor directories**

Run:

```bash
mkdir -p codex-task-executor/references
```

Expected: `codex-task-executor/references/` exists.

- [ ] **Step 2: Create `codex-task-executor/SKILL.md`**

Create `codex-task-executor/SKILL.md` with this content:

```markdown
---
name: codex-task-executor
description: Use in Codex when executing a Claude-generated task package, especially a task file under docs/tasks/<task-id>/task.md. Follow the shared task contract, modify only scoped files, verify the work, write docs/tasks/<task-id>/codex-report.md, and exit. 适用于 Codex 接收 Claude 生成的任务包并执行后汇报。
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
```

- [ ] **Step 3: Create `codex-task-executor/references/execution-protocol.md`**

Create `codex-task-executor/references/execution-protocol.md` with this content:

```markdown
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
- `mode`
- `artifact_policy`
- goal
- context
- allowed scope
- out-of-scope items
- constraints
- verification commands
- report path

If the task is provided directly in the prompt, treat the prompt as the task file.

## 2. Confirm Working Directory

Work inside `target_project`.

If the current working directory is not the target project, change to the target project before reading or writing project files.

Do not write outside `target_project` unless the task explicitly allows it and the user has approved that capability.

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

Use `references/report-template.md`.

Always write a report, including failed and partial runs.

## 10. Exit

After writing the report, stop. Do not keep background processes running.
```

- [ ] **Step 4: Create `codex-task-executor/references/report-template.md`**

Create `codex-task-executor/references/report-template.md` with this content:

```markdown
# Codex Report: {{title}}

task_id: {{task_id}}
status: {{success_or_partial_or_failed}}
mode: {{semi_auto_or_auto}}
artifact_policy: {{keep_report_only_or_keep_run_artifacts_or_promote_useful_tests}}

## Summary

{{what_codex_completed_in_plain_language}}

## Changed Files

- `{{path}}`: {{why_this_file_changed}}

## Verification

- Command: `{{command}}`
  Result: {{pass_or_fail_or_not_run}}
  Notes: {{important_output_or_blocker}}

## Tests

Promoted tests:

- `{{path}}`: {{reason_this_test_should_remain_in_the_project}}

Temporary smoke checks:

- `.codex-runs/{{task_id}}/smoke/{{file}}`: {{what_it_checked}}

## Risks / Follow-ups

- {{remaining_risk_or_follow_up}}

## Suggested Commit

```text
{{type}}({{scope}}): {{imperative_subject_under_72_characters}}

{{body_explaining_what_changed_why_and_verification_when_the_change_is_not_tiny}}
```

## Commit Split Assessment

{{single_commit_is_reasonable_or_consider_splitting_with_reason}}

## Notes for Claude

{{short_notes_claude_should_include_when_reporting_to_the_user}}
```

- [ ] **Step 5: Verify Codex executor files**

Run:

```bash
test -f codex-task-executor/SKILL.md
test -f codex-task-executor/references/execution-protocol.md
test -f codex-task-executor/references/report-template.md
rg "codex-report.md|git status --short|Do not run git add|Do not run git commit|Promoted tests|Temporary smoke checks" codex-task-executor
```

Expected: all `test` commands exit with code 0, and `rg` prints matches from the three created files.

- [ ] **Step 6: Commit the Codex executor skill if root Git is valid**

Run:

```bash
git rev-parse --is-inside-work-tree
git add codex-task-executor
git commit -m "feat(codex-task-executor): add task execution protocol"
```

Expected: commit succeeds when root Git is valid. If root Git is invalid, skip the commit and record that in the implementation report.

## Task 5: Cross-Check Protocol Consistency

**Files:**
- Verify: `README.md`
- Verify: `shared/codex-task-contract.md`
- Verify: `claude-codex-runner/SKILL.md`
- Verify: `claude-codex-runner/references/task-template.md`
- Verify: `claude-codex-runner/references/runner-workflow.md`
- Verify: `codex-task-executor/SKILL.md`
- Verify: `codex-task-executor/references/execution-protocol.md`
- Verify: `codex-task-executor/references/report-template.md`

- [ ] **Step 1: Verify every planned file exists**

Run:

```bash
test -f README.md
test -f shared/codex-task-contract.md
test -f claude-codex-runner/SKILL.md
test -f claude-codex-runner/references/task-template.md
test -f claude-codex-runner/references/runner-workflow.md
test -f codex-task-executor/SKILL.md
test -f codex-task-executor/references/execution-protocol.md
test -f codex-task-executor/references/report-template.md
```

Expected: every `test` command exits with code 0.

- [ ] **Step 2: Verify skill frontmatter names**

Run:

```bash
rg "^name: claude-codex-runner$|^name: codex-task-executor$" claude-codex-runner/SKILL.md codex-task-executor/SKILL.md
```

Expected: exactly two frontmatter name matches are printed.

- [ ] **Step 3: Verify directory conventions are consistent**

Run:

```bash
rg "docs/tasks/<task-id>/task.md|docs/tasks/<task-id>/codex-report.md|.codex-runs/<task-id>/" README.md shared/codex-task-contract.md claude-codex-runner codex-task-executor
```

Expected: matches appear in the shared contract and in both skill directories.

- [ ] **Step 4: Verify Git boundary is consistent**

Run:

```bash
rg "Do not run `git add`|Do not run `git commit`|Do not run git add|Do not run git commit|must not run `git add`|must not run `git commit`" shared/codex-task-contract.md claude-codex-runner codex-task-executor
```

Expected: matches appear in the shared contract and in both skill directories.

- [ ] **Step 5: Verify no draft markers remain**

Run:

```bash
rg "T[B]D|TO[D]O|fix[ ]stuff|misc[ ]changes|w[i]p" README.md shared claude-codex-runner codex-task-executor
```

Expected: no matches.

- [ ] **Step 6: Commit consistency fixes if root Git is valid**

Run:

```bash
git rev-parse --is-inside-work-tree
git status --short
git add README.md shared claude-codex-runner codex-task-executor
git commit -m "docs: align codex runner skill protocol"
```

Expected: commit succeeds only if Task 5 required additional edits after earlier commits. If there are no additional changes, Git prints that there is nothing to commit. If root Git is invalid, skip the commit and record that in the implementation report.

## Task 6: Dry-Run The Workflow With A Disposable Target Project

**Files:**
- Create during verification: `/tmp/codex-runner-smoke/`
- Do not modify repository source files unless the dry-run exposes a protocol inconsistency.

- [ ] **Step 1: Create a disposable target project**

Run:

```bash
mkdir -p /tmp/codex-runner-smoke
cd /tmp/codex-runner-smoke
git init
printf '# Smoke Project\n' > README.md
git add README.md
git commit -m "chore: initialize smoke project"
```

Expected: a Git repository exists at `/tmp/codex-runner-smoke`.

- [ ] **Step 2: Simulate Claude-side task directories**

Run:

```bash
cd /tmp/codex-runner-smoke
mkdir -p docs/tasks/2026-06-28-smoke-task
mkdir -p .codex-runs/2026-06-28-smoke-task/smoke
mkdir -p .codex-runs/2026-06-28-smoke-task/logs
mkdir -p .codex-runs/2026-06-28-smoke-task/tmp
mkdir -p .codex-runs/2026-06-28-smoke-task/artifacts
printf '.codex-runs/\n' > .gitignore
```

Expected: task and artifact directories exist, and `.gitignore` ignores `.codex-runs/`.

- [ ] **Step 3: Simulate a task file**

Create `/tmp/codex-runner-smoke/docs/tasks/2026-06-28-smoke-task/task.md` with this content:

```markdown
# Codex Task: Smoke Task

task_id: 2026-06-28-smoke-task
target_project: /tmp/codex-runner-smoke
mode: semi-auto
artifact_policy: keep-report-only
source: claude-code

## Goal

Append one sentence to the smoke project README.

## Context

This disposable project checks the task directory and report protocol.

## Scope

Allowed:

- `README.md`

Out of scope:

- dependency installation
- network access
- commits

## Constraints

- Do not run `git add`.
- Do not run `git commit`.
- Do not write temporary files outside `.codex-runs/2026-06-28-smoke-task/`.
- Preserve unrelated user changes.
- Ensure `.codex-runs/` is present in `.gitignore`.

## Verification

Commands:

- `rg "Codex runner smoke check" README.md`

Expected result:

- The command finds the appended sentence.

## Report

Write report to:

```text
docs/tasks/2026-06-28-smoke-task/codex-report.md
```
```

- [ ] **Step 4: Simulate Codex-side report**

Create `/tmp/codex-runner-smoke/docs/tasks/2026-06-28-smoke-task/codex-report.md` with this content:

```markdown
# Codex Report: Smoke Task

task_id: 2026-06-28-smoke-task
status: success
mode: semi-auto
artifact_policy: keep-report-only

## Summary

Verified the task and report directory layout with a disposable target project.

## Changed Files

- `README.md`: Would contain the smoke sentence in a real execution.
- `.gitignore`: Ignores `.codex-runs/`.

## Verification

- Command: `rg "Codex runner smoke check" README.md`
  Result: not run
  Notes: This dry-run validates protocol layout only.

## Tests

Promoted tests:

- None.

Temporary smoke checks:

- `.codex-runs/2026-06-28-smoke-task/smoke/`: Directory exists for one-off checks.

## Risks / Follow-ups

- None for the directory protocol.

## Suggested Commit

```text
docs: validate codex runner smoke layout
```

## Commit Split Assessment

Single commit is reasonable for this dry-run.

## Notes for Claude

The task directory and report path are easy to locate under `docs/tasks/<task-id>/`.
```

- [ ] **Step 5: Verify the dry-run layout**

Run:

```bash
cd /tmp/codex-runner-smoke
test -f docs/tasks/2026-06-28-smoke-task/task.md
test -f docs/tasks/2026-06-28-smoke-task/codex-report.md
test -d .codex-runs/2026-06-28-smoke-task/smoke
rg ".codex-runs/" .gitignore
rg "status: success|Suggested Commit|Notes for Claude" docs/tasks/2026-06-28-smoke-task/codex-report.md
```

Expected: every command exits with code 0.

## Task 7: Final Review

**Files:**
- Review: all files created by Tasks 1 through 4

- [ ] **Step 1: Show final repository changes**

Run:

```bash
git status --short
```

Expected: created files are listed if commits were skipped, or the working tree is clean if commits succeeded.

- [ ] **Step 2: Inspect the final diff when root Git is valid**

Run:

```bash
git diff -- README.md shared claude-codex-runner codex-task-executor
```

Expected: the diff contains only the planned README, shared contract, Claude runner skill, and Codex executor skill changes.

- [ ] **Step 3: Prepare implementation report**

Report these items to the user:

```text
Implemented:
- README.md
- shared/codex-task-contract.md
- claude-codex-runner/SKILL.md
- claude-codex-runner/references/task-template.md
- claude-codex-runner/references/runner-workflow.md
- codex-task-executor/SKILL.md
- codex-task-executor/references/execution-protocol.md
- codex-task-executor/references/report-template.md

Verified:
- skill files exist
- frontmatter names are present
- task/report paths are consistent
- .codex-runs policy is consistent
- Git staging and commit are disabled by default for Codex
- disposable dry-run layout works

Notes:
- Root Git status: <valid-or-invalid>
- Commits created: <yes-or-no>
```

Replace `<valid-or-invalid>` and `<yes-or-no>` with the actual observed values before reporting.

## Self-Review

- Spec coverage: The plan covers the dual-skill structure, shared protocol, task-directory layout, `.codex-runs/` artifact layout, default `semi-auto` permission mode, optional `auto` mode, default `keep-report-only` policy, `.gitignore` maintenance, no default staging or committing, report format, and dry-run verification.
- Placeholder scan: The only double-brace values are intentional template variables inside task and report templates. No draft-marker text is used in planned source files.
- Type consistency: The same `task_id`, `mode`, `artifact_policy`, `docs/tasks/<task-id>/task.md`, `docs/tasks/<task-id>/codex-report.md`, and `.codex-runs/<task-id>/` names are used across the README, shared contract, Claude runner files, Codex executor files, and dry-run steps.
