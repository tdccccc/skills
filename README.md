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
