# Personal Skills

This repository is a personal skills package for Claude Code and Codex workflows.

## Install

Quick install:

```bash
curl -fsSL https://raw.githubusercontent.com/tdccccc/skills/main/bootstrap.sh | bash
```

This downloads `bootstrap.sh`, clones or updates this repository under
`${CODEX_HOME:-$HOME/.codex}/skill-repos/personal-skills`, then runs
`install.sh` from that cached repository.

Clone this repository and run the installer:

```bash
git clone <repo-url> personal-skills
cd personal-skills
./install.sh
```

The installer copies every root-level directory containing `SKILL.md` into
`${CODEX_HOME:-$HOME/.codex}/skills`. It also installs shared support
directories used by the skills, currently `shared/` and `tools/`.

For local development, install with symlinks instead of copies:

```bash
./install.sh --link
```

Useful options:

```bash
./install.sh --force           # Replace existing installed directories
./install.sh --dest /path/to/skills
./install.sh --dry-run
```

With the one-line installer, pass installer options after `bash -s --`:

```bash
curl -fsSL https://raw.githubusercontent.com/tdccccc/skills/main/bootstrap.sh | bash -s -- --force
```

Restart Codex after installing or updating skills.

## Skills

- `article-summary/` summarizes astronomy and academic papers into structured Chinese notes.
- `claude-codex-runner/` lets Claude Code package a task and invoke Codex CLI for one-shot execution.
- `codex-task-executor/` tells Codex how to execute Claude-generated task packages and write structured reports.
- `security-audit/` audits Claude Code configuration for malicious hooks, MCP servers, and suspicious commands.

## Shared Protocols

- `shared/codex-task-contract.md` defines the task and report contract used by `claude-codex-runner` and `codex-task-executor`.

## Tools

- `tools/codex-runner/codex-runner` starts, polls, reads, cancels, and resumes Codex task runs.
- `security-audit/scripts/scan.py` runs the standalone Claude Code security scan.

Common commands:

```bash
tools/codex-runner/codex-runner start docs/tasks/<task-id>/task.md --background
tools/codex-runner/codex-runner status <task-id>
tools/codex-runner/codex-runner result <task-id>
tools/codex-runner/codex-runner cancel <task-id>
tools/codex-runner/codex-runner resume <task-id> --goal "<follow-up goal>"
```

## Layout

```text
skills/
  README.md
  bootstrap.sh
  install.sh
  shared/
    codex-task-contract.md
  tools/
    codex-runner/
      codex-runner
    codex_runner/
      cli.py
      runner.py
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
  security-audit/
    SKILL.md
    scripts/
      scan.py
    LICENSE
    README.md
```

## Conventions

- Each skill directory contains one `SKILL.md`.
- Supporting instructions and templates live in `references/`.
- Bundled executables for a skill live in that skill's `scripts/`.
- Imported third-party skills may keep their upstream `LICENSE` and `README.md`.
- Shared contracts used by multiple skills live in `shared/`.
- Task records generated in target projects use `docs/tasks/<task-id>/`.
- Temporary Codex execution artifacts in target projects use `.codex-runs/<task-id>/` and should be ignored by Git.
