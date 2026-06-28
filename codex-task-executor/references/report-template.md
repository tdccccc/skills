# Codex Report: {{title}}

task_id: {{task_id}}
status: {{success_or_partial_or_failed}}
mode: {{semi_auto_or_auto}}
sandbox: {{read_only_or_workspace_write_or_danger_full_access}}
provider: {{provider_profile_or_blank}}
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
