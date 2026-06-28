# Codex Task: {{title}}

task_id: {{task_id}}
target_project: {{absolute_target_project_path}}
task_kind: implementation
mode: semi-auto
sandbox: workspace-write
provider: {{optional_codex_profile_name_or_blank}}
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
